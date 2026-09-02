
import streamlit as st
import pandas as pd
import os
from PIL import Image


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personalized Fashion Recommendation",
    page_icon="👗",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("👗 Personalized Fashion Recommendation System")

st.write(
    "Select your fashion preferences below and get personalized "
    "product recommendations."
)

st.divider()


# ============================================================
# FIND DATASET
# ============================================================

# Possible dataset locations
possible_csv_paths = [
    "/content/drive/MyDrive/Fashion Project/Fashion ML Project/dataset/styles.csv",
    "dataset/styles.csv",
    "./dataset/styles.csv",
    "styles.csv",
    "./styles.csv"
]

CSV_PATH = None

for path in possible_csv_paths:
    if os.path.exists(path):
        CSV_PATH = path
        break


# ============================================================
# FIND IMAGE FOLDER
# ============================================================

possible_image_paths = [
    "/content/drive/MyDrive/Fashion Project/Fashion ML Project/dataset/images",
    "dataset/images",
    "./dataset/images",
    "images",
    "./images"
]

IMAGE_PATH = None

for path in possible_image_paths:
    if os.path.exists(path):
        IMAGE_PATH = path
        break


# ============================================================
# CHECK DATASET
# ============================================================

if CSV_PATH is None:

    st.error("❌ styles.csv was not found.")

    st.write("Your project should have this structure:")

    st.code(
        """
Fashion ML Project/
│
├── app.py
│
├── requirements.txt
│
└── dataset/
    ├── styles.csv
    └── images/
        ├── 15970.jpg
        ├── 39386.jpg
        ├── ...
        """
    )

    st.stop()


# ============================================================
# LOAD DATASET
# ============================================================

@st.cache_data
def load_dataset(path):

    data = pd.read_csv(
        path,
        engine="python",
        on_bad_lines="skip"
    )

    return data


try:

    fashion_df = load_dataset(CSV_PATH)

except Exception as e:

    st.error("❌ Error loading styles.csv")
    st.exception(e)
    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

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


missing_columns = [
    column
    for column in required_columns
    if column not in fashion_df.columns
]


if missing_columns:

    st.error(
        "❌ Missing columns in styles.csv:"
    )

    st.write(missing_columns)

    st.stop()


# Make a copy
fashion_df = fashion_df.copy()


# Convert columns to strings
text_columns = [
    "gender",
    "masterCategory",
    "subCategory",
    "articleType",
    "baseColour",
    "season",
    "usage",
    "productDisplayName"
]


for column in text_columns:

    fashion_df[column] = (
        fashion_df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )


# Remove duplicate product IDs
fashion_df = fashion_df.drop_duplicates(
    subset=["id"]
).reset_index(drop=True)

# Keep only products that have an available image
if IMAGE_PATH is not None:
    def image_exists(product_id):
        extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]

        for extension in extensions:
            image_file = os.path.join(
                IMAGE_PATH,
                str(int(product_id)) + extension
            )

            if os.path.exists(image_file):
                return True

        return False

    fashion_df["has_image"] = fashion_df["id"].apply(image_exists)

    fashion_df = fashion_df[
        fashion_df["has_image"] == True
    ].copy()

    fashion_df = fashion_df.drop(
        columns=["has_image"]
    )

    fashion_df = fashion_df.reset_index(drop=True)


# ============================================================
# DATASET INFORMATION
# ============================================================

with st.expander("📊 Dataset Information"):

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Products",
            len(fashion_df)
        )

    with col2:

        st.metric(
            "Categories",
            fashion_df["masterCategory"].nunique()
        )

    with col3:

        st.metric(
            "Genders",
            fashion_df["gender"].nunique()
        )


# ============================================================
# GET DROPDOWN VALUES
# ============================================================

genders = sorted(
    fashion_df["gender"].unique()
)

categories = sorted(
    fashion_df["masterCategory"].unique()
)

subcategories = sorted(
    fashion_df["subCategory"].unique()
)

article_types = sorted(
    fashion_df["articleType"].unique()
)

colours = sorted(
    fashion_df["baseColour"].unique()
)

seasons = sorted(
    fashion_df["season"].unique()
)

usages = sorted(
    fashion_df["usage"].unique()
)


# ============================================================
# USER PREFERENCES
# ============================================================

st.header("👤 Select Your Preferences")


col1, col2 = st.columns(2)


with col1:

    gender = st.selectbox(
        "Gender",
        genders
    )

    category = st.selectbox(
        "Category",
        categories
    )

    subcategory = st.selectbox(
        "Sub Category",
        subcategories
    )

    article_type = st.selectbox(
        "Article Type",
        article_types
    )


with col2:

    colour = st.selectbox(
        "Colour",
        colours
    )

    season = st.selectbox(
        "Season",
        seasons
    )

    usage = st.selectbox(
        "Usage",
        usages
    )


st.divider()


# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def personalized_fashion_recommendation(
    gender,
    category,
    subcategory,
    article_type,
    colour,
    season,
    usage,
    number_of_recommendations=5
):

    data = fashion_df.copy()

    # Start score
    data["preference_score"] = 0

    # --------------------------------------------------------
    # Gender
    # --------------------------------------------------------

    data.loc[
        data["gender"] == gender,
        "preference_score"
    ] += 3


    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    data.loc[
        data["masterCategory"] == category,
        "preference_score"
    ] += 3


    # --------------------------------------------------------
    # Sub Category
    # --------------------------------------------------------

    data.loc[
        data["subCategory"] == subcategory,
        "preference_score"
    ] += 2


    # --------------------------------------------------------
    # Article Type
    # --------------------------------------------------------

    data.loc[
        data["articleType"] == article_type,
        "preference_score"
    ] += 3


    # --------------------------------------------------------
    # Colour
    # --------------------------------------------------------

    data.loc[
        data["baseColour"] == colour,
        "preference_score"
    ] += 2


    # --------------------------------------------------------
    # Season
    # --------------------------------------------------------

    data.loc[
        data["season"] == season,
        "preference_score"
    ] += 1


    # --------------------------------------------------------
    # Usage
    # --------------------------------------------------------

    data.loc[
        data["usage"] == usage,
        "preference_score"
    ] += 2


    # --------------------------------------------------------
    # Sort by score
    # --------------------------------------------------------

    data = data.sort_values(
        by=[
            "preference_score",
            "id"
        ],
        ascending=[
            False,
            True
        ]
    )


    # --------------------------------------------------------
    # Take recommendations
    # --------------------------------------------------------

    recommendations = data.head(
        number_of_recommendations
    ).copy()


    return recommendations


# ============================================================
# IMAGE FUNCTION
# ============================================================

def find_product_image(product_id):

    if IMAGE_PATH is None:

        return None


    extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".JPG",
        ".JPEG",
        ".PNG"
    ]


    for extension in extensions:

        image_file = os.path.join(
            IMAGE_PATH,
            str(int(product_id)) + extension
        )


        if os.path.exists(image_file):

            return image_file


    return None


# ============================================================
# RECOMMEND BUTTON
# ============================================================

if st.button(
    "🎯 Recommend Fashion Products",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "🔍 Finding the best fashion recommendations..."
    ):

        recommendations = personalized_fashion_recommendation(

            gender=gender,

            category=category,

            subcategory=subcategory,

            article_type=article_type,

            colour=colour,

            season=season,

            usage=usage,

            number_of_recommendations=5
        )


    # ========================================================
    # DISPLAY USER PREFERENCES
    # ========================================================

    st.success(
        "✅ Recommendations generated successfully!"
    )


    st.header("👤 Your Preferences")


    preference_col1, preference_col2 = st.columns(2)


    with preference_col1:

        st.write("**Gender:**", gender)

        st.write("**Category:**", category)

        st.write(
            "**Sub Category:**",
            subcategory
        )

        st.write(
            "**Article Type:**",
            article_type
        )


    with preference_col2:

        st.write(
            "**Colour:**",
            colour
        )

        st.write(
            "**Season:**",
            season
        )

        st.write(
            "**Usage:**",
            usage
        )


    st.divider()


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.header("🎯 Recommended Products")


    # Create 5 columns
    product_columns = st.columns(
        len(recommendations)
    )


    for column, (_, product) in zip(
        product_columns,
        recommendations.iterrows()
    ):

        with column:

            product_id = product["id"]

            image_file = find_product_image(
                product_id
            )


            # ------------------------------------------------
            # Display image
            # ------------------------------------------------

            if image_file is not None:

                try:

                    image = Image.open(
                        image_file
                    )

                    st.image(
                        image,
                        use_container_width=True
                    )

                except Exception:

                    st.warning(
                        "⚠️ Image could not be opened."
                    )

            else:

                st.info(
                    "🖼️ Image not available"
                )


            # ------------------------------------------------
            # Product name
            # ------------------------------------------------

            st.write(
                f"**{product['productDisplayName']}**"
            )


            # ------------------------------------------------
            # Product ID
            # ------------------------------------------------

            st.write(
                f"Product ID: `{int(product_id)}`"
            )


            # ------------------------------------------------
            # Score
            # ------------------------------------------------

            st.write(
                f"⭐ Preference Score: "
                f"**{product['preference_score']}/16**"
            )


    # ========================================================
    # PRODUCT DETAILS
    # ========================================================

    st.divider()

    st.header("📋 Product Details")


    display_columns = [
        "id",
        "gender",
        "masterCategory",
        "subCategory",
        "articleType",
        "baseColour",
        "season",
        "usage",
        "productDisplayName",
        "preference_score"
    ]


    display_data = recommendations[
        display_columns
    ].reset_index(drop=True)


    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "👗 Personalized Fashion Recommendation System | "
    "Machine Learning Project"
)
