from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json
import os
import time
import random
import db

# Ensure database is initialized at import
db.init_db()

# Location of this Python file
BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "static" / "index.html"

# In-memory alert registry
ALERTS_DATA = [
    {
        "id": "ALT-101",
        "astronaut_id": "ASTRO-001",
        "astronaut_name": "Mark Vance",
        "alert_type": "Hypoxia Risk",
        "severity": "CRITICAL",
        "status": "NEW",
        "timestamp": "2026-11-13 14:22:10 UTC",
        "rationale": "Blood oxygen saturation dropped below threshold (SpO2: 89%). Acute cardiovascular strain detected.",
        "protocol": "Deploy auxiliary cabin O2 mask and verify environmental life support loop (ECLSS)."
    },
    {
        "id": "ALT-102",
        "astronaut_id": "ASTRO-002",
        "astronaut_name": "Sarah Chen",
        "alert_type": "Circadian Sleep Debt",
        "severity": "ELEVATED",
        "status": "UNDER REVIEW",
        "timestamp": "2026-11-13 09:15:40 UTC",
        "rationale": "Consecutive 3-day sleep restriction (average 4.5 hrs/day). Subjective fatigue elevated to 7/10.",
        "protocol": "Implement crew rest schedule extension. Shift lighting spectrum to 460nm blue-depleted."
    },
    {
        "id": "ALT-103",
        "astronaut_id": "ASTRO-004",
        "astronaut_name": "James Wilson",
        "alert_type": "Radiation Exposure Warning",
        "severity": "ADVISORY",
        "status": "RESOLVED",
        "timestamp": "2026-11-12 18:40:00 UTC",
        "rationale": "Minor solar energetic particle (SEP) flux enhancement detected outside habitat module.",
        "protocol": "Astronaut in storm shelter. Dose rate nominal within shielding threshold."
    }
]

# In-memory crew members
ASTRONAUTS_DATA = [
    {
        "id": "ASTRO-001",
        "name": "Mark Vance",
        "role": "Mission Commander",
        "age": 42,
        "agency": "Orbitalis / NASA",
        "mission_day": 45,
        "status": "NOMINAL",
        "heart_rate": 72,
        "spo2": 98,
        "sleep_avg": 7.6,
        "fatigue_score": 3,
        "readiness_score": 94,
        "radiation_dose": 38.2
    },
    {
        "id": "ASTRO-002",
        "name": "Sarah Chen",
        "role": "Flight Engineer",
        "age": 36,
        "agency": "Orbitalis / ESA",
        "mission_day": 45,
        "status": "ELEVATED RISK",
        "heart_rate": 96,
        "spo2": 95,
        "sleep_avg": 5.2,
        "fatigue_score": 7,
        "readiness_score": 71,
        "radiation_dose": 42.1
    },
    {
        "id": "ASTRO-003",
        "name": "Elena Rostova",
        "role": "Science Specialist",
        "age": 39,
        "agency": "Orbitalis / JAXA",
        "mission_day": 45,
        "status": "NOMINAL",
        "heart_rate": 68,
        "spo2": 99,
        "sleep_avg": 7.9,
        "fatigue_score": 2,
        "readiness_score": 96,
        "radiation_dose": 36.8
    },
    {
        "id": "ASTRO-004",
        "name": "James Wilson",
        "role": "Pilot / EVA Specialist",
        "age": 44,
        "agency": "Orbitalis / CSA",
        "mission_day": 45,
        "status": "MONITORING",
        "heart_rate": 82,
        "spo2": 97,
        "sleep_avg": 6.4,
        "fatigue_score": 5,
        "readiness_score": 83,
        "radiation_dose": 45.4
    }
]

ENVIRONMENT_DATA = {
    "mission_day": 45,
    "microgravity_days": 45,
    "radiation_cumulative_msv": 42.8,
    "radiation_rate_usv_hr": 38.5,
    "solar_particle_status": "QUIET (LEVEL 0)",
    "cabin_pressure_kpa": 101.3,
    "cabin_o2_percent": 20.9,
    "cabin_co2_mmhg": 2.6,
    "cabin_temp_c": 21.6,
    "cabin_humidity_percent": 45.2,
    "geomagnetic_kp": 2.0,
    "timestamp": "2026-11-13 18:30:00 UTC"
}

# In-memory connected digital devices and AI feeds registry
CONNECTED_DEVICES = [
    {
        "id": "DEV-ASTROSKIN-01",
        "name": "NASA AstroSkin Bio-Harness",
        "category": "Wearable Smart Garment",
        "status": "ONLINE",
        "protocol": "BLE 5.2 / UHF SpaceLink",
        "battery": 88,
        "sample_rate": "250 Hz",
        "channels": ["3-Lead ECG", "Dual Respiration Bands", "Skin Temperature", "3-Axis Accelerometer"],
        "last_sync": "Just now",
        "signal_strength_dbm": -42
    },
    {
        "id": "DEV-PULSE-OX-04",
        "name": "Nonin Medical Continuous SpO2",
        "category": "Pulse Oximeter & Plethysmograph",
        "status": "ONLINE",
        "protocol": "Medical Bluetooth (IEEE 11073)",
        "battery": 94,
        "sample_rate": "75 Hz",
        "channels": ["Arterial Oxygen (SpO2)", "Pulse Rate", "Perfusion Index"],
        "last_sync": "1s ago",
        "signal_strength_dbm": -38
    },
    {
        "id": "DEV-RING-CIRCAD-02",
        "name": "Orbital Biomarker Smart Ring",
        "category": "Autonomous Circadian & HRV Tracker",
        "status": "ONLINE",
        "protocol": "NFC / Autonomous Cloud Sync",
        "battery": 76,
        "sample_rate": "10 Hz",
        "channels": ["HRV (rMSSD)", "Core Temp Gradient", "Sleep Architecture"],
        "last_sync": "12s ago",
        "signal_strength_dbm": -50
    },
    {
        "id": "DEV-ECLSS-CABIN-09",
        "name": "Habitat ECLSS Avionics Bus",
        "category": "Environmental & Life Support Systems",
        "status": "ONLINE",
        "protocol": "MIL-STD-1553B Avionics",
        "battery": 100,
        "sample_rate": "1 Hz",
        "channels": ["Cabin ppCO2", "ppO2", "Cabin Pressure", "Cosmic Dosimetry"],
        "last_sync": "Real-time",
        "signal_strength_dbm": -20
    },
    {
        "id": "AI-EDGE-DIAGNOSTIC-01",
        "name": "SpaceMed Onboard Bio-AI Copilot",
        "category": "Edge AI Inference Model",
        "status": "ACTIVE_INFERENCE",
        "protocol": "Neural Processing Unit (NPU)",
        "battery": 100,
        "sample_rate": "Dynamic Inference",
        "channels": ["Multivariable Risk Engine", "Synthetic Biomarker Projection", "Microgravity Adaptation Horizon"],
        "last_sync": "Continuous",
        "latency_ms": 12
    }
]

# Latest live digital telemetry frame
LATEST_TELEMETRY = {
    "packet_id": "PKT-INIT-001",
    "device_id": "DEV-ASTROSKIN-01",
    "source_name": "NASA AstroSkin Bio-Harness",
    "source_type": "digital_device",
    "timestamp": "2026-11-14 00:45:00 UTC",
    "astronaut_id": "ASTRO-001",
    "heart_rate": 72.0,
    "spo2": 98.4,
    "temperature": 36.8,
    "systolic": 118,
    "diastolic": 76,
    "respiration": 15,
    "hrv": 68,
    "status": "NOMINAL",
    "problems": [],
    "signal_quality": "OPTIMAL (99.2%)",
    "notes": "Autonomous telemetry stream active"
}

# Rolling audit trail of ingested digital packets
TELEMETRY_LOG = [
    {
        "packet_id": "PKT-INIT-000",
        "device_id": "DEV-ASTROSKIN-01",
        "source_name": "NASA AstroSkin Bio-Harness",
        "source_type": "digital_device",
        "timestamp": "2026-11-14 00:40:00 UTC",
        "heart_rate": 71.0,
        "spo2": 98.6,
        "temperature": 36.7,
        "systolic": 117,
        "diastolic": 76,
        "respiration": 15,
        "hrv": 70,
        "status": "NOMINAL"
    }
]


class SpaceMedHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        if path == "":
            path = "/"

        if path in ("/", "/index.html"):
            if not HTML_FILE.exists():
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"ERROR: index.html was not found.")
                return

            html = HTML_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(html)
            return

        elif path == "/api/astronauts":
            astros = db.get_astronauts()
            self._send_json(200, astros if astros else ASTRONAUTS_DATA)
            return

        elif path.startswith("/api/astronauts/"):
            astro_id = path.split("/")[-1]
            astro = db.get_astronaut_by_id(astro_id)
            if not astro:
                self._send_error(404, "Astronaut not found")
                return
            stats = db.get_stats_summary(astro_id)
            alerts = db.get_alerts_for_astronaut(astro_id)
            astro["stats"] = stats
            astro["alerts"] = alerts
            res_payload = {
                **astro,
                "astronaut": dict(astro),
                "stats": stats,
                "alerts": alerts
            }
            self._send_json(200, res_payload)
            return

        elif path == "/api/records":
            parsed_url = urlparse(self.path)
            qs = parse_qs(parsed_url.query)
            astro_id = qs.get("astronaut_id", ["ASTRO-001"])[0]
            range_param = qs.get("range", ["30d"])[0]
            start_date = qs.get("start_date", [None])[0]
            end_date = qs.get("end_date", [None])[0]

            limit = 30
            if range_param == "24h":
                limit = 2
            elif range_param == "7d":
                limit = 7
            elif range_param == "30d":
                limit = 30
            elif range_param == "all":
                limit = 100

            records = db.get_records(astro_id, limit=limit, start_date=start_date, end_date=end_date)
            summary = db.get_stats_summary(astro_id, limit=limit)
            self._send_json(200, {
                "astronaut_id": astro_id,
                "range": range_param,
                "count": len(records),
                "summary": summary,
                "averages": summary.get("averages", {}),
                "records": records
            })
            return

        elif path.startswith("/api/records/"):
            try:
                rec_id = int(path.split("/")[-1])
                rec = db.get_record_by_id(rec_id)
                if not rec:
                    self._send_error(404, "Record not found")
                    return
                self._send_json(200, rec)
            except Exception as e:
                self._send_error(400, "Invalid record ID", str(e))
            return

        elif path == "/api/alerts":
            data = json.dumps(ALERTS_DATA).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
            return

        elif path == "/api/environment":
            data = json.dumps(ENVIRONMENT_DATA).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
            return

        elif path == "/api/devices":
            data = json.dumps(CONNECTED_DEVICES).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
            return

        elif path == "/api/telemetry/latest":
            res = {
                "latest": LATEST_TELEMETRY,
                "recent_packets": TELEMETRY_LOG[-10:] if TELEMETRY_LOG else [LATEST_TELEMETRY]
            }
            data = json.dumps(res).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
            return

        elif path == "/api/telemetry/stream":
            self._handle_telemetry_stream()
            return

        # Check for static file requests
        potential_static = BASE_DIR / "static" / path.lstrip("/")
        if potential_static.exists() and potential_static.is_file():
            content = potential_static.read_bytes()
            mime = "text/plain"
            if path.endswith(".css"):
                mime = "text/css"
            elif path.endswith(".js"):
                mime = "application/javascript"
            elif path.endswith(".json"):
                mime = "application/json"
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(content)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            incoming = json.loads(body) if body else {}
        except Exception as e:
            self._send_error(400, "Invalid JSON payload", str(e))
            return

        # --- ROUTE 1: Existing check-health ---
        if path == "/check-health":
            self._handle_check_health(incoming)

        # --- ROUTE 2: AI Mission Health Intelligence Analyzer ---
        elif path == "/api/health/analyze":
            self._handle_health_analyze(incoming)

        # --- ROUTE 3: Alert Creation ---
        elif path == "/api/alerts":
            self._handle_create_alert(incoming)

        # --- ROUTE 4: Alert Resolution ---
        elif path in ("/api/alerts/resolve", "/api/alerts/acknowledge"):
            self._handle_resolve_alert(incoming)

        # --- ROUTE 5: Demo Scenario Starter ---
        elif path == "/api/demo/start":
            self._handle_demo_start(incoming)

        # --- ROUTE 6: Digital Telemetry Ingestion (Any Device or AI) ---
        elif path == "/api/telemetry/ingest":
            self._handle_telemetry_ingest(incoming)

        # --- ROUTE 7: Batch Telemetry Import (Files & Multi-Day Logs) ---
        elif path == "/api/telemetry/batch":
            self._handle_telemetry_batch(incoming)

        # --- ROUTE 8: Health Records Create (CRUD) ---
        elif path == "/api/records":
            self._handle_create_record(incoming)

        # --- ROUTE 9: Health Variation Simulator ---
        elif path == "/api/simulate-variation":
            self._handle_simulate_variation(incoming)

        # --- ROUTE 10: Cognitive Battery Result Ingestion ---
        elif path == "/api/cognitive/save":
            self._handle_cognitive_save(incoming)

        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        path = self.path.split("?")[0].rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            incoming = json.loads(body) if body else {}
        except Exception as e:
            self._send_error(400, "Invalid JSON payload", str(e))
            return

        if path.startswith("/api/records/"):
            try:
                rec_id = int(path.split("/")[-1])
                success = db.update_record(rec_id, incoming)
                if success:
                    updated = db.get_record_by_id(rec_id)
                    self._send_json(200, {
                        "success": True,
                        "id": rec_id,
                        "record": updated,
                        "message": "Health reading updated successfully in mission database."
                    })
                else:
                    self._send_error(404, "Record not found or update failed")
            except Exception as err:
                self._send_error(400, "Failed to update record", str(err))
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        path = self.path.split("?")[0].rstrip("/")

        if path.startswith("/api/records/"):
            try:
                rec_id = int(path.split("/")[-1])
                success = db.delete_record(rec_id)
                if success:
                    self._send_json(200, {
                        "success": True,
                        "id": rec_id,
                        "message": "Health reading safely deleted from mission database."
                    })
                else:
                    self._send_error(404, "Record not found or delete failed")
            except Exception as err:
                self._send_error(400, "Failed to delete record", str(err))
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, status_code, obj):
        res = json.dumps(obj).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(res)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(res)

    def _send_error(self, status_code, msg, details=""):
        self._send_json(status_code, {"error": msg, "details": details})

    def _handle_check_health(self, incoming):
        try:
            data = {
                "name": incoming.get("name", "Unknown Astronaut"),
                "heart_rate": float(incoming.get("heart_rate", 0)),
                "spo2": float(incoming.get("spo2", 0)),
                "temperature": float(incoming.get("temperature", 0)),
                "systolic": float(incoming.get("systolic", 0)),
                "diastolic": float(incoming.get("diastolic", 0))
            }

            problems = []
            if data["heart_rate"] < 60 or data["heart_rate"] > 100:
                problems.append("Abnormal heart rate")
            if data["spo2"] < 95:
                problems.append("Low blood oxygen")
            if data["temperature"] < 36.1 or data["temperature"] > 37.5:
                problems.append("Abnormal body temperature")
            if data["systolic"] < 90 or data["systolic"] > 129:
                problems.append("Abnormal systolic blood pressure")
            if data["diastolic"] < 60 or data["diastolic"] > 84:
                problems.append("Abnormal diastolic blood pressure")

            if len(problems) == 0:
                status = "NORMAL"
            elif len(problems) <= 2:
                status = "NEEDS MONITORING"
            else:
                status = "MEDICAL ALERT"

            self._send_json(200, {
                "astronaut": data["name"],
                "status": status,
                "problems": problems
            })
        except Exception as err:
            self._send_error(400, "Invalid health data", str(err))

    def _handle_health_analyze(self, incoming):
        """
        Flagship AI-Powered Astronaut Health Risk Prediction Engine
        Multivariable assessment of physiological, circadian, and environmental factors.
        """
        try:
            astronaut_id = incoming.get("astronaut_id", "ASTRO-001")
            hr = float(incoming.get("heart_rate", 72))
            spo2 = float(incoming.get("spo2", 98))
            sleep_hours = float(incoming.get("sleep_hours", 7.5))
            fatigue = float(incoming.get("fatigue_score", 3))
            stress = float(incoming.get("stress_score", 3))
            mission_day = int(incoming.get("mission_day", 45))

            risk_factors = []
            penalty_score = 0

            # 1. Cardiovascular adaptation & strain
            if hr > 115:
                risk_factors.append(f"Significant resting tachycardia ({int(hr)} bpm)")
                penalty_score += 32
            elif hr > 95:
                risk_factors.append(f"Elevated resting heart rate ({int(hr)} bpm)")
                penalty_score += 18
            elif hr < 50:
                risk_factors.append(f"Marked bradycardia ({int(hr)} bpm)")
                penalty_score += 20

            # 2. Oxygenation & Respiratory Status
            if spo2 < 90:
                risk_factors.append(f"Critical arterial hypoxia (SpO2: {spo2}%)")
                penalty_score += 45
            elif spo2 < 95:
                risk_factors.append(f"Suboptimal blood oxygen saturation (SpO2: {spo2}%)")
                penalty_score += 22

            # 3. Circadian Disruption & Sleep Deficit
            if sleep_hours < 4.5:
                risk_factors.append(f"Acute sleep deprivation ({sleep_hours:.1f} hrs/day)")
                penalty_score += 30
            elif sleep_hours < 6.0:
                risk_factors.append(f"Chronic sleep restriction ({sleep_hours:.1f} hrs/day)")
                penalty_score += 15

            # 4. Neurobehavioral Fatigue
            if fatigue >= 8:
                risk_factors.append(f"High self-reported fatigue index ({int(fatigue)}/10)")
                penalty_score += 25
            elif fatigue >= 6:
                risk_factors.append(f"Elevated cumulative fatigue score ({int(fatigue)}/10)")
                penalty_score += 12

            # 5. Operational Stress Load
            if stress >= 8:
                risk_factors.append(f"Elevated operational stress levels ({int(stress)}/10)")
                penalty_score += 18
            elif stress >= 6:
                risk_factors.append(f"Moderate psychological strain ({int(stress)}/10)")
                penalty_score += 8

            # Calculate composite risk index (0 to 100)
            risk_score = min(100, max(5, int(penalty_score)))

            if risk_score >= 65:
                risk_level = "CRITICAL"
                recommendation = "Immediate flight surgeon consult required. Pause EVA/critical operational activities. Administer supplemental oxygen if SpO2 < 92%, and enforce medical rest protocol."
            elif risk_score >= 35:
                risk_level = "ELEVATED"
                recommendation = "Schedule mandatory 2-hour sleep buffer, oral electrolyte rehydration, and review mission workload. Re-assess vitals in 4 hours."
            else:
                risk_level = "NOMINAL"
                recommendation = "All monitored physiological and circadian parameters within mission flight-rules tolerance. Continue nominal schedule."

            # Protocol recommendations aligned with NASA Flight Rules
            protocols = [
                "Circadian regulation: align cabin ambient lighting to NASA blue-enriched (480nm) during active duty and blue-depleted (460nm cut) 2 hours pre-sleep.",
                "ECLSS cabin air check: verify cabin partial pressure of CO2 is maintained below 3.0 mmHg to prevent microgravity headache.",
                "Cardiovascular countermeasure: confirm completion of daily 30-minute high-intensity cycle ergometer or ARED resistance workout."
            ]

            res = {
                "astronaut_id": astronaut_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors if risk_factors else ["No significant clinical risk factors detected."],
                "recommended_action": recommendation,
                "mitigation_protocols": protocols,
                "confidence": None  # Explicitly null per NASA Space Apps recommendation to indicate explainable rule-based logic
            }
            self._send_json(200, res)

        except Exception as err:
            self._send_error(400, "Error running risk prediction", str(err))

    def _handle_create_alert(self, incoming):
        new_alert = {
            "id": f"ALT-{int(time.time()) % 10000}",
            "astronaut_id": incoming.get("astronaut_id", "ASTRO-001"),
            "astronaut_name": incoming.get("astronaut_name", "Mark Vance"),
            "alert_type": incoming.get("alert_type", "Manual Clinical Alert"),
            "severity": incoming.get("severity", "ELEVATED"),
            "status": "NEW",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "rationale": incoming.get("rationale", "User triggered clinical alert"),
            "protocol": incoming.get("protocol", "Follow standard spaceflight operational medical procedures.")
        }
        ALERTS_DATA.insert(0, new_alert)
        self._send_json(201, {"success": True, "alert": new_alert})

    def _handle_resolve_alert(self, incoming):
        alert_id = incoming.get("id")
        for alert in ALERTS_DATA:
            if alert["id"] == alert_id:
                alert["status"] = "RESOLVED"
                self._send_json(200, {"success": True, "alert": alert})
                return
        self._send_error(404, "Alert ID not found")

    def _handle_demo_start(self, incoming):
        scenario = incoming.get("scenario", "normal")
        if scenario == "fatigue":
            data = {
                "scenario": "fatigue",
                "label": "Sleep Deprivation & High Workload Scenario",
                "astronaut": {
                    "id": "ASTRO-001",
                    "name": "Mark Vance",
                    "heart_rate": 92,
                    "spo2": 96,
                    "sleep_hours": 4.2,
                    "fatigue_score": 8,
                    "stress_score": 7,
                    "temperature": 36.9,
                    "systolic": 128,
                    "diastolic": 82
                },
                "status_badge": "SIMULATED TELEMETRY: FATIGUE SCENARIO"
            }
        elif scenario == "alert":
            data = {
                "scenario": "alert",
                "label": "Acute Cardiovascular & Hypoxia Alert Scenario",
                "astronaut": {
                    "id": "ASTRO-001",
                    "name": "Mark Vance",
                    "heart_rate": 112,
                    "spo2": 89,
                    "sleep_hours": 3.8,
                    "fatigue_score": 9,
                    "stress_score": 9,
                    "temperature": 38.1,
                    "systolic": 152,
                    "diastolic": 96
                },
                "status_badge": "SIMULATED TELEMETRY: CRITICAL ALERT"
            }
        else:
            data = {
                "scenario": "normal",
                "label": "Nominal Spaceflight Mission Telemetry",
                "astronaut": {
                    "id": "ASTRO-001",
                    "name": "Mark Vance",
                    "heart_rate": 72,
                    "spo2": 98,
                    "sleep_hours": 7.8,
                    "fatigue_score": 3,
                    "stress_score": 3,
                    "temperature": 36.7,
                    "systolic": 118,
                    "diastolic": 76
                },
                "status_badge": "SIMULATED TELEMETRY: NOMINAL MISSION"
            }
        self._send_json(200, data)

    def _handle_telemetry_stream(self):
        """Generates realistic live biological and environmental telemetry from active sensors."""
        # Base vitals with micro-variations
        hr = round(random.uniform(70.5, 75.8), 1)
        spo2 = round(random.uniform(98.1, 99.4), 1)
        temp = round(random.uniform(36.6, 36.9), 1)
        systolic = int(random.uniform(116, 122))
        diastolic = int(random.uniform(74, 80))
        resp = int(random.uniform(14, 16))
        hrv = int(random.uniform(62, 74))

        packet = {
            "packet_id": f"PKT-{int(time.time()*1000)%1000000}",
            "device_id": "DEV-ASTROSKIN-01",
            "source_name": "NASA AstroSkin Bio-Harness",
            "source_type": "digital_device",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "astronaut_id": "ASTRO-001",
            "heart_rate": hr,
            "spo2": spo2,
            "temperature": temp,
            "systolic": systolic,
            "diastolic": diastolic,
            "respiration": resp,
            "hrv": hrv,
            "accel_g": [round(random.uniform(-0.02, 0.02), 3) for _ in range(3)],
            "signal_quality": "OPTIMAL (99.4%)",
            "status": "NOMINAL"
        }
        self._send_json(200, packet)

    def _handle_telemetry_ingest(self, incoming):
        """
        Ingests digital telemetry transmitted from any device, sensor, or AI model.
        Evaluates clinical thresholds and routes to alert system if necessary.
        """
        try:
            device_id = incoming.get("device_id", "EXTERNAL-DEVICE")
            source_type = incoming.get("source_type", "digital_device")
            source_name = incoming.get("source_name", "Connected Digital Medical Device")
            astronaut_id = incoming.get("astronaut_id", "ASTRO-001")
            
            hr = float(incoming.get("heart_rate", 72))
            spo2 = float(incoming.get("spo2", 98))
            temp = float(incoming.get("temperature", 36.8))
            systolic = float(incoming.get("systolic", 118))
            diastolic = float(incoming.get("diastolic", 78))
            resp = float(incoming.get("respiration", 15))
            hrv = float(incoming.get("hrv", 65))

            # Safety and Anomaly Assessment
            problems = []
            if hr < 55 or hr > 115:
                problems.append(f"Heart rate outside flight tolerance ({hr} bpm)")
            if spo2 < 93:
                problems.append(f"Critical arterial hypoxia detected (SpO2: {spo2}%)")
            elif spo2 < 95:
                problems.append(f"Low arterial oxygen saturation (SpO2: {spo2}%)")
            if temp < 35.8 or temp > 37.8:
                problems.append(f"Abnormal thermal regulation ({temp} °C)")
            if systolic > 140 or systolic < 90:
                problems.append(f"Systolic blood pressure out of bounds ({systolic} mmHg)")

            if len(problems) >= 2 or spo2 < 92:
                status = "CRITICAL"
                # Automatically register an alert in the central registry
                ALERTS_DATA.insert(0, {
                    "id": f"ALT-{int(time.time())%10000}",
                    "astronaut_id": astronaut_id,
                    "astronaut_name": incoming.get("astronaut_name", "Astronaut"),
                    "alert_type": "Device/AI Ingest Anomaly",
                    "severity": "CRITICAL",
                    "status": "NEW",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "rationale": "; ".join(problems),
                    "protocol": f"Auto-generated by digital ingestion from {source_name}. Initiate medical protocol."
                })
            elif len(problems) == 1:
                status = "NEEDS MONITORING"
            else:
                status = "NOMINAL"

            packet_id = f"PKT-{int(time.time()*1000)%1000000}"
            packet = {
                "packet_id": packet_id,
                "device_id": device_id,
                "source_name": source_name,
                "source_type": source_type,
                "astronaut_id": astronaut_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "heart_rate": hr,
                "spo2": spo2,
                "temperature": temp,
                "systolic": systolic,
                "diastolic": diastolic,
                "respiration": resp,
                "hrv": hrv,
                "status": status,
                "problems": problems,
                "notes": incoming.get("notes", "")
            }

            global LATEST_TELEMETRY
            LATEST_TELEMETRY = packet
            TELEMETRY_LOG.append(packet)
            if len(TELEMETRY_LOG) > 50:
                TELEMETRY_LOG.pop(0)

            self._send_json(200, {
                "success": True,
                "status": "INGESTED",
                "packet_id": packet_id,
                "clinical_evaluation": status,
                "problems_detected": problems,
                "telemetry": packet,
                "message": f"Successfully ingested digital telemetry from {source_name}."
            })
        except Exception as e:
            self._send_error(400, "Failed to ingest digital telemetry", str(e))

    def _handle_telemetry_batch(self, incoming):
        """Ingests a batch of digital records (e.g. from CSV/JSON device export)."""
        try:
            records = incoming.get("records", [])
            if not isinstance(records, list) or len(records) == 0:
                self._send_error(400, "Invalid batch payload. Expected array of records.")
                return

            ingested_count = 0
            for item in records:
                packet = {
                    "packet_id": f"BATCH-{int(time.time()*1000)%1000000}-{ingested_count}",
                    "device_id": item.get("device_id", "DEVICE-BATCH-IMPORT"),
                    "source_name": item.get("source_name", "Device Log Batch"),
                    "source_type": "file_import",
                    "timestamp": item.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())),
                    "heart_rate": float(item.get("heart_rate", item.get("hr", 72))),
                    "spo2": float(item.get("spo2", 98)),
                    "temperature": float(item.get("temperature", item.get("temp", 36.8))),
                    "systolic": float(item.get("systolic", 118)),
                    "diastolic": float(item.get("diastolic", 78)),
                    "respiration": float(item.get("respiration", 15)),
                    "hrv": float(item.get("hrv", 65)),
                    "status": "NOMINAL"
                }
                TELEMETRY_LOG.append(packet)
                ingested_count += 1

            self._send_json(200, {
                "success": True,
                "ingested_count": ingested_count,
                "message": f"Successfully ingested {ingested_count} digital telemetry records into mission archive."
            })
        except Exception as e:
            self._send_error(400, "Batch ingestion error", str(e))

    def _handle_create_record(self, incoming):
        """Creates a new persistent health record in SQLite database."""
        try:
            if not incoming.get("astronaut_id"):
                incoming["astronaut_id"] = "ASTRO-001"
            
            rec_id = db.insert_record(incoming)
            created = db.get_record_by_id(rec_id)
            astro = db.get_astronaut_by_id(incoming["astronaut_id"])
            self._send_json(201, {
                "success": True,
                "id": rec_id,
                "record": created,
                "astronaut": astro,
                "message": f"Successfully created health record #{rec_id} for {incoming['astronaut_id']} in mission database."
            })
        except Exception as err:
            self._send_error(400, "Failed to create health record", str(err))

    def _handle_cognitive_save(self, incoming):
        """Saves evaluation results from the interactive neurocognitive testing suite."""
        try:
            astro_id = incoming.get("astronaut_id", "ASTRO-001")
            test_type = incoming.get("test_type", "Comprehensive Cognitive Battery")
            score = float(incoming.get("score", 90))
            reaction_ms = float(incoming.get("reaction_time_ms", 240))
            accuracy = float(incoming.get("accuracy", 100))
            attention = float(incoming.get("attention_score", 90))
            memory = float(incoming.get("memory_score", 85))
            notes = incoming.get("notes", "")

            rec_id = db.save_cognitive_result(
                astro_id=astro_id,
                test_type=test_type,
                score=score,
                reaction_ms=reaction_ms,
                accuracy=accuracy,
                attention_score=attention,
                memory_score=memory,
                notes=notes
            )
            created = db.get_record_by_id(rec_id)
            astro = db.get_astronaut_by_id(astro_id)
            self._send_json(201, {
                "success": True,
                "id": rec_id,
                "astronaut": astro,
                "record": created,
                "message": f"Successfully recorded {test_type} score {score}/100 into mission database."
            })
        except Exception as e:
            self._send_error(400, "Failed to save cognitive result", str(e))

    def _handle_simulate_variation(self, incoming):
        """
        Health Variation Simulator:
        Allows modifying parameters (e.g. sleep, HR, stress, exercise) and calculates
        how variations affect risk scores, recovery, fatigue, and triggers simulated alerts.
        Clearly tagged with is_simulated: true.
        """
        try:
            astro_id = incoming.get("astronaut_id", "ASTRO-001")
            astro = db.get_astronaut_by_id(astro_id) or {"name": "Astronaut", "role": "Crew Member"}
            summary = db.get_stats_summary(astro_id, limit=30)
            avg = summary.get("averages", {})

            # Baseline comparisons
            base_sleep = avg.get("sleep_hours", 7.5)
            base_hr = avg.get("heart_rate", 72.0)
            base_spo2 = avg.get("spo2", 98.0)
            base_stress = avg.get("stress_level", 3.0)
            base_exercise = avg.get("exercise_duration_min", 45.0)
            base_fatigue = avg.get("fatigue_score", 3.0)

            # Simulated overrides (support both key conventions)
            sim_sleep = float(incoming.get("sleep_total_hours") or incoming.get("sleep_hours") or base_sleep)
            sim_hr = float(incoming.get("heart_rate_bpm") or incoming.get("heart_rate") or base_hr)
            sim_spo2 = float(incoming.get("spo2_percent") or incoming.get("spo2") or base_spo2)
            sim_stress = float(incoming.get("stress_level", base_stress))
            sim_exercise = float(incoming.get("exercise_duration_min", base_exercise))
            sim_fatigue = float(incoming.get("fatigue_score", base_fatigue))

            # Dynamic impact equations based on aerospace physiology
            sleep_deficit = max(0.0, 7.5 - sim_sleep)
            projected_fatigue = round(min(10.0, max(1.0, sim_fatigue + sleep_deficit * 0.9)), 1)
            projected_sleep_quality = round(min(100.0, max(25.0, 90.0 - sleep_deficit * 12.0 - (sim_stress - 3) * 3.5)), 1)
            projected_recovery = round(min(100.0, max(20.0, 100.0 - (projected_fatigue * 7.5) + (sim_sleep * 3.5) - (sim_stress * 2.0))), 1)
            projected_reaction_ms = round(240.0 + sleep_deficit * 26.0 + (sim_stress - 3) * 11.0, 1)
            projected_cognitive = round(min(100.0, max(45.0, 94.0 - sleep_deficit * 5.0 - (sim_stress - 3) * 2.5)), 1)

            # Multivariable Risk Penalty
            risk_penalty = 5.0
            forecast_alerts = []
            observations = []

            if sim_sleep < 4.5:
                risk_penalty += 32.0
                forecast_alerts.append({
                    "severity": "CRITICAL",
                    "title": "Severe Circadian Sleep Debt",
                    "desc": f"Simulated {sim_sleep:.1f}h sleep falls into acute neurobehavioral lapse zone (<4.5h)."
                })
                observations.append("Severe sleep deprivation impairs vigilant attention, micro-sleep vulnerability elevated.")
            elif sim_sleep < 6.0:
                risk_penalty += 15.0
                forecast_alerts.append({
                    "severity": "ELEVATED",
                    "title": "Moderate Sleep Restriction",
                    "desc": f"Simulated {sim_sleep:.1f}h daily sleep causes cumulative neurocognitive latency."
                })
                observations.append("Mild sleep restriction detected; recovery schedule extension recommended.")

            if sim_spo2 < 93.0:
                risk_penalty += 45.0
                forecast_alerts.append({
                    "severity": "CRITICAL",
                    "title": "Simulated Arterial Hypoxia Alert",
                    "desc": f"Arterial saturation {sim_spo2}% requires supplemental O2 and ECLSS cabin purge."
                })
                observations.append("Hypoxic cellular stress: immediate atmospheric life-support intervention indicated.")
            elif sim_spo2 < 95.0:
                risk_penalty += 18.0
                forecast_alerts.append({
                    "severity": "ELEVATED",
                    "title": "Suboptimal Blood Oxygen",
                    "desc": f"SpO2 {sim_spo2}% is below optimal flight rule baseline (>95%)."
                })

            if sim_hr > 110.0 or sim_hr < 50.0:
                risk_penalty += 28.0
                forecast_alerts.append({
                    "severity": "CRITICAL",
                    "title": "Cardiovascular Deconditioning / Tachycardia",
                    "desc": f"Heart rate of {sim_hr} bpm reflects abnormal autonomic stress response."
                })
            elif sim_hr > 88.0:
                risk_penalty += 12.0

            if sim_stress > 7.0:
                risk_penalty += 18.0
                forecast_alerts.append({
                    "severity": "ELEVATED",
                    "title": "High Operational Stress Index",
                    "desc": f"Stress level {sim_stress}/10 accelerates sympathetic tone exhaustion."
                })

            if sim_exercise < 25.0:
                risk_penalty += 14.0
                forecast_alerts.append({
                    "severity": "ADVISORY",
                    "title": "Insufficient Musculoskeletal Countermeasures",
                    "desc": f"Daily exercise {sim_exercise} min below NASA 45-min ARED/CEVIS flight rule minimum."
                })
                observations.append("Reduced mechanical loading accelerates trabecular bone calcium loss (~1.2%/month).")

            sim_risk_score = int(min(100, max(5, round(risk_penalty))))
            if sim_risk_score >= 65:
                risk_level = "CRITICAL ALERT"
            elif sim_risk_score >= 35:
                risk_level = "ELEVATED RISK"
            else:
                risk_level = "NOMINAL"

            if not observations:
                observations.append("All simulated health dimensions stay within acceptable NASA spaceflight tolerance envelopes.")

            # Simulated 7-day Trajectory Points for graphical comparison overlay
            trajectory_days = ["Day -3", "Day -2", "Day -1", "Today", "Sim +1", "Sim +2", "Sim +3"]
            sim_trajectory = []
            comparison_trajectory = []
            for i, dlabel in enumerate(trajectory_days):
                factor = (i - 3) / 3.0 if i >= 3 else 0
                sim_rec = round(min(100.0, max(20.0, 85.0 + (projected_recovery - 85.0) * (1 if i >= 3 else 0))), 1)
                sim_risk = round(min(100.0, max(5.0, 15.0 + (sim_risk_score - 15.0) * (1 if i >= 3 else 0))), 1)
                
                sim_trajectory.append({
                    "label": dlabel,
                    "heart_rate": round(base_hr + (sim_hr - base_hr) * (1 if i >= 3 else 0), 1),
                    "sleep_hours": round(base_sleep + (sim_sleep - base_sleep) * (1 if i >= 3 else 0), 1),
                    "spo2": round(base_spo2 + (sim_spo2 - base_spo2) * (1 if i >= 3 else 0), 1),
                    "fatigue": round(min(10.0, max(1.0, base_fatigue + (projected_fatigue - base_fatigue) * (1 if i >= 3 else 0))), 1),
                    "recovery": sim_rec,
                    "is_simulated": (i >= 3)
                })

                comparison_trajectory.append({
                    "day_label": dlabel,
                    "actual_recovery": 85.0 if i >= 3 else round(83.0 + i, 1),
                    "simulated_recovery": sim_rec,
                    "actual_risk": 15.0,
                    "simulated_risk": sim_risk,
                    "is_simulated": (i >= 3)
                })

            alert_strings = [f"{a['title']}: {a['desc']}" for a in forecast_alerts]

            self._send_json(200, {
                "success": True,
                "is_simulated": True,
                "astronaut_id": astro_id,
                "astronaut_name": astro.get("name"),
                "projected_risk_score": sim_risk_score,
                "risk_level": risk_level,
                "simulated_sleep_quality": projected_sleep_quality,
                "simulated_recovery_score": projected_recovery,
                "simulated_reaction_time_ms": projected_reaction_ms,
                "simulated_cognitive_score": projected_cognitive,
                "alerts_triggered": alert_strings,
                "comparison_trajectory": comparison_trajectory,
                "simulated_inputs": {
                    "sleep_hours": sim_sleep,
                    "heart_rate": sim_hr,
                    "spo2": sim_spo2,
                    "stress_level": sim_stress,
                    "exercise_duration_min": sim_exercise,
                    "fatigue_score": sim_fatigue
                },
                "impact_analysis": {
                    "composite_risk_score": sim_risk_score,
                    "risk_level": risk_level,
                    "sleep_quality_projected": projected_sleep_quality,
                    "recovery_score_projected": projected_recovery,
                    "fatigue_projected": projected_fatigue,
                    "reaction_time_latency_ms": projected_reaction_ms,
                    "cognitive_projected": projected_cognitive,
                    "forecast_alerts": forecast_alerts,
                    "clinical_observations": observations
                },
                "trajectory": sim_trajectory,
                "message": f"Simulation computed successfully. Risk Index: {sim_risk_score}/100 ({risk_level})."
            })
        except Exception as e:
            self._send_error(400, "Simulation computation error", str(e))


def run_server(port=None):
    if port is None:
        port = int(os.environ.get("PORT", 8000))

    print()
    print("======================================")
    print("          🚀 SPACEMED")
    print("  Astronaut Health Monitoring System")
    print("======================================")
    print(f"Server started on port {port}")
    print(f"Index expected at: {HTML_FILE}")
    print("Serving with AI Health Intelligence & Mission Control API")
    print()

    server = HTTPServer(("0.0.0.0", port), SpaceMedHandler)
    return server


if __name__ == "__main__":
    s = run_server()
    s.serve_forever()
