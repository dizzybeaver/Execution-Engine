#!/usr/bin/env python3
"""CloudWatch Dashboard Configuration for LEE
Creates a Lambda observability dashboard programmatically
"""

import json
import os

import boto3

from lee.lee_config.constants import (
    CLOUDWATCH_LONG_PERIOD,
    CLOUDWATCH_SHORT_PERIOD,
)


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


# Dashboard configuration
DASHBOARD_NAME = "LEE-Observability"

def get_dashboard_body() -> str:
    """Returns the dashboard JSON definition.

    Dashboard widgets:
    1. Lambda Invocation Count (Total + Errors)
    2. Lambda Latency (P50, P95, P99)
    3. Anomaly Detection Alerts
    4. Home Assistant API Health
    5. Cache Performance
    6. Circuit Breaker Status
    """
    widgets = []

    # Widget 1: Lambda Invocation Count
    widgets.append({
        "type": "metric",
        "x": 0,
        "y": 0,
        "width": 12,
        "height": 6,
        "properties": {
            "metrics": [
                ["LEE/Lambda", "InvocationCount", "Function", "lambda_handler", {"stat": "Sum", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Total Invocations"}],
                ["LEE/Lambda", "InvocationCount", "Function", "lambda_handler", {"label": "Errors"}],
            ],
            "period": CLOUDWATCH_LONG_PERIOD,
            "stat": "Sum",
            "region": "us-east-1",
            "title": "Lambda Invocations (5 min)",
            "view": "timeSeries",
            "stacked": False,
        },
    })

    # Widget 2: Lambda Latency Percentiles
    widgets.append({
        "type": "metric",
        "x": 0,
        "y": 6,
        "width": 12,
        "height": 6,
        "properties": {
            "metrics": [
                ["LEE/Lambda", "Latency", "Function", "lambda_handler", {"stat": "p50", "period": CLOUDWATCH_SHORT_PERIOD, "label": "P50"}],
                ["LEE/Lambda", "Latency", "Function", "lambda_handler", {"stat": "p95", "period": CLOUDWATCH_SHORT_PERIOD, "label": "P95"}],
                ["LEE/Lambda", "Latency", "Function", "lambda_handler", {"stat": "p99", "period": CLOUDWATCH_SHORT_PERIOD, "label": "P99"}],
            ],
            "period": CLOUDWATCH_LONG_PERIOD,
            "stat": "Average",
            "region": "us-east-1",
            "title": "Lambda Latency Percentiles (5 min)",
            "view": "timeSeries",
        },
    })

    # Widget 3: Anomaly Detection Alerts
    widgets.append({
        "type": "metric",
        "x": 0,
        "y": 12,
        "width": 12,
        "height": 6,
        "properties": {
            "metrics": [
                ["LEE/Anomaly", "AnomalyDetected", {"stat": "Sum", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Anomalies"}],
                ["LEE/Anomaly", "AnomalyScore", {"stat": "Average", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Avg Score"}],
            ],
            "period": CLOUDWATCH_LONG_PERIOD,
            "region": "us-east-1",
            "title": "Anomaly Detection",
            "view": "timeSeries",
        },
    })

    # Widget 4: Home Assistant Health
    widgets.append({
        "type": "metric",
        "x": 0,
        "y": 18,
        "width": 12,
        "height": 6,
        "properties": {
            "metrics": [
                ["LEE/Health", "HAConnectivity", {"stat": "Average", "period": CLOUDWATCH_SHORT_PERIOD, "label": "HA Connectivity"}],
                ["LEE/Health", "CircuitBreakerTripped", {"stat": "Sum", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Circuit Breaker Trips"}],
            ],
            "period": CLOUDWATCH_LONG_PERIOD,
            "region": "us-east-1",
            "title": "Home Assistant Health",
            "view": "timeSeries",
        },
    })

    # Widget 5: Cache Performance
    widgets.append({
        "type": "metric",
        "x": 0,
        "y": 24,
        "width": 12,
        "height": 6,
        "properties": {
            "metrics": [
                ["LEE/Cache", "CacheHit", {"stat": "Sum", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Hits"}],
                ["LEE/Cache", "CacheMiss", {"stat": "Sum", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Misses"}],
            ],
            "period": CLOUDWATCH_LONG_PERIOD,
            "region": "us-east-1",
            "title": "Cache Performance",
            "view": "timeSeries",
            "stacked": True,
        },
    })

    # Widget 6: Error Rate
    widgets.append({
        "type": "metric",
        "x": 12,
        "y": 0,
        "width": 12,
        "height": 6,
        "properties": {
            "metrics": [
                ["LEE/Lambda", "Error", {"stat": "Sum", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Errors"}],
            ],
            "period": CLOUDWATCH_LONG_PERIOD,
            "region": "us-east-1",
            "title": "Error Rate",
            "view": "timeSeries",
            "yAxis": {"left": {"min": 0}},
        },
    })

    # Widget 7: Dropped Metrics (if rate limiting occurs)
    widgets.append({
        "type": "metric",
        "x": 12,
        "y": 6,
        "width": 12,
        "height": 6,
        "properties": {
            "metrics": [
                ["LEE/Internal", "DroppedMetrics", {"stat": "Sum", "period": CLOUDWATCH_SHORT_PERIOD, "label": "Metrics Dropped"}],
            ],
            "period": CLOUDWATCH_LONG_PERIOD,
            "region": "us-east-1",
            "title": "Dropped Metrics (Rate Limiting)",
            "view": "timeSeries",
        },
    })

    # Widget 8: Log Events (text widget with info)
    widgets.append({
        "type": "text",
        "x": 12,
        "y": 12,
        "width": 12,
        "height": 6,
        "properties": {
            "markdown": """
            **LEE Lambda Observability Dashboard**

            **What to watch for:**
            - [GREEN] **Latency Spikes**: P95 > 500ms indicates issues
            - [YELLOW] **Anomaly Spikes**: >5 anomalies/minute = investigate
            - [RED] **Errors**: Any errors need immediate attention
            - [ORANGE] **Cache Miss**: >50% miss rate = review caching strategy

            **Typical healthy values:**
            - P50 Latency: 100-200ms
            - P95 Latency: 200-400ms
            - P99 Latency: 300-600ms
            - Cache Hit Rate: >70%
            - Anomalies: <5 per hour
            """,
        },
    })

    return json.dumps({"widgets": widgets})


def create_dashboard() -> dict:
    """Creates or updates the CloudWatch dashboard.

    Returns:
        Dict: AWS response

    """
    cloudwatch = boto3.client("cloudwatch")

    dashboard_body = get_dashboard_body()

    try:
        response = cloudwatch.put_dashboard(
            DashboardName=DASHBOARD_NAME,
            DashboardBody=dashboard_body,
        )

        return {
            "success": True,
            "dashboard_url": f"https://console.aws.amazon.com/cloudwatch/home?region={boto3.session.Session().region_name}#dashboards:name={DASHBOARD_NAME}",
            "response": response,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - AWS unavailable
        return {
            "success": False,
            "error": str(e),
        }
    except (boto3.exceptions.BotoCoreError, boto3.exceptions.ClientError) as e:
        # AWS-specific errors
        return {
            "success": False,
            "error": str(e),
        }


def delete_dashboard() -> dict:
    """Deletes the CloudWatch dashboard.

    Returns:
        Dict: AWS response

    """
    cloudwatch = boto3.client("cloudwatch")

    try:
        response = cloudwatch.delete_dashboards(
            DashboardNames=[DASHBOARD_NAME],
        )

        return {
            "success": True,
            "response": response,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - AWS unavailable
        return {
            "success": False,
            "error": str(e),
        }
    except (boto3.exceptions.BotoCoreError, boto3.exceptions.ClientError) as e:
        # AWS-specific errors
        return {
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Create the dashboard
    result = create_dashboard()

    if result["success"]:
        if _is_debug_mode():
            print("[OK] Dashboard created successfully!")
            print(f"[LINK] View at: {result['dashboard_url']}")
    else:
        if _is_debug_mode():
            print(f"[ERROR] Failed to create dashboard: {result['error']}")
