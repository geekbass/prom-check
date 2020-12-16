"""
Script is used to check the /ready endpoint of prometheus to see if it is available or not. When the check fails a
number of times in a row, specified by THRESHOLD, it will send an alert to Slack or PagerDuty that Prometheus is
currently failing and that your monitoring system is not longer monitoring your environment. This is written to support
Prometheus on Kubernetes.
"""

import os
import requests
import logging
import time
import threading
import healthz
import slack

# TODO: Constants to file?
# We are passing ENV variables with defaults if they do not exist where possible
ALERT_THRESHOLD = os.getenv("THRESHOLD", 5)
ALERT_SENT_PAUSE_INTERVAL = os.getenv("ALERT_SENT_PAUSE_INTERVAL", 900)
CHECK_INTERVAL = os.getenv("INTERVAL", 30)

CLUSTER_NAME = os.getenv("CLUSTER_NAME", "Production")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "prometheus")
PROMETHEUS_SERVICE_NAME = os.getenv("PROMETHEUS_SERVICE_NAME", "prometheus-kubeaddons-prom-prometheus")
PROMETHEUS_SERVICE_NS = os.getenv("PROMETHEUS_SERVICE_NS", "kubeaddons")
PROMETHEUS_SERVICE_DOMAIN = os.getenv("PROMETHEUS_SERVICE_DOMAIN", "cluster.local")
PROMETHEUS_SERVICE_PORT = os.getenv("PROMETHEUS_SERVICE_PORT", "9090")
PROMETHEUS_SERVICE_PROTOCOL = os.getenv("PROMETHEUS_SERVICE_PROTOCOL", "http")
PROMETHEUS_REQUEST_URL = os.getenv("PROMETHEUS_REQUEST_URL", "{}://{}.{}.svc.{}:{}/-/ready".format(
    PROMETHEUS_SERVICE_PROTOCOL,
    PROMETHEUS_SERVICE_NAME,
    PROMETHEUS_SERVICE_NS,
    PROMETHEUS_SERVICE_DOMAIN,
    PROMETHEUS_SERVICE_PORT))

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

def main():
    log_format = "%(asctime)s - %(levelname)s - %(process)d/%(threadName)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)

    logging.info("Initializing Promcheck.")

    # Initialize threshold counter
    threshold_counter = []

    while True:
        # Get the response code for Prometheus
        resp = requests.get("PROMETHEUS_REQUEST_URL").status_code

        # Get the data from endpoint. Remove the new blank link and lower case all the things.
        data = requests.get(PROMETHEUS_REQUEST_URL).text.lower().strip('\n')
        # TODO: Add some error handling

        # If we don't get response code 200, increase the threshold counter
        if resp != 200 or "prometheus is ready" not in data:
            threshold_counter.append(resp)
            logging.info("Could not reach {} {} times. Checking again in {} seconds.".format(
                CONTAINER_NAME, len(threshold_counter), CHECK_INTERVAL))
        else:
            logging.info("{} is up. Checking again in {} seconds.".format(
                CONTAINER_NAME, CHECK_INTERVAL))

        # If we are over threshold then its time to alert
        if len(threshold_counter) >= int(ALERT_THRESHOLD):
            logging.info("Threshold reached. Triggering Alert.")
            # TODO: Error handling for missing SLACK variables

            # Create an alert
            # TODO: Include additional Alerting platforms such as PagerDuty, etc...
            slack.alert_slack(SLACK_WEBHOOK_URL, SLACK_CHANNEL, CLUSTER_NAME, CONTAINER_NAME, PROMETHEUS_SERVICE_NS)

            # Reset the threshold counter
            threshold_counter = []

            # Pause for a few minutes again before starting checks again.
            # This prevents blowing up a channel.
            logging.info("Alert has been sent. Pausing before trying checks again.")
            time.sleep()

        # Sleep before next check is run
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    # Use threading to run Flask and main function
    threading.Thread(target=main).start()
    threading.Thread(target=healthz.app.run('0.0.0.0')).start()
