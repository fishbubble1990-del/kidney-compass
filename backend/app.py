# Hugging Face Spaces 入口文件
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uvicorn import run

# 导入主应用
from main import app as main_app

# 创建 Hugging Face Spaces 应用
app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径重定向到 main_app
@app.get("/")
async def root():
    return {"message": "Kidney Compass Backend - Hugging Face Spaces"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Kidney Compass Backend is running!"}

# 挂载主应用的所有路由
app.include_router(main_app.router, prefix="")

if __name__ == "__main__":
    # Hugging Face Spaces 使用 7860 端口
    port = int(os.environ.get("PORT", 7860))
    run("app:app", host="0.0.0.0", port=port)
