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


# ---------------- DATABASE ---------------- #

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
    FROM newss_articles
    ORDER BY id DESC
    LIMIT 50
    """

    dataframe = pd.read_sql(query, connection)

    connection.close()

    return dataframe


# ---------------- UI HEADER ---------------- #

st.title("News Sentiment Analysis Dashboard")

st.markdown(
    """
    Real-time sentiment analytics dashboard powered by
    AWS Lambda, PostgreSQL, Amazon S3, EventBridge,
    Streamlit, and NewsAPI.
    """
)

# ---------------- LOAD DATA ---------------- #

dataframe = fetch_news_data()

if dataframe.empty:
    st.warning("No news articles found in database.")
    st.stop()

# ---------------- DATA CLEANING ---------------- #

dataframe["published_at"] = pd.to_datetime(
    dataframe["published_at"]
)

dataframe["published_at"] = dataframe[
    "published_at"
].dt.strftime("%Y-%m-%d %H:%M")

# ---------------- METRICS ---------------- #

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

avg_sentiment = round(
    dataframe["sentiment_score"].mean(),
    2
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Articles", total_articles)
col2.metric("Positive", positive_count)
col3.metric("Negative", negative_count)
col4.metric("Neutral", neutral_count)
col5.metric("Avg Sentiment", avg_sentiment)

st.divider()

# ---------------- CHARTS ---------------- #

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    sentiment_chart = px.pie(
        dataframe,
        names="sentiment_label",
        title="Sentiment Distribution",
        hole=0.45
    )

    st.plotly_chart(
        sentiment_chart,
        use_container_width=True
    )

with chart_col2:
    sentiment_bar = px.histogram(
        dataframe,
        x="sentiment_label",
        title="Sentiment Frequency",
        text_auto=True
    )

    st.plotly_chart(
        sentiment_bar,
        use_container_width=True
    )

st.divider()

# ---------------- FILTERS ---------------- #

st.subheader("News Analytics Table")

filter_col1, filter_col2 = st.columns(2)

sentiment_filter = filter_col1.selectbox(
    "Filter by Sentiment",
    ["All", "positive", "negative", "neutral"]
)

search_query = filter_col2.text_input(
    "Search Article Title"
)

filtered_dataframe = dataframe.copy()

if sentiment_filter != "All":
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["sentiment_label"]
        == sentiment_filter
    ]

if search_query:
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["title"]
        .str.contains(search_query, case=False)
    ]

# ---------------- SENTIMENT COLORS ---------------- #

def color_sentiment(value):
    if value == "positive":
        return "background-color: #163d1b; color: #7CFC8A;"
    elif value == "negative":
        return "background-color: #3d1616; color: #ff8080;"
    elif value == "neutral":
        return "background-color: #2f2f2f; color: #d3d3d3;"
    return ""


display_dataframe = filtered_dataframe[
    [
        "published_at",
        "source_name",
        "title",
        "sentiment_label",
        "sentiment_score",
        "article_url"
    ]
]

styled_dataframe = display_dataframe.style.map(
    color_sentiment,
    subset=["sentiment_label"]
)

# ---------------- TABLE ---------------- #

st.dataframe(
    styled_dataframe,
    use_container_width=True,
    hide_index=True,
    height=650
)

# ---------------- FOOTER ---------------- #

st.caption(
    "Auto-refresh enabled every 5 minutes"
)