#!/bin/sh
# wait-for-mariadb.sh

# Exit on failure
set -e

host="$1"
# Skip parameter above (aka host) in input parameter
# in order to proper execute other commands after this parameter further on
shift

until mariadb --host=localhost --port=3306 --user=root --password=example metricsDB; do

  >&2 echo "MariaDB is unavailable - waiting..."
  sleep 1
done

>&2 echo "MariaDB is up - executing command"
exec "$@"
