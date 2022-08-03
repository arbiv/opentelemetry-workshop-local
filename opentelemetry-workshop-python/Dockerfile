FROM python:3.7-alpine
WORKDIR /code
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc g++ musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]
#ENV PYTHONUNBUFFERED=true 
#ENV OTEL_LOG_LEVEL=debug 
#CMDpython3 server.py
