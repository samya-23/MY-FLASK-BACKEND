from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from generate_pdf import create_pdf
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS

VISITOR_DATA_FILE = 'visitors.json'
PDF_DIR = 'static/pdfs'

# Endpoint to receive form data
@app.route('/api/messages', methods=['POST'])
def receive_visitor():
    try:
        data = request.get_json(force=True)

        if not all(k in data for k in ('name', 'email', 'phone')):
            return jsonify({'success': False, 'message': 'Missing fields'}), 400

        # Add timestamp
        data['timestamp'] = datetime.utcnow().isoformat()

        # Ensure the data file exists
        if not os.path.exists(VISITOR_DATA_FILE):
            with open(VISITOR_DATA_FILE, 'w') as f:
                json.dump([], f)

        # Append new visitor
        with open(VISITOR_DATA_FILE, 'r+') as f:
            existing = json.load(f)
            existing.append(data)
            f.seek(0)
            json.dump(existing, f, indent=4)
            f.truncate()

        # Generate PDF
        filename = create_pdf(data)

        return jsonify({'success': True, 'pdf': filename})

    except Exception as e:
        print("Error in /api/messages:", e)
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

# Endpoint to download latest PDF
@app.route('/api/download-pdf', methods=['GET'])
def download_pdf():
    try:
        if not os.path.exists(PDF_DIR):
            return jsonify({'success': False, 'message': 'PDF directory not found'}), 404

        files = sorted(os.listdir(PDF_DIR))
        if not files:
            return jsonify({'success': False, 'message': 'No PDF available'}), 404

        latest_pdf = files[-1]
        return send_file(os.path.join(PDF_DIR, latest_pdf), as_attachment=True)

    except Exception as e:
        print("Error in /api/download-pdf:", e)
        return jsonify({'success': False, 'message': 'Could not download PDF'}), 500

# ✅ New route to serve all visitor data
@app.route('/api/visitors', methods=['GET'])
def get_visitors():
    try:
        if not os.path.exists(VISITOR_DATA_FILE):
            return jsonify([])

        with open(VISITOR_DATA_FILE, 'r') as f:
            visitors = json.load(f)
        return jsonify(visitors)

    except Exception as e:
        print("Error in /api/visitors:", e)
        return jsonify({'success': False, 'message': 'Error fetching data'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

