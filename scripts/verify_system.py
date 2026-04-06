import httpx
import pytest
import time

API_URL = "http://localhost:8000"
MCP_URL = "http://localhost:8001"

def test_api_health():
    response = httpx.get(f"{API_URL}/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_mcp_health():
    response = httpx.get(f"{MCP_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_canvas_recovery():
    # This triggers the fallback logic if not already triggered
    response = httpx.get(f"{API_URL}/v1/canvas/day")
    assert response.status_code == 200
    data = response.json()
    assert "tracks" in data
    assert "health" in data["tracks"]
    # Verify readiness is present (fallback default)
    assert data["tracks"]["health"]["readiness"] == 80

def test_modes_integrity():
    # Verify the modes endpoint can handle re-initialization
    response = httpx.get(f"{API_URL}/v1/modes/")
    assert response.status_code == 200
    assert response.json()["active_mode"] == "FOCUS"

def test_location_fallback():
    # Verify office-route returns the demo fallback instead of 404
    response = httpx.get(f"{API_URL}/v1/location/office-route")
    assert response.status_code == 200
    assert "Singapore" in response.json()["origin"]

if __name__ == "__main__":
    # Simple manual run
    print("Running 2026 NEXUS Integration Tests...")
    try:
        test_api_health()
        print("[PASS] API Health")
        test_mcp_health()
        print("[PASS] MCP Health")
        test_canvas_recovery()
        print("[PASS] Canvas Recovery (SQLite Fallback)")
        test_modes_integrity()
        print("[PASS] Modes Integrity")
        test_location_fallback()
        print("[PASS] Location Fallback")
        print("\nALL SYSTEMS FUNCTIONAL. 2026 NEXUS READY FOR DEMO.")
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
