from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.pricing_rule import PricingRule, RuleAction, RuleCondition
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.pricing_rule import PricingRuleCreate, PricingRuleOut, PricingRuleUpdate
from app.services.cache_service import invalidate_rules

router = APIRouter(prefix="/pricing-rules", tags=["Pricing Rules"])


def _load(db: Session, rule_id: int) -> PricingRule:
    rule = (
        db.query(PricingRule)
        .options(joinedload(PricingRule.conditions), joinedload(PricingRule.actions))
        .filter(PricingRule.id == rule_id)
        .first()
    )
    if not rule:
        raise NotFoundException("Pricing rule not found")
    return rule


@router.get("", response_model=APIResponse[PaginatedResponse[PricingRuleOut]])
def list_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(PricingRule).options(joinedload(PricingRule.conditions), joinedload(PricingRule.actions))
    if search:
        q = q.filter(PricingRule.name.ilike(f"%{search}%"))
    if is_active is not None:
        q = q.filter(PricingRule.is_active == is_active)
    total = q.distinct().count()
    items = (
        q.order_by(PricingRule.priority.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[PricingRuleOut.model_validate(r) for r in items],
            total=total, page=page, page_size=page_size,
            total_pages=max((total + page_size - 1) // page_size, 1),
        )
    )


@router.get("/{rule_id}", response_model=APIResponse[PricingRuleOut])
def get_rule(rule_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return APIResponse(data=PricingRuleOut.model_validate(_load(db, rule_id)))


@router.post("", response_model=APIResponse[PricingRuleOut], status_code=201)
def create_rule(payload: PricingRuleCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    data = payload.model_dump(exclude={"conditions", "actions"})
    rule = PricingRule(**data)
    rule.conditions = [RuleCondition(**c.model_dump()) for c in payload.conditions]
    rule.actions = [RuleAction(**a.model_dump()) for a in payload.actions]
    db.add(rule)
    db.commit()
    db.refresh(rule)
    invalidate_rules()
    return APIResponse(message="Pricing rule created", data=PricingRuleOut.model_validate(rule))


@router.put("/{rule_id}", response_model=APIResponse[PricingRuleOut])
def update_rule(rule_id: int, payload: PricingRuleUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    rule = _load(db, rule_id)
    data = payload.model_dump(exclude_unset=True, exclude={"conditions", "actions"})
    for k, v in data.items():
        setattr(rule, k, v)

    if payload.conditions is not None:
        rule.conditions = [RuleCondition(**c.model_dump()) for c in payload.conditions]
    if payload.actions is not None:
        rule.actions = [RuleAction(**a.model_dump()) for a in payload.actions]

    db.commit()
    db.refresh(rule)
    invalidate_rules()
    return APIResponse(message="Pricing rule updated", data=PricingRuleOut.model_validate(rule))


@router.delete("/{rule_id}", response_model=APIResponse[None])
def delete_rule(rule_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    rule = _load(db, rule_id)
    db.delete(rule)
    db.commit()
    invalidate_rules()
    return APIResponse(message="Pricing rule deleted")
