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
    # 首先尝试从数据库中查找
    if supabase:
        try:
            result = supabase.table('food_classifications').select('*').eq('name', item.query).eq('type', item.type).execute()
            if result.data and len(result.data) > 0:
                # 从数据库中找到结果
                food_data = result.data[0]
                return {
                    "name": food_data['name'],
                    "level": food_data['level'],
                    "reason": food_data['reason'],
                    "advice": food_data['advice']
                }
        except Exception as db_error:
            print(f"数据库查询错误: {db_error}")
    
    # 如果数据库中没有找到，使用 AI 分析
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
        
        # 将 AI 分析结果保存到数据库
        if supabase:
            try:
                analysis_result = response.parsed
                supabase.table('food_classifications').insert({
                    'name': analysis_result['name'],
                    'level': analysis_result['level'],
                    'reason': analysis_result['reason'],
                    'advice': analysis_result['advice'],
                    'type': item.type
                }).execute()
            except Exception as save_error:
                print(f"保存到数据库失败: {save_error}")
        
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
    # 首先尝试从数据库中随机获取一个食谱
    if supabase:
        try:
            result = supabase.table('recipes').select('*').execute()
            if result.data and len(result.data) > 0:
                # 从数据库中随机选择一个食谱
                import random
                recipe_data = random.choice(result.data)
                return {
                    "dishName": recipe_data['dish_name'],
                    "tags": recipe_data['tags'],
                    "ingredients": recipe_data['ingredients'],
                    "steps": recipe_data['steps'],
                    "nutritionBenefit": recipe_data['nutrition_benefit']
                }
        except Exception as db_error:
            print(f"数据库查询错误: {db_error}")
    
    # 如果数据库中没有找到，使用 AI 生成
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
        
        # 将 AI 生成的食谱保存到数据库
        if supabase:
            try:
                recipe_result = response.parsed
                supabase.table('recipes').insert({
                    'dish_name': recipe_result['dishName'],
                    'tags': recipe_result['tags'],
                    'ingredients': recipe_result['ingredients'],
                    'steps': recipe_result['steps'],
                    'nutrition_benefit': recipe_result['nutritionBenefit']
                }).execute()
            except Exception as save_error:
                print(f"保存到数据库失败: {save_error}")
        
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

# 增加一个简单的健康检查端点，用于验证后端服务是否正常运行
@app.get("/api/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "ok",
        "message": "Kidney Compass Backend is running",
        "timestamp": datetime.now().isoformat()
    }

# 增加一个端点，用于获取预设的食物分类数据，当数据库不可用时使用
@app.get("/api/fallback/foods")
async def get_fallback_foods():
    return {
        "foods": [
            # 蔬菜类
            {
                "name": "白萝卜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "白萝卜低磷低盐低钾，富含维生素C和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或煮汤。",
                "type": "food"
            },
            {
                "name": "胡萝卜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "胡萝卜低磷低盐低钾，富含胡萝卜素和维生素，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或煮汤。",
                "type": "food"
            },
            {
                "name": "黄瓜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "黄瓜低磷低盐低钾，含水量高，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议生吃或清炒。",
                "type": "food"
            },
            {
                "name": "茄子",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "茄子低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清蒸或清炒，避免油炸。",
                "type": "food"
            },
            {
                "name": "南瓜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "南瓜低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清蒸或煮汤。",
                "type": "food"
            },
            {
                "name": "花菜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "花菜低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或煮汤。",
                "type": "food"
            },
            {
                "name": "冬瓜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "冬瓜低磷低盐低钾，有利尿作用，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议煮汤或清炒。",
                "type": "food"
            },
            {
                "name": "丝瓜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "丝瓜低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或煮汤。",
                "type": "food"
            },
            {
                "name": "莴笋",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "莴笋低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或凉拌。",
                "type": "food"
            },
            {
                "name": "白菜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "白菜低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或煮汤。",
                "type": "food"
            },
            {
                "name": "西兰花",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "西兰花低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或煮汤。",
                "type": "food"
            },
            {
                "name": "芹菜",
                "category": "蔬菜",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "芹菜低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "可作为日常蔬菜食用，建议清炒或凉拌。",
                "type": "food"
            },
            # 水果类
            {
                "name": "苹果",
                "category": "水果",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "苹果富含纤维和抗氧化物质，钾含量适中，适合肾病患者食用。",
                "advice": "每天可食用1个中等大小的苹果，最好带皮食用以获取更多营养。",
                "type": "food"
            },
            {
                "name": "梨",
                "category": "水果",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "梨低磷低盐低钾，富含维生素和纤维，适合肾病患者食用。",
                "advice": "每天可食用1个中等大小的梨。",
                "type": "food"
            },
            {
                "name": "草莓",
                "category": "水果",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "草莓低磷低盐低钾，富含维生素C和抗氧化物质，适合肾病患者食用。",
                "advice": "每天可食用10-15颗草莓。",
                "type": "food"
            },
            {
                "name": "蓝莓",
                "category": "水果",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "蓝莓低磷低盐低钾，富含抗氧化物质和纤维，适合肾病患者食用。",
                "advice": "每天可食用10-15颗蓝莓。",
                "type": "food"
            },
            {
                "name": "香蕉",
                "category": "水果",
                "nutrition": ["低蛋白", "低磷", "低钠", "高钾"],
                "level": "yellow",
                "reason": "香蕉钾含量较高，肾功能不全患者需要注意控制摄入量。",
                "advice": "每周食用不超过2次，每次半根，避免在高血钾时食用。",
                "type": "food"
            },
            {
                "name": "西瓜",
                "category": "水果",
                "nutrition": ["低蛋白", "低磷", "低钠", "中钾"],
                "level": "yellow",
                "reason": "西瓜含水量高，可能会增加尿量，但同时也含有一定量的钾。",
                "advice": "适量食用，每天不超过200克，避免在水肿或少尿时食用。",
                "type": "food"
            },
            # 肉类
            {
                "name": "鸡蛋",
                "category": "蛋类",
                "nutrition": ["高蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "鸡蛋是优质蛋白质的良好来源，低钾低磷，适合肾病患者食用。",
                "advice": "每天可食用1-2个鸡蛋，最好选择煮鸡蛋或蒸鸡蛋。",
                "type": "food"
            },
            {
                "name": "瘦肉",
                "category": "肉类",
                "nutrition": ["高蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "瘦肉是优质蛋白质的良好来源，低钾低磷，适合肾病患者食用。",
                "advice": "每天可食用50-100克瘦肉，选择猪瘦肉、鸡肉或鱼肉。",
                "type": "food"
            },
            {
                "name": "鱼肉",
                "category": "肉类",
                "nutrition": ["高蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "鱼肉是优质蛋白质的良好来源，低钾低磷，富含不饱和脂肪酸，适合肾病患者食用。",
                "advice": "每周可食用2-3次，每次100-150克，选择淡水鱼或海水鱼。",
                "type": "food"
            },
            {
                "name": "鸡肉",
                "category": "肉类",
                "nutrition": ["高蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "鸡肉是优质蛋白质的良好来源，低钾低磷，适合肾病患者食用。",
                "advice": "每周可食用2-3次，每次100-150克，选择鸡胸肉。",
                "type": "food"
            },
            # 主食类
            {
                "name": "米饭",
                "category": "主食",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "米饭是碳水化合物的主要来源，低钾低磷低钠，适合肾病患者作为主食。",
                "advice": "可作为日常主食，建议与优质蛋白和蔬菜搭配食用。",
                "type": "food"
            },
            {
                "name": "面条",
                "category": "主食",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "面条是碳水化合物的主要来源，低钾低磷低钠，适合肾病患者作为主食。",
                "advice": "可作为日常主食，建议选择全麦面条以获取更多纤维。",
                "type": "food"
            },
            {
                "name": "馒头",
                "category": "主食",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "馒头是碳水化合物的主要来源，低磷低盐低钾，适合肾病患者作为主食。",
                "advice": "可作为日常主食，建议与优质蛋白和蔬菜搭配食用。",
                "type": "food"
            },
            {
                "name": "燕麦",
                "category": "主食",
                "nutrition": ["低蛋白", "低磷", "低钠", "低钾"],
                "level": "green",
                "reason": "燕麦是碳水化合物的良好来源，低磷低盐低钾，富含纤维，适合肾病患者作为主食。",
                "advice": "可作为日常主食，建议与牛奶或豆浆搭配食用。",
                "type": "food"
            },
            # 坚果类
            {
                "name": "杏仁",
                "category": "坚果",
                "nutrition": ["高蛋白", "高磷", "低钠", "低钾"],
                "level": "yellow",
                "reason": "杏仁含有一定量的磷和蛋白质，肾功能不全患者需要注意控制摄入量。",
                "advice": "每周食用不超过2次，每次不超过10颗。",
                "type": "food"
            },
            {
                "name": "核桃",
                "category": "坚果",
                "nutrition": ["高蛋白", "高磷", "低钠", "低钾"],
                "level": "yellow",
                "reason": "核桃含有一定量的磷和蛋白质，肾功能不全患者需要注意控制摄入量。",
                "advice": "每周食用不超过2次，每次不超过2颗。",
                "type": "food"
            },
            # 其他
            {
                "name": "牛奶",
                "category": "乳制品",
                "nutrition": ["高蛋白", "高磷", "低钠", "低钾"],
                "level": "yellow",
                "reason": "牛奶含有一定量的磷和钾，肾功能不全患者需要注意控制摄入量。",
                "advice": "每周食用不超过3次，每次不超过200毫升，可选择低磷牛奶。",
                "type": "food"
            },
            {
                "name": "豆腐",
                "category": "豆制品",
                "nutrition": ["高蛋白", "高磷", "低钠", "低钾"],
                "level": "yellow",
                "reason": "豆腐含有一定量的磷和植物蛋白，肾功能不全患者需要注意控制摄入量。",
                "advice": "每周食用不超过2次，每次不超过100克，避免与高磷食物同时食用。",
                "type": "food"
            }
        ]
    }

# 增加一个端点，用于获取预设的食谱数据，当数据库不可用时使用
@app.get("/api/fallback/recipes")
async def get_fallback_recipes():
    return {
        "recipes": [
            # 鱼类食谱
            {
                "dishName": "清蒸鲈鱼",
                "tags": ["优质蛋白", "低油", "低盐", "低磷", "低钾"],
                "ingredients": ["鲈鱼 1条", "姜丝 适量", "葱段 适量", "低钠酱油 少许"],
                "steps": ["鲈鱼洗净划刀", "放姜葱蒸8分钟", "倒掉汤汁淋少许热油和酱油"],
                "nutritionBenefit": "鲈鱼富含优质蛋白质，低脂肪，低磷低钾，适合 IgA CKD 3期和病理4级患者食用。清蒸的烹饪方式保留了鱼肉的营养，同时减少了油脂的摄入。"
            },
            {
                "dishName": "香煎鳕鱼",
                "tags": ["优质蛋白", "低油", "低盐", "低磷", "低钾"],
                "ingredients": ["鳕鱼 150克", "柠檬汁 适量", "黑胡椒 少许", "低钠盐 少许", "植物油 少许"],
                "steps": ["鳕鱼洗净切块", "用柠檬汁、黑胡椒和低钠盐腌制10分钟", "锅中放油，小火煎至两面金黄即可"],
                "nutritionBenefit": "鳕鱼富含优质蛋白质，低脂肪，低磷低钾，适合 IgA CKD 3期和病理4级患者食用。香煎的烹饪方式使鱼肉更加美味。"
            },
            # 鸡肉食谱
            {
                "dishName": "清蒸鸡胸肉",
                "tags": ["优质蛋白", "低油", "低盐", "低磷", "低钾"],
                "ingredients": ["鸡胸肉 150克", "姜丝 适量", "葱段 适量", "低钠酱油 少许"],
                "steps": ["鸡胸肉洗净切片", "放姜葱蒸10分钟", "倒掉汤汁淋少许低钠酱油即可"],
                "nutritionBenefit": "鸡胸肉富含优质蛋白质，低脂肪，低磷低钾，适合 IgA CKD 3期和病理4级患者食用。清蒸的烹饪方式保留了鸡肉的营养，同时减少了油脂的摄入。"
            },
            {
                "dishName": "鸡蛋白菜汤",
                "tags": ["优质蛋白", "低磷", "低钾", "低钠", "低蛋白"],
                "ingredients": ["鸡蛋 2个", "白菜 200克", "葱花 适量", "低钠盐 少许"],
                "steps": ["鸡蛋打散", "白菜切丝", "水烧开后加入白菜", "煮沸后淋入蛋液", "加低钠盐调味即可"],
                "nutritionBenefit": "鸡蛋提供优质蛋白质，白菜富含维生素和纤维，低钾低磷低钠，适合 IgA CKD 3期和病理4级患者日常食用。"
            },
            # 猪肉食谱
            {
                "dishName": "冬瓜排骨汤",
                "tags": ["低磷", "低钾", "低钠", "低蛋白"],
                "ingredients": ["排骨 100克", "冬瓜 200克", "姜 2片", "低钠盐 少许"],
                "steps": ["排骨焯水去血沫", "冬瓜切块", "所有材料放入锅中加水煮30分钟", "加低钠盐调味即可"],
                "nutritionBenefit": "冬瓜有利尿作用，排骨提供少量优质蛋白质，此汤低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "清炒瘦肉片",
                "tags": ["优质蛋白", "低油", "低盐", "低磷", "低钾"],
                "ingredients": ["瘦肉 100克", "黄瓜 100克", "胡萝卜 50克", "蒜末 适量", "低钠盐 少许", "植物油 少许"],
                "steps": ["瘦肉切片", "黄瓜、胡萝卜切片", "锅中放油，爆香蒜末", "加入瘦肉片翻炒至变色", "加入黄瓜、胡萝卜翻炒", "加低钠盐调味即可"],
                "nutritionBenefit": "瘦肉提供优质蛋白质，黄瓜、胡萝卜低磷低钾，此菜低油低盐，适合 IgA CKD 3期和病理4级患者食用。"
            },
            # 蔬菜食谱
            {
                "dishName": "清炒西兰花",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["西兰花 200克", "蒜末 适量", "低钠盐 少许", "植物油 少许"],
                "steps": ["西兰花切小朵焯水", "锅中放油爆香蒜末", "加入西兰花翻炒", "加低钠盐调味即可"],
                "nutritionBenefit": "西兰花富含维生素和纤维，低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "清炒白萝卜",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["白萝卜 200克", "蒜末 适量", "低钠盐 少许", "植物油 少许"],
                "steps": ["白萝卜切丝", "锅中放油爆香蒜末", "加入白萝卜丝翻炒", "加低钠盐调味即可"],
                "nutritionBenefit": "白萝卜低磷低钾低钠，富含维生素和纤维，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "清炒黄瓜",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["黄瓜 200克", "蒜末 适量", "低钠盐 少许", "植物油 少许"],
                "steps": ["黄瓜切片", "锅中放油爆香蒜末", "加入黄瓜片翻炒", "加低钠盐调味即可"],
                "nutritionBenefit": "黄瓜低磷低钾低钠，富含维生素和纤维，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "清炒茄子",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["茄子 200克", "蒜末 适量", "低钠盐 少许", "植物油 少许"],
                "steps": ["茄子切块", "锅中放油爆香蒜末", "加入茄子块翻炒", "加低钠盐调味即可"],
                "nutritionBenefit": "茄子低磷低钾低钠，富含维生素和纤维，适合 IgA CKD 3期和病理4级患者食用。"
            },
            # 汤类食谱
            {
                "dishName": "番茄鸡蛋汤",
                "tags": ["优质蛋白", "低磷", "低钾", "低钠", "低蛋白"],
                "ingredients": ["番茄 1个", "鸡蛋 1个", "葱花 适量", "低钠盐 少许"],
                "steps": ["番茄切块炒软", "加水烧开", "淋入蛋液", "加低钠盐调味即可"],
                "nutritionBenefit": "番茄富含维生素C，鸡蛋提供优质蛋白质，此汤低磷低钾低钠，适合 IgA CKD 3期和病理4级患者日常食用。"
            },
            {
                "dishName": "南瓜汤",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["南瓜 200克", "姜 2片", "低钠盐 少许"],
                "steps": ["南瓜切块", "所有材料放入锅中加水煮20分钟", "用搅拌机打成泥", "加低钠盐调味即可"],
                "nutritionBenefit": "南瓜低磷低钾低钠，富含维生素和纤维，适合 IgA CKD 3期和病理4级患者食用。"
            },
            # 主食类食谱
            {
                "dishName": "番茄鸡蛋面",
                "tags": ["低磷", "低钾", "低钠", "低蛋白"],
                "ingredients": ["面条 50克", "番茄 1个", "鸡蛋 1个", "葱花 适量", "低钠盐 少许"],
                "steps": ["番茄切块炒软", "加水烧开", "下面条煮至八分熟", "淋入蛋液", "加低钠盐调味即可"],
                "nutritionBenefit": "番茄富含维生素C，鸡蛋提供优质蛋白质，面条提供能量，此餐低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "蔬菜粥",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["大米 50克", "白菜 50克", "胡萝卜 50克", "低钠盐 少许"],
                "steps": ["大米洗净煮粥", "白菜、胡萝卜切丝", "粥煮至八分熟时加入蔬菜丝", "煮至蔬菜熟软", "加低钠盐调味即可"],
                "nutritionBenefit": "大米提供能量，白菜、胡萝卜低磷低钾，此粥低钠低蛋白，适合 IgA CKD 3期和病理4级患者食用。"
            },
            # 其他食谱
            {
                "dishName": "凉拌黄瓜",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["黄瓜 200克", "蒜末 适量", "醋 少许", "低钠盐 少许", "香油 少许"],
                "steps": ["黄瓜切丝", "加入蒜末、醋、低钠盐、香油拌匀即可"],
                "nutritionBenefit": "黄瓜低磷低钾低钠，富含维生素和纤维，适合 IgA CKD 3期和病理4级患者食用。"
            },
            {
                "dishName": "清蒸南瓜",
                "tags": ["低磷", "低钾", "低钠", "低蛋白", "高纤维"],
                "ingredients": ["南瓜 200克", "红枣 3颗", "低钠盐 少许"],
                "steps": ["南瓜切块", "红枣洗净去核", "南瓜块上放红枣", "蒸15分钟", "加低钠盐调味即可"],
                "nutritionBenefit": "南瓜低磷低钾低钠，富含维生素和纤维，适合 IgA CKD 3期和病理4级患者食用。"
            }
        ]
    }

# 增加一个端点，用于获取食物白名单
@app.get("/api/food-whitelist")
async def get_food_whitelist():
    try:
        # 尝试从数据库获取食物白名单
        if supabase:
            result = supabase.table('food_whitelist').select('*').execute()
            if result.data:
                return {"whitelist": result.data}
        # 如果数据库中没有数据或Supabase未初始化，返回预设的食物白名单
        return {
            "whitelist": [
                {"category": "肉类", "name": "鸡胸肉", "note": "优质蛋白，必须去皮切片焯水"},
                {"category": "肉类", "name": "瘦猪肉", "note": "含铁丰富，必须切片焯水"},
                {"category": "肉类", "name": "鸭肉", "note": "利水消肿，必须去皮焯水"},
                {"category": "水产", "name": "黑鱼", "note": "促进伤口愈合，只吃肉不喝汤"},
                {"category": "水产", "name": "鲈鱼/草鱼", "note": "易消化，清蒸最佳"},
                {"category": "蛋奶", "name": "鸡蛋清", "note": "目前最推荐的蛋白来源，无限量"},
                {"category": "蛋奶", "name": "低脂牛奶", "note": "每日限200ml，补钙"},
                {"category": "增重主食", "name": "红薯粉条/粉丝", "note": "极低磷、无蛋白、高热量，长肉神器"},
                {"category": "增重主食", "name": "麦淀粉(澄粉)", "note": "可做水晶饺，补充热量"},
                {"category": "蔬菜", "name": "冬瓜/丝瓜", "note": "低钾低磷，利尿"},
                {"category": "蔬菜", "name": "大白菜/包菜", "note": "安全蔬菜，需炒熟"},
                {"category": "蔬菜", "name": "西葫芦/黄瓜", "note": "低嘌呤，推荐"},
                {"category": "水果", "name": "苹果/梨", "note": "低钾安全果，每日一个"},
                {"category": "油脂", "name": "菜籽油/橄榄油", "note": "每日35-40g，护肝且补充能量"}
            ]
        }
    except Exception as e:
        print(f"获取食物白名单失败: {e}")
        # 如果数据库连接失败，返回预设的食物白名单
        return {
            "whitelist": [
                {"category": "肉类", "name": "鸡胸肉", "note": "优质蛋白，必须去皮切片焯水"},
                {"category": "肉类", "name": "瘦猪肉", "note": "含铁丰富，必须切片焯水"},
                {"category": "肉类", "name": "鸭肉", "note": "利水消肿，必须去皮焯水"},
                {"category": "水产", "name": "黑鱼", "note": "促进伤口愈合，只吃肉不喝汤"},
                {"category": "水产", "name": "鲈鱼/草鱼", "note": "易消化，清蒸最佳"},
                {"category": "蛋奶", "name": "鸡蛋清", "note": "目前最推荐的蛋白来源，无限量"},
                {"category": "蛋奶", "name": "低脂牛奶", "note": "每日限200ml，补钙"},
                {"category": "增重主食", "name": "红薯粉条/粉丝", "note": "极低磷、无蛋白、高热量，长肉神器"},
                {"category": "增重主食", "name": "麦淀粉(澄粉)", "note": "可做水晶饺，补充热量"},
                {"category": "蔬菜", "name": "冬瓜/丝瓜", "note": "低钾低磷，利尿"},
                {"category": "蔬菜", "name": "大白菜/包菜", "note": "安全蔬菜，需炒熟"},
                {"category": "蔬菜", "name": "西葫芦/黄瓜", "note": "低嘌呤，推荐"},
                {"category": "水果", "name": "苹果/梨", "note": "低钾安全果，每日一个"},
                {"category": "油脂", "name": "菜籽油/橄榄油", "note": "每日35-40g，护肝且补充能量"}
            ]
        }

@app.get("/api/food-blacklist")
async def get_food_blacklist():
    try:
        # 尝试从数据库获取食物黑名单
        if supabase:
            result = supabase.table('food_blacklist').select('*').execute()
            if result.data:
                return {"blacklist": result.data}
        # 如果数据库中没有数据或Supabase未初始化，返回预设的食物黑名单
        return {
            "blacklist": [
                {"name": "火锅", "reason": "高盐高嘌呤，加重肾脏负担", "level": "red"},
                {"name": "豆腐", "reason": "高磷高蛋白，不适合肾病患者", "level": "red"},
                {"name": "动物内脏", "reason": "高嘌呤高胆固醇，增加痛风风险", "level": "red"},
                {"name": "海鲜", "reason": "高嘌呤，可能引发痛风", "level": "red"},
                {"name": "浓汤", "reason": "高磷高嘌呤，加重肾脏负担", "level": "red"},
                {"name": "腌制食品", "reason": "高盐，加重肾脏负担", "level": "red"},
                {"name": "碳酸饮料", "reason": "高磷，影响钙磷代谢", "level": "yellow"},
                {"name": "坚果", "reason": "高磷高钾，需限量食用", "level": "yellow"},
                {"name": "香蕉", "reason": "高钾，肾病患者需限制", "level": "yellow"},
                {"name": "橙子", "reason": "高钾，肾病患者需限制", "level": "yellow"},
                {"name": "菠菜", "reason": "高钾高草酸，影响钙吸收", "level": "yellow"},
                {"name": "蘑菇", "reason": "高嘌呤，可能引发痛风", "level": "yellow"}
            ]
        }
    except Exception as e:
        print(f"获取食物黑名单失败: {e}")
        # 如果数据库连接失败，返回预设的食物黑名单
        return {
            "blacklist": [
                {"name": "火锅", "reason": "高盐高嘌呤，加重肾脏负担", "level": "red"},
                {"name": "豆腐", "reason": "高磷高蛋白，不适合肾病患者", "level": "red"},
                {"name": "动物内脏", "reason": "高嘌呤高胆固醇，增加痛风风险", "level": "red"},
                {"name": "海鲜", "reason": "高嘌呤，可能引发痛风", "level": "red"},
                {"name": "浓汤", "reason": "高磷高嘌呤，加重肾脏负担", "level": "red"},
                {"name": "腌制食品", "reason": "高盐，加重肾脏负担", "level": "red"},
                {"name": "碳酸饮料", "reason": "高磷，影响钙磷代谢", "level": "yellow"},
                {"name": "坚果", "reason": "高磷高钾，需限量食用", "level": "yellow"},
                {"name": "香蕉", "reason": "高钾，肾病患者需限制", "level": "yellow"},
                {"name": "橙子", "reason": "高钾，肾病患者需限制", "level": "yellow"},
                {"name": "菠菜", "reason": "高钾高草酸，影响钙吸收", "level": "yellow"},
                {"name": "蘑菇", "reason": "高嘌呤，可能引发痛风", "level": "yellow"}
            ]
        }
