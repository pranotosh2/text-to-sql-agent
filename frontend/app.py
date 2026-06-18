import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

API_URL = "http://backend:8000"  # Docker; for local dev use http://localhost:8000

# -----------------------------------------------------
# Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="AI Text-to-SQL Analytics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------
# Custom CSS (Dark Forest Green Theme)
# -----------------------------------------------------
st.markdown("""
<style>
.main {
    background-color: #013220;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(135deg, #11221A, #1E3E2F);
    padding: 2rem;
    border-radius: 18px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.12);
}
.hero h1 { margin: 0; font-size: 2.3rem; }
.hero p  { margin-top: 0.5rem; opacity: 0.9; }
section[data-testid="stSidebar"] { background: #11221A; }
section[data-testid="stSidebar"] * { color: white !important; }
.stButton > button {
    border-radius: 12px;
    border: none;
    font-weight: 600;
    padding: 0.55rem 1rem;
    background: linear-gradient(90deg, #2E7D32, #1B5E20);
    color: white;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 6px 20px rgba(46,125,50,0.3);
}
.metric-card {
    background: #F4F9F6;
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.05);
}
textarea { font-family: Consolas !important; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.footer {
    text-align: center;
    color: #556B2F;
    padding: 20px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# Chart helper (matplotlib — green theme)
# -----------------------------------------------------
GREEN_DARK   = "#1B5E20"
GREEN_MID    = "#2E7D32"
GREEN_LIGHT  = "#81C784"
CHART_BG     = "#F4F9F6"

def render_chart(chart_df, x_col, y_col, chart_type):
    fig, ax = plt.subplots(figsize=(11, 4.8))
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#C8E6C9")
    ax.spines["bottom"].set_color("#C8E6C9")
    ax.tick_params(colors="#2E7D32", labelsize=9)
    ax.grid(axis="y", color="#C8E6C9", linewidth=0.8, linestyle="--")
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())

    xs = chart_df[x_col].astype(str)
    ys = chart_df[y_col]

    if chart_type == "Bar":
        bars = ax.bar(xs, ys, color=GREEN_MID, width=0.55,
                      edgecolor="white", linewidth=0.6, zorder=3)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + h * 0.01,
                    f"{h:,.0f}", ha="center", va="bottom",
                    fontsize=8, color="#1B5E20")

    elif chart_type == "Line":
        ax.plot(xs, ys, color=GREEN_MID, linewidth=2.2,
                marker="o", markersize=5,
                markerfacecolor="white", markeredgewidth=1.8,
                markeredgecolor=GREEN_MID, zorder=3)
        ax.fill_between(range(len(xs)), ys, alpha=0.10, color=GREEN_MID)

    else:  # Scatter
        ax.scatter(chart_df[x_col], chart_df[y_col],
                   color=GREEN_MID, s=65, alpha=0.78,
                   edgecolors="white", linewidth=0.8, zorder=3)

    ax.set_xlabel(x_col, fontsize=9, color="#2E7D32", labelpad=8)
    ax.set_ylabel(y_col, fontsize=9, color="#2E7D32", labelpad=8)
    ax.set_title(f"{y_col}  by  {x_col}", fontsize=11,
                 fontweight="bold", color="#11221A", pad=14)
    plt.xticks(rotation=38, ha="right", fontsize=8.5)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------
with st.sidebar:
    st.title("Text-to-SQL Agent")
    st.markdown("Convert natural language into SQL queries and analyze your database using AI.")
    st.divider()
    st.subheader("Example Questions")

    examples = [
        "Show top 10 customers by total order value",
        "Which products have never been ordered?",
        "What is the monthly revenue trend for 1997?",
        "List all employees and how many orders they handled",
        "Show products with stock below reorder level",
        "Which country has the most customers?"
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["question"] = ex
            st.session_state["trigger"] = True

    st.divider()

st.subheader("🗄 Database")
if st.button("View Database Schema", use_container_width=True):
    try:
        response = requests.get(f"{API_URL}/schema", timeout=10)
        schema = response.json()["schema"]
        st.text_area("Schema", schema, height=300)
    except Exception as e:
        st.error(f"Connection failed: {e}")

# -----------------------------------------------------
# Hero Section
# -----------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 AI Text-to-SQL Analytics Dashboard</h1>
    <p>
        Ask questions in natural language, generate SQL automatically,
        execute queries, and visualize results instantly.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# Query Input
# -----------------------------------------------------
question = st.text_input(
    "Ask your database a question",
    value=st.session_state.get("question", ""),
    placeholder="e.g. Show top 10 customers by total order value",
    key="question_input"
)

col_run, col_space = st.columns([1, 6])
with col_run:
    run_btn = st.button("Run Query", type="primary")

trigger = st.session_state.pop("trigger", False)

# -----------------------------------------------------
# Execute Query
# -----------------------------------------------------
if (run_btn or trigger):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating SQL and querying database..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": question},
                    timeout=60
                )
                response.raise_for_status()
                st.session_state["query_data"] = response.json()
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend API.")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"API Error: {e.response.json().get('detail', str(e))}")
                st.stop()
            except Exception as e:
                st.error(f"Unexpected Error: {e}")
                st.stop()

# -----------------------------------------------------
# Dashboard
# -----------------------------------------------------
if "query_data" in st.session_state:
    data = st.session_state["query_data"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rows Returned", data.get("row_count", 0))
    with c2:
        st.metric("Status", "Success")
    with c3:
        st.metric("Query Type", "SELECT")

    edited_sql = st.text_area(
        "Generated SQL",
        value=data.get("sql", ""),
        height=150
    )

    colA, colB = st.columns([1, 5])
    with colA:
        if st.button("Re-run SQL"):
            try:
                rerun = requests.post(
                    f"{API_URL}/execute",
                    json={"sql": edited_sql},
                    timeout=30
                )
                rerun.raise_for_status()
                rerun_data = rerun.json()
                data["rows"]      = rerun_data["rows"]
                data["columns"]   = rerun_data["columns"]
                data["row_count"] = rerun_data["row_count"]
                st.session_state["query_data"] = data
                st.success(f"Returned {data['row_count']} rows")
                st.rerun()
            except Exception as e:
                st.error(f"Execution Error: {e}")

    if data.get("rows"):
        df = pd.DataFrame(data["rows"])

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Results",
            "📈 Visualization",
            "📝 SQL",
            "🤖 Agent Reasoning"
        ])

        with tab1:
            st.dataframe(df, use_container_width=True, height=500)

        with tab2:
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            text_cols    = df.select_dtypes(include="object").columns.tolist()

            if numeric_cols and text_cols:
                col1, col2, col3 = st.columns(3)
                with col1:
                    x_col = st.selectbox("X Axis", text_cols)
                with col2:
                    y_col = st.selectbox("Y Axis", numeric_cols)
                with col3:
                    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter"])

                chart_df = df[[x_col, y_col]].dropna()
                render_chart(chart_df, x_col, y_col, chart_type)
            else:
                st.info("Visualization requires at least one text column and one numeric column.")

        with tab3:
            st.code(edited_sql, language="sql")

        with tab4:
            st.write(data.get("summary", "No reasoning available."))

        csv = df.to_csv(index=False)
        st.divider()
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "⬇ Download CSV", data=csv,
                file_name="query_results.csv", mime="text/csv",
                use_container_width=True
            )
        with d2:
            st.download_button(
                "⬇ Download SQL", data=edited_sql,
                file_name="generated_query.sql",
                use_container_width=True
            )
    else:
        st.info("Query executed successfully but returned no rows.")

# -----------------------------------------------------
# Footer
# -----------------------------------------------------
st.markdown("---")
st.markdown("""
<div class="footer">
    AI Text-to-SQL Analytics Dashboard • FastAPI • LangGraph • Streamlit • SQL
</div>
""", unsafe_allow_html=True)