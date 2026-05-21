import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="News Sentiment Dashboard",
    layout="wide"
)

st_autorefresh(interval=300000, key="dashboard_refresh")

RDS_HOST = "news-platform-postgres.c1iccwg44xf2.ap-south-1.rds.amazonaws.com"
RDS_PORT = "5432"
RDS_DATABASE = "newsplatformdatabase"
RDS_USERNAME = "postgres"
RDS_PASSWORD = "NewsPlatform123"


def get_database_connection():
    return psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        database=RDS_DATABASE,
        user=RDS_USERNAME,
        password=RDS_PASSWORD
    )


def fetch_news_data():
    connection = get_database_connection()

    query = """
    SELECT
        id,
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
    FROM news_articles
    ORDER BY id DESC
    LIMIT 50
    """

    dataframe = pd.read_sql(query, connection)

    connection.close()

    return dataframe


st.title("News Sentiment Analysis Dashboard")

dataframe = fetch_news_data()

if dataframe.empty:
    st.warning("No news articles found in database.")
    st.stop()

total_articles = len(dataframe)

positive_count = len(
    dataframe[dataframe["sentiment_label"] == "positive"]
)

negative_count = len(
    dataframe[dataframe["sentiment_label"] == "negative"]
)

neutral_count = len(
    dataframe[dataframe["sentiment_label"] == "neutral"]
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Articles", total_articles)
col2.metric("Positive", positive_count)
col3.metric("Negative", negative_count)
col4.metric("Neutral", neutral_count)

sentiment_chart = px.pie(
    dataframe,
    names="sentiment_label",
    title="Sentiment Distribution"
)

st.plotly_chart(sentiment_chart, use_container_width=True)

sentiment_timeline = px.histogram(
    dataframe,
    x="sentiment_label",
    title="Sentiment Frequency"
)

st.plotly_chart(sentiment_timeline, use_container_width=True)

st.subheader("Latest News Articles")

for _, row in dataframe.iterrows():
    with st.container():
        st.markdown(f"### {row['title']}")

        st.write(f"Source: {row['source_name']}")

        st.write(f"Sentiment: {row['sentiment_label']}")

        st.write(f"Score: {row['sentiment_score']}")

        st.write(row["description"])

        st.markdown(
            f"[Read Full Article]({row['article_url']})"
        )

        st.divider()