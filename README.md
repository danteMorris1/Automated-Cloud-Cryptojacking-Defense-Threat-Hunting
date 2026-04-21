<h1 align="center">Automated Cloud Cryptojacking Defense & Threat Hunting Project</h1>


![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)
![image](https://media.discordapp.net/attachments/1486889265991254076/1496278191688519772/Untitled.png?ex=69e94d28&is=69e7fba8&hm=78c2f2fe04b5db76e2e4c25a3aa39fabe857e0ceff0e4a77cd5a3eb36c7521e5&=&format=webp&quality=lossless&width=1823&height=862)
![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

### Project Overview![image](https://media.discordapp.net/attachments/1486889265991254076/1496281967313027082/Untitled_1.png?ex=69e950ac&is=69e7ff2c&hm=a5cb24a2cdabec75982f6bf491edf491d5fa502b60c5aaa10e0f8678f0e1d522&=&format=webp&quality=lossless)

This cloud hooneypot is a fully automated, cloud-native Threat Intelligence and Incident Response pipeline. The objective of this project was to deploy a vulnerable honeypot in a live cloud environment, capture real-world cryptojacking indicators of compromise (IOCs), and engineer an automated kill-switch that isolates compromised infrastructure without human intervention.

## 🏗️ Architecture & Tech Stack

* **Cloud Infrastructure:** DigitalOcean (Ubuntu 22.04 LTS Droplets)
* **Containerization:** Docker (Intentionally vulnerable Redis 5.0.3 deployment)
* **Telemetry & SIEM:** Datadog (Live Process & Network Monitoring, Custom Dashboards, Webhooks)
* **Automation & Orchestration:** Python (Flask, Requests), DigitalOcean API
* **Networking:** Ngrok (Secure tunneling for local SOC webhook ingestion)

## ⚙️ The Attack & Defense Lifecycle

1. **The Trap:** An outdated, unauthenticated Redis database container is exposed to the public internet via port `6379`.
2. **The Compromise:** Automated botnets scan the IPv4 space, detect the open port, and execute a remote code execution (RCE) payload to drop a cryptocurrency miner (e.g., `xmrig` or `kdevtmpfsi`).
3. **The Watchtower:** The Datadog Agent, running at the kernel level, detects a massive spike in `system.cpu.user` (>90%) and irregular outbound network traffic (`system.net.bytes_sent`) communicating with external mining pools.
4. **The Trigger:** A custom Datadog Metric Monitor evaluates the anomaly. If the CPU remains spiked for a sustained 5-minute window, it triggers a `CRITICAL` alert and fires a JSON webhook.
5. **The Kill-Switch:** A local Python-based SOC script receives the webhook via an Ngrok tunnel. It parses the alert, authenticates with the DigitalOcean API, and instantly issues a `power_off` command to the compromised Droplet, neutralizing the threat and preventing unauthorized cloud compute billing.

## 📊 Threat Intelligence Dashboard

Using Datadog, I built a custom SOC dashboard to visualize the attack in real-time. Key metrics tracked include:

* **CPU Hijacking (User %):** Visualizing the instant the cryptominer executes.
* **Top Malicious Processes:** Correlating the CPU spike to the exact malware binary name executing the attack.
* **Outbound Traffic:** Tracking the telemetry data sent back to the hacker's Command & Control (C2) server.

## 💻 The Auto-Remediation Code (Python Snippet)

This snippet highlights the webhook listener that catches the Datadog alert and executes the API kill command.

```python
@app.route('/datadog-alert', methods=['POST'])
def handle_alert():
    print("[!!!] CRITICAL ALERT: Cryptomining behavior detected. Initiating kill switch...")
    
    headers = {
        "Authorization": f"Bearer {DO_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"type": "power_off"}
    
    response = requests.post(
        f"[https://api.digitalocean.com/v2/droplets/](https://api.digitalocean.com/v2/droplets/){DROPLET_ID}/actions", 
        headers=headers, 
        json=data
    )
    
    if response.status_code == 201:
        return "Droplet successfully powered down. Threat neutralized.", 200
```
