"""Dashboard HTML Template.

This module contains the HTML template for the EE Universal Gateway Dashboard.
Extracted from dashboard_handler.py to meet SIMA file size limits.

**Version:** 1.0.0
**Date:** 2026-01-01
**Purpose:** Dashboard HTML template
**Type:** Template
"""

from __future__ import annotations

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>EE Universal Gateway Dashboard</title>
<style>
    body {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        display: flex;
        height: 100vh;
        overflow: hidden;
        background: #f5f5f5;
    }
    #sidebar {
        width: 280px;
        background: #2c3e50;
        color: #ecf0f1;
        padding: 20px;
        overflow-y: auto;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    #sidebar h2 {
        margin-top: 0;
        font-size: 1.5em;
        border-bottom: 2px solid #34495e;
        padding-bottom: 10px;
    }
    #sidebar .domain {
        margin: 8px 0;
        cursor: pointer;
        padding: 10px;
        border-radius: 6px;
        transition: background 0.2s;
        font-weight: 500;
    }
    #sidebar .domain:hover {
        background: #34495e;
    }
    #sidebar .domain.selected {
        background: #27ae60;
    }
    #main {
        flex: 1;
        padding: 30px;
        overflow-y: auto;
    }
    #main h1 {
        color: #2c3e50;
        margin-top: 0;
    }
    #main h2 {
        color: #34495e;
        border-bottom: 2px solid #bdc3c7;
        padding-bottom: 8px;
    }
    #main h3 {
        color: #7f8c8d;
    }
    .route-item {
        background: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 6px;
        cursor: pointer;
        border-left: 4px solid #3498db;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .route-item:hover {
        background: #ecf0f1;
        border-left-color: #2980b9;
        transform: translateX(4px);
    }
    .route-item.selected {
        background: #d5dbdb;
        border-left-color: #27ae60;
    }
    pre {
        background: #2c3e50;
        color: #ecf0f1;
        padding: 15px;
        border-radius: 6px;
        overflow-x: auto;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.9em;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    textarea {
        width: 100%;
        height: 150px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        padding: 12px;
        border: 2px solid #bdc3c7;
        border-radius: 6px;
        font-size: 0.9em;
        resize: vertical;
        background: white;
        transition: border-color 0.2s;
    }
    textarea:focus {
        outline: none;
        border-color: #3498db;
    }
    button {
        padding: 12px 24px;
        margin-top: 15px;
        cursor: pointer;
        background: #3498db;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 1em;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    button:hover {
        background: #2980b9;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    button:active {
        transform: translateY(0);
    }
    .info-box {
        background: #d5f4e6;
        border-left: 4px solid #27ae60;
        padding: 15px;
        border-radius: 6px;
        margin: 15px 0;
    }
    .error-box {
        background: #fadbd8;
        border-left: 4px solid #e74c3c;
        padding: 15px;
        border-radius: 6px;
        margin: 15px 0;
    }
</style>
</head>
<body>

<div id="sidebar">
    <h2>Gateway Domains</h2>
    <div id="domain-list"></div>
</div>

<div id="main">
    <h1>EE Universal Gateway Dashboard</h1>
    <p class="info-box">Interactive web interface for EE Universal Gateway operations. Select a domain to view routes and execute commands.</p>

    <h2 id="selected-domain">No domain selected</h2>

    <h3>Available Routes</h3>
    <div id="route-list"></div>

    <h3>Request Payload</h3>
    <textarea id="payload" placeholder="Enter JSON payload, e.g., {&#34;key&#34;: &#34;value&#34;}">{}</textarea>

    <button onclick="executeRoute()">Execute Route</button>

    <h3>Response</h3>
    <pre id="result">Select a domain and route to execute...</pre>
</div>

<script>
let selectedDomain = null;
let selectedRoute = null;

async function loadDomains() {
    try {
        const res = await fetch('/list-domains');
        const data = await res.json();
        const domains = data.data || data;
        const container = document.getElementById('domain-list');
        container.innerHTML = '';

        domains.forEach(domain => {
            const div = document.createElement('div');
            div.className = 'domain';
            div.textContent = domain;
            div.onclick = () => loadDomain(domain);
            container.appendChild(div);
        });
    } catch (error) {
        document.getElementById('result').textContent = 'Error loading domains: ' + error.message;
    }
}

async function loadDomain(domain) {
    selectedDomain = domain;
    selectedRoute = null;
    document.getElementById('selected-domain').textContent = domain;

    // Update sidebar selection
    document.querySelectorAll('.domain').forEach(el => {
        el.classList.remove('selected');
        if (el.textContent === domain) {
            el.classList.add('selected');
        }
    });

    try {
        const res = await fetch('/list-routes');
        const data = await res.json();
        const allRoutes = data.data || data;
        const routes = allRoutes[domain] || {};

        const container = document.getElementById('route-list');
        container.innerHTML = '';

        if (Object.keys(routes).length === 0) {
            container.innerHTML = '<p style="color: #95a5a6;">No routes available</p>';
            return;
        }

        Object.keys(routes).forEach(route => {
            const div = document.createElement('div');
            div.className = 'route-item';
            div.innerHTML = `<strong>${domain}.${route}</strong>`;
            div.onclick = () => selectRoute(route, div);
            container.appendChild(div);
        });
    } catch (error) {
        document.getElementById('result').textContent = 'Error loading routes: ' + error.message;
    }
}

function selectRoute(route, element) {
    selectedRoute = route;

    // Update route selection
    document.querySelectorAll('.route-item').forEach(el => {
        el.classList.remove('selected');
    });
    element.classList.add('selected');

    document.getElementById('result').textContent = `Selected route: ${selectedDomain}.${selectedRoute}\nReady to execute with current payload.`;
}

async function executeRoute() {
    if (!selectedDomain || !selectedRoute) {
        alert('Please select a domain and a route first');
        return;
    }

    let payload = {};
    try {
        const payloadText = document.getElementById('payload').value;
        if (payloadText.trim()) {
            payload = JSON.parse(payloadText);
        }
    } catch (e) {
        alert('Invalid JSON payload: ' + e.message);
        return;
    }

    const fullPath = selectedDomain + '.' + selectedRoute;

    try {
        document.getElementById('result').textContent = 'Executing...';

        const res = await fetch('/exec/' + fullPath, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        const result = await res.json();
        document.getElementById('result').textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        document.getElementById('result').textContent = 'Error: ' + error.message;
    }
}

// Load domains on page load
loadDomains();
</script>

</body>
</html>
"""
