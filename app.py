from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime

app = Flask(__name__)

# -------------------------------
# Rate Limiting Configuration
# -------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

# -------------------------------
# Logging Configuration
# -------------------------------
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------------------
# Request Validation + Logging
# -------------------------------
@app.before_request
def validate_and_log_request():
    allowed_paths = ['/api/data', '/health']

    # Request validation
    if request.path not in allowed_paths:
        logging.warning(f"Invalid endpoint access from IP: {request.remote_addr} -> {request.path}")
        return jsonify({"error": "Invalid endpoint"}), 404

    # Request logging
    logging.info(
        f"IP: {request.remote_addr}, Endpoint: {request.path}, Method: {request.method}"
    )

# -------------------------------
# API Endpoint
# -------------------------------
@app.route('/api/data', methods=['GET'])
@limiter.limit("10 per minute")
def get_data():
    return jsonify({
        "message": "API Traffic Management System is working successfully",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success"
    })

# -------------------------------
# Health Check Endpoint
# -------------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running"
    })

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == '__main__':
    print("Containerized API Traffic Management System is running...")
    print("Open: http://127.0.0.1:5000/health")
    print("Open: http://127.0.0.1:5000/api/data")
    app.run(host='0.0.0.0', port=5000)
