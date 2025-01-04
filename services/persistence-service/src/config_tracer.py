import os
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace

TRACER_SERVICE_NAME = "persistence-service"
TRACER_OTLP_ENDPOINT = os.getenv("TRACER_OTLP_ENDPOINT")


def get_tracer():
    """
    Konfiguriert den OTLP-Tracer für OpenTelemetry.
    Nutzt OTLP-Protokoll, das nativ von Jaeger unterstützt wird.

    :param service_name: Name des Services für das Tracing.
    """
    otlp_exporter = OTLPSpanExporter(
        endpoint=TRACER_OTLP_ENDPOINT,
        insecure=True
    )

    # TracerProvider initialisieren
    tracer_provider = TracerProvider(
        resource=Resource.create({"service.name": TRACER_SERVICE_NAME})
    )

    # SpanProcessor hinzufügen
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # TracerProvider global setzen
    trace.set_tracer_provider(tracer_provider)

    return trace.get_tracer(__name__)
