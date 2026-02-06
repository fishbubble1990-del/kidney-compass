# 自动部署配置

本项目已配置 GitHub Actions 实现全自动部署。

## 部署流程

### 前端部署到 Vercel
- **触发条件**：推送到 `main` 分支
- **自动执行**：构建前端并部署到 Vercel

### 后端部署到 Railway
- **触发条件**：推送到 `main` 分支且修改了 `backend/` 目录
- **自动执行**：部署后端到 Railway

## 初始配置步骤

### 1. 配置 Vercel 部署

1. 访问 https://vercel.com/account/tokens
2. 创建新的 Token，选择 "Full Account" 权限
3. 复制生成的 Token

4. 访问你的 GitHub 仓库设置
5. 进入 "Settings" → "Secrets and variables" → "Actions"
6. 添加以下 Secrets：
   - `VERCEL_TOKEN`：你刚才创建的 Vercel Token
   - `VERCEL_ORG_ID`：你的 Vercel 组织 ID（可选）
   - `VERCEL_PROJECT_ID`：你的 Vercel 项目 ID（可选）

### 2. 配置 Railway 部署

1. 访问 https://railway.app/account/tokens
2. 创建新的 API Token
3. 复制生成的 Token

4. 在 GitHub 仓库的 Secrets 中添加：
   - `RAILWAY_TOKEN`：你刚才创建的 Railway Token
   - `RAILWAY_SERVICE_ID`：你的 Railway 服务 ID（可选）

### 3. 首次手动部署

由于 GitHub Actions 只在代码推送到 GitHub 后触发，你需要：

1. **在 Vercel 创建项目**：
   - 访问 https://vercel.com/new
   - 从 GitHub 导入 `kidney-compass` 仓库
   - 配置项目设置并完成首次部署

2. **在 Railway 创建项目**：
   - 访问 https://railway.app/new
   - 从 GitHub 导入 `kidney-compass` 仓库
   - 选择 `backend` 目录作为根目录
   - 配置环境变量并完成首次部署

3. **获取项目 ID**（可选）：
   - Vercel 项目 ID：在项目设置中找到
   - Railway 服务 ID：在服务设置中找到
   - 将这些 ID 添加到 GitHub Secrets 中

## 使用方法

### 自动部署

配置完成后，每次你推送代码到 GitHub 的 `main` 分支时：

1. **前端**会自动构建并部署到 Vercel
2. **后端**会自动部署到 Railway（如果修改了 backend/ 目录）
3. 你可以在 GitHub Actions 标签页查看部署进度和日志

### 手动触发部署

你也可以手动触发部署：

1. 访问 GitHub 仓库的 "Actions" 标签页
2. 选择 "Deploy Frontend to Vercel" 或 "Deploy Backend to Railway"
3. 点击右侧的 "Run workflow" 按钮
4. 选择分支（通常是 `main`）
5. 点击 "Run workflow" 开始部署

## 环境变量配置

### Vercel 环境变量
在 Vercel 项目设置中添加：
- `SUPABASE_URL`：你的 Supabase 项目 URL
- `SUPABASE_KEY`：你的 Supabase 匿名 API 密钥
- `GEMINI_API_KEY`：你的 Google Gemini API 密钥

### Railway 环境变量
在 Railway 项目设置中添加：
- `SUPABASE_URL`：你的 Supabase 项目 URL
- `SUPABASE_KEY`：你的 Supabase 匿名 API 密钥
- `SUPABASE_SERVICE_ROLE_KEY`：你的 Supabase 服务角色密钥
- `GEMINI_API_KEY`：你的 Google Gemini API 密钥

## 部署 URL

部署完成后，你会获得以下 URL：

- **前端**：`https://kidney-compass.vercel.app`（或你的自定义域名）
- **后端**：`https://kidney-compass-backend.up.railway.app`（或 Railway 提供的 URL）

## 注意事项

1. **首次部署**：必须先在 Vercel 和 Railway 上手动创建项目
2. **环境变量**：确保在两个平台都配置了相同的环境变量
3. **部署时间**：通常需要 2-5 分钟完成
4. **监控**：在 GitHub Actions 和平台控制台中监控部署状态
5. **回滚**：如果部署失败，可以在平台控制台中回滚到之前的版本

## 故障排除

### 部署失败
- 检查 GitHub Actions 日志
- 确认所有 Secrets 都已正确配置
- 验证项目 ID 是否正确

### 环境变量错误
- 确保在 Vercel 和 Railway 中都配置了所有必需的环境变量
- 检查变量名是否完全匹配（区分大小写）
- 验证 API 密钥是否有效

### 连接问题
- 确保前端正确配置了后端 URL
- 检查 CORS 配置是否允许前端访问
- 验证后端服务是否正常运行