from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.routes import market
from app.api.v1.routes.stock import router as stock_router
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Register routers
app.include_router(market.router, prefix="/api/v1")
app.include_router(stock_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}