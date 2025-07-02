from datetime import date, timedelta
from typing import Tuple

import streamlit as st


def iso_format(d: date) -> str:
    """Convert date to ISO format string (YYYY-MM-DD)."""
    return d.isoformat()


def get_date_inputs() -> Tuple[date, date]:
    """Get date inputs from sidebar."""
    TODAY = date.today()
    start_default = TODAY - timedelta(days=30)
    end_default = TODAY - timedelta(days=1)

    with st.sidebar:
        st.header("📅 Date Range")
        start: date = st.date_input("Start", start_default, max_value=TODAY)
        end: date = st.date_input("End", end_default, max_value=TODAY)
        if end < start:
            st.error("End date must be after start date.")
            st.stop()
    return start, end


@st.cache_data(show_spinner=False)
def get_date_range(start: date, end: date) -> Tuple[date, date, date, date, int]:
    """Calculate date ranges based on input dates."""
    period = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period - 1)
    return start, end, prev_start, prev_end, period
