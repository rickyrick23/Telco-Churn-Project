from fastapi import APIRouter

router = APIRouter()


@router.get("/customer/{customer_id}")
async def customer_insights(customer_id: str):
    return {
        "customer_id": customer_id,
        "summary": "Usage down 35%, negative sentiment on billing, high bill",
        "structured": {"usage_drop_pct": 35, "monthly_bill": 1200},
        "unstructured": {"sentiment": "Negative", "topic": "Billing Issue"},
    }
