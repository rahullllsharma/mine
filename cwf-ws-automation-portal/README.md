# cwf-ws-automation-portal
CWF WS Automation Portal

## Overview
This repository contains automated tests. These instructions will help you set up and run the tests locally.

## Prerequisites
- Node.js (v14 or higher)
- npm (comes with Node.js)
- Java Development Kit (JDK) for Allure report generation
- Access to company VPN (Using OpenVPN)

## Getting Started

### 1. Java Installation (macOS with Homebrew)

# Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

# Install Java (Recommended: Latest LTS version)
```bash
brew install openjdk@17
```

# Set up Java environment
```bash
echo 'export PATH="/usr/local/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
echo 'export JAVA_HOME="/usr/local/opt/openjdk@17"' >> ~/.zshrc
source ~/.zshrc
```

# Verify Java installation
```bash
java --version
javac --version
```

### 1. Clone the Repository
```bash
git clone https://github.com/urbint/dp-automation-portal
cd {into-the-repo-directory}
```

### 2. Install Dependencies
```bash
npm install
npx playwright install
```

### 3. VPN Connection
Connect to your company VPN before running tests.

## Running Tests
Note: Before running tests check the Excel Sheet which contains sheet named "EnvConfiguration" in this set the Environment to respective environment('INT' || 'STAGING' || 'PROD') you want to test.
After connecting to VPN, execute:
```bash
npm run test
```

### Test Reports
Test results will be available in the respective environment folder inside "AutomationResults" folder.
Single HTML File Report (Allure) will be generated in the report-records folder.

## Troubleshooting

### Common Issues
1. **VPN Connection**
   - Verify VPN is active and stable
   - Try reconnecting if tests fail

2. **Dependencies**
   - Ensure all packages are installed:
     ```bash
     npm install
     ```

3. **Node Version**
   - Verify Node.js version:
     ```bash
     node --version
     ```

## Support
Contact the SDE-Test Team for any issues or questions.

