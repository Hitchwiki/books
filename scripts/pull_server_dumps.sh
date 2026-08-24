#!/bin/sh
# Pull local-only dumps over SSH. Never commit dumps/ or local/hosts.env.
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
ENV="$ROOT/local/hosts.env"
SQL="$ROOT/dumps/sql"
mkdir -p "$SQL" "$ROOT/dumps/zim"

if [ ! -f "$ENV" ]; then
  echo "missing local/hosts.env — copy local/hosts.env.example and set the SSH hosts" >&2
  exit 1
fi
# shellcheck disable=SC1090
. "$ENV"
: "${MW_SQL_HOST:?}" "${DRUPAL_HOST:?}"
MW_SQL_PATH="${MW_SQL_PATH:-/var/backups/mysql/sqldump}"

echo ">> trashwiki SQL"
scp -o BatchMode=yes "$MW_SQL_HOST:$MW_SQL_PATH/trashwiki.sql.gz" "$SQL/trashwiki.sql.gz"

echo ">> Drupal content dumps (node tables only, no users)"
ssh -o BatchMode=yes "$DRUPAL_HOST" 'mkdir -p /tmp/books-sql
sudo -n mysqldump --single-transaction --no-tablespaces randomroads node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image_top | gzip -c > /tmp/books-sql/randomroads-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces dumpsterdam tb_node tb_node_revision tb_field_data_body tb_field_revision_body tb_url_alias tb_file_managed tb_field_data_field_image | gzip -c > /tmp/books-sql/dumpsterdam-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces moneylessorg node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image | gzip -c > /tmp/books-sql/moneylessorg-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces geldloosnl node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image | gzip -c > /tmp/books-sql/geldloosnl-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces sindineronet node node_revision field_data_body field_revision_body url_alias file_managed field_data_field_image | gzip -c > /tmp/books-sql/sindineronet-content.sql.gz
sudo -n mysqldump --single-transaction --no-tablespaces casarobino node node_revisions url_alias files | gzip -c > /tmp/books-sql/casarobino-content.sql.gz
'

echo ">> copy SQL + node XML"
scp -o BatchMode=yes "$DRUPAL_HOST":'/tmp/books-sql/*-content.sql.gz' "$SQL/"
scp -o BatchMode=yes "$DRUPAL_HOST":'/tmp/books-sql/*-nodes.xml.gz' "$SQL/" 2>/dev/null || true
ls -lh "$SQL"
