
import React, { useState, useRef } from 'react';
import { Utensils, GlassWater, Search, Loader2, Info, Skull, ChefHat, RefreshCw, Leaf } from 'lucide-react';
import { classifyItem, getKidneyFriendlyRecipe } from '../services/geminiService';
import { DailyRecord, ActivityClassification, Recipe } from '../types';

interface DietWaterManagerProps {
  record: DailyRecord;
  setRecord: (r: DailyRecord) => void;
}

const DietWaterManager: React.FC<DietWaterManagerProps> = ({ record, setRecord }) => {
  const [foodQuery, setFoodQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [foodResult, setFoodResult] = useState<ActivityClassification | null>(null);
  
  // Recipe State
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [isRecipeLoading, setIsRecipeLoading] = useState(false);

  // Water Progress Bar State
  const progressBarRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const goal = 2000;
  const maxBarValue = 3000; // Max visual range for the slider

  const addWater = (amount: number) => {
    setRecord({ ...record, waterIntake: record.waterIntake + amount });
  };

  // Interactive Progress Bar Handlers
  const updateWaterFromPointer = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!progressBarRef.current) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    // Clamp x position between 0 and width
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const percentage = x / rect.width;
    // Calculate water amount, snap to nearest 50ml
    const newWater = Math.round((percentage * maxBarValue) / 50) * 50;
    setRecord({ ...record, waterIntake: newWater });
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    setIsDragging(true);
    progressBarRef.current?.setPointerCapture(e.pointerId);
    updateWaterFromPointer(e);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isDragging) {
      updateWaterFromPointer(e);
    }
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    setIsDragging(false);
    progressBarRef.current?.releasePointerCapture(e.pointerId);
  };

  const barWidthPercent = Math.min((record.waterIntake / maxBarValue) * 100, 100);

  const handleFoodSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!foodQuery.trim()) return;
    setIsLoading(true);
    const res = await classifyItem(foodQuery, 'food');
    setFoodResult(res);
    setIsLoading(false);
  };

  const generateRecipe = async () => {
    setIsRecipeLoading(true);
    const newRecipe = await getKidneyFriendlyRecipe();
    setRecipe(newRecipe);
    setIsRecipeLoading(false);
  };

  return (
    <div className="space-y-6 pb-24">
      <header className="flex items-center space-x-3">
        <div className="p-2 bg-blue-100 rounded-xl">
          <Utensils className="text-blue-600 w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-800">饮食与饮水管家</h2>
          <p className="text-xs text-slate-500">分时段补水，精细化控盐控嘌呤。</p>
        </div>
      </header>

      {/* Water Tracker */}
      <section className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-lg font-bold flex items-center">
              <GlassWater className="w-5 h-5 text-blue-500 mr-2" /> 饮水进度
            </h3>
            <p className="text-xs text-slate-500 mt-1">目标：{goal}ml / 建议：150ml/h</p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-black text-blue-600">{record.waterIntake}</span>
            <span className="text-xs text-slate-400"> / {goal} ml</span>
          </div>
        </div>

        {/* Draggable Progress Bar */}
        <div className="relative mb-6 pt-2 pb-2">
          <div 
            ref={progressBarRef}
            className="relative w-full h-5 bg-slate-100 rounded-full cursor-pointer touch-none select-none"
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
          >
             {/* Goal Marker Line (2000ml) */}
            <div 
              className="absolute top-0 bottom-0 w-[2px] bg-slate-300 z-0" 
              style={{ left: `${(goal / maxBarValue) * 100}%` }}
            ></div>

            {/* Filled Bar */}
            <div 
              className={`absolute left-0 top-0 bottom-0 bg-blue-500 rounded-full ${isDragging ? '' : 'transition-all duration-300 ease-out'}`}
              style={{ width: `${barWidthPercent}%` }}
            ></div>

            {/* Drag Handle */}
            <div 
              className={`absolute top-1/2 w-6 h-6 bg-white border-2 border-blue-500 rounded-full shadow-md z-10 flex items-center justify-center ${isDragging ? 'scale-110' : 'transition-all duration-300 ease-out'}`}
              style={{ 
                left: `${barWidthPercent}%`, 
                transform: 'translate(-50%, -50%)' 
              }}
            >
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
            </div>
          </div>
          <div className="flex justify-between mt-1 px-1">
             <span className="text-[10px] text-slate-400">0ml</span>
             <span className="text-[10px] text-slate-400 pl-8">目标 2000ml</span>
             <span className="text-[10px] text-slate-400">3000ml</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          {[150, 250, 500].map(amount => (
            <button 
              key={amount}
              onClick={() => addWater(amount)}
              className="py-3 bg-blue-50 text-blue-700 font-bold rounded-xl border border-blue-100 active:scale-95 transition-transform"
            >
              +{amount}ml
            </button>
          ))}
        </div>
        
        {record.waterIntake < 1500 && (
          <div className="mt-4 p-3 bg-amber-50 text-amber-700 rounded-xl flex items-start space-x-2 border border-amber-100">
            <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <p className="text-xs font-medium">当前补水不足，可能增加尿酸沉积风险，请及时补充。</p>
          </div>
        )}
      </section>

      {/* Recipe Generator Section */}
      <section className="bg-gradient-to-br from-teal-50 to-emerald-50 p-6 rounded-3xl border border-teal-100 relative overflow-hidden">
        <div className="flex justify-between items-center mb-4 relative z-10">
          <h3 className="text-lg font-bold text-teal-800 flex items-center">
            <ChefHat className="w-5 h-5 mr-2" /> 今日护肾灵感
          </h3>
          <button 
            onClick={generateRecipe}
            disabled={isRecipeLoading}
            className="flex items-center justify-center w-24 h-8 bg-white text-teal-700 rounded-full font-bold shadow-sm hover:shadow-md transition-all active:scale-95 disabled:opacity-50"
          >
            {isRecipeLoading ? (
              <Loader2 className="w-4 h-4 animate-spin text-teal-500 origin-center" />
            ) : (
              <div className="flex items-center space-x-1 text-xs">
                <RefreshCw className="w-3 h-3" />
                <span>{recipe ? '换一个' : '生成食谱'}</span>
              </div>
            )}
          </button>
        </div>

        <Leaf className="absolute -right-4 -bottom-4 w-24 h-24 text-teal-200 opacity-30 rotate-12" />

        {!recipe && !isRecipeLoading && (
          <div className="text-center py-6 text-teal-600/60 text-sm">
            <p>不知道吃什么？</p>
            <p className="text-xs mt-1">点击右上角，生成低盐低脂优质蛋白食谱</p>
          </div>
        )}

        {isRecipeLoading && (
          <div className="py-8 flex flex-col items-center justify-center space-y-3">
            <div className="w-10 h-10 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-teal-500 animate-spin origin-center" />
            </div>
            <p className="text-xs text-teal-600 animate-pulse">正在为您调配营养食材...</p>
          </div>
        )}

        {recipe && !isRecipeLoading && (
          <div className="relative z-10 bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-white animate-in fade-in slide-in-from-bottom-2">
            <div className="flex justify-between items-start mb-2">
              <h4 className="text-lg font-black text-slate-800">{recipe.dishName}</h4>
            </div>
            
            <div className="flex flex-wrap gap-1 mb-3">
              {recipe.tags.map((tag, i) => (
                <span key={i} className="text-[10px] font-bold bg-teal-100 text-teal-700 px-2 py-0.5 rounded-md">
                  {tag}
                </span>
              ))}
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-xs font-bold text-slate-500 mb-1 uppercase tracking-wider">食材准备</p>
                <div className="flex flex-wrap gap-2">
                  {recipe.ingredients.map((ing, i) => (
                    <span key={i} className="text-xs text-slate-700 bg-slate-100 px-2 py-1 rounded-lg">{ing}</span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-bold text-slate-500 mb-1 uppercase tracking-wider">烹饪步骤</p>
                <ol className="list-decimal list-inside space-y-1">
                  {recipe.steps.map((step, i) => (
                    <li key={i} className="text-xs text-slate-600 leading-relaxed pl-1 marker:text-teal-500 marker:font-bold">
                      {step}
                    </li>
                  ))}
                </ol>
              </div>

              <div className="bg-teal-50 p-2 rounded-lg border border-teal-100 mt-2">
                <p className="text-[10px] text-teal-800 leading-tight">
                  <span className="font-bold">✨ 推荐理由：</span>{recipe.nutritionBenefit}
                </p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Food/Med Search */}
      <section className="space-y-4 pt-2">
        <h3 className="text-sm font-bold text-slate-600 flex items-center">
          <Search className="w-4 h-4 mr-1" /> 黑白名单查询 (含用药风险)
        </h3>
        <form onSubmit={handleFoodSearch} className="relative">
          <input 
            type="text" 
            placeholder="搜“火锅”、“豆腐”、“布洛芬”..."
            className="w-full p-4 pl-4 pr-12 bg-white border border-slate-200 rounded-2xl shadow-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            value={foodQuery}
            onChange={(e) => setFoodQuery(e.target.value)}
          />
          <button 
            type="submit" 
            disabled={isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-xl hover:bg-slate-50 transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin text-blue-500 origin-center" />
            ) : (
              <Search className="w-5 h-5 text-slate-400" />
            )}
          </button>
        </form>

        {foodResult && (
          <div className={`p-5 rounded-3xl border animate-in fade-in slide-in-from-top-4 ${
            foodResult.level === 'red' ? 'bg-red-50 border-red-200' : 
            foodResult.level === 'yellow' ? 'bg-amber-50 border-amber-200' : 'bg-teal-50 border-teal-200'
          }`}>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-lg font-bold text-slate-800">{foodResult.name}</h4>
              {foodResult.level === 'red' ? <Skull className="w-6 h-6 text-red-600" /> : <Info className={`w-6 h-6 ${foodResult.level === 'yellow' ? 'text-amber-500' : 'text-teal-500'}`} />}
            </div>
            <p className="text-sm text-slate-600 mb-2 font-medium">{foodResult.reason}</p>
            <p className="text-xs text-slate-500 bg-white bg-opacity-40 p-2 rounded-lg italic">
              建议：{foodResult.advice}
            </p>
          </div>
        )}
      </section>
    </div>
  );
};

export default DietWaterManager;
