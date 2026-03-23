import type { CreditEvaluationResponse } from '../types/credit';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  MessageSquare,
  AlertTriangle,
} from 'lucide-react';

interface SimpleResultProps {
  result: CreditEvaluationResponse;
}

export function SimpleResult({ result }: SimpleResultProps) {
  const getDecisionIcon = () => {
    switch (result.final_decision) {
      case 'approve':
        return <CheckCircle className="w-12 h-12 text-green-600" />;
      case 'reject':
        return <XCircle className="w-12 h-12 text-red-600" />;
      case 'review':
        return <AlertCircle className="w-12 h-12 text-yellow-600" />;
      default:
        return <AlertCircle className="w-12 h-12 text-gray-600" />;
    }
  };

  const getDecisionText = () => {
    switch (result.final_decision) {
      case 'approve':
        return '批准贷款';
      case 'reject':
        return '拒绝贷款';
      case 'review':
        return '待复核';
      default:
        return result.final_decision;
    }
  };

  const getDecisionBgClass = () => {
    switch (result.final_decision) {
      case 'approve':
        return 'bg-green-50 border-green-200';
      case 'reject':
        return 'bg-red-50 border-red-200';
      case 'review':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Decision */}
      <div className={`rounded-xl border-2 p-6 ${getDecisionBgClass()}`}>
        <div className="flex items-center gap-4">
          {getDecisionIcon()}
          <div>
            <h2 className="text-2xl font-bold">{getDecisionText()}</h2>
            <p className="text-gray-600 mt-1">{result.decision_reason}</p>
          </div>
        </div>

        {result.conflict_detected && (
          <div className="mt-4 bg-yellow-100 border border-yellow-300 rounded-lg p-3 flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-medium text-yellow-800">检测到冲突</span>
              <p className="text-yellow-700 text-sm">{result.conflict_details}</p>
            </div>
          </div>
        )}
      </div>

      {/* Numeric Result */}
      {result.numeric_result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">数值分析</h3>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-purple-700">
                {result.numeric_result.credit_score}
              </div>
              <div className="text-sm text-purple-600 mt-1">信用评分</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-purple-700">
                {(result.numeric_result.probability_default * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-purple-600 mt-1">违约概率</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <span className={`inline-block px-3 py-1 rounded-full text-lg font-medium ${
                result.numeric_result.risk_level === 'low' ? 'bg-green-100 text-green-700' :
                result.numeric_result.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {result.numeric_result.risk_level.toUpperCase()}
              </span>
              <div className="text-sm text-gray-500 mt-1">风险等级</div>
            </div>
          </div>
        </div>
      )}

      {/* Semantic Result */}
      {result.semantic_risk && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <MessageSquare className="w-5 h-5 text-teal-600" />
            <h3 className="font-semibold text-gray-900">语义分析</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-500">还款意愿</div>
              <span className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-medium ${
                result.semantic_risk.repayment_willingness === 'low' ? 'bg-red-100 text-red-700' :
                result.semantic_risk.repayment_willingness === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-green-100 text-green-700'
              }`}>
                {result.semantic_risk.repayment_willingness.toUpperCase()}
              </span>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-500">行业风险</div>
              <span className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-medium ${
                result.semantic_risk.industry_risk === 'low' ? 'bg-green-100 text-green-700' :
                result.semantic_risk.industry_risk === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {result.semantic_risk.industry_risk.toUpperCase()}
              </span>
            </div>
          </div>

          {result.semantic_risk.fraud_indicators.length > 0 && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-red-700">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-medium">欺诈指标</span>
              </div>
              <ul className="mt-2 text-sm text-red-600 space-y-1">
                {result.semantic_risk.fraud_indicators.map((item, idx) => (
                  <li key={idx}>• {item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
