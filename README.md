# 📊 SalesIQ: Executive AI Business Intelligence Dashboard

## 🎯 Objective

This project is the **Business Intelligence Dashboard with AI Insights** build: a Python/Streamlit application that analyzes sales and business data, surfaces KPI and trend analytics, and generates AI-based insights to support business decision-making — the Python/AI-insights layer of the wider BI assignment (alongside the Power BI dashboard and SQL components described below).

Traditional dashboards tell you *what* happened; this dashboard tells you *why* it happened and *what it means*. SalesIQ transforms raw retail data into an interactive, context-aware analytics pipeline, and integrates a Large Language Model (LLM) directly into the UI to generate natural-language executive summaries and strategic recommendations based on whatever filters the user has active.

## ✨ Key Features

Mapped directly to the assignment's expected features:

| Brief Requirement | Implementation |
|---|---|
| Import data from Excel/CSV/SQL | Loads and caches CSV data via Pandas (`@st.cache_data`); schema-agnostic, so it degrades gracefully instead of crashing if expected columns are missing |
| Data cleaning & preprocessing | Automatic date parsing, null-handling for filters/aggregations, and safe fallbacks when optional columns (Customer, Quantity, Discount) aren't present |
| KPI dashboard | Four headline KPIs — Revenue, Profit, Profit Margin, Orders — with **Year-over-Year** deltas instead of Month-over-Month, since this dataset is highly seasonal and MoM comparisons mostly just measure the holiday-season spike rather than real performance change |
| Sales and customer analytics | Dedicated Customer Analytics tab: top customers by revenue, revenue by segment, quantity sold, discount rate |
| Trend analysis | Monthly revenue trend (full timeline) **plus** a Year-over-Year seasonal overlay chart that lines every year up on the same Jan–Dec axis, so real growth is visible separately from seasonality |
| AI-generated business recommendations | Google Gemini API integration generates an on-demand executive narrative from the live filtered dataset; a rule-based Executive Summary is also always visible with zero API calls needed |
| Export reports | CSV export of the currently filtered dataset from the Raw Data tab |

**Additional engineering highlights:**

* **🤖 Context-Aware AI Insights** — reads the live, filtered data and generates summaries that flag vulnerable profit margins and highlight growth metrics.
* **📈 Dynamic Drill-Down Visualizations** — built with Altair; filtering by Category reveals a Segment breakdown, and drilling further reveals Sub-Category, with a consistent color scale maintained across every view.
* **⚡ Resilient Data Pipeline** — Python + Pandas with `@st.cache_data`, schema-agnostic so the app adapts to missing columns instead of crashing.
* **🎨 Enterprise UI/UX** — custom CSS, a clear visual hierarchy (4 primary KPIs vs. secondary metrics), and a tabbed interface that prioritizes actionable intelligence over visual clutter.

## 🛠️ Tech Stack

**This repository (Python AI-insights app):**
* **Web Framework:** Streamlit
* **Data Processing:** Python 3.11, Pandas
* **Data Visualization:** Altair
* **AI Integration:** Google Gemini 2.5 Flash API
* **Version Control:** Git & GitHub

**Wider BI project stack (per assignment brief):**
* SQL — *[add: where SQL is used, e.g. data extraction/cleaning scripts, link file/folder]*
* Power BI — *[add: link to .pbix file or published Power BI report]*
* Excel — *[add: if Excel is used for raw data intake or export, note it here]*

> 📝 **Note for reviewers:** the assignment brief calls for a full stack including SQL and Power BI. Those components should be added to this repo (or linked here) alongside this Streamlit app — see the Deliverables Checklist below for what's currently complete.

## 📂 Dataset Context

* **Source:** [Superstore Sales Dataset — Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
* **Context:** Simulated US Retail Co. sales data spanning 4 years, containing 9,994 rows and 21 columns (Sales, Profit, Quantity, Customer & Product segments).

## ⚙️ Local Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/alok263-commits/power-bi-dashboard-ai-insights.git
cd power-bi-dashboard-ai-insights
```

**2. Install dependencies**

Ensure you have Python 3.11+ installed, then install the required packages:

```bash
pip install streamlit pandas altair google-generativeai python-dotenv
```

**3. Configure your environment variables**

Create a `.env` file in the root directory and securely add your Gemini API key:

```
GEMINI_API_KEY="your_api_key_here"
```

**4. Launch the application**

```bash
streamlit run app.py
```


## 👤 Author

Alok Verma
