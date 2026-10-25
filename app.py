
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
JARVIS_URL = os.getenv(
    "JARVIS_BASE_URL", "http://127.0.0.1:8000"
).rstrip("/")
JARVIS_MODEL = os.getenv("JARVIS_MODEL", "qwen3:0.6b")

# -------------------- DEFAULT BUSINESS DATA --------------------
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
                saved.setdefault(key, json.loads(json.dumps(value)))

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


# -------------------- BUILD LIVE DASHBOARD CONTEXT --------------------
def build_dashboard_context():
    """
    Create a fresh snapshot of the current business data
    whenever Jarvis receives a question.
    """
    current_data = st.session_state.data

    products = current_data.get("products", [])
    orders = current_data.get("orders", [])
    employees = current_data.get("employees", [])

    completed_statuses = {"completed", "delivered"}
    cancelled_statuses = {"cancelled", "canceled"}

    open_statuses = {
        "new",
        "preparing",
        "ready to ship",
        "pending",
        "processing",
        "in progress",
    }

    def get_status(record):
        return str(record.get("status", "")).strip().lower()

    product_lookup = {
        str(product.get("name", "")).strip().lower(): product
        for product in products
    }

    def get_product_cost(order):
        product_name = str(
            order.get("product", "")
        ).strip().lower()

        product = product_lookup.get(product_name, {})
        return float(product.get("cost", 0) or 0)

    def get_order_quantity(order):
        return int(order.get("qty", 1) or 1)

    # Order counts
    completed_orders = [
        order for order in orders
        if get_status(order) in completed_statuses
    ]

    cancelled_orders = [
        order for order in orders
        if get_status(order) in cancelled_statuses
    ]

    open_orders = [
        order for order in orders
        if get_status(order) in open_statuses
    ]

    # Financial calculations
    total_order_value = sum(
        float(order.get("total", 0) or 0)
        for order in orders
    )

    completed_revenue = sum(
        float(order.get("total", 0) or 0)
        for order in completed_orders
    )

    completed_product_cost = sum(
        get_product_cost(order) * get_order_quantity(order)
        for order in completed_orders
    )

    estimated_completed_profit = (
        completed_revenue - completed_product_cost
    )

    # Inventory calculations
    total_stock_units = sum(
        int(product.get("stock", 0) or 0)
        for product in products
    )

    low_stock_products = [
        {
            "name": product.get("name", "Unnamed product"),
            "category": product.get("category", ""),
            "stock": int(product.get("stock", 0) or 0),
        }
        for product in products
        if int(product.get("stock", 0) or 0) <= 10
    ]

    out_of_stock_products = [
        product.get("name", "Unnamed product")
        for product in products
        if int(product.get("stock", 0) or 0) == 0
    ]

    # Team task calculations
    task_status_counts = {}

    for employee in employees:
        status = str(employee.get("status", "Pending"))

        task_status_counts[status] = (
            task_status_counts.get(status, 0) + 1
        )

    # Remove image URLs to keep the AI context smaller.
    product_records = [
        {
            "name": product.get("name", ""),
            "category": product.get("category", ""),
            "price": float(product.get("price", 0) or 0),
            "cost": float(product.get("cost", 0) or 0),
            "stock": int(product.get("stock", 0) or 0),
        }
        for product in products
    ]

    order_records = [
        {
            "customer": order.get("customer", ""),
            "product": order.get("product", ""),
            "quantity": get_order_quantity(order),
            "status": order.get("status", "New"),
            "date": order.get("created", ""),
            "total": float(order.get("total", 0) or 0),
        }
        for order in orders
    ]

    employee_records = [
        {
            "name": employee.get("name", ""),
            "role": employee.get("role", ""),
            "task": employee.get("task", ""),
            "status": employee.get("status", "Pending"),
        }
        for employee in employees
    ]

    return {
        "summary": {
            "product_count": len(products),
            "total_stock_units": total_stock_units,
            "low_stock_product_count": len(low_stock_products),
            "low_stock_products": low_stock_products,
            "out_of_stock_products": out_of_stock_products,
            "total_order_count": len(orders),
            "open_order_count": len(open_orders),
            "completed_order_count": len(completed_orders),
            "cancelled_order_count": len(cancelled_orders),
            "total_order_value_eur": round(total_order_value, 2),
            "completed_sales_eur": round(completed_revenue, 2),
            "estimated_completed_product_cost_eur": round(
                completed_product_cost, 2
            ),
            "estimated_completed_profit_eur": round(
                estimated_completed_profit, 2
            ),
            "team_member_and_task_count": len(employees),
            "task_status_counts": task_status_counts,
        },
        "products": product_records,
        "orders": order_records,
        "team_tasks": employee_records,
    }


# -------------------- AI JARVIS --------------------
def ask_jarvis(chat_messages):
    """
    Send the user's question, recent conversation,
    and current dashboard data to Jarvis.
    """
    dashboard_context = build_dashboard_context()

    system_prompt = f"""
You are Jarvis, the friendly AI assistant for GLOW NEST,
a handcrafted candle business.

YOUR TWO MAIN RESPONSIBILITIES

1. GENERAL ASSISTANT
Answer general questions about technology, education, writing,
ideas, marketing, creativity, everyday topics, and other subjects.
You are not limited to candle-business questions.

2. BUSINESS ASSISTANT
Answer questions about GLOW NEST using the live dashboard
data included below.

IMPORTANT INSTRUCTIONS

- You HAVE access to the business data provided below.
- Do not say you cannot access employee counts, product stock,
  orders, sales, or tasks when the answer is available below.
- Use the actual data instead of guessing.
- Never invent business figures, customer records, or employees.
- If a requested detail is missing, clearly say that it is not
  recorded in the dashboard.
- Use the previous conversation to understand follow-up questions.
- Answer in the user's language. If the user writes in Hindi or
  Hinglish, reply in simple Hindi or Hinglish.
- Keep answers clear, practical, and friendly.
- Use bullet points when they make the answer easier to understand.
- Currency values are in euros (EUR).

HOW TO INTERPRET THE BUSINESS FIGURES

- Total order value includes all orders, regardless of status.
- Completed sales include only orders with status Completed or Delivered.
- Open orders include New, Preparing, Ready to ship, Pending,
  Processing, or In progress orders.
- Cancelled orders are not counted as open orders.
- A product is low-stock when its stock is 10 units or fewer.
- Estimated completed profit is completed sales minus the estimated
  product cost of completed orders.
- Estimated profit does not include rent, wages, taxes, shipping,
  marketing, or other operating expenses.
- Do not describe estimated profit as final net profit.
- Product cost calculations use the cost and quantity recorded
  for each order. If an order's product is not found, its product
  cost cannot be calculated from the current product list.

CURRENT DASHBOARD DATA:
{json.dumps(dashboard_context, ensure_ascii=False, indent=2)}

For general questions unrelated to the dashboard, answer normally.
For business questions, use the supplied dashboard data.
"""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Keep recent conversation history for follow-up questions.
    messages.extend(chat_messages[-20:])

    response = requests.post(
        f"{JARVIS_URL}/v1/chat/completions",
        json={
            "model": JARVIS_MODEL,
            "messages": messages,
            "stream": False,
        },
        timeout=90,
    )

    response.raise_for_status()
    result = response.json()

    return result["choices"][0]["message"]["content"].strip()


# -------------------- BLUE AND WHITE THEME --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

:root {
    --gold: #F2C879;
    --white: #FFFFFF;
    --muted: #D0D9E6;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: radial-gradient(
        ellipse at 85% 0%,
        #1B3150 0%,
        #101C2E 45%,
        #0B1220 100%
    ) !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #172943 0%,
        #0D1728 100%
    ) !important;
    border-right: 1px solid #344863 !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    color: #FFFFFF !important;
}

h1 {
    font-size: 3rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
}

p, label, .stCaption,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #E2EAF4 !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1B2D46, #132137) !important;
    border: 1px solid #344863 !important;
    padding: 18px 20px;
    border-radius: 18px;
    box-shadow: 0 12px 32px #00000030;
}

[data-testid="stMetricLabel"] {
    color: #E2EAF4 !important;
}

[data-testid="stMetricValue"] {
    color: #F2C879 !important;
    font-weight: 700 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(23, 41, 67, 0.85);
    border: 1px solid #344863;
    border-radius: 16px;
}

.stButton button,
.stFormSubmitButton button {
    background: #F2C879 !important;
    color: #101827 !important;
    border: 1px solid #F2C879 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: #FFDEA0 !important;
    color: #101827 !important;
}

input, textarea {
    color: #FFFFFF !important;
    background-color: #132137 !important;
    border-color: #455D7A !important;
}

[data-baseweb="select"] > div {
    color: #FFFFFF !important;
    background-color: #132137 !important;
    border-color: #455D7A !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background-color: #172943 !important;
    color: #FFFFFF !important;
}

[role="option"] {
    color: #FFFFFF !important;
}

[data-testid="stChatMessage"] {
    background: #172943 !important;
    border: 1px solid #344863 !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] {
    border-color: #455D7A !important;
}

hr {
    border-color: #344863 !important;
}

a {
    color: #F2C879 !important;
}

.business-kicker {
    color: #F2C879;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.welcome-text {
    color: #E2EAF4;
    font-size: 1.08rem;
    margin-top: -0.5rem;
}

.section-note {
    color: #D0D9E6;
    font-size: 0.92rem;
}
</style>
""", unsafe_allow_html=True)


# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 18px 0;">
        <div style="font-size:2.2rem;">🕯️</div>
        <div style="font-family:'Playfair Display',serif;
                    font-size:2rem;font-weight:700;
                    letter-spacing:1.5px;color:#FFFFFF;">
            GLOW NEST
        </div>
        <div style="color:#F2C879;font-size:0.78rem;
                    letter-spacing:2px;">CANDLE STUDIO</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    pages = ["Overview", "Products", "Orders", "Team Tasks"]

    current_index = (
        pages.index(st.session_state.page)
        if st.session_state.page in pages else 0
    )

    st.session_state.page = st.radio(
        "NAVIGATION",
        pages,
        index=current_index,
    )

    page = st.session_state.page

    st.divider()
    st.caption("Your candle business, all in one place.")

    if st.button("💾 Save business data", use_container_width=True):
        save_data()
        st.success("Business data saved.")


# -------------------- BUSINESS HEADER --------------------
header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown(
        '<div class="business-kicker">HANDCRAFTED • WARM • TIMELESS</div>',
        unsafe_allow_html=True,
    )

    st.markdown("# GLOW NEST")

    st.markdown(
        '<div class="welcome-text">Welcome to Our Business</div>',
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        f"""
        <div style="text-align:right;padding-top:14px;">
            <div style="color:#FFFFFF;font-weight:700;">
                🗓️ {date.today().strftime("%d %B %Y")}
            </div>
            <div style="color:#F2C879;font-size:0.9rem;">
                Candle Studio Dashboard
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")


# -------------------- BUSINESS CALCULATIONS --------------------
products = data["products"]
orders = data["orders"]
employees = data["employees"]

total_revenue = sum(
    float(order.get("total", 0) or 0)
    for order in orders
)

estimated_cost = sum(
    float(
        next(
            (
                product.get("cost", 0)
                for product in products
                if product.get("name") == order.get("product")
            ),
            0,
        ) or 0
    ) * int(order.get("qty", 1) or 1)
    for order in orders
)

estimated_profit = total_revenue - estimated_cost

open_orders = sum(
    1 for order in orders
    if order.get("status", "").strip().lower()
    not in ["completed", "delivered", "cancelled", "canceled"]
)

low_stock = sum(
    1 for product in products
    if int(product.get("stock", 0) or 0) <= 10
)


# -------------------- OVERVIEW PAGE --------------------
if page == "Overview":
    st.markdown("## Business Overview")

    st.markdown(
        '<div class="section-note">A quick look at how your candle studio is doing today.</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Total Sales",
        euro(total_revenue),
        f"{len(orders)} orders",
    )

    m2.metric(
        "Estimated Profit",
        euro(estimated_profit),
        "Before other expenses",
    )

    m3.metric("Active Orders", open_orders)

    m4.metric(
        "Low-Stock Products",
        low_stock,
        "Check inventory" if low_stock else "Stock looks good",
    )

    st.write("")

    left, right = st.columns([1.45, 1], gap="large")

    # -------------------- FEATURED PRODUCTS --------------------
    with left:
        st.markdown("### ✨ Featured Candles")

        st.markdown(
            '<div class="section-note">Your current product collection.</div>',
            unsafe_allow_html=True,
        )

        if products:
            card_cols = st.columns(min(2, len(products)))

            for i, product in enumerate(products):
                with card_cols[i % len(card_cols)]:
                    with st.container(border=True):
                        image_url = product.get("image", "")

                        if image_url:
                            st.image(
                                image_url,
                                use_container_width=True,
                            )

                        st.markdown(f"#### {product['name']}")

                        st.caption(
                            product.get("category", "Candle")
                        )

                        st.markdown(
                            f"**{euro(product.get('price', 0))}**"
                        )

                        stock = int(product.get("stock", 0) or 0)

                        if stock <= 10:
                            st.warning(
                                f"Only {stock} left in stock"
                            )
                        else:
                            st.caption(f"{stock} available")

        else:
            st.info(
                "Add a product from the Products page to see it here."
            )

        st.write("")

        # -------------------- RECENT ORDERS --------------------
        st.markdown("### 📦 Recent Orders")

        if orders:
            st.dataframe(
                [
                    {
                        "Customer": order.get("customer", ""),
                        "Product": order.get("product", ""),
                        "Qty": order.get("qty", 1),
                        "Status": order.get("status", ""),
                        "Total": euro(order.get("total", 0)),
                    }
                    for order in orders[-5:][::-1]
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info("No orders yet.")

    # -------------------- JARVIS AND TEAM TASKS --------------------
    with right:
        st.markdown("### 🤖 AI Jarvis")

        st.markdown(
            '<div class="section-note">Ask Jarvis about your live business data, '
            'stock, orders, team tasks, marketing, or general questions.</div>',
            unsafe_allow_html=True,
        )

        for message in st.session_state.chat_history:
            avatar = (
                "🤖"
                if message["role"] == "assistant"
                else "🙂"
            )

            with st.chat_message(
                message["role"],
                avatar=avatar,
            ):
                st.markdown(message["content"])

        prompt = st.chat_input("Ask Jarvis something...")

        if prompt:
            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            with st.chat_message("user", avatar="🙂"):
                st.markdown(prompt)

            try:
                with st.spinner("Jarvis is thinking..."):
                    answer = ask_jarvis(
                        st.session_state.chat_history
                    )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(answer)

            except requests.exceptions.ConnectionError:
                answer = (
                    "I cannot connect to Jarvis. Please make sure "
                    "your local Jarvis API is running at "
                    f"{JARVIS_URL}."
                )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.error(answer)

            except requests.exceptions.Timeout:
                st.error(
                    "Jarvis took too long to respond. "
                    "Please try again."
                )

            except (
                requests.exceptions.RequestException,
                KeyError,
                IndexError,
                TypeError,
                ValueError,
            ) as exc:
                st.error(f"Jarvis request failed: {exc}")

        if st.session_state.chat_history:
            if st.button("Clear Jarvis chat"):
                st.session_state.chat_history = []
                st.rerun()

        st.write("")

        st.markdown("### 👥 Team Tasks")

        for employee in employees[:5]:
            status = employee.get("status", "Pending")

            with st.container(border=True):
                st.markdown(
                    f"**{employee.get('task', '')}**"
                )

                st.caption(
                    f"{employee.get('name', '')} · "
                    f"{employee.get('role', '')}"
                )

                if status.lower() == "completed":
                    st.success(status)

                elif status.lower() == "in progress":
                    st.info(status)

                else:
                    st.warning(status)


# -------------------- PRODUCTS PAGE --------------------
elif page == "Products":
    st.markdown("## 🕯️ Product Collection")

    st.markdown(
        '<div class="section-note">Manage candle prices, costs, stock, and product details.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Add a new product"):
        with st.form("add_product_form", clear_on_submit=True):
            c1, c2 = st.columns(2)

            new_name = c1.text_input("Product name")

            new_category = c2.text_input(
                "Category",
                value="Signature",
            )

            c3, c4, c5 = st.columns(3)

            new_price = c3.number_input(
                "Selling price (€)",
                min_value=0.0,
                value=15.0,
                step=0.5,
            )

            new_cost = c4.number_input(
                "Cost per candle (€)",
                min_value=0.0,
                value=5.0,
                step=0.5,
            )

            new_stock = c5.number_input(
                "Stock quantity",
                min_value=0,
                value=10,
                step=1,
            )

            new_image = st.text_input(
                "Image URL (optional)"
            )

            submitted = st.form_submit_button("Add product")

            if submitted:
                if not new_name.strip():
                    st.error("Please enter a product name.")

                elif any(
                    product["name"].lower()
                    == new_name.strip().lower()
                    for product in products
                ):
                    st.error(
                        "A product with this name already exists."
                    )

                else:
                    products.append(
                        {
                            "name": new_name.strip(),
                            "category": (
                                new_category.strip() or "General"
                            ),
                            "price": float(new_price),
                            "cost": float(new_cost),
                            "stock": int(new_stock),
                            "image": new_image.strip(),
                        }
                    )

                    save_data()
                    st.success("Product added.")
                    st.rerun()

    for idx, product in enumerate(products):
        with st.container(border=True):
            p1, p2, p3, p4 = st.columns([2, 1, 1, 1])

            p1.markdown(
                f"### {product.get('name', 'Unnamed product')}"
            )

            p1.caption(product.get("category", "Candle"))

            p2.metric(
                "Price",
                euro(product.get("price", 0)),
            )

            p3.metric(
                "Cost",
                euro(product.get("cost", 0)),
            )

            p4.metric(
                "Stock",
                int(product.get("stock", 0) or 0),
            )

            with st.expander(
                f"Edit {product.get('name', 'product')}"
            ):
                with st.form(f"edit_product_{idx}"):
                    name = st.text_input(
                        "Name",
                        value=product.get("name", ""),
                    )

                    category = st.text_input(
                        "Category",
                        value=product.get("category", ""),
                    )

                    price = st.number_input(
                        "Price (€)",
                        min_value=0.0,
                        value=float(product.get("price", 0)),
                        step=0.5,
                    )

                    cost = st.number_input(
                        "Cost (€)",
                        min_value=0.0,
                        value=float(product.get("cost", 0)),
                        step=0.5,
                    )

                    stock = st.number_input(
                        "Stock",
                        min_value=0,
                        value=int(product.get("stock", 0)),
                        step=1,
                    )

                    image_url = st.text_input(
                        "Image URL",
                        value=product.get("image", ""),
                    )

                    save_product = st.form_submit_button(
                        "Save changes"
                    )

                    if save_product:
                        if not name.strip():
                            st.error(
                                "Product name cannot be empty."
                            )

                        else:
                            product.update(
                                {
                                    "name": name.strip(),
                                    "category": category.strip(),
                                    "price": float(price),
                                    "cost": float(cost),
                                    "stock": int(stock),
                                    "image": image_url.strip(),
                                }
                            )

                            save_data()
                            st.success("Product updated.")
                            st.rerun()

                if st.button(
                    f"Delete {product.get('name', 'product')}",
                    key=f"delete_product_{idx}",
                ):
                    products.pop(idx)
                    save_data()
                    st.rerun()


# -------------------- ORDERS PAGE --------------------
elif page == "Orders":
    st.markdown("## 📦 Order Management")

    st.markdown(
        '<div class="section-note">Track customer orders and update their status.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Add a new order"):
        with st.form("add_order_form", clear_on_submit=True):
            customer = st.text_input("Customer name")

            product_names = [
                product["name"]
                for product in products
            ]

            selected_product = st.selectbox(
                "Product",
                product_names
                if product_names
                else ["No products available"],
            )

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
                    "Completed",
                    "Cancelled",
                ],
            )

            submitted_order = st.form_submit_button(
                "Add order"
            )

            if submitted_order:
                if not customer.strip():
                    st.error(
                        "Please enter the customer's name."
                    )

                elif not products:
                    st.error("Add a product first.")

                else:
                    selected = next(
                        product
                        for product in products
                        if product["name"] == selected_product
                    )

                    orders.append(
                        {
                            "customer": customer.strip(),
                            "product": selected_product,
                            "qty": int(qty),
                            "status": status,
                            "created": str(date.today()),
                            "total": round(
                                float(selected.get("price", 0))
                                * int(qty),
                                2,
                            ),
                        }
                    )

                    save_data()
                    st.success("Order added.")
                    st.rerun()

    if not orders:
        st.info(
            "No orders available. Add your first order above."
        )

    for idx, order in enumerate(orders):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 2])

            c1.markdown(
                f"**{order.get('customer', 'Customer')}**"
            )

            c1.caption(
                f"Order date: {order.get('created', '')}"
            )

            c2.write(order.get("product", ""))

            c2.caption(
                f"Quantity: {order.get('qty', 1)}"
            )

            c3.markdown(
                f"**{euro(order.get('total', 0))}**"
            )

            statuses = [
                "New",
                "Preparing",
                "Ready to ship",
                "Completed",
                "Cancelled",
            ]

            old_status = order.get("status", "New")

            status_index = (
                statuses.index(old_status)
                if old_status in statuses
                else 0
            )

            new_status = c4.selectbox(
                "Status",
                statuses,
                index=status_index,
                key=f"order_status_{idx}",
            )

            if new_status != order.get("status"):
                order["status"] = new_status
                save_data()
                st.rerun()

            if st.button(
                "Delete order",
                key=f"delete_order_{idx}",
            ):
                orders.pop(idx)
                save_data()
                st.rerun()


# -------------------- TEAM TASKS PAGE --------------------
elif page == "Team Tasks":
    st.markdown("## 👥 Team Tasks")

    st.markdown(
        '<div class="section-note">Assign work and track what your team is doing.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Add a team task"):
        with st.form("add_task_form", clear_on_submit=True):
            employee_name = st.text_input(
                "Team member name"
            )

            role = st.text_input("Role")

            task = st.text_input("Task description")

            task_status = st.selectbox(
                "Status",
                ["Pending", "In progress", "Completed"],
            )

            submitted_task = st.form_submit_button(
                "Add task"
            )

            if submitted_task:
                if (
                    not employee_name.strip()
                    or not task.strip()
                ):
                    st.error(
                        "Please enter a team member name and task."
                    )

                else:
                    employees.append(
                        {
                            "name": employee_name.strip(),
                            "role": role.strip() or "Team member",
                            "task": task.strip(),
                            "status": task_status,
                        }
                    )

                    save_data()
                    st.success("Task added.")
                    st.rerun()

    for idx, employee in enumerate(employees):
        with st.container(border=True):
            t1, t2, t3 = st.columns([2, 3, 2])

            t1.markdown(
                f"**{employee.get('name', '')}**"
            )

            t1.caption(employee.get("role", ""))

            t2.write(employee.get("task", ""))

            statuses = [
                "Pending",
                "In progress",
                "Completed",
            ]

            old_status = employee.get("status", "Pending")

            status_index = (
                statuses.index(old_status)
                if old_status in statuses
                else 0
            )

            updated_status = t3.selectbox(
                "Task status",
                statuses,
                index=status_index,
                key=f"task_status_{idx}",
            )

            if updated_status != employee.get("status"):
                employee["status"] = updated_status
                save_data()
                st.rerun()

            if st.button(
                "Delete task",
                key=f"delete_task_{idx}",
            ):
                employees.pop(idx)
                save_data()
                st.rerun()


# -------------------- FOOTER --------------------
st.write("")
st.divider()

st.markdown(
    '<div style="text-align:center;color:#AEBED1;font-size:0.82rem;">'
    '🕯️ GLOW NEST · Made with care, powered by ideas.</div>',
    unsafe_allow_html=True,
)
