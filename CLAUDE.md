# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Install dependencies**: `uv sync` (uses uv package manager)
- **Run the application**: `streamlit run Home.py`
- **Run specific dashboard page**: `streamlit run pages/1_Google_Analytics_Dashboard.py` or `streamlit run pages/2_EC_Dashboard.py`

## Project Architecture

This is a Streamlit-based Business Intelligence application with dual focus on Google Analytics 4 (GA4) and E-commerce data analysis, both integrated with BigQuery.

### Core Structure

- **Entry Point**: `Home.py` - Main Streamlit application with basic BigQuery connectivity test
- **Pages**: Multi-page app with dashboard pages in `/pages/` directory
  - `pages/1_Google_Analytics_Dashboard.py` - GA4 analytics dashboard using modular components
  - `pages/2_EC_Dashboard.py` - E-commerce analytics dashboard with integrated AI Data Agent
- **Components**: Modular analysis components organized by domain
  - `/components/ga4/` - Google Analytics 4 analysis components
  - `/components/ec/` - E-commerce analysis components with integrated AI Data Agent
- **Data Layer**: BigQuery client and utilities in `/lib/`

### Key Components

**BigQuery Integration**:

- `lib/bigquery_client.py` - Main BigQuery client with Base64 encoded service account authentication
- `lib/tailwind_colors.py` - Color utilities for styling
- Authentication uses `SERVICE_ACCOUNT_JSON_BASE64` environment variable

**AI Data Agent** (`components/ec/data_agent/`):

- LangGraph-based agent using Google Gemini model
- `data_agent.py` - Main agent implementation
- `tools.py` - Tools for BigQuery SQL execution and Python code execution
- `bigquery_utils.py` - BigQuery utility functions
- `state.py` - Agent state management
- `utils.py` - General utility functions
- Interactive data analysis capabilities accessible via `data_agent_chat.py`
- Integrated into `pages/2_EC_Dashboard.py` as "AI Data Agent" page

**GA4 Analytics Components** (`components/ga4/`):

- Modular dashboard components for different GA4 analysis types
- Charts for user behavior, traffic patterns, device analysis, etc.
- Uses plotly for visualizations and pygwalker for exploratory data analysis

**E-commerce Analytics Components** (`components/ec/`):

- `utils.py` - Shared utility functions (date handling, input widgets)
- `data_queries.py` - BigQuery data fetching functions for e-commerce datasets
- `executive_overview.py` - Executive dashboard with KPIs and trend analysis
- `geo_logistics.py` - Geographic distribution and logistics analytics
- `product_merchandising.py` - Product performance and RFM analysis
- `inventory_supply.py` - Inventory management and supply chain metrics
- `sales_trends.py` - Daily sales and profit trend analysis
- `demographics.py` - Customer demographics and order status analysis
- `category_brand.py` - Product category and brand performance analysis

### Authentication Setup

The application uses Base64-encoded service account JSON for BigQuery authentication. Required BigQuery permissions:

- BigQuery Job User
- BigQuery Read Session User

Required environment variables (set in `.env` file):

- `SERVICE_ACCOUNT_JSON_BASE64` - Base64-encoded service account JSON for BigQuery
- `GOOGLE_API_KEY` - Google Gemini API key for AI Data Agent
- `OPENAI_API_KEY` - OpenAI API key (optional, for alternative LLM support)
- `E2B_API_KEY` - E2B API key for code execution environment

### Data Sources

**GA4 Analytics**:

- GA4 sample data from BigQuery public datasets
- Custom BigQuery datasets configured via `GOOGLE_CLOUD_PROJECT_ID` and `BIGQUERY_DATASET_NAME`

**E-commerce Analytics**:

- `bigquery-public-data.thelook_ecommerce` dataset
- Includes orders, users, products, inventory, and distribution center data
- Used for comprehensive e-commerce performance analysis

### Dependencies

Key dependencies managed via uv:

- `streamlit` - Web app framework
- `google-cloud-bigquery[pandas]` - BigQuery integration with pandas support
- `google-cloud-bigquery-storage` - BigQuery Storage API
- `langgraph` + `langchain-google-genai` - AI agent framework
- `google-genai` - Google Generative AI client
- `plotly` - Interactive visualizations
- `pygwalker` - Exploratory data analysis interface
- `pandas` + `polars` - Data manipulation libraries
- `e2b` + `e2b-code-interpreter` - Code execution environment
- `matplotlib` - Additional plotting capabilities

## Architecture Patterns

**Component Organization**: Both GA4 and EC dashboards follow a modular component pattern where each analysis type is a separate Python module with its own data fetching, processing, and visualization logic.

**Data Caching**: Extensive use of `@st.cache_data` decorators throughout components for performance optimization of BigQuery queries and expensive computations.

**Multi-page Navigation**: EC Dashboard uses a radio-based navigation system in the sidebar, while GA4 Dashboard uses Streamlit's native multi-page structure.

**State Management**: The AI Data Agent uses LangGraph's StateGraph for conversation state and MemorySaver for persistence across interactions.

## Lint and Format

- **Linting**: Use `uv run ruff check --extend-select I --fix .`
- **Formatting**: Use `uv run ruff format .`
