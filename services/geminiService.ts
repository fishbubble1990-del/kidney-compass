
import { ActivityClassification, DailyRecord, HealthAnalysis, Recipe, ReportAnalysis } from "../types";

const API_BASE_URL = "https://huggingface.co/spaces/fishbubble1234/kidney-compass-backend";

export const classifyItem = async (query: string, type: 'activity' | 'food' | 'medicine'): Promise<ActivityClassification> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/classify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, type })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Classify Error:", error);
    return { name: query, level: 'yellow', reason: "连接服务器失败，请稍后重试", advice: "咨询医生" };
  }
};

export const analyzeHealthTrends = async (history: DailyRecord[]): Promise<HealthAnalysis> => {
  // Placeholder: If/When backend supports this, switch to fetch
  // Currently returning static/fallback data to prevent crash if backend endpoint doesn't exist yet
  // or if we want to migrate this later.
  console.warn("analyzeHealthTrends is currently disabled/mocked until backend endpoint is ready.");
  return {
    summary: "AI 分析服务升级中...",
    trend: "stable",
    actionableAdvice: ["保持健康饮食", "注意休息"]
  };
};

export const getKidneyFriendlyRecipe = async (): Promise<Recipe> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recipe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Recipe Gen Error:", error);
    return {
      dishName: "清蒸鲈鱼 (示例)",
      tags: ["优质蛋白", "低油"],
      ingredients: ["鲈鱼 1条", "姜丝 适量", "葱段 适量", "低钠酱油 少许"],
      steps: ["鲈鱼洗净划刀", "放姜葱蒸8分钟", "倒掉汤汁淋少许热油和酱油"],
      nutritionBenefit: "后端连接失败，显示的为示例数据。"
    };
  }
};

export const analyzeMedicalReport = async (imageBase64: string): Promise<ReportAnalysis> => {
  // Placeholder
  console.warn("analyzeMedicalReport is currently disabled/mocked.");
  return {
    date: new Date().toISOString(),
    indicators: { creatinine: "?", egfr: "?", uricAcid: "?", proteinuria: "?" },
    status: 'warning',
    tailoredStrategy: "图片分析服务升级中..."
  };
};
