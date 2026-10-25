import os
import json
from pathlib import Path
from datetime import datetime

import requests
import streamlit as st

# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="GLOW NEST | Candle Studio",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).with_name("glow_nest_data.json")

# ==========================================================
# 2. JARVIS AI API CONFIGURATION
# ==========================================================

# Paste your NEW OpenRouter API key between the quotes.
# Do not upload this key to a public GitHub repository.

try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

JARVIS_MODEL = "qwen/qwen3-4b:free"
JARVIS_URL = "https://openrouter.ai/api/v1/chat/completions"

# ==========================================================
# 3. DEFAULT BUSINESS DATA
# ==========================================================

DEFAULT_DATA = {
    "products": [
        {
            "id": 1,
            "name": "Amber Glow",
            "category": "Warm & Woody",
            "price": 18.00,
            "cost": 7.00,
            "stock": 25,
            "description": "A warm amber fragrance for cosy evenings.",
        },
        {
            "id": 2,
            "name": "Vanilla Cloud",
            "category": "Sweet & Soft",
            "price": 16.00,
            "cost": 6.00,
            "stock": 30,
            "description": "A soft and comforting vanilla fragrance.",
        },
        {
            "id": 3,
            "name": "Midnight Cedar",
            "category": "Wood & Earth",
            "price": 22.00,
            "cost": 9.00,
            "stock": 15,
            "description": "A rich cedarwood fragrance for peaceful nights.",
        },
        {
            "id": 4,
            "name": "Rose Ritual",
            "category": "Floral",
            "price": 19.00,
            "cost": 8.00,
            "stock": 20,
            "description": "A beautiful floral fragrance with rose notes.",
        },
    ],
    "orders": [
        {
            "id": 1001,
            "customer": "Emma",
            "product": "Amber Glow",
            "quantity": 2,
            "total": 36.00,
            "status": "Completed",
            "date": "2026-10-20",
        },
        {
            "id": 1002,
            "customer": "Sofia",
            "product": "Vanilla Cloud",
            "quantity": 1,
            "total": 16.00,
            "status": "Processing",
            "date": "2026-10-21",
        },
        {
            "id": 1003,
            "customer": "Laura",
            "product": "Rose Ritual",
            "quantity": 3,
            "total": 57.00,
            "status": "Pending",
            "date": "2026-10-22",
        },
    ],
    "team": [
        {
            "id": 1,
            "name": "Team Member 1",
            "role": "Production",
            "task": "Prepare candle batches",
            "status": "In progress",
        },
        {
            "id": 2,
            "name": "Team Member 2",
            "role": "Packaging",
            "task": "Pack customer orders",
            "status": "Pending",
        },
        {
            "id": 3,
            "name": "Team Member 3",
            "role": "Marketing",
            "task": "Prepare social media content",
            "status": "In progress",
        },
        {
            "id": 4,
            "name": "Team Member 4",
            "role": "Inventory",
            "task": "Check stock levels",
            "status": "Completed",
        },
        {
            "id": 5,
            "name": "Team Member 5",
            "role": "Customer Service",
            "task": "Reply to customer messages",
            "status": "Pending",
        },
    ],
}

# ==========================================================
# 4. LOAD AND SAVE DATA
# ==========================================================

def load_data():
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            loaded_data = json.load(file)

        for key, default_value in DEFAULT_DATA.items():
            if key not in loaded_data:
                loaded_data[key] = json.loads(json.dumps(default_value))

        return loaded_data

    except (OSError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except OSError as error:
        st.error(f"Unable to save data: {error}")


if "business_data" not in st.session_state:
    st.session_state.business_data = load_data()

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "jarvis_messages" not in st.session_state:
    st.session_state.jarvis_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am Jarvis, our GLOW NEST business assistant. "
                "I can help with marketing, candle ideas, pricing, "
                "sales, and business planning. What would you like help with?"
            ),
        }
    ]

data = st.session_state.business_data


def refresh_data():
    st.session_state.business_data = data
    save_data(data)


def next_id(items):
    if not items:
        return 1
    return max(int(item.get("id", 0)) for item in items) + 1


def money(value):
    return f"€{float(value):,.2f}"


# ==========================================================
# 5. JARVIS AI FUNCTION
# ==========================================================

def ask_jarvis(messages):
    api_key = OPENROUTER_API_KEY.strip()

    if not api_key:
        return (
            "Jarvis needs an API key to work. Set the "
            "OPENROUTER_API_KEY environment variable and restart the app."
        )

    products_summary = "\n".join(
        [
            f"- {p['name']}: price {money(p['price'])}, "
            f"cost {money(p['cost'])}, stock {p['stock']}"
            for p in data.get("products", [])
        ]
    )

    orders_summary = "\n".join(
        [
            f"- Order #{o['id']}: {o['product']}, "
            f"quantity {o['quantity']}, total {money(o['total'])}, "
            f"status {o['status']}"
            for o in data.get("orders", [])
        ]
    )

    system_prompt = f"""
You are Jarvis, the friendly AI assistant for GLOW NEST,
a handmade candle business.

Use simple, clear English.
Give practical advice and easy-to-follow steps.
Be friendly and concise.
Do not claim that you have changed anything in the dashboard.

OUR PRODUCTS:
{products_summary}

OUR ORDERS:
{orders_summary}

Help with candle ideas, marketing, customer messages, pricing,
profit calculations, sales improvement, inventory, and business planning.
"""

    payload = {
        "model": JARVIS_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages[-12:],
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "GLOW NEST Business Studio",
    }

    try:
        response = requests.post(
            JARVIS_URL,
            headers=headers,
            json=payload,
            timeout=90,
        )

        if not response.ok:
            try:
                details = response.json().get("error", {}).get(
                    "message", response.text[:300]
                )
            except ValueError:
                details = response.text[:300]

            return f"Jarvis API error: {details}"

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "Jarvis took too long to respond. Please try again."

    except requests.exceptions.RequestException as error:
        return f"Could not connect to Jarvis: {error}"

    except (KeyError, IndexError, ValueError):
        return "Jarvis returned an unexpected response. Please try again."


# ==========================================================
# 6. CUSTOM DESIGN AND COLOURS
# ==========================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600;700&display=swap'
    );

    :root {
        --navy: #101b32;
        --blue: #4169e1;
        --gold: #ffd166;
        --cream: #fffaf0;
        --text: #202b3c;
        --muted: #64748b;
        --border: #e6eaf0;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 95% 0%,
                rgba(255, 209, 102, 0.18),
                transparent 30%
            ),
            linear-gradient(180deg, #f8faff 0%, #fffaf2 100%);
        color: var(--text);
    }

    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif !important;
        color: var(--navy) !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #314b70 0%,
            #18263e 55%,
            #0a1222 100%
        );
        border-right: 2px solid var(--gold);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffe09a !important;
    }

    .brand-mark {
        background: linear-gradient(135deg, #ffe7a3, #ffd166, #f3a712);
        color: #17243b;
        padding: 14px;
        border-radius: 18px;
        text-align: center;
        font-size: 34px;
        margin-bottom: 12px;
    }

    .brand-name {
        font-family: 'Playfair Display', serif;
        font-size: 31px;
        font-weight: 700;
        color: #ffe09a;
        text-align: center;
        letter-spacing: 1px;
    }

    .brand-subtitle {
        text-align: center;
        font-size: 11px;
        letter-spacing: 2px;
        margin-bottom: 20px;
        color: #ffffff;
    }

    .hero {
        background: linear-gradient(120deg, #314b70, #18263e, #0a1222);
        padding: 32px;
        border-radius: 24px;
        color: white;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 209, 102, 0.7);
        box-shadow: 0 12px 30px rgba(16, 27, 50, 0.16);
    }

    .hero h1 {
        color: #ffe09a !important;
        font-size: 39px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #ffffff !important;
        font-size: 15px;
    }

    .hero-eyebrow {
        color: #ffd166;
        letter-spacing: 3px;
        font-size: 11px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .metric-card {
        background: linear-gradient(145deg, #ffffff, #fffaf0);
        border: 1px solid #f0e4c8;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(16, 27, 50, 0.08);
        min-height: 132px;
    }

    .metric-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        color: #17243b;
        font-size: 28px;
        font-weight: 800;
        margin-top: 8px;
    }

    .metric-note {
        color: #64748b;
        font-size: 12px;
        margin-top: 5px;
    }

    .section-heading {
        font-family: 'Playfair Display', serif;
        color: #17243b;
        font-size: 25px;
        font-weight: 700;
        margin: 12px 0 4px 0;
    }

    .section-caption {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 16px;
    }

    .product-card {
        background: #ffffff;
        border: 1px solid #e9edf4;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(16, 27, 50, 0.08);
        margin-bottom: 10px;
    }

    .product-icon {
        font-size: 32px;
        background: linear-gradient(135deg, #fff0c2, #ffe4ed);
        width: 62px;
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        margin-bottom: 12px;
    }

    .product-name {
        font-family: 'Playfair Display', serif;
        color: #17243b;
        font-size: 21px;
        font-weight: 700;
    }

    .product-category {
        color: #64748b;
        font-size: 12px;
        margin-bottom: 10px;
    }

    .product-price {
        color: #b77900;
        font-size: 23px;
        font-weight: 800;
    }

    .jarvis-banner {
        background: linear-gradient(120deg, #314b70, #18263e, #101b32);
        border: 1px solid #ffd166;
        border-radius: 22px;
        padding: 22px;
        color: #ffffff;
        margin-bottom: 18px;
    }

    .jarvis-banner h2 {
        color: #ffe09a !important;
    }

    .jarvis-banner p {
        color: #ffffff !important;
    }

    /* Normal input fields */
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea,
    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #17243b !important;
        -webkit-text-fill-color: #17243b !important;
        caret-color: #17243b !important;
        border-radius: 10px !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }

    /* Make Jarvis input bright and readable */
    [data-testid="stChatInput"] {
        background: #ffffff !important;
        border: 2px solid #ffd166 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 16px rgba(16, 27, 50, 0.08) !important;
    }

    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] textarea:focus {
        background: #ffffff !important;
        color: #17243b !important;
        -webkit-text-fill-color: #17243b !important;
        caret-color: #17243b !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] button {
        background: #ffd166 !important;
        color: #17243b !important;
        border-radius: 10px !important;
    }

    .stButton button,
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #4169e1, #253e63);
        color: #ffffff !important;
        border: none;
        border-radius: 11px;
        font-weight: 700;
        padding: 9px 16px;
        transition: all 0.2s ease;
    }

    .stButton button:hover,
    .stFormSubmitButton button:hover {
        background: linear-gradient(135deg, #ffd166, #f3a712);
        color: #17243b !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border-radius: 10px;
        color: #253e63;
        border: 1px solid #e6eaf0;
    }

    .stTabs [aria-selected="true"] {
        background: #fff0c2 !important;
        color: #17243b !important;
        border-color: #ffd166 !important;
    }

    .footer {
        color: #64748b;
        text-align: center;
        padding: 25px 0 10px 0;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# 7. SIDEBAR NAVIGATION
# ==========================================================

with st.sidebar:
    st.markdown(
        '<div class="brand-mark">🕯️</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="brand-name">GLOW NEST</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="brand-subtitle">OUR CANDLE BUSINESS STUDIO</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### ✨ Main Menu")

    pages = [
        ("🏠", "Overview"),
        ("🕯️", "Products"),
        ("📦", "Orders"),
        ("👥", "Our Team"),
        ("🤖", "Jarvis AI"),
        ("💰", "Profit Calculator"),
    ]

    for page_icon, page_name in pages:
        if st.button(
            f"{page_icon}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
        ):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("---")
    st.markdown("### 🌟 Our Mission")
    st.write(
        "Creating beautiful candles and meaningful moments, "
        "one glow at a time."
    )
    st.markdown("---")
    st.caption("Our business data is saved locally on this computer.")
    st.caption("GLOW NEST © 2026")


# ==========================================================
# 8. COMMON UI FUNCTIONS
# ==========================================================

def page_title(eyebrow, title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, note, emoji):
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:24px">{emoji}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title, caption=None):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )

    if caption:
        st.markdown(
            f'<div class="section-caption">{caption}</div>',
            unsafe_allow_html=True,
        )


# ==========================================================
# 9. OVERVIEW PAGE
# ==========================================================

def show_overview():
    page_title(
        "WELCOME TO OUR BUSINESS",
        "Our business, glowing brighter.",
        "One beautiful place for our candles, our team, and our next big idea.",
    )

    products = data["products"]
    orders = data["orders"]

    completed_revenue = sum(
        float(order.get("total", 0))
        for order in orders
        if order.get("status") == "Completed"
    )

    open_orders = sum(
        1 for order in orders
        if order.get("status") in ["Pending", "Processing"]
    )

    total_stock = sum(
        int(product.get("stock", 0))
        for product in products
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Completed Sales",
            money(completed_revenue),
            "Revenue from completed orders",
            "💰",
        )

    with c2:
        metric_card(
            "Our Products",
            str(len(products)),
            "Products in our collection",
            "🕯️",
        )

    with c3:
        metric_card(
            "Open Orders",
            str(open_orders),
            "Pending or processing",
            "📦",
        )

    with c4:
        metric_card(
            "Items in Stock",
            str(total_stock),
            "Total inventory available",
            "✨",
        )

    st.write("")

    left, right = st.columns([1.4, 1])

    with left:
        section_heading(
            "Our candle collection",
            "A quick look at the products we offer.",
        )

        if not products:
            st.info("Add our first product from the Products page.")
        else:
            product_columns = st.columns(2)

            for index, product in enumerate(products[:4]):
                with product_columns[index % 2]:
                    st.markdown(
                        f"""
                        <div class="product-card">
                            <div class="product-icon">🕯️</div>
                            <div class="product-name">{product['name']}</div>
                            <div class="product-category">
                                {product.get('category', 'Candle')}
                            </div>
                            <div class="product-price">
                                {money(product['price'])}
                            </div>
                            <p>{product.get('description', '')}</p>
                            <b>Stock: {product.get('stock', 0)}</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with right:
        section_heading("Our daily focus", "Small steps, brighter results.")

        st.markdown(
            """
            <div class="product-card">
                <div style="font-size:28px">🎯</div>
                <h3>Quality first</h3>
                <p>Create candles that look beautiful and smell amazing.</p>
            </div>
            <div class="product-card">
                <div style="font-size:28px">💌</div>
                <h3>Happy customers</h3>
                <p>Deliver orders on time and respond kindly to customers.</p>
            </div>
            <div class="product-card">
                <div style="font-size:28px">📈</div>
                <h3>Grow together</h3>
                <p>Track sales, manage stock, and find new opportunities.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_heading("Recent orders", "The latest activity in our business.")

    if orders:
        recent = sorted(
            orders,
            key=lambda order: str(order.get("date", "")),
            reverse=True,
        )[:5]

        st.dataframe(
            [
                {
                    "Order ID": f"#{o['id']}",
                    "Customer": o["customer"],
                    "Product": o["product"],
                    "Quantity": o["quantity"],
                    "Total": money(o["total"]),
                    "Status": o["status"],
                    "Date": o["date"],
                }
                for o in recent
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Our orders will appear here.")


# ==========================================================
# 10. PRODUCTS PAGE
# ==========================================================

def show_products():
    page_title(
        "OUR COLLECTION",
        "Products & candles",
        "Manage our candle collection, prices, costs, and stock.",
    )

    products = data["products"]

    view_tab, add_tab, manage_tab = st.tabs(
        ["🕯️ Our Products", "➕ Add Product", "🛠️ Manage Products"]
    )

    with view_tab:
        if not products:
            st.info("No products yet.")
        else:
            for product in products:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

                    with c1:
                        st.markdown(f"### 🕯️ {product['name']}")
                        st.caption(
                            f"{product.get('category', 'Candle')} — "
                            f"{product.get('description', '')}"
                        )

                    with c2:
                        st.markdown("**Selling price**")
                        st.write(money(product["price"]))

                    with c3:
                        st.markdown("**Unit cost**")
                        st.write(money(product["cost"]))

                    with c4:
                        st.markdown("**Stock**")
                        st.write(product["stock"])

    with add_tab:
        st.markdown("### Add a new candle")

        with st.form("add_product_form", clear_on_submit=True):
            name = st.text_input("Product name")

            category = st.selectbox(
                "Category",
                [
                    "Floral",
                    "Warm & Woody",
                    "Sweet & Soft",
                    "Fresh",
                    "Wood & Earth",
                    "Seasonal",
                    "Other",
                ],
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                price = st.number_input(
                    "Selling price (€)",
                    min_value=0.0,
                    value=15.0,
                    step=0.5,
                )

            with c2:
                cost = st.number_input(
                    "Cost to make (€)",
                    min_value=0.0,
                    value=5.0,
                    step=0.5,
                )

            with c3:
                stock = st.number_input(
                    "Stock quantity",
                    min_value=0,
                    value=10,
                    step=1,
                )

            description = st.text_area(
                "Description",
                placeholder="Describe the fragrance and style...",
            )

            submitted = st.form_submit_button(
                "Add product",
                use_container_width=True,
            )

            if submitted:
                if not name.strip():
                    st.error("Please enter a product name.")
                else:
                    products.append(
                        {
                            "id": next_id(products),
                            "name": name.strip(),
                            "category": category,
                            "price": float(price),
                            "cost": float(cost),
                            "stock": int(stock),
                            "description": description.strip(),
                        }
                    )

                    refresh_data()
                    st.success("Product added to our collection.")
                    st.rerun()

    with manage_tab:
        if not products:
            st.info("There are no products to manage.")
        else:
            selected_id = st.selectbox(
                "Select a product",
                options=[p["id"] for p in products],
                format_func=lambda pid: next(
                    p["name"] for p in products if p["id"] == pid
                ),
            )

            product = next(p for p in products if p["id"] == selected_id)

            with st.form("edit_product_form"):
                edited_name = st.text_input(
                    "Product name",
                    value=product["name"],
                )

                edited_category = st.text_input(
                    "Category",
                    value=product.get("category", ""),
                )

                c1, c2, c3 = st.columns(3)

                with c1:
                    edited_price = st.number_input(
                        "Selling price (€)",
                        min_value=0.0,
                        value=float(product["price"]),
                        step=0.5,
                    )

                with c2:
                    edited_cost = st.number_input(
                        "Cost (€)",
                        min_value=0.0,
                        value=float(product["cost"]),
                        step=0.5,
                    )

                with c3:
                    edited_stock = st.number_input(
                        "Stock",
                        min_value=0,
                        value=int(product["stock"]),
                        step=1,
                    )

                edited_description = st.text_area(
                    "Description",
                    value=product.get("description", ""),
                )

                save_changes = st.form_submit_button(
                    "Save changes",
                    use_container_width=True,
                )

                if save_changes:
                    if not edited_name.strip():
                        st.error("Product name cannot be empty.")
                    else:
                        product.update(
                            {
                                "name": edited_name.strip(),
                                "category": edited_category.strip(),
                                "price": float(edited_price),
                                "cost": float(edited_cost),
                                "stock": int(edited_stock),
                                "description": edited_description.strip(),
                            }
                        )

                        refresh_data()
                        st.success("Product updated.")
                        st.rerun()

            st.markdown("---")
            st.markdown("### Delete product")

            confirm_delete = st.checkbox(
                f"Confirm deletion of {product['name']}",
                key=f"delete_product_{selected_id}",
            )

            if st.button(
                "Delete selected product",
                disabled=not confirm_delete,
            ):
                data["products"] = [
                    p for p in data["products"]
                    if p["id"] != selected_id
                ]

                refresh_data()
                st.success("Product deleted.")
                st.rerun()


# ==========================================================
# 11. ORDERS PAGE
# ==========================================================

def show_orders():
    page_title(
        "CUSTOMER ORDERS",
        "Orders & fulfilment",
        "Create orders, update their status, and track customer purchases.",
    )

    orders = data["orders"]
    products = data["products"]

    revenue = sum(
        float(o.get("total", 0))
        for o in orders
        if o.get("status") == "Completed"
    )

    pending = sum(1 for o in orders if o.get("status") == "Pending")
    processing = sum(1 for o in orders if o.get("status") == "Processing")

    c1, c2, c3 = st.columns(3)
    c1.metric("Completed revenue", money(revenue))
    c2.metric("Pending orders", pending)
    c3.metric("Processing orders", processing)

    view_tab, add_tab, manage_tab = st.tabs(
        ["📦 All Orders", "➕ Create Order", "🛠️ Manage Orders"]
    )

    with view_tab:
        if not orders:
            st.info("No orders yet.")
        else:
            st.dataframe(
                [
                    {
                        "Order ID": f"#{o['id']}",
                        "Customer": o["customer"],
                        "Product": o["product"],
                        "Quantity": o["quantity"],
                        "Total": money(o["total"]),
                        "Status": o["status"],
                        "Date": o["date"],
                    }
                    for o in sorted(
                        orders,
                        key=lambda item: str(item.get("date", "")),
                        reverse=True,
                    )
                ],
                use_container_width=True,
                hide_index=True,
            )

    with add_tab:
        if not products:
            st.warning("Add a product before creating an order.")
        else:
            with st.form("create_order_form", clear_on_submit=True):
                customer = st.text_input("Customer name")

                product_id = st.selectbox(
                    "Select product",
                    options=[p["id"] for p in products],
                    format_func=lambda pid: next(
                        f"{p['name']} — {money(p['price'])} "
                        f"(Stock: {p['stock']})"
                        for p in products
                        if p["id"] == pid
                    ),
                )

                selected_product = next(
                    p for p in products if p["id"] == product_id
                )

                max_quantity = max(1, int(selected_product["stock"]))

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=max_quantity,
                    value=1,
                    step=1,
                )

                status = st.selectbox(
                    "Order status",
                    ["Pending", "Processing", "Completed", "Cancelled"],
                )

                st.info(
                    f"Order total: "
                    f"{money(selected_product['price'] * quantity)}"
                )

                submitted = st.form_submit_button(
                    "Create order",
                    use_container_width=True,
                )

                if submitted:
                    if not customer.strip():
                        st.error("Please enter the customer's name.")
                    elif int(quantity) > int(selected_product["stock"]):
                        st.error("There is not enough stock.")
                    else:
                        new_order = {
                            "id": next_id(orders),
                            "customer": customer.strip(),
                            "product": selected_product["name"],
                            "quantity": int(quantity),
                            "total": round(
                                float(selected_product["price"])
                                * int(quantity),
                                2,
                            ),
                            "status": status,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                        }

                        orders.append(new_order)

                        if status != "Cancelled":
                            selected_product["stock"] -= int(quantity)

                        refresh_data()
                        st.success(
                            f"Order #{new_order['id']} created successfully."
                        )
                        st.rerun()

    with manage_tab:
        if not orders:
            st.info("There are no orders to manage.")
        else:
            order_id = st.selectbox(
                "Choose an order",
                options=[o["id"] for o in orders],
                format_func=lambda oid: next(
                    f"#{o['id']} — {o['customer']} — {o['product']}"
                    for o in orders
                    if o["id"] == oid
                ),
            )

            order = next(o for o in orders if o["id"] == order_id)

            st.write(f"**Customer:** {order['customer']}")
            st.write(f"**Product:** {order['product']}")
            st.write(f"**Total:** {money(order['total'])}")
            st.write(f"**Current status:** {order['status']}")

            statuses = [
                "Pending",
                "Processing",
                "Completed",
                "Cancelled",
            ]

            new_status = st.selectbox(
                "Update status",
                statuses,
                index=statuses.index(order["status"])
                if order["status"] in statuses
                else 0,
                key=f"status_{order_id}",
            )

            if st.button("Update order status"):
                order["status"] = new_status
                refresh_data()
                st.success("Order status updated.")
                st.rerun()

            st.markdown("---")

            confirm_delete = st.checkbox(
                f"Confirm deletion of order #{order_id}",
                key=f"delete_order_{order_id}",
            )

            if st.button(
                "Delete selected order",
                disabled=not confirm_delete,
            ):
                data["orders"] = [
                    o for o in data["orders"]
                    if o["id"] != order_id
                ]

                refresh_data()
                st.success("Order deleted.")
                st.rerun()


# ==========================================================
# 12. OUR TEAM PAGE
# ==========================================================

def show_team():
    page_title(
        "OUR PEOPLE",
        "Our team & tasks",
        "Organise our daily work and track team responsibilities.",
    )

    team = data["team"]

    completed = sum(
        1 for m in team if m.get("status") == "Completed"
    )
    in_progress = sum(
        1 for m in team if m.get("status") == "In progress"
    )
    pending = sum(
        1 for m in team if m.get("status") == "Pending"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Completed tasks", completed)
    c2.metric("In progress", in_progress)
    c3.metric("Pending tasks", pending)

    view_tab, add_tab, manage_tab = st.tabs(
        ["👥 Our Team", "➕ Add Team Member", "🛠️ Manage Tasks"]
    )

    with view_tab:
        if not team:
            st.info("Add our first team member.")
        else:
            for member in team:
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])

                    with c1:
                        st.markdown(f"### 👤 {member['name']}")
                        st.write(f"**Role:** {member['role']}")
                        st.write(f"**Task:** {member['task']}")

                    with c2:
                        st.write("**Task status**")

                        if member["status"] == "Completed":
                            st.success(member["status"])
                        elif member["status"] == "In progress":
                            st.info(member["status"])
                        else:
                            st.warning(member["status"])

    with add_tab:
        with st.form("add_team_form", clear_on_submit=True):
            name = st.text_input("Team member name")
            role = st.text_input("Role")
            task = st.text_input("Assigned task")

            status = st.selectbox(
                "Task status",
                ["Pending", "In progress", "Completed"],
            )

            submitted = st.form_submit_button(
                "Add team member",
                use_container_width=True,
            )

            if submitted:
                if not name.strip():
                    st.error("Please enter a team member name.")
                elif not role.strip():
                    st.error("Please enter a role.")
                else:
                    team.append(
                        {
                            "id": next_id(team),
                            "name": name.strip(),
                            "role": role.strip(),
                            "task": task.strip(),
                            "status": status,
                        }
                    )

                    refresh_data()
                    st.success("Team member added.")
                    st.rerun()

    with manage_tab:
        if not team:
            st.info("There are no team members to manage.")
        else:
            member_id = st.selectbox(
                "Select team member",
                options=[m["id"] for m in team],
                format_func=lambda mid: next(
                    m["name"] for m in team if m["id"] == mid
                ),
            )

            member = next(m for m in team if m["id"] == member_id)

            with st.form("edit_team_form"):
                name = st.text_input("Name", value=member["name"])
                role = st.text_input("Role", value=member["role"])
                task = st.text_input("Task", value=member.get("task", ""))

                statuses = ["Pending", "In progress", "Completed"]

                status = st.selectbox(
                    "Task status",
                    statuses,
                    index=statuses.index(member["status"])
                    if member["status"] in statuses
                    else 0,
                )

                submitted = st.form_submit_button(
                    "Save team changes",
                    use_container_width=True,
                )

                if submitted:
                    member["name"] = name.strip()
                    member["role"] = role.strip()
                    member["task"] = task.strip()
                    member["status"] = status

                    refresh_data()
                    st.success("Team details updated.")
                    st.rerun()

            confirm_delete = st.checkbox(
                f"Confirm deletion of {member['name']}",
                key=f"delete_member_{member_id}",
            )

            if st.button(
                "Delete team member",
                disabled=not confirm_delete,
            ):
                data["team"] = [
                    m for m in data["team"]
                    if m["id"] != member_id
                ]

                refresh_data()
                st.success("Team member deleted.")
                st.rerun()


# ==========================================================
# 13. JARVIS AI PAGE
# ==========================================================

def show_jarvis():
    page_title(
        "OUR BUSINESS CO-PILOT",
        "Meet Jarvis AI",
        "Our AI assistant for candle ideas, marketing, and business decisions.",
    )

    st.markdown(
        """
        <div class="jarvis-banner">
            <h2>🤖 Hello, I'm Jarvis!</h2>
            <p>
                Ask me anything about our handmade candle brand GLOW NEST.
                I can help with planning, writing, calculations, and ideas.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 💡 Try asking Jarvis")

    quick_prompts = [
        "Give me 5 marketing ideas for our candle business.",
        "Write an Instagram caption for our new candle.",
        "How can we increase our candle sales?",
        "Suggest a new candle fragrance for our collection.",
    ]

    columns = st.columns(2)

    for index, prompt in enumerate(quick_prompts):
        with columns[index % 2]:
            if st.button(
                prompt,
                key=f"jarvis_quick_{index}",
                use_container_width=True,
            ):
                st.session_state.jarvis_messages.append(
                    {"role": "user", "content": prompt}
                )

                with st.spinner("Jarvis is thinking..."):
                    answer = ask_jarvis(
                        st.session_state.jarvis_messages
                    )

                st.session_state.jarvis_messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Chat with Jarvis")

    for message in st.session_state.jarvis_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "Ask Jarvis about our candle business..."
    )

    if user_prompt:
        st.session_state.jarvis_messages.append(
            {"role": "user", "content": user_prompt}
        )

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Jarvis is thinking..."):
                answer = ask_jarvis(
                    st.session_state.jarvis_messages
                )
            st.markdown(answer)

        st.session_state.jarvis_messages.append(
            {"role": "assistant", "content": answer}
        )

    if st.button("🗑️ Clear chat"):
        st.session_state.jarvis_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm Jarvis, our GLOW NEST business assistant. "
                    "What would you like help with today?"
                ),
            }
        ]
        st.rerun()

    st.caption(
        "AI suggestions may be incorrect. Review important decisions "
        "before using them in our business."
    )


# ==========================================================
# 14. PROFIT CALCULATOR PAGE
# ==========================================================

def show_profit_calculator():
    page_title(
        "SMART BUSINESS TOOLS",
        "Profit calculator",
        "Calculate candle profits and estimate earnings for our business.",
    )

    st.markdown("### 🧮 Calculate profit per candle")

    c1, c2 = st.columns(2)

    with c1:
        selling_price = st.number_input(
            "Selling price per candle (€)",
            min_value=0.0,
            value=18.0,
            step=0.5,
        )

        material_cost = st.number_input(
            "Materials cost (€)",
            min_value=0.0,
            value=4.0,
            step=0.5,
        )

        packaging_cost = st.number_input(
            "Packaging cost (€)",
            min_value=0.0,
            value=1.5,
            step=0.5,
        )

    with c2:
        labour_cost = st.number_input(
            "Labour cost per candle (€)",
            min_value=0.0,
            value=1.0,
            step=0.5,
        )

        other_cost = st.number_input(
            "Other costs per candle (€)",
            min_value=0.0,
            value=0.5,
            step=0.5,
        )

        quantity = st.number_input(
            "Number of candles sold",
            min_value=0,
            value=50,
            step=1,
        )

    total_unit_cost = (
        material_cost
        + packaging_cost
        + labour_cost
        + other_cost
    )

    unit_profit = selling_price - total_unit_cost

    margin = (
        unit_profit / selling_price * 100
        if selling_price > 0
        else 0
    )

    total_revenue = selling_price * quantity
    total_cost = total_unit_cost * quantity
    total_profit = unit_profit * quantity

    st.markdown("---")
    st.markdown("### 📊 Our estimated results")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Profit per candle",
            money(unit_profit),
            "Selling price minus unit costs",
            "🕯️",
        )

    with c2:
        metric_card(
            "Profit margin",
            f"{margin:.1f}%",
            "Profit as a percentage of selling price",
            "📈",
        )

    with c3:
        metric_card(
            "Estimated total profit",
            money(total_profit),
            f"For {quantity} candles",
            "💰",
        )

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Revenue and costs")
        st.write(f"**Total revenue:** {money(total_revenue)}")
        st.write(f"**Total costs:** {money(total_cost)}")
        st.write(f"**Estimated profit:** {money(total_profit)}")

    with c2:
        st.markdown("#### Cost breakdown per candle")
        st.write(f"Materials: {money(material_cost)}")
        st.write(f"Packaging: {money(packaging_cost)}")
        st.write(f"Labour: {money(labour_cost)}")
        st.write(f"Other costs: {money(other_cost)}")
        st.write(f"**Total unit cost:** {money(total_unit_cost)}")

    if unit_profit < 0:
        st.error(
            "Our candle is making a loss. Consider reducing costs "
            "or reviewing the selling price."
        )
    elif unit_profit == 0:
        st.warning("Our candle is breaking even.")
    else:
        st.success(
            "Our candle is profitable based on the costs entered."
        )

    st.caption(
        "This estimate excludes taxes, delivery charges, and other costs "
        "unless you include them above."
    )


# ==========================================================
# 15. MAIN APP ROUTER
# ==========================================================

current_page = st.session_state.page

if current_page == "Overview":
    show_overview()

elif current_page == "Products":
    show_products()

elif current_page == "Orders":
    show_orders()

elif current_page == "Our Team":
    show_team()

elif current_page == "Jarvis AI":
    show_jarvis()

elif current_page == "Profit Calculator":
    show_profit_calculator()

else:
    show_overview()


# ==========================================================
# 16. FOOTER
# ==========================================================

st.markdown(
    """
    <div class="footer">
        🕯️ GLOW NEST · Our Business, Our Passion · Made with care
    </div>
    """,
    unsafe_allow_html=True,
)