SHELL := /bin/bash
DOCKER ?= docker

.PHONY: install up down logs test-unit test-sanity test-e2e test-all model-pull full-e2e clean

install:
	npm install
	python3 -m pip install -r tests/requirements.txt
	npx playwright install --with-deps chromium

up:
	$(DOCKER) compose up --build -d

down:
	$(DOCKER) compose down

logs:
	$(DOCKER) compose logs -f --tail=200

model-pull:
	$(DOCKER) compose exec -T ollama ollama pull llama3

test-unit:
	python3 -m pytest tests/unit -q

test-sanity:
	python3 -m pytest tests/sanity -q

test-e2e:
	npm run test:e2e

test-all: test-unit test-sanity test-e2e

full-e2e:
	bash scripts/full_e2e_check.sh

clean:
	rm -rf apps/pwa-interface/.next
	rm -rf node_modules
	rm -rf tests/e2e/screenshots/*.png
