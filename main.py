from flask import Flask, request, jsonify, render_template
from cryptography.fernet import Fernet
import json
import datetime
import re
from collections import deque

app = Flask(__name__)

# === Config ===
FERNET_KEY = b'Cp0Ekjev9SEORvIhHdLACGri-88AY5i17lSsO7pN5-E='
cipher_suite = Fernet(FERNET_KEY)

# Use deque for automatic trimming to last 1000 logs
logs_storage = deque(maxlen=1000)

@app.route('/')
def dashboard():
    return render_template("home.html", logs=logs_storage)

@app.route('/api/logs', methods=['POST'])
def receive_logs():
    try:
        data = request.get_json()
        encrypted_log = data.get('encrypted_log')

        if not encrypted_log:
            return jsonify({'error': 'No encrypted_log provided'}), 400

        decrypted_log = cipher_suite.decrypt(encrypted_log.encode()).decode()
        log_data = json.loads(decrypted_log)

        log_type = log_data.get("log_type", "system").lower()
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'received_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'log_type': log_type,
            **log_data
        }

        logs_storage.append(log_entry)
        print(f"✅ Received log from {log_entry.get('host', 'unknown')} | Type: {log_type} | Source: {log_entry.get('source')}")

        return jsonify({'status': 'success', 'message': 'Log received and stored'})

    except Exception as e:
        print(f"❌ Error in /api/logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(list(logs_storage))

@app.route('/api/analyze', methods=['POST'])
def analyze_logs():
    data = request.get_json()
    logs = data.get('logs', [])
    if not isinstance(logs, list):
        return jsonify({'analysis': 'Invalid log data.'})
    analysis_text = analyze_logs_locally(logs)
    return jsonify({'analysis': analysis_text})

def analyze_logs_locally(logs):
    analysis = []

    # --- Log levels ---
    level_counts = {}
    for log in logs:
        level = log.get('level', 'UNKNOWN').upper()
        level_counts[level] = level_counts.get(level, 0) + 1
    analysis.append(f"Log counts by level: {level_counts}")

    # --- Event IDs ---
    event_id_counts = {}
    for log in logs[-100:]:  # look at last 100 logs
        event_id = log.get('event_id')
        if event_id is not None:
            event_id_counts[event_id] = event_id_counts.get(event_id, 0) + 1
    if event_id_counts:
        # sort descending by count
        sorted_event_ids = sorted(event_id_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        analysis.append(f"Top event IDs in last 100 logs: {sorted_event_ids}")

    # --- Recent errors ---
    recent_errors = [log for log in logs[-20:] if log.get('level', '').upper() == 'ERROR']
    if len(recent_errors) > 5:
        analysis.append(f"High number of ERROR logs in last 20 entries: {len(recent_errors)}")

    # --- Suspicious keywords ---
    suspicious_keywords = ['failed login', 'unauthorized', 'attack', 'malware', 'exploit', 'denied', 'ransomware']
    found_keywords = {}
    for log in logs[-50:]:
        msg = log.get('message', '').lower()
        for kw in suspicious_keywords:
            if kw in msg:
                found_keywords[kw] = found_keywords.get(kw, 0) + 1
    if found_keywords:
        analysis.append(f"Suspicious keywords found: {found_keywords}")

    # --- Repeated failed login sources ---
    failed_login_pattern = re.compile(r'failed login', re.IGNORECASE)
    failed_logins = {}
    for log in logs[-100:]:
        if failed_login_pattern.search(log.get('message', '')):
            src = log.get('source', 'unknown')
            failed_logins[src] = failed_logins.get(src, 0) + 1
    repeated_failed_sources = {k: v for k, v in failed_logins.items() if v >= 3}
    if repeated_failed_sources:
        analysis.append(f"Repeated failed login attempts: {repeated_failed_sources}")

    if not analysis:
        analysis.append("No suspicious activity detected in recent logs.")
    return "\n".join(analysis)


if __name__ == '__main__':
    print("\n🔐 Flask NFX Server Starting...")
    print("📊 Dashboard available at: localhost:5000")
    print("🛡️ End-to-End Encryption is ACTIVE\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
