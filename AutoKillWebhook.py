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