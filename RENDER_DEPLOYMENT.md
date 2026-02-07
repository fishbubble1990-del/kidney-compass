# Render 部署指南

## 部署步骤

### 1. 创建 Render 账户
- 访问 https://render.com 注册账户

### 2. 新建 Web 服务
1. 登录 Render 控制台
2. 点击 "New" → "Web Service"
3. 选择 "GitHub" 作为代码源
4. 选择 kidney-compass 仓库
5. 配置部署设置：
   - **Name**: kidney-compass-backend
   - **Region**: Singapore 或 Oregon
   - **Branch**: main
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

### 3. 配置环境变量
在 "Environment Variables" 部分添加以下变量：

| 变量名 | 值 |
|--------|-----|
| SUPABASE_URL | https://fdpglrvsxuztgwvhlamd.supabase.co |
| SUPABASE_KEY | sb_publishable_zvTXR4EL2ChwRSKjKGyn1A_BFZdD-mw |
| GEMINI_API_KEY | gen-lang-client-0962011102 |

### 4. 部署服务
- 点击 "Create Web Service" 开始部署
- 等待部署完成

### 5. 验证部署
- 访问 Render 提供的服务 URL
- 测试健康检查端点：`/api/health`
- 测试核心功能：
  - 食物白名单：`GET /api/food-whitelist`
  - 食物黑名单：`GET /api/food-blacklist`
  - 食谱生成：`POST /api/recipe`

### 6. 配置自动部署
- 在 Render 服务页面，点击 "Settings" 标签
- 确保 "Auto-Deploy" 选项已启用

## 部署文件说明

- **Procfile**: 定义了应用的启动命令
- **requirements.txt**: 定义了 Python 依赖
- **render.yaml**: Render 部署配置文件（可选）

## 故障排除

- 如果部署失败，检查构建日志
- 确保所有环境变量都已正确配置
- 验证 requirements.txt 中的依赖是否正确
- 检查 Procfile 配置是否正确