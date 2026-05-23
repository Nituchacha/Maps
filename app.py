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
    background: linear-gradient(180deg, #161a2b 0%, #0f1117 100%);
    border-right: 1px solid #242b4d;
}

.hero-header {
    background: linear-gradient(135deg, #191c33 0%, #22294a 50%, #161a2b 100%);
    border: 1px solid #2f386b;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #788cde, #aa89e3, #f5a9e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero-subtitle { color: #8892b0; font-size: 0.95rem; margin-top: 0.3rem; }

.kpi-card {
    background: linear-gradient(135deg, #191c33 0%, #22294a 100%);
    border: 1px solid #2f386b;
    border-radius: 10px;
    padding: 1rem 0.8rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 0.5rem;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(120, 140, 222, 0.2); }
.kpi-value { font-size: 1.6rem; font-weight: 700; color: #788cde; margin: 0.2rem 0; }
.kpi-value-b { font-size: 1.6rem; font-weight: 700; color: #aa89e3; margin: 0.2rem 0; }
.kpi-label { font-size: 0.72rem; color: #a8b2d1; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; }
.kpi-delta { font-size: 0.7rem; font-weight: 500; margin-top: 0.2rem; }
.delta-up { color: #43e97b; }
.delta-down { color: #f7797d; }

.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #e2e8f0;
    border-left: 4px solid #788cde;
    padding-left: 0.6rem;
    margin: 1.2rem 0 0.8rem 0;
}

.explanation-box {
    background-color: #16192b;
    border-left: 3px solid #6366f1;
    padding: 0.8rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.4;
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #788cde, #aa89e3) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
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

# Naming lookup for cleaner descriptions
COLUMN_LABELS = {
    'Population': '👤 Total Population',
    'Households_with_Internet': '💻 Internet Households',
    'sex_ratio': '⚧️ Sex Ratio (Females per 100 Males)',
    'literacy_rate': '📖 Literacy Rate (%)',
    'Internet_Penetration': '📶 Internet Penetration (%)'
}

NUMERIC_COLS = list(COLUMN_LABELS.keys())
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
    paper_bgcolor='rgba(25, 28, 51, 0.8)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#cbd5e1', family='Inter'),
    title_font=dict(color='#e2e8f0', size=13),
)

list_of_states = sorted(df['State'].unique().tolist())
list_of_states_with_overall = ['Overall India'] + list_of_states

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ India Census Settings")
    st.markdown("Adjust the options below to filter the dashboard views:")

    mode = st.radio("Dashboard View Mode", ["🔍 Single State Explorer", "⚔️ Compare States"], horizontal=False)
    st.markdown("---")

    if mode == "🔍 Single State Explorer":
        selected_state = st.selectbox("Select Region", list_of_states_with_overall)
    else:
        state_a = st.selectbox("State A (First)", list_of_states, index=0)
        state_b = st.selectbox("State B (Second)", list_of_states, index=5 if len(list_of_states) > 5 else 1)

    st.markdown("#### Map Customization")
    primary_key = st.selectbox(
        "Bubble Size Indicates",
        NUMERIC_COLS,
        index=0,
        format_func=lambda x: COLUMN_LABELS[x]
    )
    secondary_key = st.selectbox(
        "Bubble Color Indicates",
        NUMERIC_COLS,
        index=3,
        format_func=lambda x: COLUMN_LABELS[x]
    )
    map_style_label = st.selectbox("Map Theme", list(MAP_STYLES.keys()))
    map_style = MAP_STYLES[map_style_label]

    st.markdown("---")
    search_district = st.text_input("🔍 Highlight Specific District", placeholder="e.g. Jaipur")

    st.markdown("---")
    if mode == "🔍 Single State Explorer":
        dl_df = df if selected_state == 'Overall India' else df[df['State'] == selected_state]
    else:
        dl_df = df[df['State'].isin([state_a, state_b])]

    st.download_button(
        "⬇️ Download Current Data (CSV)",
        data=dl_df.to_csv(index=False),
        file_name="india_census_filtered.csv",
        mime="text/csv"
    )
    st.markdown("---")
    st.caption("Data Source: 2011 Census of India")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <p class="hero-title">🗺️ India Census Explorer</p>
    <p class="hero-subtitle">An elegant dashboard simplifying district-level socio-economic patterns across India</p>
</div>
""", unsafe_allow_html=True)

# Collapsible User Friendly Explanation to remove ambiguity
with st.expander("📖 Welcome! How do I read this dashboard?"):
    st.markdown("""
    This app visualizes key indicators from the **2011 Census of India** at a district level:
    - **Total Population**: Total number of residents.
    - **Literacy Rate**: Percentage of the population who can read and write.
    - **Sex Ratio**: Number of female residents per 100 male residents (values above 100 represent more women than men).
    - **Internet Penetration**: The percentage of the population living in households with active internet.
    
    ### 💡 Quick Tips:
    - Use the **tabs below** to switch between the interactive map, rankings, and statistical analyses without getting lost.
    - In the **Map Explorer**, the **size of each circle** represents one metric (e.g. Population) while the **color** represents another (e.g. Literacy Rate). 
    - Hover over any circle on the map to see details about that specific district.
    - Switch to **Compare States** in the sidebar to view two states head-to-head.
    """)

# ─────────────────────────────────────────────────────────────────────────────
# EXPLORE MODE
# ─────────────────────────────────────────────────────────────────────────────
if mode == "🔍 Single State Explorer":
    view_df = df if selected_state == 'Overall India' else df[df['State'] == selected_state]

    # Clean, intuitive tabs
    tab_map, tab_rankings, tab_distributions = st.tabs([
        "🗺️ Map Explorer & Key Metrics", 
        "🏆 District Rankings (Top & Bottom)", 
        "📈 Advanced Distributions & Correlations"
    ])

    # ── TAB 1: MAP EXPLORER ──
    with tab_map:
        # Key Metrics KPI Cards
        st.markdown('<p class="section-header">📊 Summary Stats for Selected Region</p>', unsafe_allow_html=True)
        
        total_pop   = view_df['Population'].sum()
        n_districts = len(view_df)
        avg_lit     = view_df['literacy_rate'].mean()
        avg_sex     = view_df['sex_ratio'].mean()
        avg_int     = view_df['Internet_Penetration'].mean()

        def delta_tag(val, unit=""):
            arrow, cls = ("▲", "delta-up") if val >= 0 else ("▼", "delta-down")
            return f'<span class="kpi-delta {cls}">{arrow} {abs(val):.1f}{unit} vs national average</span>'

        c1, c2, c3, c4, c5 = st.columns(5)
        for col, value, label, delta in [
            (c1, f"{total_pop/1e6:.2f}M", "Total Population", ""),
            (c2, f"{n_districts}",        "Total Districts",        ""),
            (c3, f"{avg_lit:.1f}%",       "Average Literacy",     delta_tag(avg_lit - NAT_AVG['literacy_rate'], "%")),
            (c4, f"{avg_sex:.0f}",        "Average Sex Ratio",    delta_tag(avg_sex - NAT_AVG['sex_ratio'])),
            (c5, f"{avg_int:.2f}%",       "Avg Internet Penetration", delta_tag(avg_int - NAT_AVG['Internet_Penetration'], "%")),
        ]:
            with col:
                st.markdown(f"""<div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    {delta}
                </div>""", unsafe_allow_html=True)

        st.markdown('<p class="section-header">🗺️ Interactive Map</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="explanation-box">
            This map displays districts as circles. 
            The <b>size</b> of the bubble represents <b>{COLUMN_LABELS[primary_key]}</b>, 
            and the <b>color</b> represents <b>{COLUMN_LABELS[secondary_key]}</b>. 
            Use scroll/pinch to zoom and drag to move around.
        </div>
        """, unsafe_allow_html=True)

        map_df = view_df[view_df[primary_key] > 0].copy()
        zoom   = 4 if selected_state == 'Overall India' else 6

        fig_map = px.scatter_mapbox(
            map_df,
            lat="Latitude", lon="Longitude",
            size=primary_key, color=secondary_key,
            zoom=zoom, size_max=35,
            mapbox_style=map_style,
            height=500,
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
                    marker=dict(size=20, color='#ff3838'),
                    name=f"📍 Highlighted: {search_district}",
                    hovertext=matched['District'],
                ))
                st.success(f"📍 Highlighted **{len(matched)}** district(s) matching '{search_district}' on the map.")
            else:
                st.warning(f"No district found matching '{search_district}'")

        st.plotly_chart(fig_map, width='stretch')

    # ── TAB 2: RANKINGS ──
    with tab_rankings:
        st.markdown('<p class="section-header">🏆 Highs and Lows</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="explanation-box">
            Compare the top 10 highest-scoring and bottom 10 lowest-scoring districts in this region for 
            <b>{COLUMN_LABELS[primary_key]}</b>. This is useful for identifying regions needing development.
        </div>
        """, unsafe_allow_html=True)
        
        col_top, col_bot = st.columns(2)

        with col_top:
            top10 = view_df.nlargest(10, primary_key)[['District', 'State', primary_key]].reset_index(drop=True)
            fig_t = px.bar(top10, x=primary_key, y='District', orientation='h',
                           title=f"Top 10 Highest Districts ({primary_key.replace('_',' ').title()})", color=primary_key,
                           color_continuous_scale='Blues', hover_data=['State'])
            fig_t.update_layout(**CHART_THEME, height=350, coloraxis_showscale=False,
                                margin=dict(l=0, r=10, t=40, b=10))
            fig_t.update_xaxes(gridcolor='#2d3561')
            st.plotly_chart(fig_t, width='stretch')

        with col_bot:
            bot10 = view_df.nsmallest(10, primary_key)[['District', 'State', primary_key]].reset_index(drop=True)
            fig_b = px.bar(bot10, x=primary_key, y='District', orientation='h',
                           title=f"Bottom 10 Lowest Districts ({primary_key.replace('_',' ').title()})", color=primary_key,
                           color_continuous_scale='Reds', hover_data=['State'])
            fig_b.update_layout(**CHART_THEME, height=350, coloraxis_showscale=False,
                                margin=dict(l=0, r=10, t=40, b=10))
            fig_b.update_xaxes(gridcolor='#2d3561')
            st.plotly_chart(fig_b, width='stretch')

    # ── TAB 3: ANALYTICS & DISTRIBUTIONS ──
    with tab_distributions:
        st.markdown('<p class="section-header">📉 Distribution of the Census Metrics</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explanation-box">
            <b>Left Chart:</b> Displays what percentage of districts fall into low, medium, or high literacy bands.<br>
            <b>Right Chart:</b> A histogram showing how common different ranges of values are for your selected secondary metric.
        </div>
        """, unsafe_allow_html=True)
        
        col_pie, col_hist = st.columns(2)

        with col_pie:
            band = view_df['Literacy_Band'].value_counts().reset_index()
            band.columns = ['Band', 'Count']
            fig_pie = px.pie(band, names='Band', values='Count',
                             title='Literacy Bands Distribution',
                             color_discrete_sequence=['#f7797d', '#fbd786', '#43e97b'],
                             hole=0.45)
            fig_pie.update_layout(**CHART_THEME, height=320, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_pie, width='stretch')

        with col_hist:
            fig_hist = px.histogram(view_df, x=secondary_key, nbins=20,
                                    title=f'How values are spread out for: {secondary_key.replace("_"," ").title()}',
                                    color_discrete_sequence=['#788cde'])
            fig_hist.update_layout(**CHART_THEME, height=320, margin=dict(l=0, r=10, t=40, b=10))
            fig_hist.update_xaxes(gridcolor='#242b4d')
            fig_hist.update_yaxes(gridcolor='#242b4d')
            st.plotly_chart(fig_hist, width='stretch')

        st.markdown('<p class="section-header">🔵 Correlation & Relationships</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explanation-box">
            <b>Scatter Relationship Plot:</b> Select any two metrics for the X and Y axes to see if they follow a pattern (e.g. Do districts with higher literacy also have better internet access?). The diagonal trendline highlights the general direction of the relationship.<br>
            <b>Pearson Correlation Matrix:</b> Values close to 1 mean a strong positive relationship, values close to -1 mean a strong negative relationship, and values close to 0 mean no relationship.
        </div>
        """, unsafe_allow_html=True)
        
        sc1, sc2 = st.columns(2)
        with sc1:
            x_axis = st.selectbox("Select X Axis (Predictor)", sorted(NUMERIC_COLS), index=3, format_func=lambda x: COLUMN_LABELS[x], key="sc_x")
        with sc2:
            y_axis = st.selectbox("Select Y Axis (Response)", sorted(NUMERIC_COLS), index=4, format_func=lambda x: COLUMN_LABELS[x], key="sc_y")

        col_scatter, col_heatmap = st.columns(2)
        
        with col_scatter:
            fig_sc = px.scatter(view_df, x=x_axis, y=y_axis, color='State' if selected_state == 'Overall India' else None,
                                hover_name='District', size='Population',
                                size_max=25, opacity=0.75,
                                title=f"Pattern: {y_axis.replace('_',' ').title()} vs {x_axis.replace('_',' ').title()}",
                                trendline='ols', color_discrete_sequence=['#aa89e3'])
            fig_sc.update_layout(**CHART_THEME, height=380, margin=dict(l=0, r=0, t=40, b=0))
            fig_sc.update_xaxes(gridcolor='#242b4d')
            fig_sc.update_yaxes(gridcolor='#242b4d')
            st.plotly_chart(fig_sc, width='stretch')

        with col_heatmap:
            corr_cols = ['Population', 'literacy_rate', 'sex_ratio', 'Internet_Penetration', 'Households_with_Internet']
            corr = view_df[corr_cols].corr().round(2)
            # rename indexes for non-technical users
            corr.index = [c.replace('_', ' ').title() for c in corr.index]
            corr.columns = [c.replace('_', ' ').title() for c in corr.columns]
            
            fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu',
                                 zmin=-1, zmax=1,
                                 title='Strength of Relationship Between Indicators', aspect='auto')
            fig_heat.update_layout(**CHART_THEME, height=380, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_heat, width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# COMPARE MODE
# ─────────────────────────────────────────────────────────────────────────────
else:
    df_a = df[df['State'] == state_a]
    df_b = df[df['State'] == state_b]

    # Clean, intuitive tabs for comparison
    tab_comp_stats, tab_comp_maps, tab_comp_corr = st.tabs([
        "⚔️ Comparison Summary & Rankings", 
        "🗺️ Side-by-Side Map Visualizations", 
        "🔗 Correlation Relationships"
    ])

    # ── TAB 1: COMPARISON STATS & RANKINGS ──
    with tab_comp_stats:
        st.markdown(f'<p class="section-header">📊 Head-to-Head Comparison: {state_a} vs {state_b}</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explanation-box">
            A quick comparison of key statistics for the two selected states. The state with the higher value for each metric is awarded a trophy.
        </div>
        """, unsafe_allow_html=True)

        metrics_map = {
            'Population': ('Total Population', 'M', True),
            'literacy_rate': ('Avg Literacy Rate', '%', False),
            'sex_ratio': ('Avg Sex Ratio', '', False),
            'Internet_Penetration': ('Avg Internet Penetration', '%', False),
        }
        cols = st.columns(len(metrics_map))
        for col, (metric, (label, unit, is_sum)) in zip(cols, metrics_map.items()):
            val_a = df_a[metric].sum() if is_sum else df_a[metric].mean()
            val_b = df_b[metric].sum() if is_sum else df_b[metric].mean()
            fmt_a = f"{val_a/1e6:.2f}M" if is_sum else f"{val_a:.1f}{unit}"
            fmt_b = f"{val_b/1e6:.2f}M" if is_sum else f"{val_b:.1f}{unit}"
            winner = state_a if val_a >= val_b else state_b
            with col:
                st.markdown(f"""<div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value" style="font-size:1.15rem; color:#788cde;">{state_a}: {fmt_a}</div>
                    <div class="kpi-value-b" style="font-size:1.15rem; color:#aa89e3;">{state_b}: {fmt_b}</div>
                    <div class="kpi-delta delta-up">🏆 Higher: {winner}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<p class="section-header">📊 Top Districts Comparison</p>', unsafe_allow_html=True)
        compare_metric = st.selectbox(
            "Select Metric to Compare Districts",
            NUMERIC_COLS,
            format_func=lambda x: COLUMN_LABELS[x]
        )

        top_a = df_a.nlargest(10, compare_metric)[['District', compare_metric]].copy()
        top_a['State'] = state_a
        top_b = df_b.nlargest(10, compare_metric)[['District', compare_metric]].copy()
        top_b['State'] = state_b
        compare_df = pd.concat([top_a, top_b])

        fig_cmp = px.bar(compare_df, x='District', y=compare_metric, color='State',
                         barmode='group', title=f"Top 10 Districts Comparison ({compare_metric.replace('_',' ').title()})",
                         color_discrete_map={state_a: '#788cde', state_b: '#aa89e3'})
        fig_cmp.update_layout(**CHART_THEME, height=380, margin=dict(l=0, r=0, t=40, b=0))
        fig_cmp.update_xaxes(gridcolor='#242b4d', tickangle=-25)
        fig_cmp.update_yaxes(gridcolor='#242b4d')
        st.plotly_chart(fig_cmp, width='stretch')

    # ── TAB 2: SIDE-BY-SIDE MAPS ──
    with tab_comp_maps:
        st.markdown('<p class="section-header">🗺️ Regional Side-by-Side Map View</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="explanation-box">
            Compare the geographic patterns of both states side by side. 
            Bubble Size: <b>{COLUMN_LABELS[primary_key]}</b> | Bubble Color: <b>{COLUMN_LABELS[secondary_key]}</b>
        </div>
        """, unsafe_allow_html=True)

        col_ma, col_mb = st.columns(2)
        for col, sname, sdf in [(col_ma, state_a, df_a), (col_mb, state_b, df_b)]:
            with col:
                st.markdown(f"##### {sname}")
                sdf_f = sdf[sdf[primary_key] > 0]
                fig_m = px.scatter_mapbox(
                    sdf_f, lat="Latitude", lon="Longitude",
                    size=primary_key, color=secondary_key,
                    zoom=5, size_max=30, mapbox_style=map_style,
                    height=380, hover_name='District',
                    color_continuous_scale='Viridis',
                )
                fig_m.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    coloraxis_showscale=False)
                st.plotly_chart(fig_m, width='stretch')

    # ── TAB 3: CORRELATION COMPARISON ──
    with tab_comp_corr:
        st.markdown('<p class="section-header">🔗 Relationship Comparison (Correlation Heatmaps)</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explanation-box">
            Compare how different indicators relate to each other in State A vs State B. 
            For instance, check if Internet Penetration shows a stronger link with Literacy Rate in one state compared to the other.
        </div>
        """, unsafe_allow_html=True)

        corr_cols = ['Population', 'literacy_rate', 'sex_ratio', 'Internet_Penetration']
        ch1, ch2 = st.columns(2)
        for col, sname, sdf in [(ch1, state_a, df_a), (ch2, state_b, df_b)]:
            with col:
                corr = sdf[corr_cols].corr().round(2)
                corr.index = [c.replace('_', ' ').title() for c in corr.index]
                corr.columns = [c.replace('_', ' ').title() for c in corr.columns]
                
                fig_h = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu',
                                  zmin=-1, zmax=1, title=f'Indicators Link strength inside: {sname}', aspect='auto')
                fig_h.update_layout(**CHART_THEME, height=300,
                                    margin=dict(l=0, r=0, t=40, b=0),
                                    coloraxis_showscale=False)
                st.plotly_chart(fig_h, width='stretch')

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#6b7280;font-size:0.75rem;">'
    '🗺️ India Census Explorer &nbsp;|&nbsp; Data: Census of India 2011 &nbsp;|&nbsp; Designed with Streamlit & Plotly'
    '</p>',
    unsafe_allow_html=True
)
