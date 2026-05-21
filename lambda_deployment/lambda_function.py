import json
import os
from datetime import datetime

import boto3
import psycopg2
import requests
from textblob import TextBlob

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = os.getenv("RDS_PORT")
RDS_DATABASE = os.getenv("RDS_DATABASE")
RDS_USERNAME = os.getenv("RDS_USERNAME")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

NEWS_API_URL = (
    f"https://newsapi.org/v2/top-headlines?"
    f"country=in&"
    f"category=technology&"
    f"pageSize=20&"
    f"apiKey={NEWS_API_KEY}"
)


def fetch_news_articles():
    response = requests.get(NEWS_API_URL)
    response.raise_for_status()
    return response.json()


def upload_raw_json_to_s3(news_data):
    s3_client = boto3.client("s3", region_name=AWS_REGION)

    current_time = datetime.utcnow()

    file_key = (
        f"{current_time.year}/"
        f"{current_time.month:02d}/"
        f"{current_time.day:02d}/"
        f"news_{current_time.strftime('%H_%M_%S')}.json"
    )

    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=file_key,
        Body=json.dumps(news_data),
        ContentType="application/json"
    )

    print(f"Raw JSON uploaded to S3: {file_key}")


def analyze_sentiment(text):
    if not text:
        return "neutral", 0.0

    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        label = "positive"
    elif polarity < 0:
        label = "negative"
    else:
        label = "neutral"

    return label, polarity


def insert_articles_into_rds(articles):
    connection = psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        database=RDS_DATABASE,
        user=RDS_USERNAME,
        password=RDS_PASSWORD
    )

    cursor = connection.cursor()

    insert_query = """
    INSERT INTO news_articles (
        source_name,
        author,
        title,
        description,
        article_url,
        image_url,
        published_at,
        content,
        sentiment_label,
        sentiment_score
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")

        sentiment_input = f"{title} {description}"

        sentiment_label, sentiment_score = analyze_sentiment(
            sentiment_input
        )

        values = (
            article.get("source", {}).get("name"),
            article.get("author"),
            title,
            description,
            article.get("url"),
            article.get("urlToImage"),
            article.get("publishedAt"),
            article.get("content"),
            sentiment_label,
            sentiment_score
        )

        cursor.execute(insert_query, values)

    connection.commit()

    cursor.close()
    connection.close()

    print("News articles inserted into RDS successfully")


def lambda_handler(event, context):
    try:
        news_data = fetch_news_articles()

        upload_raw_json_to_s3(news_data)

        articles = news_data.get("articles", [])

        insert_articles_into_rds(articles)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "News pipeline executed successfully",
                    "articles_processed": len(articles)
                }
            )
        }

    except Exception as error:
        print(f"Pipeline error: {str(error)}")

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(error)
                }
            )
        }


if __name__ == "__main__":
    result = lambda_handler({}, {})
    print(result)