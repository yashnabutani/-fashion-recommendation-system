import streamlit as st
import pandas as pd
import os
from urllib.parse import quote

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Personalized Fashion Recommendation",
    page_icon="👗",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("👗 Personalized Fashion Recommendation System")
st.write(
    "Find fashion products based on your preferences."
)

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


# Remove duplicate product IDs
df = df.drop_duplicates(subset=["id"])


# =========================================================
# SIDEBAR / USER PREFERENCES
# =========================================================

st.sidebar.header("🎯 Select Your Preferences")

# Gender
gender_options = sorted(
    df["gender"].dropna().unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Gender",
    gender_options
)


# Category
category_options = sorted(
    df["masterCategory"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Category",
    category_options
)


# Sub Category
subcategory_options = sorted(
    df["subCategory"].dropna().unique().tolist()
)

selected_subcategory = st.sidebar.selectbox(
    "Sub Category",
    subcategory_options
)


# Article Type
article_options = sorted(
    df["articleType"].dropna().unique().tolist()
)

selected_article = st.sidebar.selectbox(
    "Article Type",
    article_options
)


# Colour
colour_options = sorted(
    df["baseColour"].dropna().unique().tolist()
)

selected_colour = st.sidebar.selectbox(
    "Colour",
    colour_options
)


# Season
season_options = sorted(
    df["season"].dropna().unique().tolist()
)

selected_season = st.sidebar.selectbox(
    "Season",
    season_options
)


# Usage
usage_options = sorted(
    df["usage"].dropna().unique().tolist()
)

selected_usage = st.sidebar.selectbox(
    "Usage",
    usage_options
)


# =========================================================
# RECOMMENDATION FUNCTION
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

    # Start score at 0
    recommendation_df["preference_score"] = 0

    # Gender = 3 points
    recommendation_df.loc[
        recommendation_df["gender"] == gender,
        "preference_score"
    ] += 3

    # Category = 3 points
    recommendation_df.loc[
        recommendation_df["masterCategory"] == category,
        "preference_score"
    ] += 3

    # Sub Category = 2 points
    recommendation_df.loc[
        recommendation_df["subCategory"] == subcategory,
        "preference_score"
    ] += 2

    # Article Type = 3 points
    recommendation_df.loc[
        recommendation_df["articleType"] == article,
        "preference_score"
    ] += 3

    # Colour = 2 points
    recommendation_df.loc[
        recommendation_df["baseColour"] == colour,
        "preference_score"
    ] += 2

    # Season = 1 point
    recommendation_df.loc[
        recommendation_df["season"] == season,
        "preference_score"
    ] += 1

    # Usage = 2 points
    recommendation_df.loc[
        recommendation_df["usage"] == usage,
        "preference_score"
    ] += 2

    # Sort by highest score
    recommendation_df = recommendation_df.sort_values(
        by="preference_score",
        ascending=False
    )

    # Return top 5
    return recommendation_df.head(5)

# =========================================================
# FASHION PLACEHOLDER FUNCTION
# =========================================================

def get_fashion_placeholder(
    category,
    article_type,
    product_id
):

    category = str(category).lower()
    article_type = str(article_type).lower()

    # ---------------------------------------------
    # Decide emoji based on product
    # ---------------------------------------------

    if "shoe" in article_type or "footwear" in category:

        emoji = "👟"
        title = "FASHION SHOES"

    elif "bag" in article_type or "bag" in category:

        emoji = "👜"
        title = "FASHION BAG"

    elif (
        "dress" in article_type
        or "dress" in category
    ):

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

    # ---------------------------------------------
    # Create placeholder text
    # ---------------------------------------------

    text = (
        f"{emoji}  {title}\\n"
        f"Product #{product_id}"
    )

    # Encode text for URL
    encoded_text = quote(text)

    # ---------------------------------------------
    # Placeholder image URL
    # ---------------------------------------------

    image_url = (
        f"https://placehold.co/500x600"
        f"/f5f3ff/4f46e5"
        f"?text={encoded_text}"
    )

    return image_url


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

        st.write(
            f"**Gender:** {selected_gender}"
        )

        st.write(
            f"**Category:** {selected_category}"
        )

        st.write(
            f"**Sub Category:** {selected_subcategory}"
        )

        st.write(
            f"**Article Type:** {selected_article}"
        )

    with col2:

        st.write(
            f"**Colour:** {selected_colour}"
        )

        st.write(
            f"**Season:** {selected_season}"
        )

        st.write(
            f"**Usage:** {selected_usage}"
        )

    st.divider()

    # =====================================================
    # RECOMMENDED PRODUCTS
    # =====================================================

    st.header("🎯 Recommended Products")

    columns = st.columns(5)

    for index, (_, product) in enumerate(
        recommendations.iterrows()
    ):

        with columns[index]:

            # ---------------------------------------------
            # PRODUCT INFORMATION
            # ---------------------------------------------

            product_name = product["productDisplayName"]

            product_id = product["id"]

            category = product["masterCategory"]

            article_type = product["articleType"]

            # ---------------------------------------------
            # CREATE FASHION PLACEHOLDER
            # ---------------------------------------------

            image_url = get_fashion_placeholder(
                category,
                article_type,
                product_id
            )

            # ---------------------------------------------
            # DISPLAY IMAGE
            # ---------------------------------------------

            st.image(
                image_url,
                use_container_width=True
            )

            # ---------------------------------------------
            # PRODUCT NAME
            # ---------------------------------------------

            st.markdown(
                f"**{product_name}**"
            )

            # ---------------------------------------------
            # PRODUCT ID
            # ---------------------------------------------

            st.write(
                f"Product ID: `{product_id}`"
            )

            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            score = int(
                product["preference_score"]
            )

            st.write(
                f"⭐ Preference Score: **{score}/16**"
            )



# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "👗 Personalized Fashion Recommendation System | "
    "Machine Learning Project"
)
