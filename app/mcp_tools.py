import httpx
import asyncio
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
from app.config import settings, get_weather_code_info

# Initialize FastMCP Server
mcp_server = FastMCP(
    "WeatherIntelligenceServer",
    dependencies=["httpx"]
)

# Async HTTP Client with timeout
HTTP_TIMEOUT = httpx.Timeout(10.0, connect=5.0)

GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}

async def geocode_city(city: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Geocode a city name into latitude, longitude, and metadata via Open-Meteo with caching."""
    key = f"{city.strip().lower()}:{country.strip().lower() if country else ''}"
    if key in GEOCODE_CACHE:
        return GEOCODE_CACHE[key]

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        params = {"name": city.strip(), "count": 1, "language": "en", "format": "json"}
        try:
            resp = await client.get(settings.GEOCODING_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results")
            if not results:
                return None
            res = results[0]
            geo_info = {
                "name": res.get("name"),
                "country": res.get("country", ""),
                "country_code": res.get("country_code", ""),
                "latitude": res.get("latitude"),
                "longitude": res.get("longitude"),
                "timezone": res.get("timezone", "UTC"),
                "elevation": res.get("elevation", 0)
            }
            GEOCODE_CACHE[key] = geo_info
            return geo_info
        except Exception as e:
            return None

# ==================== MCP TOOLS ====================

@mcp_server.tool()
async def get_live_weather(city: str, country: str = "") -> Dict[str, Any]:
    """
    Get live, real-time meteorological conditions for any city worldwide.
    Returns temperature, humidity, feels-like, wind speed, weather condition and WMO code.
    """
    geo = await geocode_city(city, country)
    if not geo:
        return {"error": f"City '{city}' could not be located. Please check spelling."}

    params = {
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "timezone": geo["timezone"]
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            resp = await client.get(settings.FORECAST_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            curr = data.get("current", {})
            
            w_code = curr.get("weather_code", 0)
            code_info = get_weather_code_info(w_code)

            return {
                "status": "success",
                "city": geo["name"],
                "country": geo["country"],
                "latitude": geo["latitude"],
                "longitude": geo["longitude"],
                "timezone": geo["timezone"],
                "time": curr.get("time"),
                "temperature": curr.get("temperature_2m"),
                "temperature_unit": "°C",
                "apparent_temperature": curr.get("apparent_temperature"),
                "humidity": curr.get("relative_humidity_2m"),
                "wind_speed": curr.get("wind_speed_10m"),
                "wind_speed_unit": "km/h",
                "precipitation": curr.get("precipitation"),
                "weather_code": w_code,
                "condition": code_info["description"],
                "icon": code_info["icon"],
                "severity": code_info["severity"]
            }
        except Exception as e:
            return {"error": f"Failed to fetch weather for {city}: {str(e)}"}

@mcp_server.tool()
async def get_weather_forecast(city: str, days: int = 5) -> Dict[str, Any]:
    """
    Fetch a multi-day weather forecast (up to 7 days) for a city.
    Includes daily high/low temperatures, precipitation chance, and expected conditions.
    """
    geo = await geocode_city(city)
    if not geo:
        return {"error": f"City '{city}' could not be located."}

    days = max(1, min(days, 7))
    params = {
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
        "forecast_days": days,
        "timezone": geo["timezone"]
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            resp = await client.get(settings.FORECAST_API_URL, params=params)
            resp.raise_for_status()
            daily = resp.json().get("daily", {})
            
            times = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            w_codes = daily.get("weather_code", [])
            precip_probs = daily.get("precipitation_probability_max", [])
            wind_max = daily.get("wind_speed_10m_max", [])

            forecast_list = []
            for i in range(len(times)):
                code = w_codes[i] if i < len(w_codes) else 0
                code_info = get_weather_code_info(code)
                forecast_list.append({
                    "date": times[i],
                    "max_temp": max_temps[i] if i < len(max_temps) else None,
                    "min_temp": min_temps[i] if i < len(min_temps) else None,
                    "precipitation_probability": precip_probs[i] if i < len(precip_probs) else 0,
                    "max_wind_speed": wind_max[i] if i < len(wind_max) else 0,
                    "weather_code": code,
                    "condition": code_info["description"],
                    "icon": code_info["icon"]
                })

            return {
                "status": "success",
                "city": geo["name"],
                "country": geo["country"],
                "days_count": len(forecast_list),
                "forecast": forecast_list
            }
        except Exception as e:
            return {"error": f"Failed to fetch forecast for {city}: {str(e)}"}

@mcp_server.tool()
async def get_air_quality(city: str) -> Dict[str, Any]:
    """
    Fetch live Air Quality Index (AQI), PM2.5, PM10, Ozone, and UV index.
    Provides health impact classification and sensitive group warnings.
    """
    geo = await geocode_city(city)
    if not geo:
        return {"error": f"City '{city}' could not be located."}

    params = {
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "current": "european_aqi,us_aqi,pm10,pm2_5,ozone,uv_index",
        "timezone": geo["timezone"]
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            resp = await client.get(settings.AIR_QUALITY_API_URL, params=params)
            resp.raise_for_status()
            curr = resp.json().get("current", {})
            
            us_aqi = curr.get("us_aqi", 0)
            uv = curr.get("uv_index", 0.0)
            
            # Health interpretation
            if us_aqi <= 50:
                health_level = "Good"
                health_advice = "Air quality is satisfactory with little or no risk."
            elif us_aqi <= 100:
                health_level = "Moderate"
                health_advice = "Air quality is acceptable. Very sensitive individuals may consider reducing prolonged outdoor exertion."
            elif us_aqi <= 150:
                health_level = "Unhealthy for Sensitive Groups"
                health_advice = "Members of sensitive groups (asthma, children, elderly) may experience health effects. General public not likely affected."
            elif us_aqi <= 200:
                health_level = "Unhealthy"
                health_advice = "Everyone may experience health effects. Sensitive groups should avoid outdoor exertion. Consider N95 masks."
            else:
                health_level = "Very Unhealthy / Hazardous"
                health_advice = "Health alert: Serious risk of respiratory impact. Avoid all outdoor activity."

            # UV category
            if uv < 3:
                uv_category = "Low"
            elif uv < 6:
                uv_category = "Moderate"
            elif uv < 8:
                uv_category = "High"
            elif uv < 11:
                uv_category = "Very High"
            else:
                uv_category = "Extreme"

            return {
                "status": "success",
                "city": geo["name"],
                "country": geo["country"],
                "us_aqi": us_aqi,
                "european_aqi": curr.get("european_aqi"),
                "pm2_5": curr.get("pm2_5"),
                "pm10": curr.get("pm10"),
                "ozone": curr.get("ozone"),
                "uv_index": uv,
                "uv_category": uv_category,
                "health_level": health_level,
                "health_advice": health_advice
            }
        except Exception as e:
            return {"error": f"Failed to fetch air quality for {city}: {str(e)}"}

@mcp_server.tool()
async def get_severe_weather_alerts(city: str) -> Dict[str, Any]:
    """
    Evaluate weather conditions against severe thresholds (gale winds, extreme cold/heat, torrential rain, thunderstorms).
    Returns active meteorological safety advisories and risk levels.
    """
    weather = await get_live_weather(city)
    if "error" in weather:
        return weather

    alerts = []
    temp = weather.get("temperature", 20)
    wind = weather.get("wind_speed", 0)
    w_code = weather.get("weather_code", 0)
    precip = weather.get("precipitation", 0)

    # 1. Temperature checks
    if temp >= 38:
        alerts.append({
            "severity": "CRITICAL",
            "type": "Extreme Heat Advisory",
            "message": f"Dangerous heat of {temp}°C detected. Risk of heat exhaustion and heatstroke is elevated."
        })
    elif temp >= 33:
        alerts.append({
            "severity": "WARNING",
            "type": "Heat Advisory",
            "message": f"High temperature of {temp}°C. Hydrate frequently and avoid mid-day sun."
        })
    elif temp <= -10:
        alerts.append({
            "severity": "CRITICAL",
            "type": "Severe Freeze Warning",
            "message": f"Extreme sub-zero cold ({temp}°C). Frostbite risk on exposed skin within 20 minutes."
        })
    elif temp <= 0:
        alerts.append({
            "severity": "ADVISORY",
            "type": "Freezing Condition Advisory",
            "message": f"Freezing temperatures ({temp}°C). Watch for black ice on roadways and sidewalks."
        })

    # 2. Wind checks
    if wind >= 65:
        alerts.append({
            "severity": "CRITICAL",
            "type": "Gale / Storm Wind Warning",
            "message": f"Severe wind gusts at {wind} km/h (Beaufort 8+). High risk of falling branches and flying debris."
        })
    elif wind >= 45:
        alerts.append({
            "severity": "WARNING",
            "type": "Strong Wind Advisory",
            "message": f"High winds of {wind} km/h. Difficult conditions for cycling, high-sided vehicles, and drones."
        })

    # 3. Storm & precipitation checks
    if w_code in [95, 96, 99]:
        alerts.append({
            "severity": "DANGER",
            "type": "Thunderstorm / Hail Alert",
            "message": "Active thunderstorms detected in the area. Seek sturdy indoor shelter immediately."
        })
    elif precip >= 15:
        alerts.append({
            "severity": "WARNING",
            "type": "Torrential Rain Warning",
            "message": f"Heavy precipitation ({precip} mm). Potential for localized flash flooding in low-lying areas."
        })

    return {
        "status": "success",
        "city": weather.get("city"),
        "active_alerts_count": len(alerts),
        "alerts": alerts,
        "is_severe": len([a for a in alerts if a["severity"] in ["CRITICAL", "DANGER", "WARNING"]]) > 0
    }

@mcp_server.tool()
async def compare_weather(city_a: str, city_b: str) -> Dict[str, Any]:
    """
    Compare current weather conditions between two different cities side-by-side.
    """
    res_a, res_b = await asyncio.gather(
        get_live_weather(city_a),
        get_live_weather(city_b)
    )
    return {
        "status": "success",
        "city_a": res_a,
        "city_b": res_b,
        "temperature_difference": (
            res_a.get("temperature", 0) - res_b.get("temperature", 0)
            if "temperature" in res_a and "temperature" in res_b else None
        )
    }

# ==================== TOOL REGISTRY & DISPATCHER ====================

TOOL_MAP = {
    "get_live_weather": get_live_weather,
    "get_weather_forecast": get_weather_forecast,
    "get_air_quality": get_air_quality,
    "get_severe_weather_alerts": get_severe_weather_alerts,
    "compare_weather": compare_weather
}

TOOL_SCHEMAS = [
    {
        "name": "get_live_weather",
        "description": "Fetch real-time current weather metrics (temperature, humidity, feels-like, wind, conditions) for any city worldwide.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Name of the city (e.g. 'Tokyo', 'London', 'New York')"},
                "country": {"type": "string", "description": "Optional country name or 2-letter code"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_weather_forecast",
        "description": "Fetch a multi-day forecast (1 to 7 days) with high/low temperatures and precipitation probability.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Name of the city"},
                "days": {"type": "integer", "description": "Number of days (1-7, default 5)", "default": 5}
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_air_quality",
        "description": "Fetch real-time Air Quality Index (US & European AQI), PM2.5, PM10, and UV index with health advisories.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Name of the city"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_severe_weather_alerts",
        "description": "Evaluate current weather against severe thresholds (gale winds, heat stress, freezing cold, storms).",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Name of the city"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "compare_weather",
        "description": "Compare meteorological conditions between two cities side-by-side.",
        "parameters": {
            "type": "object",
            "properties": {
                "city_a": {"type": "string", "description": "First city name"},
                "city_b": {"type": "string", "description": "Second city name"}
            },
            "required": ["city_a", "city_b"]
        }
    }
]

async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP tool function safely and return result or error."""
    tool_fn = TOOL_MAP.get(tool_name)
    if not tool_fn:
        return {"error": f"Tool '{tool_name}' not registered in Weather MCP Server."}
    try:
        res = await tool_fn(**arguments)
        return res
    except Exception as e:
        return {"error": f"Execution error in MCP tool '{tool_name}': {str(e)}"}
