export interface NumericData {
  age: number;
  income: number;
  credit_history_length: number;
  debt_to_income_ratio: number;
  employment_length: number;
  loan_amount: number;
  loan_purpose: 'personal' | 'business' | 'education' | 'home';
  existing_loans: number;
  payment_history: number;
}

export interface TextData {
  application_statement: string;
  credit_remarks?: string;
}

export interface CreditEvaluationRequest {
  numeric_data: NumericData;
  text_data: TextData;
}

export interface NumericResult {
  credit_score: number;
  probability_default: number;
  risk_level: 'low' | 'medium' | 'high';
  features_importance: Record<string, number>;
}

export interface SemanticRisk {
  fraud_indicators: string[];
  repayment_willingness: 'low' | 'medium' | 'high';
  industry_risk: 'low' | 'medium' | 'high';
  concerns: string[];
  confidence: number;
}

export interface RuleResults {
  passed: boolean;
  passed_rules: string[];
  failed_rules: string[];
}

export interface CreditReport {
  report_id: string;
  evaluation_time: string;
  applicant_info: {
    age: number;
    income: number;
    credit_history_length: number;
    debt_to_income_ratio: number;
    employment_length: number;
    loan_amount: number;
    loan_purpose: string;
    existing_loans: number;
    payment_history: number;
    application_statement: string;
    credit_remarks?: string;
    loan_to_income_ratio: number;
  };
  numeric_analysis: {
    credit_score: number;
    probability_default: number;
    risk_level: string;
    features_importance: Record<string, number>;
  };
  semantic_analysis: {
    repayment_willingness: string;
    industry_risk: string;
    fraud_indicators: string[];
    concerns: string[];
  };
  rule_results: RuleResults;
  compliance_basis: string[];
  risk_warnings: string[];
  final_decision: string;
  decision_reason: string;
  overall_score: number;
  risk_level: string;
}

export interface TraceStep {
  node?: string;
  agent?: string;
  action: string;
  plan?: string;
  result?: string;
  error?: string;
  decision?: string;
  reason?: string;
  results_count?: number;
  status?: string;
}

export interface CreditEvaluationResponse {
  final_decision: 'approve' | 'reject' | 'review' | 'error';
  decision_reason: string;
  numeric_result: NumericResult | null;
  semantic_risk: SemanticRisk | null;
  conflict_detected: boolean;
  conflict_details: string | null;
  trace: TraceStep[];
  credit_report: CreditReport | null;
}
