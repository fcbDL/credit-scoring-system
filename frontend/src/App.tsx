import { useState } from 'react';
import { CreditForm } from './components/CreditForm';
import { CreditReportDisplay } from './components/CreditReport';
import { SimpleResult } from './components/SimpleResult';
import { TraceVisualization } from './components/TraceVisualization';
import type { NumericData, TextData, CreditEvaluationResponse } from './types/credit';
import { evaluateCredit } from './services/api';
import { Banknote, ChevronDown, ChevronUp, GitBranch, AlertCircle } from 'lucide-react';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<CreditEvaluationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTrace, setShowTrace] = useState(false);

  const handleSubmit = async (numericData: NumericData, textData: TextData) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setShowTrace(false);

    try {
      const response = await evaluateCredit({ numeric_data: numericData, text_data: textData });
      setResult(response);
      if (response.final_decision === 'error') {
        setError(response.decision_reason);
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('请求失败，请检查后端服务是否启动');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Banknote className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">信贷评分系统</h1>
              <p className="text-sm text-gray-500">基于多智能体协同的风控决策</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-2">
            <CreditForm onSubmit={handleSubmit} isLoading={isLoading} />

            {/* Error Display */}
            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-medium text-red-800">发生错误</span>
                  <p className="text-red-600 text-sm mt-1">{error}</p>
                </div>
              </div>
            )}

            {/* Results */}
            {result && result.final_decision !== 'error' && (
              <div className="mt-8">
                {result.credit_report ? (
                  <CreditReportDisplay report={result.credit_report} />
                ) : (
                  <SimpleResult result={result} />
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Info Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">决策说明</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-start gap-2">
                  <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-green-600 text-xs font-bold">✓</span>
                  </div>
                  <div>
                    <span className="font-medium text-green-800">批准</span>
                    <p className="text-gray-600">综合评分良好，可批准贷款</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-red-600 text-xs font-bold">✗</span>
                  </div>
                  <div>
                    <span className="font-medium text-red-800">拒绝</span>
                    <p className="text-gray-600">存在高风险因素，拒绝贷款</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-6 h-6 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-yellow-600 text-xs font-bold">!</span>
                  </div>
                  <div>
                    <span className="font-medium text-yellow-800">待复核</span>
                    <p className="text-gray-600">存在争议，需要人工审核</p>
                  </div>
                </div>
              </div>
            </div>

            {/* System Info */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">系统说明</h3>
              <div className="space-y-3 text-sm text-gray-600">
                <p>本系统采用多智能体协同架构：</p>
                <ul className="list-disc list-inside space-y-1 pl-2">
                  <li>数值分析 Agent - XGBoost 评分</li>
                  <li>语义分析 Agent - LLM 风险识别</li>
                  <li>主控决策 Agent - 综合决策</li>
                </ul>
                <p className="pt-2 border-t border-gray-200">
                  通过冲突检测机制，确保数值与语义分析的一致性。
                </p>
              </div>
            </div>

            {/* API Status */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">API 状态</h3>
              <p className="text-sm text-gray-600">
                后端地址: <code className="bg-gray-100 px-1 rounded">http://localhost:8000</code>
              </p>
              <p className="text-sm text-gray-500 mt-2">
                确保后端服务已启动后再提交评估
              </p>
            </div>
          </div>
        </div>

        {/* Trace Section - Below main content */}
        {result && result.trace && result.trace.length > 0 && (
          <div className="mt-8">
            <button
              onClick={() => setShowTrace(!showTrace)}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <GitBranch className="w-5 h-5" />
              {showTrace ? '隐藏推理链路' : '显示推理链路'}
              {showTrace ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showTrace && (
              <div className="mt-4">
                <TraceVisualization trace={result.trace} />
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-gray-200 bg-white">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <p className="text-center text-sm text-gray-500">
            基于 LangGraph + MiniMax 多智能体协同风控决策系统
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
