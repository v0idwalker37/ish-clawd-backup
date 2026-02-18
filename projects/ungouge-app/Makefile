.PHONY: help dev up down build test lint clean deploy-staging deploy-prod logs

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development environment
	docker-compose up

up: ## Start services in background
	docker-compose up -d

down: ## Stop all services
	docker-compose down

build: ## Rebuild all services
	docker-compose build

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs for all services
	docker-compose logs -f

logs-api: ## Show API Gateway logs
	docker-compose logs -f api-gateway

logs-cost: ## Show Cost Model logs
	docker-compose logs -f cost-model

logs-extractor: ## Show Quote Extractor logs
	docker-compose logs -f quote-extractor

logs-webhook: ## Show Webhook Handler logs
	docker-compose logs -f webhook-handler

test: ## Run all unit tests
	pytest services/*/test_main.py -v

test-api: ## Test API Gateway
	cd services/api-gateway && pytest test_main.py -v

test-cost: ## Test Cost Model
	cd services/cost-model && pytest test_main.py -v

test-extractor: ## Test Quote Extractor
	cd services/quote-extractor && pytest test_main.py -v

lint: ## Lint all Python code
	ruff check services/*/main.py
	ruff check services/*/test_main.py

lint-fix: ## Lint and auto-fix
	ruff check --fix services/*/main.py
	ruff check --fix services/*/test_main.py

format: ## Format all Python code
	black services/*/main.py
	black services/*/test_main.py

health: ## Check health of all services
	@echo "API Gateway:"
	@curl -s http://localhost:8000/health/live | jq .
	@echo "\nCost Model:"
	@curl -s http://localhost:8001/health/live | jq .
	@echo "\nQuote Extractor:"
	@curl -s http://localhost:8002/health/live | jq .
	@echo "\nWebhook Handler:"
	@curl -s http://localhost:8003/health/live | jq .

ready: ## Check readiness of all services
	@echo "API Gateway:"
	@curl -s http://localhost:8000/health/ready | jq .
	@echo "\nCost Model:"
	@curl -s http://localhost:8001/health/ready | jq .
	@echo "\nQuote Extractor:"
	@curl -s http://localhost:8002/health/ready | jq .
	@echo "\nWebhook Handler:"
	@curl -s http://localhost:8003/health/ready | jq .

db-shell: ## Connect to database
	docker-compose exec postgres psql -U ungouge -d ungouge

redis-cli: ## Connect to Redis
	docker-compose exec redis redis-cli

clean: ## Remove all containers, volumes, and images
	docker-compose down -v --rmi all

reset: ## Full reset (clean + rebuild + start)
	$(MAKE) clean
	$(MAKE) build
	$(MAKE) up

deploy-staging: ## Deploy to staging (via GitHub Actions)
	git checkout develop
	git pull
	git push origin develop
	@echo "Staging deployment triggered. Check GitHub Actions for status."

deploy-prod: ## Deploy to production (requires approval)
	git checkout main
	git pull
	git merge develop
	git push origin main
	@echo "Production deployment triggered. REQUIRES MANUAL APPROVAL in GitHub Actions."

tf-init-staging: ## Initialize Terraform for staging
	cd infra/terraform/environments/staging && terraform init

tf-plan-staging: ## Plan Terraform changes for staging
	cd infra/terraform/environments/staging && terraform plan

tf-apply-staging: ## Apply Terraform changes to staging
	cd infra/terraform/environments/staging && terraform apply

tf-init-prod: ## Initialize Terraform for production
	cd infra/terraform/environments/production && terraform init

tf-plan-prod: ## Plan Terraform changes for production
	cd infra/terraform/environments/production && terraform plan

tf-apply-prod: ## Apply Terraform changes to production
	cd infra/terraform/environments/production && terraform apply

install: ## Install development dependencies
	pip install -r requirements-dev.txt

docs: ## Generate API documentation
	@echo "API documentation available at:"
	@echo "  http://localhost:8000/docs (API Gateway)"
	@echo "  http://localhost:8001/docs (Cost Model)"
	@echo "  http://localhost:8002/docs (Quote Extractor)"
	@echo "  http://localhost:8003/docs (Webhook Handler)"
