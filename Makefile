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

try-kill:
	@echo "Kill Prometheus. You should begin to see failures in the logs and a message sent."
	@docker kill prometheus
	@docker logs prom-check -f --tail -30

try-down:
	@echo "Killing the stack. Thanks for trying it out."
	@docker-compose down


