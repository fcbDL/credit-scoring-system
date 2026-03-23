import { useState } from 'react';
import type { NumericData, TextData } from '../types/credit';
import { Calculator, FileText, Loader2 } from 'lucide-react';

interface CreditFormProps {
  onSubmit: (numericData: NumericData, textData: TextData) => void;
  isLoading: boolean;
}

const defaultNumericData: NumericData = {
  age: 35,
  income: 80000,
  credit_history_length: 5,
  debt_to_income_ratio: 0.3,
  employment_length: 3,
  loan_amount: 50000,
  loan_purpose: 'home',
  existing_loans: 1,
  payment_history: 0.9,
};

const defaultTextData: TextData = {
  application_statement: '贷款用于房屋装修，已签订装修合同，有稳定收入来源。',
  credit_remarks: '信用记录良好，无逾期记录。',
};

export function CreditForm({ onSubmit, isLoading }: CreditFormProps) {
  const [numericData, setNumericData] = useState<NumericData>(defaultNumericData);
  const [textData, setTextData] = useState<TextData>(defaultTextData);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(numericData, textData);
  };

  const handleReset = () => {
    setNumericData(defaultNumericData);
    setTextData(defaultTextData);
  };

  const updateNumeric = (field: keyof NumericData, value: string | number) => {
    setNumericData(prev => ({
      ...prev,
      [field]: typeof numericData[field] === 'number' ? Number(value) : value,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Numeric Data Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-6">
          <Calculator className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">数值数据</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              年龄
            </label>
            <input
              type="number"
              value={numericData.age}
              onChange={e => updateNumeric('age', e.target.value)}
              min={18}
              max={100}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              年收入 (¥)
            </label>
            <input
              type="number"
              value={numericData.income}
              onChange={e => updateNumeric('income', e.target.value)}
              min={0}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              贷款金额 (¥)
            </label>
            <input
              type="number"
              value={numericData.loan_amount}
              onChange={e => updateNumeric('loan_amount', e.target.value)}
              min={0}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              信用历史 (年)
            </label>
            <input
              type="number"
              value={numericData.credit_history_length}
              onChange={e => updateNumeric('credit_history_length', e.target.value)}
              min={0}
              max={50}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              工作年限 (年)
            </label>
            <input
              type="number"
              value={numericData.employment_length}
              onChange={e => updateNumeric('employment_length', e.target.value)}
              min={0}
              max={50}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              现有贷款数
            </label>
            <input
              type="number"
              value={numericData.existing_loans}
              onChange={e => updateNumeric('existing_loans', e.target.value)}
              min={0}
              max={20}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              贷款用途
            </label>
            <select
              value={numericData.loan_purpose}
              onChange={e => updateNumeric('loan_purpose', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="personal">个人消费</option>
              <option value="business">企业经营</option>
              <option value="education">教育</option>
              <option value="home">房屋贷款</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              负债率 ({numericData.debt_to_income_ratio.toFixed(2)})
            </label>
            <input
              type="range"
              value={numericData.debt_to_income_ratio}
              onChange={e => updateNumeric('debt_to_income_ratio', parseFloat(e.target.value))}
              min={0}
              max={1}
              step={0.01}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              还款历史 ({(numericData.payment_history * 100).toFixed(0)}%)
            </label>
            <input
              type="range"
              value={numericData.payment_history}
              onChange={e => updateNumeric('payment_history', parseFloat(e.target.value))}
              min={0}
              max={1}
              step={0.01}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>差</span>
              <span>中</span>
              <span>优</span>
            </div>
          </div>
        </div>
      </div>

      {/* Text Data Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-6">
          <FileText className="w-5 h-5 text-green-600" />
          <h2 className="text-lg font-semibold text-gray-900">文本资料</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              贷款申请说明
            </label>
            <textarea
              value={textData.application_statement}
              onChange={e => setTextData(prev => ({ ...prev, application_statement: e.target.value }))}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="请描述贷款用途、还款计划等信息..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              信用备注 (可选)
            </label>
            <textarea
              value={textData.credit_remarks || ''}
              onChange={e => setTextData(prev => ({ ...prev, credit_remarks: e.target.value }))}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="补充信用相关信息..."
            />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              评估中...
            </>
          ) : (
            '提交评估'
          )}
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          重置
        </button>
      </div>
    </form>
  );
}
