import os
import json
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace

TRACER_SERVICE_NAME = "mqtt-consumer"
TRACER_OTLP_ENDPOINT = os.getenv("TRACER_OTLP_ENDPOINT")
LOCAL_TRACE_FILE = f"{TRACER_SERVICE_NAME}_traces.jsonl"


class OTLPJsonFileExporter(SpanExporter):
    """
    Ein OTLP-kompatibler File Exporter für Traces im JSON Lines-Format.
    Speichert Traces in einer Datei, wobei jede Zeile ein JSON-Objekt ist.
    """

    def __init__(self, filepath):
        self.filepath = os.path.abspath(filepath)
        open(self.filepath, 'a').close()

    def export(self, spans):
        """
        Exportiert die Spans in das JSON Lines-Format.
        """
        with open(self.filepath, "a", encoding="utf-8") as f:
            for span in spans:
                span_data = {
                    "traceId": format(span.context.trace_id, "032x"),  # Hex-String
                    "spanId": format(span.context.span_id, "016x"),  # Hex-String
                    "parentSpanId": format(span.parent.span_id, "016x") if span.parent else None,
                    "name": span.name,
                    "startTimeUnixNano": span.start_time,
                    "endTimeUnixNano": span.end_time,
                    "attributes": dict(span.attributes),  # mappingproxy zu dict
                    "status": {
                        "code": span.status.status_code.name,
                        "description": span.status.description,
                    },
                    "kind": span.kind.name,  # Enum zu String
                }
                f.write(json.dumps(span_data) + "\n")
        return SpanExportResult.SUCCESS


def get_tracer():
    """
    Konfiguriert den OTLP-Tracer für OpenTelemetry und fügt den JSON Lines File Exporter hinzu.
    """
    # OTLP-Exporter für Tempo/Jaeger
    otlp_exporter = OTLPSpanExporter(
        endpoint=TRACER_OTLP_ENDPOINT,
        insecure=True
    )

    # JSON Lines File Exporter
    file_exporter = OTLPJsonFileExporter(LOCAL_TRACE_FILE)

    # TracerProvider initialisieren
    tracer_provider = TracerProvider(
        resource=Resource.create({"service.name": TRACER_SERVICE_NAME})
    )

    # Exporter hinzufügen
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # JSON File Exporter hinzufügen
    file_span_processor = BatchSpanProcessor(file_exporter)
    tracer_provider.add_span_processor(file_span_processor)

    # TracerProvider global setzen
    trace.set_tracer_provider(tracer_provider)

    return trace.get_tracer(__name__)
