


# Start with a more lightweight base image if possible
FROM python:3.9-slim

# Install Google Chrome Stable specific version
RUN apt-get update && apt-get install -y wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Download and unzip Chrome to /opt/chrome
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.184/linux64/chrome-linux64.zip -O /tmp/chrome-linux64.zip && \
    unzip /tmp/chrome-linux64.zip -d /opt/chrome && \
    rm /tmp/chrome-linux64.zip

# Copy the requirements file first (to cache the installed dependencies)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . .

# Make sure any binaries or scripts from Chrome are executable, if necessary
# Depending on how you plan to run Chrome, you might need to set permissions
# RUN chmod +x /opt/chrome/chrome  # Adjust this line as necessary

# Set environment variables to run Chrome in a headless environment
ENV DISPLAY=:99
# If using chromedriver or similar tools, ensure they know where to find Chrome
ENV CHROME_PATH=/opt/chrome/chrome-linux64/chrome  








ENV PATH /root/.local/bin:$PATH

# Copy the requirements file and install Python dependencies in one layer


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . .
RUN chmod +x /app/chromedriver

# Further instructions to set up your application



