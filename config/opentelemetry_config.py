import os
from typing import Optional
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.api.metrics import set_meter_provider
from opentelemetry.api.trace import set_tracer_provider
import logging

logger = logging.getLogger('opentelemetry_config')

class OpenTelemetryConfig:
    """OpenTelemetry configuration and initialization"""
    
    def __init__(
        self,
        service_name: str = "event-planning-api",
        jaeger_host: str = os.getenv("JAEGER_HOST", "localhost"),
        jaeger_port: int = int(os.getenv("JAEGER_PORT", 6831)),
        otlp_endpoint: Optional[str] = os.getenv("OTLP_ENDPOINT"),
        prometheus_port: int = int(os.getenv("PROMETHEUS_PORT", 8001)),
        enabled: bool = os.getenv("OTEL_ENABLED", "true").lower() == "true"
    ):
        self.service_name = service_name
        self.jaeger_host = jaeger_host
        self.jaeger_port = jaeger_port
        self.otlp_endpoint = otlp_endpoint
        self.prometheus_port = prometheus_port
        self.enabled = enabled
        self.tracer = None
        self.meter = None
    
    def setup_tracing(self):
        """Setup distributed tracing with Jaeger or OTLP"""
        if not self.enabled:
            logger.warning("OpenTelemetry is disabled")
            return
        
        # Create resource
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENV", "development"),
        })
        
        # Setup trace provider
        trace_provider = TracerProvider(resource=resource)
        
        # Add Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=self.jaeger_host,
            agent_port=self.jaeger_port,
        )
        trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        
        # Add OTLP exporter if configured
        if self.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        set_tracer_provider(trace_provider)
        self.tracer = trace.get_tracer(__name__)
        
        logger.info(f"Tracing setup complete (Jaeger: {self.jaeger_host}:{self.jaeger_port})")
    
    def setup_metrics(self):
        """Setup metrics with Prometheus or OTLP"""
        if not self.enabled:
            logger.warning("OpenTelemetry metrics disabled")
            return
        
        # Create resource
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
        })
        
        # Setup metrics with Prometheus
        prometheus_reader = PrometheusMetricReader()
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[prometheus_reader]
        )
        
        # Add OTLP metric exporter if configured
        if self.otlp_endpoint:
            otlp_metric_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
            metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)
            meter_provider.add_metric_reader(metric_reader)
        
        set_meter_provider(meter_provider)
        self.meter = metrics.get_meter(__name__)
        
        logger.info(f"Metrics setup complete (Prometheus available on port {self.prometheus_port})")
    
    def setup_instrumentors(self, app=None):
        """Setup automatic instrumentation"""
        if not self.enabled:
            logger.warning("OpenTelemetry instrumentation disabled")
            return
        
        # Instrument FastAPI
        if app:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation enabled")
        
        # Instrument HTTP clients
        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTP client instrumentation enabled")
        
        # Instrument logging
        LoggingInstrumentor().instrument()
        logger.info("Logging instrumentation enabled")
        
        # Instrument database (if using)
        try:
            SQLAlchemyInstrumentor().instrument()
            logger.info("SQLAlchemy instrumentation enabled")
        except Exception as e:
            logger.debug(f"SQLAlchemy instrumentation not available: {e}")
        
        try:
            AsyncPGInstrumentor().instrument()
            logger.info("AsyncPG instrumentation enabled")
        except Exception as e:
            logger.debug(f"AsyncPG instrumentation not available: {e}")
    
    def initialize(self, app=None):
        """Initialize all OpenTelemetry components"""
        if not self.enabled:
            logger.warning("OpenTelemetry is disabled")
            return
        
        logger.info(f"Initializing OpenTelemetry for {self.service_name}")
        self.setup_tracing()
        self.setup_metrics()
        self.setup_instrumentors(app)
        logger.info("OpenTelemetry initialization complete")

# Global instance
otel_config = None

def init_otel(app=None, **kwargs) -> OpenTelemetryConfig:
    """Initialize OpenTelemetry"""
    global otel_config
    otel_config = OpenTelemetryConfig(**kwargs)
    otel_config.initialize(app)
    return otel_config

def get_tracer(name: str = ""):
    """Get tracer"""
    return trace.get_tracer(name or __name__)

def get_meter(name: str = ""):
    """Get meter"""
    return metrics.get_meter(name or __name__)