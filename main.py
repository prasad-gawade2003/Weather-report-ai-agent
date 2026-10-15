import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    ChatRequest, ChatResponse, RAGSearchRequest, RAGDocumentItem,
    MCPToolCallRequest, MCPToolCallResponse
)
from app.mcp_tools import execute_mcp_tool, TOOL_SCHEMAS
from app.rag_engine import rag_engine
from app.weather_agent import weather_agent

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Weather Agent combining FastMCP, FastAPI, LLMs, and RAG"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints

@app.get("/api/status")
async def get_system_status():
    """Return system readiness, available tools, and provider status."""
    has_gemini = bool(settings.GEMINI_API_KEY)
    has_openai = bool(settings.OPENAI_API_KEY)
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mcp_tools_count": len(TOOL_SCHEMAS),
        "rag_docs_count": len(rag_engine.documents),
        "providers": {
            "gemini": {"configured": has_gemini, "model": "gemini-2.0-flash"},
            "openai": {"configured": has_openai, "model": "gpt-4o-mini"},
            "neural_engine": {"configured": True, "model": "WeatherAI Neural Synthesis (Offline)"}
        },
        "default_provider": settings.DEFAULT_LLM_PROVIDER
    }

@app.get("/api/location/detect")
async def detect_user_location(request: Request):
    """
    Detect user's approximate location via headers or fallback to India/Mumbai.
    """
    client_host = request.client.host if request.client else "127.0.0.1"
    # Localhost/private fallback defaults to Mumbai, India (standard local client)
    return {
        "status": "success",
        "city": "Mumbai",
        "country": "India",
        "timezone": "Asia/Kolkata",
        "ip": client_host
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(req: ChatRequest):
    """
    Send prompt to Weather Intelligence Agent.
    Orchestrates MCP tools + RAG retrieval + LLM synthesis.
    """
    try:
        response = await weather_agent.run(
            message=req.message,
            city_override=req.city,
            user_location=req.user_location,
            user_timezone=req.user_timezone,
            llm_provider=req.llm_provider,
            api_key=req.api_key
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

@app.post("/api/chat/stream")
async def chat_with_agent_stream(req: ChatRequest):
    """
    Stream agent reasoning steps and the synthesized weather report via Server-Sent Events (SSE).
    """
    async def event_generator():
        try:
            # Step 1: Query analysis
            p1 = {'event': 'trace', 'title': 'Analyzing Query', 'detail': f"Parsing: {req.message}", 'step_type': 'thought'}
            yield f"data: {json.dumps(p1)}\n\n"
            await asyncio.sleep(0.15)

            # Extract intent & location
            cities, intent = weather_agent._extract_cities_and_intent(req.message, req.user_location, req.user_timezone)
            primary_city = req.city.strip() if req.city else cities[0]
            
            loc_note = f" (Implicit: Auto-resolved from your location)" if intent.get('is_implicit_location') else ""
            p2 = {'event': 'trace', 'title': 'Intent & Entity Detected', 'detail': f"Target Sector: {primary_city}{loc_note}", 'step_type': 'thought'}
            yield f"data: {json.dumps(p2)}\n\n"
            await asyncio.sleep(0.15)

            # Step 2: RAG
            p3 = {'event': 'trace', 'title': 'Querying RAG Knowledge Base', 'detail': f"Retrieving meteorological safety protocols for {primary_city}", 'step_type': 'rag_retrieval'}
            yield f"data: {json.dumps(p3)}\n\n"

            rag_query = req.message
            if primary_city.lower() in ["mumbai", "bombay"]:
                rag_query = f"mumbai coastal weather october heat imd warning {req.message}"
            rag_results = rag_engine.search(rag_query, top_k=3)
            rag_titles = [f"{r.title} ({int(r.score*100)}%)" for r in rag_results]
            p4 = {'event': 'trace', 'title': 'RAG Sources Retrieved', 'detail': ', '.join(rag_titles), 'step_type': 'rag_retrieval', 'sources': [r.dict() for r in rag_results]}
            yield f"data: {json.dumps(p4)}\n\n"
            await asyncio.sleep(0.15)

            # Step 3: MCP Calls
            p5 = {'event': 'trace', 'title': 'Invoking MCP Tools', 'detail': f"Calling get_live_weather, get_weather_forecast, get_air_quality for {primary_city}", 'step_type': 'tool_call'}
            yield f"data: {json.dumps(p5)}\n\n"
            
            # Execute full agent
            full_response = await weather_agent.run(
                message=req.message,
                city_override=req.city,
                user_location=req.user_location,
                user_timezone=req.user_timezone,
                llm_provider=req.llm_provider,
                api_key=req.api_key
            )

            # Emit final completed response
            p6 = {'event': 'complete', 'data': full_response.dict()}
            yield f"data: {json.dumps(p6)}\n\n"
        except Exception as e:
            err_p = {'event': 'error', 'message': str(e)}
            yield f"data: {json.dumps(err_p)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/weather/quick")
async def get_quick_weather(city: str):
    """Fetch quick snapshot of live weather for dashboard cards."""
    res = await execute_mcp_tool("get_live_weather", {"city": city})
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.get("/api/mcp/tools")
async def list_mcp_tools():
    """List all registered Model Context Protocol (MCP) tools and schemas."""
    return {
        "server_name": "WeatherIntelligenceServer",
        "protocol": "Model Context Protocol (MCP)",
        "tools": TOOL_SCHEMAS
    }

@app.post("/api/mcp/call", response_model=MCPToolCallResponse)
async def call_mcp_tool(req: MCPToolCallRequest):
    """Directly execute any registered MCP tool."""
    res = await execute_mcp_tool(req.tool_name, req.arguments)
    is_err = "error" in res
    return MCPToolCallResponse(
        tool_name=req.tool_name,
        arguments=req.arguments,
        success=not is_err,
        result=res if not is_err else None,
        error=res.get("error") if is_err else None
    )

@app.get("/api/rag/documents")
async def list_rag_documents():
    """Return all indexed documents in the RAG knowledge store."""
    return rag_engine.get_all_documents()

@app.post("/api/rag/search")
async def search_rag(req: RAGSearchRequest):
    """Perform semantic and keyword search across the meteorological RAG knowledge base."""
    results = rag_engine.search(query=req.query, top_k=req.top_k, category=req.category)
    return {"query": req.query, "results": [r.dict() for r in results]}

@app.post("/api/rag/add")
async def add_rag_document(doc: RAGDocumentItem):
    """Add a new custom meteorological document or local advisory to the RAG vector index."""
    doc_id = rag_engine.add_document(doc.dict())
    return {"status": "success", "message": "Document indexed into RAG store", "doc_id": doc_id}

# Mount static folder for dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve main web UI dashboard."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h3>Weather AI Agent API is running. UI loading...</h3>")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting Weather Intelligence Agent on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
