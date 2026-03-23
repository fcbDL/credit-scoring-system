import type { CreditReport } from '../types/credit';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  TrendingUp,
  MessageSquare,
  Scale,
  AlertTriangle,
  FileText,
} from 'lucide-react';

interface CreditReportDisplayProps {
  report: CreditReport;
}

export function CreditReportDisplay({ report }: CreditReportDisplayProps) {
  const getDecisionIcon = () => {
    switch (report.final_decision) {
      case 'approve':
        return <CheckCircle className="w-8 h-8 text-green-600" />;
      case 'reject':
        return <XCircle className="w-8 h-8 text-red-600" />;
      case 'review':
        return <AlertCircle className="w-8 h-8 text-yellow-600" />;
      default:
        return <AlertCircle className="w-8 h-8 text-gray-600" />;
    }
  };

  const getDecisionText = () => {
    switch (report.final_decision) {
      case 'approve':
        return '批准贷款';
      case 'reject':
        return '拒绝贷款';
      case 'review':
        return '待复核';
      default:
        return report.final_decision;
    }
  };

  const getDecisionBgClass = () => {
    switch (report.final_decision) {
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

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header Decision */}
      <div className={`rounded-xl border-2 p-6 ${getDecisionBgClass()}`}>
        <div className="flex items-center gap-4">
          {getDecisionIcon()}
          <div>
            <h2 className="text-2xl font-bold">{getDecisionText()}</h2>
            <p className="text-gray-600 mt-1">{report.decision_reason}</p>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">{report.overall_score}</div>
            <div className="text-sm text-gray-500">综合评分</div>
          </div>
          <div className="h-12 w-px bg-gray-300" />
          <div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(report.risk_level)}`}>
              {report.risk_level.toUpperCase()} 风险
            </span>
          </div>
        </div>
      </div>

      {/* Applicant Info */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <User className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">申请人基本信息</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">年龄</div>
            <div className="text-lg font-semibold">{report.applicant_info.age}岁</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">年收入</div>
            <div className="text-lg font-semibold">{formatCurrency(report.applicant_info.income)}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">贷款金额</div>
            <div className="text-lg font-semibold">{formatCurrency(report.applicant_info.loan_amount)}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">负债率</div>
            <div className="text-lg font-semibold">{(report.applicant_info.debt_to_income_ratio * 100).toFixed(1)}%</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">贷款用途</div>
            <div className="text-lg font-semibold">{report.applicant_info.loan_purpose}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">信用历史</div>
            <div className="text-lg font-semibold">{report.applicant_info.credit_history_length}年</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">现有贷款</div>
            <div className="text-lg font-semibold">{report.applicant_info.existing_loans}笔</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">贷款/收入比</div>
            <div className="text-lg font-semibold">{report.applicant_info.loan_to_income_ratio.toFixed(1)}倍</div>
          </div>
        </div>
      </div>

      {/* Numeric Analysis */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900">数值评分分析</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-4xl font-bold text-purple-700">
              {report.numeric_analysis.credit_score}
            </div>
            <div className="text-sm text-purple-600 mt-1">信用评分</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-4xl font-bold text-purple-700">
              {(report.numeric_analysis.probability_default * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-purple-600 mt-1">违约概率</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <span className={`inline-block px-4 py-2 rounded-full text-lg font-medium ${getRiskColor(report.numeric_analysis.risk_level)}`}>
              {report.numeric_analysis.risk_level.toUpperCase()}
            </span>
            <div className="text-sm text-gray-500 mt-1">风险等级</div>
          </div>
        </div>

        {/* Feature Importance */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">特征贡献度</h4>
          <div className="space-y-2">
            {Object.entries(report.numeric_analysis.features_importance)
              .sort(([, a], [, b]) => b - a)
              .map(([name, value]) => (
                <div key={name} className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 w-24 truncate">{name}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full transition-all"
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-700 w-12 text-right">
                    {(value * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Semantic Analysis */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="w-5 h-5 text-teal-600" />
          <h3 className="font-semibold text-gray-900">语义风险评估</h3>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-500">还款意愿</div>
            <span className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(report.semantic_analysis.repayment_willingness)}`}>
              {report.semantic_analysis.repayment_willingness.toUpperCase()}
            </span>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-500">行业风险</div>
            <span className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(report.semantic_analysis.industry_risk)}`}>
              {report.semantic_analysis.industry_risk.toUpperCase()}
            </span>
          </div>
        </div>

        {report.semantic_analysis.fraud_indicators.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="w-4 h-4" />
              <span className="font-medium">欺诈指标</span>
            </div>
            <ul className="mt-2 text-sm text-red-600 space-y-1">
              {report.semantic_analysis.fraud_indicators.map((item, idx) => (
                <li key={idx}>• {item}</li>
              ))}
            </ul>
          </div>
        )}

        {report.semantic_analysis.concerns.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-yellow-700">
              <AlertTriangle className="w-4 h-4" />
              <span className="font-medium">风险关注点</span>
            </div>
            <ul className="mt-2 text-sm text-yellow-600 space-y-1">
              {report.semantic_analysis.concerns.map((item, idx) => (
                <li key={idx}>• {item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Rule Results */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Scale className="w-5 h-5 text-orange-600" />
          <h3 className="font-semibold text-gray-900">规则命中情况</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-sm text-gray-500 mb-2">通过规则</div>
            {report.rule_results.passed_rules.length > 0 ? (
              <ul className="text-sm text-green-700 space-y-1">
                {report.rule_results.passed_rules.map((rule, idx) => (
                  <li key={idx}>✓ {rule}</li>
                ))}
              </ul>
            ) : (
              <span className="text-sm text-gray-500">暂无</span>
            )}
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <div className="text-sm text-gray-500 mb-2">未通过规则</div>
            {report.rule_results.failed_rules.length > 0 ? (
              <ul className="text-sm text-red-700 space-y-1">
                {report.rule_results.failed_rules.map((rule, idx) => (
                  <li key={idx}>✗ {rule}</li>
                ))}
              </ul>
            ) : (
              <span className="text-sm text-gray-500">暂无</span>
            )}
          </div>
        </div>
      </div>

      {/* Risk Warnings */}
      {report.risk_warnings.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h3 className="font-semibold text-amber-800">风险提示</h3>
          </div>
          <ul className="space-y-2">
            {report.risk_warnings.map((warning, idx) => (
              <li key={idx} className="text-amber-700 flex items-start gap-2">
                {warning.includes('✓') ? (
                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                )}
                <span>{warning}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Compliance Basis */}
      {report.compliance_basis.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-blue-800">合规依据</h3>
          </div>
          <ul className="space-y-2">
            {report.compliance_basis.map((basis, idx) => (
              <li key={idx} className="text-blue-700 text-sm">
                {basis}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Report Footer */}
      <div className="text-center text-sm text-gray-500 border-t pt-4">
        报告编号: {report.report_id} | 评估时间: {report.evaluation_time}
      </div>
    </div>
  );
}
