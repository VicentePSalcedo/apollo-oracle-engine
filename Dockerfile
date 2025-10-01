FROM python:3.12-slim

RUN apt-get update && apt-get install -y cron tzdata zlib1g-dev rsyslog && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV TZ=America/New_York

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps

COPY . .

COPY crontab /etc/cron.d/my-cron-job

RUN chmod 0644 /etc/cron.d/my-cron-job

RUN touch /var/log/cron.log

RUN chmod 0666 /var/log/cron.log

COPY start.sh /start.sh

RUN chmod +x /start.sh

CMD ["/start.sh"]

# CMD ["sh", "-c", "rsyslogd && cron && tail -f /var/log/syslog"]
