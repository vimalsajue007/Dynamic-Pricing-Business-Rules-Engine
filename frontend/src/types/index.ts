export type Role = "admin" | "user";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: Role;
  is_active: boolean;
}

export interface Category {
  id: number;
  name: string;
  description?: string | null;
  is_active: boolean;
}

export interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string | null;
  base_price: number;
  category_id?: number | null;
  category?: Category | null;
  is_active: boolean;
}

export type CustomerType = "Regular" | "Premium" | "Business" | "Wholesale";

export interface Customer {
  id: number;
  name: string;
  email: string;
  customer_type: CustomerType;
  location?: string | null;
  category?: string | null;
  is_active: boolean;
}

export type ConditionField = "customer_type" | "quantity" | "location" | "category" | "product" | "order_total" | "date";
export type Operator = "equals" | "not_equals" | "greater_than" | "greater_or_equal" | "less_than" | "less_or_equal" | "in";
export type ActionType = "percent_discount" | "flat_discount" | "surcharge_percent" | "surcharge_flat" | "fixed_price";
export type RuleLogic = "AND" | "OR";

export interface RuleCondition {
  id?: number;
  field: ConditionField;
  operator: Operator;
  value: string;
}

export interface RuleAction {
  id?: number;
  action_type: ActionType;
  value: number;
  max_amount?: number | null;
}

export interface PricingRule {
  id: number;
  name: string;
  description?: string | null;
  priority: number;
  condition_logic: RuleLogic;
  is_exclusive: boolean;
  is_stackable: boolean;
  start_date?: string | null;
  end_date?: string | null;
  is_active: boolean;
  conditions: RuleCondition[];
  actions: RuleAction[];
}

export type DiscountType = "percent" | "flat";

export interface Promotion {
  id: number;
  code: string;
  description?: string | null;
  discount_type: DiscountType;
  discount_value: number;
  minimum_purchase: number;
  maximum_discount?: number | null;
  start_date?: string | null;
  expiry_date?: string | null;
  usage_limit?: number | null;
  usage_count: number;
  is_active: boolean;
}

export interface AppliedRuleDetail {
  rule_id?: number | null;
  rule_name: string;
  action_type: string;
  discount_amount: number;
  surcharge_amount: number;
  stacked: boolean;
}

export interface NonMatchedRuleDetail {
  rule_id: number;
  rule_name: string;
  reason: string;
}

export interface PromotionDetail {
  code: string;
  discount_amount: number;
  valid: boolean;
  message?: string | null;
}

export interface PricingResult {
  product_id: number;
  product_name: string;
  base_price: number;
  quantity: number;
  subtotal: number;
  applied_rules: AppliedRuleDetail[];
  rule_discount_total: number;
  promotion?: PromotionDetail | null;
  promotion_discount: number;
  surcharge_total: number;
  taxable_amount: number;
  tax_rate_percent: number;
  tax_amount: number;
  final_price: number;
}

export interface RuleTestResult {
  pricing: PricingResult;
  matched_rules: AppliedRuleDetail[];
  non_matched_rules: NonMatchedRuleDetail[];
}

export interface PricingHistoryItem {
  id: number;
  product_id: number;
  customer_id?: number | null;
  input_parameters: Record<string, any>;
  applied_rules: any;
  promo_code?: string | null;
  original_price: number;
  discount_amount: number;
  tax_amount: number;
  final_price: number;
  calculation_time: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DashboardSummary {
  total_products: number;
  active_pricing_rules: number;
  active_promotions: number;
  total_discounts_given: number;
  pricing_calculation_count: number;
  most_applied_rules: { rule_name: string; times_applied: number }[];
  pricing_activity_trend: { date: string; count: number }[];
}
