# utils/calculator.py
def compute_cart_totals(cart, flat_gst_percent=None, discount_percent=0.0):
    """
    cart = list of {item_id, item_name, qty, unit_price, gst_percent}
    flat_gst_percent: if given, overrides per-item gst
    """
    subtotal = 0.0
    gst_total = 0.0
    enriched = []
    for it in cart:
        qty = int(it["qty"])
        price = float(it["unit_price"])
        gst_pct = float(flat_gst_percent if flat_gst_percent is not None else it.get("gst_percent", 5.0))
        line_sub = qty * price
        line_gst = line_sub * (gst_pct/100.0)
        line_total = line_sub + line_gst
        subtotal += line_sub
        gst_total += line_gst
        enriched.append({**it, "gst_percent": gst_pct, "line_total": round(line_total,2)})
    discount = (subtotal + gst_total) * (float(discount_percent)/100.0)
    grand_total = subtotal + gst_total - discount
    return round(subtotal,2), round(gst_total,2), round(discount,2), round(grand_total,2), enriched
