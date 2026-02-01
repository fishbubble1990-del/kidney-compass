
import React from 'react';
import { 
  Bell, Shield, LogOut, ChevronRight, 
  Smartphone, Moon, Database, Heart, ArrowLeft, Compass, Users, Activity, ExternalLink
} from 'lucide-react';

interface SettingsProps {
  onClose: () => void;
  onLogout: () => void;
  ckdStage: string;
}

const Settings: React.FC<SettingsProps> = ({ onClose, onLogout, ckdStage }) => {
  const sections = [
    {
      title: "健康偏好与预警 (Health Preference)",
      items: [
        { icon: Bell, label: "警戒值提醒", value: "敏感模式", color: "text-teal-600", bg: "bg-teal-50" },
        { icon: Activity, label: "实时数据监控", value: "已同步", color: "text-teal-600", bg: "bg-teal-50" },
        { icon: Moon, label: "夜间模式", value: "智能跟随", color: "text-teal-600", bg: "bg-teal-50" },
      ]
    },
    {
      title: "数据安全性 (Data Security)",
      items: [
        { icon: Database, label: "云端备份", value: "12:30 自动", color: "text-teal-600", bg: "bg-teal-50" },
        { icon: Shield, label: "隐私保护设置", value: "最高等级", color: "text-slate-500", bg: "bg-slate-50" },
        { icon: Smartphone, label: "绑定健康设备", value: "Apple Watch", color: "text-slate-800", bg: "bg-slate-100" },
      ]
    }
  ];

  return (
    <div className="fixed inset-0 z-[100] bg-slate-50 flex flex-col animate-in slide-in-from-right duration-400 ease-out">
      {/* 头部导航 */}
      <header className="p-4 flex items-center bg-white/90 backdrop-blur-lg sticky top-0 border-b border-slate-100 z-10">
        <button onClick={onClose} className="p-2 -ml-2 hover:bg-slate-100 rounded-full text-slate-400 transition-colors">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <h2 className="ml-2 text-lg font-black text-slate-800">系统设置</h2>
      </header>

      <div className="flex-1 overflow-y-auto">
        {/* 用户临床信息卡片 */}
        <div className="p-8 bg-white border-b border-slate-50 flex flex-col items-center">
          <div className="relative mb-4">
            <div className="w-24 h-24 rounded-[40px] p-1 bg-gradient-to-br from-teal-400 to-teal-600 shadow-2xl">
              <div className="w-full h-full rounded-[36px] border-4 border-white overflow-hidden bg-slate-100">
                <img src="https://picsum.photos/seed/medical/200/200" alt="Avatar" className="w-full h-full object-cover" />
              </div>
            </div>
            <div className="absolute -bottom-1 -right-1 bg-teal-500 border-2 border-white w-6 h-6 rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            </div>
          </div>
          <div className="text-center">
            <h3 className="text-xl font-black text-slate-800">王志远 (ID: 0892)</h3>
            <div className="flex items-center justify-center mt-2 space-x-2">
              <span className="text-[10px] font-black px-2 py-1 bg-teal-100 text-teal-700 rounded-lg uppercase">IgA Nephropathy</span>
              <span className="text-[10px] font-black px-2 py-1 bg-teal-600 text-white rounded-lg uppercase">{ckdStage}</span>
            </div>
          </div>
        </div>

        {/* 功能列表 */}
        <div className="p-5 space-y-8 pb-12">
          {sections.map((section, idx) => (
            <div key={idx} className="space-y-3">
              <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest px-2">{section.title}</h4>
              <div className="bg-white rounded-[28px] border border-slate-100 shadow-sm overflow-hidden">
                {section.items.map((item, i) => (
                  <button 
                    key={i} 
                    className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0"
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`p-2.5 ${item.bg} rounded-2xl ${item.color}`}>
                        <item.icon className="w-4 h-4" strokeWidth={2.5} />
                      </div>
                      <span className="text-sm font-bold text-slate-700">{item.label}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-slate-300">
                      <span className="text-[11px] font-bold mr-1 text-slate-400">{item.value}</span>
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}

          {/* 账户操作 */}
          <div className="px-2 pt-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <button 
                onClick={onLogout}
                className="py-4 bg-white border border-slate-200 text-slate-600 rounded-2xl font-bold flex flex-col items-center justify-center space-y-2 shadow-sm hover:border-teal-100 hover:text-teal-600 transition-all active:scale-95"
              >
                <Users className="w-5 h-5" />
                <span className="text-xs">切换账号</span>
              </button>
              
              <button 
                onClick={onLogout}
                className="py-4 bg-white border border-red-100 text-red-500 rounded-2xl font-bold flex flex-col items-center justify-center space-y-2 shadow-sm hover:bg-red-50 transition-all active:scale-95"
              >
                <LogOut className="w-5 h-5" />
                <span className="text-xs">退出登录</span>
              </button>
            </div>
            
            <div className="bg-teal-50 p-4 rounded-2xl border border-teal-100 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <ExternalLink className="w-4 h-4 text-teal-600" />
                <span className="text-xs font-bold text-teal-800">导出年度健康报表 (.PDF)</span>
              </div>
              <ChevronRight className="w-4 h-4 text-teal-400" />
            </div>

            <div className="mt-8 flex flex-col items-center opacity-30 space-y-2">
              <Compass className="w-6 h-6 text-slate-400" />
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Verified Digital Health Platform</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
