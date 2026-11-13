import urllib.request
import json

base_url = "http://127.0.0.1:8000"

print("--- Testing SpaceMed Backend & Frontend ---")

# 1. GET /
with urllib.request.urlopen(f"{base_url}/") as res:
    assert res.status == 200
    html = res.read().decode("utf-8")
    assert "ORBITALIS" in html
    assert "missionScrollTrack" in html
    assert "missionScrollProgress" in html
    assert "hudBackToTop" in html
    assert "spacemed-condition-checker" in html
    assert "condition-period-select" in html
    print("[PASS] GET / serves updated frontend with interactive scrolling and condition checker")

# 2. POST /check-health
data = json.dumps({"heart_rate": 78, "spo2": 97, "temperature": 36.6, "systolic": 120, "diastolic": 80}).encode("utf-8")
req = urllib.request.Request(f"{base_url}/check-health", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as res:
    assert res.status == 200
    res_data = json.loads(res.read().decode("utf-8"))
    assert "status" in res_data
    print(f"[PASS] POST /check-health returned status={res_data['status']}")

# 3. POST /api/health/analyze
data = json.dumps({
    "heart_rate": 82, "spo2": 96, "temperature": 36.9, "systolic": 125, "diastolic": 82,
    "radiation_msv": 45.0, "microgravity_days": 180, "sleep_hours": 6.5, "co2_level_mmhg": 2.8
}).encode("utf-8")
req = urllib.request.Request(f"{base_url}/api/health/analyze", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as res:
    assert res.status == 200
    res_data = json.loads(res.read().decode("utf-8"))
    assert "risk_score" in res_data
    assert "risk_level" in res_data
    print(f"[PASS] POST /api/health/analyze returned risk_score={res_data['risk_score']} risk_level={res_data['risk_level']}")

# 4. GET /api/alerts
with urllib.request.urlopen(f"{base_url}/api/alerts") as res:
    assert res.status == 200
    alerts = json.loads(res.read().decode("utf-8"))
    assert isinstance(alerts, list)
    print(f"[PASS] GET /api/alerts returned {len(alerts)} alerts")

# 5. GET /api/environment
with urllib.request.urlopen(f"{base_url}/api/environment") as res:
    assert res.status == 200
    env = json.loads(res.read().decode("utf-8"))
    assert "radiation_cumulative_msv" in env
    print(f"[PASS] GET /api/environment returned radiation={env['radiation_cumulative_msv']} mSv")

# 6. GET /api/astronauts
with urllib.request.urlopen(f"{base_url}/api/astronauts") as res:
    assert res.status == 200
    crew = json.loads(res.read().decode("utf-8"))
    assert len(crew) >= 4
    print(f"[PASS] GET /api/astronauts returned {len(crew)} crew members")

# 7. POST /api/demo/start
data = json.dumps({"scenario": "alert"}).encode("utf-8")
req = urllib.request.Request(f"{base_url}/api/demo/start", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as res:
    assert res.status == 200
    scenario_res = json.loads(res.read().decode("utf-8"))
    assert scenario_res.get("scenario") == "alert"
    print(f"[PASS] POST /api/demo/start returned scenario={scenario_res['scenario']}")

# 8. GET /api/devices (Digital Devices & AI Registry)
with urllib.request.urlopen(f"{base_url}/api/devices") as res:
    assert res.status == 200
    devices = json.loads(res.read().decode("utf-8"))
    assert len(devices) >= 4
    assert any(d["id"] == "DEV-ASTROSKIN-01" for d in devices)
    assert any("AI" in d["id"] for d in devices)
    print(f"[PASS] GET /api/devices returned {len(devices)} connected digital devices and AI feeds")

# 9. GET /api/telemetry/stream (Live Sensor Telemetry Stream)
with urllib.request.urlopen(f"{base_url}/api/telemetry/stream") as res:
    assert res.status == 200
    pkt = json.loads(res.read().decode("utf-8"))
    assert "heart_rate" in pkt
    assert "spo2" in pkt
    assert "packet_id" in pkt
    print(f"[PASS] GET /api/telemetry/stream generated live frame: HR={pkt['heart_rate']} bpm, SpO2={pkt['spo2']}%")

# 10. POST /api/telemetry/ingest (Direct Digital & AI Ingestion)
digital_payload = json.dumps({
    "device_id": "TEST-AI-SENSOR-01",
    "source_name": "Autonomous Bio-AI Copilot",
    "source_type": "ai",
    "astronaut_id": "ASTRO-001",
    "heart_rate": 74.2,
    "spo2": 98.6,
    "temperature": 36.8,
    "systolic": 119,
    "diastolic": 77,
    "respiration": 15,
    "hrv": 67,
    "notes": "Verified automated digital ingestion"
}).encode("utf-8")
req = urllib.request.Request(f"{base_url}/api/telemetry/ingest", data=digital_payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as res:
    assert res.status == 200
    ingest_res = json.loads(res.read().decode("utf-8"))
    assert ingest_res.get("status") == "INGESTED"
    assert ingest_res.get("clinical_evaluation") == "NOMINAL"
    print(f"[PASS] POST /api/telemetry/ingest successfully ingested digital frame from AI: packet_id={ingest_res['packet_id']}")

# 11. POST /api/telemetry/batch (File Batch Import)
batch_payload = json.dumps({
    "records": [
        {"timestamp": "Day 45 08:00", "heart_rate": 70, "spo2": 99, "temperature": 36.7, "systolic": 118, "diastolic": 76},
        {"timestamp": "Day 45 12:00", "heart_rate": 74, "spo2": 98, "temperature": 36.8, "systolic": 120, "diastolic": 78}
    ]
}).encode("utf-8")
req = urllib.request.Request(f"{base_url}/api/telemetry/batch", data=batch_payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as res:
    assert res.status == 200
    batch_res = json.loads(res.read().decode("utf-8"))
    assert batch_res.get("ingested_count") == 2
    print(f"[PASS] POST /api/telemetry/batch successfully imported {batch_res['ingested_count']} digital records")

print("\n--- ALL 11 TEST SUITES PASSED WITH ZERO ERRORS ---")
