
import React, { useState, useRef } from 'react';
import { 
  CalendarDays, Pill, Bell, ClipboardList, ChevronRight, Upload, 
  ScanLine, FileText, CheckCircle, Loader2, Check, FlaskConical,
  X, Info, UtensilsCrossed, Zap, ShieldCheck, Activity
} from 'lucide-react';
import { analyzeMedicalReport } from '../services/geminiService';
import { ReportAnalysis } from '../types';

const CheckupCalendar: React.FC = () => {
  const [report, setReport] = useState<ReportAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const checkupDaysLeft = 14;
  
  const 必查项目 = [
    { name: "肌酐 (Cr)", desc: "衡量血液中代谢废物的排泄效率", icon: Zap, color: "text-blue-500", bg: "bg-blue-50" },
    { name: "eGFR", desc: "肾小球滤过率：肾脏核心“工作效率”", icon: Activity, color: "text-indigo-500", bg: "bg-indigo-50" },
    { name: "ACR/PCR", desc: "尿蛋白/肌酐比：检测肾脏滤网是否破损", icon: ShieldCheck, color: "text-emerald-500", bg: "bg-emerald-50" },
    { name: "血尿酸", desc: "高尿酸会导致结晶沉积，加重肾损", icon: FlaskConical, color: "text-amber-500", bg: "bg-amber-50" },
    { name: "血钾", desc: "维持心脏跳动与神经电位稳定的关键", icon: Zap, color: "text-red-500", bg: "bg-red-50" }
  ];

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsAnalyzing(true);
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64String = (reader.result as string).split(',')[1];
      try {
        const result = await analyzeMedicalReport(base64String);
        setReport(result);
      } catch (e) {
        console.error("Analysis failed", e);
      } finally {
        setIsAnalyzing(false);
      }
    };
    reader.readAsDataURL(file);
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-6 pb-24">
      <header className="flex items-center space-x-3">
        <div className="p-2 bg-indigo-100 rounded-xl">
          <CalendarDays className="text-indigo-600 w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-800">药物与复查</h2>
          <p className="text-xs text-slate-500">上传报告，定制您的健康防线。</p>
        </div>
      </header>

      {/* Report Analyzer Section */}
      <section className="bg-gradient-to-r from-violet-500 to-indigo-600 rounded-3xl p-1 shadow-lg">
        <div className="bg-white rounded-[20px] p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-slate-800 flex items-center">
              <ScanLine className="w-5 h-5 text-indigo-500 mr-2" /> 智能报告解读
            </h3>
            {!isAnalyzing && (
              <button 
                onClick={triggerUpload}
                className="flex items-center space-x-1 text-xs bg-indigo-50 text-indigo-600 px-3 py-1.5 rounded-full font-bold hover:bg-indigo-100 transition-colors"
              >
                <Upload className="w-3 h-3" />
                <span>上传化验单</span>
              </button>
            )}
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept="image/*"
              onChange={handleFileUpload}
            />
          </div>

          {isAnalyzing && (
            <div className="py-8 text-center flex flex-col items-center justify-center space-y-3">
              <Loader2 className="w-8 h-8 text-indigo-500 animate-spin origin-center" />
              <p className="text-xs text-indigo-600 font-medium animate-pulse">
                正在识别关键指标并生成策略...
              </p>
            </div>
          )}

          {!isAnalyzing && !report && (
            <div 
              onClick={triggerUpload}
              className="border-2 border-dashed border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center text-slate-400 cursor-pointer hover:bg-slate-50 transition-colors"
            >
              <FileText className="w-8 h-8 mb-2 opacity-50" />
              <p className="text-xs">点击上传或拍摄最新复查报告</p>
              <p className="text-[10px] opacity-60 mt-1">支持识别肌酐、eGFR、尿酸等指标</p>
            </div>
          )}

          {!isAnalyzing && report && (
            <div className="space-y-4 animate-in fade-in zoom-in-95 duration-300">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                  <p className="text-[10px] text-slate-400 uppercase tracking-wider font-bold">肌酐 (Creatinine)</p>
                  <p className="text-lg font-black text-slate-800">{report.indicators.creatinine}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                  <p className="text-[10px] text-slate-400 uppercase tracking-wider font-bold">eGFR</p>
                  <p className={`text-lg font-black ${report.status === 'warning' ? 'text-amber-600' : 'text-slate-800'}`}>
                    {report.indicators.egfr}
                  </p>
                </div>
              </div>
              
              <div className={`p-4 rounded-xl border ${
                report.status === 'warning' ? 'bg-amber-50 border-amber-100' : 
                report.status === 'critical' ? 'bg-red-50 border-red-100' : 
                'bg-emerald-50 border-emerald-100'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className={`w-4 h-4 ${
                     report.status === 'warning' ? 'text-amber-500' : 
                     report.status === 'critical' ? 'text-red-500' : 'text-emerald-500'
                  }`} />
                  <span className="text-sm font-bold text-slate-800">下阶段定制策略</span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed font-medium">
                  {report.tailoredStrategy}
                </p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Meds Section */}
      <section className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-bold flex items-center text-slate-800">
            <Pill className="w-5 h-5 text-indigo-500 mr-2" /> 今日用药
          </h3>
          <Bell className="w-5 h-5 text-slate-300" />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-200">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600 shadow-sm">
                <Pill className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-800">沙坦类降压药 (ARB)</p>
                <p className="text-xs text-slate-500">早餐后 1 片</p>
              </div>
            </div>
            <div className="relative flex items-center justify-center">
              <input 
                type="checkbox" 
                className="peer appearance-none w-6 h-6 border-2 border-slate-300 rounded-lg checked:bg-indigo-600 checked:border-indigo-600 transition-all cursor-pointer"
                defaultChecked 
              />
              <Check className="absolute w-4 h-4 text-white opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity" strokeWidth={3} />
            </div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-200">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600 shadow-sm">
                <FlaskConical className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-800">非布司他</p>
                <p className="text-xs text-slate-500">睡前 0.5 片</p>
              </div>
            </div>
            <div className="relative flex items-center justify-center">
              <input 
                type="checkbox" 
                className="peer appearance-none w-6 h-6 border-2 border-slate-300 rounded-lg checked:bg-indigo-600 checked:border-indigo-600 transition-all cursor-pointer" 
              />
              <Check className="absolute w-4 h-4 text-white opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity" strokeWidth={3} />
            </div>
          </div>
        </div>
      </section>

      {/* Clickable Checkup Checklist Section */}
      <section 
        onClick={() => setIsDetailsOpen(true)}
        className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 cursor-pointer hover:bg-slate-50 active:scale-[0.98] transition-all"
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold flex items-center text-slate-800">
            <ClipboardList className="w-5 h-5 text-indigo-500 mr-2" /> 复查清单生成
          </h3>
          <ChevronRight className="w-5 h-5 text-slate-300" />
        </div>
        <div className="flex flex-wrap gap-2">
          {必查项目.map(item => (
            <span key={item.name} className="px-3 py-1 bg-indigo-50 text-indigo-700 text-[10px] font-bold rounded-full">
              {item.name}
            </span>
          ))}
        </div>
        <p className="mt-4 text-[11px] text-slate-400 text-center italic">点击展开详细复查指标解读及注意事项</p>
      </section>
      
      {/* Checkup Countdown */}
      <div className="text-center pb-4">
        <p className="text-xs text-slate-400">距离下次常规复查还有 <span className="text-indigo-600 font-bold">{checkupDaysLeft}</span> 天</p>
      </div>

      {/* Detailed Checklist Modal Overlay */}
      {isDetailsOpen && (
        <div className="fixed inset-0 z-[60] flex items-end justify-center animate-in fade-in duration-300">
          <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={() => setIsDetailsOpen(false)}></div>
          <div className="relative w-full max-w-md bg-slate-50 rounded-t-[40px] shadow-2xl overflow-hidden max-h-[90vh] flex flex-col animate-in slide-in-from-bottom-full duration-500">
            <div className="flex justify-between items-center p-6 bg-white border-b border-slate-100">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-indigo-100 rounded-xl">
                  <ClipboardList className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-slate-800">复查深度解析</h3>
                  <p className="text-[10px] text-slate-400 font-bold uppercase">Clinical Intelligence</p>
                </div>
              </div>
              <button 
                onClick={() => setIsDetailsOpen(false)}
                className="w-10 h-10 flex items-center justify-center bg-slate-100 rounded-full text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Prep Advice */}
              <div className="bg-emerald-50 border border-emerald-100 rounded-3xl p-5 flex space-x-4">
                <UtensilsCrossed className="w-6 h-6 text-emerald-600 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-bold text-emerald-900">复查前准备</h4>
                  <p className="text-xs text-emerald-700 mt-1 leading-relaxed">
                    前三天低蛋白饮食，复查当天清晨空腹（禁食禁水），避开感冒或剧烈运动。
                  </p>
                </div>
              </div>

              {/* Indicator List */}
              <div className="space-y-3">
                <h4 className="text-xs font-black text-slate-400 uppercase px-1">核心检测项</h4>
                {必查项目.map((item, i) => (
                  <div key={i} className="bg-white p-4 rounded-3xl border border-slate-100 shadow-sm flex items-start space-x-4">
                    <div className={`p-3 ${item.bg} rounded-2xl flex-shrink-0`}>
                      <item.icon className={`w-5 h-5 ${item.color}`} />
                    </div>
                    <div>
                      <p className="text-sm font-black text-slate-800">{item.name}</p>
                      <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Extra Tip */}
              <div className="bg-white p-5 rounded-3xl border border-indigo-100 shadow-sm flex items-start space-x-3">
                <Info className="w-5 h-5 text-indigo-500 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-slate-600 leading-relaxed italic">
                  * 建议每次都在同一家实验室检测，以确保数据对比的可靠性。如有异常，请及时联系主治医师。
                </p>
              </div>
            </div>

            <div className="p-6 bg-white border-t border-slate-100">
              <button 
                onClick={() => setIsDetailsOpen(false)}
                className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold text-sm shadow-lg shadow-indigo-100 active:scale-95 transition-all"
              >
                我知道了
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CheckupCalendar;
