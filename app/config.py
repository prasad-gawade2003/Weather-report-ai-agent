import os
from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    APP_NAME: str = "WeatherAI - Intelligent Weather Agent"
    APP_VERSION: str = "1.0.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "auto") # auto, gemini, openai, offline
    
    # External APIs (Open-Meteo is free & keyless)
    GEOCODING_API_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_API_URL: str = "https://api.open-meteo.com/v1/forecast"
    AIR_QUALITY_API_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# WMO Weather Interpretation Codes (WW) mapping
WMO_WEATHER_CODES: Dict[int, Dict[str, Any]] = {
    0: {"description": "Clear sky", "icon": "☀️", "category": "clear", "severity": "normal"},
    1: {"description": "Mainly clear", "icon": "🌤️", "category": "clear", "severity": "normal"},
    2: {"description": "Partly cloudy", "icon": "⛅", "category": "cloudy", "severity": "normal"},
    3: {"description": "Overcast", "icon": "☁️", "category": "cloudy", "severity": "normal"},
    45: {"description": "Foggy", "icon": "🌫️", "category": "fog", "severity": "advisory"},
    48: {"description": "Depositing rime fog", "icon": "🌫️", "category": "fog", "severity": "advisory"},
    51: {"description": "Light drizzle", "icon": "🌦️", "category": "rain", "severity": "normal"},
    53: {"description": "Moderate drizzle", "icon": "🌧️", "category": "rain", "severity": "normal"},
    55: {"description": "Dense drizzle", "icon": "🌧️", "category": "rain", "severity": "advisory"},
    61: {"description": "Slight rain", "icon": "🌦️", "category": "rain", "severity": "normal"},
    63: {"description": "Moderate rain", "icon": "🌧️", "category": "rain", "severity": "normal"},
    65: {"description": "Heavy rain", "icon": "🌧️⚡", "category": "rain", "severity": "warning"},
    71: {"description": "Slight snow fall", "icon": "🌨️", "category": "snow", "severity": "advisory"},
    73: {"description": "Moderate snow fall", "icon": "🌨️❄️", "category": "snow", "severity": "warning"},
    75: {"description": "Heavy snow fall", "icon": "❄️🚨", "category": "snow", "severity": "danger"},
    77: {"description": "Snow grains", "icon": "🌨️", "category": "snow", "severity": "advisory"},
    80: {"description": "Slight rain showers", "icon": "🌦️", "category": "rain", "severity": "normal"},
    81: {"description": "Moderate rain showers", "icon": "🌧️", "category": "rain", "severity": "normal"},
    82: {"description": "Violent rain showers", "icon": "⛈️🚨", "category": "rain", "severity": "danger"},
    85: {"description": "Slight snow showers", "icon": "🌨️", "category": "snow", "severity": "advisory"},
    86: {"description": "Heavy snow showers", "icon": "❄️🚨", "category": "snow", "severity": "danger"},
    95: {"description": "Thunderstorm", "icon": "⛈️", "category": "storm", "severity": "warning"},
    96: {"description": "Thunderstorm with slight hail", "icon": "⛈️🧊", "category": "storm", "severity": "danger"},
    99: {"description": "Thunderstorm with heavy hail", "icon": "⛈️🧊🚨", "category": "storm", "severity": "critical"}
}

def get_weather_code_info(code: int) -> Dict[str, Any]:
    return WMO_WEATHER_CODES.get(code, {
        "description": "Variable weather",
        "icon": "🌤️",
        "category": "variable",
        "severity": "normal"
    })
