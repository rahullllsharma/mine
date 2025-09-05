### Not using this docker for now. ###
### Mongo docker image is directly pulled in docker-compose file ###

FROM mongo:latest
# Optional: Add any customization or configuration here
# Install the mongo client
RUN apt-get update && \
    apt-get install -y gnupg wget coreutils && \
    wget -qO- https://www.mongodb.org/static/pgp/server-7.0.asc | tee /etc/apt/trusted.gpg.d/server-7.0.asc && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list \
    apt-get update && \
    apt-get install -y mongodb-mongosh

# Set the root username and password
ENV MONGO_INITDB_ROOT_USERNAME root
ENV MONGO_INITDB_ROOT_PASSWORD password
ENV MONGO_INTIDB_DB_NAME asgard
ENV MONGO_INITDB_COLLECTION_NAME public

# Copy and execute the initialization script
COPY ./mongo-init.sh /docker-entrypoint-initdb.d/mongo-init.sh


