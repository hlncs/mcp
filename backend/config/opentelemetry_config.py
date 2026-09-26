import logging
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

logger = logging.getLogger(__name__)

class OpenTelemetryConfig:
    """OpenTelemetry configuration and initialization"""
    
    def __init__(self, service_name: str = "event-planning-api", jaeger_host: str = "localhost", jaeger_port: int = 6831):
        self.service_name = service_name
        self.jaeger_host = jaeger_host
        self.jaeger_port = jaeger_port
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
    
    def initialize(self, app=None):
        """Initialize OpenTelemetry"""
        try:
            self._setup_tracing()
            self._setup_metrics()
            self._setup_instrumentation(app)
            logger.info("✅ OpenTelemetry initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenTelemetry: {e}")
    
    def _setup_tracing(self):
        """Setup distributed tracing with Jaeger"""
        try:
            # Create Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.jaeger_host,
                agent_port=self.jaeger_port,
            )
            
            # Create tracer provider
            self.tracer_provider = TracerProvider()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            logger.info(f"✅ Tracing setup complete (Jaeger: {self.jaeger_host}:{self.jaeger_port})")
        except Exception as e:
            logger.error(f"❌ Failed to setup tracing: {e}")
    
    def _setup_metrics(self):
        """Setup metrics with Prometheus"""
        try:
            # Create Prometheus metric reader
            prometheus_reader = PrometheusMetricReader()
            
            # Create meter provider
            self.meter_provider = MeterProvider(metric_readers=[prometheus_reader])
            
            # Set global meter provider
            metrics.set_meter_provider(self.meter_provider)
            
            logger.info("✅ Metrics setup complete")
        except Exception as e:
            logger.error(f"❌ Failed to setup metrics: {e}")
    
    def _setup_instrumentation(self, app=None):
        """Setup automatic instrumentation"""
        try:
            # FastAPI instrumentation
            if app:
                FastAPIInstrumentor.instrument_app(app)
            
            # HTTP client instrumentation
            RequestsInstrumentor().instrument()
            HTTPXClientInstrumentor().instrument()
            
            # Database instrumentation
            SQLAlchemyInstrumentor().instrument()
            AsyncPGInstrumentor().instrument()
            
            # Logging instrumentation
            LoggingInstrumentor().instrument()
            
            logger.info("✅ FastAPI instrumentation enabled")
            logger.info("✅ HTTP client instrumentation enabled")
            logger.info("✅ Logging instrumentation enabled")
        except Exception as e:
            logger.error(f"❌ Failed to setup instrumentation: {e}")

def init_otel(service_name: str = "event-planning-api") -> OpenTelemetryConfig:
    """Factory function to create and return OpenTelemetry config"""
    return OpenTelemetryConfig(service_name=service_name)