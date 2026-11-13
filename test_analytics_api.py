import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def request_json(path, method="GET", payload=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def main():
    print("=== Testing SpaceMed Health Analytics APIs ===")

    # 1. Test Static files
    for fname in ["/chart.umd.min.js", "/jspdf.umd.min.js", "/index.html"]:
        req = urllib.request.Request(f"{BASE_URL}{fname}")
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            print(f"[OK] Static file {fname}: {resp.status} (Size: {len(content)} bytes)")

    # 2. Test GET /api/astronauts
    status, data = request_json("/api/astronauts")
    assert status == 200, f"Expected 200, got {status}"
    astros = data if isinstance(data, list) else data.get("astronauts", [])
    assert len(astros) == 4, f"Expected 4 astronauts, got {len(astros)}"
    print(f"[OK] GET /api/astronauts returned {len(astros)} astronauts: {[a['id'] for a in astros]}")

    # 3. Test GET /api/astronauts/ASTRO-001
    status, data = request_json("/api/astronauts/ASTRO-001")
    assert status == 200, f"Expected 200, got {status}"
    astro = data.get("astronaut") if isinstance(data, dict) and "astronaut" in data else data
    assert astro["id"] == "ASTRO-001" and astro["name"] == "Mark Vance"
    print(f"[OK] GET /api/astronauts/ASTRO-001: {astro['name']} ({astro['role']})")

    # 4. Test GET /api/records?astronaut_id=ASTRO-001&range=30d
    status, data = request_json("/api/records?astronaut_id=ASTRO-001&range=30d")
    assert status == 200, f"Expected 200, got {status}"
    records = data.get("records", [])
    averages = data.get("averages", {})
    assert len(records) > 0, "Expected records for ASTRO-001"
    print(f"[OK] GET /api/records?astronaut_id=ASTRO-001: {len(records)} records, avg HR: {averages.get('heart_rate') or averages.get('heart_rate_bpm')}")

    # 5. Test POST /api/records (Create)
    new_rec = {
        "astronaut_id": "ASTRO-001",
        "recorded_at": "2026-11-14 12:00:00",
        "source_type": "manual",
        "source_name": "Test Suite Verifier",
        "heart_rate_bpm": 74.0,
        "hrv_rmssd": 65.0,
        "spo2_percent": 98.8,
        "body_temperature_c": 36.7,
        "blood_pressure_sys": 118,
        "blood_pressure_dia": 76,
        "respiration_rate": 15.0,
        "sleep_total_hours": 7.8,
        "sleep_deep_hours": 1.9,
        "sleep_rem_hours": 1.7,
        "sleep_quality_score": 89.0,
        "sleep_efficiency_percent": 92.0,
        "cognitive_performance_score": 94.0,
        "reaction_time_ms": 235.0,
        "stress_level": 2.5,
        "mood_assessment": 8.5,
        "bone_density_tscore": -0.30,
        "muscle_strength_index": 80.0,
        "exercise_duration_min": 50.0,
        "fatigue_score": 2.5,
        "energy_level": 8.0,
        "water_intake_liters": 2.8,
        "notes": "Automated verification test record"
    }
    status, data = request_json("/api/records", method="POST", payload=new_rec)
    assert status == 201, f"Expected 201 Created, got {status}: {data}"
    created_id = data.get("id")
    print(f"[OK] POST /api/records: Created record ID #{created_id}")

    # 6. Test GET /api/records/<id>
    status, data = request_json(f"/api/records/{created_id}")
    assert status == 200, f"Expected 200, got {status}"
    rec = data.get("record") if isinstance(data, dict) and "record" in data else data
    assert rec["heart_rate"] == 74.0 or rec.get("heart_rate_bpm") == 74.0
    print(f"[OK] GET /api/records/{created_id}: Fetched successfully")

    # 7. Test PUT /api/records/<id> (Update)
    update_payload = dict(new_rec)
    update_payload["heart_rate_bpm"] = 82.5
    update_payload["heart_rate"] = 82.5
    update_payload["notes"] = "Updated via PUT"
    status, data = request_json(f"/api/records/{created_id}", method="PUT", payload=update_payload)
    assert status == 200, f"Expected 200, got {status}"

    status, data = request_json(f"/api/records/{created_id}")
    rec = data.get("record") if isinstance(data, dict) and "record" in data else data
    assert rec.get("heart_rate") == 82.5 or rec.get("heart_rate_bpm") == 82.5
    print(f"[OK] PUT /api/records/{created_id}: Updated HR to 82.5 bpm")

    # 8. Test DELETE /api/records/<id>
    status, data = request_json(f"/api/records/{created_id}", method="DELETE")
    assert status == 200, f"Expected 200, got {status}"
    status, data = request_json(f"/api/records/{created_id}")
    assert status == 404, f"Expected 404 after deletion, got {status}"
    print(f"[OK] DELETE /api/records/{created_id}: Deleted and verified 404")

    # 9. Test POST /api/simulate-variation
    sim_payload = {
        "astronaut_id": "ASTRO-001",
        "sleep_total_hours": 3.5,     # Severe deprivation
        "heart_rate_bpm": 115.0,     # Tachycardia
        "spo2_percent": 91.0,        # Hypoxia
        "stress_level": 8.5,         # Severe stress
        "exercise_duration_min": 10.0,
        "fatigue_score": 8.0         # Severe fatigue
    }
    status, sim_data = request_json("/api/simulate-variation", method="POST", payload=sim_payload)
    assert status == 200, f"Expected 200, got {status}"
    assert sim_data["projected_risk_score"] > 60, f"Expected high risk, got {sim_data['projected_risk_score']}"
    assert len(sim_data["alerts_triggered"]) >= 3, f"Expected multiple alerts, got {sim_data['alerts_triggered']}"
    assert len(sim_data["comparison_trajectory"]) > 0, "Expected comparison trajectory points"
    print(f"[OK] POST /api/simulate-variation: Risk Score {sim_data['projected_risk_score']} ({sim_data['risk_level']}), Alerts: {sim_data['alerts_triggered']}")

    print("\n🎉 ALL BACKEND APIS AND DATA FLOWS FULLY VERIFIED WITHOUT ERRORS!")

if __name__ == "__main__":
    main()
