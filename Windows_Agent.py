import tkinter as tk
from tkinter import ttk, messagebox
import threading
import win32evtlog
import win32evtlogutil
import socket
import json
import time
import requests
from cryptography.fernet import Fernet
from datetime import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === Config ===
SERVER_URL = "REPLASE WITH YOUR SERVER URL" #eg: on replit
FERNET_KEY = b'Cp0Ekjev9SEORvIhHdLACGri-88AY5i17lSsO7pN5-E='

class WinEvtLogClient:
    def __init__(self, server_url, fernet_cipher, log_types):
        self.server_url = server_url
        self.cipher = fernet_cipher
        self.hostname = socket.gethostname()
        self.log_types = log_types
        self.last_record_number = {lt: 0 for lt in log_types}
        self.running = False

    def format_event(self, ev, log_type):
        try:
            msg = win32evtlogutil.SafeFormatMessage(ev, log_type)
        except Exception:
            msg = f"<Could not format message for EventID {ev.EventID}>"

        return {
            "record_number": ev.RecordNumber,
            "received_at": datetime.now().isoformat(),
            "time_generated": ev.TimeGenerated.Format(),
            "source": ev.SourceName,
            "event_id": ev.EventID & 0xFFFF,
            "event_type": ev.EventType,
            "category": ev.EventCategory,
            "computer": ev.ComputerName,
            "message": msg,
            "host": self.hostname,
            "user": "system",
            "process_id": ev.EventID,
            "log_type": log_type.lower()
        }

    def encrypt_log(self, log_data):
        log_json = json.dumps(log_data)
        encrypted = self.cipher.encrypt(log_json.encode())
        return encrypted.decode()

    def send_log(self, log_data):
        encrypted_log = self.encrypt_log(log_data)
        payload = {'encrypted_log': encrypted_log}
        try:
            response = requests.post(
                f"{self.server_url}/api/logs",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Sent {log_data['log_type']} log: {log_data['source']} - {log_data['event_id']}")
            else:
                print(f"❌ Failed to send: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error sending log: {e}")

    def run(self):
        self.running = True
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        while self.running:
            for log_type in self.log_types:
                try:
                    handle = win32evtlog.OpenEventLog(None, log_type)
                    events = win32evtlog.ReadEventLog(handle, flags, 0)
                    if events:
                        for ev in events:
                            if ev.RecordNumber > self.last_record_number[log_type]:
                                evt_dict = self.format_event(ev, log_type)
                                self.send_log(evt_dict)
                                self.last_record_number[log_type] = ev.RecordNumber
                except Exception as e:
                    print(f"[ERROR] Reading {log_type} logs: {e}")
            time.sleep(3)

    def stop(self):
        self.running = False


class LogAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Log Agent")
        self.root.geometry("400x300")
        self.client = None
        self.thread = None

        self.log_types = ["Application", "System", "Security", "Setup"]

        ttk.Label(root, text="Select Log Types:").pack(pady=10)
        self.check_vars = {}
        for log_type in self.log_types:
            var = tk.BooleanVar(value=(log_type in ["Application", "System"]))
            cb = ttk.Checkbutton(root, text=log_type, variable=var)
            cb.pack(anchor="w", padx=20)
            self.check_vars[log_type] = var

        self.start_button = ttk.Button(root, text="Start Agent", command=self.start_agent)
        self.start_button.pack(pady=15)

        self.stop_button = ttk.Button(root, text="Stop Agent", command=self.stop_agent, state=tk.DISABLED)
        self.stop_button.pack()

        self.status_label = ttk.Label(root, text="Status: Idle")
        self.status_label.pack(pady=10)

    def start_agent(self):
        selected = [lt for lt, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showerror("No Selection", "Please select at least one log type.")
            return

        if not isinstance(FERNET_KEY, bytes):
            key = FERNET_KEY.encode()
        else:
            key = FERNET_KEY

        cipher = Fernet(key)
        self.client = WinEvtLogClient(SERVER_URL, cipher, selected)

        self.thread = threading.Thread(target=self.client.run, daemon=True)
        self.thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running...")

    def stop_agent(self):
        if self.client:
            self.client.stop()
            self.status_label.config(text="Status: Stopping...")
            self.thread.join(timeout=2)
            self.status_label.config(text="Status: Idle")

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogAgentGUI(root)
    root.mainloop()
