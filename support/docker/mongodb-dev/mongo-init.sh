#!/bin/bash

# Wait for MongoDB to be ready
until mongosh --eval "print(\"waited for connection\")"
do
    mongosh --version
    sleep 2
done

# Get the database name and collection name from environment variables
DATABASE_NAME="$MONGO_INTIDB_DB_NAME"
COLLECTION_NAME="$MONGO_INITDB_COLLECTION_NAME"

# Check if the DATABASE_NAME and COLLECTION_NAME are set
if [ -z "$DATABASE_NAME" ] || [ -z "$COLLECTION_NAME" ]; then
  echo "Error: MONGO_DATABASE_NAME or MONGO_COLLECTION_NAME environment variable is not set."
  exit 1
fi

# Create the specified database
mongosh --eval 'use '$DATABASE_NAME'; db.createCollection('$COLLECTION_NAME');'