FROM python:3.10-alpine
RUN adduser -D codehub
WORKDIR /home/codehub
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
COPY app app
COPY migrations migrations
COPY app.py config.py boot.sh ./
RUN chmod +x boot.sh
ENV FLASK_APP app.py
RUN chown -R codehub:codehub ./
USER codehub
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]