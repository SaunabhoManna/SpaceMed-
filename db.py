"""
ORBITALIS - SpaceMed
SQLite Database Architecture for Astronaut Health Analytics & Reporting System
Zero external dependencies - standard library sqlite3
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone
import json

DB_FILE = Path(__file__).resolve().parent / "spacemed.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes database tables and seeds 30-day historical data if empty."""
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Astronauts Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS astronauts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        age INTEGER NOT NULL,
        agency TEXT NOT NULL,
        mission_day INTEGER NOT NULL,
        mission_start_date TEXT NOT NULL,
        status TEXT NOT NULL,
        baseline_heart_rate REAL,
        baseline_spo2 REAL,
        baseline_sleep REAL,
        baseline_fatigue REAL,
        readiness_score REAL,
        radiation_dose REAL
    );
    """)

    # 2. Health Records Table (Physiological, Sleep, Neuro, Musculo, Fatigue)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        astronaut_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        date TEXT NOT NULL,
        
        -- A. Physiological Health
        heart_rate REAL NOT NULL,
        hrv REAL NOT NULL,
        spo2 REAL NOT NULL,
        temperature REAL NOT NULL,
        systolic INTEGER NOT NULL,
        diastolic INTEGER NOT NULL,
        respiration REAL NOT NULL,
        
        -- B. Sleep Health
        sleep_hours REAL NOT NULL,
        deep_sleep_hours REAL NOT NULL,
        rem_sleep_hours REAL NOT NULL,
        light_sleep_hours REAL NOT NULL,
        sleep_quality REAL NOT NULL,
        sleep_efficiency REAL NOT NULL,
        sleep_consistency REAL NOT NULL,
        
        -- C. Neurobehavioural Health
        cognitive_score REAL NOT NULL,
        reaction_time_ms REAL NOT NULL,
        attention_score REAL NOT NULL,
        memory_score REAL NOT NULL,
        stress_level REAL NOT NULL,
        mood_score REAL NOT NULL,
        mental_fatigue REAL NOT NULL,
        
        -- D. Musculoskeletal Health
        bone_mineral_density_t REAL NOT NULL,
        muscle_strength_kg REAL NOT NULL,
        exercise_duration_min REAL NOT NULL,
        mobility_score REAL NOT NULL,
        
        -- E. Fatigue and Recovery
        fatigue_score REAL NOT NULL,
        energy_level REAL NOT NULL,
        recovery_score REAL NOT NULL,
        physical_workload_kcal REAL NOT NULL,
        water_liters REAL NOT NULL,
        active_minutes REAL NOT NULL,
        
        -- Meta / Simulation Tagging
        is_simulated INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (astronaut_id) REFERENCES astronauts (id)
    );
    """)

    # 3. Health Alerts Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_alerts (
        id TEXT PRIMARY KEY,
        astronaut_id TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        rationale TEXT NOT NULL,
        protocol TEXT NOT NULL,
        FOREIGN KEY (astronaut_id) REFERENCES astronauts (id)
    );
    """)

    conn.commit()

    # Seed Astronauts if empty
    cur.execute("SELECT COUNT(*) as count FROM astronauts;")
    if cur.fetchone()["count"] == 0:
        seed_astronauts(cur)
        conn.commit()

    # Seed 30-Day Historical Records if empty
    cur.execute("SELECT COUNT(*) as count FROM health_records;")
    if cur.fetchone()["count"] == 0:
        seed_historical_records(cur)
        conn.commit()

    # Seed Alerts if empty
    cur.execute("SELECT COUNT(*) as count FROM health_alerts;")
    if cur.fetchone()["count"] == 0:
        seed_alerts(cur)
        conn.commit()

    conn.close()


def seed_astronauts(cur):
    astronauts = [
        ("ASTRO-001", "Mark Vance", "Mission Commander", 42, "Orbitalis / NASA", 45, "2026-10-01", "NOMINAL", 72, 98, 7.6, 3, 94, 38.2),
        ("ASTRO-002", "Sarah Chen", "Flight Engineer", 36, "Orbitalis / ESA", 45, "2026-10-01", "ELEVATED RISK", 96, 95, 5.2, 7, 71, 42.1),
        ("ASTRO-003", "Elena Rostova", "Science Specialist", 39, "Orbitalis / JAXA", 45, "2026-10-01", "NOMINAL", 68, 99, 7.9, 2, 96, 36.8),
        ("ASTRO-004", "James Wilson", "Pilot / EVA Specialist", 44, "Orbitalis / CSA", 45, "2026-10-01", "MONITORING", 82, 97, 6.4, 5, 83, 45.4)
    ]
    cur.executemany("""
    INSERT INTO astronauts (
        id, name, role, age, agency, mission_day, mission_start_date, status,
        baseline_heart_rate, baseline_spo2, baseline_sleep, baseline_fatigue, readiness_score, radiation_dose
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, astronauts)


def seed_alerts(cur):
    alerts = [
        ("ALT-101", "ASTRO-001", "Hypoxia Risk", "CRITICAL", "RESOLVED", "2026-11-13 14:22:10 UTC",
         "Transient arterial O2 drop below 90% during EVA pressure hatch ingress.",
         "Deploy auxiliary cabin O2 mask and verify environmental life support loop (ECLSS)."),
        ("ALT-102", "ASTRO-002", "Circadian Sleep Debt", "ELEVATED", "NEW", "2026-11-13 09:15:40 UTC",
         "Consecutive 3-day sleep restriction (<5.0h) with cumulative fatigue index 7/10.",
         "Implement crew rest schedule extension. Shift lighting spectrum to 460nm blue-depleted."),
        ("ALT-103", "ASTRO-004", "Radiation Exposure Warning", "ADVISORY", "RESOLVED", "2026-11-12 18:40:00 UTC",
         "Minor solar energetic particle (SEP) flux enhancement detected outside habitat module.",
         "Astronaut in storm shelter. Dose rate nominal within shielding threshold.")
    ]
    cur.executemany("""
    INSERT INTO health_alerts (id, astronaut_id, alert_type, severity, status, timestamp, rationale, protocol)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, alerts)


def seed_historical_records(cur):
    """Generates 30 days of distinct, scientifically coherent records for each astronaut."""
    today = datetime(2026, 11, 14, 8, 0, 0)

    # 4 distinct physiological & behavioral archetypes
    archetypes = {
        "ASTRO-001": {  # Mark Vance: Stable, regular commander
            "base_hr": 71, "base_hrv": 68, "base_spo2": 98.4, "base_temp": 36.7,
            "base_bp_sys": 118, "base_bp_dia": 76, "base_resp": 15,
            "base_sleep": 7.6, "deep_ratio": 0.22, "rem_ratio": 0.23, "quality": 88,
            "cognitive": 92, "reaction": 240, "stress": 3.2, "mood": 8.0,
            "bmd": -0.32, "strength": 78, "exercise": 45, "fatigue": 2.8, "energy": 7.8, "water": 2.7
        },
        "ASTRO-002": {  # Sarah Chen: Elevated fatigue, sleep deficit over last 10 days
            "base_hr": 84, "base_hrv": 52, "base_spo2": 96.5, "base_temp": 36.9,
            "base_bp_sys": 126, "base_bp_dia": 82, "base_resp": 17,
            "base_sleep": 5.4, "deep_ratio": 0.16, "rem_ratio": 0.18, "quality": 64,
            "cognitive": 78, "reaction": 295, "stress": 6.8, "mood": 6.0,
            "bmd": -0.45, "strength": 65, "exercise": 30, "fatigue": 6.8, "energy": 5.2, "water": 2.2
        },
        "ASTRO-003": {  # Elena Rostova: High HRV, science specialist, excellent circadian
            "base_hr": 67, "base_hrv": 78, "base_spo2": 99.1, "base_temp": 36.6,
            "base_bp_sys": 114, "base_bp_dia": 74, "base_resp": 14,
            "base_sleep": 7.9, "deep_ratio": 0.25, "rem_ratio": 0.24, "quality": 93,
            "cognitive": 95, "reaction": 225, "stress": 2.4, "mood": 8.8,
            "bmd": -0.28, "strength": 72, "exercise": 50, "fatigue": 2.1, "energy": 8.4, "water": 2.8
        },
        "ASTRO-004": {  # James Wilson: EVA specialist, high physical activity, moderate recovery
            "base_hr": 78, "base_hrv": 62, "base_spo2": 97.4, "base_temp": 36.8,
            "base_bp_sys": 122, "base_bp_dia": 78, "base_resp": 16,
            "base_sleep": 6.5, "deep_ratio": 0.20, "rem_ratio": 0.21, "quality": 79,
            "cognitive": 86, "reaction": 260, "stress": 4.5, "mood": 7.2,
            "bmd": -0.38, "strength": 84, "exercise": 60, "fatigue": 4.6, "energy": 7.0, "water": 3.1
        }
    }

    records = []
    import math

    for astro_id, prof in archetypes.items():
        for day_offset in range(30, -1, -1):
            dt = today - timedelta(days=day_offset)
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")

            # Deterministic, non-random natural circadian / trajectory wave
            wave = math.sin(day_offset * 0.4)
            wave2 = math.cos(day_offset * 0.25)

            # Sarah Chen has a fatigue worsening trajectory in the last 7 days
            trend_factor = 0
            if astro_id == "ASTRO-002" and day_offset < 8:
                trend_factor = (8 - day_offset) * 0.25

            hr = round(prof["base_hr"] + wave * 3.5 + trend_factor * 2.0, 1)
            hrv = round(max(30, prof["base_hrv"] - wave * 4.0 - trend_factor * 3.0), 1)
            spo2 = round(min(100.0, max(92.0, prof["base_spo2"] + wave2 * 0.6 - trend_factor * 0.3)), 1)
            temp = round(prof["base_temp"] + wave * 0.15, 1)
            systolic = int(round(prof["base_bp_sys"] + wave * 4.0 + trend_factor * 2.0))
            diastolic = int(round(prof["base_bp_dia"] + wave * 2.5 + trend_factor * 1.5))
            respiration = round(prof["base_resp"] + wave2 * 0.8, 1)

            total_sleep = round(max(3.5, prof["base_sleep"] + wave * 0.6 - trend_factor * 0.4), 1)
            deep_sleep = round(total_sleep * prof["deep_ratio"], 1)
            rem_sleep = round(total_sleep * prof["rem_ratio"], 1)
            light_sleep = round(total_sleep - deep_sleep - rem_sleep, 1)
            sleep_quality = round(min(100.0, max(40.0, prof["quality"] + wave * 6.0 - trend_factor * 5.0)), 1)
            sleep_efficiency = round(min(98.0, max(65.0, 85.0 + wave * 5.0 - trend_factor * 3.0)), 1)
            sleep_consistency = round(min(96.0, max(70.0, 88.0 + wave2 * 4.0)), 1)

            cognitive = round(min(100.0, max(50.0, prof["cognitive"] + wave * 3.0 - trend_factor * 4.0)), 1)
            reaction_time = round(prof["reaction"] - wave * 15.0 + trend_factor * 20.0, 1)
            attention = round(min(100.0, max(45.0, cognitive * 0.98 + wave2 * 2.0)), 1)
            memory = round(min(100.0, max(50.0, cognitive * 0.95 + wave * 2.0)), 1)
            stress = round(min(10.0, max(1.0, prof["stress"] - wave * 0.8 + trend_factor * 0.8)), 1)
            mood = round(min(10.0, max(1.0, prof["mood"] + wave * 0.7 - trend_factor * 0.6)), 1)
            mental_fatigue = round(min(10.0, max(1.0, 10.0 - (energy := max(1.0, prof["energy"] + wave * 0.8 - trend_factor * 0.7)))), 1)

            # Bone mineral density slowly drifts -0.01 every few weeks in microgravity
            bmd = round(prof["bmd"] - (30 - day_offset) * 0.003, 3)
            strength = round(prof["strength"] + wave * 2.0, 1)
            exercise_duration = round(max(15.0, prof["exercise"] + wave2 * 8.0), 1)
            mobility = round(min(100.0, max(60.0, 86.0 + wave * 4.0)), 1)

            fatigue = round(min(10.0, max(1.0, prof["fatigue"] - wave * 0.8 + trend_factor * 0.7)), 1)
            recovery = round(min(100.0, max(35.0, 100.0 - (fatigue * 7.5) + (total_sleep * 3.0))), 1)
            workload = round(450.0 + exercise_duration * 6.5 + wave * 30.0, 1)
            water = round(max(1.5, prof["water"] + wave2 * 0.3), 1)
            active_mins = round(exercise_duration + 35.0 + wave * 10.0, 1)

            records.append((
                astro_id, time_str, date_str,
                hr, hrv, spo2, temp, systolic, diastolic, respiration,
                total_sleep, deep_sleep, rem_sleep, light_sleep, sleep_quality, sleep_efficiency, sleep_consistency,
                cognitive, reaction_time, attention, memory, stress, mood, mental_fatigue,
                bmd, strength, exercise_duration, mobility,
                fatigue, energy, recovery, workload, water, active_mins,
                0, f"Day {45 - day_offset} mission record"
            ))

    cur.executemany("""
    INSERT INTO health_records (
        astronaut_id, timestamp, date,
        heart_rate, hrv, spo2, temperature, systolic, diastolic, respiration,
        sleep_hours, deep_sleep_hours, rem_sleep_hours, light_sleep_hours, sleep_quality, sleep_efficiency, sleep_consistency,
        cognitive_score, reaction_time_ms, attention_score, memory_score, stress_level, mood_score, mental_fatigue,
        bone_mineral_density_t, muscle_strength_kg, exercise_duration_min, mobility_score,
        fatigue_score, energy_level, recovery_score, physical_workload_kcal, water_liters, active_minutes,
        is_simulated, notes
    ) VALUES (
        ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?
    );
    """, records)


# ================= DATA ACCESS FUNCTIONS ================= #

def get_astronauts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM astronauts ORDER BY id ASC;")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_astronaut_by_id(astro_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM astronauts WHERE id = ?;", (astro_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def _normalize_record(r):
    """Ensures consistent camel/snake/alias keys across backend and frontend."""
    if not r:
        return r
    d = dict(r)
    d["heart_rate_bpm"] = d.get("heart_rate")
    d["hrv_rmssd"] = d.get("hrv")
    d["spo2_percent"] = d.get("spo2")
    d["body_temperature_c"] = d.get("temperature")
    d["blood_pressure_sys"] = d.get("systolic")
    d["blood_pressure_dia"] = d.get("diastolic")
    d["respiration_rate"] = d.get("respiration")
    d["sleep_total_hours"] = d.get("sleep_hours")
    d["sleep_quality_score"] = d.get("sleep_quality")
    d["sleep_efficiency_percent"] = d.get("sleep_efficiency")
    d["cognitive_performance_score"] = d.get("cognitive_score")
    d["mood_assessment"] = d.get("mood_score")
    d["bone_density_tscore"] = d.get("bone_mineral_density_t")
    d["muscle_strength_index"] = d.get("muscle_strength_kg")
    d["recorded_at"] = d.get("timestamp")
    return d


def get_records(astro_id, limit=30, start_date=None, end_date=None, include_simulated=True):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM health_records WHERE astronaut_id = ?"
    params = [astro_id]

    if not include_simulated:
        query += " AND is_simulated = 0"

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY timestamp ASC"

    if limit and not (start_date or end_date):
        query += f" LIMIT {int(limit)}"

    cur.execute(query, params)
    rows = [_normalize_record(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_record_by_id(record_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM health_records WHERE id = ?;", (record_id,))
    row = cur.fetchone()
    conn.close()
    return _normalize_record(row) if row else None


def insert_record(data):
    conn = get_db_connection()
    cur = conn.cursor()

    # Determine date & timestamp if not provided
    ts = data.get("timestamp") or data.get("recorded_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    date_str = data.get("date") or ts[:10]

    cur.execute("""
    INSERT INTO health_records (
        astronaut_id, timestamp, date,
        heart_rate, hrv, spo2, temperature, systolic, diastolic, respiration,
        sleep_hours, deep_sleep_hours, rem_sleep_hours, light_sleep_hours, sleep_quality, sleep_efficiency, sleep_consistency,
        cognitive_score, reaction_time_ms, attention_score, memory_score, stress_level, mood_score, mental_fatigue,
        bone_mineral_density_t, muscle_strength_kg, exercise_duration_min, mobility_score,
        fatigue_score, energy_level, recovery_score, physical_workload_kcal, water_liters, active_minutes,
        is_simulated, notes
    ) VALUES (
        ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?
    );
    """, (
        data.get("astronaut_id", "ASTRO-001"),
        ts,
        date_str,
        float(data.get("heart_rate") or data.get("heart_rate_bpm") or 72),
        float(data.get("hrv") or data.get("hrv_rmssd") or 65),
        float(data.get("spo2") or data.get("spo2_percent") or 98),
        float(data.get("temperature") or data.get("body_temperature_c") or 36.8),
        int(data.get("systolic") or data.get("blood_pressure_sys") or 118),
        int(data.get("diastolic") or data.get("blood_pressure_dia") or 76),
        float(data.get("respiration") or data.get("respiration_rate") or 15),
        float(data.get("sleep_hours") or data.get("sleep_total_hours") or 7.5),
        float(data.get("deep_sleep_hours", 1.8)),
        float(data.get("rem_sleep_hours", 1.6)),
        float(data.get("light_sleep_hours", 4.1)),
        float(data.get("sleep_quality") or data.get("sleep_quality_score") or 85),
        float(data.get("sleep_efficiency") or data.get("sleep_efficiency_percent") or 90),
        float(data.get("sleep_consistency", 88)),
        float(data.get("cognitive_score") or data.get("cognitive_performance_score") or 90),
        float(data.get("reaction_time_ms", 245)),
        float(data.get("attention_score", 88)),
        float(data.get("memory_score", 86)),
        float(data.get("stress_level", 3.0)),
        float(data.get("mood_score") or data.get("mood_assessment") or 8.0),
        float(data.get("mental_fatigue", 3.0)),
        float(data.get("bone_mineral_density_t") or data.get("bone_density_tscore") or -0.35),
        float(data.get("muscle_strength_kg") or data.get("muscle_strength_index") or 75),
        float(data.get("exercise_duration_min", 45)),
        float(data.get("mobility_score", 88)),
        float(data.get("fatigue_score", 3.0)),
        float(data.get("energy_level", 7.5)),
        float(data.get("recovery_score", 82)),
        float(data.get("physical_workload_kcal", 550)),
        float(data.get("water_liters") or data.get("water_intake_liters") or 2.6),
        float(data.get("active_minutes", 55)),
        int(data.get("is_simulated", 0)),
        data.get("notes", "User entered record")
    ))
    record_id = cur.lastrowid
    conn.commit()
    conn.close()
    return record_id


def update_record(record_id, data):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE health_records SET
        heart_rate = ?, hrv = ?, spo2 = ?, temperature = ?, systolic = ?, diastolic = ?, respiration = ?,
        sleep_hours = ?, deep_sleep_hours = ?, rem_sleep_hours = ?, light_sleep_hours = ?, sleep_quality = ?, sleep_efficiency = ?,
        cognitive_score = ?, reaction_time_ms = ?, stress_level = ?, mood_score = ?, mental_fatigue = ?,
        bone_mineral_density_t = ?, muscle_strength_kg = ?, exercise_duration_min = ?,
        fatigue_score = ?, energy_level = ?, recovery_score = ?, water_liters = ?, active_minutes = ?,
        notes = ?
    WHERE id = ?;
    """, (
        float(data.get("heart_rate") or data.get("heart_rate_bpm") or 72),
        float(data.get("hrv") or data.get("hrv_rmssd") or 65),
        float(data.get("spo2") or data.get("spo2_percent") or 98),
        float(data.get("temperature") or data.get("body_temperature_c") or 36.8),
        int(data.get("systolic") or data.get("blood_pressure_sys") or 118),
        int(data.get("diastolic") or data.get("blood_pressure_dia") or 76),
        float(data.get("respiration") or data.get("respiration_rate") or 15),
        float(data.get("sleep_hours") or data.get("sleep_total_hours") or 7.5),
        float(data.get("deep_sleep_hours", 1.8)),
        float(data.get("rem_sleep_hours", 1.6)),
        float(data.get("light_sleep_hours", 4.1)),
        float(data.get("sleep_quality") or data.get("sleep_quality_score") or 85),
        float(data.get("sleep_efficiency") or data.get("sleep_efficiency_percent") or 90),
        float(data.get("cognitive_score") or data.get("cognitive_performance_score") or 90),
        float(data.get("reaction_time_ms", 245)),
        float(data.get("stress_level", 3.0)),
        float(data.get("mood_score") or data.get("mood_assessment") or 8.0),
        float(data.get("mental_fatigue", 3.0)),
        float(data.get("bone_mineral_density_t") or data.get("bone_density_tscore") or -0.35),
        float(data.get("muscle_strength_kg") or data.get("muscle_strength_index") or 75),
        float(data.get("exercise_duration_min", 45)),
        float(data.get("fatigue_score", 3.0)),
        float(data.get("energy_level", 7.5)),
        float(data.get("recovery_score", 82)),
        float(data.get("water_liters") or data.get("water_intake_liters") or 2.6),
        float(data.get("active_minutes", 55)),
        data.get("notes", "Updated record"),
        int(record_id)
    ))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_record(record_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM health_records WHERE id = ?;", (int(record_id),))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_stats_summary(astro_id, limit=30):
    """Calculates comprehensive averages, min, max and recent values across all 5 dimensions."""
    records = get_records(astro_id, limit=limit, include_simulated=False)
    if not records:
        return {}

    def avg(key):
        vals = [r[key] for r in records if r.get(key) is not None]
        return round(sum(vals) / len(vals), 1) if vals else 0

    latest = records[-1]

    base_avg = {
        "heart_rate": avg("heart_rate"),
        "heart_rate_bpm": avg("heart_rate"),
        "hrv": avg("hrv"),
        "hrv_rmssd": avg("hrv"),
        "spo2": avg("spo2"),
        "spo2_percent": avg("spo2"),
        "temperature": avg("temperature"),
        "body_temperature_c": avg("temperature"),
        "systolic": avg("systolic"),
        "blood_pressure_sys": avg("systolic"),
        "diastolic": avg("diastolic"),
        "blood_pressure_dia": avg("diastolic"),
        "respiration": avg("respiration"),
        "respiration_rate": avg("respiration"),
        "sleep_hours": avg("sleep_hours"),
        "sleep_total_hours": avg("sleep_hours"),
        "deep_sleep_hours": avg("deep_sleep_hours"),
        "rem_sleep_hours": avg("rem_sleep_hours"),
        "light_sleep_hours": avg("light_sleep_hours"),
        "sleep_quality": avg("sleep_quality"),
        "sleep_quality_score": avg("sleep_quality"),
        "sleep_efficiency": avg("sleep_efficiency"),
        "sleep_efficiency_percent": avg("sleep_efficiency"),
        "cognitive_score": avg("cognitive_score"),
        "cognitive_performance_score": avg("cognitive_score"),
        "reaction_time_ms": avg("reaction_time_ms"),
        "stress_level": avg("stress_level"),
        "mood_score": avg("mood_score"),
        "mood_assessment": avg("mood_score"),
        "mental_fatigue": avg("mental_fatigue"),
        "bone_mineral_density_t": round(avg("bone_mineral_density_t"), 3),
        "bone_density_tscore": round(avg("bone_mineral_density_t"), 3),
        "muscle_strength_kg": avg("muscle_strength_kg"),
        "muscle_strength_index": avg("muscle_strength_kg"),
        "exercise_duration_min": avg("exercise_duration_min"),
        "mobility_score": avg("mobility_score"),
        "fatigue_score": avg("fatigue_score"),
        "energy_level": avg("energy_level"),
        "recovery_score": avg("recovery_score"),
        "water_liters": avg("water_liters"),
        "active_minutes": avg("active_minutes")
    }

    return {
        "record_count": len(records),
        "latest": latest,
        "averages": base_avg
    }


def get_alerts_for_astronaut(astro_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM health_alerts WHERE astronaut_id = ? ORDER BY timestamp DESC;", (astro_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    astros = get_astronauts()
    print(f"Astronauts count: {len(astros)}")
    recs = get_records("ASTRO-001", limit=10)
    print(f"ASTRO-001 records: {len(recs)}")
