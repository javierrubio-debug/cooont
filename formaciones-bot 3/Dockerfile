FROM node:20-slim

# Python
RUN apt-get update && apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Node deps
COPY package.json .
RUN npm install

# Python deps
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# App files
COPY bot.py ppt_generator.py generate_ppt.js ./

CMD ["python3", "bot.py"]
