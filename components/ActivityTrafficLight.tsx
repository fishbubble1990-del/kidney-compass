
import React, { useState } from 'react';
import { Search, Loader2, Footprints, AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { classifyItem } from '../services/geminiService';
import { ActivityClassification, StatusLevel } from '../types';

const ActivityTrafficLight: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ActivityClassification | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    const classification = await classifyItem(query, 'activity');
    setResult(classification);
    setIsLoading(false);
  };

  const renderLevelIcon = (level: StatusLevel) => {
    switch (level) {
      case 'red': return <ShieldAlert className="w-8 h-8 text-red-500" />;
      case 'yellow': return <AlertCircle className="w-8 h-8 text-amber-500" />;
      case 'green': return <CheckCircle2 className="w-8 h-8 text-teal-500" />;
    }
  };

  const getLevelColor = (level: StatusLevel) => {
    switch (level) {
      case 'red': return 'border-red-200 bg-red-50';
      case 'yellow': return 'border-amber-200 bg-amber-50';
      case 'green': return 'border-teal-200 bg-teal-50';
    }
  };

  return (
    <div className="space-y-6 pb-24">
      <header className="flex items-center space-x-3">
        <div className="p-2 bg-teal-100 rounded-xl">
          <Footprints className="text-teal-600 w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-800">体力红绿灯</h2>
          <p className="text-xs text-slate-500">明确界定什么能干，防止透支。</p>
        </div>
      </header>

      <form onSubmit={handleSearch} className="relative group">
        <input 
          type="text" 
          placeholder="搜索动作：如“搬快递”、“擦窗”..."
          className="w-full p-4 pl-12 pr-12 bg-white border border-slate-200 rounded-2xl shadow-sm focus:ring-2 focus:ring-teal-500 outline-none transition-all"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
          <Search className="text-slate-400 w-5 h-5" />
        </div>
        
        <button 
          type="submit" 
          disabled={isLoading}
          className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-xl hover:bg-slate-50 transition-colors"
        >
          {isLoading ? (
            <Loader2 className="text-teal-500 w-5 h-5 animate-spin origin-center" />
          ) : (
            <div className="w-5 h-5" /> // Spacer to maintain layout
          )}
        </button>
      </form>

      {!result && !isLoading && (
        <div className="grid grid-cols-1 gap-4">
          <div className="p-4 bg-white rounded-2xl border border-slate-100 shadow-sm">
            <h4 className="text-sm font-bold text-red-600 mb-2 flex items-center">
              <ShieldAlert className="w-4 h-4 mr-1" /> 绝对禁止 (🔴)
            </h4>
            <ul className="text-xs text-slate-600 space-y-1 list-disc list-inside">
              <li>搬运 &gt;5kg 重物（米袋、水桶）</li>
              <li>剧烈跑跳 / HIIT / 举铁</li>
              <li>弯腰拖地超过 15 分钟</li>
            </ul>
          </div>
          <div className="p-4 bg-white rounded-2xl border border-slate-100 shadow-sm">
            <h4 className="text-sm font-bold text-amber-600 mb-2 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" /> 谨慎进行 (🟡)
            </h4>
            <ul className="text-xs text-slate-600 space-y-1 list-disc list-inside">
              <li>性生活（建议 &lt; 2次/周）</li>
              <li>长途出差（需开启出差模式）</li>
              <li>长时间驾车或伏案工作</li>
            </ul>
          </div>
        </div>
      )}

      {result && (
        <div className={`p-6 rounded-3xl border animate-in fade-in slide-in-from-bottom-4 duration-500 ${getLevelColor(result.level)}`}>
          <div className="flex justify-between items-start mb-4">
            <div>
              <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full mb-2 inline-block ${
                result.level === 'red' ? 'bg-red-200 text-red-800' :
                result.level === 'yellow' ? 'bg-amber-200 text-amber-800' : 'bg-teal-200 text-teal-800'
              }`}>
                {result.level === 'red' ? '高风险' : result.level === 'yellow' ? '中风险' : '低风险'}
              </span>
              <h3 className="text-2xl font-bold text-slate-800">{result.name}</h3>
            </div>
            {renderLevelIcon(result.level)}
          </div>
          <p className="text-sm font-semibold text-slate-700 mb-2">原因：</p>
          <p className="text-sm text-slate-600 mb-4">{result.reason}</p>
          <div className="bg-white bg-opacity-50 p-3 rounded-xl">
            <p className="text-xs font-bold text-slate-800">专业建议：</p>
            <p className="text-xs text-slate-600 leading-relaxed mt-1">{result.advice}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityTrafficLight;
