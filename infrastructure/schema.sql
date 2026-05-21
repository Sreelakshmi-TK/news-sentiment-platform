CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(255),
    author VARCHAR(255),
    title TEXT NOT NULL,
    description TEXT,
    article_url TEXT,
    image_url TEXT,
    published_at TIMESTAMP,
    content TEXT,
    sentiment_label VARCHAR(50),
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);