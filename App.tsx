
import React, { useState, useEffect } from 'react';
import { AppTab, DailyRecord } from './types';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import ActivityTrafficLight from './components/ActivityTrafficLight';
import DietWaterManager from './components/DietWaterManager';
import CheckupCalendar from './components/CheckupCalendar';
import Login from './components/Login';
import Settings from './components/Settings';
import { Compass, ChevronDown, MoreHorizontal, Circle } from 'lucide-react';

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState<AppTab>(AppTab.DASHBOARD);
  const [ckdStage, setCkdStage] = useState<string>('CKD 3A');
  const [isStageSelectorOpen, setIsStageSelectorOpen] = useState(false);

  const [record, setRecord] = useState<DailyRecord>({
    date: new Date().toISOString().split('T')[0],
    weight: 72.5,
    systolic: 122,
    diastolic: 78,
    bpHand: 'left',
    edema: false,
    hematuria: false,
    foamyUrine: false,
    waterIntake: 0,
  });

  // Mock historical data
  const [history] = useState<DailyRecord[]>([
    { date: '2023-10-21', weight: 72.1, systolic: 125, diastolic: 82, bpHand: 'left', edema: false, hematuria: false, foamyUrine: true, waterIntake: 1800 },
    { date: '2023-10-22', weight: 72.3, systolic: 128, diastolic: 84, bpHand: 'right', edema: true, hematuria: false, foamyUrine: false, waterIntake: 1500 },
    { date: '2023-10-23', weight: 72.4, systolic: 120, diastolic: 75, bpHand: 'left', edema: false, hematuria: false, foamyUrine: false, waterIntake: 2000 },
    { date: '2023-10-24', weight: 72.6, systolic: 135, diastolic: 88, bpHand: 'left', edema: false, hematuria: false, foamyUrine: true, waterIntake: 1200 },
  ]);

  // 检查本地是否有登录 Token
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  useEffect(() => {
    const checkTime = () => {
      const now = new Date();
      if (now.getHours() >= 23 || (now.getHours() === 22 && now.getMinutes() >= 30)) {
        document.body.classList.add('sepia-[0.3]');
      } else {
        document.body.classList.remove('sepia-[0.3]');
      }
    };
    const interval = setInterval(checkTime, 60000);
    checkTime();
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    setIsLoggedIn(false);
    setShowSettings(false);
    setActiveTab(AppTab.DASHBOARD);
  };

  if (!isLoggedIn) {
    return <Login onLogin={() => setIsLoggedIn(true)} />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case AppTab.DASHBOARD: return <Dashboard record={record} setRecord={setRecord} history={history} />;
      case AppTab.ACTIVITY: return <ActivityTrafficLight />;
      case AppTab.DIET: return <DietWaterManager record={record} setRecord={setRecord} />;
      case AppTab.CHECKUP: return <CheckupCalendar />;
      default: return <Dashboard record={record} setRecord={setRecord} history={history} />;
    }
  };

  const kidneyStages = ['CKD 1', 'CKD 2', 'CKD 3A', 'CKD 3B', 'CKD 4', 'CKD 5'];

  return (
    <div className="h-screen w-full max-w-md mx-auto bg-slate-50 relative flex flex-col shadow-2xl overflow-hidden">
      {/* 顶部导航栏 - 小程序风格适配 */}
      <header className="bg-slate-50/90 backdrop-blur-md sticky top-0 z-40 border-b border-slate-100 flex-shrink-0">
        {/* 系统安全区 */}
        <div className="h-[env(safe-area-inset-top)]" />

        {/* 标题行 */}
        <div className="h-12 px-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(true)}
              className="w-8 h-8 rounded-full bg-slate-200 border-2 border-white shadow-sm overflow-hidden active:scale-90 transition-transform"
            >
              <img src="https://picsum.photos/seed/designer/100/100" alt="Profile" />
            </button>
            <h1 className="text-base font-black text-slate-800 tracking-tight">护肾罗盘</h1>
          </div>

          {/* 右侧模拟胶囊按钮 */}
          <div className="capsule-placeholder">
            <MoreHorizontal className="w-5 h-5 text-slate-400" />
            <div className="w-px h-4 bg-slate-200" />
            <Circle className="w-4 h-4 text-slate-400 fill-current" />
          </div>
        </div>

        {/* 状态选择行 */}
        <div className="px-4 pb-2 flex items-center justify-between">
          <div className="relative">
            <button
              onClick={() => setIsStageSelectorOpen(!isStageSelectorOpen)}
              className="flex items-center space-x-1 text-[10px] font-bold px-3 py-1 bg-teal-100 text-teal-800 rounded-full uppercase tracking-tighter hover:bg-teal-200 transition-colors"
            >
              <span>{ckdStage}</span>
              <ChevronDown className="w-3 h-3" />
            </button>

            {isStageSelectorOpen && (
              <>
                <div className="fixed inset-0 z-10 cursor-default" onClick={() => setIsStageSelectorOpen(false)}></div>
                <div className="absolute top-full left-0 mt-2 w-28 bg-white rounded-xl shadow-xl border border-slate-100 p-1 z-20 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                  {kidneyStages.map((stage) => (
                    <button
                      key={stage}
                      onClick={() => {
                        setCkdStage(stage);
                        setIsStageSelectorOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-xs font-bold rounded-lg transition-colors ${ckdStage === stage ? 'bg-teal-50 text-teal-700' : 'text-slate-600 hover:bg-slate-50'
                        }`}
                    >
                      {stage}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          <div className="flex items-center space-x-1">
            <div className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse"></div>
            <span className="text-[9px] font-bold text-slate-400">AI 实时监护中</span>
          </div>
        </div>
      </header>

      {/* 主内容区域 - 内部滚动 */}
      <main className="flex-1 overflow-y-auto no-scrollbar px-4 pt-4">
        {renderContent()}
      </main>

      {/* 底部导航 */}
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      {showSettings && (
        <Settings
          ckdStage={ckdStage}
          onClose={() => setShowSettings(false)}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
};

export default App;
