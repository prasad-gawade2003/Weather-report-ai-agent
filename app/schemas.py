from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentStepTrace(BaseModel):
    step_type: str = Field(..., description="thought, tool_call, tool_result, rag_retrieval, summary")
    title: str
    detail: str
    data: Optional[Dict[str, Any]] = None
    timestamp_ms: Optional[float] = None

class RAGSource(BaseModel):
    id: str
    title: str
    category: str
    snippet: str
    score: float

class DailyForecastItem(BaseModel):
    date: str
    max_temp: float
    min_temp: float
    weather_code: int
    condition: str
    icon: str
    precipitation_prob: Optional[int] = 0

class WeatherSnapshot(BaseModel):
    city: str
    country: Optional[str] = ""
    temperature: float
    apparent_temperature: float
    humidity: int
    wind_speed: float
    weather_code: int
    condition: str
    icon: str
    severity: str
    uv_index: Optional[float] = None
    aqi_us: Optional[int] = None
    pm2_5: Optional[float] = None
    forecast: Optional[List[DailyForecastItem]] = []

class ChatRequest(BaseModel):
    message: str = Field(..., example="what is todays weather")
    city: Optional[str] = None
    user_location: Optional[str] = Field(None, description="Auto-detected or user configured location (e.g. 'Mumbai, India')")
    user_timezone: Optional[str] = Field("Asia/Kolkata", description="Client timezone (e.g. 'Asia/Kolkata')")
    client_timestamp: Optional[str] = None
    temperature_unit: Optional[str] = "celsius"
    llm_provider: Optional[str] = None  # gemini, openai, offline, auto
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    query: str
    response: str
    city_detected: Optional[str] = None
    user_location_used: Optional[str] = None
    weather: Optional[WeatherSnapshot] = None
    rag_sources: List[RAGSource] = []
    agent_traces: List[AgentStepTrace] = []
    model_used: str

class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 4
    category: Optional[str] = None

class RAGDocumentItem(BaseModel):
    id: str
    title: str
    category: str
    tags: List[str]
    content: str

class MCPToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class MCPToolCallResponse(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    success: bool
    result: Any
    error: Optional[str] = None
