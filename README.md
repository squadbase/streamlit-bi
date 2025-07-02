# 📊 Streamlit Business Intelligence Dashboard

A comprehensive business intelligence application built with Streamlit, featuring Google Analytics 4 (GA4) analytics and E-commerce data analysis powered by BigQuery and AI-driven insights.

Made by [Squadbase](https://www.squadbase.dev/) - the platform for secure, scalable Streamlit deployments.

## ✨ Features

### 📈 Google Analytics 4 Dashboard

- **Real-time BigQuery Integration** - Direct connection to GA4 data in BigQuery
- **Interactive Data Exploration** - PyGWalker integration for drag-and-drop analysis
- **Comprehensive Analytics**:
  - User behavior and traffic patterns
  - Device and browser distribution analysis
  - Session anomaly detection with 7-day moving averages
  - Landing page performance metrics
  - Channel attribution and comparison
  - Geographic user distribution
  - New vs returning visitor analysis

### 🛒 E-commerce Analytics Dashboard

- **AI Data Agent** - Natural language queries using LangGraph + Google Gemini
- **Executive Overview** - Key performance indicators and trend analysis
- **Multi-dimensional Analysis**:
  - Geographic distribution and logistics insights
  - Product performance and RFM customer segmentation
  - Inventory management and supply chain metrics
  - Sales trends and profit analysis
  - Customer demographics and order patterns
  - Category and brand performance analysis

### 🤖 AI-Powered Features

- **Intelligent Data Agent** - Ask questions in natural language about your data
- **Automated SQL Generation** - Convert business questions to BigQuery queries
- **Code Execution Environment** - Run Python analysis code dynamically
- **Interactive Conversations** - Stateful dialogue for iterative data exploration

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud Platform account with BigQuery access
- Service account with BigQuery permissions
- API keys for Google Gemini, OpenAI (optional), and E2B

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd streamlit-business-intelligence
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:

   ```env
   SERVICE_ACCOUNT_JSON_BASE64=your_base64_encoded_service_account_json
   GOOGLE_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key  # Optional
   E2B_API_KEY=your_e2b_api_key
   ```

4. **Run the application**
   ```bash
   streamlit run Home.py
   ```

## 🚀 Deploy to Production with Squadbase

**Ready to share your dashboard with your team?** Squadbase makes secure deployment effortless:

### One-Click Deployment

1. Push your customized dashboard to a Git repository
2. Connect your repository to [Squadbase](https://www.squadbase.dev/)
3. Your dashboard is automatically deployed with enterprise-grade security

### Built-in Features

- **🔐 Member-Only Access** - Control who can access your dashboard
- **👥 User Management** - Role-based permissions and team management
- **🔄 Auto-Deploy** - Automatic updates when you push code changes
- **📊 Usage Analytics** - See how your team uses the dashboard
- **💬 Built-in Feedback** - Collect user feedback for continuous improvement
- **🔒 Enterprise Security** - SSL certificates, secure hosting, and compliance-ready

Perfect for internal company dashboards, client analytics, or any scenario where you need secure, controlled access to your data insights.

### BigQuery Setup

#### Required Permissions

Your service account needs the following BigQuery roles:

- **BigQuery Job User** - Execute queries
- **BigQuery Read Session User** - Read data efficiently

#### Service Account Setup

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Encode it to Base64: `base64 -i service-account-key.json`
4. Set the encoded string as `SERVICE_ACCOUNT_JSON_BASE64` in your `.env` file

## 🏗️ Architecture

### Project Structure

```
├── Home.py                          # Main application entry point
├── pages/                           # Streamlit pages
│   ├── 1_Google_Analytics_Dashboard.py
│   └── 2_EC_Dashboard.py
├── components/                      # Modular analysis components
│   ├── ga4/                        # GA4 analytics modules
│   │   ├── basic_metrics.py
│   │   ├── device_and_browser.py
│   │   ├── session_anomaly.py
│   │   └── ...
│   └── ec/                         # E-commerce analytics modules
│       ├── executive_overview.py
│       ├── product_merchandising.py
│       ├── data_agent/             # AI Data Agent
│       │   ├── data_agent.py
│       │   ├── tools.py
│       │   └── ...
│       └── ...
├── lib/                            # Core utilities
│   ├── bigquery_client.py          # BigQuery client with auth
│   └── tailwind_colors.py          # Styling utilities
└── notebook/                       # Jupyter notebooks for exploration
```

### Key Design Patterns

- **Modular Components** - Each analysis type is a separate, reusable module
- **Data Caching** - Extensive use of `@st.cache_data` for performance
- **Multi-page Navigation** - Organized dashboard sections
- **State Management** - LangGraph for AI agent conversation state

## 📊 Data Sources

### Google Analytics 4

- **Public Datasets**: `bigquery-public-data.google_analytics_sample`
- **Custom Datasets**: Configure via environment variables
- **Metrics**: Sessions, pageviews, users, conversions, and more

### E-commerce Data

- **Dataset**: `bigquery-public-data.thelook_ecommerce`
- **Tables**: Orders, users, products, inventory, distribution centers
- **Analysis**: Sales performance, customer behavior, inventory management

## 🔧 Usage

### Running Specific Dashboards

```bash
# GA4 Dashboard only
streamlit run pages/1_Google_Analytics_Dashboard.py

# E-commerce Dashboard only
streamlit run pages/2_EC_Dashboard.py
```

### AI Data Agent Usage

1. Navigate to the E-commerce Dashboard
2. Select "AI Data Agent" from the sidebar
3. Ask questions in natural language:
   - "What are the top 5 products by revenue this month?"
   - "Show me customer demographics by region"
   - "Analyze inventory levels for electronics category"

### Data Exploration

- Use PyGWalker interface in GA4 dashboard for drag-and-drop analysis
- Leverage cached queries for better performance
- Filter data using sidebar controls in each dashboard section

## 🚀 Deployment

### Squadbase Platform

Deploy securely to your organization using [Squadbase](https://www.squadbase.dev/):

- **Built-in Authentication** - User management and RBAC
- **Git-based CI/CD** - Automatic deployment pipeline
- **Security First** - Enterprise-grade security infrastructure
- **Runtime Monitoring** - Automatic logging and analytics
- **User Feedback** - Built-in comment system

### Self-Hosting

1. Set up environment variables on your server
2. Install dependencies: `uv sync`
3. Run with: `streamlit run Home.py --server.port 8501`
4. Configure reverse proxy (nginx/Apache) as needed

## 🛠️ Development

### Adding New Components

1. Create module in appropriate directory (`components/ga4/` or `components/ec/`)
2. Implement data fetching with `@st.cache_data` decorator
3. Add visualization using Plotly or Streamlit native components
4. Import and integrate in relevant dashboard page

### Extending AI Agent

1. Add new tools in `components/ec/data_agent/tools.py`
2. Update agent configuration in `data_agent.py`
3. Test with various natural language queries

### Linting and Formatting

- **Linting**: Use `uv run ruff check --extend-select I --fix .`
- **Formatting**: Use `uv run ruff format .`

## 📝 Dependencies

### Core Framework

- **streamlit** - Web application framework
- **uv** - Fast Python package installer and resolver

### Data & Analytics

- **google-cloud-bigquery[pandas]** - BigQuery integration
- **pandas**, **polars** - Data manipulation
- **plotly** - Interactive visualizations
- **pygwalker** - Exploratory data analysis

### AI & LLM

- **langgraph**, **langchain-google-genai** - AI agent framework
- **google-genai** - Google Gemini API client
- **openai** - OpenAI API client (optional)
- **e2b**, **e2b-code-interpreter** - Code execution environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- Create an issue for bug reports or feature requests
- Check the documentation in `CLAUDE.md` for development guidance
- Review example notebooks in the `notebook/` directory

---

Built with ❤️ using Streamlit, BigQuery, Google Gemini, Claude Code, and Squadbase.
