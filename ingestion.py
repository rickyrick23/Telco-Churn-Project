from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db.session import get_db
import pandas as pd
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from ..models.document import Document

router = APIRouter()

# Lazy global
_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model


@router.get("/customers/count")
async def get_customer_count(db: Session = Depends(get_db)):
    """Get total customer count"""
    try:
        result = db.execute(text("SELECT COUNT(*) FROM customers_data"))
        count = result.scalar()
        return {"count": count}
    except Exception as e:
        return {"count": 0, "error": str(e)}


@router.get("/interactions/count")
async def get_interaction_count(db: Session = Depends(get_db)):
    """Get total interaction count"""
    try:
        result = db.execute(text("SELECT COUNT(*) FROM interactions_data"))
        count = result.scalar()
        return {"count": count}
    except Exception as e:
        return {"count": 0, "error": str(e)}


@router.get("/customers/explore")
async def explore_customers(
    gender: Optional[str] = Query(None, description="Filter by gender"),
    contract: Optional[str] = Query(None, description="Filter by contract type"),
    churn: Optional[str] = Query(None, description="Filter by churn status"),
    limit: int = Query(100, description="Maximum number of customers to return"),
    db: Session = Depends(get_db)
):
    """Explore customers with optional filters"""
    try:
        query = "SELECT * FROM customers_data WHERE 1=1"
        params = {}
        
        if gender:
            query += " AND gender = :gender"
            params['gender'] = gender
            
        if contract:
            query += " AND contract = :contract"
            params['contract'] = contract
            
        if churn:
            query += " AND churn = :churn"
            params['churn'] = churn == 'true'
            
        query += " LIMIT :limit"
        params['limit'] = limit
        
        result = db.execute(text(query), params)
        customers = [dict(row._mapping) for row in result]
        
        return {"customers": customers, "total": len(customers)}
        
    except Exception as e:
        return {"customers": [], "error": str(e)}


@router.get("/customers/export")
async def export_customers(
    gender: Optional[str] = Query(None, description="Filter by gender"),
    contract: Optional[str] = Query(None, description="Filter by contract type"),
    churn: Optional[str] = Query(None, description="Filter by churn status"),
    db: Session = Depends(get_db)
):
    """Export filtered customers to CSV"""
    try:
        query = "SELECT * FROM customers_data WHERE 1=1"
        params = {}
        
        if gender:
            query += " AND gender = :gender"
            params['gender'] = gender
            
        if contract:
            query += " AND contract = :contract"
            params['contract'] = contract
            
        if churn:
            query += " AND churn = :churn"
            params['churn'] = churn == 'true'
        
        result = db.execute(text(query), params)
        customers = [dict(row._mapping) for row in result]
        
        # Convert to CSV
        import io
        import csv
        
        output = io.StringIO()
        if customers:
            writer = csv.DictWriter(output, fieldnames=customers[0].keys())
            writer.writeheader()
            writer.writerows(customers)
        
        from fastapi.responses import StreamingResponse
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=customers.csv"}
        )
        
    except Exception as e:
        return {"error": str(e)}


@router.post("/structured/upload")
async def upload_structured(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    rows = 0
    for f in files:
        df = pd.read_csv(f.file)
        rows += len(df)
    return {"status": "ok", "files": len(files), "rows": rows}


@router.post("/unstructured/upload")
async def upload_unstructured(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    return {"status": "ok", "files": len(files)}


@router.post("/audio/transcripts")
async def upload_audio_transcripts(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return {"status": "ok", "transcript_file": file.filename}


@router.get("/normalize")
async def normalize_data(db: Session = Depends(get_db)):
    return {"status": "ok", "message": "Normalization queued"}


@router.post("/documents/csv")
async def ingest_csv(file: UploadFile = File(...), text_column: str = "text", title_column: str | None = None, customer_id_column: str | None = None, source: str | None = None, db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    if text_column not in df.columns:
        return {"status": "error", "message": f"Column '{text_column}' not found"}

    model = get_model()
    texts: List[str] = df[text_column].astype(str).tolist()
    embeddings = model.encode(texts, normalize_embeddings=True)

    items = []
    for i, text in enumerate(texts):
        title = str(df[title_column].iloc[i]) if title_column and title_column in df.columns else None
        customer_id = str(df[customer_id_column].iloc[i]) if customer_id_column and customer_id_column in df.columns else None
        doc = Document(
            customer_id=customer_id,
            source=source,
            title=title,
            text=text,
            embedding=embeddings[i].tolist(),
        )
        db.add(doc)
        items.append(doc)
    db.commit()
    return {"status": "ok", "inserted": len(items)}
