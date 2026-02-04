import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 加载环境变量
load_dotenv()

# 获取 Supabase 配置
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
gemini_key: str = os.environ.get("GEMINI_API_KEY")

if not url or not key or "your_supabase" in url:
    print("警告: 未检测到有效的 SUPABASE_URL 或 SUPABASE_KEY，请检查 .env 文件")

# 初始化 Supabase 客户端
supabase: Client = create_client(url, key) if url and key and "your_supabase" not in url else None

# 初始化 Gemini 客户端
ai_client = genai.Client(api_key=gemini_key) if gemini_key else None

app = FastAPI()

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为前端的实际 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求模型
class UserLogin(BaseModel):
    email: str
    password: str

class QueryItem(BaseModel):
    query: str
    type: str = "food"  # food, activity, medicine

# 路由定义
@app.get("/")
def read_root():
    return {"message": "Kidney Compass Backend is running!"}

@app.post("/api/classify")
async def classify_item(item: QueryItem):
    if not ai_client:
        raise HTTPException(status_code=500, detail="Server missing GEMINI_API_KEY")
    
    system_instruction = """
    You are a friendly medical expert assistant for a 36-year-old male designer with IgA Nephropathy (CKD Stage 3).
    Classify input into RED (Absolute NO), YELLOW (Caution), GREEN (Safe).
    Output MUST be in JSON format.
    IMPORTANT: The 'reason' and 'advice' fields MUST be in Simplified Chinese (简体中文).
    """

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f'Query: "{item.query}" (Type: {item.type})',
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": types.Type.OBJECT,
                    "properties": {
                        "name": {"type": types.Type.STRING},
                        "level": {"type": types.Type.STRING, "enum": ['green', 'yellow', 'red']},
                        "reason": {"type": types.Type.STRING},
                        "advice": {"type": types.Type.STRING}
                    },
                    "required": ['name', 'level', 'reason', 'advice']
                }
            }
        )
        return response.parsed
    except Exception as e:
        print(f"Gemini Error: {e}")
        # 返回预设的分类结果，避免因 API 配额不足导致应用无法使用
        preset_results = {
            "火锅": {
                "name": "火锅",
                "level": "yellow",
                "reason": "火锅通常含有较高的盐分和嘌呤，可能会增加肾脏负担。",
                "advice": "建议选择清淡汤底，避免食用内脏和加工肉类，控制食用频率。"
            },
            "苹果": {
                "name": "苹果",
                "level": "green",
                "reason": "苹果富含纤维和抗氧化物质，钾含量适中，适合肾病患者食用。",
                "advice": "每天可食用1个中等大小的苹果，最好带皮食用以获取更多营养。"
            },
            "香蕉": {
                "name": "香蕉",
                "level": "yellow",
                "reason": "香蕉钾含量较高，肾功能不全患者需要注意控制摄入量。",
                "advice": "每周食用不超过2次，每次半根，避免在高血钾时食用。"
            }
        }
        
        # 检查查询是否在预设结果中
        if item.query in preset_results:
            return preset_results[item.query]
        else:
            # 返回默认结果
            return {
                "name": item.query,
                "level": "yellow",
                "reason": "API 调用失败，返回默认分类结果。",
                "advice": "建议咨询医生或营养师获取更准确的建议。"
            }

@app.post("/api/recipe")
async def generate_recipe():
    if not ai_client:
        raise HTTPException(status_code=500, detail="Server missing GEMINI_API_KEY")

    system_instruction = """
    You are a renal dietitian specializing in Chinese cuisine for CKD Stage 3 patients.
    Generate a delicious, easy-to-cook recipe that strictly follows these rules:
    - Low Salt (Low Sodium)
    - Low Oil
    - Low Phosphorus
    - Low Potassium
    - High Quality Protein (e.g., Egg whites, Fish, Chicken breast, Lean pork)
    
    The output must be in JSON format.
    IMPORTANT: All text fields (dishName, ingredients, steps, nutritionBenefit) MUST be in Simplified Chinese (简体中文).
    """

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Generate one random lunch or dinner recipe.",
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": types.Type.OBJECT,
                    "properties": {
                        "dishName": {"type": types.Type.STRING},
                        "tags": {"type": types.Type.ARRAY, "items": {"type": types.Type.STRING}},
                        "ingredients": {"type": types.Type.ARRAY, "items": {"type": types.Type.STRING}},
                        "steps": {"type": types.Type.ARRAY, "items": {"type": types.Type.STRING}},
                        "nutritionBenefit": {"type": types.Type.STRING}
                    },
                    "required": ['dishName', 'tags', 'ingredients', 'steps', 'nutritionBenefit']
                }
            }
        )
        return response.parsed
    except Exception as e:
        print(f"Recipe Gen Error: {e}")
        # 返回预设的食谱结果，避免因 API 配额不足导致应用无法使用
        preset_recipes = [
            {
                "dishName": "清蒸鲈鱼",
                "tags": ["优质蛋白", "低油", "低盐", "低磷", "低钾"],
                "ingredients": ["鲈鱼 1条", "姜丝 适量", "葱段 适量", "低钠酱油 少许"],
                "steps": ["鲈鱼洗净划刀", "放姜葱蒸8分钟", "倒掉汤汁淋少许热油和酱油"],
                "nutritionBenefit": "鲈鱼富含优质蛋白质，低脂肪，低磷低钾，适合 IgA CKD 3期和病理4级患者食用。清蒸的烹饪方式保留了鱼肉的营养，同时减少了油脂的摄入。"
            },
            {
                "dishName": "鸡蛋白菜汤",
                "tags": ["优质蛋白", "低磷", "低钾", "低钠", "低蛋白"],
                "ingredients": ["鸡蛋 2个", "白菜 200克", "葱花 适量", "低钠盐 少许"],
                "steps": ["鸡蛋打散", "白菜切丝", "水烧开后加入白菜", "煮沸后淋入蛋液", "加低钠盐调味即可"],
                "nutritionBenefit": "鸡蛋提供优质蛋白质，白菜富含维生素和纤维，低钾低磷低钠，适合 IgA CKD 3期和病理4级患者日常食用。"
            },
            {
                "dishName": "冬瓜排骨汤",
                "tags": ["低磷", "低钾", "低钠", "低蛋白"],
                "ingredients": ["排骨 100克", "冬瓜 200克", "姜 2片", "低钠盐 少许"],
                "steps": ["排骨焯水去血沫", "冬瓜切块", "所有材料放入锅中加水煮30分钟", "加低钠盐调味即可"],
                "nutritionBenefit": "冬瓜有利尿作用，排骨提供少量优质蛋白质，此汤低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "番茄鸡蛋面",
                "tags": ["低磷", "低钾", "低钠", "低蛋白"],
                "ingredients": ["面条 50克", "番茄 1个", "鸡蛋 1个", "葱花 适量", "低钠盐 少许"],
                "steps": ["番茄切块炒软", "加水烧开", "下面条煮至八分熟", "淋入蛋液", "加低钠盐调味即可"],
                "nutritionBenefit": "番茄富含维生素C，鸡蛋提供优质蛋白质，面条提供能量，此餐低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "清炒西兰花",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["西兰花 200克", "蒜末 适量", "低钠盐 少许", "植物油 少许"],
                "steps": ["西兰花切小朵焯水", "锅中放油爆香蒜末", "加入西兰花翻炒", "加低钠盐调味即可"],
                "nutritionBenefit": "西兰花富含维生素和纤维，低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。"
            }
        ]
        
        # 随机返回一个预设食谱
        import random
        return random.choice(preset_recipes)

@app.post("/auth/signup")
def signup(user: UserLogin):
    email = user.email.strip()
    password = user.password.strip()
    
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized. Please check .env file.")
    
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        return {"message": "无需确认邮件，如果 Supabase 关闭了 Confirm Email 则直接注册成功", "data": response}
    except Exception as e:
        # Supabase 返回的 error message 通常包含详细信息
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def login(user: UserLogin):
    email = user.email.strip()
    password = user.password.strip()

    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized. Please check .env file.")
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        return {"token": response.session.access_token, "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=401, detail="登录失败: " + str(e))
