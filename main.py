from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.session import init_db
from .routers import ingestion, analysis, churn, query, retention, insights, dashboard

app = FastAPI(title="Churn Prediction Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion.router, prefix="/ingestion", tags=["Module 1 – Ingestion & Preprocessing"]) 
app.include_router(analysis.router, prefix="/analysis", tags=["Module 2 – Sentiment & Topic"]) 
app.include_router(churn.router, prefix="/churn", tags=["Module 3 – Churn Prediction"]) 
app.include_router(query.router, prefix="/query", tags=["Module 4 – NL Query"]) 
app.include_router(retention.router, prefix="/retention", tags=["Module 5 – Retention Strategy"]) 
app.include_router(insights.router, prefix="/insights", tags=["Module 6 – Multi-Modal Insights"]) 
app.include_router(dashboard.router, prefix="/dashboard", tags=["Module 7 – Dashboard & Alerts"]) 


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}
