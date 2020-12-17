# Example Usage
### Standalone
Standalone with checks every 60 seconds:
```
python3.9 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export PROMETHEUS_REQUEST_URL=prometheus:9090/-/ready
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/BLAH/BLAHBLAH/SOMETEXT"
export SLACK_CHANNEL="alerts"
export CHECK_INTERVAL=60
python3.9 main.py
```

### Docker 
Using Docker to check every 60 seconds with a label that supplies a link to the Prometheus development instance. If an alert is triggered it will provide a link to https://prometheus.development.com within the Slack message.
```
docker run -d -e "PROMETHEUS_REQUEST_URL=prometheus:9090/-/ready" -e  "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/BLAH/BLAHBLAH/SOMETEXT" -e "SLACK_CHANNEL=alerts" \ 
 -e "CHECK_INTERVAL=60" -e "CLUSTER_NAME=https://prometheus.development.com" python-test:latest
```

### Kubernetes

`Coming soon.`
