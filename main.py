from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json


# Location of this Python file
BASE_DIR = Path(__file__).resolve().parent

# Location of index.html
HTML_FILE = BASE_DIR / "static" / "index.html"


class SpaceMedHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/" or self.path == "/index.html":

            if not HTML_FILE.exists():

                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()

                message = (
                    "ERROR: index.html was not found.\n\n"
                    "Expected location:\n"
                    + str(HTML_FILE)
                )

                self.wfile.write(message.encode())
                return

            # Read HTML file
            html = HTML_FILE.read_bytes()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(html))
            )

            self.end_headers()

            self.wfile.write(html)

        else:

            self.send_response(404)
            self.end_headers()


    def do_POST(self):

        if self.path != "/check-health":

            self.send_response(404)
            self.end_headers()
            return


        try:

            length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(length)

            data = json.loads(body)

        except Exception:

            self.send_response(400)
            self.end_headers()
            return


        problems = []


        # Heart rate
        if data["heart_rate"] < 60 or data["heart_rate"] > 100:

            problems.append(
                "Abnormal heart rate"
            )


        # Oxygen
        if data["spo2"] < 95:

            problems.append(
                "Low oxygen level"
            )


        # Temperature
        if (
            data["temperature"] < 36
            or data["temperature"] > 37.5
        ):

            problems.append(
                "Abnormal temperature"
            )


        # Systolic blood pressure
        if (
            data["systolic"] < 90
            or data["systolic"] > 139
        ):

            problems.append(
                "Abnormal systolic blood pressure"
            )


        # Diastolic blood pressure
        if (
            data["diastolic"] < 60
            or data["diastolic"] > 89
        ):

            problems.append(
                "Abnormal diastolic blood pressure"
            )


        # Overall status
        if len(problems) == 0:

            status = "NORMAL"

        elif len(problems) <= 2:

            status = "NEEDS MONITORING"

        else:

            status = "MEDICAL ALERT"


        result = {

            "astronaut": data["name"],

            "status": status,

            "problems": problems

        }


        response = json.dumps(result).encode("utf-8")


        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(response)



print()
print("======================================")
print("          🚀 SPACEMED")
print("  Astronaut Health Monitoring System")
print("======================================")
print()

print("Server started successfully!")

print()

print("Index file expected at:")

print(HTML_FILE)

print()

if HTML_FILE.exists():

    print("✅ index.html FOUND!")

else:

    print("❌ index.html NOT FOUND!")

print()

print("Open Chrome and go to:")

print("http://0.0.0.0:8080")

print()

print("Keep Pydroid running.")

print()


server = HTTPServer(
    ("0.0.0.0", port),
    SpaceMedHandler
)


server.serve_forever()