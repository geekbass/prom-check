"""
Script is used to post an alert to a Slack Channel via webhook. You must create this the webhook prior to running this
script.

See https://api.slack.com/methods/chat.postMessage for more information.
"""
import requests
import logging
import json


def alert_slack(slack_webhook_url, channel, cluster_name, container, namespace):
    log_format = "%(asctime)s - %(levelname)s - %(process)d/%(threadName)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)

    logging.info("Sending alert to Slack Channel {}.".format(channel))

    """
    Define the body of the post call
    other values can be found https://api.slack.com/methods/chat.postMessage
    """
    # TODO: All for user to specify own data.
    data = {
        "channel": channel,
        "username": "PrometheusCheck",
        "icon_url": "https://avatars3.githubusercontent.com/u/3380462",
        "attachments": [
            {
                "text": "*alertname*: `PrometheusCannotBeReached`\n*cluster:* `" + cluster_name + "`\n*container:* `" + container + "`\n*namespace:* `" + namespace + "`\n*severity:* `critical`",
                "color": "#d10202"
            }
        ]
    }

    # Post payload and headers to your webhook url
    requests.post(slack_webhook_url, data=json.dumps(data), headers={"Content-Type": "application"})
