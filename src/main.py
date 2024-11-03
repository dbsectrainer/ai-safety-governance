from flask import Flask, jsonify
from model_monitoring.monitoring import ModelMonitor
from model_monitoring.explainer import ModelExplainer
from security.threat_detection import ThreatDetector
from security.privacy_guard import PrivacyGuard

app = Flask(__name__)

# Initialize components
model_monitor = ModelMonitor()
model_explainer = ModelExplainer()
threat_detector = ThreatDetector()
privacy_guard = PrivacyGuard()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/monitor', methods=['GET'])
def get_monitoring_status():
    return jsonify(model_monitor.get_status())

@app.route('/explain/<model_id>', methods=['GET'])
def explain_model(model_id):
    return jsonify(model_explainer.explain(model_id))

@app.route('/security/scan', methods=['POST'])
def security_scan():
    return jsonify(threat_detector.scan())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
