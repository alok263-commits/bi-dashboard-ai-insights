import streamlit as st
import sys
import os
import pandas as pd
import altair as alt
from datetime import datetime

# =================================================================
# CATEGORY / SEGMENT COLOR MAPS
# One consistent palette per dimension, reused across EVERY chart
# in the app (fix for "Category Colors Are Inconsistent").
# =================================================================
CATEGORY_COLORS = {
    "Furniture": "#1f77b4",       # blue
    "Office Supplies": "#d62728",  # red
    "Technology": "#2ca02c",       # green
}
CATEGORY_COLOR_SCALE = alt.Scale(
    domain=list(CATEGORY_COLORS.keys()),
    range=list(CATEGORY_COLORS.values()),
)

SEGMENT_COLORS = {
    "Consumer": "#ff7f0e",      # orange
    "Corporate": "#9467bd",     # purple
    "Home Office": "#17becf",   # teal
}
SEGMENT_COLOR_SCALE = alt.Scale(
    domain=list(SEGMENT_COLORS.keys()),
    range=list(SEGMENT_COLORS.values()),
)

NEUTRAL_BAR_COLOR = "#6ea8fe"

# Trend colors reserved ONLY for meaning (positive / negative / neutral),
# never for decoration (fix for "colors used as decoration").
TREND_UP = "#2ecc71"
TREND_DOWN = "#e74c3c"
TREND_NEUTRAL = "#9aa0b4"

DATASET_NAME = "superstore_clean.csv"

# =================================================================
# PATH SETUP
# =================================================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
from ai_module import generate_kpi_summary

# =================================================================
# PAGE CONFIG
# =================================================================
st.set_page_config(
    page_title="Executive AI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =================================================================
# CUSTOM STYLING
# One neutral card style everywhere. Primary cards are visually
# bigger/bolder than secondary cards, giving true hierarchy instead
# of 9 equally-weighted widgets. Colors only ever signal trend.
# Card height is reduced (~25%) vs the original design.
# =================================================================
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(160deg, #0b0e14 0%, #12151f 55%, #0e1117 100%);
        }
        .block-container {
            padding-top: 1.2rem;
        }

        /* --- Primary KPI cards (the 4 that matter) --- */
        .kpi-primary {
            background: rgba(255, 255, 255, 0.045);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.30);
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
            height: 100%;
        }
        .kpi-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            border-color: rgba(255,255,255,0.18);
        }
        .kpi-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            color: #9aa0b4;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #f5f6fa;
            line-height: 1.1;
            margin-bottom: 4px;
        }
        .kpi-delta {
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* --- Secondary KPI cards (Customer Analytics tab) --- */
        .kpi-secondary {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 10px 13px;
            height: 100%;
        }
        .kpi-secondary .kpi-label { font-size: 0.68rem; margin-bottom: 3px; }
        .kpi-secondary .kpi-value { font-size: 1.25rem; margin-bottom: 2px; }
        .kpi-secondary .kpi-delta { font-size: 0.74rem; }

        /* --- Header --- */
        .app-brand {
            font-size: 0.75rem;
            letter-spacing: 2.5px;
            font-weight: 700;
            text-transform: uppercase;
            color: #6ea8fe;
            margin-bottom: 2px;
        }
        .app-title {
            font-size: 2.0rem;
            font-weight: 800;
            color: #f5f6fa;
            line-height: 1.15;
            margin-bottom: 2px;
        }
        .app-subtitle {
            font-size: 0.95rem;
            font-weight: 500;
            color: #9aa0b4;
        }
        .app-meta {
            text-align: right;
            color: #757c92;
            font-size: 0.8rem;
            line-height: 1.55;
        }

        /* --- Executive summary / insight cards --- */
        .insight-card {
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.08);
            border-left: 3px solid #6ea8fe;
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 0.92rem;
            color: #d7dae2;
            line-height: 1.7;
        }

        /* Tighten the gap between the last chart/section and the tabs */
        .stTabs { margin-top: -0.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =================================================================
# DATA LOADING
# =================================================================
@st.cache_data(show_spinner="Loading dataset...")
def load_data(path: str = DATASET_NAME) -> pd.DataFrame:
    data = pd.read_csv(path)
    if "Order Date" in data.columns:
        data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error("🚨 Dataset not found! Make sure 'superstore_clean.csv' is in your main folder.")
    st.stop()
except Exception as e:
    st.error(f"🚨 Couldn't load the dataset: {e}")
    st.stop()

# =================================================================
# SIDEBAR — filters ONLY. "Records in view" moved out of the
# sidebar entirely (now lives once, in the Raw Data tab / footer).
# =================================================================
st.sidebar.header("🔎 Dashboard Filters")

for key in ("filter_region", "filter_category", "filter_segment"):
    if key not in st.session_state:
        st.session_state[key] = "All"


def filter_dropdown(label: str, column: str, key: str):
    if column not in df.columns:
        return "All"
    options = ["All"] + sorted(df[column].dropna().unique().tolist())
    return st.sidebar.selectbox(label, options, key=key)


selected_region = filter_dropdown("Region", "Region", "filter_region")
selected_category = filter_dropdown("Category", "Category", "filter_category")
selected_segment = filter_dropdown("Segment", "Segment", "filter_segment")


def reset_filters():
    st.session_state["filter_region"] = "All"
    st.session_state["filter_category"] = "All"
    st.session_state["filter_segment"] = "All"


st.sidebar.button("↺ Reset Filters", use_container_width=True, on_click=reset_filters)

filtered_df = df.copy()
if "Region" in df.columns and selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if "Category" in df.columns and selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
if "Segment" in df.columns and selected_segment != "All":
    filtered_df = filtered_df[filtered_df["Segment"] == selected_segment]

coverage = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0

# =================================================================
# HEADER — compact, includes active filters + last-updated + dataset
# name so there's no dead whitespace between title and content.
# =================================================================
active_filters = ", ".join(
    f"{lbl}: {val}"
    for lbl, val in [("Region", selected_region), ("Category", selected_category), ("Segment", selected_segment)]
    if val != "All"
) or "All Segments"

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown(
        f"""
        <div class="app-brand">📊 SalesIQ</div>
        <div class="app-title">Executive Sales Dashboard</div>
        <div class="app-subtitle">{active_filters}</div>
        """,
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown(
        f"""
        <div class="app-meta">
            📅 {datetime.now().strftime('%d %b %Y, %I:%M %p')}<br>
            🔄 Last updated: {datetime.now().strftime('%I:%M %p')}<br>
            🗂️ Dataset: {DATASET_NAME}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =================================================================
# KPI CALCULATIONS
# =================================================================
total_revenue = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

order_col = "Order ID" if "Order ID" in filtered_df.columns else None
total_orders = filtered_df[order_col].nunique() if order_col else len(filtered_df)
avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0

customer_col = "Customer ID" if "Customer ID" in filtered_df.columns else (
    "Customer Name" if "Customer Name" in filtered_df.columns else None
)
total_customers = filtered_df[customer_col].nunique() if customer_col else None

quantity_col = "Quantity" if "Quantity" in filtered_df.columns else None
total_quantity = filtered_df[quantity_col].sum() if quantity_col else None

discount_col = "Discount" if "Discount" in filtered_df.columns else None
avg_discount = (filtered_df[discount_col].mean() * 100) if discount_col else None

overall_revenue = df["Sales"].sum()
overall_profit = df["Profit"].sum()
overall_margin = (overall_profit / overall_revenue * 100) if overall_revenue > 0 else 0
overall_orders = df[order_col].nunique() if order_col else len(df)
overall_aov = (overall_revenue / overall_orders) if overall_orders > 0 else 0
overall_customers = df[customer_col].nunique() if customer_col else None
overall_quantity = df[quantity_col].sum() if quantity_col else None
overall_avg_discount = (df[discount_col].mean() * 100) if discount_col else None


def monthly_agg(data: pd.DataFrame, col, agg: str):
    """Aggregates `col` for the most recent complete month vs the SAME month
    one year earlier (Year-over-Year). This dataset is highly seasonal
    (big holiday-season spikes), so month-over-month comparisons mostly
    just measure seasonality rather than real performance change. YoY
    strips that out. Returns (current, same_month_last_year) or None if
    there isn't a full year of history to compare against."""
    if "Order Date" not in data.columns:
        return None
    d = data.dropna(subset=["Order Date"])
    if d.empty:
        return None
    d = d.copy()
    d["_month"] = d["Order Date"].dt.to_period("M")
    months = sorted(d["_month"].unique())
    if not months:
        return None

    latest_month = months[-1]
    prior_year_month = latest_month - 12
    if prior_year_month not in months:
        return None

    def _calc(subset: pd.DataFrame):
        if agg == "count":
            return len(subset)
        if col is None:
            return None
        if agg == "sum":
            return subset[col].sum()
        if agg == "mean":
            return subset[col].mean()
        if agg == "nunique":
            return subset[col].nunique()
        return None

    cur = _calc(d[d["_month"] == latest_month])
    prev = _calc(d[d["_month"] == prior_year_month])
    return cur, prev


def yoy_pct(data, col, agg):
    """Despite the name (kept for minimal diff elsewhere), this now returns
    Year-over-Year % growth: latest month vs the same month last year."""
    result = monthly_agg(data, col, agg)
    if not result or not result[1]:
        return None
    cur, prev = result
    return (cur - prev) / prev * 100


# =================================================================
# KPI CARD RENDERER — single neutral style. Color is used ONLY to
# signal trend direction (green/red/gray), never as decoration.
# =================================================================
def kpi_card(label: str, value: str, delta_text: str, delta_direction: str, size: str = "primary") -> str:
    arrow = {"up": "▲", "down": "▼", "neutral": "•"}[delta_direction]
    color = {"up": TREND_UP, "down": TREND_DOWN, "neutral": TREND_NEUTRAL}[delta_direction]
    css_class = "kpi-primary" if size == "primary" else "kpi-secondary"
    return f"""
    <div class="{css_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta" style="color:{color};">{arrow} {delta_text}</div>
    </div>
    """


def delta_from_mom_or_fallback(growth_pct, fallback_text, fallback_direction, unit="%"):
    if growth_pct is not None:
        direction = "up" if growth_pct >= 0 else "down"
        return f"{growth_pct:+.0f}{unit} vs Last Year", direction
    return fallback_text, fallback_direction


# --- Revenue ---
revenue_growth = yoy_pct(filtered_df, "Sales", "sum")
revenue_share = (total_revenue / overall_revenue * 100) if overall_revenue > 0 else 0
revenue_delta_text, revenue_dir = delta_from_mom_or_fallback(
    revenue_growth, f"{revenue_share:.0f}% of total revenue", "neutral"
)

# --- Profit ---
profit_growth = yoy_pct(filtered_df, "Profit", "sum")
margin_delta_pp = profit_margin - overall_margin
profit_fallback_dir = "up" if total_profit >= 0 else "down"
profit_delta_text, profit_dir = delta_from_mom_or_fallback(
    profit_growth, f"{margin_delta_pp:+.1f}pp margin vs avg", profit_fallback_dir
)

# --- Margin ---
sales_yoy = monthly_agg(filtered_df, "Sales", "sum")
profit_yoy = monthly_agg(filtered_df, "Profit", "sum")
if sales_yoy and profit_yoy and sales_yoy[0] and sales_yoy[1]:
    cur_margin = (profit_yoy[0] / sales_yoy[0] * 100) if sales_yoy[0] else 0
    prev_margin = (profit_yoy[1] / sales_yoy[1] * 100) if sales_yoy[1] else 0
    margin_growth_pp = cur_margin - prev_margin
    margin_delta_text = f"{margin_growth_pp:+.1f}pp vs Last Year"
    margin_dir = "up" if margin_growth_pp >= 0 else "down"
else:
    margin_delta_text = f"{margin_delta_pp:+.1f}pp vs {overall_margin:.1f}% avg"
    margin_dir = "up" if margin_delta_pp >= 0 else "down"

# --- Orders ---
order_growth = yoy_pct(filtered_df, order_col, "nunique") if order_col else yoy_pct(filtered_df, None, "count")
order_share = (total_orders / overall_orders * 100) if overall_orders > 0 else 0
order_delta_text, order_dir = delta_from_mom_or_fallback(
    order_growth, f"{order_share:.0f}% of total orders", "neutral"
)

# --- Secondary: Avg Order Value ---
orders_yoy = monthly_agg(filtered_df, order_col, "nunique") if order_col else monthly_agg(filtered_df, None, "count")
if sales_yoy and orders_yoy and orders_yoy[0] and orders_yoy[1]:
    cur_aov = sales_yoy[0] / orders_yoy[0] if orders_yoy[0] else 0
    prev_aov = sales_yoy[1] / orders_yoy[1] if orders_yoy[1] else 0
    aov_growth = ((cur_aov - prev_aov) / prev_aov * 100) if prev_aov else None
else:
    aov_growth = None
aov_delta_pct = ((avg_order_value - overall_aov) / overall_aov * 100) if overall_aov > 0 else 0
aov_delta_text, aov_dir = delta_from_mom_or_fallback(
    aov_growth, f"{aov_delta_pct:+.0f}% vs ${overall_aov:,.0f} avg", "up" if aov_delta_pct >= 0 else "down"
)

# --- Secondary: Customers ---
if customer_col:
    customer_growth = yoy_pct(filtered_df, customer_col, "nunique")
    customer_share = (total_customers / overall_customers * 100) if overall_customers else 0
    customer_delta_text, customer_dir = delta_from_mom_or_fallback(
        customer_growth, f"{customer_share:.0f}% of total customers", "neutral"
    )
    customer_value = f"{total_customers:,}"
else:
    customer_delta_text, customer_dir = "No customer column found", "neutral"
    customer_value = "—"

# --- Secondary: Quantity ---
if quantity_col:
    quantity_growth = yoy_pct(filtered_df, quantity_col, "sum")
    quantity_share = (total_quantity / overall_quantity * 100) if overall_quantity else 0
    quantity_delta_text, quantity_dir = delta_from_mom_or_fallback(
        quantity_growth, f"{quantity_share:.0f}% of total units", "neutral"
    )
    quantity_value = f"{total_quantity:,.0f}"
else:
    quantity_delta_text, quantity_dir = "No quantity column found", "neutral"
    quantity_value = "—"

# --- Secondary: Discount (rising discount = bad, so color is flipped) ---
if discount_col:
    disc_yoy = monthly_agg(filtered_df, discount_col, "mean")
    if disc_yoy and disc_yoy[1] is not None:
        disc_growth_pp = (disc_yoy[0] - disc_yoy[1]) * 100
        discount_delta_text = f"{disc_growth_pp:+.1f}pp vs Last Year"
        discount_dir = "down" if disc_growth_pp >= 0 else "up"
    else:
        disc_vs_avg_pp = avg_discount - overall_avg_discount if overall_avg_discount is not None else 0
        discount_delta_text = f"{disc_vs_avg_pp:+.1f}pp vs {overall_avg_discount:.1f}% avg"
        discount_dir = "down" if disc_vs_avg_pp >= 0 else "up"
    discount_value = f"{avg_discount:.1f}%"
else:
    discount_delta_text, discount_dir = "No discount column found", "neutral"
    discount_value = "—"

records_delta_text = f"{coverage:.0f}% of total records"

# =================================================================
# PRIMARY KPI ROW — exactly 4 cards: Revenue, Profit, Margin, Orders.
# This is the entire "first 5 seconds" view (fix for KPI overload
# and "too much above the fold").
# =================================================================
primary_cols = st.columns(4)
with primary_cols[0]:
    st.markdown(kpi_card("Total Revenue", f"${total_revenue:,.0f}", revenue_delta_text, revenue_dir), unsafe_allow_html=True)
with primary_cols[1]:
    st.markdown(kpi_card("Total Profit", f"${total_profit:,.0f}", profit_delta_text, profit_dir), unsafe_allow_html=True)
with primary_cols[2]:
    st.markdown(kpi_card("Profit Margin", f"{profit_margin:.1f}%", margin_delta_text, margin_dir), unsafe_allow_html=True)
with primary_cols[3]:
    st.markdown(kpi_card("Orders", f"{total_orders:,}", order_delta_text, order_dir), unsafe_allow_html=True)

st.write("")

# =================================================================
# EXECUTIVE SUMMARY — always-visible, rule-based takeaways (no API
# call needed) that bridge "here are numbers" -> "here's what it
# means". Fixes "No Executive Summary".
# =================================================================
def generate_quick_insights(data: pd.DataFrame) -> list:
    insights = []

    if "Category" in data.columns:
        cat_profit = data.groupby("Category")["Profit"].sum().sort_values(ascending=False)
        if not cat_profit.empty:
            top_cat = cat_profit.index[0]
            insights.append(f"**{top_cat}** is generating the most profit in the current view.")
            losers = cat_profit[cat_profit < 0]
            if not losers.empty:
                worst_cat = losers.index[0]
                insights.append(f"**{worst_cat}** is currently loss-making and may need attention.")

    if "Region" in data.columns:
        region_growth = {}
        for region, rdata in data.groupby("Region"):
            g = yoy_pct(rdata, "Sales", "sum")
            if g is not None:
                region_growth[region] = g
        if region_growth:
            best_region = max(region_growth, key=region_growth.get)
            insights.append(f"**{best_region}** region shows the strongest year-over-year sales growth ({region_growth[best_region]:+.0f}%).")
        else:
            region_rev = data.groupby("Region")["Sales"].sum().sort_values(ascending=False)
            if not region_rev.empty:
                insights.append(f"**{region_rev.index[0]}** is the top-performing region by revenue.")

    if aov_growth is not None:
        direction = "increased" if aov_growth >= 0 else "decreased"
        insights.append(f"Average Order Value has **{direction} {abs(aov_growth):.0f}%** vs last year.")

    if not insights:
        insights.append("Not enough data in the current filter selection to generate insights.")

    return insights[:4]


summary_left, summary_right = st.columns([2, 1])

def md_bold_to_html(text: str) -> str:
    """Converts **bold** markdown syntax to <strong> tags. Needed because
    this content is rendered inside a raw HTML div, which bypasses
    Streamlit's markdown parser entirely."""
    parts = text.split("**")
    # Every odd-indexed part was wrapped in ** ** and should be bolded
    return "".join(f"<strong>{p}</strong>" if i % 2 == 1 else p for i, p in enumerate(parts))


with summary_left:
    st.markdown("###### 📌 Executive Summary")
    bullets_html = "<br>".join(f"• {md_bold_to_html(b)}" for b in generate_quick_insights(filtered_df))
    st.markdown(f'<div class="insight-card">{bullets_html}</div>', unsafe_allow_html=True)

with summary_right:
    st.markdown("###### 🤖 AI-Generated Report")
    gen_col, clear_col = st.columns([1, 1])
    generate_clicked = gen_col.button("✨ Generate", use_container_width=True)
    clear_clicked = clear_col.button("🗑️ Clear", use_container_width=True)

    if clear_clicked:
        st.session_state.pop("ai_summary", None)
        st.session_state.pop("ai_summary_context", None)

    if generate_clicked:
        live_data_string = (
            f"Region: {selected_region}, Category: {selected_category}, Segment: {selected_segment}, "
            f"Total Revenue: ${total_revenue:,.2f}, Total Profit: ${total_profit:,.2f}, "
            f"Profit Margin: {profit_margin:.1f}%, Avg Order Value: ${avg_order_value:,.2f}"
        )
        with st.spinner("Analyzing live data..."):
            try:
                ai_result = generate_kpi_summary(live_data_string)
                st.session_state["ai_summary"] = ai_result
                st.session_state["ai_summary_context"] = live_data_string
            except Exception as e:
                st.session_state.pop("ai_summary", None)
                st.error(f"⚠️ AI request failed: {e}")

    if st.session_state.get("ai_summary"):
        with st.expander("View Full AI Report", expanded=True):
            st.caption(f"Data analyzed: {st.session_state['ai_summary_context']}")
            st.write(st.session_state["ai_summary"])
    elif not generate_clicked:
        st.caption("Click Generate for a Gemini-written narrative summary.")

st.write("")

# =================================================================
# MONTHLY TREND — full width, placed right after the summary since
# "how is the business changing over time" is the next natural
# question an executive asks (fix for "Missing Monthly Trend" +
# chart storytelling order).
# =================================================================
if "Order Date" in filtered_df.columns and filtered_df["Order Date"].notna().any():
    trend_left, trend_right = st.columns(2)

    with trend_left:
        st.markdown("###### 📈 Monthly Revenue Trend")
        monthly_sales_df = (
            filtered_df.dropna(subset=["Order Date"])
            .set_index("Order Date")
            .resample("ME")["Sales"]
            .sum()
            .reset_index()
        )
        chart_trend = (
            alt.Chart(monthly_sales_df)
            .mark_line(point=True, color=NEUTRAL_BAR_COLOR)
            .encode(
                x=alt.X("Order Date:T", title=""),
                y=alt.Y("Sales:Q", title="Monthly Sales"),
                tooltip=[alt.Tooltip("Order Date:T", format="%b %Y"), alt.Tooltip("Sales:Q", format="$,.0f")],
            )
            .properties(height=260)
        )
        st.altair_chart(chart_trend, use_container_width=True)

    with trend_right:
        # Same-month-across-years overlay. This is the actionable view for a
        # seasonal/spiky dataset: it separates "the usual holiday spike" from
        # "actual growth or decline" by lining every year up on the same
        # Jan-Dec axis, rather than comparing adjacent months.
        st.markdown("###### 📆 Year-over-Year Seasonal Comparison")
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        yoy_df = filtered_df.dropna(subset=["Order Date"]).copy()
        yoy_df["Year"] = yoy_df["Order Date"].dt.year.astype(str)
        yoy_df["Month"] = yoy_df["Order Date"].dt.strftime("%b")
        yoy_seasonal = yoy_df.groupby(["Year", "Month"])["Sales"].sum().reset_index()

        chart_yoy = (
            alt.Chart(yoy_seasonal)
            .mark_line(point=True)
            .encode(
                x=alt.X("Month:N", sort=month_order, title=""),
                y=alt.Y("Sales:Q", title="Monthly Sales"),
                color=alt.Color("Year:N", legend=alt.Legend(title="Year")),
                tooltip=["Year", "Month", alt.Tooltip("Sales:Q", format="$,.0f")],
            )
            .properties(height=260)
        )
        st.altair_chart(chart_yoy, use_container_width=True)

# =================================================================
# TABS — each tab answers the next business question in sequence:
# Comparisons -> Customer Analytics -> Raw Data.
# =================================================================
tab_compare, tab_customer, tab_data = st.tabs(
    ["📊 Business Comparisons", "👥 Customer Analytics", "🗂️ Raw Data"]
)


def build_breakdown_chart(data: pd.DataFrame, value_col: str, value_format="$,.0f"):
    """Picks the next dimension to break down by based on which filters are
    still 'All', so drilling into one Category reveals Segment, and so on.
    Each level keeps its own consistent, meaningful palette. Bars now carry
    value labels (fix for 'Charts Don't Show Values')."""
    if "Category" in data.columns and selected_category == "All":
        dim, scale = "Category", CATEGORY_COLOR_SCALE
    elif "Segment" in data.columns and selected_segment == "All":
        dim, scale = "Segment", SEGMENT_COLOR_SCALE
    elif "Sub-Category" in data.columns:
        dim, scale = "Sub-Category", None
    else:
        return None, None

    grouped = data.groupby(dim)[value_col].sum().reset_index().sort_values(value_col, ascending=False)
    color_enc = alt.Color(f"{dim}:N", scale=scale, legend=None) if scale is not None else alt.Color(f"{dim}:N", legend=None)

    base = alt.Chart(grouped).encode(
        x=alt.X(f"{dim}:N", sort="-y", title=""),
        y=alt.Y(f"{value_col}:Q", title=f"Total {value_col}"),
    )
    bars = base.mark_bar().encode(color=color_enc, tooltip=[dim, alt.Tooltip(f"{value_col}:Q", format=value_format)])
    labels = base.mark_text(dy=-8, color="#d7dae2", fontSize=11).encode(
        text=alt.Text(f"{value_col}:Q", format=value_format)
    )
    return (bars + labels).properties(height=300), dim


with tab_compare:
    left, right = st.columns(2)
    with left:
        chart_sales, dim_used = build_breakdown_chart(filtered_df, "Sales")
        if chart_sales is not None:
            st.write(f"**Total Sales by {dim_used}**")
            st.altair_chart(chart_sales, use_container_width=True)
        else:
            st.info("No further dimension available to break Sales down by.")
    with right:
        chart_profit, dim_used = build_breakdown_chart(filtered_df, "Profit")
        if chart_profit is not None:
            st.write(f"**Total Profit by {dim_used}**")
            st.altair_chart(chart_profit, use_container_width=True)
        else:
            st.info("No further dimension available to break Profit down by.")

    if "Sub-Category" in filtered_df.columns:
        st.write("**Top 10 Sub-Categories by Profit** (colored by parent Category)")
        if "Category" in filtered_df.columns:
            subcat_df = (
                filtered_df.groupby(["Sub-Category", "Category"])["Profit"]
                .sum().reset_index().sort_values("Profit", ascending=False).head(10)
            )
            base = alt.Chart(subcat_df).encode(
                x=alt.X("Profit:Q", title="Total Profit"),
                y=alt.Y("Sub-Category:N", sort="-x", title=""),
            )
            bars = base.mark_bar().encode(
                color=alt.Color("Category:N", scale=CATEGORY_COLOR_SCALE, legend=alt.Legend(title="Category")),
                tooltip=["Sub-Category", "Category", alt.Tooltip("Profit:Q", format="$,.0f")],
            )
            labels = base.mark_text(dx=25, color="#d7dae2", fontSize=11).encode(
                text=alt.Text("Profit:Q", format="$,.0f")
            )
            chart_subcat = (bars + labels).properties(height=320)
        else:
            subcat_df = (
                filtered_df.groupby("Sub-Category")["Profit"]
                .sum().reset_index().sort_values("Profit", ascending=False).head(10)
            )
            base = alt.Chart(subcat_df).encode(
                x=alt.X("Profit:Q", title="Total Profit"),
                y=alt.Y("Sub-Category:N", sort="-x", title=""),
            )
            bars = base.mark_bar(color=NEUTRAL_BAR_COLOR).encode(
                tooltip=["Sub-Category", alt.Tooltip("Profit:Q", format="$,.0f")]
            )
            labels = base.mark_text(dx=25, color="#d7dae2", fontSize=11).encode(
                text=alt.Text("Profit:Q", format="$,.0f")
            )
            chart_subcat = (bars + labels).properties(height=320)
        st.altair_chart(chart_subcat, use_container_width=True)

with tab_customer:
    st.caption("Secondary metrics for this view — supporting detail, not headline KPIs.")
    sec_cols = st.columns(3)
    with sec_cols[0]:
        st.markdown(kpi_card("Customers", customer_value, customer_delta_text, customer_dir, size="secondary"), unsafe_allow_html=True)
    with sec_cols[1]:
        st.markdown(kpi_card("Quantity Sold", quantity_value, quantity_delta_text, quantity_dir, size="secondary"), unsafe_allow_html=True)
    with sec_cols[2]:
        st.markdown(kpi_card("Avg Discount", discount_value, discount_delta_text, discount_dir, size="secondary"), unsafe_allow_html=True)

    st.write("")
    cust_left, cust_right = st.columns(2)

    with cust_left:
        if customer_col:
            st.write("**Top 10 Customers by Revenue**")
            top_customers = (
                filtered_df.groupby(customer_col)["Sales"]
                .sum().reset_index().sort_values("Sales", ascending=False).head(10)
            )
            base = alt.Chart(top_customers).encode(
                x=alt.X("Sales:Q", title="Total Sales"),
                y=alt.Y(f"{customer_col}:N", sort="-x", title=""),
            )
            bars = base.mark_bar(color=NEUTRAL_BAR_COLOR).encode(
                tooltip=[customer_col, alt.Tooltip("Sales:Q", format="$,.0f")]
            )
            labels = base.mark_text(dx=25, color="#d7dae2", fontSize=11).encode(
                text=alt.Text("Sales:Q", format="$,.0f")
            )
            st.altair_chart((bars + labels).properties(height=320), use_container_width=True)
        else:
            st.info("No customer column found in the dataset.")

    with cust_right:
        if "Segment" in filtered_df.columns:
            st.write("**Revenue by Customer Segment**")
            seg_df = filtered_df.groupby("Segment")["Sales"].sum().reset_index().sort_values("Sales", ascending=False)
            base = alt.Chart(seg_df).encode(
                x=alt.X("Segment:N", sort="-y", title=""),
                y=alt.Y("Sales:Q", title="Total Sales"),
            )
            bars = base.mark_bar().encode(
                color=alt.Color("Segment:N", scale=SEGMENT_COLOR_SCALE, legend=None),
                tooltip=["Segment", alt.Tooltip("Sales:Q", format="$,.0f")],
            )
            labels = base.mark_text(dy=-8, color="#d7dae2", fontSize=11).encode(
                text=alt.Text("Sales:Q", format="$,.0f")
            )
            st.altair_chart((bars + labels).properties(height=320), use_container_width=True)
        else:
            st.info("No Segment column found in the dataset.")

with tab_data:
    st.write(f"Showing filtered dataset — **{len(filtered_df):,} rows**")
    st.metric("Records in view", f"{len(filtered_df):,}", records_delta_text)
    st.dataframe(filtered_df.head(50), use_container_width=True)

    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name=f"filtered_{selected_region}_{selected_category}.csv".replace(" ", "_"),
        mime="text/csv",
    )

st.divider()
st.caption(f"Built with Streamlit • Data: Superstore dataset • AI: Gemini 2.5 Flash • {len(filtered_df):,} of {len(df):,} records in view")