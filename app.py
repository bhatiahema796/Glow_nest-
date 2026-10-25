
import os
import json
from pathlib import Path
from datetime import date

import requests
import streamlit as st


# =====================================================
# 1. PAGE SETTINGS
# =====================================================

st.set_page_config(
    page_title="GLOW NEST | Handmade Candle Studio",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).with_name("glow_nest_data.json")

try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    API_KEY = os.getenv("OPENROUTER_API_KEY", "")

AI_MODEL = "qwen/qwen3-4b:free"
AI_URL = "https://openrouter.ai/api/v1/chat/completions"


# =====================================================
# 2. CANDLE AND TEAM PHOTOS
# =====================================================

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

HERO_PHOTO = (
    "https://images.unsplash.com/photo-1603006905003-be475563bc59"
    "?auto=format&fit=crop&w=1800&q=90"
)


# =====================================================
# 3. DEFAULT DATA
# =====================================================

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
            "description": "Delicate floral fragrance inspired by fresh roses.",
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


# =====================================================
# 4. LOAD AND SAVE DATA
# =====================================================

def load_data():
    if not DATA_FILE.exists():
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid data file")

        for key, value in DEFAULT_DATA.items():
            if key not in data:
                data[key] = json.loads(json.dumps(value))

        return data

    except (OSError, ValueError, json.JSONDecodeError):
        st.error(
            "Could not read glow_nest_data.json. "
            "Please check the file or restore your backup."
        )
        return json.loads(json.dumps(DEFAULT_DATA))


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
                "I'm Jarvis, your AI business assistant. "
                "How can I help you today?"
            ),
        }
    ]


def save_data():
    try:
        temp_file = DATA_FILE.with_suffix(".tmp")

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(
                st.session_state.business_data,
                f,
                indent=4,
                ensure_ascii=False,
            )

        temp_file.replace(DATA_FILE)
        return True

    except OSError as error:
        st.error(f"Unable to save data: {error}")
        return False


# =====================================================
# 5. HELPER FUNCTIONS
# =====================================================

def money(amount):
    return f"€{float(amount):,.2f}"


def get_product(name):
    for product in st.session_state.business_data["products"]:
        if product["name"] == name:
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


# =====================================================
# 6. PREMIUM DESIGN
# =====================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    .stApp {
        background: #fffaf5;
        color: #47352c;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #f2e4d8;
        border-right: 1px solid #e5cdbb;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #6f4332 !important;
    }

    p, label, li {
        color: #59483e;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #ead9cc;
        padding: 18px;
        border-radius: 15px;
        box-shadow: 0 3px 12px rgba(100, 65, 42, 0.04);
    }

    [data-testid="stMetricLabel"] {
        color: #8a6a56;
    }

    [data-testid="stMetricValue"] {
        color: #704531;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: #81533c;
        color: white;
        border: 1px solid #81533c;
        border-radius: 9px;
        min-height: 42px;
        font-weight: 600;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: #68402f;
        color: white;
        border-color: #68402f;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #ead9cc;
        border-radius: 14px;
        padding: 18px;
    }

    .hero {
        background: linear-gradient(
            110deg,
            rgba(48, 31, 24, 0.91),
            rgba(93, 57, 39, 0.68)
        );
        padding: 45px 35px;
        border-radius: 20px;
        color: #fff9f2;
        margin: 8px 0 25px 0;
    }

    .hero h1 {
        color: #fff9f2 !important;
        font-size: 39px;
        margin-bottom: 12px;
    }

    .hero p {
        color: #f9e9db;
        font-size: 16px;
        max-width: 650px;
        line-height: 1.7;
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #e6c4a8;
        font-size: 11px;
        font-weight: 700;
    }

    .product-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 21px;
        font-weight: 600;
        color: #6f4330;
        margin: 10px 0 3px 0;
    }

    .product-category {
        font-size: 12px;
        color: #9a7c68;
        margin-bottom: 8px;
    }

    .product-price {
        font-size: 20px;
        font-weight: 700;
        color: #754a35;
    }

    .mini-note {
        font-size: 12px;
        color: #8f7868;
    }

    .footer {
        text-align: center;
        color: #967d6b;
        padding: 20px 0 8px 0;
        font-size: 12px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# 7. SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:12px 0 5px 0;">
            <div style="font-size:12px; letter-spacing:3px; color:#91664d;">
                THE CANDLE STUDIO
            </div>
            <h1 style="font-size:32px; margin:0;">
                🕯️ GLOW NEST
            </h1>
            <div style="color:#967561; font-size:12px;">
                Crafted for beautiful moments
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    pages = [
        "Overview",
        "Products",
        "Orders",
        "Our Team",
        "Jarvis AI",
        "Profit Calculator",
    ]

    st.caption("BUSINESS MENU")

    selected = st.radio(
        "Navigate",
        pages,
        index=pages.index(st.session_state.current_page),
        label_visibility="collapsed",
    )

    st.session_state.current_page = selected

    st.divider()

    st.markdown("**A little warmth in every corner.**")
    st.caption("Handmade candles • Thoughtful details • Cozy living")


# =====================================================
# 8. OVERVIEW DASHBOARD
# =====================================================

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
                A world of handmade candles, beautiful fragrances,
                and little moments of calm. Explore our collection
                and manage the heart of our candle studio from one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## The Studio at a Glance")
    st.caption("A quick look at what's happening across our business.")

    completed_orders = [
        o for o in orders if o.get("status") == "Completed"
    ]
    pending_orders = [
        o for o in orders if o.get("status") == "Pending"
    ]
    low_stock = [
        p for p in products if int(p.get("stock", 0)) <= 5
    ]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Our Products", len(products))

    with c2:
        st.metric("Total Orders", len(orders))

    with c3:
        st.metric("Revenue", money(revenue_total()))

    with c4:
        st.metric("Our Team", len(team))

    st.markdown("---")

    # Featured candle collection
    st.markdown("## Our Signature Candle Collection")
    st.caption(
        "Beautiful scents, carefully selected for every mood and moment."
    )

    if products:
        columns = st.columns(4)

        for i, product in enumerate(products):
            with columns[i % 4]:
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
                        f'{money(product.get("price", 0))}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    stock = int(product.get("stock", 0))

                    if stock <= 5:
                        st.warning(f"Only {stock} left in stock")
                    else:
                        st.caption(f"Available: {stock} candles")

    else:
        st.info("Add candles from the Products section to show them here.")

    st.markdown("---")

    # Two business insight columns
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("## Recent Orders")

        if orders:
            for order in orders[-4:][::-1]:
                with st.container(border=True):
                    a, b = st.columns([3, 1])

                    with a:
                        st.markdown(
                            f"**Order #{order.get('id')}**"
                        )
                        st.write(
                            f"{order.get('customer', 'Customer')} · "
                            f"{order.get('product', 'Candle')}"
                        )
                        st.caption(order.get("date", ""))

                    with b:
                        st.write(
                            f"× {order.get('quantity', 1)}"
                        )
                        st.caption(order.get("status", "Pending"))
        else:
            st.info("No orders yet. Create the first order.")

    with right:
        st.markdown("## Studio Insights")

        st.metric(
            "Completed Orders",
            len(completed_orders),
        )

        st.metric(
            "Pending Orders",
            len(pending_orders),
        )

        st.metric(
            "Estimated Product Profit",
            money(completed_profit()),
        )

        if low_stock:
            st.warning(
                "Low stock: "
                + ", ".join(p["name"] for p in low_stock)
            )
        else:
            st.success("No products with critically low stock.")

        st.caption(
            "Estimated profit excludes taxes and other operating expenses."
        )

    st.markdown("---")

    st.markdown("## The GLOW NEST Promise")

    a, b, c = st.columns(3)

    with a:
        st.markdown("### 🕯️ Thoughtfully Made")
        st.write(
            "A collection designed to make everyday moments feel special."
        )

    with b:
        st.markdown("### 🌿 Fragrance & Comfort")
        st.write(
            "Warm, floral, sweet, and woody fragrance inspirations."
        )

    with c:
        st.markdown("### 🎁 Made for Gifting")
        st.write(
            "Thoughtful candle gifts for celebrations and quiet evenings."
        )


# =====================================================
# 9. PRODUCTS PAGE
# =====================================================

def show_products():
    st.title("Our Candle Collection")
    st.write(
        "Manage the products that bring the GLOW NEST experience to life."
    )

    data = st.session_state.business_data
    products = data["products"]

    tab1, tab2 = st.tabs(["Explore Candles", "Add a Candle"])

    with tab1:
        if not products:
            st.info("No candles added yet.")
        else:
            for start in range(0, len(products), 3):
                cols = st.columns(3)

                for j, product in enumerate(products[start:start + 3]):
                    with cols[j]:
                        with st.container(border=True):
                            st.image(
                                candle_photo(product["name"]),
                                use_container_width=True,
                            )

                            st.subheader(product["name"])
                            st.caption(product.get("category", "Candle"))
                            st.write(product.get("description", ""))

                            st.markdown(
                                f"### {money(product.get('price', 0))}"
                            )
                            st.write(
                                f"Production cost: "
                                f"{money(product.get('cost', 0))}"
                            )
                            st.write(
                                f"Stock: {product.get('stock', 0)}"
                            )

                            unit_profit = (
                                float(product.get("price", 0))
                                - float(product.get("cost", 0))
                            )

                            st.caption(
                                f"Estimated profit per unit: "
                                f"{money(unit_profit)}"
                            )

                            with st.expander("Edit this candle"):
                                with st.form(
                                    f"edit_product_{product['id']}"
                                ):
                                    name = st.text_input(
                                        "Name",
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
                                        "Cost (€)",
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
                                            st.error("Enter a product name.")
                                        elif any(
                                            p["id"] != product["id"]
                                            and p["name"].lower()
                                            == name.strip().lower()
                                            for p in products
                                        ):
                                            st.error(
                                                "This product name already exists."
                                            )
                                        else:
                                            product.update(
                                                {
                                                    "name": name.strip(),
                                                    "category": category.strip(),
                                                    "price": price,
                                                    "cost": cost,
                                                    "stock": stock,
                                                    "description": description.strip(),
                                                }
                                            )

                                            if save_data():
                                                st.success("Product updated.")
                                                st.rerun()

                            with st.expander("Delete this candle"):
                                st.warning(
                                    "This removes the product from the collection."
                                )

                                if st.button(
                                    "Confirm Delete",
                                    key=f"delete_{product['id']}",
                                ):
                                    data["products"] = [
                                        p for p in products
                                        if p["id"] != product["id"]
                                    ]

                                    if save_data():
                                        st.rerun()

    with tab2:
        with st.form("add_product_form", clear_on_submit=True):
            st.subheader("Create a New Candle")

            name = st.text_input("Product name")
            category = st.selectbox(
                "Fragrance category",
                [
                    "Warm & Woody",
                    "Sweet & Comforting",
                    "Floral & Elegant",
                    "Fresh & Clean",
                    "Other",
                ],
            )
            price = st.number_input(
                "Selling price (€)",
                min_value=0.0,
                value=18.0,
                step=1.0,
            )
            cost = st.number_input(
                "Production cost (€)",
                min_value=0.0,
                value=8.0,
                step=1.0,
            )
            stock = st.number_input(
                "Opening stock",
                min_value=0,
                value=10,
                step=1,
            )
            description = st.text_area("Product description")

            if st.form_submit_button("Add to Collection"):
                if not name.strip():
                    st.error("Please enter a product name.")
                elif any(
                    p["name"].lower() == name.strip().lower()
                    for p in products
                ):
                    st.error("This candle is already in the collection.")
                else:
                    new_id = max(
                        [int(p.get("id", 0)) for p in products],
                        default=0,
                    ) + 1

                    products.append(
                        {
                            "id": new_id,
                            "name": name.strip(),
                            "category": category,
                            "price": price,
                            "cost": cost,
                            "stock": stock,
                            "description": description.strip(),
                        }
                    )

                    if save_data():
                        st.success("Your candle has been added!")
                        st.rerun()


# =====================================================
# 10. ORDERS PAGE
# =====================================================

def show_orders():
    st.title("Order Management")
    st.write("Keep track of customer orders and their progress.")

    data = st.session_state.business_data
    orders = data["orders"]
    products = data["products"]

    tab1, tab2 = st.tabs(["All Orders", "Create Order"])

    with tab1:
        if not orders:
            st.info("No orders yet.")
        else:
            for order in orders[::-1]:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 2])

                    with c1:
                        st.subheader(f"Order #{order.get('id')}")
                        st.write(order.get("customer", "Customer"))
                        st.caption(order.get("date", ""))

                    with c2:
                        st.write(f"**{order.get('product', '')}**")
                        st.write(
                            f"Quantity: {order.get('quantity', 1)}"
                        )

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
                            key=f"order_status_{order.get('id')}",
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
            st.warning("Add a candle first.")
        else:
            with st.form("new_order_form", clear_on_submit=True):
                customer = st.text_input("Customer name")
                product_name = st.selectbox(
                    "Choose a candle",
                    [p["name"] for p in products],
                )
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    step=1,
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

                            orders.append(
                                {
                                    "id": new_id,
                                    "customer": customer.strip(),
                                    "product": product_name,
                                    "quantity": int(quantity),
                                    "status": "Pending",
                                    "date": str(date.today()),
                                }
                            )

                            if product:
                                product["stock"] -= int(quantity)

                            if save_data():
                                st.success(f"Order #{new_id} created.")
                                st.rerun()


# =====================================================
# 11. TEAM PAGE
# =====================================================

def show_team():
    st.title("Meet Our Team")
    st.write(
        "The people, creativity, and care behind our candle studio."
    )

    data = st.session_state.business_data
    team = data["team"]

    tab1, tab2 = st.tabs(["Our People", "Add Team Member"])

    with tab1:
        if not team:
            st.info("Add your team members to get started.")
        else:
            columns = st.columns(3)

            for i, member in enumerate(team):
                with columns[i % 3]:
                    with st.container(border=True):
                        photo = member.get("photo") or TEAM_PHOTOS[
                            i % len(TEAM_PHOTOS)
                        ]

                        st.image(
                            photo,
                            use_container_width=True,
                        )
                        st.subheader(member.get("name", "Team Member"))
                        st.caption(member.get("role", "Team Member"))
                        st.write(member.get("task", ""))
                        st.caption(
                            f"Status: {member.get('status', 'Active')}"
                        )

                        with st.expander("Edit team member"):
                            with st.form(f"edit_team_{i}"):
                                name = st.text_input(
                                    "Name",
                                    value=member.get("name", ""),
                                )
                                role = st.text_input(
                                    "Role",
                                    value=member.get("role", ""),
                                )
                                task = st.text_area(
                                    "Responsibilities",
                                    value=member.get("task", ""),
                                )
                                statuses = [
                                    "Active",
                                    "On Leave",
                                    "Inactive",
                                ]
                                current_status = member.get("status", "Active")

                                status = st.selectbox(
                                    "Status",
                                    statuses,
                                    index=(
                                        statuses.index(current_status)
                                        if current_status in statuses
                                        else 0
                                    ),
                                )

                                if st.form_submit_button("Save Changes"):
                                    if not name.strip():
                                        st.error("Name is required.")
                                    else:
                                        member.update(
                                            {
                                                "name": name.strip(),
                                                "role": role.strip(),
                                                "task": task.strip(),
                                                "status": status,
                                            }
                                        )

                                        if save_data():
                                            st.success("Team updated.")
                                            st.rerun()

    with tab2:
        with st.form("add_team_form", clear_on_submit=True):
            name = st.text_input("Full name")
            role = st.text_input("Job role")
            task = st.text_area("Responsibilities")
            status = st.selectbox(
                "Status",
                ["Active", "On Leave", "Inactive"],
            )

            if st.form_submit_button("Add Team Member"):
                if not name.strip():
                    st.error("Enter the team member's name.")
                else:
                    team.append(
                        {
                            "name": name.strip(),
                            "role": role.strip(),
                            "task": task.strip(),
                            "status": status,
                        }
                    )

                    if save_data():
                        st.success("Team member added.")
                        st.rerun()


# =====================================================
# 12. JARVIS AI PAGE
# =====================================================

def ask_jarvis(messages):
    if not API_KEY:
        return (
            "My AI key is not configured. Please add "
            "OPENROUTER_API_KEY in Streamlit Cloud → Settings → Secrets."
        )

    data = st.session_state.business_data

    products = [
        {
            "name": p.get("name"),
            "price": p.get("price"),
            "cost": p.get("cost"),
            "stock": p.get("stock"),
        }
        for p in data["products"]
    ]

    orders = [
        {
            "id": o.get("id"),
            "product": o.get("product"),
            "quantity": o.get("quantity"),
            "status": o.get("status"),
        }
        for o in data["orders"][-15:]
    ]

    system_message = f"""
You are Jarvis, the helpful AI assistant for GLOW NEST,
a handmade candle business.

Use friendly, simple, professional language.
Help with candle ideas, customer service, stock, orders,
pricing, profit calculations, and marketing.

Do not claim that you changed app data. The user must do that
through the app's controls.

Current products:
{json.dumps(products, ensure_ascii=False)}

Recent orders:
{json.dumps(orders, ensure_ascii=False)}

Completed-order revenue: {revenue_total():.2f} EUR
Estimated product profit on completed orders:
{completed_profit():.2f} EUR
"""

    try:
        response = requests.post(
            AI_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
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
                "Check your OpenRouter key, account limits, and model."
            )

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except requests.RequestException:
        return "I could not connect to the AI service. Please try again."
    except (KeyError, IndexError, ValueError):
        return "I received an unexpected response. Please try again."


def show_jarvis():
    st.title("Jarvis AI")
    st.write("Your intelligent companion for the GLOW NEST studio.")

    left, right = st.columns([1, 2])

    with left:
        st.image(JARVIS_PHOTO, use_container_width=True)
        st.subheader("Meet Jarvis")
        st.write(
            "Ask questions about products, business performance, "
            "marketing strategies, or ideas for growing our candle studio."
        )

        st.markdown("**Try asking:**")
        st.caption("• How can we increase candle sales?")
        st.caption("• Suggest a social media campaign.")
        st.caption("• Which candles have low stock?")

    with right:
        for message in st.session_state.jarvis_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Message Jarvis...")

        if prompt:
            st.session_state.jarvis_messages.append(
                {"role": "user", "content": prompt}
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Jarvis is thinking..."):
                    answer = ask_jarvis(
                        st.session_state.jarvis_messages
                    )
                st.markdown(answer)

            st.session_state.jarvis_messages.append(
                {"role": "assistant", "content": answer}
            )

        if st.button("Clear Conversation"):
            st.session_state.jarvis_messages = [
                {
                    "role": "assistant",
                    "content": "Hello! Welcome to GLOW NEST. How can I help?",
                }
            ]
            st.rerun()


# =====================================================
# 13. PROFIT CALCULATOR
# =====================================================

def show_profit_calculator():
    st.title("Profit Calculator")
    st.write("Understand how much our candles can earn.")

    products = st.session_state.business_data["products"]

    if products:
        product_names = [p["name"] for p in products]
        chosen = st.selectbox("Choose a candle", product_names)
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
            "Candles sold",
            min_value=1,
            value=10,
            step=1,
        )

        extra_expenses = st.number_input(
            "Other expenses (€)",
            min_value=0.0,
            value=0.0,
            step=1.0,
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
            st.success("Your sales cover the costs in this calculation.")

        st.caption(
            "This estimate excludes any expenses not entered above, "
            "including taxes or fees."
        )


# =====================================================
# 14. PAGE ROUTER
# =====================================================

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


# =====================================================
# 15. FOOTER
# =====================================================

st.markdown(
    """
    <div class="footer">
        🕯️ <b>GLOW NEST</b><br>
        <span>Welcome to our world of warmth, fragrance, and handmade candles.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
