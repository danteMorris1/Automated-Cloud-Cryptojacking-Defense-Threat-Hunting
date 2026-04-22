<h1 align="center">Automated Cloud Cryptojacking Defense & Threat Hunting Project</h1>

![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)
![image](https://media.discordapp.net/attachments/1486889265991254076/1496286203085983815/Untitled_4.png?ex=69e9549e&is=69e8031e&hm=135654b51660dfd5638d6f0faac32bd092dbdd25fcb1b701ae2dda3c7e561b57&=&format=webp&quality=lossless&width=1828&height=864)
![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

![image](https://media.discordapp.net/attachments/1486889265991254076/1496281967313027082/Untitled_1.png?ex=69e950ac&is=69e7ff2c&hm=a5cb24a2cdabec75982f6bf491edf491d5fa502b60c5aaa10e0f8678f0e1d522&=&format=webp&quality=lossless)![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

This **live** cloud honeypot project was a fully automated, cloud-native Threat Intelligence and Incident Response pipeline. The **objective** of this project was to deploy a vulnerable honeypot in a live cloud environment, capture **real-world** cryptojacking indicators of compromise (IOCs), and engineer an automated kill-switch that isolates compromised infrastructure *without* human intervention!

![image](https://media.discordapp.net/attachments/1486889265991254076/1496293621345947778/Untitled_6.png?ex=69e95b87&is=69e80a07&hm=babefbb1505b719629e60ca513cb95ede1132e32a386b0895c4ae5a1a2b05bdf&=&format=webp&quality=lossless)![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

* **Cloud Infrastructure -** DigitalOcean (Droplet VM running Ubuntu 22.04 LTS)
* **Containerization -** Docker (Intentionally vulnerable Redis 5.0.3 deployment)
* **Telemetry & SIEM -** Datadog (Live Process & Network Monitoring, Custom Dashboards, Webhooks)
* **Automation & Orchestration -** Python (Flask, Requests), DigitalOcean API
* **Networking -** Ngrok (Secure tunneling for local SOC webhook ingestion)

![image](https://media.discordapp.net/attachments/1486889265991254076/1496299297141030952/Untitled_9.png?ex=69e960d0&is=69e80f50&hm=1cf4e46dac7d5e8bddbee11d546d75dbe4ee4c58ef2a62db36c20315a980968d&=&format=webp&quality=lossless)![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

1. **The "Honeypot" -** An outdated, unauthenticated Redis database container is exposed to the public internet via port `6379`.
2. **The Compromise:** Automated botnets scan the IPv4 space, detect the open port, and execute a remote code execution (RCE) payload to drop a cryptocurrency miner (e.g., `xmrig` or `kdevtmpfsi`).
3. **The Watchtower:** The Datadog Agent, running at the *kernel* level in the droplet, detects a massive spike in `system.cpu.user` (>90%) and irregular outbound network traffic (`system.net.bytes_sent`) communicating with external mining pools.
4. **The Trigger:** A custom Datadog Metric Monitor evaluates the anomaly. If the CPU remains spiked for a sustained 5-minute window, it triggers a `CRITICAL` alert and fires a JSON webhook.
5. **The Kill-Switch:** A local Python-based SOC script receives the webhook via an Ngrok tunnel. It parses the alert, authenticates with the DigitalOcean API, and instantly issues a `power_off` command to the compromised Droplet, neutralizing the threat and preventing unauthorized cloud compute billing.

![image](https://media.discordapp.net/attachments/1486889265991254076/1496307394202832956/Untitled_10.png?ex=69e9685a&is=69e816da&hm=13e8266ea6e44ab0b8c7e60ad43470ecb418972f36adecf4a66c489a50dfcc17&=&format=webp&quality=lossless)![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

Using Datadog, I built a custom SOC dashboard to visualize the attack in real-time. Key metrics tracked include:

* **CPU Hijacking (User %):** Visualizing the instant the cryptominer executes.
* **Top Malicious Processes:** Correlating the CPU spike to the exact malware binary name executing the attack.
* **Outbound Traffic:** Tracking the telemetry data sent back to the hacker's Command & Control (C2) server.

![image](https://media.discordapp.net/attachments/1486889265991254076/1496313378296041572/image_4.png?ex=69e96ded&is=69e81c6d&hm=bde1a5a8594efa8000e53b9560c4941d868acc8384582b82376a2c58762983fd&=&format=webp&quality=lossless&width=550&height=276)

(Datadog dashboard showing my widget setup)

![image](https://media.discordapp.net/attachments/1486889265991254076/1496308458864119859/Untitled_11.png?ex=69e96958&is=69e817d8&hm=3f1355b942ac78218d6661d4799a4a724bed6de49e7236b1f3db35a3faafc606&=&format=webp&quality=lossless)![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)


This simple python script I built with the help of AI highlights the webhook listener that catches the Datadog alert and executes the API kill command.

If you're interested in using it yourself, replace DO_TOKEN and DROPLET_ID with your personal DigitalOcean Token & ID. You would also have to establish an **Ngrok** tunnel to route the external Datadog webhook alerts into *your* personal local environment.

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# DigitalOcean credentials
DO_TOKEN = "YOUR DIGITALOCEAN TOKEN HERE"
DROPLET_ID = "DROPLET ID HERE"

@app.route('/datadog-alert', methods=['POST'])
def handle_alert():
    print("\n[!!!] CRITICAL ALERT RECEIVED FROM DATADOG [!!!]")
    print("Cryptomining behavior detected. Initiating immediate kill switch...")
    
    headers = {
        "Authorization": f"Bearer {DO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # API payload to power off the server
    data = {"type": "power_off"}
    
    # Sends kill command directly to DigitalOcean
    print("Transmitting power_off command to DigitalOcean API...")
    response = requests.post(
        f"https://api.digitalocean.com/v2/droplets/{DROPLET_ID}/actions", 
        headers=headers, 
        json=data
    )
    
    if response.status_code == 201:
        print("[SUCCESS] Droplet successfully powered down. Threat neutralized.\n")
        return jsonify({"status": "success", "message": "Droplet killed"}), 200
    else:
        print(f"[ERROR] Failed to kill droplet. API responded with status: {response.status_code}\n")
        return jsonify({"status": "error", "message": "Failed to kill droplet"}), 500

if __name__ == '__main__':
    # Running the Flask app on port 5000
    print("SOC Automator is running & listening for Datadog webhooks on port 5000...")
    app.run(port=5000)
```

> ⚠️ **WARNING: PROTECT YOUR API KEYS** > If you are replicating this project, **NEVER** hardcode your DigitalOcean API token directly into your scripts or commit it to GitHub. Leaked cloud credentials are scraped by botnets in seconds and will result in thousands of dollars in unauthorized compute charges. [This Microsoft report observed targeted organizations incurred more than **$300,000** in compute fees due to cryptojacking attacks](https://www.microsoft.com/en-us/security/blog/2023/07/25/cryptojacking-understanding-and-defending-against-cloud-compute-resource-abuse/). Gulp. 
> 
> Always use environment variables (like a `.env` file) to store your secrets locally.

![image](https://media.discordapp.net/attachments/1486889265991254076/1496315234632077464/Untitled_12.png?ex=69e96fa8&is=69e81e28&hm=453da62525faff5a2ee716e4e4507cd5d1102dc9a4a2e0adb7db7d7dd1c5f8f5&=&format=webp&quality=lossless)![image](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

Within just 12 hours of exposing the vulnerable Redis instance, a real botnet attacked. My pipeline worked as intended, moving from detection to neutralization.

1\. **Detection - The Threat is Active**
The Datadog Metric Monitor detected the anomaly. the user CPU usage spiked and held firm around 32% as the malware throttled its usage to blend in. 
![image](https://cdn.discordapp.com/attachments/1486889265991254076/1496316119009591296/image.png?ex=69e9707a&is=69e81efa&hm=19b59a145c9f743dc92ca94d3f36f70ce064fb67b9bc69ea9bb4958ed17f29da&)

I had set my anomaly detection % to 90%, so I moved it to 30% to trigger the auto-remediation script. Whilst doing this, I did a forensic hunt to see where the process was being hidden.


**2\. Hunting - Indicator Extraction (IOCs)**


![image](https://media.discordapp.net/attachments/1486889265991254076/1496322633501774024/image_1.webp?ex=69e9768c&is=69e8250c&hm=eb13aaf5e04ce8bd6444c043f58e375516470a1b90deb424072e693a07680ae4&=&format=webp)


* Looking at this screenshot from Datadog, you see that Process ID `59444` is running a massive Base64 obfuscated string `0DKgJzzdUj. . .` to bypass standard text-based process monitoring.
* I used the command `ls -l /proc/59444/exe` to track the malicious process to a temporary folder: `/tmp/0DKgJzzdUj`

![image](https://cdn.discordapp.com/attachments/1486889265991254076/1496324451766112357/image_7.png?ex=69e9783d&is=69e826bd&hm=bf21d776185e6be3119344d1d7ef3b48d550141ab2e8a4dcdd5e7849d1488928&)

The botnet decided to hide in the `tmp` folder as it offers a reliable, low-restriction area for storing and running malicious files without immediate user detection.

**3\. Verification - Packet Sniffing**
I used tcpdump for live packet analysis. The traffic was intense. The server was not *just* mining crypto; it was actively spreading. I caught the worm rapidly firing SYN packets to other vulnerable Redis instances ``(Port 6379)`` on the ``104.x.x.x`` subnet.
![image](https://media.discordapp.net/attachments/1486889265991254076/1496324255221285035/image.jpg?ex=69e9780e&is=69e8268e&hm=0f70f2524d9883e9c0bd4709b3f501af47173fcc0fd76bd7992c2684e778aaa0&=&format=webp)

**4\. Auto-Remediation: Result Verified**
The Datadog Metric Monitor (configured to threshold: 25%) triggered. The alert traveled the Ngrok tunnel, and the SOC Automator script received and validated the JSON payload.

As shown in the final architecture diagram and this terminal screenshot, the kill switch successfully activated, transmitting the `power_off` API call to DigitalOcean and neutralizing the threat. The mean-time-to-respond was measured in minutes, successfully containing the malware and severing all command-and-control (C2) communication.

![image](https://media.discordapp.net/attachments/1486889265991254076/1487150220138516560/image.png?ex=69e90d92&is=69e7bc12&hm=887fb454d39c78e98fb7622db434558f23c061d4f5e94b285a64e12565c49268&=&format=webp&quality=lossless)
