import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Census Explorer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

.stApp { background-color: #0f1117; color: #ffffff; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1f35 0%, #0f1117 100%);
    border-right: 1px solid #2d3561;
}

.hero-header {
    background: linear-gradient(135deg, #1e2340 0%, #2d3561 50%, #1a1f35 100%);
    border: 1px solid #3d4f8f;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero-subtitle { color: #8892b0; font-size: 0.95rem; margin-top: 0.5rem; }

.kpi-card {
    background: linear-gradient(135deg, #1e2340 0%, #2d3561 100%);
    border: 1px solid #3d4f8f;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 0.5rem;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(102,126,234,0.3); }
.kpi-value { font-size: 1.7rem; font-weight: 700; color: #667eea; margin: 0.3rem 0; }
.kpi-value-b { font-size: 1.7rem; font-weight: 700; color: #f093fb; margin: 0.3rem 0; }
.kpi-label { font-size: 0.75rem; color: #8892b0; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; }
.kpi-delta { font-size: 0.72rem; font-weight: 500; margin-top: 0.2rem; }
.delta-up { color: #43e97b; }
.delta-down { color: #f7797d; }

.section-header {
    font-size: 1.05rem;
    font-weight: 600;
    color: #ccd6f6;
    border-left: 3px solid #667eea;
    padding-left: 0.75rem;
    margin: 1.5rem 0 1rem 0;
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ── Load & Prepare Data ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('india.csv')
    df = df.drop_duplicates(subset=['State', 'District', 'Latitude', 'Longitude'])
    df = df.dropna(subset=['Latitude', 'Longitude', 'Population'])
    df = df[df['Population'] > 0]
    df['Internet_Penetration'] = (df['Households_with_Internet'] / df['Population'] * 100).round(2)
    df['Literacy_Band'] = pd.cut(
        df['literacy_rate'],
        bins=[0, 55, 70, 100],
        labels=['Low (<55%)', 'Medium (55–70%)', 'High (>70%)']
    )
    return df

df = load_data()

NUMERIC_COLS = ['Population', 'Households_with_Internet', 'sex_ratio', 'literacy_rate', 'Internet_Penetration']
NAT_AVG = {
    'literacy_rate': df['literacy_rate'].mean(),
    'sex_ratio': df['sex_ratio'].mean(),
    'Internet_Penetration': df['Internet_Penetration'].mean(),
}
MAP_STYLES = {
    '🌙 Dark': 'carto-darkmatter',
    '☀️ Light': 'carto-positron',
    '🗺️ Streets': 'open-street-map',
    '🌿 Terrain': 'stamen-terrain',
}
CHART_THEME = dict(
    paper_bgcolor='rgba(30,35,64,0.85)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white', family='Inter'),
    title_font=dict(color='#ccd6f6', size=14),
)

list_of_states = sorted(df['State'].unique().tolist())
list_of_states_with_overall = ['Overall India'] + list_of_states

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ India Census Explorer")
    st.markdown("---")

    mode = st.radio("Dashboard Mode", ["🔍 Explore", "⚔️ Compare States"], horizontal=False)
    st.markdown("---")

    if mode == "🔍 Explore":
        selected_state = st.selectbox("Select State / UT", list_of_states_with_overall)
    else:
        state_a = st.selectbox("State A", list_of_states, index=0)
        state_b = st.selectbox("State B", list_of_states, index=5)

    primary   = st.selectbox("Primary Metric (bubble size)",  sorted(NUMERIC_COLS), index=0)
    secondary = st.selectbox("Secondary Metric (bubble color)", sorted(NUMERIC_COLS), index=3)
    map_style_label = st.selectbox("Map Style", list(MAP_STYLES.keys()))
    map_style = MAP_STYLES[map_style_label]

    st.markdown("---")
    search_district = st.text_input("🔍 Highlight District", placeholder="e.g. Jaipur")

    st.markdown("---")
    if mode == "🔍 Explore":
        dl_df = df if selected_state == 'Overall India' else df[df['State'] == selected_state]
    else:
        dl_df = df[df['State'].isin([state_a, state_b])]

    st.download_button(
        "⬇️ Download Filtered Data",
        data=dl_df.to_csv(index=False),
        file_name="india_census_filtered.csv",
        mime="text/csv"
    )
    st.markdown("---")
    st.caption("Source: Census of India 2011")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <p class="hero-title">🗺️ India Census Explorer</p>
    <p class="hero-subtitle">Interactive district-level socio-economic dashboard · Census of India 2011</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# EXPLORE MODE
# ─────────────────────────────────────────────────────────────────────────────
if mode == "🔍 Explore":
    view_df = df if selected_state == 'Overall India' else df[df['State'] == selected_state]

    # ── KPI Cards ────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">📊 Key Metrics</p>', unsafe_allow_html=True)

    total_pop   = view_df['Population'].sum()
    n_districts = len(view_df)
    avg_lit     = view_df['literacy_rate'].mean()
    avg_sex     = view_df['sex_ratio'].mean()
    avg_int     = view_df['Internet_Penetration'].mean()

    def delta_tag(val, unit=""):
        arrow, cls = ("▲", "delta-up") if val >= 0 else ("▼", "delta-down")
        return f'<span class="kpi-delta {cls}">{arrow} {abs(val):.1f}{unit} vs national avg</span>'

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, value, label, delta in [
        (c1, f"{total_pop/1e6:.1f}M", "Total Population", ""),
        (c2, f"{n_districts}",        "Districts",        ""),
        (c3, f"{avg_lit:.1f}%",       "Avg Literacy",     delta_tag(avg_lit - NAT_AVG['literacy_rate'], "%")),
        (c4, f"{avg_sex:.0f}",        "Avg Sex Ratio",    delta_tag(avg_sex - NAT_AVG['sex_ratio'])),
        (c5, f"{avg_int:.1f}%",       "Internet Penetration", delta_tag(avg_int - NAT_AVG['Internet_Penetration'], "%")),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                {delta}
            </div>""", unsafe_allow_html=True)

    st.markdown(" ")

    # ── Map ───────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">🗺️ District Map</p>', unsafe_allow_html=True)

    map_df = view_df[view_df[primary] > 0].copy()
    zoom   = 4 if selected_state == 'Overall India' else 6

    fig_map = px.scatter_mapbox(
        map_df,
        lat="Latitude", lon="Longitude",
        size=primary, color=secondary,
        zoom=zoom, size_max=40,
        mapbox_style=map_style,
        height=580,
        hover_name='District',
        hover_data={'State': True, 'Population': ':,', 'literacy_rate': ':.1f',
                    'sex_ratio': ':.0f', 'Internet_Penetration': ':.2f',
                    'Latitude': False, 'Longitude': False},
        color_continuous_scale='Viridis',
    )
    fig_map.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(bgcolor='rgba(15,17,23,0.8)',
                                tickfont=dict(color='white'),
                                title=dict(font=dict(color='white')))
    )

    if search_district:
        matched = view_df[view_df['District'].str.contains(search_district, case=False, na=False)]
        if not matched.empty:
            fig_map.add_trace(go.Scattermapbox(
                lat=matched['Latitude'], lon=matched['Longitude'],
                mode='markers',
                marker=dict(size=22, color='#f7797d'),
                name=f"📍 {search_district}",
                hovertext=matched['District'],
            ))
            st.success(f"📍 Found **{len(matched)}** district(s) matching '{search_district}'")
        else:
            st.warning(f"No district found matching '{search_district}'")

    st.plotly_chart(fig_map, width='stretch')
    st.caption(f"💡 Bubble size = **{primary}** · Color = **{secondary}**")

    # ── Top / Bottom 10 ───────────────────────────────────────────────────────
    st.markdown('<p class="section-header">🏆 District Rankings</p>', unsafe_allow_html=True)
    col_top, col_bot = st.columns(2)

    with col_top:
        top10 = view_df.nlargest(10, primary)[['District', 'State', primary]].reset_index(drop=True)
        fig_t = px.bar(top10, x=primary, y='District', orientation='h',
                       title=f"Top 10 · {primary}", color=primary,
                       color_continuous_scale='Blues', hover_data=['State'])
        fig_t.update_layout(**CHART_THEME, height=380, coloraxis_showscale=False,
                            margin=dict(l=0, r=10, t=40, b=10))
        fig_t.update_xaxes(gridcolor='#2d3561')
        st.plotly_chart(fig_t, width='stretch')

    with col_bot:
        bot10 = view_df.nsmallest(10, primary)[['District', 'State', primary]].reset_index(drop=True)
        fig_b = px.bar(bot10, x=primary, y='District', orientation='h',
                       title=f"Bottom 10 · {primary}", color=primary,
                       color_continuous_scale='Reds', hover_data=['State'])
        fig_b.update_layout(**CHART_THEME, height=380, coloraxis_showscale=False,
                            margin=dict(l=0, r=10, t=40, b=10))
        fig_b.update_xaxes(gridcolor='#2d3561')
        st.plotly_chart(fig_b, width='stretch')

    # ── Literacy Pie + Histogram ───────────────────────────────────────────────
    st.markdown('<p class="section-header">📉 Distributions</p>', unsafe_allow_html=True)
    col_pie, col_hist = st.columns(2)

    with col_pie:
        band = view_df['Literacy_Band'].value_counts().reset_index()
        band.columns = ['Band', 'Count']
        fig_pie = px.pie(band, names='Band', values='Count',
                         title='Literacy Band Distribution',
                         color_discrete_sequence=['#f7797d', '#fbd786', '#43e97b'],
                         hole=0.45)
        fig_pie.update_layout(**CHART_THEME, height=350, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_pie, width='stretch')

    with col_hist:
        fig_hist = px.histogram(view_df, x=secondary, nbins=25,
                                title=f'Distribution of {secondary}',
                                color_discrete_sequence=['#667eea'])
        fig_hist.update_layout(**CHART_THEME, height=350, margin=dict(l=0, r=10, t=40, b=10))
        fig_hist.update_xaxes(gridcolor='#2d3561')
        fig_hist.update_yaxes(gridcolor='#2d3561')
        st.plotly_chart(fig_hist, width='stretch')

    # ── Scatter Plot (metric vs metric) ──────────────────────────────────────
    st.markdown('<p class="section-header">🔵 Metric Scatter</p>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    x_axis = sc1.selectbox("X Axis", sorted(NUMERIC_COLS), index=3)
    y_axis = sc2.selectbox("Y Axis", sorted(NUMERIC_COLS), index=4)

    fig_sc = px.scatter(view_df, x=x_axis, y=y_axis, color='State',
                        hover_name='District', size='Population',
                        size_max=30, opacity=0.75,
                        title=f"{y_axis} vs {x_axis}",
                        trendline='ols')
    fig_sc.update_layout(**CHART_THEME, height=450, margin=dict(l=0, r=0, t=40, b=0))
    fig_sc.update_xaxes(gridcolor='#2d3561')
    fig_sc.update_yaxes(gridcolor='#2d3561')
    st.plotly_chart(fig_sc, width='stretch')

    # ── Correlation Heatmap ────────────────────────────────────────────────────
    st.markdown('<p class="section-header">🔗 Correlation Heatmap</p>', unsafe_allow_html=True)
    corr_cols = ['Population', 'literacy_rate', 'sex_ratio', 'Internet_Penetration', 'Households_with_Internet']
    corr = view_df[corr_cols].corr().round(2)
    fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu',
                         zmin=-1, zmax=1,
                         title='Pearson Correlation Between Census Metrics', aspect='auto')
    fig_heat.update_layout(**CHART_THEME, height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_heat, width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# COMPARE MODE
# ─────────────────────────────────────────────────────────────────────────────
else:
    df_a = df[df['State'] == state_a]
    df_b = df[df['State'] == state_b]

    st.markdown(f'<p class="section-header">⚔️ {state_a} vs {state_b}</p>', unsafe_allow_html=True)

    # KPI comparison cards
    metrics_map = {
        'Population': ('Total Population', 'M', True),
        'literacy_rate': ('Avg Literacy', '%', False),
        'sex_ratio': ('Avg Sex Ratio', '', False),
        'Internet_Penetration': ('Avg Internet %', '%', False),
    }
    cols = st.columns(len(metrics_map))
    for col, (metric, (label, unit, is_sum)) in zip(cols, metrics_map.items()):
        val_a = df_a[metric].sum() if is_sum else df_a[metric].mean()
        val_b = df_b[metric].sum() if is_sum else df_b[metric].mean()
        fmt_a = f"{val_a/1e6:.1f}M" if is_sum else f"{val_a:.1f}{unit}"
        fmt_b = f"{val_b/1e6:.1f}M" if is_sum else f"{val_b:.1f}{unit}"
        winner = state_a if val_a >= val_b else state_b
        with col:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="font-size:1.2rem;">{state_a}: {fmt_a}</div>
                <div class="kpi-value-b" style="font-size:1.2rem;">{state_b}: {fmt_b}</div>
                <div class="kpi-delta delta-up">🏆 {winner}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(" ")

    # Side-by-side maps
    st.markdown('<p class="section-header">🗺️ Side-by-Side Maps</p>', unsafe_allow_html=True)
    col_ma, col_mb = st.columns(2)
    for col, sname, sdf in [(col_ma, state_a, df_a), (col_mb, state_b, df_b)]:
        with col:
            st.markdown(f"**{sname}**")
            sdf_f = sdf[sdf[primary] > 0]
            fig_m = px.scatter_mapbox(
                sdf_f, lat="Latitude", lon="Longitude",
                size=primary, color=secondary,
                zoom=5, size_max=35, mapbox_style=map_style,
                height=420, hover_name='District',
                color_continuous_scale='Viridis',
            )
            fig_m.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                margin=dict(l=0, r=0, t=0, b=0),
                                coloraxis_showscale=False)
            st.plotly_chart(fig_m, width='stretch')

    # Grouped bar comparison
    st.markdown('<p class="section-header">📊 Top Districts Comparison</p>', unsafe_allow_html=True)
    compare_metric = st.selectbox("Metric to compare", sorted(NUMERIC_COLS))

    top_a = df_a.nlargest(10, compare_metric)[['District', compare_metric]].copy()
    top_a['State'] = state_a
    top_b = df_b.nlargest(10, compare_metric)[['District', compare_metric]].copy()
    top_b['State'] = state_b
    compare_df = pd.concat([top_a, top_b])

    fig_cmp = px.bar(compare_df, x='District', y=compare_metric, color='State',
                     barmode='group', title=f"Top 10 Districts · {compare_metric}",
                     color_discrete_map={state_a: '#667eea', state_b: '#f093fb'})
    fig_cmp.update_layout(**CHART_THEME, height=420, margin=dict(l=0, r=0, t=40, b=0))
    fig_cmp.update_xaxes(gridcolor='#2d3561', tickangle=-30)
    fig_cmp.update_yaxes(gridcolor='#2d3561')
    st.plotly_chart(fig_cmp, width='stretch')

    # Correlation heatmaps side by side
    st.markdown('<p class="section-header">🔗 Correlation Comparison</p>', unsafe_allow_html=True)
    corr_cols = ['Population', 'literacy_rate', 'sex_ratio', 'Internet_Penetration']
    ch1, ch2 = st.columns(2)
    for col, sname, sdf in [(ch1, state_a, df_a), (ch2, state_b, df_b)]:
        with col:
            corr = sdf[corr_cols].corr().round(2)
            fig_h = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu',
                              zmin=-1, zmax=1, title=f'{sname}', aspect='auto')
            fig_h.update_layout(**CHART_THEME, height=320,
                                margin=dict(l=0, r=0, t=40, b=0),
                                coloraxis_showscale=False)
            st.plotly_chart(fig_h, width='stretch')

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#4a5568;font-size:0.75rem;">'
    '🗺️ India Census Explorer &nbsp;|&nbsp; Data: Census of India 2011 &nbsp;|&nbsp; Built with Streamlit & Plotly'
    '</p>',
    unsafe_allow_html=True
)

