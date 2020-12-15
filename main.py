import os
import requests
import logging
import time
import threading
import healthz

# TODO: Constants to file?
# We are passing ENV variables with defaults if they do not exist
ALERT_THRESHOLD = os.getenv("THRESHOLD", 5)
CHECK_INTERVAL = os.getenv("INTERVAL", 30)

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
            # TODO: trigger alert to slack or PD

            # Reset the threshold counter
            threshold_counter = []

        # Sleep before next check is run
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    # Use threading to run Flask and main function
    threading.Thread(target=main).start()
    threading.Thread(target=healthz.app.run('0.0.0.0')).start()
