import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取 Supabase 配置
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# 如果没有服务角色密钥，尝试使用普通密钥
if not key:
    key = os.environ.get("SUPABASE_KEY")
    print("⚠️  未检测到 SUPABASE_SERVICE_ROLE_KEY，使用普通 SUPABASE_KEY 尝试初始化（可能权限不足）")

if not url or not key:
    print("错误: 未检测到有效的 SUPABASE_URL 或 SUPABASE_KEY，请检查 .env 文件")
    exit(1)

print(f"🔗 连接到 Supabase: {url}")

# 初始化 Supabase 客户端
try:
    supabase: Client = create_client(url, key)
    print("✅ Supabase 客户端初始化成功")
except Exception as e:
    print(f"❌ Supabase 客户端初始化失败: {e}")
    exit(1)

# 创建数据表
def create_tables():
    print("\n开始创建数据表...")
    
    # 创建每日记录表
    try:
        supabase.table('daily_records').insert({
            'user_id': 'test_user',
            'date': '2023-10-21',
            'weight': 72.1,
            'systolic': 125,
            'diastolic': 82,
            'bp_hand': 'left',
            'edema': False,
            'hematuria': False,
            'foamy_urine': True,
            'water_intake': 1800
        }).execute()
        print("✅ 每日记录表创建成功")
    except Exception as e:
        print(f"❌ 每日记录表创建失败: {e}")
    
    # 创建食物分类表
    try:
        supabase.table('food_classifications').insert({
            'name': '火锅',
            'level': 'yellow',
            'reason': '火锅通常含有较高的盐分和嘌呤，可能会增加肾脏负担。',
            'advice': '建议选择清淡汤底，避免食用内脏和加工肉类，控制食用频率。',
            'type': 'food'
        }).execute()
        print("✅ 食物分类表创建成功")
    except Exception as e:
        print(f"❌ 食物分类表创建失败: {e}")
    
    # 创建食谱表
    try:
        supabase.table('recipes').insert({
            'dish_name': '清蒸鲈鱼',
            'tags': ['优质蛋白', '低油', '低盐', '低磷', '低钾'],
            'ingredients': ['鲈鱼 1条', '姜丝 适量', '葱段 适量', '低钠酱油 少许'],
            'steps': ['鲈鱼洗净划刀', '放姜葱蒸8分钟', '倒掉汤汁淋少许热油和酱油'],
            'nutrition_benefit': '鲈鱼富含优质蛋白质，低脂肪，低磷低钾，适合 IgA CKD 3期和病理4级患者食用。清蒸的烹饪方式保留了鱼肉的营养，同时减少了油脂的摄入。'
        }).execute()
        print("✅ 食谱表创建成功")
    except Exception as e:
        print(f"❌ 食谱表创建失败: {e}")
    
    # 创建食物白名单表
    try:
        supabase.table('food_whitelist').insert({
            'category': '肉类',
            'name': '鸡胸肉',
            'note': '优质蛋白，必须去皮切片焯水'
        }).execute()
        print("✅ 食物白名单表创建成功")
    except Exception as e:
        print(f"❌ 食物白名单表创建失败: {e}")
    
    # 创建食物黑名单表
    try:
        supabase.table('food_blacklist').insert({
            'name': '火锅',
            'reason': '高盐高嘌呤，加重肾脏负担',
            'level': 'red'
        }).execute()
        print("✅ 食物黑名单表创建成功")
    except Exception as e:
        print(f"❌ 食物黑名单表创建失败: {e}")

# 导入初始数据
def import_initial_data():
    print("\n开始导入初始数据...")
    
    # 导入食物分类数据
    food_data = [
        {
            'name': '苹果',
            'level': 'green',
            'reason': '苹果富含纤维和抗氧化物质，钾含量适中，适合肾病患者食用。',
            'advice': '每天可食用1个中等大小的苹果，最好带皮食用以获取更多营养。',
            'type': 'food'
        },
        {
            'name': '香蕉',
            'level': 'yellow',
            'reason': '香蕉钾含量较高，肾功能不全患者需要注意控制摄入量。',
            'advice': '每周食用不超过2次，每次半根，避免在高血钾时食用。',
            'type': 'food'
        },
        {
            'name': '西瓜',
            'level': 'yellow',
            'reason': '西瓜含水量高，可能会增加尿量，但同时也含有一定量的钾。',
            'advice': '适量食用，每天不超过200克，避免在水肿或少尿时食用。',
            'type': 'food'
        },
        {
            'name': '菠菜',
            'level': 'yellow',
            'reason': '菠菜富含草酸和钾，可能会影响钙的吸收和增加肾脏负担。',
            'advice': '焯水后食用，减少草酸含量，每周食用不超过2次。',
            'type': 'food'
        },
        {
            'name': '豆腐',
            'level': 'yellow',
            'reason': '豆腐含有一定量的磷和植物蛋白，肾功能不全患者需要注意控制摄入量。',
            'advice': '每周食用不超过2次，每次不超过100克，避免与高磷食物同时食用。',
            'type': 'food'
        },
        {
            'name': '米饭',
            'level': 'green',
            'reason': '米饭是碳水化合物的主要来源，低钾低磷低钠，适合肾病患者作为主食。',
            'advice': '可作为日常主食，建议与优质蛋白和蔬菜搭配食用。',
            'type': 'food'
        },
        {
            'name': '面条',
            'level': 'green',
            'reason': '面条是碳水化合物的主要来源，低钾低磷低钠，适合肾病患者作为主食。',
            'advice': '可作为日常主食，建议选择全麦面条以获取更多纤维。',
            'type': 'food'
        },
        {
            'name': '鸡蛋',
            'level': 'green',
            'reason': '鸡蛋是优质蛋白质的良好来源，低钾低磷，适合肾病患者食用。',
            'advice': '每天可食用1-2个鸡蛋，最好选择煮鸡蛋或蒸鸡蛋。',
            'type': 'food'
        },
        {
            'name': '牛奶',
            'level': 'yellow',
            'reason': '牛奶含有一定量的磷和钾，肾功能不全患者需要注意控制摄入量。',
            'advice': '每周食用不超过3次，每次不超过200毫升，可选择低磷牛奶。',
            'type': 'food'
        },
        {
            'name': '瘦肉',
            'level': 'green',
            'reason': '瘦肉是优质蛋白质的良好来源，低钾低磷，适合肾病患者食用。',
            'advice': '每天可食用50-100克瘦肉，选择猪瘦肉、鸡肉或鱼肉。',
            'type': 'food'
        }
    ]
    
    print("\n📥 导入食物分类数据...")
    success_count = 0
    failure_count = 0
    
    for food in food_data:
        try:
            # 先检查是否已存在
            existing = supabase.table('food_classifications').select('*').eq('name', food['name']).execute()
            if existing.data and len(existing.data) > 0:
                print(f"⚠️  食物 {food['name']} 已存在，跳过导入")
                continue
            
            supabase.table('food_classifications').insert(food).execute()
            print(f"✅ 导入食物: {food['name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ 导入食物失败 {food['name']}: {e}")
            failure_count += 1
    
    print(f"\n🍎 食物分类数据导入完成: 成功 {success_count}, 失败 {failure_count}")
    
    # 导入食谱数据
    recipe_data = [
        {
            'dish_name': '鸡蛋白菜汤',
            'tags': ['优质蛋白', '低磷', '低钾', '低钠', '低蛋白'],
            'ingredients': ['鸡蛋 2个', '白菜 200克', '葱花 适量', '低钠盐 少许'],
            'steps': ['鸡蛋打散', '白菜切丝', '水烧开后加入白菜', '煮沸后淋入蛋液', '加低钠盐调味即可'],
            'nutrition_benefit': '鸡蛋提供优质蛋白质，白菜富含维生素和纤维，低钾低磷低钠，适合 IgA CKD 3期和病理4级患者日常食用。'
        },
        {
            'dish_name': '冬瓜排骨汤',
            'tags': ['低磷', '低钾', '低钠', '低蛋白'],
            'ingredients': ['排骨 100克', '冬瓜 200克', '姜 2片', '低钠盐 少许'],
            'steps': ['排骨焯水去血沫', '冬瓜切块', '所有材料放入锅中加水煮30分钟', '加低钠盐调味即可'],
            'nutrition_benefit': '冬瓜有利尿作用，排骨提供少量优质蛋白质，此汤低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。'
        },
        {
            'dish_name': '番茄鸡蛋面',
            'tags': ['低磷', '低钾', '低钠', '低蛋白'],
            'ingredients': ['面条 50克', '番茄 1个', '鸡蛋 1个', '葱花 适量', '低钠盐 少许'],
            'steps': ['番茄切块炒软', '加水烧开', '下面条煮至八分熟', '淋入蛋液', '加低钠盐调味即可'],
            'nutrition_benefit': '番茄富含维生素C，鸡蛋提供优质蛋白质，面条提供能量，此餐低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。'
        },
        {
            'dish_name': '清炒西兰花',
            'tags': ['低磷', '低钾', '低钠', '低蛋白', '高纤维'],
            'ingredients': ['西兰花 200克', '蒜末 适量', '低钠盐 少许', '植物油 少许'],
            'steps': ['西兰花切小朵焯水', '锅中放油爆香蒜末', '加入西兰花翻炒', '加低钠盐调味即可'],
            'nutrition_benefit': '西兰花富含维生素和纤维，低磷低钾低钠，适合 IgA CKD 3期和病理4级患者食用。'
        },
        {
            'dish_name': '清蒸鲈鱼',
            'tags': ['优质蛋白', '低油', '低盐', '低磷', '低钾'],
            'ingredients': ['鲈鱼 1条', '姜丝 适量', '葱段 适量', '低钠酱油 少许'],
            'steps': ['鲈鱼洗净划刀', '放姜葱蒸8分钟', '倒掉汤汁淋少许热油和酱油'],
            'nutrition_benefit': '鲈鱼富含优质蛋白质，低脂肪，低磷低钾，适合 IgA CKD 3期和病理4级患者食用。清蒸的烹饪方式保留了鱼肉的营养，同时减少了油脂的摄入。'
        }
    ]
    
    print("\n📥 导入食谱数据...")
    success_count = 0
    failure_count = 0
    
    for recipe in recipe_data:
        try:
            # 先检查是否已存在
            existing = supabase.table('recipes').select('*').eq('dish_name', recipe['dish_name']).execute()
            if existing.data and len(existing.data) > 0:
                print(f"⚠️  食谱 {recipe['dish_name']} 已存在，跳过导入")
                continue
            
            supabase.table('recipes').insert(recipe).execute()
            print(f"✅ 导入食谱: {recipe['dish_name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ 导入食谱失败 {recipe['dish_name']}: {e}")
            failure_count += 1
    
    print(f"\n🍲 食谱数据导入完成: 成功 {success_count}, 失败 {failure_count}")
    
    # 导入食物白名单数据
    whitelist_data = [
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
    
    print("\n📥 导入食物白名单数据...")
    success_count = 0
    failure_count = 0
    
    for item in whitelist_data:
        try:
            # 先检查是否已存在
            existing = supabase.table('food_whitelist').select('*').eq('name', item['name']).execute()
            if existing.data and len(existing.data) > 0:
                print(f"⚠️  食物白名单项目 {item['name']} 已存在，跳过导入")
                continue
            
            supabase.table('food_whitelist').insert(item).execute()
            print(f"✅ 导入食物白名单项目: {item['name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ 导入食物白名单项目失败 {item['name']}: {e}")
            failure_count += 1
    
    print(f"\n✅ 食物白名单数据导入完成: 成功 {success_count}, 失败 {failure_count}")
    
    # 导入食物黑名单数据
    blacklist_data = [
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
    
    print("\n📥 导入食物黑名单数据...")
    success_count = 0
    failure_count = 0
    
    for item in blacklist_data:
        try:
            # 先检查是否已存在
            existing = supabase.table('food_blacklist').select('*').eq('name', item['name']).execute()
            if existing.data and len(existing.data) > 0:
                print(f"⚠️  食物黑名单项目 {item['name']} 已存在，跳过导入")
                continue
            
            supabase.table('food_blacklist').insert(item).execute()
            print(f"✅ 导入食物黑名单项目: {item['name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ 导入食物黑名单项目失败 {item['name']}: {e}")
            failure_count += 1
    
    print(f"\n✅ 食物黑名单数据导入完成: 成功 {success_count}, 失败 {failure_count}")

# 验证数据导入结果
def verify_data():
    print("\n🔍 验证数据导入结果...")
    
    # 验证食物分类数据
    try:
        result = supabase.table('food_classifications').select('*').execute()
        if result.data:
            print(f"✅ 食物分类表中共有 {len(result.data)} 条数据")
            print("\n📋 部分食物分类数据:")
            for i, food in enumerate(result.data[:5]):
                print(f"  {i+1}. {food['name']} - {food['level']}")
        else:
            print("❌ 食物分类表中没有数据")
    except Exception as e:
        print(f"❌ 验证食物分类数据失败: {e}")
    
    # 验证食谱数据
    try:
        result = supabase.table('recipes').select('*').execute()
        if result.data:
            print(f"\n✅ 食谱表中共有 {len(result.data)} 条数据")
            print("\n🍲 部分食谱数据:")
            for i, recipe in enumerate(result.data[:3]):
                print(f"  {i+1}. {recipe['dish_name']}")
        else:
            print("\n❌ 食谱表中没有数据")
    except Exception as e:
        print(f"\n❌ 验证食谱数据失败: {e}")
    
    # 验证食物白名单数据
    try:
        result = supabase.table('food_whitelist').select('*').execute()
        if result.data:
            print(f"\n✅ 食物白名单表中共有 {len(result.data)} 条数据")
            print("\n📋 部分食物白名单数据:")
            for i, item in enumerate(result.data[:5]):
                print(f"  {i+1}. {item['category']} - {item['name']}")
        else:
            print("\n❌ 食物白名单表中没有数据")
    except Exception as e:
        print(f"\n❌ 验证食物白名单数据失败: {e}")
    
    # 验证食物黑名单数据
    try:
        result = supabase.table('food_blacklist').select('*').execute()
        if result.data:
            print(f"\n✅ 食物黑名单表中共有 {len(result.data)} 条数据")
            print("\n📋 部分食物黑名单数据:")
            for i, item in enumerate(result.data[:5]):
                print(f"  {i+1}. {item['name']} - {item['level']}")
        else:
            print("\n❌ 食物黑名单表中没有数据")
    except Exception as e:
        print(f"\n❌ 验证食物黑名单数据失败: {e}")

if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    create_tables()
    import_initial_data()
    verify_data()
    print("\n🎉 数据库初始化完成！")
    print("\n💡 提示：")
    print("   1. 如需添加更多食物分类数据，请修改 food_data 列表")
    print("   2. 如需添加更多食谱数据，请修改 recipe_data 列表")
    print("   3. 如需使用更高权限的操作，请在 .env 文件中添加 SUPABASE_SERVICE_ROLE_KEY")
