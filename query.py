from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from pgvector.sqlalchemy import cosine_distance
from ..db.session import get_db
from ..models.document import Document

router = APIRouter()


def nl_to_sql_placeholder(query: str) -> str:
    q = query.lower()
    base = "SELECT customer_id, name, churn_risk AS churn_pct, churn_reason FROM customers WHERE 1=1"
    if ">" in q and "churn" in q:
        # naive parse threshold like >80
        import re
        m = re.search(r">\s*(\d+)", q)
        if m:
            base += f" AND churn_risk > {m.group(1)}"
    if "delhi" in q:
        base += " AND lower(region) = 'delhi'"
    if "bill" in q or "monthly" in q:
        import re
        m = re.search(r">\s*₹?\s*(\d+)", q)
        if m:
            base += f" AND monthly_bill > {m.group(1)}"
    return base + " ORDER BY churn_risk DESC LIMIT 200"


@router.post("/sql")
async def generate_sql(nl_query: str):
    sql = nl_to_sql_placeholder(nl_query)
    return {"sql": sql}


@router.post("/execute")
async def execute_sql(nl_query: str, db: Session = Depends(get_db)):
    sql = nl_to_sql_placeholder(nl_query)
    # Placeholder: skip actual execution without ORM mapping here
    return {"sql": sql, "rows": []}


# Vector search over documents
from sentence_transformers import SentenceTransformer
_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model


@router.get("/vector-search")
async def vector_search(q: str, k: int = 5, db: Session = Depends(get_db)):
    model = get_model()
    emb = model.encode([q], normalize_embeddings=True)[0].tolist()
    stmt = (
        select(Document)
        .order_by(cosine_distance(Document.embedding, emb))
        .limit(k)
    )
    rows = db.execute(stmt).scalars().all()
    return {
        "query": q,
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "source": r.source,
                "customer_id": r.customer_id,
                "text": r.text[:500] + ("…" if len(r.text) > 500 else ""),
            }
            for r in rows
        ],
    }
