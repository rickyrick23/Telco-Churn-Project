from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

router = APIRouter()
_analyzer = SentimentIntensityAnalyzer()


@router.post("/sentiment")
async def analyze_sentiment(text: str, db: Session = Depends(get_db)):
    scores = _analyzer.polarity_scores(text)
    label = "Positive" if scores["compound"] > 0.05 else ("Negative" if scores["compound"] < -0.05 else "Neutral")
    return {"label": label, "scores": scores}


@router.post("/topic")
async def topic_model_placeholder(texts: list[str], db: Session = Depends(get_db)):
    # Placeholder: return simple keywords-based tags
    tags = []
    for t in texts:
        t_low = t.lower()
        if "bill" in t_low:
            tags.append("Billing Issue")
        elif "network" in t_low or "signal" in t_low:
            tags.append("Network Problem")
        elif "offer" in t_low or "port" in t_low:
            tags.append("Competitor Offer")
        else:
            tags.append("General")
    return {"topics": tags}
