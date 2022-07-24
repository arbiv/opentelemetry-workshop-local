import logging
from flask import Flask, request
import requests
import sys
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)

from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
import requests
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(filename)s:%(funcName)s:%(lineno)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.debug(
    "Log level is set to debug, spans will sent and printed to console"
)

provider = TracerProvider(resource=Resource.create(
    {SERVICE_NAME: "workshop-test"}))
otlpExporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
processor = BatchSpanProcessor(otlpExporter)
provider.add_span_processor(processor)
# Sets the global default tracer provider
trace.set_tracer_provider(provider)
# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(
    endpoint="http://otel-collector:4317"), export_interval_millis=30*1000)
meter_provider = MeterProvider(metric_readers=[metric_reader])
# Sets the global default meter provider
metrics.set_meter_provider(meter_provider)
# Creates a meter from the global meter provider
meter = metrics.get_meter(__name__)


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route("/")
def root():
    with tracer.start_as_current_span("root") as span:
        # this is a workaround for a glitch logging issue
        sys.stdout.write('\n')
    return "Click [Logs] to see spans!"


@app.route("/fib")
@app.route("/fibInternal")
def fibHandler():
    value = int(request.args.get('i'))
    current_span = trace.get_current_span()
    current_span.set_attribute("parameter", value)

    returnValue = 0
    if value == 1:
        returnValue = 0
    elif value == 2:
        returnValue = 1
    else:
        minusOnePayload = {'i': value - 1}
        minusTwoPayload = {'i': value - 2}
        # if True:
        with tracer.start_as_current_span("getMinusOne") as span:
            span.set_attribute("payloadValue", value - 1)
            respOne = requests.get(
                'http://127.0.0.1:5000/fibInternal', minusOnePayload)

        # if True:
        with tracer.start_as_current_span("getMinusTwo") as span:
            span.set_attribute("payloadValue", value - 2)
            respTwo = requests.get(
                'http://127.0.0.1:5000/fibInternal', minusTwoPayload)
        returnValue = int(respOne.content) + int(respTwo.content)
    # this is a workaround for a glitch logging issue
    sys.stdout.write('\n')
    return str(returnValue)


if __name__ == "__main__":
    app.run(debug=True)
