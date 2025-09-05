#/bin/sh
SCRIPT_DIR=$(dirname $0)
PROJECT_DIR="${SCRIPT_DIR}/../"
CACHE_DIR="${PROJECT_DIR}/node_modules/.cache"
mkdir -p "${CACHE_DIR}"
TMP="${CACHE_DIR}/tsconfig.json"

cat >$TMP <<EOF
{
  "extends": "../../tsconfig.json",
  "include": [
EOF
for file in "$@"; do
  echo "    \"$file\"," >> $TMP
done
cat >>$TMP <<EOF
    "../../*.d.ts",
    "../../@types/*"
  ]
}
EOF
$PROJECT_DIR/node_modules/.bin/tsc --project $TMP --pretty --skipLibCheck --noEmit