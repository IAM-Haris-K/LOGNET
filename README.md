# LogNet
A simple, secure Python-based system for collecting, encrypting, transmitting, and analyzing Windows Event Logs.
Ideal for system administrators, SOC teams, and cybersecurity enthusiasts to monitor system activity and detect suspicious patterns.

 # ⚠️ Legal Disclaimer
This project is intended strictly for educational and authorized monitoring purposes.
Do not deploy this software on any systems you do not own or do not have explicit permission to monitor.
Unauthorized surveillance is illegal and unethical.

✨ Features
 Collects Windows Event Logs (Application, System, Security, Setup)
 Encrypts logs using Fernet (AES + HMAC) for end-to-end security
 Transmits logs over HTTPS to a Flask server
 Stores the last 1000 logs in memory
 Web dashboard to view logs and run automated analysis
 Detects repeated failed logins, suspicious keywords, spikes in errors, and top event IDs

🛠 Requirements
For the agent
🖥️ Windows machine

Python 3.x

Libraries:

bash
Copy
Edit
pip install pywin32 cryptography requests
For the server
Linux / Windows / Mac

Python 3.x

Libraries:

bash
Copy
Edit
pip install flask cryptography
🚀 Getting Started
🔌 Run the server
bash
Copy
Edit
python server.py
It will start on http://localhost:5000.

🖥️ Run the agent on Windows
bash
Copy
Edit
python agent.py
Or run silently (no console window):

cmd
Copy
Edit
pythonw.exe agent.py
⚙️ Configuration
Edit the agent script to set your:

python
Copy
Edit
SERVER_URL = "https://yourserver.com"
FERNET_KEY = b'your-generated-fernet-key'
Choose which logs to monitor in the GUI when starting the agent.

📝 Analysis & Dashboard
View logs in real-time on the web dashboard at http://localhost:5000

Click Analyze to get insights:

Log levels count

Top event IDs

Repeated failed login sources

Suspicious keywords

❤️ Contributing
Pull requests and issues are welcome!
If you’d like to add new detection rules or improve the UI, please open a PR.

📜 License
This project is licensed under the MIT License.
Use responsibly.
