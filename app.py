import json
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, Response
from werkzeug.utils import secure_filename
import os
import subprocess
import platform
import socket
import psutil
import threading
import queue
import datetime
import sqlite3
from flask_sqlalchemy import SQLAlchemy

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
CONVERTED_FOLDER = os.path.join(os.path.dirname(__file__), 'converted')
ALLOWED_EXTENSIONS = {'onnx'}
DB_PATH = os.path.join(os.path.dirname(__file__), 'file_infos.db')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

conversion_queues = {}

app = Flask(__name__)
app.secret_key = 'rknn_secret_key'

# SQLAlchemy DB config from environment or default
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.environ.get('DB_USER', 'rknn')}:"
    f"{os.environ.get('DB_PASSWORD', 'rknnpass')}@"
    f"{os.environ.get('DB_HOST', 'localhost')}/"
    f"{os.environ.get('DB_NAME', 'rknnwebui')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class FileInfo(db.Model):
    __tablename__ = 'file_infos'
    filename = db.Column(db.String(255), primary_key=True)
    platform = db.Column(db.String(32))
    model_type = db.Column(db.String(16))
    created = db.Column(db.String(32))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Add more fields as needed

with app.app_context():
    db.create_all()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS file_infos (
        filename TEXT PRIMARY KEY,
        platform TEXT,
        model_type TEXT,
        created TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def save_file_info(filename, platform, model_type, created):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('REPLACE INTO file_infos (filename, platform, model_type, created) VALUES (?, ?, ?, ?)',
              (filename, platform, model_type, created))
    conn.commit()
    conn.close()

def get_file_info(filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT platform, model_type, created FROM file_infos WHERE filename=?', (filename,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'platform': row[0], 'model_type': row[1], 'created': row[2]}
    return None

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

global_config = load_config()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_ip():
    # Try to get a real external IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'Unavailable'

def get_server_info():
    return {
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'system': platform.system(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'ip': get_ip(),
        'cpu_count': psutil.cpu_count(),
        'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'disk_space_gb': round(psutil.disk_usage('/').free / (1024**3), 2),
        'disk_usage_percent': round(psutil.disk_usage('/').percent, 2)
    }

def stream_convert_log(task_id):
    q = conversion_queues.get(task_id)
    if not q:
        yield 'data: ERROR: No log queue found.\n\n'
        return
    while True:
        line = q.get()
        if line is None:
            break
        yield f'data: {line}\n\n'

@app.route('/convert_stream/<task_id>')
def convert_stream(task_id):
    return Response(stream_convert_log(task_id), mimetype='text/event-stream')

def run_conversion(cmd, q):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in proc.stdout:
        q.put(line.rstrip())
    proc.wait()
    q.put(None)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', config=global_config)

@app.route('/settings', methods=['GET'])
def settings():
    server_info = get_server_info() if global_config.get('show_server_info', True) else None
    # Determine current theme from config and/or localStorage (for display only)
    current_theme = global_config.get('default_theme', 'light')
    return render_template('settings.html', config=global_config, saved=False, server_info=server_info, current_theme=current_theme)

@app.route('/export', methods=['GET', 'POST'])
def export():
    message = None
    task_id = None
    platforms = ['rk3562', 'rk3566', 'rk3568', 'rk3576', 'rk3588', 'rv1126b']
    default_platform = global_config.get('default_platform', '')
    # Check for running conversions if parallel not allowed
    if not global_config.get('allow_parallel_conversions', False):
        for q in conversion_queues.values():
            if q and not q.empty():
                message = 'A conversion is already running. Please wait until it finishes.'
                return render_template('export.html', config=global_config, message=message, platforms=platforms, task_id=None, default_platform=default_platform)
    if request.method == 'POST':
        if 'model_file' not in request.files:
            message = 'No file part'
        else:
            file = request.files['model_file']
            if file.filename == '':
                message = 'No selected file'
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(upload_path)
                # Use global default_platform if set and no platform selected
                platform_ = request.form.get('platform') or default_platform or 'rk3576'
                dtype = request.form.get('dtype', 'fp')
                output_name = filename.rsplit('.', 1)[0] + f'_{platform_}_{dtype}.rknn'
                output_path = os.path.join(CONVERTED_FOLDER, output_name)
                # Save file info to SQLite DB
                save_file_info(output_name, platform_, dtype, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                cmd = [
                    'python3', 'convert.py',
                    upload_path, platform_, dtype, output_path
                ]
                import uuid
                task_id = str(uuid.uuid4())
                q = queue.Queue()
                conversion_queues[task_id] = q
                t = threading.Thread(target=run_conversion, args=(cmd, q), daemon=True)
                t.start()
                message = f'Conversion started. Log will appear below.'
                # Return a minimal HTML with the task_id for AJAX
                return f'<input type="hidden" id="task_id" name="task_id" value="{task_id}">'  # Only task_id for JS
            else:
                message = 'Invalid file type. Only .onnx files allowed.'
    return render_template('export.html', config=global_config, message=message, platforms=platforms, task_id=task_id, default_platform=default_platform)

@app.route('/files', methods=['GET'])
def files():
    uploaded = os.listdir(UPLOAD_FOLDER)
    converted = os.listdir(CONVERTED_FOLDER)
    # Additional information for RKNN models (from filename or metadata file, here as example dummy parsing)
    def parse_rknn_info(fname):
        # Robust: Search for known platform and model type in the name
        platforms = ['rk3562', 'rk3566', 'rk3568', 'rk3576', 'rk3588', 'rv1126b']
        model_types = ['fp', 'i8', 'u8']
        platform = '-'
        model_type = '-'
        for p in platforms:
            if p in fname:
                platform = p
                break
        for t in model_types:
            if f'_{t}' in fname or fname.endswith(f'_{t}.rknn'):
                model_type = t
                break
        return platform, model_type

    def file_info(folder, fname, is_converted=False):
        try:
            path = os.path.join(folder, fname)
            stat = os.stat(path)
            dt = datetime.datetime.fromtimestamp(stat.st_mtime)
            info = dt.strftime('%Y-%m-%d %H:%M')
            if is_converted:
                meta = get_file_info(fname)
                if meta:
                    platform = meta.get('platform', '-')
                    model_type = meta.get('model_type', '-')
                    created = meta.get('created', info)
                    return f"Converted: {created} | Platform: {platform} | Model Type: {model_type}"
                else:
                    platform, model_type = parse_rknn_info(fname)
                    return f"Converted: {info} | Platform: {platform} | Model Type: {model_type}"
            else:
                return f"Uploaded: {info}"
        except Exception:
            return ''
    uploaded_infos = {f: file_info(UPLOAD_FOLDER, f) for f in uploaded}
    converted_infos = {f: file_info(CONVERTED_FOLDER, f, is_converted=True) for f in converted}
    return render_template('files.html', config=global_config, uploaded=uploaded, converted=converted, uploaded_infos=uploaded_infos, converted_infos=converted_infos)

@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    if folder == 'uploads':
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    elif folder == 'converted':
        return send_from_directory(CONVERTED_FOLDER, filename, as_attachment=True)
    else:
        return 'Invalid folder', 404

@app.route('/delete/<folder>/<filename>', methods=['POST'])
def delete_file(folder, filename):
    if folder == 'uploads':
        path = os.path.join(UPLOAD_FOLDER, filename)
    elif folder == 'converted':
        path = os.path.join(CONVERTED_FOLDER, filename)
    else:
        return 'Invalid folder', 404
    if os.path.exists(path):
        os.remove(path)
        flash(f'{filename} deleted.')
    return redirect(url_for('files'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
