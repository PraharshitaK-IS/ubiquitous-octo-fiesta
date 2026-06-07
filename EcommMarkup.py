import streamlit as st
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Sneaker Store",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SAMPLE PRODUCT DATA
# In a real ecommerce app, this would come from a database.
# ============================================================

PRODUCTS = [
    {
        "id": 1,
        "code": "12678ASFG",
        "name": "Canvas Hightop Sneaker - Yellow",
        "category": "Sneakers",
        "gender": "Men",
        "price": 50,
        "euro_price": 45,
        "old_price": 83,
        "old_euro_price": 79,
        "discount": 30,
        "description": (
            "A bold canvas hightop sneaker with a lightweight sole, contrast laces, "
            "and streetwear-inspired styling. Designed for casual wear and everyday comfort."
        ),
        "colors": {
            "Red": "#e53935",
            "Yellow": "#ffb629",
            "Blue": "#1da1f2",
            "Mint": "#2ecc71",
            "Black": "#111111",
        },
        "sizes": ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10"],
        "rating": 4.5,
        "reviews": [
            {
                "name": "Adrian007",
                "rating": 5,
                "date": "17 February 2022 / 15:00",
                "text": "Great color, comfortable fit, and the design looks better than expected.",
            },
            {
                "name": "SarahMTX",
                "rating": 4,
                "date": "29 January 2022 / 18:25",
                "text": "Good sneaker for casual wear. Runs slightly narrow but looks excellent.",
            },
        ],
    },
    {
        "id": 2,
        "code": "88910BLK",
        "name": "Urban Lowtop Sneaker - Black",
        "category": "Sneakers",
        "gender": "Woman",
        "price": 64,
        "euro_price": 58,
        "old_price": 90,
        "old_euro_price": 82,
        "discount": 20,
        "description": "Minimal lowtop sneaker with a clean silhouette and durable rubber sole.",
        "colors": {
            "Black": "#111111",
            "White": "#f5f5f5",
            "Blue": "#1da1f2",
        },
        "sizes": ["UK 4", "UK 5", "UK 6", "UK 7", "UK 8"],
        "rating": 4.2,
        "reviews": [],
    },
    {
        "id": 3,
        "code": "KID2024RED",
        "name": "Kids Play Sneaker - Red",
        "category": "Kids",
        "gender": "Kids",
        "price": 35,
        "euro_price": 32,
        "old_price": 50,
        "old_euro_price": 45,
        "discount": 15,
        "description": "Lightweight kids sneaker with flexible sole and easy lace support.",
        "colors": {
            "Red": "#e53935",
            "Yellow": "#ffb629",
            "Blue": "#1da1f2",
        },
        "sizes": ["UK 1", "UK 2", "UK 3", "UK 4"],
        "rating": 4.7,
        "reviews": [],
    },
]


# ============================================================
# SESSION STATE
# Stores cart, wishlist, selected page, and user-generated reviews.
# ============================================================

def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "product"

    if "selected_product_id" not in st.session_state:
        st.session_state.selected_product_id = 1

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if "wishlist" not in st.session_state:
        st.session_state.wishlist = set()

    if "extra_reviews" not in st.session_state:
        st.session_state.extra_reviews = {}

    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    if "carousel_index" not in st.session_state:
        st.session_state.carousel_index = 0


init_state()


# ============================================================
# GLOBAL CSS
# Most visual styling lives here so the Python code stays clean.
# ============================================================

st.markdown(
    """
    <style>
    /* ---------- App background ---------- */
    [data-testid="stAppViewContainer"] {
        background: #b8d9f0;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        display: none;
    }

    .block-container {
        max-width: 1220px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ---------- Main white ecommerce shell ---------- */
    .store-shell {
        background: white;
        border-radius: 24px;
        box-shadow: 0 26px 45px rgba(28, 95, 140, 0.25);
        overflow: auto;
        min-height: 100%;
    }

    /* ---------- Header ---------- */
    .top-banner {
        height: 58px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e5e5e5;
    }

    .logo-box {
        width: 330px;
        height: 58px;
        background: linear-gradient(135deg, #0097c0, #005a8d);
        color: white;
        font-weight: 900;
        font-size: 20px;
        display: flex;
        align-items: center;
        padding-left: 45px;
        clip-path: polygon(0 0, 86% 0, 100% 50%, 86% 100%, 0 100%);
        letter-spacing: 0.5px;
    }

    .nav-spacer {
        flex: 1;
    }

    .small-top-text {
        color: #222;
        font-size: 11px;
        margin-right: 24px;
    }

    .store-body {
        padding: 28px 72px 60px 72px;
        display: block;
    }

    .breadcrumb {
        color: #666;
        font-size: 12px;
        margin-bottom: 28px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* ---------- Product image panel ---------- */
    .image-panel {
        position: relative;
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        min-height: 480px;
        border-radius: 16px;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.05);
    }

    .discount-ribbon {
        position: absolute;
        top: 0;
        left: 0;
        width: 210px;
        height: 105px;
        background: linear-gradient(135deg, #0097c0, #006d94);
        clip-path: polygon(0 0, 100% 0, 0 100%);
        color: white;
        font-weight: 900;
        font-size: 38px;
        padding: 18px 0 0 15px;
        line-height: 0.85;
        z-index: 5;
    }

    .discount-ribbon span {
        font-size: 18px;
    }

    .slider-arrow-left,
    .slider-arrow-right {
        position: absolute;
        top: 48%;
        font-size: 42px;
        color: #0097c0;
        font-weight: 200;
    }

    .slider-arrow-left {
        left: 16px;
    }

    .slider-arrow-right {
        right: 16px;
    }

    .slider-dots {
        display: flex;
        justify-content: center;
        gap: 9px;
        margin-top: -20px;
        margin-bottom: 20px;
    }

    .dot {
        width: 42px;
        height: 3px;
        background: #d5d5d5;
        border-radius: 999px;
    }

    .dot.active {
        background: #0097c0;
    }

    /* ---------- Product details ---------- */
    .product-code {
        font-size: 11px;
        color: #666;
        margin-bottom: 8px;
    }

    .product-title {
        font-size: 32px;
        line-height: 1.2;
        text-transform: uppercase;
        color: #0a5a75;
        font-weight: 950;
        margin-bottom: 16px;
        letter-spacing: -0.5px;
    }

    .product-description {
        font-size: 14px;
        line-height: 1.8;
        color: #555;
        max-width: 440px;
        margin-bottom: 28px;
    }

    .section-line {
        border-top: 1px solid #e3e3e3;
        padding-top: 16px;
        margin-top: 16px;
        margin-bottom: 14px;
    }

    .label {
        color: #555;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .color-chip {
        display: inline-block;
        width: 18px;
        height: 18px;
        margin-right: 7px;
        border-radius: 2px;
        border: 1px solid #ddd;
    }

    .price {
        font-size: 42px;
        font-weight: 950;
        color: #0097c0;
        letter-spacing: 1px;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .old-price {
        font-size: 24px;
        color: #b6b6b6;
        font-weight: 900;
        text-decoration: line-through;
        margin-bottom: 18px;
    }

    .shipping {
        margin-top: 22px;
        font-size: 11px;
        color: #555;
        line-height: 1.5;
    }

    .shipping strong {
        color: #444;
        font-size: 12px;
    }

    /* ---------- Reviews ---------- */
    .review-title {
        font-size: 13px;
        font-weight: 900;
        color: #111;
        margin-top: 35px;
        padding-bottom: 12px;
        border-bottom: 1px solid #e5e5e5;
    }

    .review-card {
        padding: 14px 0;
        border-bottom: 1px solid #efefef;
    }

    .review-head {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        font-size: 11px;
        color: #555;
        font-weight: 800;
    }

    .stars {
        color: #ffc400;
        letter-spacing: 1px;
    }

    .review-text {
        color: #666;
        font-size: 11px;
        line-height: 1.6;
        max-width: 670px;
        margin-top: 8px;
    }

    /* ---------- Cards for catalog/cart ---------- */
    .product-card {
        border: 1px solid #e0e8f0;
        border-radius: 12px;
        padding: 16px;
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        min-height: 320px;
        transition: all 0.3s ease;
    }

    .product-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }

    .product-card-name {
        color: #0c3d5e;
        font-size: 16px;
        font-weight: 900;
        margin-top: 14px;
        min-height: 48px;
        line-height: 1.3;
    }

    .product-card-price {
        color: #0097c0;
        font-size: 24px;
        font-weight: 950;
        margin: 10px 0 12px 0;
    }

    .cart-box {
        border: 1px solid #e5e5e5;
        padding: 18px;
        border-radius: 18px;
        margin-bottom: 14px;
    }

    .total-box {
        background: #f4fbff;
        border: 1px solid #d7f3ff;
        padding: 24px;
        border-radius: 18px;
    }

    .help-bubble {
        position: fixed;
        right: 95px;
        bottom: 90px;
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #0097c0, #006d94);
        color: white;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: 950;
        box-shadow: 0 12px 28px rgba(0, 151, 192, 0.4);
        z-index: 9999;
    }

    /* ---------- Streamlit button styling ---------- */
    div[data-testid="stButton"] > button {
        border-radius: 8px;
        border: 2px solid #0097c0;
        background: #0097c0;
        color: white;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        padding: 0.65rem 1.2rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }

    div[data-testid="stButton"] > button:hover {
        border: 2px solid #006d94;
        background: #006d94;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 151, 192, 0.3);
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label {
        font-size: 12px;
        color: #555;
        font-weight: 700;
        text-transform: uppercase;
    }

    @media screen and (max-width: 900px) {
        .store-body {
            padding: 24px;
        }

        .logo-box {
            width: 220px;
            padding-left: 24px;
            font-size: 16px;
        }

        .help-bubble {
            right: 24px;
            bottom: 24px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_product(product_id):
    """Return one product dictionary by product id."""
    return next(product for product in PRODUCTS if product["id"] == product_id)


def format_price(value):
    """Simple price formatter."""
    return f"$ {value}"


def render_stars(rating):
    """Convert rating number into stars."""
    full_stars = int(rating)
    return "★" * full_stars + "☆" * (5 - full_stars)


def navigate(page):
    """Change current app page."""
    st.session_state.page = page
    st.rerun()


def add_to_cart(product, color, size, quantity):
    """Add selected product configuration to cart."""
    if not size:
        st.warning("Please choose a size before adding to cart.")
        return

    cart_item = {
        "product_id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "color": color,
        "size": size,
        "quantity": quantity,
        "added_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    }

    st.session_state.cart.append(cart_item)
    st.success("Added to cart.")


def toggle_wishlist(product_id):
    """Add/remove product from wishlist."""
    if product_id in st.session_state.wishlist:
        st.session_state.wishlist.remove(product_id)
        st.info("Removed from wishlist.")
    else:
        st.session_state.wishlist.add(product_id)
        st.success("Added to wishlist.")


def cart_total():
    """Calculate cart total."""
    return sum(item["price"] * item["quantity"] for item in st.session_state.cart)


def sneaker_svg(primary_color="#ffb629"):
    """
    Render a simple sneaker illustration using SVG.
    This avoids needing external image files.
    You can replace this with st.image("your-product-image.png").
    """
    return f"<svg width=\"430\" height=\"300\" viewBox=\"0 0 430 300\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><ellipse cx=\"214\" cy=\"254\" rx=\"155\" ry=\"18\" fill=\"rgba(0,0,0,0.10)\"/><path d=\"M82 214 C132 205, 170 165, 200 90 C207 72, 224 66, 246 72 L324 90 C347 95, 360 112, 365 137 L378 196 C382 218, 367 236, 344 238 L111 240 C91 240, 74 232, 82 214Z\" fill=\"{primary_color}\" stroke=\"#333\" stroke-width=\"2\"/><path d=\"M199 89 L322 117 L339 196 L154 202 C173 165, 190 125, 199 89Z\" fill=\"{primary_color}\"/><path d=\"M224 73 C259 77, 294 86, 330 98 C324 72, 285 55, 239 52 C224 51, 215 61, 224 73Z\" fill=\"#151515\"/><path d=\"M91 215 C161 216, 261 206, 380 194 L382 210 C348 235, 209 251, 85 236 C77 231, 78 221, 91 215Z\" fill=\"#f7f7f7\" stroke=\"#333\" stroke-width=\"1.5\"/><path d=\"M105 239 C180 250, 301 242, 374 217\" stroke=\"#999\" stroke-width=\"2\"/><path d=\"M222 100 L177 201\" stroke=\"white\" stroke-width=\"9\" stroke-linecap=\"round\"/><path d=\"M252 105 L209 201\" stroke=\"white\" stroke-width=\"9\" stroke-linecap=\"round\"/><path d=\"M291 119 L274 182\" stroke=\"#e67e22\" stroke-width=\"2\" stroke-dasharray=\"8 8\"/><path d=\"M184 111 L141 119\" stroke=\"white\" stroke-width=\"6\" stroke-linecap=\"round\"/><path d=\"M176 132 L135 139\" stroke=\"white\" stroke-width=\"6\" stroke-linecap=\"round\"/><path d=\"M166 153 L125 162\" stroke=\"white\" stroke-width=\"6\" stroke-linecap=\"round\"/><path d=\"M156 176 L114 184\" stroke=\"white\" stroke-width=\"6\" stroke-linecap=\"round\"/><path d=\"M334 94 C346 78, 353 70, 361 69\" stroke=\"#aaa\" stroke-width=\"8\" stroke-linecap=\"round\"/></svg>"


def render_product_image(product, selected_color):
    """Render product image section with color carousel."""
    color_names = list(product["colors"].keys())
    num_colors = len(color_names)
    
    # Ensure carousel_index is valid
    if st.session_state.carousel_index >= num_colors:
        st.session_state.carousel_index = 0
    
    current_color_name = color_names[st.session_state.carousel_index]
    color_hex = product["colors"][current_color_name]
    
    # Create carousel controls with arrow buttons on sides
    carousel_cols = st.columns([0.8, 10, 0.8])
    
    with carousel_cols[0]:
        st.write("")
        if st.button("◄", key="prev_color", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index - 1) % num_colors
            st.rerun()
    
    with carousel_cols[1]:
        st.markdown(
            f"""
            <div class="image-panel">
                <div class="discount-ribbon">{product["discount"]}<span>%</span><br><span>OFF</span></div>
                {sneaker_svg(color_hex)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Render clickable dots below the image
        st.markdown('<div class="slider-dots">', unsafe_allow_html=True)
        dot_cols = st.columns(num_colors)
        for i, dot_col in enumerate(dot_cols):
            with dot_col:
                is_active = i == st.session_state.carousel_index
                button_text = "●" if is_active else "○"
                if st.button(button_text, key=f"dot_{i}", use_container_width=True):
                    st.session_state.carousel_index = i
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with carousel_cols[2]:
        st.write("")
        if st.button("►", key="next_color", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % num_colors
            st.rerun()


def render_header():
    """Render logo, navigation, search, and cart shortcut."""
    st.markdown('<div class="top-banner"><div class="logo-box">✦ Shoes Galore</div>', unsafe_allow_html=True)

    nav_cols = st.columns([1.2, 1.2, 1.2, 1.2, 3.2, 1.5, 1.2])

    with nav_cols[0]:
        if st.button("MEN", use_container_width=True):
            st.session_state.page = "catalog"
            st.session_state.search_query = "Men"
            st.rerun()

    with nav_cols[1]:
        if st.button("WOMAN", use_container_width=True):
            st.session_state.page = "catalog"
            st.session_state.search_query = "Woman"
            st.rerun()

    with nav_cols[2]:
        if st.button("KIDS", use_container_width=True):
            st.session_state.page = "catalog"
            st.session_state.search_query = "Kids"
            st.rerun()

    with nav_cols[3]:
        if st.button("SALE", use_container_width=True):
            st.session_state.page = "catalog"
            st.session_state.search_query = "sale"
            st.rerun()

    with nav_cols[4]:
        query = st.text_input(
            "Search product",
            value=st.session_state.search_query,
            placeholder="search product",
            label_visibility="collapsed",
        )
        st.session_state.search_query = query

    with nav_cols[5]:
        if st.button(f"CART ({len(st.session_state.cart)})", use_container_width=True):
            navigate("cart")

    with nav_cols[6]:
        if st.button("LOGIN", use_container_width=True):
            navigate("login")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PRODUCT DETAIL PAGE
# ============================================================

def product_detail_page():
    product = get_product(st.session_state.selected_product_id)
    
    # Reset carousel when viewing a new product
    if "current_product_id" not in st.session_state or st.session_state.current_product_id != product["id"]:
        st.session_state.carousel_index = 0
        st.session_state.current_product_id = product["id"]

    st.markdown(
        '<div class="breadcrumb">&lt; Back &nbsp;&nbsp; Men / Lifestyle / Sneaker / High Top</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.2, 1.0], gap="large")

    with right:
        st.markdown(
            f"""
            <div class="product-code">PRODUCT CODE : {product["code"]}</div>
            <div class="product-title">{product["name"]}</div>
            <div class="product-description">{product["description"]}</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-line"><div class="label">Color Available</div></div>', unsafe_allow_html=True)

        selected_color = st.selectbox(
            "Choose color",
            list(product["colors"].keys()),
            label_visibility="collapsed",
        )

        color_chips = "".join(
            f'<span class="color-chip" style="background:{hex_code};"></span>'
            for hex_code in product["colors"].values()
        )
        st.markdown(color_chips, unsafe_allow_html=True)

        st.markdown('<div class="section-line"><div class="label">Size</div></div>', unsafe_allow_html=True)

        size_col, guide_col = st.columns([2.5, 0.5])
        with size_col:
            selected_size = st.selectbox(
                "Choose your size",
                [""] + product["sizes"],
                label_visibility="collapsed",
                placeholder="Choose your size",
            )

        with guide_col:
            st.caption("SIZE GUIDE")

        st.markdown(
            f"""
            <div class="price">$ {product["price"]} / € {product["euro_price"]}</div>
            <div class="old-price">$ {product["old_price"]} / € {product["old_euro_price"]}</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div style="margin: 20px 0;\"></div>', unsafe_allow_html=True)

        quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1, step=1)

        action_col_1, action_col_2 = st.columns([1, 1])

        with action_col_1:
            if st.button("ADD TO CART", use_container_width=True):
                add_to_cart(product, selected_color, selected_size, quantity)

        with action_col_2:
            wishlist_label = "REMOVE WISHLIST" if product["id"] in st.session_state.wishlist else "ADD WISHLIST"
            if st.button(wishlist_label, use_container_width=True):
                toggle_wishlist(product["id"])

        st.markdown(
            """
            <div class="shipping">
                <strong>SHIPPING AND RETURN</strong><br>
                Read our Terms and Conditions
            </div>
            """,
            unsafe_allow_html=True,
        )

    with left:
        render_product_image(product, selected_color)

    render_reviews(product)


def render_reviews(product):
    """Render reviews and review form."""
    st.markdown('<div class="review-title">REVIEW</div>', unsafe_allow_html=True)

    all_reviews = product["reviews"] + st.session_state.extra_reviews.get(product["id"], [])

    if not all_reviews:
        st.info("No reviews yet. Be the first to review this product.")

    for review in all_reviews:
        st.markdown(
            f"""
            <div class="review-card">
                <div class="review-head">
                    <div>{review["name"]} &nbsp; <span class="stars">{render_stars(review["rating"])}</span></div>
                    <div>{review["date"]}</div>
                </div>
                <div class="review-text">{review["text"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Write a review"):
        name = st.text_input("Your name")
        rating = st.slider("Rating", 1, 5, 5)
        text = st.text_area("Review")

        if st.button("Submit review"):
            if not name.strip() or not text.strip():
                st.warning("Please enter your name and review.")
            else:
                new_review = {
                    "name": name.strip(),
                    "rating": rating,
                    "date": datetime.now().strftime("%d %B %Y / %H:%M"),
                    "text": text.strip(),
                }

                st.session_state.extra_reviews.setdefault(product["id"], []).append(new_review)
                st.success("Review submitted.")
                st.rerun()


# ============================================================
# CATALOG PAGE
# ============================================================

def catalog_page():
    st.subheader("Product Catalog")

    query = st.session_state.search_query.lower().strip()

    filtered_products = []
    for product in PRODUCTS:
        searchable_text = " ".join(
            [
                product["name"],
                product["category"],
                product["gender"],
                "sale" if product["discount"] > 0 else "",
            ]
        ).lower()

        if query in searchable_text or query == "":
            filtered_products.append(product)

    if not filtered_products:
        st.warning("No products found.")
        return

    cols = st.columns(3)

    for index, product in enumerate(filtered_products):
        with cols[index % 3]:
            default_color = list(product["colors"].values())[0]

            st.markdown(
                f"""
                <div class="product-card">
                    <div style="background:#f2f4f6;border-radius:14px;text-align:center;padding:10px;">
                        {sneaker_svg(default_color)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("View product", key=f"view_{product['id']}", use_container_width=True):
                st.session_state.selected_product_id = product["id"]
                navigate("product")


# ============================================================
# CART PAGE
# ============================================================

def cart_page():
    st.subheader("Shopping Cart")

    if not st.session_state.cart:
        st.info("Your cart is empty.")
        if st.button("Continue shopping"):
            navigate("catalog")
        return

    for index, item in enumerate(st.session_state.cart):
        st.markdown(
            f"""
            <div class="cart-box">
                <strong>{item["name"]}</strong><br>
                Color: {item["color"]} · Size: {item["size"]} · Quantity: {item["quantity"]}<br>
                Price: $ {item["price"]} each<br>
                Added: {item["added_at"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Remove", key=f"remove_{index}"):
            st.session_state.cart.pop(index)
            st.rerun()

    subtotal = cart_total()
    shipping = 5 if subtotal > 0 else 0
    grand_total = subtotal + shipping

    st.markdown(
        f"""
        <div class="total-box">
            <h3>Order Summary</h3>
            Subtotal: <strong>$ {subtotal}</strong><br>
            Shipping: <strong>$ {shipping}</strong><br>
            <hr>
            Total: <strong>$ {grand_total}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    checkout_col, continue_col = st.columns([1, 1])

    with checkout_col:
        if st.button("Proceed to checkout", use_container_width=True):
            navigate("checkout")

    with continue_col:
        if st.button("Continue shopping", use_container_width=True):
            navigate("catalog")


# ============================================================
# CHECKOUT PAGE
# ============================================================

def checkout_page():
    st.subheader("Checkout")

    if not st.session_state.cart:
        st.warning("Your cart is empty.")
        return

    with st.form("checkout_form"):
        st.write("Shipping Details")

        name = st.text_input("Full name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        address = st.text_area("Shipping address")

        payment_method = st.radio(
            "Payment method",
            ["Cash on Delivery", "Credit/Debit Card", "UPI"],
            horizontal=True,
        )

        submitted = st.form_submit_button("Place order")

    if submitted:
        if not name or not email or not phone or not address:
            st.warning("Please fill all checkout details.")
        else:
            st.success("Order placed successfully.")
            st.write(f"Thank you, **{name}**. Your order total is **$ {cart_total() + 5}**.")
            st.session_state.cart = []


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():
    st.subheader("Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Create account"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if email and password:
                st.success("Logged in successfully. This is a demo login.")
            else:
                st.warning("Please enter email and password.")

    with tab2:
        name = st.text_input("Name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Create password", type="password")

        if st.button("Create account"):
            if name and signup_email and signup_password:
                st.success("Account created. This is a demo signup.")
            else:
                st.warning("Please complete all fields.")


# ============================================================
# WISHLIST PAGE
# ============================================================

def wishlist_page():
    st.subheader("Wishlist")

    if not st.session_state.wishlist:
        st.info("Your wishlist is empty.")
        return

    wishlist_products = [
        product for product in PRODUCTS
        if product["id"] in st.session_state.wishlist
    ]

    cols = st.columns(3)

    for index, product in enumerate(wishlist_products):
        with cols[index % 3]:
            default_color = list(product["colors"].values())[0]

            st.markdown(
                f"""
                <div class="product-card">
                    <div style="background:#f2f4f6;border-radius:14px;text-align:center;padding:10px;">
                        {sneaker_svg(default_color)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("View", key=f"wish_view_{product['id']}"):
                st.session_state.selected_product_id = product["id"]
                navigate("product")


# ============================================================
# MAIN APP ROUTER
# ============================================================

st.markdown('<div class="store-shell">', unsafe_allow_html=True)

render_header()

st.markdown('<div class="store-body">', unsafe_allow_html=True)

st.write("")

# Route to selected page
if st.session_state.page == "product":
    product_detail_page()
elif st.session_state.page == "catalog":
    catalog_page()
elif st.session_state.page == "cart":
    cart_page()
elif st.session_state.page == "checkout":
    checkout_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "wishlist":
    wishlist_page()

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="help-bubble">HELP?</div>', unsafe_allow_html=True)