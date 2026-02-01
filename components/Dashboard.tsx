
import React, { useState, useEffect } from 'react';
import { AlertCircle, Thermometer, Droplets, Weight, Activity as PulseIcon, HeartPulse, History, Sparkles, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { DailyRecord, HealthAnalysis } from '../types';
import { analyzeHealthTrends } from '../services/geminiService';

interface DashboardProps {
  record: DailyRecord;
  setRecord: (r: DailyRecord) => void;
  history: DailyRecord[];
}

const Dashboard: React.FC<DashboardProps> = ({ record, setRecord, history }) => {
  const [showCheckIn, setShowCheckIn] = useState(false);
  const [isRedAlert, setIsRedAlert] = useState(false);
  const [analysis, setAnalysis] = useState<HealthAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (record.systolic >= 140 || record.diastolic >= 90 || record.hematuria) {
      setIsRedAlert(true);
    } else {
      setIsRedAlert(false);
    }
  }, [record]);

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    const result = await analyzeHealthTrends([...history, record]);
    setAnalysis(result);
    setIsAnalyzing(false);
  };

  const getStatusColor = (): string => {
    if (isRedAlert) return 'bg-red-50 text-red-700 border-red-200';
    if (record.systolic >= 130 || record.diastolic >= 80) return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-teal-50 text-teal-700 border-teal-200';
  };

  const renderTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="text-teal-500 w-5 h-5" />;
      case 'declining': return <TrendingDown className="text-red-500 w-5 h-5" />;
      default: return <Minus className="text-slate-400 w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6 pb-24">
      {/* Red Line Dashboard Banner */}
      <div className={`p-6 rounded-3xl border transition-all duration-500 ${getStatusColor()}`}>
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-bold mb-1">能量状态：{isRedAlert ? '高度警戒' : '稳步守护中'}</h2>
            <p className="text-sm opacity-90">
              {isRedAlert ? '身体正在发出求救信号，请联系医生或休息。' : '早安，设计师。今日的肾脏依然值得被细心照顾。'}
            </p>
          </div>
          <HeartPulse className={`w-10 h-10 ${isRedAlert ? 'text-red-600' : 'text-teal-600'}`} />
        </div>
        
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="bg-white bg-opacity-60 p-3 rounded-xl">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-semibold uppercase tracking-wider">当前血压</p>
              <span className="text-[9px] font-bold bg-white/40 px-1.5 rounded uppercase">{record.bpHand === 'left' ? '左手' : '右手'}</span>
            </div>
            <p className="text-2xl font-black">{record.systolic}/{record.diastolic} <span className="text-xs font-normal">mmHg</span></p>
          </div>
          <div className="bg-white bg-opacity-60 p-3 rounded-xl">
            <p className="text-xs font-semibold uppercase tracking-wider mb-1">今日体重</p>
            <p className="text-2xl font-black">{record.weight} <span className="text-xs font-normal">kg</span></p>
          </div>
        </div>

        {isRedAlert && (
          <div className="mt-4 bg-red-600 text-white p-3 rounded-xl flex items-center space-x-2 animate-pulse">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm font-bold">强制警戒：今日请勿参与高强度设计，建议静养。</span>
          </div>
        )}
      </div>

      {/* AI Analysis & History Section */}
      <section className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 overflow-hidden relative">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-slate-800 flex items-center">
            <Sparkles className="w-5 h-5 text-teal-500 mr-2" /> 历史趋势与 AI 分析
          </h3>
          <button 
            onClick={runAnalysis}
            disabled={isAnalyzing}
            className="text-xs bg-teal-50 text-teal-600 px-3 py-1.5 rounded-full font-bold hover:bg-teal-100 disabled:opacity-50 transition-colors"
          >
            {isAnalyzing ? '分析中...' : '生成智能简报'}
          </button>
        </div>

        {analysis ? (
          <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-500">
            <div className="flex items-center space-x-3 p-3 bg-slate-50 rounded-2xl border border-slate-100">
              {renderTrendIcon(analysis.trend)}
              <p className="text-sm text-slate-700 leading-relaxed font-medium">
                {analysis.summary}
              </p>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {analysis.actionableAdvice.map((advice, idx) => (
                <div key={idx} className="flex items-start space-x-2 text-xs text-slate-600 bg-white p-2 rounded-xl border border-slate-50 shadow-sm">
                  <div className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-1.5 flex-shrink-0"></div>
                  <span>{advice}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="py-8 flex flex-col items-center justify-center text-slate-400">
            <History className="w-10 h-10 mb-2 opacity-20" />
            <p className="text-xs">点击上方按钮，让 AI 深度解读您的健康历史</p>
          </div>
        )}

        {/* Mini History Bar Chart Placeholder */}
        <div className="mt-6 flex items-end justify-between h-12 px-2">
          {[40, 60, 45, 70, 55, 30, 80].map((h, i) => (
            <div 
              key={i} 
              className={`w-4 rounded-t-sm transition-all duration-1000 ${i === 6 ? 'bg-teal-500' : 'bg-slate-200'}`} 
              style={{ height: isAnalyzing ? '20%' : `${h}%` }}
            ></div>
          ))}
        </div>
        <div className="flex justify-between px-1 mt-1">
          <span className="text-[8px] text-slate-400 uppercase">7天前</span>
          <span className="text-[8px] text-teal-600 font-bold uppercase">今日</span>
        </div>
      </section>

      {/* Daily Self-Check Section */}
      <section className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-slate-800">晨起快速自检</h3>
          {!showCheckIn && (
            <button 
              onClick={() => setShowCheckIn(true)}
              className="text-sm text-teal-600 font-semibold"
            >
              重新录入
            </button>
          )}
        </div>

        {showCheckIn ? (
          <div className="space-y-5">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-bold text-slate-700">血压录入</label>
                <div className="flex bg-slate-100 p-1 rounded-xl">
                  <button 
                    onClick={() => setRecord({...record, bpHand: 'left'})}
                    className={`px-3 py-1 text-[10px] font-bold rounded-lg transition-all ${record.bpHand === 'left' ? 'bg-white text-teal-600 shadow-sm' : 'text-slate-400'}`}
                  >
                    左手
                  </button>
                  <button 
                    onClick={() => setRecord({...record, bpHand: 'right'})}
                    className={`px-3 py-1 text-[10px] font-bold rounded-lg transition-all ${record.bpHand === 'right' ? 'bg-white text-teal-600 shadow-sm' : 'text-slate-400'}`}
                  >
                    右手
                  </button>
                </div>
              </div>
              <div className="flex space-x-2">
                <div className="relative flex-1">
                  <input 
                    type="number" 
                    placeholder="收缩压" 
                    className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-800 font-bold text-center"
                    value={record.systolic || ''}
                    onChange={(e) => setRecord({...record, systolic: Number(e.target.value)})}
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-slate-300">SYS</span>
                </div>
                <div className="relative flex-1">
                  <input 
                    type="number" 
                    placeholder="舒张压" 
                    className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-800 font-bold text-center"
                    value={record.diastolic || ''}
                    onChange={(e) => setRecord({...record, diastolic: Number(e.target.value)})}
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-slate-300">DIA</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button 
                onClick={() => setRecord({...record, edema: !record.edema})}
                className={`p-4 rounded-xl border text-left transition-all ${record.edema ? 'bg-amber-50 border-amber-300' : 'bg-slate-50 border-slate-200'}`}
              >
                <Thermometer className={`w-5 h-5 mb-1 ${record.edema ? 'text-amber-600' : 'text-slate-400'}`} />
                <p className="text-sm font-semibold">脚踝浮肿</p>
                <p className="text-[10px] text-slate-500">{record.edema ? '按压回弹慢' : '无明显肿胀'}</p>
              </button>
              <button 
                onClick={() => setRecord({...record, hematuria: !record.hematuria})}
                className={`p-4 rounded-xl border text-left transition-all ${record.hematuria ? 'bg-red-50 border-red-300' : 'bg-slate-50 border-slate-200'}`}
              >
                <Droplets className={`w-5 h-5 mb-1 ${record.hematuria ? 'text-red-600' : 'text-slate-400'}`} />
                <p className="text-sm font-semibold">尿液异常</p>
                <p className="text-[10px] text-slate-500">{record.hematuria ? '肉眼可见红/深' : '清亮无异常'}</p>
              </button>
            </div>

            <button 
              onClick={() => setShowCheckIn(false)}
              className="w-full bg-teal-600 text-white py-4 rounded-2xl font-bold hover:bg-teal-700 transition-colors shadow-lg shadow-teal-50"
            >
              保存今日状态
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between text-slate-600">
            <div className="flex items-center space-x-4">
              <div className="flex flex-col items-center">
                <PulseIcon className={`w-5 h-5 ${record.foamyUrine ? 'text-amber-500' : 'text-teal-500'}`} />
                <span className="text-[10px] mt-1 font-bold">泡沫</span>
              </div>
              <div className="flex flex-col items-center">
                <Weight className="w-5 h-5 text-teal-500" />
                <span className="text-[10px] mt-1 font-bold">稳定</span>
              </div>
            </div>
            <p className="text-sm italic">“今日数据已同步，肾脏很喜欢这个节奏。”</p>
          </div>
        )}
      </section>

      {/* Designer Pace Guard - LIGHT THEME */}
      <section className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-800">⏳ 工作卫士</h3>
            <p className="text-xs text-slate-400 italic">不要为了画一张图，丢掉一个肾单位。</p>
          </div>
          <div className="p-2 bg-slate-50 rounded-xl">
            <Sparkles className="w-5 h-5 text-teal-500" />
          </div>
        </div>
        
        <div className="flex items-end justify-between">
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">下次休息倒计时</p>
            <p className="text-3xl font-mono font-bold tracking-tighter text-slate-800">42:15</p>
          </div>
          <div className="flex flex-col items-end">
            <div className="flex space-x-1 mb-2">
              {[1,2,3,4].map(i => (
                <div key={i} className={`h-1 w-6 rounded-full ${i <= 3 ? 'bg-teal-500' : 'bg-slate-200'}`}></div>
              ))}
            </div>
            <p className="text-[10px] text-slate-500 font-medium">今日已完成 3 次深度设计周期</p>
          </div>
        </div>

        <div className="mt-6 flex space-x-3">
          <button className="flex-1 bg-slate-50 text-slate-600 py-3 rounded-xl text-xs font-bold hover:bg-slate-100 transition-colors border border-slate-100">暂停节奏</button>
          <button className="flex-1 bg-teal-600 text-white py-3 rounded-xl text-xs font-bold hover:bg-teal-700 transition-colors shadow-sm shadow-teal-100">开启休息</button>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
