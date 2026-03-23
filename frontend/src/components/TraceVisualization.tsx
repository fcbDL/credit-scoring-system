import type { TraceStep } from '../types/credit';
import { GitBranch, CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react';

interface TraceVisualizationProps {
  trace: TraceStep[];
}

export function TraceVisualization({ trace }: TraceVisualizationProps) {
  const getStepIcon = (step: TraceStep) => {
    if (step.error) {
      return <XCircle className="w-5 h-5 text-red-500" />;
    }
    if (step.result || step.decision) {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    }
    if (step.plan) {
      return <GitBranch className="w-5 h-5 text-blue-500" />;
    }
    return <AlertCircle className="w-5 h-5 text-gray-400" />;
  };

  const getAgentColor = (agent: string | undefined) => {
    switch (agent) {
      case 'numeric':
        return 'border-purple-300 bg-purple-50';
      case 'semantic':
        return 'border-teal-300 bg-teal-50';
      case 'supervisor':
        return 'border-amber-300 bg-amber-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  const getAgentLabel = (agent: string | undefined) => {
    switch (agent) {
      case 'numeric':
        return '数值分析';
      case 'semantic':
        return '语义分析';
      case 'supervisor':
        return '主控决策';
      case 'supervisor':
        return '主控';
      default:
        return agent || '系统';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <GitBranch className="w-5 h-5 text-blue-600" />
        推理链路
      </h3>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />

        <div className="space-y-4">
          {trace.map((step, index) => (
            <div key={index} className="relative flex items-start gap-4">
              {/* Icon */}
              <div className="relative z-10 w-10 h-10 rounded-full bg-white border-2 border-gray-200 flex items-center justify-center flex-shrink-0">
                {getStepIcon(step)}
              </div>

              {/* Content */}
              <div className={`flex-1 rounded-lg border p-4 ${getAgentColor(step.agent || step.node)}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-medium text-gray-900">
                    {step.agent ? getAgentLabel(step.agent) : step.node ? '系统' : ''}
                  </span>
                  {step.agent && (
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      step.agent === 'numeric' ? 'bg-purple-100 text-purple-700' :
                      step.agent === 'semantic' ? 'bg-teal-100 text-teal-700' :
                      'bg-amber-100 text-amber-700'
                    }`}>
                      Agent
                    </span>
                  )}
                </div>

                {/* Action */}
                <div className="text-sm text-gray-700 mb-2">
                  <span className="font-medium">操作:</span> {step.action}
                </div>

                {/* Plan (for supervisor) */}
                {step.plan && (
                  <div className="bg-blue-50 rounded p-2 text-sm text-blue-700">
                    <span className="font-medium">计划:</span> {step.plan}
                  </div>
                )}

                {/* Result */}
                {step.result && (
                  <div className="bg-green-50 rounded p-2 text-sm text-green-700">
                    <span className="font-medium">结果:</span> {step.result}
                  </div>
                )}

                {/* Error */}
                {step.error && (
                  <div className="bg-red-50 rounded p-2 text-sm text-red-700">
                    <span className="font-medium">错误:</span> {step.error}
                  </div>
                )}

                {/* Decision (for supervisor final decision) */}
                {step.decision && (
                  <div className="bg-amber-50 rounded p-2 mt-2">
                    <div className="text-sm">
                      <span className="font-medium text-amber-700">决策:</span>{' '}
                      <span className={`font-bold ${
                        step.decision === 'approve' ? 'text-green-600' :
                        step.decision === 'reject' ? 'text-red-600' :
                        'text-yellow-600'
                      }`}>
                        {step.decision === 'approve' ? '批准' :
                         step.decision === 'reject' ? '拒绝' : '待复核'}
                      </span>
                    </div>
                    {step.reason && (
                      <div className="text-sm text-amber-600 mt-1">
                        {step.reason}
                      </div>
                    )}
                  </div>
                )}

                {/* Results count (for RAG retrieval) */}
                {step.results_count !== undefined && (
                  <div className="text-sm text-gray-500 mt-1">
                    检索到 {step.results_count} 条相关规则
                  </div>
                )}

                {/* Status indicator */}
                {step.status && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
                    {step.status === 'completed' ? (
                      <>
                        <CheckCircle2 className="w-3 h-3 text-green-500" />
                        <span>已完成</span>
                      </>
                    ) : (
                      <>
                        <Loader2 className="w-3 h-3 text-blue-500 animate-spin" />
                        <span>进行中</span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
