from fastapi import APIRouter

router = APIRouter()


@router.get("/metrics")
async def metrics():
    return {
        "daily_churn_trend": [
            {"date": "2025-01-01", "avg_risk": 42},
            {"date": "2025-01-02", "avg_risk": 44},
        ],
        "top_reasons": [
            {"reason": "Billing Issue", "count": 120},
            {"reason": "Network Problem", "count": 95},
        ],
        "distribution_by_region": [
            {"region": "Delhi", "avg_risk": 48},
            {"region": "Mumbai", "avg_risk": 41},
        ],
    }


@router.get("/alerts")
async def alerts(threshold: float = 80, min_value: float = 1000):
    return {
        "threshold": threshold,
        "alerts": [
            {"customer_id": "CUST0001", "risk": 92, "bill": 2200},
            {"customer_id": "CUST0005", "risk": 87, "bill": 1450},
        ],
    }
