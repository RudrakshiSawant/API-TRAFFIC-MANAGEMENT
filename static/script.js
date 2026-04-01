async function fetchStats() {
  const res = await fetch('/api/stats');
  const data = await res.json();

  const totalReceived = document.getElementById('total_received');
  const totalAllowed = document.getElementById('total_allowed');
  const totalBlocked = document.getElementById('total_blocked');
  const unhealthyServices = document.getElementById('unhealthy_services');

  if (totalReceived) totalReceived.innerText = data.total_received;
  if (totalAllowed) totalAllowed.innerText = data.total_allowed;
  if (totalBlocked) totalBlocked.innerText = data.total_blocked;
  if (unhealthyServices) unhealthyServices.innerText = data.unhealthy_services;

  const dashboardServices = document.getElementById('dashboardServices');
  const serviceCards = document.getElementById('serviceCards');

  if (dashboardServices || serviceCards) {
    const target = dashboardServices || serviceCards;
    target.innerHTML = '';

    for (const [service, stats] of Object.entries(data.service_usage)) {
      let healthClass = '';
      let healthColor = 'green';

      if (stats.health === 'Degraded') {
        healthClass = 'degraded';
        healthColor = 'yellow';
      } else if (stats.health === 'Unhealthy') {
        healthClass = 'unhealthy';
        healthColor = 'red';
      }

      target.innerHTML += `
        <div class="service-card ${healthClass}">
          <h4>${service}</h4>
          <div class="service-meta">
            <div><strong>Status:</strong> <span class="${healthColor}">${stats.health}</span></div>
            <div><strong>Total Received:</strong> ${stats.received}</div>
            <div><strong>Allowed:</strong> ${stats.allowed}</div>
            <div><strong>Blocked:</strong> ${stats.blocked}</div>
            <div><strong>Overload Score:</strong> ${stats.overload_score}</div>
            <div><strong>Last Activity:</strong> ${stats.last_activity}</div>
          </div>
        </div>
      `;
    }
  }
}

async function fetchLogs() {
  const res = await fetch('/api/logs');
  const logs = await res.json();

  const logsTable = document.getElementById('logsTable');
  const timelineBox = document.getElementById('timelineBox');

  if (logsTable) logsTable.innerHTML = '';
  if (timelineBox) timelineBox.innerHTML = '';

  logs.forEach(log => {
    let healthColor = 'green';
    if (log.health === 'Degraded') healthColor = 'yellow';
    if (log.health === 'Unhealthy') healthColor = 'red';

    if (logsTable) {
      logsTable.innerHTML += `
        <tr>
          <td>${log.time}</td>
          <td>${log.service}</td>
          <td>${log.traffic_type}</td>
          <td>${log.requests}</td>
          <td class="green">${log.allowed}</td>
          <td class="red">${log.blocked}</td>
          <td class="${healthColor}">${log.health}</td>
          <td>${log.decision}</td>
        </tr>
      `;
    }

    if (timelineBox) {
      timelineBox.innerHTML += `
        <div class="timeline-item">
          <div class="time">${log.time}</div>
          <div class="event">
            <strong>${log.service}</strong> received <strong>${log.requests}</strong> ${log.traffic_type.toLowerCase()} request(s).
            <span class="green">${log.allowed} allowed</span>,
            <span class="red">${log.blocked} blocked</span>.
            Current health: <span class="${healthColor}">${log.health}</span>.
          </div>
        </div>
      `;
    }
  });

  if (timelineBox && logs.length === 0) {
    timelineBox.innerHTML = `
      <div class="timeline-item">
        <div class="time">No Events Yet</div>
        <div class="event">Traffic activity will appear here once simulation begins.</div>
      </div>
    `;
  }
}

function animateFlow() {
  const nodes = ["node-client", "node-filter", "node-rule", "node-backend"];
  nodes.forEach(id => document.getElementById(id).classList.remove("active-flow"));

  let index = 0;
  const interval = setInterval(() => {
    if (index > 0) {
      document.getElementById(nodes[index - 1]).classList.remove("active-flow");
    }
    if (index < nodes.length) {
      document.getElementById(nodes[index]).classList.add("active-flow");
      index++;
    } else {
      clearInterval(interval);
    }
  }, 400);
}

async function simulateTraffic() {
  const service = document.getElementById('service').value;
  const traffic_type = document.getElementById('traffic_type').value;
  const request_count = parseInt(document.getElementById('request_count').value);

  document.getElementById('backendServiceName').innerText = service;
  document.getElementById('clientRequests').innerText = request_count;
  document.getElementById('filterRequests').innerText = request_count;
  document.getElementById('ruleRequests').innerText = request_count;
  document.getElementById('backendRequests').innerText = '...';

  animateFlow();

  document.getElementById('apiOutputBox').innerHTML = `
    <div><span class="terminal-prompt">></span> Fetching backend API response...</div>
  `;

  document.getElementById('resultBox').innerHTML = `
    <div><span class="terminal-prompt">></span> Incoming traffic received...</div>
    <div><span class="terminal-prompt">></span> Initializing traffic analysis...</div>
  `;

  const simulationRes = await fetch('/simulate_traffic', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ service, traffic_type, request_count })
  });

  const simulationData = await simulationRes.json();

  let apiResponse = null;

  if (simulationData.allowed_requests > 0) {
    const apiRes = await fetch(simulationData.service_endpoint);
    apiResponse = await apiRes.json();
    document.getElementById('backendRequests').innerText = simulationData.allowed_requests;
  } else {
    document.getElementById('backendRequests').innerText = 0;
  }

  let healthClass = 'green';
  if (simulationData.health === 'Degraded') healthClass = 'yellow';
  if (simulationData.health === 'Unhealthy') healthClass = 'red';

  if (apiResponse) {
    document.getElementById('apiOutputBox').innerHTML = `
      <pre>${JSON.stringify(apiResponse, null, 2)}</pre>
    `;
  } else {
    document.getElementById('apiOutputBox').innerHTML = `
      <div><span class="terminal-prompt">></span> API execution blocked.</div>
      <div><span class="terminal-prompt">></span> No backend response generated.</div>
    `;
  }

  document.getElementById('resultBox').innerHTML = `
    <div><span class="terminal-prompt">></span> Incoming traffic received...</div>
    <div><span class="terminal-prompt">></span> Service selected: <span class="terminal-info">${simulationData.service}</span></div>
    <div><span class="terminal-prompt">></span> Endpoint mapped: <span class="terminal-info">${simulationData.service_endpoint}</span></div>
    <div><span class="terminal-prompt">></span> Traffic type: <span class="terminal-info">${simulationData.traffic_type}</span></div>
    <div><span class="terminal-prompt">></span> Requests received: <span class="terminal-info">${simulationData.requests_sent}</span></div>
    <div><span class="terminal-prompt">></span> Applying traffic control rules...</div>
    <div><span class="terminal-prompt">></span> Allowed requests: <span class="green">${simulationData.allowed_requests}</span></div>
    <div><span class="terminal-prompt">></span> Blocked requests: <span class="red">${simulationData.blocked_requests}</span></div>
    <div><span class="terminal-prompt">></span> Current service health: <span class="${healthClass}">${simulationData.health}</span></div>
    <div><span class="terminal-prompt">></span> Decision: <span class="terminal-info">${simulationData.decision}</span></div>
    <div><span class="terminal-prompt">></span> Timestamp: <span class="terminal-info">${simulationData.timestamp}</span></div>
  `;

  fetchStats();
  fetchLogs();
  fetchAlerts();

}

async function resetSystem() {
  await fetch('/api/reset', { method: 'POST' });
  alert('System reset successful.');
  window.location.reload();
}

document.addEventListener('DOMContentLoaded', () => {
  if (typeof fetchStats === "function") fetchStats();
  if (typeof fetchLogs === "function") fetchLogs();
  fetchAlerts();
});

// -------------------------------
// Alerts Fetch
// -------------------------------
async function fetchAlerts() {
  try {
    const res = await fetch('/api/alerts');
    const alerts = await res.json();

    const alertDot = document.getElementById('alertDot');
    const simulatorAlertBox = document.getElementById('simulatorAlertBox');
    const simulatorAlertText = document.getElementById('simulatorAlertText');
    const alertsContainer = document.getElementById('alertsContainer');

    // Sidebar red dot
    if (alertDot) {
      if (alerts.length > 0) {
        alertDot.classList.remove('hidden');
      } else {
        alertDot.classList.add('hidden');
      }
    }

    // Simulator alert banner
    if (simulatorAlertBox && simulatorAlertText) {
      if (alerts.length > 0) {
        simulatorAlertBox.classList.remove('hidden');

        const highest = alerts.find(a => a.severity === "critical") || alerts[0];

        simulatorAlertText.innerText = highest.message;

        simulatorAlertBox.classList.remove('warning-alert', 'critical-alert');
        simulatorAlertBox.classList.add(
          highest.severity === "critical" ? 'critical-alert' : 'warning-alert'
        );
      } else {
        simulatorAlertBox.classList.add('hidden');
      }
    }

    // Alerts page content
    if (alertsContainer) {
      if (alerts.length === 0) {
        alertsContainer.innerHTML = `
          <div class="empty-state">No active alerts. All services are operating normally.</div>
        `;
      } else {
        alertsContainer.innerHTML = '';

        alerts.forEach(alert => {
          alertsContainer.innerHTML += `
            <div class="alert-card ${alert.severity}">
              <div class="alert-title">${alert.service}</div>
              <div class="alert-message">${alert.message}</div>
            </div>
          `;
        });
      }
    }
  } catch (error) {
    console.error("Error fetching alerts:", error);
  }
}
