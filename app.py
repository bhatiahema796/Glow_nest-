import json
import os
from pathlib import Path
from datetime import date

import requests
import streamlit as st

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="GLOW NEST | Candle Studio",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).with_name("glow_nest_data.json")


# -------------------- API SETTINGS --------------------
def get_setting(name, default=""):
    """Read Streamlit Secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, None)
        if value not in (None, ""):
            return str(value)
    except Exception:
        pass

    return os.getenv(name, default)


JARVIS_URL = get_setting(
    "JARVIS_BASE_URL",
    "https://openrouter.ai/api/v1",
).rstrip("/")

JARVIS_MODEL = get_setting(
    "JARVIS_MODEL",
    "qwen/qwen3-4b:free",
)


# -------------------- DEFAULT DATA --------------------
DEFAULT_DATA = {
    "products": [
        {
            "name": "Amber Glow",
            "category": "Signature",
            "price": 18.50,
            "cost": 7.00,
            "stock": 24,
            "image": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=900&q=85",
        },
        {
            "name": "Vanilla Cloud",
            "category": "Soft & Sweet",
            "price": 16.00,
            "cost": 6.00,
            "stock": 18,
            "image": "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?auto=format&fit=crop&w=900&q=85",
        },
        {
            "name": "Midnight Cedar",
            "category": "Woody",
            "price": 22.00,
            "cost": 9.00,
            "stock": 9,
            "image": "https://images.unsplash.com/photo-1602523961358-f9f03dd557db?auto=format&fit=crop&w=900&q=85",
        },
        {
            "name": "Rose Ritual",
            "category": "Floral",
            "price": 19.50,
            "cost": 7.50,
            "stock": 14,
            "image": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=900&q=85",
        },
    ],
    "orders": [
        {
            "customer": "Emma L.",
            "product": "Amber Glow",
            "qty": 2,
            "status": "Preparing",
            "created": str(date.today()),
            "total": 37.00,
        },
        {
            "customer": "Sofia M.",
            "product": "Vanilla Cloud",
            "qty": 1,
            "status": "Ready to ship",
            "created": str(date.today()),
            "total": 16.00,
        },
        {
            "customer": "Laura K.",
            "product": "Midnight Cedar",
            "qty": 1,
            "status": "New",
            "created": str(date.today()),
            "total": 22.00,
        },
    ],
    "employees": [
        {
            "name": "Employee 1",
            "role": "Candle Making",
            "task": "Prepare today's candle batch",
            "status": "In progress",
        },
        {
            "name": "Employee 2",
            "role": "Packing",
            "task": "Pack completed candle orders",
            "status": "Pending",
        },
        {
            "name": "Employee 3",
            "role": "Order Management",
            "task": "Check new customer orders",
            "status": "In progress",
        },
        {
            "name": "Employee 4",
            "role": "Stock Management",
            "task": "Check low-stock products",
            "status": "Pending",
        },
        {
            "name": "Employee 5",
            "role": "Customer Support",
            "task": "Reply to customer messages",
            "status": "Completed",
        },
    ],
}


# -------------------- LOAD AND SAVE DATA --------------------
def load_data():
    if DATA_FILE.exists():
        try:
            saved = json.loads(
                DATA_FILE.read_text(encoding="utf-8")
            )

            for key, value in DEFAULT_DATA.items():
                saved.setdefault(key, value)

            return saved

        except (json.JSONDecodeError, OSError):
            pass

    return json.loads(json.dumps(DEFAULT_DATA))


if "data" not in st.session_state:
    st.session_state.data = load_data()

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

data = st.session_state.data


def save_data():
    DATA_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def euro(value):
    return f"€{float(value):,.2f}"


# -------------------- JARVIS AI FUNCTION --------------------
def ask_jarvis(prompt, business_context):
    """Send a message to Jarvis using the OpenRouter API."""

    api_key = get_setting("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing. "
            "Add your API key in Streamlit Cloud "
            "under Settings > Secrets."
        )

    system_prompt = (
        "You are Jarvis, a friendly and practical AI assistant "
        "for GLOW NEST, a candle business. "
        "Use simple English and give helpful, concise answers. "
        "Use the business data provided below. "
        "Do not invent business figures. "
        "Business data: " + business_context
    )

    try:
        response = requests.post(
            f"{JARVIS_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": JARVIS_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.7,
                "max_tokens": 450,
            },
            timeout=90,
        )

        if response.status_code != 200:
            try:
                detail = response.json().get("error", {})

                if isinstance(detail, dict):
                    detail = detail.get(
                        "message",
                        str(detail),
                    )

            except (ValueError, AttributeError):
                detail = response.text[:500]

            raise RuntimeError(
                f"AI API error ({response.status_code}): "
                f"{detail}"
            )

        result = response.json()

        return result["choices"][0]["message"]["content"]

    except requests.Timeout:
        raise RuntimeError(
            "Jarvis took too long to respond. Please try again."
        )

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to Jarvis: {exc}"
        )

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError(
            f"Unexpected AI response: {exc}"
        )


# -------------------- STYLE --------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

:root {
    --gold: #f2c879;
    --cream: #f8fafc;
    --muted: #d1d8e2;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: radial-gradient(
        ellipse at 85% 0%,
        #263449 0%,
        #151d2b 44%,
        #0d1320 100%
    );
    color: var(--cream);
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1d293b 0%,
        #111827 100%
    );
    border-right: 1px solid #344256;
}

[data-testid="stSidebar"] * {
    color: #f8fafc;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #f8fafc !important;
}

p, label, .stCaption {
    color: #e2e8f0;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #263449, #1b2636);
    border: 1px solid #3a4a60;
    padding: 18px 20px;
    border-radius: 18px;
    box-shadow: 0 12px 32px #00000020;
}

div[data-testid="stMetricLabel"] {
    color: #dbe5f1 !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

div[data-testid="stMetricDelta"] {
    color: #c4d9a7 !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #e7c98e, #c18d4e);
    color: #24170f;
    border: 0;
    border-radius: 12px;
    font-weight: 700;
    min-height: 2.65rem;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #f2d7a5;
    color: #24170f;
    border: 0;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
div[data-baseweb="select"] > div {
    background: #111827 !important;
    color: #ffffff !important;
    border-color: #52627a !important;
    border-radius: 10px !important;
}

div[data-testid="stChatMessage"] {
    background: #202c3e;
    border: 1px solid #40516a;
    border-radius: 16px;
    color: #f8fafc;
}

hr {
    border-color: #344256;
}

.hero {
    background: linear-gradient(
        115deg,
        rgba(37,52,73,.98),
        rgba(24,34,49,.96)
    );
    border: 1px solid #465873;
    border-radius: 24px;
    padding: 27px 30px;
    box-shadow: 0 18px 45px #00000024;
}

.eyebrow {
    color: #f2c879;
    font-size: .75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2.4px;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.65rem;
    line-height: 1.13;
    color: #ffffff;
    margin: .45rem 0 .7rem;
}

.hero-sub {
    color: #e2e8f0;
    font-size: 1rem;
    line-height: 1.65;
}

.brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    letter-spacing: 3px;
    color: #f2c879;
}

.brand-sub {
    font-size: .65rem;
    letter-spacing: 2.3px;
    color: #dbe5f1;
    margin-top: 4px;
}

.product-card {
    background: linear-gradient(150deg, #263449, #1b2636);
    border: 1px solid #3a4a60;
    border-radius: 18px;
    overflow: hidden;
}

.product-info {
    padding: 16px 17px 18px;
}

.product-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    color: #ffffff;
}

.muted {
    color: #d1dbe8;
    font-size: .86rem;
}

.pill {
    display: inline-block;
    border: 1px solid #6c5a38;
    background: #293448;
    color: #ffe0a0;
    padding: 5px 10px;
    border-radius: 30px;
    font-size: .75rem;
}

.task-card {
    background: #202c3e;
    border: 1px solid #40516a;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 10px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #40516a;
    border-radius: 12px;
}
</style>
""",
    unsafe_allow_html=True,
)


# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown(
        "<div style='font-size:2.2rem'>🕯️</div>"
        "<div class='brand'>GLOW NEST</div>"
        "<div class='brand-sub'>THE ART OF WARMTH</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("YOUR CANDLE BUSINESS STUDIO")

    pages = [
        ("✦", "Overview"),
        ("🕯️", "Products & Stock"),
        ("📦", "Orders"),
        ("♧", "Team & Tasks"),
        ("✧", "Jarvis AI"),
        ("◎", "Profit Studio"),
    ]

    for icon, label in pages:
        if st.button(
            f"{icon}   {label}",
            key=f"nav_{label}",
            use_container_width=True,
        ):
            st.session_state.page = label
            st.rerun()

    st.markdown("---")

    st.markdown(
        "<span class='pill'>● Workspace ready</span>",
        unsafe_allow_html=True,
    )

    st.caption(
        "Your business data is saved locally on this computer."
    )

    st.markdown(
        "<div style='height:18px'></div>"
        "<div class='muted'>Handcrafted candles. Beautiful moments.</div>",
        unsafe_allow_html=True,
    )


# -------------------- CALCULATIONS --------------------
products = data["products"]
orders = data["orders"]
employees = data["employees"]

stock_units = sum(
    int(product.get("stock", 0))
    for product in products
)

low_stock = sum(
    1
    for product in products
    if int(product.get("stock", 0)) < 10
)

tracked_sales = sum(
    float(order.get("total", 0))
    for order in orders
    if order.get("status") in [
        "Preparing",
        "Ready to ship",
        "Shipped",
        "Completed",
    ]
)

pending_tasks = sum(
    1
    for employee in employees
    if employee.get("status") != "Completed"
)

stock_margin = sum(
    (
        float(product.get("price", 0))
        - float(product.get("cost", 0))
    )
    * int(product.get("stock", 0))
    for product in products
)


# -------------------- TOP HEADER --------------------
page = st.session_state.page

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        "<div class='eyebrow'>THE CANDLE BUSINESS DASHBOARD</div>",
        unsafe_allow_html=True,
    )

    title = (
        "Your business, glowing brighter."
        if page == "Overview"
        else page
    )

    st.markdown(
        f"<div class='hero-title'>{title}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='hero-sub'>One beautiful place for your candles, "
        "your team, and your next big idea.</div>",
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        f"<div style='text-align:right;padding-top:12px;"
        f"color:#f2c879;font-weight:700'>"
        f"{date.today().strftime('%A')}</div>"
        f"<div style='text-align:right;color:#d1dbe8'>"
        f"{date.today().strftime('%d %B %Y')}</div>",
        unsafe_allow_html=True,
    )


# -------------------- OVERVIEW --------------------
if page == "Overview":
    hero_left, hero_right = st.columns([1.55, 1])

    with hero_left:
        st.markdown(
            """
            <div class="hero" style="height:100%">
              <div class="eyebrow">WELCOME TO GLOW NEST</div>
              <div style="font-family:Playfair Display,serif;
              font-size:2rem;color:#ffffff;line-height:1.2;
              margin:10px 0">
                The little details make the glow.
              </div>
              <div class="hero-sub">
                Manage your handmade candle collection, stay on top
                of customer orders, and keep your whole team moving
                — without the chaos.
              </div>
              <div style="margin-top:19px">
                <span class="pill">✦ Thoughtful products</span>
                <span class="pill">✦ One simple workspace</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with hero_right:
        st.image(
            "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=1000&q=85",
            caption="GLOW NEST · Light up your moments",
            use_container_width=True,
        )

    st.markdown("")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Sales tracked",
        euro(tracked_sales),
        "active & completed orders",
    )

    m2.metric(
        "Candles in stock",
        stock_units,
        f"{low_stock} low-stock products",
    )

    m3.metric(
        "Open team tasks",
        pending_tasks,
        f"of {len(employees)} employees",
    )

    m4.metric(
        "Estimated stock margin",
        euro(stock_margin),
        "before other expenses",
    )

    st.caption(
        "Demo orders and product details are included so you can "
        "explore the dashboard. Replace them with your real business information."
    )

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("### 📦 Recent orders")

        if orders:
            for order in orders[:4]:
                st.markdown(
                    f"""
                    <div class="task-card">
                      <div style="display:flex;justify-content:space-between;
                      gap:8px">
                        <b style="color:#f8fafc">
                          {order.get('customer', 'Customer')}
                        </b>
                        <span class="pill">
                          {order.get('status', 'New')}
                        </span>
                      </div>
                      <div class="muted" style="margin-top:6px">
                        {order.get('product')} · Qty {order.get('qty', 1)}
                        · {order.get('created', '')}
                      </div>
                      <div style="color:#f2c879;font-weight:700;margin-top:8px">
                        {euro(order.get('total', 0))}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No orders yet. Add your first order in Orders.")

    with right:
        st.markdown("### ♧ Team at a glance")

        for employee in employees:
            icon = (
                "✓"
                if employee.get("status") == "Completed"
                else (
                    "◷"
                    if employee.get("status") == "In progress"
                    else "○"
                )
            )

            st.markdown(
                f"""
                <div style="display:flex;gap:11px;align-items:center;
                padding:11px 0;border-bottom:1px solid #3d2b21">
                  <div style="background:#3b281d;border:1px solid #65472d;
                  border-radius:12px;width:38px;height:38px;display:flex;
                  align-items:center;justify-content:center;
                  color:#e5bd7a;font-weight:700">
                    {icon}
                  </div>
                  <div style="flex:1">
                    <div style="color:#f8fafc;font-weight:600">
                      {employee.get('name')}
                    </div>
                    <div class="muted">{employee.get('task')}</div>
                  </div>
                  <span class="pill">{employee.get('status')}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")

    quick1, quick2, quick3 = st.columns(3)

    if quick1.button("＋ Add a candle", use_container_width=True):
        st.session_state.page = "Products & Stock"
        st.rerun()

    if quick2.button("📦 View orders", use_container_width=True):
        st.session_state.page = "Orders"
        st.rerun()

    if quick3.button("✧ Ask Jarvis", use_container_width=True):
        st.session_state.page = "Jarvis AI"
        st.rerun()


# -------------------- PRODUCTS --------------------
elif page == "Products & Stock":
    st.markdown("### Your candle collection")

    st.caption(
        "Beautiful products, clear pricing, and stock at a glance. "
        "Prices are in euros."
    )

    with st.expander("＋ Add a new candle"):
        with st.form("add_product", clear_on_submit=True):
            c1, c2 = st.columns(2)

            name = c1.text_input("Candle name")

            category = c2.selectbox(
                "Collection",
                [
                    "Signature",
                    "Soft & Sweet",
                    "Woody",
                    "Floral",
                    "Seasonal",
                    "Other",
                ],
            )

            c3, c4, c5 = st.columns(3)

            price = c3.number_input(
                "Selling price (€)",
                min_value=0.0,
                value=18.0,
                step=0.5,
            )

            cost = c4.number_input(
                "Making cost (€)",
                min_value=0.0,
                value=7.0,
                step=0.5,
            )

            stock = c5.number_input(
                "Units in stock",
                min_value=0,
                value=10,
                step=1,
            )

            image_url = st.text_input(
                "Product image URL (optional)",
                placeholder="https://...",
            )

            if st.form_submit_button("Save candle"):
                if not name.strip():
                    st.warning("Please enter a candle name.")
                else:
                    products.append(
                        {
                            "name": name.strip(),
                            "category": category,
                            "price": price,
                            "cost": cost,
                            "stock": int(stock),
                            "image": image_url.strip(),
                        }
                    )

                    save_data()
                    st.success("Candle added!")
                    st.rerun()

    if products:
        cols = st.columns(2)

        for i, product in enumerate(products):
            with cols[i % 2]:
                img = product.get("image", "")

                if img:
                    try:
                        st.image(img, use_container_width=True)
                    except Exception:
                        st.markdown("🕯️")
                else:
                    st.markdown(
                        "<div class='hero' style='text-align:center;"
                        "font-size:3rem'>🕯️</div>",
                        unsafe_allow_html=True,
                    )

                stock = int(product.get("stock", 0))

                st.markdown(
                    f"<div class='product-name'>{product.get('name')}</div>"
                    f"<div class='muted'>{product.get('category', 'Collection')}</div>"
                    f"<div style='display:flex;justify-content:space-between;"
                    f"margin:8px 0 12px'>"
                    f"<span style='color:#f2c879;font-weight:700'>"
                    f"{euro(product.get('price', 0))}</span>"
                    f"<span class='pill'>{stock} in stock</span></div>",
                    unsafe_allow_html=True,
                )

                with st.expander(f"Edit {product.get('name')}"):
                    product["name"] = st.text_input(
                        "Name",
                        value=product.get("name", ""),
                        key=f"pn{i}",
                    )

                    categories = [
                        "Signature",
                        "Soft & Sweet",
                        "Woody",
                        "Floral",
                        "Seasonal",
                        "Other",
                    ]

                    product["category"] = st.selectbox(
                        "Category",
                        categories,
                        index=(
                            categories.index(product.get("category", "Other"))
                            if product.get("category") in categories
                            else 5
                        ),
                        key=f"pc{i}",
                    )

                    product["price"] = st.number_input(
                        "Price (€)",
                        min_value=0.0,
                        value=float(product.get("price", 0)),
                        step=0.5,
                        key=f"pp{i}",
                    )

                    product["cost"] = st.number_input(
                        "Cost (€)",
                        min_value=0.0,
                        value=float(product.get("cost", 0)),
                        step=0.5,
                        key=f"pk{i}",
                    )

                    product["stock"] = st.number_input(
                        "Stock",
                        min_value=0,
                        value=int(product.get("stock", 0)),
                        step=1,
                        key=f"ps{i}",
                    )

                    product["image"] = st.text_input(
                        "Image URL",
                        value=product.get("image", ""),
                        key=f"pi{i}",
                    )

                    save_col, delete_col = st.columns(2)

                    if save_col.button(
                        "Save changes",
                        key=f"savep{i}",
                        use_container_width=True,
                    ):
                        product["stock"] = int(product["stock"])
                        save_data()
                        st.success("Product updated.")
                        st.rerun()

                    if delete_col.button(
                        "Delete",
                        key=f"delp{i}",
                        use_container_width=True,
                    ):
                        products.pop(i)
                        save_data()
                        st.rerun()

    else:
        st.info("Add your first candle to begin.")


# -------------------- ORDERS --------------------
elif page == "Orders":
    st.markdown("### From your studio to their doorstep")

    with st.expander("＋ Create customer order"):
        with st.form("add_order", clear_on_submit=True):
            customer = st.text_input("Customer name")
            names = [product["name"] for product in products]

            if names:
                product_name = st.selectbox("Candle", names)

                qty = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    step=1,
                )

                status = st.selectbox(
                    "Order status",
                    [
                        "New",
                        "Preparing",
                        "Ready to ship",
                        "Shipped",
                        "Completed",
                    ],
                )

                if st.form_submit_button("Create order"):
                    product = next(
                        product
                        for product in products
                        if product["name"] == product_name
                    )

                    if not customer.strip():
                        st.warning("Enter the customer name.")

                    elif int(product["stock"]) < int(qty):
                        st.error("Not enough stock for this order.")

                    else:
                        product["stock"] = (
                            int(product["stock"]) - int(qty)
                        )

                        orders.insert(
                            0,
                            {
                                "customer": customer.strip(),
                                "product": product_name,
                                "qty": int(qty),
                                "status": status,
                                "created": str(date.today()),
                                "total": (
                                    float(product["price"]) * int(qty)
                                ),
                            },
                        )

                        save_data()
                        st.success("Order created and stock updated.")
                        st.rerun()

            else:
                st.info("Add a product before creating an order.")

    if not orders:
        st.info("Your order list is empty.")

    for i, order in enumerate(orders):
        with st.container(border=True):
            a, b, c = st.columns([2, 1.5, 1])

            a.markdown(f"**{order.get('customer', 'Customer')}**")

            a.caption(
                f"{order.get('product')} · Qty {order.get('qty', 1)} "
                f"· {order.get('created', '')}"
            )

            b.markdown(f"### {euro(order.get('total', 0))}")

            statuses = [
                "New",
                "Preparing",
                "Ready to ship",
                "Shipped",
                "Completed",
            ]

            current = order.get("status", "New")

            order["status"] = b.selectbox(
                "Status",
                statuses,
                index=(
                    statuses.index(current)
                    if current in statuses
                    else 0
                ),
                key=f"os{i}",
            )

            if c.button("Delete order", key=f"do{i}"):
                orders.pop(i)
                save_data()
                st.rerun()

    if st.button("Save order updates"):
        save_data()
        st.success("Orders saved.")


# -------------------- TEAM --------------------
elif page == "Team & Tasks":
    st.markdown("### Five people. One glowing team.")

    st.caption(
        "No logins or complicated setup — just give each person a task "
        "and update progress."
    )

    for i, employee in enumerate(employees):
        with st.container(border=True):
            left, right = st.columns([1, 2])

            with left:
                st.markdown(f"#### ♧ Team member {i + 1}")

                employee["name"] = st.text_input(
                    "Employee name",
                    value=employee.get("name", ""),
                    key=f"en{i}",
                )

                employee["role"] = st.text_input(
                    "Responsibility",
                    value=employee.get("role", ""),
                    key=f"er{i}",
                )

            with right:
                employee["task"] = st.text_input(
                    "Current task",
                    value=employee.get("task", ""),
                    key=f"et{i}",
                )

                statuses = [
                    "Pending",
                    "In progress",
                    "Completed",
                ]

                current = employee.get("status", "Pending")

                employee["status"] = st.selectbox(
                    "Task status",
                    statuses,
                    index=(
                        statuses.index(current)
                        if current in statuses
                        else 0
                    ),
                    key=f"es{i}",
                )

    if st.button("Save team updates", use_container_width=True):
        save_data()
        st.success("Team tasks saved.")
        st.rerun()

    completed = sum(
        1
        for employee in employees
        if employee.get("status") == "Completed"
    )

    st.progress(
        completed / max(len(employees), 1),
        text=f"{completed} of {len(employees)} tasks completed",
    )


# -------------------- JARVIS AI --------------------
elif page == "Jarvis AI":
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">YOUR BUSINESS CO-PILOT</div>
          <div style="font-family:Playfair Display,serif;
          font-size:1.8rem;color:#ffffff;margin:8px 0">
            Hello, I'm Jarvis. ✦
          </div>
          <div class="hero-sub">
            I can help with candle marketing, customer replies,
            business ideas, and a summary of your team's tasks.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    business_context = (
        f"Products: {json.dumps(products, ensure_ascii=False)}; "
        f"Orders: {json.dumps(orders, ensure_ascii=False)}; "
        f"Team: {json.dumps(employees, ensure_ascii=False)}; "
        f"Tracked sales: {euro(tracked_sales)}."
    )

    q1, q2, q3 = st.columns(3)

    quick_prompts = [
        (
            "✦ Write an Instagram caption",
            "Write an elegant Instagram caption for my handmade "
            "candle brand Glow Nest. Add a few relevant hashtags.",
        ),
        (
            "♧ Summarise team tasks",
            "Summarise the five employees' current tasks, who has "
            "completed work, and what is still pending.",
        ),
        (
            "↗ Ideas to grow sales",
            "Give me three practical, low-cost ideas to increase "
            "sales for my candle business.",
        ),
    ]

    for col, (label, prompt_text) in zip(
        [q1, q2, q3],
        quick_prompts,
    ):
        if col.button(label, use_container_width=True):
            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": prompt_text,
                }
            )

            try:
                answer = ask_jarvis(
                    prompt_text,
                    business_context,
                )
            except RuntimeError as exc:
                answer = str(exc)

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(
            message["role"],
            avatar=(
                "🤖"
                if message["role"] == "assistant"
                else "🙂"
            ),
        ):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask Jarvis about your candle business..."
    )

    if prompt:
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user", avatar="🙂"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Jarvis is thinking..."):
                try:
                    answer = ask_jarvis(
                        prompt,
                        business_context,
                    )
                except RuntimeError as exc:
                    answer = str(exc)

                st.markdown(answer)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )


# -------------------- PROFIT --------------------
elif page == "Profit Studio":
    st.markdown("### The numbers behind the glow")

    st.caption(
        "Estimate candle profit before rent, packaging, delivery, "
        "tax, and other overheads."
    )

    if products:
        selected = st.selectbox(
            "Choose a candle",
            [product["name"] for product in products],
        )

        product = next(
            product
            for product in products
            if product["name"] == selected
        )

        c1, c2 = st.columns(2)

        selling = c1.number_input(
            "Selling price (€)",
            min_value=0.0,
            value=float(product.get("price", 0)),
            step=0.5,
        )

        cost = c2.number_input(
            "Making cost (€)",
            min_value=0.0,
            value=float(product.get("cost", 0)),
            step=0.5,
        )

        units = st.number_input(
            "Units to sell",
            min_value=1,
            value=20,
            step=1,
        )

        unit_profit = selling - cost
        total_profit = unit_profit * int(units)

        a, b, c = st.columns(3)

        a.metric(
            "Profit per candle",
            euro(unit_profit),
        )

        b.metric(
            "Estimated total profit",
            euro(total_profit),
        )

        c.metric(
            "Profit margin",
            f"{unit_profit / selling * 100:.1f}%"
            if selling
            else "0.0%",
        )

        if unit_profit < 0:
            st.warning(
                "Your making cost is higher than your selling price."
            )
        else:
            st.success(
                "Estimate only — excludes other business expenses."
            )

    else:
        st.info("Add a product first.")


# -------------------- FOOTER --------------------
st.markdown("---")

st.markdown(
    "<div style='display:flex;justify-content:space-between;"
    "gap:10px;flex-wrap:wrap;color:#b9c5d5;font-size:.78rem'>"
    "<span>GLOW NEST · THE CANDLE BUSINESS STUDIO</span>"
    "<span>Handcrafted candles. Beautiful moments.</span></div>",
    unsafe_allow_html=True,
)