# ---------------- BASE IMAGE ----------------
FROM python:3.10-slim

# ---------------- ENV SETTINGS ----------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------------- WORKDIR ----------------
WORKDIR /app

# ---------------- SYSTEM DEPENDENCIES ----------------
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------------- COPY REQUIREMENTS ----------------
COPY dashboard/requirements.txt /app/requirements.txt

# ---------------- INSTALL PYTHON DEPENDENCIES ----------------
RUN pip install --no-cache-dir -r requirements.txt

# ---------------- COPY APPLICATION CODE ----------------
COPY dashboard/app/ /app/

# ---------------- STREAMLIT CONFIG ----------------
EXPOSE 8051

ENV STREAMLIT_SERVER_PORT=8051
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# ---------------- HEALTH CHECK ----------------
HEALTHCHECK CMD curl --fail http://localhost:8051 || exit 1

# ---------------- START COMMAND ----------------
CMD ["streamlit", "run", "app.py", "--server.port=8051", "--server.address=0.0.0.0"]