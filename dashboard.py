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
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 216, 155, 0.35), transparent 28%),
            radial-gradient(circle at top right, rgba(157, 228, 255, 0.28), transparent 24%),
            linear-gradient(180deg, #fffdf8 0%, #f6f9ff 100%);
        color: #1f2937;
    }
    header[data-testid="stHeader"] {
        background: rgba(255, 253, 248, 0.9) !important;
        border-bottom: 1px solid #dbe4f0;
    }
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    [data-testid="stDecoration"] {
        background: linear-gradient(90deg, #ffd58f 0%, #8fd8ff 100%) !important;
    }
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.9);
        border-right: 1px solid #dbe4f0;
    }
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #d9e2ef;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        border-top: 3px solid #2f80ed;
        box-shadow: 0 10px 30px rgba(47, 128, 237, 0.08);
    }
    [data-testid="metric-container"] label { color: #64748b !important; font-size: 0.75rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #0f172a !important; font-size: 1.8rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #0f9d58 !important; }
    h1, h2, h3 { color: #0f172a !important; }
    p, label, span, div { color: #334155; }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        padding: 6px;
        gap: 8px;
        border: 1px solid #dbe4f0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #64748b;
        border-radius: 8px;
        font-size: 0.9rem;
        padding: 8px 22px !important;
    }
    .stTabs [aria-selected="true"] { background: #2f80ed !important; color: white !important; }
    .stTextInput input {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid #dbe4f0 !important;
        color: #0f172a !important;
        border-radius: 10px !important;
        font-family: monospace;
    }
    .stButton > button {
        background: linear-gradient(180deg, #ffffff 0%, #f4f8ff 100%) !important;
        color: #1e3a5f !important;
        border: 1px solid #cfe0f5 !important;
        border-radius: 10px !important;
        box-shadow: 0 6px 18px rgba(47, 128, 237, 0.08);
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        border-color: #2f80ed !important;
        color: #0f172a !important;
        background: linear-gradient(180deg, #ffffff 0%, #eaf3ff 100%) !important;
    }
    .stButton > button:focus {
        box-shadow: 0 0 0 0.2rem rgba(47, 128, 237, 0.18) !important;
    }
    .stButton > button:disabled {
        background: #f8fafc !important;
        color: #94a3b8 !important;
        border-color: #e2e8f0 !important;
        box-shadow: none !important;
    }
    [data-testid="stDataFrame"] { background: rgba(255, 255, 255, 0.9); border-radius: 14px; }
    hr { border-color: #dbe4f0 !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# CONSTANTS
# =========================
# Add future grades here as new key/url pairs.
SHEET_SOURCES = {
    "AISSE / Grade 10": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQLsX4iJq5RtPd_Jt1hvfVIxXweaYRPnPlPwNNkbAMfcm-bVyFP45pVH7uBwVL9eZKKGe0NRxVQjO4R/pub?output=csv"
}
BAND_ORDER = ["90-100%", "80-89%", "70-79%", "60-69%", "50-59%", "40-49%", "33-39%", "Below 33%"]
BAND_COLORS = {
    "90-100%": "#1f9d55",
    "80-89%": "#2f80ed",
    "70-79%": "#56ccf2",
    "60-69%": "#9b8cff",
    "50-59%": "#f2c94c",
    "40-49%": "#f2994a",
    "33-39%": "#eb5757",
    "Below 33%": "#9aa5b1",
}


def theme(fig, title="", height=None):
    """Apply a consistent light theme to a plotly figure."""
    opts = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.82)",
        font_color="#475569",
        font_size=12,
        margin=dict(l=20, r=20, t=44 if title else 20, b=20),
        showlegend=False,
    )
    if title:
        opts["title"] = dict(text=title, font=dict(color="#0f172a", size=15))
    if height:
        opts["height"] = height
    fig.update_layout(**opts)
    fig.update_xaxes(gridcolor="#e2e8f0", linecolor="#dbe4f0", zerolinecolor="#dbe4f0")
    fig.update_yaxes(gridcolor="#e2e8f0", linecolor="#dbe4f0", zerolinecolor="#dbe4f0")
    return fig


# =========================
# PERCENTAGE BANDS
# =========================
def get_percentage_band(p):
    if p >= 90: return "90-100%"
    if p >= 80: return "80-89%"
    if p >= 70: return "70-79%"
    if p >= 60: return "60-69%"
    if p >= 50: return "50-59%"
    if p >= 40: return "40-49%"
    if p >= 33: return "33-39%"
    return "Below 33%"


def make_band_chip(label, color, count, avg_score):
    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.95);
            border: 1px solid #dbe4f0;
            border-left: 6px solid {color};
            border-radius: 14px;
            padding: 0.9rem 1rem;
            min-height: 92px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        ">
            <div style="font-weight:700;color:#0f172a;font-size:0.95rem;">{label}</div>
            <div style="color:#475569;font-size:0.82rem;margin-top:0.25rem;">{count} students</div>
            <div style="color:#64748b;font-size:0.8rem;margin-top:0.15rem;">Avg {avg_score:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# DATA LOADING
# =========================
@st.cache_data(ttl=300, show_spinner=False)
def load_data(sheet_url):
    df = pd.read_csv(sheet_url)
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
    df["PERCENTAGE_BAND"] = df["PCT"].apply(get_percentage_band)
    return df


# =========================
# DATASET PICKER
# =========================
selected_dataset = st.sidebar.selectbox("Dataset / Grade", list(SHEET_SOURCES.keys()))

# =========================
# LOAD DATA
# =========================
with st.spinner("Loading student records..."):
    try:
        df = load_data(SHEET_SOURCES[selected_dataset])
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
    st.markdown("## 🎓 Results Dashboard")
    st.caption("Pick a grade dataset, then explore the same analysis layout.")
    st.markdown(
        f"<small style='color:#64748b;font-family:monospace'>{len(df)} records loaded</small>",
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
    st.markdown("### 📚 Percentage Bands")
    for band, color in BAND_COLORS.items():
        st.markdown(
            f"<span style='display:inline-block;width:10px;height:10px;background:{color};"
            f"border-radius:2px;margin-right:6px'></span>"
            f"<span style='font-family:monospace;font-size:0.8rem;color:#64748b'>{band}</span>",
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
roll_col = next((c for c in df.columns if "Board_Roll" in c or "Roll" in c), None)
name_col = "NAME" if "NAME" in df.columns else None
father_col = next((c for c in df.columns if "FATHER" in c.upper()), None)
sub_cols = [c for c in df.columns if c.startswith("SUB")]
mo_cols = [c for c in df.columns if c.startswith("MO")]

# =========================
# HEADER + KPIs
# =========================
st.markdown(
    f"# {selected_dataset} <span style='color:#2f80ed'>Performance Dashboard</span>",
    unsafe_allow_html=True,
)
st.caption("Percentage-first analysis with class trends, score bands, and student-level lookup.")

if "selected_band" not in st.session_state:
    st.session_state.selected_band = None

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
        band_counts = (
            dff["PERCENTAGE_BAND"].value_counts()
            .reindex(BAND_ORDER, fill_value=0)
            .reset_index()
        )
        band_counts.columns = ["Percentage Range", "Count"]

        fig_band = go.Figure(go.Bar(
            x=band_counts["Percentage Range"],
            y=band_counts["Count"],
            marker_color=[BAND_COLORS[band] for band in band_counts["Percentage Range"]],
            text=band_counts["Count"],
            textposition="outside",
            textfont=dict(color="#0f172a", size=11),
            hovertemplate="%{x}: %{y} students<extra></extra>",
        ))
        fig_band.update_xaxes(title=None)
        fig_band.update_yaxes(title="Students")
        theme(fig_band, "Percentage Range Distribution")
        st.plotly_chart(fig_band, use_container_width=True)

    with col_b:
        result_counts = dff["RESULT"].value_counts() if "RESULT" in dff.columns else pd.Series()
        fig_pie = go.Figure(go.Pie(
            labels=result_counts.index.tolist(),
            values=result_counts.values.tolist(),
            hole=0.65,
            marker=dict(colors=["#1f9d55", "#eb5757"], line=dict(width=0)),
            textinfo="percent",
            textposition="inside",
            textfont=dict(color="#ffffff", size=13),
            hovertemplate="%{label}: %{value} students (%{percent})<extra></extra>",
        ))
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=-0.15,
                xanchor="center", x=0.5,
                font=dict(color="#475569", size=12),
            )
        )
        theme(fig_pie, "Pass / Fail Split", height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    fig_hist = go.Figure(go.Histogram(
        x=dff["PCT"],
        nbinsx=20,
        marker_color="#2f80ed",
        hovertemplate="Score: %{x}<br>Students: %{y}<extra></extra>",
    ))
    fig_hist.update_xaxes(title="Score (%)")
    fig_hist.update_yaxes(title="Students")
    theme(fig_hist, "Score Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)

    band_summary = (
        dff.groupby("PERCENTAGE_BAND", observed=False)
        .agg(
            Students=("PCT", "count"),
            Average_Score=("PCT", "mean"),
        )
        .reindex(BAND_ORDER, fill_value=0)
        .reset_index()
    )
    band_summary["Average_Score"] = band_summary["Average_Score"].round(1)
    st.markdown("#### Range Snapshot")

    chip_columns = st.columns(4)
    for idx, row in band_summary.iterrows():
        band_label = row["PERCENTAGE_BAND"]
        with chip_columns[idx % 4]:
            make_band_chip(
                band_label,
                BAND_COLORS[band_label],
                int(row["Students"]),
                float(row["Average_Score"]),
            )
            if st.button(
                "View students",
                key=f"band_{band_label}",
                use_container_width=True,
                disabled=int(row["Students"]) == 0,
            ):
                st.session_state.selected_band = band_label

    selected_band = st.session_state.get("selected_band")
    if selected_band:
        detail_cols = []
        for col_name in [roll_col, name_col, "CLASS", "Gender", "PCT", "RESULT", "PERCENTAGE_BAND"]:
            if col_name and col_name in dff.columns and col_name not in detail_cols:
                detail_cols.append(col_name)

        band_students = (
            dff[dff["PERCENTAGE_BAND"] == selected_band]
            .sort_values("PCT", ascending=False)[detail_cols]
        )

        header_col, action_col = st.columns([5, 1])
        with header_col:
            st.markdown(f"#### Students in {selected_band}")
        with action_col:
            if st.button("Clear", key="clear_selected_band", use_container_width=True):
                st.session_state.selected_band = None
                st.rerun()

        st.dataframe(
            band_students.style.format({"PCT": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )

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
                <div style='background:rgba(255,255,255,0.92);border:1px solid #dbe4f0;border-radius:16px;
                            padding:1.2rem 1.4rem;margin-bottom:0.5rem'>
                    <h3 style='color:#0f172a;margin:0 0 4px'>{s.get('NAME', 'N/A')}</h3>
                    <p style='color:#64748b;font-family:monospace;font-size:0.8rem;margin:0'>
                        Roll: {s.get(roll_col, 'N/A') if roll_col else 'N/A'} &middot;
                        Class: {cls} &middot; Gender: {s.get('Gender', 'N/A')} {father_str}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Score", f"{s['PCT']:.2f}%", delta=f"{s['PCT'] - school_avg:+.1f}% vs school")
                m2.metric("Total Marks", s.get("TOTAL", "N/A"))
                m3.metric("Result", s.get("RESULT", "N/A"))
                m4.metric("Range", s.get("PERCENTAGE_BAND", get_percentage_band(s["PCT"])))

                comp_vals = [s["PCT"], class_avg, school_avg]
                fig_comp = go.Figure(go.Bar(
                    x=["This Student", "Class Average", "School Average"],
                    y=comp_vals,
                    marker_color=["#2f80ed", "#56ccf2", "#9aa5b1"],
                    text=[f"{v:.1f}%" for v in comp_vals],
                    textposition="outside",
                    textfont=dict(color="#0f172a"),
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
                            marker_color="#2f80ed",
                            text=sub_df["Marks"].apply(lambda x: f"{x:.0f}"),
                            textposition="outside",
                            textfont=dict(color="#0f172a"),
                        ))
                        theme(fig_sub, "Subject-wise Marks", height=260)
                        st.plotly_chart(fig_sub, use_container_width=True)

                st.divider()

    else:
        st.markdown(
            "<div style='color:#64748b;font-family:monospace;font-size:0.85rem;padding:1rem 0'>"
            "Enter a roll number or name above to look up results</div>",
            unsafe_allow_html=True
        )
        st.markdown("#### 🏆 Top 10 Performers")
        top_cols = [c for c in ["NAME", "CLASS", "PCT", "RESULT", "PERCENTAGE_BAND"] if c in dff.columns]
        top10 = dff.nlargest(10, "PCT")[top_cols]
        st.dataframe(
            top10.style
            .background_gradient(subset=["PCT"], cmap="RdYlGn", vmin=0, vmax=100)
            .format({"PCT": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )
