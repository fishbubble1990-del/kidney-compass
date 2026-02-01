
import React from 'react';
import { LayoutDashboard, Footprints, Utensils, CalendarDays } from 'lucide-react';
import { AppTab } from '../types';

interface NavigationProps {
  activeTab: AppTab;
  setActiveTab: (tab: AppTab) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: AppTab.DASHBOARD, label: '主页', icon: LayoutDashboard },
    { id: AppTab.ACTIVITY, label: '体力', icon: Footprints },
    { id: AppTab.DIET, label: '饮食', icon: Utensils },
    { id: AppTab.CHECKUP, label: '复查', icon: CalendarDays },
  ];

  return (
    <nav className="flex-shrink-0 bg-white/95 backdrop-blur-md border-t border-slate-100 flex justify-around items-center h-16 safe-bottom z-50 px-2 shadow-[0_-4px_20px_rgba(0,0,0,0.03)]">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex flex-col items-center justify-center w-full h-full transition-all duration-300 relative ${
              isActive ? 'text-teal-600 scale-110' : 'text-slate-400'
            }`}
          >
            {isActive && (
              <div className="absolute top-0 w-8 h-1 bg-teal-600 rounded-full blur-[2px] opacity-20" />
            )}
            <Icon className={`w-5 h-5 mb-1 ${isActive ? 'stroke-[2.5px]' : 'stroke-[1.8px]'}`} />
            <span className={`text-[10px] font-bold ${isActive ? 'opacity-100' : 'opacity-70'}`}>
              {tab.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
};

export default Navigation;
