from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
from typing import Dict, Any

from .config import settings
from .api.chat import router as chat_router
from .utils.helpers import create_error_response

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="多语言检索增强商品问答 Agent API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.error(f"请求验证错误: {exc}")
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            message="请求数据验证失败",
            error_code="VALIDATION_ERROR"
        )
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP异常"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=str(exc.detail),
            error_code=f"HTTP_{exc.status_code}"
        )
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            message="服务器内部错误",
            error_code="INTERNAL_ERROR"
        )
    )

# 注册路由
app.include_router(chat_router)

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用多语言检索增强商品问答 Agent",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION
    }

# 应用信息
@app.get("/info")
async def app_info():
    """应用信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "多语言检索增强商品问答 Agent",
        "features": [
            "多语言支持（中文/英文）",
            "RAG检索增强",
            "上下文记忆管理",
            "智能Agent响应"
        ],
        "endpoints": {
            "chat": "/api/v1/chat",
            "history": "/api/v1/history/{session_id}",
            "search": "/api/v1/search",
            "language_detection": "/api/v1/detect-language"
        }
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("初始化服务...")
    
    # 这里可以添加启动时的初始化逻辑
    # 例如：初始化数据库连接、加载模型等

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("正在关闭应用...")
    
    # 这里可以添加关闭时的清理逻辑
    # 例如：关闭数据库连接、保存缓存等

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 