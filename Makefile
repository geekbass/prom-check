check-env:
ifeq ($(SLACK_WEBHOOK_URL),)
	$(error SLACK_WEBHOOK_URL is not set)
endif
ifeq ($(SLACK_CHANNEL),)
	$(error SLACK_CHANNEL is not set)
endif

try-local: check-env
	@echo "Creating Slack Configs"
	@echo SLACK_WEBHOOK_URL=$(SLACK_WEBHOOK_URL) >> tests/prom-check.conf
	@echo SLACK_CHANNEL=$(SLACK_CHANNEL) >> tests/prom-check.conf
	@echo "Creating a local stack with docker-compose"
	@docker-compose up -d
	@echo "Stack is up! We are checking Prometheus every 10 seconds and will alert once check fails 5 consecutive times."
	@echo "You can check logs of prom-check to see Prometheus is ready: docker logs -f prom-check"

try-kill:
	@echo "Killing Prometheus. You should begin to see failures in the logs and a message sent."
	@docker kill prometheus
	@echo "Prometheus is now down...."
	@echo "Tail the logs of prom-check container to watch the alert to be fired: docker logs -f prom-check"

try-recover:
	@echo "Bring Prometheus back up!. You should see failures messages that Prometheus is up once again."
	@docker start prometheus

try-down:
	@echo "Killing the stack. Thanks for trying it out."
	@docker-compose down

docker-build:
	@if [ -d "$(TAG)" ]; then \
		echo "Exiting... $(TAG) Needs Specified..." && exit 1; \
	fi
	@echo "Building docker image for local use with tag: " $(TAG)
	@docker build -t prom-check:$(TAG) .
