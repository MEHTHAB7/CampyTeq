"""
CampyTeq Computer Vision Gateway - Stream Simulator
Demonstrates edge camera capture, simulated YOLO/InsightFace inference,
and streaming detection metadata events to Django's /api/v1/tracking/ingest/.
Zero external dependencies (uses standard urllib).
"""

import sys
import time
import json
import random
import urllib.request
import urllib.error
from datetime import datetime, timezone

DJANGO_BASE_URL = "http://localhost:8000"
INGEST_ENDPOINT = f"{DJANGO_BASE_URL}/api/v1/tracking/ingest/"
AUTH_TOKEN_URL = f"{DJANGO_BASE_URL}/api/v1/auth/token/"

# Registered Edge Cameras in Apex Tech
CAMERAS = [
    {"code": "CAM-GATE-01", "zone": "ZONE-GATE-1", "name": "Main Gate 1 Inbound"},
    {"code": "CAM-BLKA-01", "zone": "ZONE-BLKA-ENT", "name": "Block A Foyer"},
    {"code": "CAM-CR204-01", "zone": "ZONE-CR-204", "name": "Classroom 204"},
    {"code": "CAM-LAB2-01", "zone": "ZONE-CSE-LAB2", "name": "CSE Lab 2 North"},
    {"code": "CAM-LIB-01", "zone": "ZONE-LIB-ENT", "name": "Central Library Entry"},
]

# Enrolled Students in Apex Tech
STUDENTS = [
    {"student_number": "STU-2026-0042", "roll_number": "2026-CSE-042", "name": "Rahul Kumar"},
    {"student_number": "STU-2026-0015", "roll_number": "2026-CSE-015", "name": "Ananya Sen"},
    {"student_number": "STU-2026-0028", "roll_number": "2026-CSE-028", "name": "Rohan Gupta"},
]


def post_json(url, data, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    headers["User-Agent"] = "CampyTeq-EdgeGateway/1.0"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"message": err_body}
    except Exception as e:
        return 0, {"error": str(e)}


def obtain_security_jwt():
    """Authenticates security service account to obtain JWT bearer token."""
    code, res = post_json(AUTH_TOKEN_URL, {
        "email": "security.chief@apex.edu",
        "password": "Password123!"
    })
    if code == 200 and "access" in res:
        return res["access"]
    print(f"[!] Authentication failed: HTTP {code} - {res}")
    return None


def simulate_detection_stream(num_events=5, interval=1):
    """Simulates periodic edge detections and dispatches them to CampyTeq."""
    print("==================================================================")
    print("  CampyTeq CV Edge Gateway — Simulated Detection Pipeline")
    print("==================================================================")
    token = obtain_security_jwt()
    if not token:
        print("[!] Cannot proceed without valid JWT. Ensure backend is active at http://localhost:8000.")
        return

    headers = {
        "Authorization": f"Bearer {token}"
    }

    print(f"[*] Authenticated as Security Administrator.")
    print(f"[*] Streaming {num_events} simulated edge detections to {INGEST_ENDPOINT}...")

    for i in range(num_events):
        cam = random.choice(CAMERAS)
        student = random.choice(STUDENTS)
        confidence = round(random.uniform(0.9400, 0.9920), 4)

        payload = {
            "camera_code": cam["code"],
            "student_number": student["student_number"],
            "confidence_score": confidence,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "event_type": "FACE_RECOGNITION",
            "snapshot_url": f"/media/detections/sim_{cam['code']}_{int(time.time())}.jpg"
        }

        code, res = post_json(INGEST_ENDPOINT, payload, headers=headers)
        if code in (200, 201):
            print(f" [+] Sighting logged: [{cam['code']}] {student['name']} ({student['roll_number']}) - Conf: {confidence*100:.1f}%")
        else:
            print(f" [-] Ingestion rejected (HTTP {code}): {res}")

        if i < num_events - 1:
            time.sleep(interval)

    print("[*] Edge stream simulation batch completed successfully.")


if __name__ == "__main__":
    count = 3
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    simulate_detection_stream(num_events=count, interval=1)
