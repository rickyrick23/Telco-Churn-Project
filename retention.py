from fastapi import APIRouter

router = APIRouter()


@router.post("/recommend")
async def recommend_actions(customer_id: str, churn_risk: float, top_reason: str | None = None):
    if churn_risk >= 80:
        offer = "20% discount for 3 months + priority support"
        campaign = "discount"
    elif churn_risk >= 50:
        offer = "Plan change to better value + loyalty reward"
        campaign = "plan_change"
    else:
        offer = "Loyalty reward and check-in call"
        campaign = "loyalty"
    script = (
        f"Hello, I'm calling regarding your recent experience. We value you. "
        f"I'd like to offer {offer}. Does that sound fair?"
    )
    return {"customer_id": customer_id, "offer": offer, "campaign": campaign, "script": script}
