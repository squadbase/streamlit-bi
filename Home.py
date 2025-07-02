import os

import streamlit as st

st.set_page_config(
    page_title="Business Intelligence Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Streamlit BI Dashboard Demo")
st.caption("Feature-rich business intelligence sample application with Streamlit")

st.markdown("""
## 🎯 Features

### 📈 GA4 Analytics Dashboard
- **BigQuery Integration**: Connect and query large datasets in real-time
- **PyGWalker EDA**: Drag-and-drop exploratory data analysis
- **Interactive Visualizations**: Dynamic charts with Plotly
- **Multi-page Architecture**: Modular component design patterns

### 🛒 E-commerce BI Dashboard
- **AI Data Agent**: Natural language queries with LangGraph + Gemini
- **Multi-tab Navigation**: Organized dashboard sections with state management
- **Dynamic Filtering**: Real-time data filtering with Streamlit widgets
- **Advanced Charts**: Complex visualizations (geographic maps, heatmaps, etc.)

## 🚀 Quick Setup
Create a `.env` file with these API keys:
```env
SERVICE_ACCOUNT_JSON_BASE64=your_bigquery_service_account
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
E2B_API_KEY=your_e2b_api_key
```
""")

# Environment check
env_status = {
    "SERVICE_ACCOUNT_JSON_BASE64": "✅"
    if os.getenv("SERVICE_ACCOUNT_JSON_BASE64")
    else "❌",
    "GOOGLE_API_KEY": "✅" if os.getenv("GOOGLE_API_KEY") else "❌",
    "OPENAI_API_KEY": "✅" if os.getenv("OPENAI_API_KEY") else "❌",
    "E2B_API_KEY": "✅" if os.getenv("E2B_API_KEY") else "❌",
}

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Environment Status")
    for var, status in env_status.items():
        st.write(f"- {var}: {status}")

with col2:
    pass

missing_env = [key for key, status in env_status.items() if status == "❌"]

if missing_env:
    st.warning(f"⚠️ Missing: {', '.join(missing_env)}")
else:
    st.success("✅ All environment variables configured!")

st.markdown("""
## 🚀 Deployment

### Squadbase - Platform for securely delivering AI applications
Deploy this BI dashboard to your organization with [Squadbase](https://www.squadbase.dev/):

- **Built-in Authentication**: User management and role-based access control per app
- **Git-based CI/CD**: Automatic deployment pipeline with Git integration
- **Security First**: Secure infrastructure designed for enterprise AI applications
- **Runtime Monitoring**: Automatic log collection and user analytics
- **User Feedback**: Built-in comment system for continuous improvement

Squadbase eliminates the heavy lifting of deploying AI applications securely within organizations, allowing you to focus on building impactful business tools.
""")
