.PHONY: build up down logs restart rebuild

## 🔧 Build l'image Docker
build:
	docker compose build

## 🚀 Démarre le conteneur avec boucle (toutes les 30 minutes)
up:
	docker compose up -d

## 🛑 Arrête le conteneur
down:
	docker compose down

## 🔁 Redémarre proprement
restart:
	docker compose down && docker compose up -d

## 🔁 Mettre à jour le code (via Git), nettoie l’environnement Docker, et relance les conteneurs avec les dernières modifications.
rebuild:
	git pull && docker compose down --remove-orphans && docker compose up -d --build

## 📜 Affiche l’historique des logs
tail-logs:
	tail -f logs/jobs.log
