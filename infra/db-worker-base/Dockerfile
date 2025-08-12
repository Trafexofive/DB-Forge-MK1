# Use a minimal base image that is widely available and secure.
FROM alpine:latest

# Install sqlite command-line tools.
# --no-cache avoids storing the package index, keeping the image small.
RUN apk add --no-cache sqlite

# The worker's purpose is to act as a data volume holder.
# The gateway interacts with the database file on the mounted volume.
# This command keeps the container running indefinitely.
CMD ["sleep", "infinity"]
