


# Start with a more lightweight base image if possible
FROM python:3.9-slim

# Install Google Chrome Stable specific version
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && wget -qO - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable=121.0.6167.184-1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# Set the PATH environment variable
RUN chmod +x /chromedriver

ENV PATH /root/.local/bin:$PATH

# Copy the requirements file and install Python dependencies in one layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . .

# Further instructions to set up your application



