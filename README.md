# OpenTelemetry Workshop - Local Copy

To start clone the repo and run:

```sh
    docker-compose build
    docker-compose up
```

1. Browse <http://127.0.0.1:5000/fib?i=3>. You should see 1, the 3rd element in Fibonacci sequence
1. Browse <http://127.0.0.1:16686/> to view traces in Jaeger
1. Browse <http://127.0.0.1:3000> to view metrics in Grafana
