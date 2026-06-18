from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent
from database import get_schema_info, execute_query

app = FastAPI(
    title="Text-to-SQL Agent API",
    description="Convert natural-language questions into SQL and execute them.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class DirectSQLRequest(BaseModel):
    sql: str


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "text-to-sql-agent"}


@app.get("/schema")
def get_schema():
    """Returns the live database schema as plain text."""
    try:
        schema = get_schema_info()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query(request: QueryRequest):
    """
    Main endpoint: accepts a natural-language question,
    runs the LangChain agent, and returns SQL + results.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_agent(request.question.strip())

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["summary"])

    return result


@app.post("/execute")
def execute_raw_sql(request: DirectSQLRequest):
    """
    Direct SQL execution endpoint (for the 'Edit SQL' feature in the UI).
    Only SELECT statements are permitted.
    """
    try:
        result = execute_query(request.sql)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
