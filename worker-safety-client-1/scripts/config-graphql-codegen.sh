#/bin/sh
Green='\033[0;32m'
Yellow='\033[0;33m'

export GRAPHQL_AUTH_RESPONSE=$(curl -s --request POST \
  --url localhost:8080/auth/realms/asgard/protocol/openid-connect/token \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=password \
  --data client_id=worker-safety-asgard \
  --data scope=openid \
  --data username=super \
  --data password=password)

echo "\n${Green}Setup to generate Graphql with codegen done\n"