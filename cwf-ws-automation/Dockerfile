# Use Node.js 18 as base image
FROM node:18-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies including Java for Allure and Xvfb
# 'cron' has been removed as it's not needed for GitHub Actions
RUN apt-get update && apt-get install -y \
    curl \
    openjdk-17-jdk \
    unzip \
    wget \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH=$PATH:$JAVA_HOME/bin

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci

# Install Playwright browsers with proper environment setup
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN npx playwright install --with-deps chromium

# Copy application code
COPY . .

# Create directories for test results
RUN mkdir -p allure-results allure-report test-results report-records logs

# Expose port for Allure report (optional)
EXPOSE 8080

# The container will now wait for a command from your 'docker run' instruction.