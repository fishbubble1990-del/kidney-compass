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
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

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
