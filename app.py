
import os
import json
from pathlib import Path
from datetime import date

import requests
import streamlit as st


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GLOW NEST | Candle Studio",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).with_name("glow_nest_data.json")

# Existing Jarvis API configuration — unchanged
AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "openrouter/free"

try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")


# =========================================================
# 2. PHOTOS
# =========================================================

CANDLE_PHOTOS = {
    "Amber Glow": (
        "https://images.unsplash.com/photo-1603006905003-be475563bc59"
        "?auto=format&fit=crop&w=1000&q=85"
    ),
    "Vanilla Cloud": (
        "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6"
        "?auto=format&fit=crop&w=1000&q=85"
    ),
    "Midnight Cedar": (
        "https://images.unsplash.com/photo-1602523961358-f9f03dd557db"
        "?auto=format&fit=crop&w=1000&q=85"
    ),
    "Rose Ritual": (
        "https://images.unsplash.com/photo-1603006905003-be475563bc59"
        "?auto=format&fit=crop&w=1000&q=85"
    ),
    "Golden Dusk": (
        "https://images.unsplash.com/photo-1603006905003-be475563bc59"
        "?auto=format&fit=crop&w=1000&q=85"
    ),
}

TEAM_PHOTOS = [
    "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=700&q=85",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=700&q=85",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=700&q=85",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=700&q=85",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=700&q=85",
]

JARVIS_PHOTO = (
    "https://images.unsplash.com/photo-1535223289827-42f1e9919769"
    "?auto=format&fit=crop&w=1000&q=85"
)


# =========================================================
# 3. DEFAULT DATA
# =========================================================

DEFAULT_DATA = {
    "products": [
        {
            "id": 1,
            "name": "Amber Glow",
            "category": "Warm & Woody",
            "price": 18.00,
            "cost": 8.00,
            "stock": 25,
            "description": "Warm amber notes for a calm, cozy evening.",
        },
        {
            "id": 2,
            "name": "Vanilla Cloud",
            "category": "Sweet & Comforting",
            "price": 16.00,
            "cost": 7.00,
            "stock": 30,
            "description": "Soft vanilla fragrance for everyday comfort.",
        },
        {
            "id": 3,
            "name": "Midnight Cedar",
            "category": "Deep & Woody",
            "price": 22.00,
            "cost": 10.00,
            "stock": 15,
            "description": "A sophisticated woody scent for peaceful nights.",
        },
        {
            "id": 4,
            "name": "Rose Ritual",
            "category": "Floral & Elegant",
            "price": 20.00,
            "cost": 9.00,
            "stock": 20,
            "description": "A delicate floral fragrance inspired by roses.",
        },
        {
            "id": 5,
            "name": "Golden Dusk",
            "category": "Luxury & Warm",
            "price": 24.00,
            "cost": 11.00,
            "stock": 18,
            "description": "A luxurious warm fragrance for golden evenings.",
        },
    ],
    "orders": [
        {
            "id": 1001,
            "customer": "Emma",
            "product": "Amber Glow",
            "quantity": 2,
            "status": "Completed",
            "date": str(date.today()),
        },
        {
            "id": 1002,
            "customer": "Olivia",
            "product": "Vanilla Cloud",
            "quantity": 1,
            "status": "Pending",
            "date": str(date.today()),
        },
    ],
    "team": [
        {
            "name": "Sophia",
            "role": "Founder",
            "task": "Brand vision and business strategy",
            "status": "Active",
        },
        {
            "name": "Olivia",
            "role": "Candle Maker",
            "task": "Candle making and quality control",
            "status": "Active",
        },
        {
            "name": "Emma",
            "role": "Product Designer",
            "task": "Packaging and product presentation",
            "status": "Active",
        },
        {
            "name": "James",
            "role": "Marketing",
            "task": "Marketing and social media",
            "status": "Active",
        },
        {
            "name": "Ava",
            "role": "Order Manager",
            "task": "Order management and customer care",
            "status": "Active",
        },
    ],
}


# =========================================================
# 4. LOAD AND SAVE DATA
# =========================================================

def load_data():
    if not DATA_FILE.exists():
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Invalid data format")

        for section, defaults in DEFAULT_DATA.items():
            if section not in data or not isinstance(data[section], list):
                data[section] = json.loads(json.dumps(defaults))

        existing_names = {
            p.get("name", "").lower()
            for p in data["products"]
        }

        for product in DEFAULT_DATA["products"]:
            if product["name"].lower() not in existing_names:
                data["products"].append(
                    json.loads(json.dumps(product))
                )

        return data

    except (OSError, ValueError, json.JSONDecodeError):
        st.error(
            "Saved data could not be read. Please check "
            "glow_nest_data.json and keep a backup."
        )
        return json.loads(json.dumps(DEFAULT_DATA))


def save_data():
    try:
        temp_file = DATA_FILE.with_suffix(".tmp")

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                st.session_state.business_data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temp_file.replace(DATA_FILE)
        return True

    except OSError as error:
        st.error(f"Could not save data: {error}")
        return False


if "business_data" not in st.session_state:
    st.session_state.business_data = load_data()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview"

if "jarvis_messages" not in st.session_state:
    st.session_state.jarvis_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! Welcome to GLOW NEST. 🕯️ "
                "I'm Jarvis, your AI assistant. How can I help?"
            ),
        }
    ]


# =========================================================
# 5. HELPER FUNCTIONS
# =========================================================

def money(amount):
    return f"€{float(amount):,.2f}"


def get_product(name):
    for product in st.session_state.business_data["products"]:
        if product.get("name") == name:
            return product
    return None


def candle_photo(name):
    return CANDLE_PHOTOS.get(name, CANDLE_PHOTOS["Amber Glow"])


def revenue_total():
    total = 0

    for order in st.session_state.business_data["orders"]:
        if order.get("status") == "Completed":
            product = get_product(order.get("product", ""))

            if product:
                total += (
                    float(product.get("price", 0))
                    * int(order.get("quantity", 0))
                )

    return total


def completed_profit():
    total = 0

    for order in st.session_state.business_data["orders"]:
        if order.get("status") == "Completed":
            product = get_product(order.get("product", ""))

            if product:
                total += (
                    float(product.get("price", 0))
                    - float(product.get("cost", 0))
                ) * int(order.get("quantity", 0))

    return total


# =========================================================
# 6. DESIGN AND CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap'
    );

    .stApp {
        background: #21130f;
        color: #fff0e4;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #491b29, #24120f);
        border-right: 1px solid #a46a43;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #ffd39c !important;
    }

    p, label, li {
        color: #f3dfcf;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #582630, #321b1b);
        border: 1px solid #b77c4a;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 6px 22px rgba(0, 0, 0, 0.22);
    }

    [data-testid="stMetricLabel"] {
        color: #f0c6a1;
    }

    [data-testid="stMetricValue"] {
        color: #ffcf82;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: linear-gradient(110deg, #a83f50, #d48b43);
        color: white;
        border: 1px solid #edbd77;
        border-radius: 10px;
        font-weight: 700;
        min-height: 40px;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: #e4a454;
        color: #28120e;
        border-color: #ffe2a8;
    }

    div[data-testid="stForm"] {
        background: #321d1b;
        border: 1px solid #85523c;
        border-radius: 15px;
        padding: 18px;
    }

    .hero {
        background: linear-gradient(
            115deg,
            rgba(38, 10, 17, 0.97),
            rgba(111, 31, 45, 0.93),
            rgba(150, 81, 35, 0.88)
        );
        padding: 42px 32px;
        border: 1px solid #d39a5a;
        border-radius: 22px;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
        margin: 8px 0 25px 0;
    }

    .hero h1 {
        color: #ffe0ad !important;
        font-size: 38px;
        margin-bottom: 12px;
    }

    .hero p {
        color: #fff0df;
        line-height: 1.8;
    }

    .eyebrow {
        color: #ffcf82;
        letter-spacing: 3px;
        font-size: 12px;
        font-weight: 700;
    }

    .product-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 22px;
        font-weight: 700;
        color: #ffd39c;
        margin-top: 10px;
    }

    .product-category {
        color: #e4ae89;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .product-price {
        font-size: 22px;
        color: #ffcc78;
        font-weight: 700;
    }

    .footer {
        text-align: center;
        color: #e8b87d;
        padding: 22px;
    }

    [data-testid="stChatMessage"] {
        background: #3b2221;
        border: 1px solid #85523c;
        border-radius: 14px;
    }

    /* ONLY CHANGE: Jarvis input text is black on white */
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        background-color: #ffffff !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #555555 !important;
        -webkit-text-fill-color: #555555 !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #d39a5a !important;
        border-radius: 12px !important;
    }

    hr {
        border-color: #704138;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 7. SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:12px 0 5px 0;">
            <div style="font-size:12px; letter-spacing:3px; color:#f1bd82;">
                THE CANDLE STUDIO
            </div>
            <h1 style="font-size:32px; margin:0;">🕯️ GLOW NEST</h1>
            <div style="color:#f1c5a4; font-size:12px;">
                Crafted for beautiful moments
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("BUSINESS MENU")

    pages = [
        "Overview",
        "Products",
        "Orders",
        "Our Team",
        "Jarvis AI",
        "Profit Calculator",
    ]

    st.session_state.current_page = st.radio(
        "Navigate",
        pages,
        index=pages.index(st.session_state.current_page),
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**A little warmth in every corner.**")
    st.caption("Handmade candles • Thoughtful details • Cozy living")


# =========================================================
# 8. OVERVIEW DASHBOARD
# =========================================================

def show_overview():
    data = st.session_state.business_data
    products = data["products"]
    orders = data["orders"]
    team = data["team"]

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">WELCOME TO OUR BUSINESS</div>
            <h1>Welcome to GLOW NEST 🕯️</h1>
            <p>
                Discover our world of handmade candles, rich fragrances,
                golden candlelight, and little moments of luxury.
                Every candle brings warmth, beauty, and comfort to our home.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## The Studio at a Glance")
    st.caption("A quick look at what's happening across our business.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Our Products", len(products))

    with c2:
        st.metric("Total Orders", len(orders))

    with c3:
        st.metric("Revenue", money(revenue_total()))

    with c4:
        st.metric("Our Team", len(team))

    st.divider()
    st.markdown("## Our Signature Candle Collection")
    st.caption("Beautiful scents for every mood and moment.")

    for start in range(0, len(products), 3):
        columns = st.columns(3)

        for j, product in enumerate(products[start:start + 3]):
            with columns[j]:
                with st.container(border=True):
                    st.image(
                        candle_photo(product["name"]),
                        use_container_width=True,
                    )

                    st.markdown(
                        f'<div class="product-name">{product["name"]}</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f'<div class="product-category">'
                        f'{product.get("category", "Handmade candle")}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    st.write(product.get("description", ""))

                    st.markdown(
                        f'<div class="product-price">'
                        f'{money(product.get("price", 0))}</div>',
                        unsafe_allow_html=True,
                    )

                    stock = int(product.get("stock", 0))

                    if stock <= 5:
                        st.warning(f"Only {stock} left in stock")
                    else:
                        st.caption(f"Available: {stock} candles")

    # Team on dashboard
    st.divider()
    st.markdown("## ✨ The People Behind GLOW NEST")
    st.caption("Meet the team bringing our candle studio to life.")

    if team:
        columns = st.columns(min(5, len(team)))

        for i, member in enumerate(team):
            with columns[i % len(columns)]:
                with st.container(border=True):
                    photo = member.get("photo") or TEAM_PHOTOS[
                        i % len(TEAM_PHOTOS)
                    ]
                    st.image(photo, use_container_width=True)
                    st.markdown(f"**{member.get('name', 'Team Member')}**")
                    st.caption(member.get("role", "Team Member"))
                    st.write(member.get("task", ""))

    # Jarvis on dashboard
    st.divider()
    st.markdown("## 🤖 Meet Jarvis — Our AI Assistant")

    jarvis_left, jarvis_right = st.columns([1, 2])

    with jarvis_left:
        st.image(JARVIS_PHOTO, use_container_width=True)

    with jarvis_right:
        st.markdown("### Your GLOW NEST AI Companion")

        # Added status indicator; it does not alter the API connection.
        if OPENROUTER_API_KEY:
            st.success("🟢 Jarvis API key configured")
        else:
            st.warning("🟠 Jarvis API key not configured")

        st.write(
            "Jarvis helps with marketing ideas, product performance, "
            "promotions, and questions about our candle business."
        )

        st.info("Open the Jarvis AI page from the sidebar to start chatting.")

        if st.button("Open Jarvis AI", key="overview_open_jarvis"):
            st.session_state.current_page = "Jarvis AI"
            st.rerun()

    st.divider()
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("## Recent Orders")

        if orders:
            for order in orders[-4:][::-1]:
                with st.container(border=True):
                    a, b = st.columns([3, 1])

                    with a:
                        st.markdown(f"**Order #{order.get('id')}**")
                        st.write(
                            f"{order.get('customer', 'Customer')} · "
                            f"{order.get('product', 'Candle')}"
                        )
                        st.caption(order.get("date", ""))

                    with b:
                        st.write(f"× {order.get('quantity', 1)}")
                        st.caption(order.get("status", "Pending"))
        else:
            st.info("No orders yet.")

    with right:
        st.markdown("## Studio Insights")

        completed_orders = [
            o for o in orders if o.get("status") == "Completed"
        ]
        pending_orders = [
            o for o in orders if o.get("status") == "Pending"
        ]

        st.metric("Completed Orders", len(completed_orders))
        st.metric("Pending Orders", len(pending_orders))
        st.metric("Estimated Product Profit", money(completed_profit()))

        low_stock = [
            p for p in products if int(p.get("stock", 0)) <= 5
        ]

        if low_stock:
            st.warning(
                "Low stock: "
                + ", ".join(p.get("name", "") for p in low_stock)
            )
        else:
            st.success("No products with critically low stock.")

        st.caption("Estimated profit excludes taxes and other expenses.")

    st.divider()
    st.markdown("## The GLOW NEST Promise")

    a, b, c = st.columns(3)

    with a:
        st.markdown("### 🕯️ Thoughtfully Made")
        st.write("Candles designed to make everyday moments feel special.")

    with b:
        st.markdown("### 🌿 Fragrance & Comfort")
        st.write("Warm, floral, sweet, and woody fragrance inspirations.")

    with c:
        st.markdown("### 🎁 Made for Gifting")
        st.write("Thoughtful candle gifts for celebrations and quiet evenings.")


# =========================================================
# 9. PRODUCTS
# =========================================================

def show_products():
    st.title("Our Candle Collection")
    st.write("Manage the products in our candle studio.")

    data = st.session_state.business_data
    products = data["products"]

    tab1, tab2 = st.tabs(["Explore Candles", "Add a Candle"])

    with tab1:
        if not products:
            st.info("No candles have been added yet.")

        for start in range(0, len(products), 3):
            columns = st.columns(3)

            for j, product in enumerate(products[start:start + 3]):
                with columns[j]:
                    with st.container(border=True):
                        st.image(
                            candle_photo(product["name"]),
                            use_container_width=True,
                        )
                        st.subheader(product["name"])
                        st.caption(product.get("category", "Candle"))
                        st.write(product.get("description", ""))
                        st.markdown(f"### {money(product.get('price', 0))}")
                        st.write(f"Cost: {money(product.get('cost', 0))}")
                        st.write(f"Stock: {product.get('stock', 0)}")

                        unit_profit = (
                            float(product.get("price", 0))
                            - float(product.get("cost", 0))
                        )
                        st.caption(
                            f"Estimated profit per candle: {money(unit_profit)}"
                        )

                        with st.expander("Edit Candle"):
                            with st.form(f"edit_product_{product['id']}"):
                                name = st.text_input(
                                    "Product name",
                                    value=product["name"],
                                )
                                category = st.text_input(
                                    "Category",
                                    value=product.get("category", ""),
                                )
                                price = st.number_input(
                                    "Selling price (€)",
                                    min_value=0.0,
                                    value=float(product.get("price", 0)),
                                    step=1.0,
                                )
                                cost = st.number_input(
                                    "Production cost (€)",
                                    min_value=0.0,
                                    value=float(product.get("cost", 0)),
                                    step=1.0,
                                )
                                stock = st.number_input(
                                    "Stock",
                                    min_value=0,
                                    value=int(product.get("stock", 0)),
                                    step=1,
                                )
                                description = st.text_area(
                                    "Description",
                                    value=product.get("description", ""),
                                )

                                if st.form_submit_button("Save Changes"):
                                    if not name.strip():
                                        st.error("Product name is required.")
                                    elif any(
                                        p["id"] != product["id"]
                                        and p["name"].lower() == name.strip().lower()
                                        for p in products
                                    ):
                                        st.error("This product name already exists.")
                                    else:
                                        product.update({
                                            "name": name.strip(),
                                            "category": category.strip(),
                                            "price": price,
                                            "cost": cost,
                                            "stock": stock,
                                            "description": description.strip(),
                                        })

                                        if save_data():
                                            st.success("Product updated.")
                                            st.rerun()

                        with st.expander("Delete Candle"):
                            st.warning("This removes the candle from the collection.")

                            if st.button(
                                "Confirm Delete",
                                key=f"delete_product_{product['id']}",
                            ):
                                data["products"] = [
                                    p for p in products
                                    if p["id"] != product["id"]
                                ]

                                if save_data():
                                    st.rerun()

    with tab2:
        with st.form("add_product_form", clear_on_submit=True):
            st.subheader("Add a New Candle")
            name = st.text_input("Product name")

            category = st.selectbox(
                "Fragrance category",
                [
                    "Warm & Woody",
                    "Sweet & Comforting",
                    "Floral & Elegant",
                    "Fresh & Clean",
                    "Luxury & Warm",
                    "Other",
                ],
            )

            price = st.number_input(
                "Selling price (€)", min_value=0.0, value=18.0, step=1.0
            )
            cost = st.number_input(
                "Production cost (€)", min_value=0.0, value=8.0, step=1.0
            )
            stock = st.number_input(
                "Opening stock", min_value=0, value=10, step=1
            )
            description = st.text_area("Description")

            if st.form_submit_button("Add to Collection"):
                if not name.strip():
                    st.error("Please enter a product name.")
                elif any(
                    p["name"].lower() == name.strip().lower()
                    for p in products
                ):
                    st.error("This candle already exists.")
                else:
                    new_id = max(
                        [int(p.get("id", 0)) for p in products],
                        default=0,
                    ) + 1

                    products.append({
                        "id": new_id,
                        "name": name.strip(),
                        "category": category,
                        "price": price,
                        "cost": cost,
                        "stock": stock,
                        "description": description.strip(),
                    })

                    if save_data():
                        st.success("Your candle has been added!")
                        st.rerun()


# =========================================================
# 10. ORDERS
# =========================================================

def show_orders():
    st.title("Order Management")
    st.write("Manage customer orders and track their progress.")

    data = st.session_state.business_data
    orders = data["orders"]
    products = data["products"]

    tab1, tab2 = st.tabs(["All Orders", "Create Order"])

    with tab1:
        if not orders:
            st.info("No orders yet.")

        for order in orders[::-1]:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 2])

                with c1:
                    st.subheader(f"Order #{order.get('id')}")
                    st.write(order.get("customer", "Customer"))
                    st.caption(order.get("date", ""))

                with c2:
                    st.write(f"**{order.get('product', '')}**")
                    st.write(f"Quantity: {order.get('quantity', 1)}")

                    product = get_product(order.get("product", ""))

                    if product:
                        total = (
                            float(product.get("price", 0))
                            * int(order.get("quantity", 1))
                        )
                        st.write(f"Total: {money(total)}")

                with c3:
                    options = [
                        "Pending",
                        "Processing",
                        "Completed",
                        "Cancelled",
                    ]
                    current = order.get("status", "Pending")

                    if current not in options:
                        current = "Pending"

                    status = st.selectbox(
                        "Order status",
                        options,
                        index=options.index(current),
                        key=f"status_{order.get('id')}",
                    )

                    if status != order.get("status"):
                        if st.button(
                            "Save Status",
                            key=f"save_status_{order.get('id')}",
                        ):
                            order["status"] = status

                            if save_data():
                                st.rerun()

    with tab2:
        if not products:
            st.warning("Add a candle before creating an order.")
        else:
            with st.form("new_order_form", clear_on_submit=True):
                customer = st.text_input("Customer name")
                product_name = st.selectbox(
                    "Choose a candle",
                    [p["name"] for p in products],
                )
                quantity = st.number_input(
                    "Quantity", min_value=1, value=1, step=1
                )

                submitted = st.form_submit_button("Create Order")

                if submitted:
                    if not customer.strip():
                        st.error("Please enter a customer name.")
                    else:
                        product = get_product(product_name)

                        if product and quantity > product.get("stock", 0):
                            st.error("Not enough stock available.")
                        else:
                            new_id = max(
                                [int(o.get("id", 1000)) for o in orders],
                                default=1000,
                            ) + 1

                            orders.append({
                                "id": new_id,
                                "customer": customer.strip(),
                                "product": product_name,
                                "quantity": int(quantity),
                                "status": "Pending",
                                "date": str(date.today()),
                            })

                            if product:
                                product["stock"] -= int(quantity)

                            if save_data():
                                st.success(f"Order #{new_id} created.")
                                st.rerun()


# =========================================================
# 11. OUR TEAM
# =========================================================

def show_team():
    st.title("Meet Our Team")
    st.write("The people, creativity, and care behind our candle studio.")

    data = st.session_state.business_data
    team = data["team"]

    tab1, tab2 = st.tabs(["Our People", "Add Team Member"])

    with tab1:
        if not team:
            st.info("Add your team members to get started.")

        columns = st.columns(3)

        for i, member in enumerate(team):
            with columns[i % 3]:
                with st.container(border=True):
                    photo = member.get("photo") or TEAM_PHOTOS[
                        i % len(TEAM_PHOTOS)
                    ]

                    st.image(photo, use_container_width=True)
                    st.subheader(member.get("name", "Team Member"))
                    st.caption(member.get("role", "Team Member"))
                    st.write(member.get("task", ""))
                    st.caption(f"Status: {member.get('status', 'Active')}")

                    with st.expander("Edit Team Member"):
                        with st.form(f"edit_team_{i}"):
                            name = st.text_input(
                                "Name", value=member.get("name", "")
                            )
                            role = st.text_input(
                                "Role", value=member.get("role", "")
                            )
                            task = st.text_area(
                                "Responsibilities",
                                value=member.get("task", ""),
                            )
                            statuses = ["Active", "On Leave", "Inactive"]
                            current_status = member.get("status", "Active")

                            status = st.selectbox(
                                "Status",
                                statuses,
                                index=(
                                    statuses.index(current_status)
                                    if current_status in statuses else 0
                                ),
                            )

                            if st.form_submit_button("Save Changes"):
                                if not name.strip():
                                    st.error("Name is required.")
                                else:
                                    member.update({
                                        "name": name.strip(),
                                        "role": role.strip(),
                                        "task": task.strip(),
                                        "status": status,
                                    })

                                    if save_data():
                                        st.success("Team member updated.")
                                        st.rerun()

    with tab2:
        with st.form("add_team_form", clear_on_submit=True):
            name = st.text_input("Full name")
            role = st.text_input("Job role")
            task = st.text_area("Responsibilities")
            status = st.selectbox(
                "Status", ["Active", "On Leave", "Inactive"]
            )

            if st.form_submit_button("Add Team Member"):
                if not name.strip():
                    st.error("Enter the team member's name.")
                else:
                    team.append({
                        "name": name.strip(),
                        "role": role.strip(),
                        "task": task.strip(),
                        "status": status,
                    })

                    if save_data():
                        st.success("Team member added.")
                        st.rerun()


# =========================================================
# 12. JARVIS AI — API CONNECTION KEPT
# =========================================================

def ask_jarvis(messages):
    if not OPENROUTER_API_KEY:
        return (
            "Jarvis AI is not connected yet. Add OPENROUTER_API_KEY "
            "in Streamlit Cloud → Settings → Secrets."
        )

    data = st.session_state.business_data

    product_context = [
        {
            "name": p.get("name"),
            "price": p.get("price"),
            "cost": p.get("cost"),
            "stock": p.get("stock"),
        }
        for p in data["products"]
    ]

    order_context = [
        {
            "id": o.get("id"),
            "product": o.get("product"),
            "quantity": o.get("quantity"),
            "status": o.get("status"),
        }
        for o in data["orders"][-15:]
    ]

    system_message = f"""
You are Jarvis, the friendly AI assistant for GLOW NEST,
a handmade candle business.

Use simple, clear, professional language.
Help with product ideas, marketing, pricing, customer service,
inventory, orders, and business planning.

Do not claim to have changed or saved app data.

Current products:
{json.dumps(product_context, ensure_ascii=False)}

Recent orders:
{json.dumps(order_context, ensure_ascii=False)}

Completed-order revenue: {revenue_total():.2f} EUR
Estimated product profit on completed orders: {completed_profit():.2f} EUR
"""

    try:
        response = requests.post(
            AI_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://glow-nest.streamlit.app",
                "X-Title": "GLOW NEST",
            },
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": system_message}
                ] + messages[-12:],
                "temperature": 0.7,
                "max_tokens": 700,
            },
            timeout=45,
        )

        if response.status_code != 200:
            return (
                f"AI service returned error {response.status_code}. "
                "Please check your API key, model, and account limits."
            )

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except requests.Timeout:
        return "The AI request took too long. Please try again."
    except requests.RequestException:
        return "Could not connect to the AI service. Please try again."
    except (KeyError, IndexError, ValueError):
        return "The AI service returned an unexpected response."


def show_jarvis():
    st.title("Jarvis AI 🤖")
    st.write("Your AI companion for our candle business.")

    left, right = st.columns([1, 2])

    with left:
        st.image(JARVIS_PHOTO, use_container_width=True)
        st.subheader("Meet Jarvis")
        st.caption("GLOW NEST AI Assistant")

        if OPENROUTER_API_KEY:
            st.success("API key configured")
        else:
            st.warning("API key not configured")

        st.write(
            "Ask Jarvis about our products, business performance, "
            "marketing plans, and ways to improve candle sales."
        )

        st.markdown("**Try asking:**")
        st.caption("• How can we increase candle sales?")
        st.caption("• Suggest a marketing campaign.")
        st.caption("• Which products have low stock?")

    with right:
        for message in st.session_state.jarvis_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Message Jarvis...")

        if prompt:
            st.session_state.jarvis_messages.append({
                "role": "user",
                "content": prompt,
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Jarvis is thinking..."):
                    answer = ask_jarvis(
                        st.session_state.jarvis_messages
                    )
                st.markdown(answer)

            st.session_state.jarvis_messages.append({
                "role": "assistant",
                "content": answer,
            })

        if st.button("Clear Conversation"):
            st.session_state.jarvis_messages = [
                {
                    "role": "assistant",
                    "content": "Hello! Welcome to GLOW NEST. How can I help?",
                }
            ]
            st.rerun()


# =========================================================
# 13. PROFIT CALCULATOR
# =========================================================

def show_profit_calculator():
    st.title("Profit Calculator 💰")
    st.write("Calculate estimated earnings from candle sales.")

    products = st.session_state.business_data["products"]

    if products:
        names = [p["name"] for p in products]
        chosen = st.selectbox("Choose a candle", names)
        product = get_product(chosen)
        default_price = float(product.get("price", 18))
        default_cost = float(product.get("cost", 8))
    else:
        default_price = 18.0
        default_cost = 8.0

    left, right = st.columns(2)

    with left:
        selling_price = st.number_input(
            "Selling price per candle (€)",
            min_value=0.0,
            value=default_price,
            step=1.0,
        )
        production_cost = st.number_input(
            "Production cost per candle (€)",
            min_value=0.0,
            value=default_cost,
            step=1.0,
        )
        quantity = st.number_input(
            "Candles sold", min_value=1, value=10, step=1
        )
        extra_expenses = st.number_input(
            "Other expenses (€)", min_value=0.0, value=0.0, step=1.0
        )

    revenue = selling_price * quantity
    costs = production_cost * quantity + extra_expenses
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0

    with right:
        st.subheader("Estimated Results")
        st.metric("Total Revenue", money(revenue))
        st.metric("Total Costs", money(costs))
        st.metric("Estimated Profit", money(profit))
        st.metric("Profit Margin", f"{margin:.1f}%")

        if profit < 0:
            st.warning("Costs are higher than revenue.")
        else:
            st.success("Revenue covers the costs entered above.")

        st.caption(
            "This estimate excludes taxes and expenses not entered above."
        )


# =========================================================
# 14. PAGE ROUTER
# =========================================================

page = st.session_state.current_page

if page == "Overview":
    show_overview()

elif page == "Products":
    show_products()

elif page == "Orders":
    show_orders()

elif page == "Our Team":
    show_team()

elif page == "Jarvis AI":
    show_jarvis()

elif page == "Profit Calculator":
    show_profit_calculator()


# =========================================================
# 15. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🕯️ <b>GLOW NEST</b><br>
        Welcome to our world of warmth, fragrance, and handmade candles.
    </div>
    """,
    unsafe_allow_html=True,
)
