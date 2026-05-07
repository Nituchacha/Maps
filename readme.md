# 🗺️ India Census Explorer

> An interactive, district-level socio-economic data visualization dashboard built with **Streamlit** and **Plotly** — powered by the **Census of India 2011** dataset.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-6.x-purple?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 Overview

**India Census Explorer** is a full-featured geospatial analytics dashboard that lets you explore and compare socio-economic indicators — Population, Literacy Rate, Sex Ratio, and Internet Penetration — across every district and state in India.

The app features two modes:
- **🔍 Explore Mode** — Deep-dive into any state or view all of India at once
- **⚔️ Compare Mode** — Select two states and compare them side-by-side

---

## 🚀 Live Features

### 🔍 Explore Mode

| Feature | Description |
|---|---|
| **KPI Summary Cards** | Total Population, District count, Avg Literacy, Avg Sex Ratio, Internet Penetration — each with ▲▼ delta vs national average |
| **Interactive Mapbox Map** | Scatter map with configurable bubble size & color. Reactive — updates instantly on sidebar change |
| **District Highlight Search** | Type any district name to pin and highlight it on the map |
| **Map Style Toggle** | Switch between Dark, Light, Streets, and Terrain map styles |
| **Top / Bottom 10 Bar Charts** | Horizontal bar rankings of districts by any selected metric |
| **Literacy Band Pie Chart** | Districts grouped into Low / Medium / High literacy bands |
| **Metric Histogram** | Distribution of any metric across all districts |
| **Metric Scatter Plot** | Plot any two metrics against each other with an OLS trendline |
| **Correlation Heatmap** | Pearson correlation matrix across all census metrics |
| **Download CSV** | Export currently filtered data as a CSV file |

### ⚔️ Compare Mode

| Feature | Description |
|---|---|
| **Side-by-Side KPI Cards** | Compare key metrics between two states with a winner badge |
| **Dual Mapbox Maps** | View both states' district maps simultaneously |
| **Grouped Bar Chart** | Top 10 districts of each state compared on any metric |
| **Dual Correlation Heatmaps** | View and compare metric correlations for each state |

---

## 📊 Dataset

**File:** `india.csv`  
**Source:** Census of India 2011  
**Coverage:** ~640 districts across 35 states and Union Territories

### Columns

| Column | Type | Description |
|---|---|---|
| `State` | String | State or Union Territory name |
| `District` | String | District name |
| `Latitude` | Float | Geographic latitude of district centroid |
| `Longitude` | Float | Geographic longitude of district centroid |
| `District code` | Integer | Official Census district code |
| `Population` | Integer | Total population of the district |
| `Households_with_Internet` | Integer | Number of households with internet access |
| `sex_ratio` | Float | Number of females per 100 males |
| `literacy_rate` | Float | Percentage of literate population |

### Computed Columns (added by the app)

| Column | Formula |
|---|---|
| `Internet_Penetration` | `(Households_with_Internet / Population) × 100` |
| `Literacy_Band` | Categorized as Low (<55%), Medium (55–70%), High (>70%) |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [Python 3.8+](https://python.org) | Core language |
| [Streamlit](https://streamlit.io) | Web app framework |
| [Plotly Express](https://plotly.com/python/plotly-express/) | All charts and maps |
| [Pandas](https://pandas.pydata.org) | Data loading and processing |
| [Statsmodels](https://www.statsmodels.org) | OLS trendline in scatter plots |

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/india-census-explorer.git
cd india-census-explorer
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit pandas plotly statsmodels
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
india-census-explorer/
│
├── app.py          # Main Streamlit application
├── india.csv       # Census of India 2011 dataset
└── README.md       # Project documentation
```

---

## 🎮 How to Use

### Sidebar Controls

| Control | Description |
|---|---|
| **Dashboard Mode** | Switch between Explore and Compare modes |
| **Select State / UT** | Filter data to a specific state or view all India |
| **Primary Metric** | The metric that controls bubble **size** on the map |
| **Secondary Metric** | The metric that controls bubble **color** on the map |
| **Map Style** | Toggle between Dark, Light, Streets, Terrain |
| **Highlight District** | Type a district name to mark it on the map |
| **Download Filtered Data** | Export the current view as a `.csv` file |

### Explore Mode Walkthrough

1. Select a **State** from the sidebar (or keep "Overall India")
2. Choose **Primary** and **Secondary** metrics
3. The **map**, **KPI cards**, and all **charts** update instantly
4. Type in the search box to **highlight a specific district** on the map
5. Scroll down to see rankings, distributions, scatter plots, and correlation heatmap

### Compare Mode Walkthrough

1. Switch mode to **⚔️ Compare States**
2. Select **State A** and **State B**
3. View side-by-side KPI cards, maps, grouped bar charts, and correlation heatmaps

---

## 📸 Screenshots

> Run the app locally to see the full interactive experience.

| Section | Description |
|---|---|
| Hero Header | Gradient title with app description |
| KPI Cards | 5 metric cards with national average deltas |
| District Map | Mapbox scatter with configurable parameters |
| Bar Charts | Top/Bottom 10 districts by selected metric |
| Pie Chart | Literacy band distribution |
| Scatter Plot | Cross-metric analysis with OLS trendline |
| Heatmap | Pearson correlation across all metrics |
| Compare View | Dual maps + grouped bars for two states |

---

## 📈 Key Insights from the Data

- **Kerala** leads in literacy rate (83–89%) and has the highest sex ratio (110+ in some districts)
- **Bihar and Uttar Pradesh** have the lowest literacy rates (40–55%) and the most districts
- **Thane, Pune, and Mumbai** (Maharashtra) are the most internet-connected districts
- **Internet Penetration** strongly correlates with **Literacy Rate** across India
- **Goa** has the highest literacy for a smaller state; **Rajasthan** shows wide disparity between districts

---

## 🔧 Potential Improvements

- [ ] Add GeoJSON choropleth boundaries for state-level mapping
- [ ] Add year-over-year comparison if multi-census data is available
- [ ] Integrate live data from the Census API
- [ ] Add a mobile-responsive layout
- [ ] Deploy to Streamlit Cloud / Heroku

---

## 👤 Author

**Your Name**  
📧 your.email@example.com  
🔗 [LinkedIn](https://linkedin.com/in/your-profile) | [GitHub](https://github.com/your-username)

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- Data: [Census of India 2011](https://censusindia.gov.in/)
- Map tiles: [CARTO](https://carto.com/), [Stamen Design](http://stamen.com/), [OpenStreetMap](https://www.openstreetmap.org/)
- Built with ❤️ using [Streamlit](https://streamlit.io) and [Plotly](https://plotly.com)
