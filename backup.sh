#!/bin/sh
# Sauvegarde quotidienne de la base (à lancer par cron sur la VM)
set -e
mkdir -p backups
docker compose exec -T db pg_dump -U otree otree | gzip > "backups/otree_$(date +%F).sql.gz"
# Garde les 30 dernières sauvegardes
ls -1t backups/*.sql.gz | tail -n +31 | xargs -r rm
