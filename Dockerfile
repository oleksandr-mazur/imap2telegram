FROM python:3.12.7-slim

RUN useradd -m imap
RUN mkdir /app && chown -R imap:imap /app
USER imap
WORKDIR /app
ADD requirements.txt .
RUN python -m pip install pip -U && python -m pip --no-cache-dir install -r requirements.txt
COPY . .

ENTRYPOINT ["python3", "main.py"]
