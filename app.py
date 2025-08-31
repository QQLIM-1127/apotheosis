import os
import json
import time
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
DB_FILE = 'db.json'
ALLOWED_EXTENSIONS = {'json'}

app = Flask(__name__, static_url_path='', static_folder='.')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Initial Setup ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump({}, f)

# --- Database Helper Functions ---
def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Frontend Routes ---
@app.route('/')
def index():
    return app.send_static_file('index.html')

# --- API Endpoints ---

@app.route('/api/graphs', methods=['GET'])
def list_graphs():
    """
    The core endpoint to list and verify all tracked graphs.
    It checks file existence and modification times on every call.
    """
    db = load_db()
    graphs_to_remove = []
    
    for path, data in db.items():
        if not os.path.exists(path):
            data['status'] = 'missing'
            continue
        
        current_mtime = os.path.getmtime(path)
        if current_mtime > data.get('stored_mtime', 0):
            data['status'] = 'updated'
            data['display_mtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_mtime))
            # The stored_mtime is NOT updated here, so the banner persists until the user views it.
        
    # Sort entries: new/updated first, then by label
    sorted_graphs = sorted(
        db.items(), 
        key=lambda item: (
            {'new': 0, 'updated': 1}.get(item[1].get('status'), 2), # Priority sort
            item[1].get('label', item[0]) # Alphabetical sort
        )
    )
    
    # Prepare for JSON response
    response_data = [{'path': path, **data} for path, data in sorted_graphs]
    
    return jsonify(response_data)

@app.route('/api/graph-data', methods=['GET'])
def get_graph_data():
    """
    Securely serves graph file data. It will only serve files
    that are explicitly tracked in our database.
    """
    graph_path = request.args.get('path')
    if not graph_path:
        abort(400, 'Path parameter is required.')
        
    db = load_db()
    if graph_path not in db:
        abort(404, 'Graph not found in the database.')
        
    if not os.path.exists(graph_path):
        abort(404, 'Graph file does not exist at the specified path.')

    # After serving, we can update the status from 'new'/'updated' to 'normal'
    db[graph_path]['status'] = 'normal'
    db[graph_path]['stored_mtime'] = os.path.getmtime(graph_path)
    save_db(db)
        
    return send_file(graph_path, mimetype='application/json')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """ Handles new graph uploads, adding them to the `uploads` dir and DB. """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400
        
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    
    db = load_db()
    db[path] = {
        'label': filename,
        'status': 'new',
        'stored_mtime': os.path.getmtime(path)
    }
    save_db(db)
    
    return jsonify({"success": True, "path": path}), 201

# --- Local Service Endpoint ---

@app.route('/_localservice/add', methods=['POST'])
def localservice_add_graph():
    """
    An endpoint only accessible from localhost to programmatically
    add or update graph entries from any path on the local filesystem.
    """
    if request.remote_addr not in ('127.0.0.1', '::1'):
        abort(403, "This endpoint is only accessible from localhost.")
        
    data = request.get_json()
    path = data.get('path')
    label = data.get('label')
    
    if not path or not label:
        return jsonify({"error": "Both 'path' and 'label' are required."}), 400
        
    if not os.path.isfile(path):
        return jsonify({"error": f"Path does not exist or is not a file: {path}"}), 400

    db = load_db()
    
    entry = db.get(path, {})
    entry['label'] = label
    entry['status'] = 'updated' if path in db else 'new'
    entry['stored_mtime'] = os.path.getmtime(path)
    
    db[path] = entry
    save_db(db)
    
    return jsonify({"success": True, "message": f"Graph '{path}' was {entry['status']}."}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)