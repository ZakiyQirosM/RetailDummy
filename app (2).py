"""
Retail Analytics Dashboard
Single-file Streamlit prototype for interview presentation.
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import random

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — clean, modern, card-based look
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    [data-testid="stAppViewContainer"] { background: #F0F4F8; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Title block */
    .dash-title   { font-size: 2rem; font-weight: 800; color: #1A237E; margin-bottom: 0; }
    .dash-sub     { font-size: 1rem; color: #5C6BC0; margin-bottom: 1.2rem; }

    /* KPI cards */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,.07);
        margin-bottom: 12px;
    }
    .kpi-label { font-size: .75rem; font-weight: 600; color: #7986CB; text-transform: uppercase; letter-spacing: .06em; }
    .kpi-value { font-size: 1.65rem; font-weight: 800; color: #1A237E; line-height: 1.2; }
    .kpi-sub   { font-size: .78rem; color: #90A4AE; margin-top: 4px; }

    /* Section headers */
    .section-title {
        font-size: 1rem; font-weight: 700; color: #283593;
        border-left: 4px solid #5C6BC0; padding-left: 10px;
        margin: 1.4rem 0 .8rem 0;
    }

    /* Insight cards */
    .insight-card {
        background: #FFFFFF; border-radius: 12px;
        padding: 14px 18px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
        border-left: 4px solid #5C6BC0; margin-bottom: 8px;
        font-size: .88rem; color: #37474F;
    }

    /* Chat bubble */
    .chat-user { background:#E8EAF6; border-radius:12px; padding:10px 14px; margin:6px 0; text-align:right; }
    .chat-bot  { background:#FFFFFF; border-radius:12px; padding:10px 14px; margin:6px 0;
                 box-shadow:0 1px 6px rgba(0,0,0,.07); border-left:4px solid #5C6BC0; }

    /* Plotly chart card wrapper */
    .chart-card {
        background:#FFFFFF; border-radius:14px;
        padding:16px; box-shadow:0 2px 10px rgba(0,0,0,.07);
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA GENERATION
# ─────────────────────────────────────────────
CUSTOMERS = ["PT ABC", "PT Maju", "CV Sukses", "PT Sejahtera"]
PRODUCTS  = ["Aqua", "Indomie", "Pocari", "Le Minerale"]
SALES_REP = ["Budi", "Andi", "Rina", "Doni"]

def generate_data() -> pd.DataFrame:
    """Generate ~300 rows of random retail data."""
    np.random.seed(random.randint(0, 9999))
    n = 300
    dates = pd.date_range("2024-01-01", "2024-12-31", periods=n)
    df = pd.DataFrame({
        "Date":     dates,
        "Month":    dates.month,
        "Year":     dates.year,
        "Customer": np.random.choice(CUSTOMERS, n),
        "Product":  np.random.choice(PRODUCTS,  n),
        "Sales":    np.random.choice(SALES_REP, n),
        "Revenue":  np.random.randint(5_000_000, 80_000_000, n),
        "Target":   np.random.randint(10_000_000, 60_000_000, n),
    })
    return df

# ─────────────────────────────────────────────
# SESSION STATE — persist data between reruns
# ─────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = generate_data()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_title, col_upload = st.columns([5, 1])
with col_title:
    st.markdown('<div class="dash-title">🛒 Retail Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-sub">Sales Performance Overview</div>', unsafe_allow_html=True)

with col_upload:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📤 Upload Excel", use_container_width=True):
        # Simulate upload with animated messages
        msgs = ["Reading file...", "Cleaning data...", "Generating dashboard..."]
        placeholder = st.empty()
        for msg in msgs:
            placeholder.info(f"⏳ {msg}")
            time.sleep(0.7)
        st.session_state.df = generate_data()
        placeholder.success("✅ Dashboard updated!")
        time.sleep(0.8)
        placeholder.empty()
        st.rerun()

st.divider()

# ─────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────
df_all = st.session_state.df.copy()

f1, f2, _ = st.columns([2, 2, 6])
with f1:
    month_opts = ["All"] + sorted(df_all["Month"].unique().tolist())
    sel_month  = st.selectbox("📅 Sort by Month", month_opts)
with f2:
    year_opts  = ["All"] + sorted(df_all["Year"].unique().tolist())
    sel_year   = st.selectbox("📆 Sort by Year", year_opts)

# Apply filters
df = df_all.copy()
if sel_month != "All":
    df = df[df["Month"] == sel_month]
if sel_year != "All":
    df = df[df["Year"] == sel_year]

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_revenue = df["Revenue"].sum()
total_target  = df["Target"].sum()
achievement   = (total_revenue / total_target * 100) if total_target else 0
top5_cust     = df.groupby("Customer")["Revenue"].sum().nlargest(5)
top5_prod     = df.groupby("Product")["Revenue"].sum().nlargest(5)
best_sales    = df.groupby("Sales")["Revenue"].sum().idxmax() if not df.empty else "N/A"

# ─────────────────────────────────────────────
# KPI CARDS — row 1
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)

def kpi_card(col, label, value, sub=""):
    col.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

kpi_card(c1, "Total Revenue",    f"Rp {total_revenue/1e9:.2f}B")
kpi_card(c2, "Total Target",     f"Rp {total_target/1e9:.2f}B")
kpi_card(c3, "Achievement",      f"{achievement:.1f}%", "vs target")
kpi_card(c4, "Top Customer",     top5_cust.index[0] if not top5_cust.empty else "N/A",
         f"Rp {top5_cust.iloc[0]/1e6:.1f}M" if not top5_cust.empty else "")
kpi_card(c5, "Top Product",      top5_prod.index[0] if not top5_prod.empty else "N/A",
         f"Rp {top5_prod.iloc[0]/1e6:.1f}M" if not top5_prod.empty else "")
kpi_card(c6, "Best Salesperson", best_sales,
         f"Rp {df.groupby('Sales')['Revenue'].sum().max()/1e6:.1f}M" if not df.empty else "")

# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
CHART_COLOR = "#5C6BC0"
PALETTE     = px.colors.qualitative.Pastel

st.markdown('<div class="section-title">Charts & Trends</div>', unsafe_allow_html=True)

# Row 1: Revenue Trend + Top Product
ch1, ch2 = st.columns([3, 2])

with ch1:
    trend = df.groupby("Month")["Revenue"].sum().reset_index()
    trend["Month_Name"] = pd.to_datetime(trend["Month"], format="%m").dt.strftime("%b")
    fig_trend = px.line(
        trend, x="Month_Name", y="Revenue",
        title="Revenue Trend (Monthly)",
        markers=True, color_discrete_sequence=[CHART_COLOR],
    )
    fig_trend.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        title_font_size=14, margin=dict(t=40, b=20, l=10, r=10),
        yaxis_tickformat=".2s",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with ch2:
    prod_rev = df.groupby("Product")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=True)
    fig_prod = px.bar(
        prod_rev, x="Revenue", y="Product",
        orientation="h", title="Top Product by Revenue",
        color="Product", color_discrete_sequence=PALETTE,
    )
    fig_prod.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, title_font_size=14,
        margin=dict(t=40, b=20, l=10, r=10),
        xaxis_tickformat=".2s",
    )
    st.plotly_chart(fig_prod, use_container_width=True)

# Row 2: Top Customer + Sales Performance
ch3, ch4 = st.columns([3, 2])

with ch3:
    cust_rev = df.groupby("Customer")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
    fig_cust = px.bar(
        cust_rev, x="Customer", y="Revenue",
        title="Top Customer by Revenue",
        color="Customer", color_discrete_sequence=PALETTE,
    )
    fig_cust.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, title_font_size=14,
        margin=dict(t=40, b=20, l=10, r=10),
        yaxis_tickformat=".2s",
    )
    st.plotly_chart(fig_cust, use_container_width=True)

with ch4:
    sales_perf = df.groupby("Sales")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=True)
    fig_sales = px.bar(
        sales_perf, x="Revenue", y="Sales",
        orientation="h", title="Sales Performance",
        color="Sales", color_discrete_sequence=PALETTE,
    )
    fig_sales.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, title_font_size=14,
        margin=dict(t=40, b=20, l=10, r=10),
        xaxis_tickformat=".2s",
    )
    st.plotly_chart(fig_sales, use_container_width=True)

# ─────────────────────────────────────────────
# AUTO INSIGHTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">💡 Auto Insights</div>', unsafe_allow_html=True)

def generate_insights(df: pd.DataFrame) -> list[str]:
    """Generate 4 automatic insights from the dataframe."""
    insights = []
    if df.empty:
        return ["No data available for the selected filters."]

    # 1. Revenue vs target
    rev   = df["Revenue"].sum()
    tgt   = df["Target"].sum()
    pct   = rev / tgt * 100 if tgt else 0
    status = "exceeds" if pct >= 100 else "is below"
    insights.append(
        f"📈 Total revenue of Rp {rev/1e9:.2f}B {status} target "
        f"({pct:.1f}% achievement)."
    )

    # 2. Top customer
    tc = df.groupby("Customer")["Revenue"].sum().idxmax()
    tc_rev = df.groupby("Customer")["Revenue"].sum().max()
    tc_share = tc_rev / rev * 100
    insights.append(
        f"🏆 {tc} is the top customer, contributing "
        f"Rp {tc_rev/1e6:.1f}M ({tc_share:.1f}% of revenue)."
    )

    # 3. Best product
    bp = df.groupby("Product")["Revenue"].sum().idxmax()
    bp_rev = df.groupby("Product")["Revenue"].sum().max()
    insights.append(
        f"🛍️ {bp} is the best-selling product with "
        f"Rp {bp_rev/1e6:.1f}M in revenue."
    )

    # 4. Best salesperson
    bs = df.groupby("Sales")["Revenue"].sum().idxmax()
    bs_rev = df.groupby("Sales")["Revenue"].sum().max()
    insights.append(
        f"⭐ {bs} is the top-performing salesperson with "
        f"Rp {bs_rev/1e6:.1f}M in closed revenue."
    )
    return insights

insights = generate_insights(df)
cols_ins = st.columns(2)
for i, insight in enumerate(insights):
    cols_ins[i % 2].markdown(
        f'<div class="insight-card">💬 {insight}</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# CHATBOT
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🤖 Ask the Dashboard</div>', unsafe_allow_html=True)

def chatbot_reply(question: str, df: pd.DataFrame) -> str:
    """Rule-based chatbot — no external API."""
    q = question.lower().strip()

    if any(k in q for k in ["top customer", "best customer", "pelanggan"]):
        tc  = df.groupby("Customer")["Revenue"].sum().idxmax()
        rev = df.groupby("Customer")["Revenue"].sum().max()
        return f"🏆 Top customer is **{tc}** with revenue Rp {rev/1e6:.1f}M."

    elif any(k in q for k in ["top product", "best product", "produk"]):
        bp  = df.groupby("Product")["Revenue"].sum().idxmax()
        rev = df.groupby("Product")["Revenue"].sum().max()
        return f"🛍️ Best-selling product is **{bp}** with Rp {rev/1e6:.1f}M in revenue."

    elif any(k in q for k in ["best sales", "top sales", "salesperson", "salesman"]):
        bs  = df.groupby("Sales")["Revenue"].sum().idxmax()
        rev = df.groupby("Sales")["Revenue"].sum().max()
        return f"⭐ Best salesperson is **{bs}** with Rp {rev/1e6:.1f}M closed."

    elif any(k in q for k in ["revenue", "total revenue", "pendapatan"]):
        rev = df["Revenue"].sum()
        return f"💰 Total revenue for the selected period is **Rp {rev/1e9:.2f}B**."

    elif any(k in q for k in ["achievement", "pencapaian", "target"]):
        rev = df["Revenue"].sum()
        tgt = df["Target"].sum()
        pct = rev / tgt * 100 if tgt else 0
        return (f"📊 Achievement is **{pct:.1f}%**  "
                f"(Revenue Rp {rev/1e9:.2f}B vs Target Rp {tgt/1e9:.2f}B).")

    else:
        return "🤔 Please ask about **sales**, **customer**, **product**, or **revenue**."

# Chat input
user_input = st.chat_input("Ask about sales, customer, product or revenue…")
if user_input:
    reply = chatbot_reply(user_input, df)
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))

# Display chat history (most recent last, max 10 messages shown)
for role, msg in st.session_state.chat_history[-10:]:
    if role == "user":
        st.markdown(f'<div class="chat-user">🧑 {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bot">🤖 {msg}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    "<center style='color:#B0BEC5; font-size:.78rem;'>"
    "Retail Analytics Dashboard — Interview Prototype · Built with Streamlit &amp; Plotly"
    "</center>",
    unsafe_allow_html=True,
)
