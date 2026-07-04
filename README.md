# 📊 SalesIQ: Executive AI Business Intelligence Dashboard

## 🚀 Overview
Traditional dashboards tell you *what* happened; this dashboard tells you *why* it happened and *what it means*. 

SalesIQ is an end-to-end, full-stack Business Intelligence application designed to bridge the gap between static data visualization and actionable strategic insights. Built for C-suite executives and sales directors, this tool transforms raw retail data into an interactive, context-aware analytics pipeline. By integrating a Large Language Model (LLM) directly into the UI, the dashboard instantly generates natural-language executive summaries and strategic recommendations based on the user's active filters.

## ✨ Key Features
* **🤖 Context-Aware AI Insights:** Integrates the Google Gemini API to dynamically read live, filtered data and instantly generate executive summaries, flagging vulnerable profit margins and highlighting key growth metrics.
* **📈 Dynamic Drill-Down Visualizations:** Engineered with Altair to provide a multi-level drill-down charting engine. Filtering by Category seamlessly reveals Customer Segment breakdowns, maintaining strict color-mapping psychology across all views.
* **⚡ Resilient Data Pipeline:** Utilizes Python and Pandas with aggressive `@st.cache_data` memory management to ensure lightning-fast load times and a schema-agnostic architecture that adapts to missing data columns without crashing.
* **🎨 Enterprise UI/UX:** Features a custom CSS frontend with interactive metric cards, automated Month-over-Month (MoM) growth calculations, and a clean, tabbed interface to prioritize actionable intelligence over visual clutter.

## 🛠️ Tech Stack
* **Web Framework:** Streamlit
* **Data Processing:** Python 3.11, Pandas
* **Data Visualization:** Altair
* **AI Integration:** Google Gemini 2.5 Flash API
* **Version Control:** Git & GitHub

## 📂 Dataset Context
* **Source:** [Superstore Sales Dataset — Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
* **Context:** Simulated US Retail Co. sales data spanning 4 years, containing 9,994 rows and 21 columns (Sales, Profit, Quantity, Customer & Product segments).

## ⚙️ Local Installation & Setup
To run this application locally on your machine, follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/alok263-commits/power-bi-dashboard-ai-insights.git](https://github.com/yourusername/power-bi-dashboard-ai-insights.git)
cd power-bi-dashboard-ai-insights
