from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import google.generativeai as genai

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
if gemini_key:
    genai.configure(api_key=gemini_key)
ai_client = genai if gemini_key else None

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
            response = supabase.table("food_classifications").select("*").eq("food_name", item.query).execute()
            if response.data and len(response.data) > 0:
                # 从数据库返回结果
                db_result = response.data[0]
                return {
                    "name": db_result.get("food_name"),
                    "level": db_result.get("level"),
                    "reason": db_result.get("reason"),
                    "advice": db_result.get("advice")
                }
        except Exception as e:
            print(f"数据库查询错误: {e}")
    
    # 如果数据库查询失败或没有结果，使用预设数据
    # 检查是否在预设食物列表中
    for food_item in FOOD_ITEMS:
        if food_item["name"] == item.query:
            return food_item
    
    # 如果不在预设列表中，使用 Gemini API 分类
    if ai_client:
        try:
            # 构建 Gemini API 请求
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # 系统提示
            system_prompt = ("你是一位专注于肾脏健康的医疗专家，精通慢性肾病（CKD）患者的饮食管理。"  
                           "请对用户提供的食物进行分类，并基于其对肾脏健康的影响给出明确的指导。"  
                           "分类标准："  
                           "- 绿色（green）：对所有 CKD 患者（包括透析患者）安全，推荐食用。"  
                           "- 黄色（yellow）：需在医生或营养师指导下，根据个人肾功能和当前阶段控制食用量。"  
                           "- 红色（red）：对大多数 CKD 患者（尤其是中晚期患者）不推荐食用，应避免。"  
                           "分析维度："  
                           "1. 蛋白质含量（过高会增加肾脏负担）"  
                           "2. 钠含量（过高会导致血压升高，加重水肿）"  
                           "3. 钾含量（肾功能不全时易引发高血钾）"  
                           "4. 磷含量（肾功能不全时易引发高血磷）"  
                           "5. 其他可能对肾脏产生影响的成分。"  
                           "回答要求："  
                           "- 明确给出分类结果（仅 green、yellow 或 red）。"  
                           "- 详细说明分类理由，特别是基于上述五个维度的分析。"  
                           "- 提供针对 CKD 患者的具体饮食建议，包括食用量、烹饪方法等。"  
                           "- 使用专业、客观的医学术语，同时确保表达清晰易懂。"  
                           "- 如遇不确定情况，请基于现有医学知识给出最合理的判断，并建议用户咨询其主治医生。"  
                           "- 输出格式："  
                           "  name: [食物名称]\n"  
                           "  level: [green/yellow/red]\n"  
                           "  reason: [分类理由]\n"  
                           "  advice: [饮食建议]")
            
            # 用户提示
            user_prompt = f"请对以下食物进行分类：{item.query}"
            
            # 生成响应
            response = model.generate_content(
                [system_prompt, user_prompt]
            )
            
            # 解析响应
            response_text = response.text
            lines = response_text.strip().split('\n')
            
            result = {
                "name": item.query,
                "level": "yellow",  # 默认值
                "reason": "AI 分析未返回有效结果",
                "advice": "建议咨询医生或营养师"
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('level:'):
                    level = line.split(':', 1)[1].strip().lower()
                    if level in ['green', 'yellow', 'red']:
                        result['level'] = level
                elif line.startswith('reason:'):
                    result['reason'] = line.split(':', 1)[1].strip()
                elif line.startswith('advice:'):
                    result['advice'] = line.split(':', 1)[1].strip()
            
            # 保存到数据库
            if supabase:
                try:
                    supabase.table("food_classifications").insert({
                        "food_name": item.query,
                        "level": result["level"],
                        "reason": result["reason"],
                        "advice": result["advice"]
                    }).execute()
                except Exception as e:
                    print(f"数据库保存错误: {e}")
            
            return result
            
        except Exception as e:
            print(f"AI 分析错误: {e}")
            # 返回默认结果
            return {
                "name": item.query,
                "level": "yellow",
                "reason": f"AI 分析失败: {str(e)}",
                "advice": "建议咨询医生或营养师"
            }
    else:
        # 没有 AI 客户端，返回默认结果
        return {
            "name": item.query,
            "level": "yellow",
            "reason": "AI 服务不可用",
            "advice": "建议咨询医生或营养师"
        }

@app.post("/api/recipe")
async def generate_recipe():
    # 首先尝试从数据库中获取
    if supabase:
        try:
            response = supabase.table("recipes").select("*").limit(1).execute()
            if response.data and len(response.data) > 0:
                # 从数据库返回结果
                db_result = response.data[0]
                return {
                    "dishName": db_result.get("dish_name"),
                    "tags": db_result.get("tags", "").split(","),
                    "ingredients": db_result.get("ingredients", "").split(","),
                    "steps": db_result.get("steps", "").split(","),
                    "nutritionBenefit": db_result.get("nutrition_benefit")
                }
        except Exception as e:
            print(f"数据库查询错误: {e}")
    
    # 如果数据库查询失败或没有结果，使用预设数据
    import random
    recipe = random.choice(RECIPES)
    
    # 如果有 AI 客户端，尝试生成新食谱
    if ai_client:
        try:
            # 构建 Gemini API 请求
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # 系统提示
            system_prompt = ("你是一位专业的肾脏健康营养师，擅长为慢性肾病（CKD）患者设计食谱。"  
                           "请基于以下原则创建一个适合 CKD 患者的健康食谱："  
                           "1. 低蛋白质（对于未透析患者）或适量优质蛋白（对于透析患者）"  
                           "2. 低钠、低钾、低磷"  
                           "3. 富含必需氨基酸和维生素"  
                           "4. 易于准备，食材常见"  
                           "5. 美味可口，适合长期食用"  
                           "请提供："  
                           "- 菜名"  
                           "- 适合人群标签（如：低蛋白、低磷、低钠、低钾等）"  
                           "- 详细的食材清单及用量"  
                           "- 详细的烹饪步骤"  
                           "- 营养价值和对肾脏健康的益处"  
                           "输出格式："  
                           "  dishName: [菜名]\n"  
                           "  tags: [标签1], [标签2], ...\n"  
                           "  ingredients: [食材1], [食材2], ...\n"  
                           "  steps: [步骤1], [步骤2], ...\n"  
                           "  nutritionBenefit: [营养价值和益处]")
            
            # 用户提示
            user_prompt = "请生成一个适合 CKD 患者的健康食谱"
            
            # 生成响应
            response = model.generate_content(
                [system_prompt, user_prompt]
            )
            
            # 解析响应
            response_text = response.text
            lines = response_text.strip().split('\n')
            
            result = {
                "dishName": "未知菜品",
                "tags": [],
                "ingredients": [],
                "steps": [],
                "nutritionBenefit": ""
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('dishName:'):
                    result['dishName'] = line.split(':', 1)[1].strip()
                elif line.startswith('tags:'):
                    tags_str = line.split(':', 1)[1].strip()
                    result['tags'] = [tag.strip() for tag in tags_str.split(',')]
                elif line.startswith('ingredients:'):
                    ingredients_str = line.split(':', 1)[1].strip()
                    result['ingredients'] = [ingredient.strip() for ingredient in ingredients_str.split(',')]
                elif line.startswith('steps:'):
                    steps_str = line.split(':', 1)[1].strip()
                    result['steps'] = [step.strip() for step in steps_str.split(',')]
                elif line.startswith('nutritionBenefit:'):
                    result['nutritionBenefit'] = line.split(':', 1)[1].strip()
            
            # 保存到数据库
            if supabase:
                try:
                    supabase.table("recipes").insert({
                        "dish_name": result["dishName"],
                        "tags": ",".join(result["tags"]),
                        "ingredients": ",".join(result["ingredients"]),
                        "steps": ",".join(result["steps"]),
                        "nutrition_benefit": result["nutritionBenefit"]
                    }).execute()
                except Exception as e:
                    print(f"数据库保存错误: {e}")
            
            return result
            
        except Exception as e:
            print(f"AI 食谱生成错误: {e}")
            # 返回预设食谱
            return recipe
    else:
        # 没有 AI 客户端，返回预设食谱
        return recipe

# 用户认证相关路由
@app.post("/auth/signup")
async def signup(user: UserLogin):
    if not supabase:
        return JSONResponse(
            status_code=503,
            content={"detail": "数据库服务暂时不可用"}
        )
    
    try:
        # 使用 Supabase Auth 进行注册
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password
            }
        )
        
        if response.user:
            return {"message": "注册成功", "user": response.user}
        else:
            return JSONResponse(
                status_code=400,
                content={"detail": "注册失败，请检查邮箱和密码"}
            )
    except Exception as e:
        print(f"注册错误: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"注册失败: {str(e)}"}
        )

@app.post("/auth/login")
async def login(user: UserLogin):
    if not supabase:
        return JSONResponse(
            status_code=503,
            content={"detail": "数据库服务暂时不可用"}
        )
    
    try:
        # 使用 Supabase Auth 进行登录
        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password
            }
        )
        
        if response.user and response.session:
            return {
                "message": "登录成功",
                "user": response.user,
                "token": response.session.access_token
            }
        else:
            return JSONResponse(
                status_code=401,
                content={"detail": "登录失败，请检查邮箱和密码"}
            )
    except Exception as e:
        print(f"登录错误: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"登录失败: {str(e)}"}
        )

@app.get("/api/health")
async def health_check():
    status = "ok" if (supabase or ai_client) else "partial"
    return {
        "status": status,
        "message": "Kidney Compass Backend is running!",
        "services": {
            "database": "connected" if supabase else "disconnected",
            "ai": "available" if ai_client else "unavailable"
        }
    }

# 预设食物分类数据
FOOD_ITEMS = [
    {"name": "苹果", "level": "green", "reason": "苹果是低蛋白、低钾、低磷的水果，富含维生素C和纤维素，适合所有CKD患者食用。", "advice": "每天可食用1-2个中等大小的苹果。"},
    {"name": "香蕉", "level": "yellow", "reason": "香蕉含有较高的钾，对于肾功能不全的患者可能需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "菠菜", "level": "yellow", "reason": "菠菜含有较高的钾和草酸，肾功能不全的患者需要限制食用。", "advice": "可通过焯水减少草酸含量，肾功能不全的患者应控制食用量。"},
    {"name": "土豆", "level": "yellow", "reason": "土豆含有较高的钾，肾功能不全的患者需要限制食用。", "advice": "可通过浸泡或焯水减少钾含量，肾功能不全的患者应控制食用量。"},
    {"name": "鸡蛋", "level": "yellow", "reason": "鸡蛋是优质蛋白的来源，但含有一定量的磷，需要根据肾功能情况控制食用量。", "advice": "每天可食用1-2个鸡蛋，肾功能不全的患者应在医生指导下调整食用量。"},
    {"name": "牛奶", "level": "yellow", "reason": "牛奶含有较高的磷和蛋白质，肾功能不全的患者需要限制食用。", "advice": "可选择低磷牛奶或在医生指导下控制食用量。"},
    {"name": "瘦肉", "level": "yellow", "reason": "瘦肉是优质蛋白的来源，但含有一定量的磷，需要根据肾功能情况控制食用量。", "advice": "每天可食用50-100克瘦肉，肾功能不全的患者应在医生指导下调整食用量。"},
    {"name": "豆腐", "level": "yellow", "reason": "豆腐是植物蛋白的来源，含有一定量的磷，需要根据肾功能情况控制食用量。", "advice": "每天可食用50-100克豆腐，肾功能不全的患者应在医生指导下调整食用量。"},
    {"name": "米饭", "level": "green", "reason": "米饭是低蛋白、低钾、低磷的主食，适合所有CKD患者食用。", "advice": "每天可食用150-200克米饭。"},
    {"name": "面条", "level": "green", "reason": "面条是低蛋白、低钾、低磷的主食，适合所有CKD患者食用。", "advice": "每天可食用150-200克面条。"},
    {"name": "馒头", "level": "green", "reason": "馒头是低蛋白、低钾、低磷的主食，适合所有CKD患者食用。", "advice": "每天可食用100-150克馒头。"},
    {"name": "面包", "level": "yellow", "reason": "面包含有一定量的钠，需要注意选择低钠面包。", "advice": "选择低钠面包，每天可食用50-100克。"},
    {"name": "橙子", "level": "yellow", "reason": "橙子含有较高的钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "橘子", "level": "yellow", "reason": "橘子含有较高的钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "葡萄", "level": "green", "reason": "葡萄是低蛋白、低钾、低磷的水果，适合所有CKD患者食用。", "advice": "每天可食用10-15颗葡萄。"},
    {"name": "草莓", "level": "green", "reason": "草莓是低蛋白、低钾、低磷的水果，富含维生素C，适合所有CKD患者食用。", "advice": "每天可食用10-15颗草莓。"},
    {"name": "蓝莓", "level": "green", "reason": "蓝莓是低蛋白、低钾、低磷的水果，富含抗氧化物质，适合所有CKD患者食用。", "advice": "每天可食用一小碗蓝莓。"},
    {"name": "梨", "level": "green", "reason": "梨是低蛋白、低钾、低磷的水果，适合所有CKD患者食用。", "advice": "每天可食用1个中等大小的梨。"},
    {"name": "桃", "level": "green", "reason": "桃是低蛋白、低钾、低磷的水果，适合所有CKD患者食用。", "advice": "每天可食用1个中等大小的桃。"},
    {"name": "杏", "level": "green", "reason": "杏是低蛋白、低钾、低磷的水果，适合所有CKD患者食用。", "advice": "每天可食用3-5个杏。"},
    {"name": "西瓜", "level": "green", "reason": "西瓜是低蛋白、低钾、低磷的水果，富含水分，适合所有CKD患者食用。", "advice": "每天可食用200-300克西瓜。"},
    {"name": "黄瓜", "level": "green", "reason": "黄瓜是低蛋白、低钾、低磷的蔬菜，富含水分和纤维素，适合所有CKD患者食用。", "advice": "每天可食用100-200克黄瓜。"},
    {"name": "西红柿", "level": "green", "reason": "西红柿是低蛋白、低钾、低磷的蔬菜，富含维生素C和番茄红素，适合所有CKD患者食用。", "advice": "每天可食用100-200克西红柿。"},
    {"name": "胡萝卜", "level": "green", "reason": "胡萝卜是低蛋白、低钾、低磷的蔬菜，富含胡萝卜素，适合所有CKD患者食用。", "advice": "每天可食用100-150克胡萝卜。"},
    {"name": "白萝卜", "level": "green", "reason": "白萝卜是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用100-150克白萝卜。"},
    {"name": "洋葱", "level": "green", "reason": "洋葱是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用50-100克洋葱。"},
    {"name": "大蒜", "level": "green", "reason": "大蒜是低蛋白、低钾、低磷的调味品，具有抗菌和抗氧化作用，适合所有CKD患者食用。", "advice": "每天可食用2-3瓣大蒜。"},
    {"name": "姜", "level": "green", "reason": "姜是低蛋白、低钾、低磷的调味品，具有温中散寒的作用，适合所有CKD患者食用。", "advice": "每天可食用5-10克姜。"},
    {"name": "葱", "level": "green", "reason": "葱是低蛋白、低钾、低磷的调味品，适合所有CKD患者食用。", "advice": "每天可食用50-100克葱。"},
    {"name": "青椒", "level": "green", "reason": "青椒是低蛋白、低钾、低磷的蔬菜，富含维生素C，适合所有CKD患者食用。", "advice": "每天可食用100-150克青椒。"},
    {"name": "茄子", "level": "green", "reason": "茄子是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用100-150克茄子。"},
    {"name": "南瓜", "level": "green", "reason": "南瓜是低蛋白、低钾、低磷的蔬菜，富含胡萝卜素，适合所有CKD患者食用。", "advice": "每天可食用100-150克南瓜。"},
    {"name": "冬瓜", "level": "green", "reason": "冬瓜是低蛋白、低钾、低磷的蔬菜，富含水分，具有利尿作用，适合所有CKD患者食用。", "advice": "每天可食用100-200克冬瓜。"},
    {"name": "丝瓜", "level": "green", "reason": "丝瓜是低蛋白、低钾、低磷的蔬菜，富含水分，适合所有CKD患者食用。", "advice": "每天可食用100-150克丝瓜。"},
    {"name": "苦瓜", "level": "green", "reason": "苦瓜是低蛋白、低钾、低磷的蔬菜，具有清热解毒的作用，适合所有CKD患者食用。", "advice": "每天可食用100-150克苦瓜。"},
    {"name": "西兰花", "level": "yellow", "reason": "西兰花含有较高的钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "菜花", "level": "green", "reason": "菜花是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用100-150克菜花。"},
    {"name": "白菜", "level": "green", "reason": "白菜是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用100-200克白菜。"},
    {"name": "生菜", "level": "green", "reason": "生菜是低蛋白、低钾、低磷的蔬菜，富含水分和纤维素，适合所有CKD患者食用。", "advice": "每天可食用100-200克生菜。"},
    {"name": "油麦菜", "level": "green", "reason": "油麦菜是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用100-200克油麦菜。"},
    {"name": "空心菜", "level": "yellow", "reason": "空心菜含有较高的钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "苋菜", "level": "yellow", "reason": "苋菜含有较高的钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "莴笋", "level": "green", "reason": "莴笋是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用100-150克莴笋。"},
    {"name": "竹笋", "level": "green", "reason": "竹笋是低蛋白、低钾、低磷的蔬菜，适合所有CKD患者食用。", "advice": "每天可食用50-100克竹笋。"},
    {"name": "香菇", "level": "yellow", "reason": "香菇含有较高的磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "金针菇", "level": "green", "reason": "金针菇是低蛋白、低钾、低磷的菌类，适合所有CKD患者食用。", "advice": "每天可食用50-100克金针菇。"},
    {"name": "平菇", "level": "green", "reason": "平菇是低蛋白、低钾、低磷的菌类，适合所有CKD患者食用。", "advice": "每天可食用50-100克平菇。"},
    {"name": "鸡肉", "level": "yellow", "reason": "鸡肉是优质蛋白的来源，但含有一定量的磷，需要根据肾功能情况控制食用量。", "advice": "每天可食用50-100克鸡肉，肾功能不全的患者应在医生指导下调整食用量。"},
    {"name": "鸭肉", "level": "yellow", "reason": "鸭肉是优质蛋白的来源，但含有一定量的磷，需要根据肾功能情况控制食用量。", "advice": "每天可食用50-100克鸭肉，肾功能不全的患者应在医生指导下调整食用量。"},
    {"name": "鱼肉", "level": "yellow", "reason": "鱼肉是优质蛋白的来源，但含有一定量的磷，需要根据肾功能情况控制食用量。", "advice": "每天可食用50-100克鱼肉，肾功能不全的患者应在医生指导下调整食用量。"},
    {"name": "虾", "level": "yellow", "reason": "虾是优质蛋白的来源，但含有较高的磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "蟹", "level": "red", "reason": "蟹含有较高的磷和嘌呤，不适合CKD患者食用。", "advice": "建议避免食用蟹类。"},
    {"name": "牛肉", "level": "yellow", "reason": "牛肉是优质蛋白的来源，但含有较高的磷和嘌呤，需要根据肾功能情况控制食用量。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "羊肉", "level": "yellow", "reason": "羊肉是优质蛋白的来源，但含有较高的磷和嘌呤，需要根据肾功能情况控制食用量。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "猪肉", "level": "yellow", "reason": "猪肉是优质蛋白的来源，但含有较高的磷和嘌呤，需要根据肾功能情况控制食用量。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "猪肝", "level": "red", "reason": "猪肝含有极高的磷和嘌呤，不适合CKD患者食用。", "advice": "建议避免食用动物内脏。"},
    {"name": "猪肾", "level": "red", "reason": "猪肾含有极高的磷和嘌呤，不适合CKD患者食用。", "advice": "建议避免食用动物内脏。"},
    {"name": "鸡蛋黄", "level": "yellow", "reason": "鸡蛋黄含有较高的磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "鸭蛋黄", "level": "yellow", "reason": "鸭蛋黄含有较高的磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "鹅蛋", "level": "yellow", "reason": "鹅蛋含有较高的磷和蛋白质，需要根据肾功能情况控制食用量。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "牛奶", "level": "yellow", "reason": "牛奶含有较高的磷和蛋白质，肾功能不全的患者需要限制食用。", "advice": "可选择低磷牛奶或在医生指导下控制食用量。"},
    {"name": "羊奶", "level": "yellow", "reason": "羊奶含有较高的磷和蛋白质，肾功能不全的患者需要限制食用。", "advice": "可选择低磷羊奶或在医生指导下控制食用量。"},
    {"name": "酸奶", "level": "yellow", "reason": "酸奶含有较高的磷和蛋白质，肾功能不全的患者需要限制食用。", "advice": "可选择低磷酸奶或在医生指导下控制食用量。"},
    {"name": "奶酪", "level": "red", "reason": "奶酪含有极高的磷和蛋白质，不适合CKD患者食用。", "advice": "建议避免食用奶酪。"},
    {"name": "豆浆", "level": "yellow", "reason": "豆浆含有较高的植物蛋白和钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "豆腐脑", "level": "yellow", "reason": "豆腐脑含有较高的植物蛋白，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "豆腐干", "level": "yellow", "reason": "豆腐干含有较高的植物蛋白，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "豆腐皮", "level": "yellow", "reason": "豆腐皮含有较高的植物蛋白，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "腐竹", "level": "yellow", "reason": "腐竹含有较高的植物蛋白，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "红豆", "level": "yellow", "reason": "红豆含有较高的植物蛋白和钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "绿豆", "level": "yellow", "reason": "绿豆含有较高的植物蛋白和钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "黄豆", "level": "yellow", "reason": "黄豆含有较高的植物蛋白和钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "黑豆", "level": "yellow", "reason": "黑豆含有较高的植物蛋白和钾，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "花生", "level": "yellow", "reason": "花生含有较高的植物蛋白和磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "核桃", "level": "yellow", "reason": "核桃含有较高的植物蛋白和磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "杏仁", "level": "yellow", "reason": "杏仁含有较高的植物蛋白和磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "腰果", "level": "yellow", "reason": "腰果含有较高的植物蛋白和磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "开心果", "level": "yellow", "reason": "开心果含有较高的植物蛋白和磷，肾功能不全的患者需要限制食用。", "advice": "肾功能正常的患者可适量食用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "巧克力", "level": "red", "reason": "巧克力含有较高的钾、磷和脂肪，不适合CKD患者食用。", "advice": "建议避免食用巧克力。"},
    {"name": "冰淇淋", "level": "red", "reason": "冰淇淋含有较高的磷、钾和脂肪，不适合CKD患者食用。", "advice": "建议避免食用冰淇淋。"},
    {"name": "蛋糕", "level": "yellow", "reason": "蛋糕含有较高的钠和糖，需要注意选择低钠低糖的蛋糕。", "advice": "选择低钠低糖的蛋糕，每天可食用一小块。"},
    {"name": "饼干", "level": "yellow", "reason": "饼干含有较高的钠和糖，需要注意选择低钠低糖的饼干。", "advice": "选择低钠低糖的饼干，每天可食用少量。"},
    {"name": "薯片", "level": "red", "reason": "薯片含有极高的钠和脂肪，不适合CKD患者食用。", "advice": "建议避免食用油炸食品。"},
    {"name": "薯条", "level": "red", "reason": "薯条含有极高的钠和脂肪，不适合CKD患者食用。", "advice": "建议避免食用油炸食品。"},
    {"name": "汉堡", "level": "red", "reason": "汉堡含有极高的钠、脂肪和磷，不适合CKD患者食用。", "advice": "建议避免食用快餐食品。"},
    {"name": "披萨", "level": "red", "reason": "披萨含有极高的钠、脂肪和磷，不适合CKD患者食用。", "advice": "建议避免食用快餐食品。"},
    {"name": "方便面", "level": "red", "reason": "方便面含有极高的钠和防腐剂，不适合CKD患者食用。", "advice": "建议避免食用方便食品。"},
    {"name": "火腿肠", "level": "red", "reason": "火腿肠含有极高的钠、防腐剂和磷，不适合CKD患者食用。", "advice": "建议避免食用加工肉类。"},
    {"name": "腊肉", "level": "red", "reason": "腊肉含有极高的钠、防腐剂和磷，不适合CKD患者食用。", "advice": "建议避免食用加工肉类。"},
    {"name": "咸菜", "level": "red", "reason": "咸菜含有极高的钠，不适合CKD患者食用。", "advice": "建议避免食用腌制食品。"},
    {"name": "泡菜", "level": "red", "reason": "泡菜含有极高的钠，不适合CKD患者食用。", "advice": "建议避免食用腌制食品。"},
    {"name": "酱菜", "level": "red", "reason": "酱菜含有极高的钠，不适合CKD患者食用。", "advice": "建议避免食用腌制食品。"},
    {"name": "酱油", "level": "yellow", "reason": "酱油含有较高的钠，需要注意选择低钠酱油。", "advice": "选择低钠酱油，每天使用量不超过10毫升。"},
    {"name": "醋", "level": "green", "reason": "醋是低钠、低钾、低磷的调味品，适合所有CKD患者食用。", "advice": "每天可使用适量的醋。"},
    {"name": "盐", "level": "yellow", "reason": "盐含有钠，需要严格控制摄入量。", "advice": "每天盐摄入量不超过5克，肾功能不全的患者应控制在3克以内。"},
    {"name": "糖", "level": "green", "reason": "糖是低钠、低钾、低磷的调味品，适合所有CKD患者食用，但需要控制摄入量。", "advice": "每天糖摄入量不超过25克。"},
    {"name": "蜂蜜", "level": "green", "reason": "蜂蜜是低钠、低钾、低磷的调味品，适合所有CKD患者食用，但需要控制摄入量。", "advice": "每天蜂蜜摄入量不超过15毫升。"},
    {"name": "橄榄油", "level": "green", "reason": "橄榄油是健康的脂肪来源，适合所有CKD患者食用。", "advice": "每天可使用10-15毫升橄榄油。"},
    {"name": "花生油", "level": "green", "reason": "花生油是健康的脂肪来源，适合所有CKD患者食用。", "advice": "每天可使用10-15毫升花生油。"},
    {"name": "大豆油", "level": "green", "reason": "大豆油是健康的脂肪来源，适合所有CKD患者食用。", "advice": "每天可使用10-15毫升大豆油。"},
    {"name": "玉米油", "level": "green", "reason": "玉米油是健康的脂肪来源，适合所有CKD患者食用。", "advice": "每天可使用10-15毫升玉米油。"},
    {"name": "葵花籽油", "level": "green", "reason": "葵花籽油是健康的脂肪来源，适合所有CKD患者食用。", "advice": "每天可使用10-15毫升葵花籽油。"},
    {"name": "猪油", "level": "yellow", "reason": "猪油含有较高的饱和脂肪，需要限制食用。", "advice": "建议选择植物油，猪油应少量食用。"},
    {"name": "牛油", "level": "yellow", "reason": "牛油含有较高的饱和脂肪，需要限制食用。", "advice": "建议选择植物油，牛油应少量食用。"},
    {"name": "羊油", "level": "yellow", "reason": "羊油含有较高的饱和脂肪，需要限制食用。", "advice": "建议选择植物油，羊油应少量食用。"},
    {"name": "茶", "level": "green", "reason": "茶是低钠、低钾、低磷的饮品，适合所有CKD患者食用。", "advice": "每天可饮用2-3杯茶，但避免饮用浓茶。"},
    {"name": "咖啡", "level": "green", "reason": "咖啡是低钠、低钾、低磷的饮品，适合所有CKD患者食用，但需要控制摄入量。", "advice": "每天可饮用1-2杯咖啡，避免添加过多的糖和奶。"},
    {"name": "果汁", "level": "yellow", "reason": "果汁含有较高的钾和糖，需要限制食用。", "advice": "肾功能正常的患者可适量饮用，肾功能不全的患者应在医生指导下控制食用量。"},
    {"name": "可乐", "level": "red", "reason": "可乐含有较高的磷和糖，不适合CKD患者食用。", "advice": "建议避免饮用碳酸饮料。"},
    {"name": "雪碧", "level": "yellow", "reason": "雪碧含有较高的糖，需要限制食用。", "advice": "可少量饮用，但避免过量。"},
    {"name": "矿泉水", "level": "green", "reason": "矿泉水是低钠、低钾、低磷的饮品，适合所有CKD患者食用。", "advice": "每天可饮用1500-2000毫升矿泉水。"},
    {"name": "纯净水", "level": "green", "reason": "纯净水是低钠、低钾、低磷的饮品，适合所有CKD患者食用。", "advice": "每天可饮用1500-2000毫升纯净水。"}
]

# 预设食谱数据
RECIPES = [
    {
        "dishName": "清蒸鲈鱼",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["鲈鱼 1条", "姜丝 10克", "葱段 20克", "料酒 5毫升", "盐 2克", "蒸鱼豉油 10毫升"],
        "steps": ["1. 将鲈鱼洗净，在鱼身上划几刀", "2. 在鱼身上撒上姜丝和葱段", "3. 淋上料酒和少许盐", "4. 放入蒸锅中蒸8-10分钟", "5. 取出后淋上蒸鱼豉油即可"],
        "nutritionBenefit": "鲈鱼是优质蛋白的来源，含有丰富的不饱和脂肪酸，有助于降低血脂。清蒸的烹饪方式减少了油脂的摄入，适合CKD患者食用。"
    },
    {
        "dishName": "清炒西兰花",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["西兰花 200克", "蒜末 10克", "盐 2克", "植物油 10毫升"],
        "steps": ["1. 将西兰花切成小朵，洗净", "2. 锅中烧开水，放入西兰花焯水1-2分钟", "3. 锅中倒入植物油，爆香蒜末", "4. 放入西兰花翻炒均匀", "5. 加入少许盐调味即可"],
        "nutritionBenefit": "西兰花富含维生素C和膳食纤维，有助于增强免疫力和促进肠道健康。清炒的烹饪方式减少了油脂的摄入，适合CKD患者食用。"
    },
    {
        "dishName": "番茄鸡蛋汤",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["番茄 1个", "鸡蛋 1个", "葱花 5克", "盐 2克", "植物油 5毫升", "水 500毫升"],
        "steps": ["1. 将番茄洗净，切成小块", "2. 锅中倒入植物油，放入番茄翻炒出汁", "3. 加入水烧开", "4. 将鸡蛋打散，缓慢倒入锅中", "5. 加入少许盐调味，撒上葱花即可"],
        "nutritionBenefit": "番茄富含维生素C和番茄红素，有助于抗氧化和保护心血管健康。鸡蛋是优质蛋白的来源，番茄鸡蛋汤清淡易消化，适合CKD患者食用。"
    },
    {
        "dishName": "凉拌黄瓜",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["黄瓜 1根", "蒜末 5克", "醋 10毫升", "香油 5毫升", "盐 2克"],
        "steps": ["1. 将黄瓜洗净，拍碎切块", "2. 加入蒜末、醋、香油和少许盐", "3. 搅拌均匀即可"],
        "nutritionBenefit": "黄瓜富含水分和膳食纤维，有助于清热解渴和促进肠道健康。凉拌的烹饪方式减少了油脂的摄入，适合CKD患者食用。"
    },
    {
        "dishName": "南瓜粥",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["南瓜 100克", "大米 50克", "水 500毫升"],
        "steps": ["1. 将南瓜洗净，去皮切块", "2. 将大米洗净", "3. 锅中加入水，放入大米和南瓜", "4. 大火烧开后转小火煮30分钟", "5. 煮至粥浓稠即可"],
        "nutritionBenefit": "南瓜富含胡萝卜素和膳食纤维，有助于保护视力和促进肠道健康。南瓜粥清淡易消化，适合CKD患者食用。"
    },
    {
        "dishName": "冬瓜排骨汤",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["冬瓜 200克", "排骨 100克", "姜 5克", "盐 2克", "水 800毫升"],
        "steps": ["1. 将排骨洗净，焯水去除血水", "2. 冬瓜洗净，去皮切块", "3. 锅中加入水，放入排骨和姜", "4. 大火烧开后转小火煮40分钟", "5. 加入冬瓜继续煮20分钟", "6. 加入少许盐调味即可"],
        "nutritionBenefit": "冬瓜富含水分和膳食纤维，有助于清热解渴和促进排尿。排骨是优质蛋白的来源，冬瓜排骨汤清淡易消化，适合CKD患者食用。"
    },
    {
        "dishName": "炒藕片",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["藕 1节", "蒜末 5克", "盐 2克", "植物油 10毫升"],
        "steps": ["1. 将藕洗净，去皮切片", "2. 锅中烧开水，放入藕片焯水1-2分钟", "3. 锅中倒入植物油，爆香蒜末", "4. 放入藕片翻炒均匀", "5. 加入少许盐调味即可"],
        "nutritionBenefit": "藕富含膳食纤维和维生素C，有助于促进肠道健康和增强免疫力。清炒的烹饪方式减少了油脂的摄入，适合CKD患者食用。"
    },
    {
        "dishName": "鸡蛋羹",
        "tags": ["低蛋白", "低磷", "低钠", "低钾"],
        "ingredients": ["鸡蛋 1个", "温水 150毫升", "盐 1克", "香油 2毫升"],
        "steps": ["1. 将鸡蛋打散", "2. 加入温水和少许盐，搅拌均匀", "3. 撇去浮沫", "4. 放入蒸锅中蒸10分钟", "5. 淋上香油即可"],
        "nutritionBenefit": "鸡蛋是优质蛋白的来源，鸡蛋羹清淡易消化，适合CKD患者食用。"
    }
]

@app.get("/api/fallback/foods")
async def get_fallback_foods():
    return FOOD_ITEMS

@app.get("/api/fallback/recipes")
async def get_fallback_recipes():
    return RECIPES

# 食物白名单
@app.get("/api/food-whitelist")
async def get_food_whitelist():
    # 从预设食物数据中筛选绿色级别食物
    whitelist = [item for item in FOOD_ITEMS if item["level"] == "green"]
    return whitelist

# 食物黑名单
@app.get("/api/food-blacklist")
async def get_food_blacklist():
    # 从预设食物数据中筛选红色级别食物
    blacklist = [item for item in FOOD_ITEMS if item["level"] == "red"]
    return blacklist