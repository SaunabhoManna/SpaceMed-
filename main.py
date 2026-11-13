from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import os
import time

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


class SpaceMedHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PATCH")
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
            data = json.dumps(ASTRONAUTS_DATA).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
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
