
export type StatusLevel = 'green' | 'yellow' | 'red';

export interface DailyRecord {
  date: string;
  weight: number;
  systolic: number;
  diastolic: number;
  bpHand: 'left' | 'right'; // Added to track measurement arm
  edema: boolean;
  hematuria: boolean;
  foamyUrine: boolean;
  waterIntake: number; // ml
}

export interface HealthAnalysis {
  summary: string;
  trend: 'improving' | 'stable' | 'declining';
  actionableAdvice: string[];
}

export interface ActivityClassification {
  name: string;
  level: StatusLevel;
  reason: string;
  advice: string;
}

export interface Recipe {
  dishName: string;
  tags: string[]; // e.g., "Low Potassium", "High Protein"
  ingredients: string[];
  steps: string[];
  nutritionBenefit: string; // Why is this good for CKD?
}

export interface ReportAnalysis {
  date: string;
  indicators: {
    creatinine: string; // 肌酐
    egfr: string;       // 肾小球滤过率
    uricAcid: string;   // 尿酸
    proteinuria: string; // 尿蛋白
  };
  status: 'stable' | 'warning' | 'critical';
  tailoredStrategy: string; // 定制化策略
}

export enum AppTab {
  DASHBOARD = 'dashboard',
  ACTIVITY = 'activity',
  DIET = 'diet',
  CHECKUP = 'checkup'
}

export interface WorkSession {
  type: 'work' | 'break';
  startTime: number;
  durationMinutes: number;
}
