from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime
import csv
import io
import random

app = Flask(__name__)

TRAFFIC_RULES = {
    "Normal": 5,
    "Burst": 10,
    "Priority": 15
}

SERVICES = {
    "Auth Service": "/service/auth",
    "Data Service": "/service/data",
    "Analytics Service": "/service/analytics",
    "Notification Service": "/service/notification"
}

traffic_data = {
    "total_received": 0,
    "total_allowed": 0,
    "total_blocked": 0,
    "unhealthy_services": 0,
    "service_usage": {
        "Auth Service": {"received": 0, "allowed": 0, "blocked": 0, "last_activity": "-", "overload_score": 0, "health": "Healthy"},
        "Data Service": {"received": 0, "allowed": 0, "blocked": 0, "last_activity": "-", "overload_score": 0, "health": "Healthy"},
        "Analytics Service": {"received": 0, "allowed": 0, "blocked": 0, "last_activity": "-", "overload_score": 0, "health": "Healthy"},
        "Notification Service": {"received": 0, "allowed": 0, "blocked": 0, "last_activity": "-", "overload_score": 0, "health": "Healthy"}
    },
    "decision_logs": []
}

def add_log(service, traffic_type, request_count, allowed, blocked, decision, health):
    log = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "service": service,
        "traffic_type": traffic_type,
        "requests": request_count,
        "allowed": allowed,
        "blocked": blocked,
        "decision": decision,
        "health": health
    }
    traffic_data["decision_logs"].insert(0, log)

    if len(traffic_data["decision_logs"]) > 100:
        traffic_data["decision_logs"] = traffic_data["decision_logs"][:100]

def update_health(service):
    overload = traffic_data["service_usage"][service]["overload_score"]

    if overload >= 15:
        traffic_data["service_usage"][service]["health"] = "Unhealthy"
    elif overload >= 8:
        traffic_data["service_usage"][service]["health"] = "Degraded"
    else:
        traffic_data["service_usage"][service]["health"] = "Healthy"

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/simulator")
def simulator():
    return render_template("simulator.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/timeline")
def timeline():
    return render_template("timeline.html")

@app.route("/logs")
def logs_page():
    return render_template("logs.html")

@app.route("/service/auth")
def auth_service():
    return jsonify({
        "service": "Auth Service",
        "status": "success",
        "token": "abc123xyz",
        "user": "sample_user",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/service/data")
def data_service():
    return jsonify({
        "service": "Data Service",
        "status": "success",
        "records": [
            {"id": 101, "value": "Temperature Data"},
            {"id": 102, "value": "Sensor Metrics"}
        ],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/service/analytics")
def analytics_service():
    return jsonify({
        "service": "Analytics Service",
        "status": "success",
        "insight": "Traffic spike detected in API cluster",
        "prediction_score": round(random.uniform(0.75, 0.98), 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/service/notification")
def notification_service():
    return jsonify({
        "service": "Notification Service",
        "status": "success",
        "message": "Alert notification dispatched successfully",
        "channel": "Email/SMS",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/simulate_traffic", methods=["POST"])
def simulate_traffic():
    data = request.get_json()

    service = data.get("service")
    traffic_type = data.get("traffic_type")
    request_count = int(data.get("request_count"))

    if service not in SERVICES:
        return jsonify({"error": "Invalid service selected"}), 400

    if traffic_type not in TRAFFIC_RULES:
        return jsonify({"error": "Invalid traffic type selected"}), 400

    current_health = traffic_data["service_usage"][service]["health"]

    if current_health == "Unhealthy":
        allowed = 0
        blocked = request_count
        decision = "Traffic rejected completely because service is unhealthy"
    else:
        allowed_limit = TRAFFIC_RULES[traffic_type]
        allowed = min(request_count, allowed_limit)
        blocked = max(0, request_count - allowed_limit)

        if blocked > 0:
            decision = f"Traffic controlled: {blocked} request(s) blocked by rate policy"
        else:
            decision = "Traffic allowed successfully"

    traffic_data["total_received"] += request_count
    traffic_data["total_allowed"] += allowed
    traffic_data["total_blocked"] += blocked

    traffic_data["service_usage"][service]["received"] += request_count
    traffic_data["service_usage"][service]["allowed"] += allowed
    traffic_data["service_usage"][service]["blocked"] += blocked
    traffic_data["service_usage"][service]["last_activity"] = datetime.now().strftime("%H:%M:%S")

    if blocked > 0:
        traffic_data["service_usage"][service]["overload_score"] += 5
    else:
        traffic_data["service_usage"][service]["overload_score"] = max(
            0,
            traffic_data["service_usage"][service]["overload_score"] - 1
        )

    update_health(service)
    new_health = traffic_data["service_usage"][service]["health"]

    traffic_data["unhealthy_services"] = sum(
        1 for s in traffic_data["service_usage"]
        if traffic_data["service_usage"][s]["health"] == "Unhealthy"
    )

    add_log(service, traffic_type, request_count, allowed, blocked, decision, new_health)

    return jsonify({
        "service": service,
        "service_endpoint": SERVICES[service],
        "traffic_type": traffic_type,
        "requests_sent": request_count,
        "allowed_requests": allowed,
        "blocked_requests": blocked,
        "decision": decision,
        "health": new_health,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/stats")
def stats():
    return jsonify({
        "total_received": traffic_data["total_received"],
        "total_allowed": traffic_data["total_allowed"],
        "total_blocked": traffic_data["total_blocked"],
        "unhealthy_services": traffic_data["unhealthy_services"],
        "service_usage": traffic_data["service_usage"]
    })

@app.route("/api/logs")
def logs():
    return jsonify(traffic_data["decision_logs"])

@app.route("/api/rules")
def rules():
    return jsonify(TRAFFIC_RULES)

@app.route("/api/export_logs")
def export_logs():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Time", "Service", "Traffic Type", "Requests", "Allowed", "Blocked", "Health", "Decision"])

    for log in traffic_data["decision_logs"]:
        writer.writerow([
            log["time"],
            log["service"],
            log["traffic_type"],
            log["requests"],
            log["allowed"],
            log["blocked"],
            log["health"],
            log["decision"]
        ])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=traffic_decision_logs.csv"}
    )

@app.route("/api/reset", methods=["POST"])
def reset():
    traffic_data["total_received"] = 0
    traffic_data["total_allowed"] = 0
    traffic_data["total_blocked"] = 0
    traffic_data["unhealthy_services"] = 0
    traffic_data["decision_logs"].clear()

    for service in traffic_data["service_usage"]:
        traffic_data["service_usage"][service]["received"] = 0
        traffic_data["service_usage"][service]["allowed"] = 0
        traffic_data["service_usage"][service]["blocked"] = 0
        traffic_data["service_usage"][service]["last_activity"] = "-"
        traffic_data["service_usage"][service]["overload_score"] = 0
        traffic_data["service_usage"][service]["health"] = "Healthy"

    return jsonify({"message": "Dashboard reset successful"})

@app.route("/alerts")
def alerts_page():
    return render_template("alerts.html")

@app.route("/api/alerts")
def alerts():
    active_alerts = []

    for service, stats in traffic_data["service_usage"].items():
        if stats["health"] == "Degraded":
            active_alerts.append({
                "service": service,
                "severity": "warning",
                "message": f"{service} is degraded due to increasing blocked traffic follow the threshold."
            })
        elif stats["health"] == "Unhealthy":
            active_alerts.append({
                "service": service,
                "severity": "critical",
                "message": f"{service} is unhealthy and currently rejecting traffic try requesting after resetting."
            })

    return jsonify(active_alerts)

if __name__ == "__main__":
    app.run(debug=True)
