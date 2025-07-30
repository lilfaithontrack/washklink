#!/bin/sh

# wait-for.sh script to wait for MongoDB to be ready

set -e

host="$1"
shift
cmd="$@"

until nc -z -v -w30 "$host" 27017
do
  echo "Waiting for MongoDB to be ready... sleeping"
  sleep 1
done

echo "MongoDB is up - executing command"
exec $cmd 