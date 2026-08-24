#!/bin/sh
# Pull local-only dumps. Never commit dumps/.
# private-sql-host: MediaWiki SQL under /var/backups/mysql/sqldump/
# private-drupal-host: Drupal DBs (content tables / node XML only — no users)
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
SQL="$ROOT/dumps/sql"
mkdir -p "$SQL" "$ROOT/dumps/zim"

echo ">> trashwiki SQL from private-sql-host"
scp -o BatchMode=yes private-sql-host:/var/backups/mysql/sqldump/trashwiki.sql.gz "$SQL/trashwiki.sql.gz"

echo ">> Drupal content dumps on private-drupal-host"
ssh -o BatchMode=yes private-drupal-host 'mkdir -p /tmp/books-sql
sudo -n mysqldump --single-transaction --no-tablespaces randomroads node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image_top | gzip -c > /tmp/books-sql/randomroads-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces dumpsterdam tb_node tb_node_revision tb_field_data_body tb_field_revision_body tb_url_alias tb_file_managed tb_field_data_field_image | gzip -c > /tmp/books-sql/dumpsterdam-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces moneylessorg node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image | gzip -c > /tmp/books-sql/moneylessorg-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces geldloosnl node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image | gzip -c > /tmp/books-sql/geldloosnl-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces sindineronet node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image | gzip -c > /tmp/books-sql/sindineronet-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces casarobino node node_revisions url_alias files | gzip -c > /tmp/books-sql/casarobino-content.sql.gz
'

echo ">> copy SQL + node XML from d7"
scp -o BatchMode=yes private-drupal-host:'/tmp/books-sql/*-content.sql.gz' "$SQL/"
scp -o BatchMode=yes private-drupal-host:'/tmp/books-sql/*-nodes.xml.gz' "$SQL/" 2>/dev/null || true
ls -lh "$SQL"
