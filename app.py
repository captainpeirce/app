import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================
# CONFIG
# ==========================

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://newsapi.org/v2/top-headlines"

st.set_page_config(
    page_title="Advanced News Dashboard",
    page_icon="📰",
    layout="wide"
)

# ==========================
# CACHED API CALL
# ==========================

@st.cache_data(ttl=300)
def fetch_news(country, category, keyword, page_size):

    params = {
        "apiKey": API_KEY,
        "pageSize": page_size
    }

    if country:
        params["country"] = country

    if category != "All":
        params["category"] = category.lower()

    if keyword:
        params["q"] = keyword

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()

    return None


# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("⚙ Filters")

countries = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp"
}

country_name = st.sidebar.selectbox(
    "Country",
    list(countries.keys())
)

country_code = countries[country_name]

categories = [
    "All",
    "Business",
    "Entertainment",
    "General",
    "Health",
    "Science",
    "Sports",
    "Technology"
]

category = st.sidebar.selectbox(
    "Category",
    categories
)

keyword = st.sidebar.text_input(
    "Search Keywords",
    placeholder="AI, Tesla, Cricket..."
)

article_count = st.sidebar.slider(
    "Number of Articles",
    min_value=5,
    max_value=100,
    value=20
)

refresh = st.sidebar.button("🔄 Refresh News")

# ==========================
# HEADER
# ==========================

st.title("📰 Advanced News Dashboard")
st.markdown("Latest headlines powered by NewsAPI")

# ==========================
# FETCH NEWS
# ==========================

news_data = fetch_news(
    country_code,
    category,
    keyword,
    article_count
)

# ==========================
# DISPLAY NEWS
# ==========================

if news_data and news_data["status"] == "ok":

    articles = news_data.get("articles", [])

    if not articles:
        st.warning("No articles found.")
        st.stop()

    news_df = pd.DataFrame(articles)

    # Sort options
    sort_option = st.selectbox(
        "Sort Articles",
        ["Newest First", "Oldest First"]
    )

    news_df["publishedAt"] = pd.to_datetime(
        news_df["publishedAt"],
        errors="coerce"
    )

    if sort_option == "Newest First":
        news_df = news_df.sort_values(
            by="publishedAt",
            ascending=False
        )
    else:
        news_df = news_df.sort_values(
            by="publishedAt",
            ascending=True
        )

    st.success(f"{len(news_df)} articles found")

    for _, article in news_df.iterrows():

        with st.container():

            col1, col2 = st.columns([1, 3])

            with col1:
                if pd.notna(article.get("urlToImage")):
                    st.image(
                        article["urlToImage"],
                        use_container_width=True
                    )

            with col2:

                st.subheader(article.get("title", "No Title"))

                source = article.get("source", {}).get("name", "Unknown")

                published = article.get("publishedAt")

                if pd.notna(published):
                    published = published.strftime(
                        "%d %b %Y %I:%M %p"
                    )

                st.caption(
                    f"Source: {source} | Published: {published}"
                )

                description = article.get(
                    "description",
                    "No description available."
                )

                st.write(description)

                st.link_button(
                    "Read Full Article",
                    article.get("url")
                )

            st.divider()

else:
    st.error(
        "Failed to fetch news. Check API key or API limits."
    )