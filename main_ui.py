# ui/main_ui.py
import streamlit as st
import pandas as pd
import json, os
from utils.db_utils import init_db, load_menu_from_csv, get_menu, create_order, get_order, sales_summary, most_sold_items
from utils.calculator import compute_cart_totals

st.set_page_config(page_title="Restaurant Billing", page_icon="🍽️", layout="wide")
init_db()

if "cart" not in st.session_state:
    st.session_state.cart = []  # list of items in cart

st.title("🍽️ Restaurant Billing Software")

# --- Admin: load/replace menu
with st.sidebar:
    st.header("Admin")
    menu_file = st.file_uploader("Upload menu.csv", type=["csv"])
    if st.button("Load Menu") and menu_file:
        tmp = os.path.join("data","menu.csv")
        os.makedirs("data", exist_ok=True)
        with open(tmp, "wb") as f: f.write(menu_file.read())
        load_menu_from_csv(tmp)
        st.success("Menu loaded.")

    st.markdown("---")
    st.header("Reports")
    colA, colB = st.columns(2)
    period = colA.selectbox("Summary Period", ["daily","weekly","monthly"])
    if colB.button("Export Sales CSV"):
        df = pd.DataFrame(sales_summary(period))
        out = os.path.join("data","sales_report.csv")
        df.to_csv(out, index=False)
        st.success(f"Saved: {out}")
        st.dataframe(df)

# --- Sales UI
menu = get_menu()
menu_df = pd.DataFrame(menu) if menu else pd.DataFrame(columns=["item_name","category","price","gst_percent"])
st.subheader("Menu")
st.dataframe(menu_df, hide_index=True, use_container_width=True)

st.markdown("### New Order")
mode = st.radio("Mode", ["Dine-In","Takeaway"], horizontal=True)
pay = st.radio("Payment Method", ["Cash","Card","UPI"], horizontal=True)
flat_gst = st.number_input("Flat GST % (leave 0 to use per-item GST)", min_value=0.0, value=0.0, step=0.5)
discount_pct = st.number_input("Discount % (optional)", min_value=0.0, value=0.0, step=0.5)

# Add item section
st.markdown("#### Add Item to Cart")
col1, col2, col3, col4 = st.columns([4,2,2,2])
with col1:
    item_names = [f'{m["item_name"]} (₹{m["price"]})' for m in menu]
    sel = st.selectbox("Item", item_names if menu else ["-- upload menu --"])
with col2:
    qty = st.number_input("Qty", min_value=1, value=1, step=1)
with col3:
    add_btn = st.button("Add ➕")
with col4:
    clear_btn = st.button("Clear Cart 🗑️")

if clear_btn:
    st.session_state.cart = []

if add_btn and menu:
    i = item_names.index(sel)
    m = menu[i]
    st.session_state.cart.append({
        "item_id": m["id"],
        "item_name": m["item_name"],
        "qty": int(qty),
        "unit_price": float(m["price"]),
        "gst_percent": float(m["gst_percent"])
    })

st.markdown("#### Cart")
if st.session_state.cart:
    flat = None if flat_gst == 0 else flat_gst
    subtotal, gst, discount, total, enriched = compute_cart_totals(st.session_state.cart, flat, discount_pct)
    cart_df = pd.DataFrame(enriched)[["item_name","qty","unit_price","gst_percent","line_total"]]
    st.dataframe(cart_df, hide_index=True, use_container_width=True)
    st.info(f"Subtotal: ₹{subtotal} | GST: ₹{gst} | Discount: ₹{discount} | **Grand Total: ₹{total}**")

    colx, coly = st.columns(2)
    if colx.button("Place Order ✅"):
        order_id, ts = create_order(mode, pay, enriched, subtotal, gst, discount, total)
        order, items = get_order(order_id)
        bill = {"order": order, "items": items}
        os.makedirs("data", exist_ok=True)
        bill_path = os.path.join("data","sample_bills.json")
        # append bill into a json list file
        try:
            if os.path.exists(bill_path):
                data = json.load(open(bill_path,"r",encoding="utf-8"))
                if isinstance(data, list):
                    data.append(bill)
                else:
                    data = [data, bill]
            else:
                data = [bill]
        except Exception:
            data = [bill]
        with open(bill_path,"w",encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success(f"Order #{order_id} saved at {ts}. Bill appended to {bill_path}")
        st.session_state.cart = []
    if coly.button("Remove Last Item ↩︎"):
        st.session_state.cart.pop()
else:
    st.caption("Cart is empty. Add items from the menu above.")

st.markdown("---")
st.subheader("Reports (Quick View)")
tab1, tab2 = st.tabs(["Sales Summary","Most Sold Items"])
with tab1:
    df = pd.DataFrame(sales_summary("daily"))
    st.dataframe(df, use_container_width=True)
with tab2:
    st.dataframe(pd.DataFrame(most_sold_items(10)), use_container_width=True)
