#LogNet
Secure Windows Event Log Collector & Analyzer
LogNet is a lightweight cybersecurity project for collecting, encrypting, transmitting, and analyzing Windows event logs.
It enables real-time monitoring of systems, helps detect suspicious activity, and maintains a secure audit trail.
Designed with simplicity and security in mind, it’s ideal for SOC teams, incident responders, and system administrators.

Features
Agent
Collects Windows Event Logs from Application, System, Security, and Setup.

Encrypts each log using Fernet (AES-CBC + HMAC).

Transmits logs securely over HTTPS to the server.

Simple GUI to select log types and start/stop the agent.

Server
Flask-based server that receives encrypted logs, decrypts, and stores them.

Web dashboard displays latest logs (up to 1000 stored in memory).

Runs automated analysis for common suspicious patterns (failed logins, malware keywords, repeated errors).

REST API to fetch logs and analysis in JSON format.

Dashboard
View recent logs in real time.

Summary of top event IDs, recent error spikes, repeated failed login attempts, and detected suspicious keywords.

Tech Stack
Python (Flask, Cryptography, Requests, pywin32)

HTML and Tailwind CSS for frontend dashboard

Windows Event Log API (via pywin32)

JSON over HTTPS

Quick Start
Server
Clone the repository and install dependencies.

bash
Copy
Edit
git clone https://github.com/yourusername/lognet.git
cd lognet
pip install -r requirements.txt
Run the Flask server:

bash
Copy
Edit
python app.py
Access the dashboard at:
http://localhost:5000

Agent
Run on any Windows machine you wish to monitor.

bash
Copy
Edit
python Agent.py
Use the GUI to select which log types to monitor.

Click Start Agent.
The agent will begin reading logs, encrypting them, and sending to the server.

Encryption
This project uses Fernet for end-to-end encryption of logs.

AES-128 (CBC mode) with HMAC SHA256 for message integrity.

The same FERNET_KEY must be configured on both the server and the agent.

Example Analysis Output
pgsql
Copy
Edit
Log counts by level: {'INFO': 56, 'WARNING': 5, 'ERROR': 3}
Top event IDs in last 100 logs: [(4624, 8), (4625, 5)]
Repeated failed login attempts: {'192.168.1.45': 6}
Suspicious keywords found: {'unauthorized': 3, 'malware': 1}
API Endpoints
POST /api/logs
Receives encrypted log data.

GET /api/logs
Returns the current list of decrypted logs in JSON.

POST /api/analyze
Accepts a JSON list of logs, returns analysis summary.

Roadmap
Add optional email or Slack alerts on suspicious detections.

Support exporting logs and analysis to CSV or JSON.

Build multi-host overview for monitoring multiple agents.

Provide Docker deployment options.

Contributing
Contributions are welcome. Please fork this repository, create a feature branch, and submit a pull request.

License
This project is licensed under the MIT License.

Example Configuration
ini
Copy
Edit
FERNET_KEY = Cp0Ekjev9SEORvIhHdLACGri-88AY5i17lSsO7pN5-E=
SERVER_URL = http://localhost:5000
