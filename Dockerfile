FROM python:3.12-slim

RUN apt-get update && apt-get install -y cron tzdata zlib1g-dev rsyslog && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV TZ=Etc/UTC

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps

COPY . .

COPY crontab /etc/cron.d/my-cron-job

RUN chmod 0644 /etc/cron.d/my-cron-job

RUN touch /var/log/cron.log

RUN chmod 0666 /var/log/cron.log

CMD ["sh", "-c", "rsyslogd && cron && tail -f /var/log/syslog"]

# FROM python:3.12-slim

# RUN apt-get update && \
#     apt-get install -y \
#     zlib1g-dev &&\
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# RUN playwright install --with-deps

# COPY . .

# CMD ["python", "main.py"]
