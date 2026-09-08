import streamlit as st
import pandas as pd
import os
import html

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Personalized Fashion Recommendation",
    page_icon="👗",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
.product-card {
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 12px;
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.product-visual {
    height: 250px;
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: linear-gradient(135deg, #f5f3ff, #e0e7ff);
    border: 1px solid #ddd6fe;
    margin-bottom: 14px;
}

.product-emoji {
    font-size: 76px;
    line-height: 1;
    margin-bottom: 14px;
}

.product-visual-title {
    font-size: 18px;
    font-weight: 700;
    color: #4338ca;
    letter-spacing: 0.5px;
}

.product-visual-id {
    font-size: 14px;
    color: #6366f1;
    margin-top: 6px;
}

.product-name {
    font-size: 16px;
    font-weight: 700;
    min-height: 54px;
    color: #111827;
}

.score {
    font-size: 14px;
    color: #374151;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("👗 Personalized Fashion Recommendation System")
st.write("Find fashion products based on your preferences.")

# =========================================================
# FIND styles.csv
# =========================================================

possible_csv_paths = [
    "styles.csv",
    "./styles.csv",
    "dataset/styles.csv",
    "./dataset/styles.csv"
]

CSV_PATH = None

for path in possible_csv_paths:
    if os.path.exists(path):
        CSV_PATH = path
        break

if CSV_PATH is None:
    st.error("❌ styles.csv not found.")
    st.stop()

# =========================================================
# LOAD DATASET
# =========================================================

@st.cache_data
def load_dataset(path):
    data = pd.read_csv(
        path,
        engine="python",
        on_bad_lines="skip"
    )
    return data

df = load_dataset(CSV_PATH)

# =========================================================
# CLEAN DATA
# =========================================================

required_columns = [
    "id",
    "gender",
    "masterCategory",
    "subCategory",
    "articleType",
    "baseColour",
    "season",
    "usage",
    "productDisplayName"
]

for column in required_columns:
    if column in df.columns:
        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

df = df.drop_duplicates(subset=["id"])

# =========================================================
# FASHION PLACEHOLDER FUNCTION
# =========================================================

def get_fashion_placeholder(category, article_type, product_id):
    category = str(category).lower()
    article_type = str(article_type).lower()

    if "shoe" in article_type or "footwear" in category:
        emoji = "👟"
        title = "FASHION SHOES"

    elif "bag" in article_type or "bag" in category:
        emoji = "👜"
        title = "FASHION BAG"

    elif "dress" in article_type or "dress" in category:
        emoji = "👗"
        title = "FASHION DRESS"

    elif (
        "shirt" in article_type
        or "top" in article_type
        or "tshirt" in article_type
        or "t-shirt" in article_type
    ):
        emoji = "👕"
        title = "FASHION TOP"

    elif (
        "watch" in article_type
        or "accessories" in category
    ):
        emoji = "⌚"
        title = "ACCESSORY"

    elif (
        "jacket" in article_type
        or "coat" in article_type
        or "blazer" in article_type
    ):
        emoji = "🧥"
        title = "FASHION WEAR"

    elif (
        "jean" in article_type
        or "trouser" in article_type
        or "pant" in article_type
    ):
        emoji = "👖"
        title = "FASHION BOTTOM"

    else:
        emoji = "👗"
        title = "FASHION PRODUCT"

    return emoji, title

# =========================================================
# SIDEBAR / USER PREFERENCES
# =========================================================

st.sidebar.header("🎯 Select Your Preferences")

gender_options = sorted(df["gender"].dropna().unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", gender_options)

category_options = sorted(df["masterCategory"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", category_options)

subcategory_options = sorted(df["subCategory"].dropna().unique().tolist())
selected_subcategory = st.sidebar.selectbox("Sub Category", subcategory_options)

article_options = sorted(df["articleType"].dropna().unique().tolist())
selected_article = st.sidebar.selectbox("Article Type", article_options)

colour_options = sorted(df["baseColour"].dropna().unique().tolist())
selected_colour = st.sidebar.selectbox("Colour", colour_options)

season_options = sorted(df["season"].dropna().unique().tolist())
selected_season = st.sidebar.selectbox("Season", season_options)

usage_options = sorted(df["usage"].dropna().unique().tolist())
selected_usage = st.sidebar.selectbox("Usage", usage_options)

# =========================================================
# RECOMMENDATION FUNCTION - MAXIMUM 10 POINTS
# =========================================================

def recommend_products(
    gender,
    category,
    subcategory,
    article,
    colour,
    season,
    usage
):
    recommendation_df = df.copy()
    recommendation_df["preference_score"] = 0

    # Gender = 2 points
    recommendation_df.loc[
        recommendation_df["gender"] == gender,
        "preference_score"
    ] += 2

    # Category = 2 points
    recommendation_df.loc[
        recommendation_df["masterCategory"] == category,
        "preference_score"
    ] += 2

    # Sub Category = 1 point
    recommendation_df.loc[
        recommendation_df["subCategory"] == subcategory,
        "preference_score"
    ] += 1

    # Article Type = 2 points
    recommendation_df.loc[
        recommendation_df["articleType"] == article,
        "preference_score"
    ] += 2

    # Colour = 1 point
    recommendation_df.loc[
        recommendation_df["baseColour"] == colour,
        "preference_score"
    ] += 1

    # Season = 1 point
    recommendation_df.loc[
        recommendation_df["season"] == season,
        "preference_score"
    ] += 1

    # Usage = 1 point
    recommendation_df.loc[
        recommendation_df["usage"] == usage,
        "preference_score"
    ] += 1

    recommendation_df = recommendation_df.sort_values(
        by="preference_score",
        ascending=False
    )

    return recommendation_df.head(5)

# =========================================================
# GET RECOMMENDATIONS
# =========================================================

if st.sidebar.button("🔍 Get Recommendations"):

    recommendations = recommend_products(
        selected_gender,
        selected_category,
        selected_subcategory,
        selected_article,
        selected_colour,
        selected_season,
        selected_usage
    )

    # =====================================================
    # USER SELECTION SUMMARY
    # =====================================================

    st.subheader("🎯 Your Selected Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Gender:** {selected_gender}")
        st.write(f"**Category:** {selected_category}")
        st.write(f"**Sub Category:** {selected_subcategory}")
        st.write(f"**Article Type:** {selected_article}")

    with col2:
        st.write(f"**Colour:** {selected_colour}")
        st.write(f"**Season:** {selected_season}")
        st.write(f"**Usage:** {selected_usage}")

    st.divider()

    # =====================================================
    # RECOMMENDED PRODUCTS
    # =====================================================

    st.header("🎯 Recommended Products")

    columns = st.columns(5)

    for index, (_, product) in enumerate(recommendations.iterrows()):

        with columns[index]:

            product_name = html.escape(
                str(product["productDisplayName"])
            )

            product_id = html.escape(
                str(product["id"])
            )

            category = product["masterCategory"]
            article_type = product["articleType"]

            emoji, title = get_fashion_placeholder(
                category,
                article_type,
                product_id
            )

            # -------------------------------------------------
            # ATTRACTIVE LOCAL PLACEHOLDER
            # No external image service is required.
            # -------------------------------------------------

            st.markdown(
                f"""
                <div class="product-card">
                    <div class="product-visual">
                        <div class="product-emoji">{emoji}</div>
                        <div class="product-visual-title">{title}</div>
                        <div class="product-visual-id">
                            Product #{product_id}
                        </div>
                    </div>

                    <div class="product-name">
                        {product_name}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write(f"Product ID: `{product_id}`")

            score = int(product["preference_score"])

            st.markdown(
                f'<div class="score">⭐ Preference Score: '
                f'<strong>{score}/10</strong></div>',
                unsafe_allow_html=True
            )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "👗 Personalized Fashion Recommendation System | "
    "Machine Learning Project"
)
