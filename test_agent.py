"""
Automated Test Suite for WeatherAI Agent
Tests FastMCP Tools, RAG Vector Search, and Multi-Step Weather Agent Orchestration.
"""
import sys
import asyncio
from app.mcp_tools import execute_mcp_tool, TOOL_SCHEMAS
from app.rag_engine import rag_engine
from app.weather_agent import weather_agent

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test_all():
    print("=" * 60)
    print("🧪 RUNNING WEATHER-AI AGENT VALIDATION SUITE")
    print("=" * 60)

    # 1. Test MCP Tools Schema
    print("\n[TEST 1] Validating Registered MCP Tool Schemas...")
    assert len(TOOL_SCHEMAS) >= 5, f"Expected at least 5 MCP tools, got {len(TOOL_SCHEMAS)}"
    tool_names = [t["name"] for t in TOOL_SCHEMAS]
    print(f"  ✓ Registered MCP Tools ({len(tool_names)}): {', '.join(tool_names)}")

    # 2. Test Live Weather Tool
    print("\n[TEST 2] Testing MCP Tool: get_live_weather('Zurich')...")
    w = await execute_mcp_tool("get_live_weather", {"city": "Zurich"})
    assert "error" not in w, f"get_live_weather returned error: {w.get('error')}"
    assert "temperature" in w, "Expected 'temperature' in result"
    print(f"  ✓ Zurich Weather: {w['temperature']}°C, {w['condition']} ({w['icon']}), Wind: {w['wind_speed']} km/h")

    # 3. Test Air Quality Tool
    print("\n[TEST 3] Testing MCP Tool: get_air_quality('Tokyo')...")
    air = await execute_mcp_tool("get_air_quality", {"city": "Tokyo"})
    assert "error" not in air, f"get_air_quality returned error: {air.get('error')}"
    print(f"  ✓ Tokyo AQI: {air.get('us_aqi')}, UV: {air.get('uv_index')} ({air.get('uv_category')}), Status: {air.get('health_level')}")

    # 4. Test Weather Comparison Tool
    print("\n[TEST 4] Testing MCP Tool: compare_weather('Paris', 'Dubai')...")
    comp = await execute_mcp_tool("compare_weather", {"city_a": "Paris", "city_b": "Dubai"})
    assert "error" not in comp, f"compare_weather failed: {comp.get('error')}"
    print(f"  ✓ Compared Paris ({comp['city_a'].get('temperature')}°C) vs Dubai ({comp['city_b'].get('temperature')}°C)")

    # 5. Test RAG Vector Search
    print("\n[TEST 5] Testing RAG Semantic Search for 'alpine hypothermia rain gear'...")
    rag_res = rag_engine.search("alpine hypothermia rain gear", top_k=2)
    assert len(rag_res) > 0, "RAG search returned 0 results"
    top_doc = rag_res[0]
    print(f"  ✓ Top RAG Match: '{top_doc.title}' (Score: {top_doc.score})")

    # 6. Test End-to-End Agent Execution
    print("\n[TEST 6] Testing End-to-End Weather Intelligence Agent...")
    prompt = "I'm planning a trail run in Tokyo tomorrow. Check weather and advise on sweat rate and hydration."
    res = await weather_agent.run(prompt)
    assert res.city_detected == "Tokyo", f"Expected city 'Tokyo', got {res.city_detected}"
    assert len(res.agent_traces) > 0, "Expected non-empty reasoning traces"
    assert len(res.rag_sources) > 0, "Expected RAG citations"
    assert len(res.response) > 200, "Expected detailed synthesized report"
    
    print(f"  ✓ Detected City: {res.city_detected}")
    print(f"  ✓ Agent Reasoning Traces: {len(res.agent_traces)} steps recorded")
    print(f"  ✓ Grounded RAG Citations: {len(res.rag_sources)} sources")
    print(f"  ✓ Model Used: {res.model_used}")
    # 7. Test Implicit Location Resolution ("what is todays weather")
    print("\n[TEST 7] Testing Implicit Query: 'what is todays weather' with auto-location 'Mumbai, India'...")
    res_mumbai = await weather_agent.run("what is todays weather", user_location="Mumbai, India", user_timezone="Asia/Kolkata")
    assert res_mumbai.city_detected == "Mumbai", f"Expected 'Mumbai', got {res_mumbai.city_detected}"
    assert res_mumbai.user_location_used == "Mumbai", f"Expected user_location_used 'Mumbai', got {res_mumbai.user_location_used}"
    assert "Mumbai" in res_mumbai.response, "Expected 'Mumbai' in briefing output"
    
    mumbai_sources = [s.title for s in res_mumbai.rag_sources]
    print(f"  ✓ Auto-Resolved City: {res_mumbai.city_detected} (from user_location='Mumbai, India')")
    print(f"  ✓ Grounded Indian RAG Sources: {', '.join(mumbai_sources)}")
    print(f"  ✓ Direct Today's Weather Verdict: {res_mumbai.response.splitlines()[2] if len(res_mumbai.response.splitlines()) > 2 else ''}")

    print("\n" + "=" * 60)
    print("🎉 ALL 7 TESTS PASSED SUCCESSFULLY! ARCHITECTURE FULLY VERIFIED.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all())
