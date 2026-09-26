"""
Monitoring and metrics collection for FastAPI application
"""
import logging
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict
from config.monitoring_metrics import (
    record_request_metrics,
    record_error,
    update_active_plans
)

logger = logging.getLogger('monitoring')


class MetricsCollector:
    """Collect and aggregate metrics for API endpoints"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.duration_totals = defaultdict(float)
        self.duration_counts = defaultdict(int)
        self.status_codes = defaultdict(lambda: defaultdict(int))
    
    def record_request(
        self,
        path: str,
        method: str,
        status_code: int,
        duration_ms: float
    ):
        """Record a request metric
        
        Args:
            path: Request path (e.g., '/plan')
            method: HTTP method (e.g., 'POST')
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
        """
        key = f'{method} {path}'
        self.request_counts[key] += 1
        self.duration_totals[key] += duration_ms
        self.duration_counts[key] += 1
        self.status_codes[key][status_code] += 1
        
        # Record Prometheus metrics
        record_request_metrics(method, path, status_code, duration_ms)
        
        if status_code >= 400:
            self.error_counts[key] += 1
            error_type = "client_error" if status_code < 500 else "server_error"
            record_error(method, path, status_code, error_type)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all endpoints
        
        Returns:
            Dictionary with timestamp, totals, and per-endpoint metrics
        """
        endpoints = []
        
        for endpoint, count in self.request_counts.items():
            avg_duration = self.duration_totals[endpoint] / self.duration_counts[endpoint]
            error_count = self.error_counts[endpoint]
            
            endpoints.append({
                'endpoint': endpoint,
                'request_count': count,
                'error_count': error_count,
                'error_rate': (error_count / count * 100) if count > 0 else 0,
                'avg_duration_ms': round(avg_duration, 2),
                'status_codes': dict(self.status_codes[endpoint])
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_endpoints': len(endpoints),
            'total_requests': sum(self.request_counts.values()),
            'total_errors': sum(self.error_counts.values()),
            'endpoints': sorted(
                endpoints,
                key=lambda x: x['request_count'],
                reverse=True
            )
        }
    
    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get detailed stats for a specific endpoint"""
        if endpoint not in self.request_counts:
            return {}
        
        count = self.request_counts[endpoint]
        avg_duration = self.duration_totals[endpoint] / self.duration_counts[endpoint]
        error_count = self.error_counts[endpoint]
        
        return {
            'endpoint': endpoint,
            'total_requests': count,
            'error_count': error_count,
            'error_rate': (error_count / count * 100) if count > 0 else 0,
            'avg_duration_ms': round(avg_duration, 2),
            'min_duration_ms': min([
                self.duration_totals.get(endpoint, 0) / self.duration_counts.get(endpoint, 1)
            ]),
            'status_codes': dict(self.status_codes[endpoint])
        }
    
    def reset(self):
        """Reset all metrics"""
        self.request_counts.clear()
        self.error_counts.clear()
        self.duration_totals.clear()
        self.duration_counts.clear()
        self.status_codes.clear()


# Global metrics collector instance
metrics_collector = MetricsCollector()
