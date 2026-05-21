FROM python:3.11-slim

WORKDIR /app

COPY dashboard/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/app ./app

EXPOSE 8051

CMD ["streamlit", "run", "app/app.py", "--server.port=8051", "--server.address=0.0.0.0"]