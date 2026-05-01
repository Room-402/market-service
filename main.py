from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routes import market
from app.api.v1.routes.stock import router as stock_router
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS middleware — allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(market.router, prefix="/api/v1")
app.include_router(stock_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}