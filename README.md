# Prometheus Up Checker
Ever wonder why alerts are all of a sudden so quiet? Is it because you are just a really awesome engineer? I'm sure you are awesome, but, being honest with ourselves here, likely this is because your monitoring system is down. Prometheus Up Checker is used to monitor your [Prometheus](https://prometheus.io/) service. Who is watching the watcher? A little something to monitor your monitoring system.

Simple python loop that continuously checks the `/-/ready` endpoint of Prometheus to see if it is available or if it returns that it is Ready. The script will run a check at the specified `CHECK_INTERVAL` and if a failure is detected in the specified `ALERT_THRESHOLD` a message will be sent to Slack to notify the user to check on Prometheus. Once the message is sent the script will then pause for the specified `ALERT_SENT_PAUSE_INTERVAL` so that alerts will continue to be sent until it is resolved but not so much that it floods your alerting platform.

There is a number of [environment variables](https://github.com/geekbass/prom-check#environment-variables) with defaults if not specified. This gives greater flexibility so that this can be run either within Kubernetes, in Docker or standalone python script.

Currently, there is only support for alerting via Slack but there are plans to support other alerting/notification platforms as well.

### The Vision
With the constantly growing popularity and ease of use of Prometheus for monitoring, we quite often forget that we must also not forget to monitor Prometheus itself. We must always consider that we must also be monitoring the thing that is responsible for monitoring all of our other things. The reason for creating this project is to make sure that we have something out there that is flexible, simple, customizable, cheap, can run anywhere and has low overhead to ensure that we are watching our watcher. It is essential that we keep Prometheus awake and ensure that we are receiving critical alerts at all times. 

The main goal here is to create an experience even more powerful and customizable than other external monitoring systems such as Pingodom, NewRelic, Datadog, etc... specifically geared to Prometheus uptime. The end goal is to have a solution that can integrate easily with "Plugin-ins" type of approach to select which alerting platform you would like to receive alerts when Prometheus is down such as Slack, PagerDuty, IFTTT Webhooks, VictorOps, etc... 
### Prereqs
- Python 3.9+
- Docker
- Helm

Check Quay repo for [latest tag](https://quay.io/repository/geekbass/prom-check).

### Usage
Please see examples below but as mentioned this can be run as standalone python, in Docker or deployed to Kubernetes. 

For standalone start by creating your python virtual env and then run the script after exporting your variables.
```
python3.9 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export PROMETHEUS_REQUEST_URL=prometheus:9090/-/ready
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/BLAH/BLAHBLAH/SOMETEXT"
export SLACK_CHANNEL="alerts"
python3.9 main.py
```

For Docker pass in the env variables via `-e`.
```
docker run -d -e "PROMETHEUS_REQUEST_URL=prometheus:9090/-/ready" -e  "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/BLAH/BLAHBLAH/SOMETEXT" -e "SLACK_CHANNEL=alerts" python-test:latest
```

For Kubernetes use Helm.

`Coming soon.`

### Environment Variables

| Variable |  Description                                   |  Default |
|----------|-----------------------------------------------------------------------------------|------|
| `SLACK_WEBHOOK_URL` | The full URL of your created webhook slack app. | None. Currently required. |
| `SLACK_CHANNEL` | The channel in which to post an alert. |   None. Currently required. |
| `ALERT_THRESHOLD` | Number of times for the check to fail consecutively before alerting.  | 5 |
| `CHECK_INTERVAL` | How often to check to see if Prometheus is available.  | 30 (seconds) |
| `ALERT_SENT_PAUSE_INTERVAL` |    Period of time after an alert has been sent before starting checks again. This is to prevent flooding alerts.   |   900 (seconds) |
| `CLUSTER_NAME` | Label to specify which Prometheus is down. TIP: Use the full URL of your clusters UI so you can open it directly from alert. |    "Production" |
| `CONTAINER_NAME` | Name of the prometheus container. |    "prometheus" |
| `PROMETHEUS_SERVICE_NAME` | [Kubernetes] If Prometheus is using a service in Kubernetes this is the name of the service. |    "prometheus-kubeaddons-prom-prometheus" |
| `PROMETHEUS_SERVICE_NS` | [Kubernetes] Namespace if used in Kubernetes. |    "kubeaddons" |
| `PROMETHEUS_SERVICE_DOMAIN` | [Kubernetes] The domain being used in Kubernetes. |    "cluster.local" |
| `PROMETHEUS_SERVICE_PORT` | Port that ready endpoint is using. |    9090 |
| `PROMETHEUS_SERVICE_PROTOCOL` | Protocol being using for ready endpoint (http or https). |    "http" |
| `PROMETHEUS_REQUEST_URL` | The Full URL of the ready endpoint. Merges all of the above `PROMETHEUS_SERVICE_*` variables. Use this for the full URL of your Prometheus's Ready endpoint if you are NOT using Kubernetes or would like to bypass all other `PROMETHEUS_SERVICE_*` variables.  |    "http://prometheus-kubeaddons-prom-prometheus.kubeaddons.svc.cluster.local:9090/-/ready" |

### Built-In Healthcheck
For monitoring this service there is a built-in web endpoint healthcheck endpoint that can be found run at `0.0.0.0:5000/healthz`. If it is healthy, it will return `OK`. 

```
> curl http://0.0.0.0:5000/healthz
OK
```

### Building Docker Image

```
docker build -t prom-check:$TAG .
```

### Slack
The slack alerting function is simply just a post to your [slack webhook URL](https://api.slack.com/messaging/webhooks) that must be created prior to use. We use the [`chat.postMessage`](https://api.slack.com/methods/chat.postMessage) function to create a Slack alert to a desired channel. The message will appear as below. The ability to define your own template will become a feature at some point.

![Slack](./images/slack.png)

### Deploying to Kubernetes
`Coming Soon`

### Try it out
You can use the `Makefile` to easily try it out locally with Docker. Use the below steps along with the output from make. NOTE: You must first have a [Slack App](https://api.slack.com/messaging/webhooks) created first.

1) Run `try-local` with your webhook url and channel exported as variables. Example:
```
make try-local SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T1290234/ABCDEFGH/123456789XYZ" SLACK_CHANNEL=alerts
```

Output:
``` 
Creating Slack Configs
Creating a local stack with docker-compose
Creating network "prom-check_default" with the default driver
Creating prom-check ... done
Creating prometheus ... done
Stack is up! We are checking Prometheus every 10 seconds and will alert once check fails 5 consecutive times.
You can check logs of prom-check to see Prometheus is ready: docker logs -f prom-check

 > docker logs -f prom-check
2020-12-18 17:11:53,794 - INFO - 1/Thread-1 - Initializing Promcheck.
 * Serving Flask app "healthz" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
2020-12-18 17:11:53,798 - INFO - 1/MainThread -  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
2020-12-18 17:11:54,855 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
2020-12-18 17:12:04,870 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
2020-12-18 17:12:14,856 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
2020-12-18 17:12:24,882 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
^C
```

2) Run `try-kill` to cause Prometheus to stop and become unavailable. 
```
> make try-kill
Killing Prometheus. You should begin to see failures in the logs and a message sent.
prometheus
Prometheus is now down....
Tail the logs of prom-check container to watch the alert to be fired: docker logs -f prom-check

...
...
...

2020-12-18 17:13:14,908 - INFO - 1/Thread-1 - Could not reach prometheus 1 times. Checking again in 10 seconds.
2020-12-18 17:13:24,925 - INFO - 1/Thread-1 - Could not reach prometheus 2 times. Checking again in 10 seconds.
2020-12-18 17:13:34,941 - INFO - 1/Thread-1 - Could not reach prometheus 3 times. Checking again in 10 seconds.
2020-12-18 17:13:44,922 - INFO - 1/Thread-1 - Could not reach prometheus 4 times. Checking again in 10 seconds.
2020-12-18 17:13:54,938 - INFO - 1/Thread-1 - Could not reach prometheus 5 times. Checking again in 10 seconds.
2020-12-18 17:13:54,938 - INFO - 1/Thread-1 - Threshold reached. Triggering Alert.
2020-12-18 17:13:54,938 - INFO - 1/Thread-1 - Sending alert to Slack Channel alerts.
2020-12-18 17:13:55,194 - INFO - 1/Thread-1 - Alert has been sent. Pausing before trying checks again.
^C
```

3) Run `try-recover` to recover Prometheus and see that Prometheus is in fact up again.
``` 
> make try-recover
Bring Prometheus back up!. You should see failures messages that Prometheus is up once again.
prometheus

...
...
...

2020-12-18 17:16:05,441 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
2020-12-18 17:16:15,427 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
2020-12-18 17:16:25,448 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
2020-12-18 17:16:35,468 - INFO - 1/Thread-1 - prometheus is up. Checking again in 10 seconds.
```

4) Run `try-down` when ready for clean up.
``` 
 > make try-down
Killing the stack. Thanks for trying it out.
Stopping prometheus ... done
Stopping prom-check ... done
Removing prometheus ... done
Removing prom-check ... done
Removing network prom-check_default
```

### Contributing
If you would like to contribute, add features, or fork for own use, first start by using `docker-build` from the `Makefile` to build locally and then run through the steps of [Try it Out](https://github.com/geekbass/prom-check#try-it-out) above while ensuring to update the `image` for `prom_check` in the `docker-compose.yaml` file.

``` 
make docker-build TAG=DESIRED_TAG
```
### To Do:
- [ ] Error Handling
- [ ] Add additional Alerting Platforms
- [ ] helm chart
- [ ] Docs
- [ ] Allow for user to pass own Template data for Slack message
- [ ] Tests
- [ ] Build out some automation: docker builds, linting, etc...
- [ ] Add resolved Message to Slack?
- [ ] Also add in checks for AlertManager as well as it is the entity responsible for firing alerts for Prometheus?

