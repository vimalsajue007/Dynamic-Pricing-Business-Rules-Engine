from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ConflictException, NotFoundException
from app.models.customer import Customer, CustomerTypeEnum
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=APIResponse[PaginatedResponse[CustomerOut]])
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = None,
    customer_type: Optional[CustomerTypeEnum] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Customer)
    if search:
        q = q.filter(Customer.name.ilike(f"%{search}%") | Customer.email.ilike(f"%{search}%"))
    if customer_type is not None:
        q = q.filter(Customer.customer_type == customer_type)
    if is_active is not None:
        q = q.filter(Customer.is_active == is_active)
    total = q.count()
    items = q.order_by(Customer.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return APIResponse(
        data=PaginatedResponse(
            items=[CustomerOut.model_validate(c) for c in items],
            total=total, page=page, page_size=page_size,
            total_pages=max((total + page_size - 1) // page_size, 1),
        )
    )


@router.post("", response_model=APIResponse[CustomerOut], status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Customer).filter(Customer.email == payload.email).first():
        raise ConflictException("A customer with this email already exists")
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return APIResponse(message="Customer created", data=CustomerOut.model_validate(customer))


@router.put("/{customer_id}", response_model=APIResponse[CustomerOut])
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise NotFoundException("Customer not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(customer, k, v)
    db.commit()
    db.refresh(customer)
    return APIResponse(message="Customer updated", data=CustomerOut.model_validate(customer))


@router.delete("/{customer_id}", response_model=APIResponse[None])
def delete_customer(customer_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise NotFoundException("Customer not found")
    db.delete(customer)
    db.commit()
    return APIResponse(message="Customer deleted")
