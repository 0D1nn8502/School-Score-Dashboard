import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="AISSE Results Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0d0f14; }
    section[data-testid="stSidebar"] { background-color: #14171f; border-right: 1px solid #252a38; }
    [data-testid="metric-container"] {
        background: #1a1e28;
        border: 1px solid #252a38;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border-top: 2px solid #4f8ef7;
    }
    [data-testid="metric-container"] label { color: #9ca3af !important; font-size: 0.75rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8eaf0 !important; font-size: 1.8rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #3ecf8e !important; }
    h1, h2, h3 { color: #e8eaf0 !important; }
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1e28; border-radius: 8px; padding: 4px; gap: 2px; border: 1px solid #252a38;
    }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #9ca3af; border-radius: 6px; font-size: 0.85rem; }
    .stTabs [aria-selected="true"] { background: #4f8ef7 !important; color: white !important; }
    .stTextInput input {
        background: #1a1e28 !important; border: 1px solid #252a38 !important;
        color: #e8eaf0 !important; border-radius: 8px !important; font-family: monospace;
    }
    hr { border-color: #252a38 !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# CONSTANTS
# =========================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQLsX4iJq5RtPd_Jt1hvfVIxXweaYRPnPlPwNNkbAMfcm-bVyFP45pVH7uBwVL9eZKKGe0NRxVQjO4R/pub?output=csv"
GRADE_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2", "D", "E"]
GRADE_COLORS = {
    "A1": "#3ecf8e", "A2": "#4f8ef7", "B1": "#7c6af5", "B2": "#a78bfa",
    "C1": "#f5a623", "C2": "#fb923c", "D": "#e75858", "E": "#6b7280"
}


def theme(fig, title="", height=None):
    """Apply consistent dark theme to a plotly figure."""
    opts = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,30,40,0.6)",
        font_color="#9ca3af",
        font_size=12,
        margin=dict(l=20, r=20, t=44 if title else 20, b=20),
        showlegend=False,
    )
    if title:
        opts["title"] = dict(text=title, font=dict(color="#e8eaf0", size=14))
    if height:
        opts["height"] = height
    fig.update_layout(**opts)
    fig.update_xaxes(gridcolor="#252a38", linecolor="#252a38", zerolinecolor="#252a38")
    fig.update_yaxes(gridcolor="#252a38", linecolor="#252a38", zerolinecolor="#252a38")
    return fig


# =========================
# GRADE FUNCTION
# =========================
def get_grade(p):
    if p >= 91: return "A1"
    if p >= 81: return "A2"
    if p >= 71: return "B1"
    if p >= 61: return "B2"
    if p >= 51: return "C1"
    if p >= 41: return "C2"
    if p >= 33: return "D"
    return "E"


# =========================
# DATA LOADING
# =========================
@st.cache_data(ttl=300, show_spinner=False)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"%": "PCT"})
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"[\n\r]", "_", regex=True)
        .str.replace(" ", "_")
        .str.replace("'", "")
    )
    if "PCT" in df.columns:
        df["PCT"] = pd.to_numeric(df["PCT"], errors="coerce").fillna(0)
    if "RESULT" in df.columns:
        df["RESULT"] = df["RESULT"].str.strip().str.upper()
    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].str.strip().str.upper()
    df["GRADE"] = df["PCT"].apply(get_grade)
    return df


# =========================
# LOAD DATA
# =========================
with st.spinner("Loading student records..."):
    try:
        df = load_data()
        load_error = None
    except Exception as e:
        df = pd.DataFrame()
        load_error = str(e)

if load_error:
    st.error(f"Failed to load data: {load_error}")
    st.stop()

# =========================
# SIDEBAR FILTERS
# =========================
with st.sidebar:
    st.markdown("## 🎓 AISSE Dashboard")
    st.markdown(
        f"<small style='color:#6b7280;font-family:monospace'>{len(df)} records loaded</small>",
        unsafe_allow_html=True
    )
    st.divider()
    st.markdown("### 🔎 Filters")

    classes = sorted(df["CLASS"].dropna().unique()) if "CLASS" in df.columns else []
    sel_classes = st.multiselect("Class", classes, default=classes)

    genders = sorted(df["Gender"].dropna().unique()) if "Gender" in df.columns else []
    sel_genders = st.multiselect("Gender", genders, default=genders)

    results_opts = sorted(df["RESULT"].dropna().unique()) if "RESULT" in df.columns else []
    sel_results = st.multiselect("Result", results_opts, default=results_opts)

    st.divider()
    st.markdown("### 🏅 Grade Legend")
    for g, c in GRADE_COLORS.items():
        st.markdown(
            f"<span style='display:inline-block;width:10px;height:10px;background:{c};"
            f"border-radius:2px;margin-right:6px'></span>"
            f"<span style='font-family:monospace;font-size:0.8rem;color:#9ca3af'>{g}</span>",
            unsafe_allow_html=True
        )

# =========================
# APPLY FILTERS
# =========================
mask = pd.Series([True] * len(df))
if sel_classes and "CLASS" in df.columns:
    mask &= df["CLASS"].isin(sel_classes)
if sel_genders and "Gender" in df.columns:
    mask &= df["Gender"].isin(sel_genders)
if sel_results and "RESULT" in df.columns:
    mask &= df["RESULT"].isin(sel_results)

dff = df[mask].copy()

# =========================
# HEADER + KPIs
# =========================
st.markdown("# AISSE <span style='color:#4f8ef7'>Results</span>", unsafe_allow_html=True)

total = len(dff)
passed = int((dff["RESULT"] == "PASS").sum()) if "RESULT" in dff.columns else 0
avg_pct = dff["PCT"].mean() if total else 0
top_pct = dff["PCT"].max() if total else 0
pass_rate = (passed / total * 100) if total else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Total Students", total)
c2.metric("✅ Passed", passed, delta=f"{pass_rate:.1f}% pass rate")
c3.metric("📈 Avg Score", f"{avg_pct:.1f}%")
c4.metric("🏆 Top Score", f"{top_pct:.1f}%")

st.divider()

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📊  Overview", "🏫  Class Analysis", "🔍  Student Lookup"])


# ─────────────────────────
# TAB 1: OVERVIEW
# ─────────────────────────
with tab1:
    col_a, col_b = st.columns([3, 2])

    with col_a:
        grade_counts = (
            dff["GRADE"].value_counts()
            .reindex(GRADE_ORDER, fill_value=0)
            .reset_index()
        )
        grade_counts.columns = ["Grade", "Count"]

        fig_grade = go.Figure(go.Bar(
            x=grade_counts["Grade"],
            y=grade_counts["Count"],
            marker_color=[GRADE_COLORS[g] for g in grade_counts["Grade"]],
            text=grade_counts["Count"],
            textposition="outside",
            textfont=dict(color="#e8eaf0", size=11),
        ))
        fig_grade.update_xaxes(title=None)
        fig_grade.update_yaxes(title="Students")
        theme(fig_grade, "Grade Distribution")
        st.plotly_chart(fig_grade, use_container_width=True)

    with col_b:
        result_counts = dff["RESULT"].value_counts() if "RESULT" in dff.columns else pd.Series()
        fig_pie = go.Figure(go.Pie(
            labels=result_counts.index.tolist(),
            values=result_counts.values.tolist(),
            hole=0.65,
            marker=dict(colors=["#3ecf8e", "#e75858"], line=dict(width=0)),
            textinfo="percent+label",
            textfont=dict(color="#e8eaf0"),
            hovertemplate="%{label}: %{value} students<extra></extra>",
        ))
        theme(fig_pie, "Pass / Fail Split")
        st.plotly_chart(fig_pie, use_container_width=True)

    fig_hist = go.Figure(go.Histogram(
        x=dff["PCT"],
        nbinsx=20,
        marker_color="#4f8ef7",
        hovertemplate="Score: %{x}<br>Students: %{y}<extra></extra>",
    ))
    fig_hist.update_xaxes(title="Score (%)")
    fig_hist.update_yaxes(title="Students")
    theme(fig_hist, "Score Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)

    if "Gender" in dff.columns and dff["Gender"].nunique() > 1:
        st.markdown("#### Gender Breakdown")
        g1, g2 = st.columns(2)
        for col, gender, label, icon in [(g1, "M", "Male", "♂"), (g2, "F", "Female", "♀")]:
            gdf = dff[dff["Gender"] == gender]
            with col:
                st.metric(
                    f"{icon} {label}", len(gdf),
                    delta=f"Avg {gdf['PCT'].mean():.1f}%" if len(gdf) else None
                )


# ─────────────────────────
# TAB 2: CLASS ANALYSIS
# ─────────────────────────
with tab2:
    if "CLASS" not in dff.columns:
        st.warning("CLASS column not found in data.")
    else:
        class_df = (
            dff.groupby("CLASS")
            .agg(
                Total=("PCT", "count"),
                Avg_Score=("PCT", "mean"),
                Max_Score=("PCT", "max"),
                Min_Score=("PCT", "min"),
                Passed=("RESULT", lambda x: (x == "PASS").sum()),
            )
            .reset_index()
        )
        class_df["Pass_Rate"] = (class_df["Passed"] / class_df["Total"] * 100).round(1)
        class_df["Avg_Score"] = class_df["Avg_Score"].round(1)

        fig_class = go.Figure(go.Bar(
            y=class_df["CLASS"].astype(str),
            x=class_df["Avg_Score"],
            orientation="h",
            marker=dict(
                color=class_df["Avg_Score"],
                colorscale=[[0, "#e75858"], [0.5, "#f5a623"], [1, "#3ecf8e"]],
                showscale=True,
                colorbar=dict(
                    title=dict(text="Avg %", font=dict(color="#9ca3af")),
                    tickfont=dict(color="#9ca3af"),
                ),
            ),
            text=class_df["Avg_Score"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(color="#e8eaf0"),
            hovertemplate="Class %{y}<br>Avg: %{x:.1f}%<extra></extra>",
        ))
        fig_class.update_xaxes(range=[0, 110], ticksuffix="%")
        theme(fig_class, "Average Score by Class", height=max(300, len(class_df) * 50 + 100))
        st.plotly_chart(fig_class, use_container_width=True)

        fig_pass = go.Figure(go.Bar(
            x=class_df["CLASS"].astype(str),
            y=class_df["Pass_Rate"],
            marker=dict(
                color=class_df["Pass_Rate"],
                colorscale=[[0, "#e75858"], [0.5, "#f5a623"], [1, "#3ecf8e"]],
                showscale=False,
            ),
            text=class_df["Pass_Rate"].apply(lambda x: f"{x:.0f}%"),
            textposition="outside",
            textfont=dict(color="#e8eaf0"),
            hovertemplate="Class %{x}<br>Pass Rate: %{y:.1f}%<extra></extra>",
        ))
        fig_pass.update_yaxes(range=[0, 115], ticksuffix="%")
        theme(fig_pass, "Pass Rate by Class")
        st.plotly_chart(fig_pass, use_container_width=True)

        st.markdown("#### Class Summary Table")
        display_df = class_df.rename(columns={
            "CLASS": "Class", "Total": "Total Students",
            "Avg_Score": "Avg Score (%)", "Max_Score": "Top Score",
            "Min_Score": "Min Score", "Passed": "Passed",
            "Pass_Rate": "Pass Rate (%)"
        })
        st.dataframe(
            display_df.style
            .background_gradient(subset=["Avg Score (%)"], cmap="RdYlGn", vmin=0, vmax=100)
            .background_gradient(subset=["Pass Rate (%)"], cmap="RdYlGn", vmin=0, vmax=100)
            .format({
                "Avg Score (%)": "{:.1f}", "Top Score": "{:.1f}",
                "Min Score": "{:.1f}", "Pass Rate (%)": "{:.1f}"
            }),
            use_container_width=True,
            hide_index=True,
        )


# ─────────────────────────
# TAB 3: STUDENT LOOKUP
# ─────────────────────────
with tab3:
    query = st.text_input(
        "🔍 Search by Roll Number or Name",
        placeholder="e.g. 12345 or Rahul Sharma"
    )

    roll_col = next((c for c in df.columns if "Board_Roll" in c or "Roll" in c), None)
    name_col = "NAME" if "NAME" in df.columns else None
    father_col = next((c for c in df.columns if "FATHER" in c.upper()), None)
    sub_cols = [c for c in df.columns if c.startswith("SUB")]
    mo_cols = [c for c in df.columns if c.startswith("MO")]
    school_avg = df["PCT"].mean()

    if query:
        cond = pd.Series([False] * len(df))
        if roll_col:
            cond |= df[roll_col].astype(str).str.strip() == query.strip()
        if name_col:
            cond |= df[name_col].str.contains(query, case=False, na=False)
        results = df[cond]

        if results.empty:
            st.error("No student found. Try a different roll number or name.")
        else:
            st.success(f"Found {len(results)} student(s)")

            for _, s in results.iterrows():
                cls = s.get("CLASS", "N/A")
                class_avg = df[df["CLASS"] == cls]["PCT"].mean() if "CLASS" in df.columns else school_avg
                father_str = f"&middot; Father: {s[father_col]}" if father_col and pd.notna(s.get(father_col)) else ""

                st.markdown(f"""
                <div style='background:#1a1e28;border:1px solid #252a38;border-radius:12px;
                            padding:1.2rem 1.4rem;margin-bottom:0.5rem'>
                    <h3 style='color:#e8eaf0;margin:0 0 4px'>{s.get('NAME', 'N/A')}</h3>
                    <p style='color:#6b7280;font-family:monospace;font-size:0.8rem;margin:0'>
                        Roll: {s.get(roll_col, 'N/A') if roll_col else 'N/A'} &middot;
                        Class: {cls} &middot; Gender: {s.get('Gender', 'N/A')} {father_str}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Score", f"{s['PCT']:.2f}%", delta=f"{s['PCT'] - school_avg:+.1f}% vs school")
                m2.metric("Total Marks", s.get("TOTAL", "N/A"))
                m3.metric("Result", s.get("RESULT", "N/A"))
                m4.metric("Grade", s.get("GRADE", get_grade(s["PCT"])))

                comp_vals = [s["PCT"], class_avg, school_avg]
                fig_comp = go.Figure(go.Bar(
                    x=["This Student", "Class Average", "School Average"],
                    y=comp_vals,
                    marker_color=["#4f8ef7", "#7c6af5", "#6b7280"],
                    text=[f"{v:.1f}%" for v in comp_vals],
                    textposition="outside",
                    textfont=dict(color="#e8eaf0"),
                ))
                fig_comp.update_yaxes(range=[0, 115], ticksuffix="%")
                theme(fig_comp, "Performance vs Peers", height=300)
                st.plotly_chart(fig_comp, use_container_width=True)

                if sub_cols and mo_cols:
                    sub_data = []
                    for sub, mo in zip(sub_cols, mo_cols):
                        code = s.get(sub)
                        marks = s.get(mo)
                        if pd.notna(code) and pd.notna(marks):
                            try:
                                sub_data.append({"Subject": str(int(float(code))), "Marks": float(marks)})
                            except (ValueError, TypeError):
                                pass
                    if sub_data:
                        sub_df = pd.DataFrame(sub_data)
                        fig_sub = go.Figure(go.Bar(
                            x=sub_df["Subject"],
                            y=sub_df["Marks"],
                            marker_color="#4f8ef7",
                            text=sub_df["Marks"].apply(lambda x: f"{x:.0f}"),
                            textposition="outside",
                            textfont=dict(color="#e8eaf0"),
                        ))
                        theme(fig_sub, "Subject-wise Marks", height=260)
                        st.plotly_chart(fig_sub, use_container_width=True)

                st.divider()

    else:
        st.markdown(
            "<div style='color:#6b7280;font-family:monospace;font-size:0.85rem;padding:1rem 0'>"
            "Enter a roll number or name above to look up results</div>",
            unsafe_allow_html=True
        )
        st.markdown("#### 🏆 Top 10 Performers")
        top_cols = [c for c in ["NAME", "CLASS", "PCT", "RESULT", "GRADE"] if c in dff.columns]
        top10 = dff.nlargest(10, "PCT")[top_cols]
        st.dataframe(
            top10.style
            .background_gradient(subset=["PCT"], cmap="RdYlGn", vmin=0, vmax=100)
            .format({"PCT": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )