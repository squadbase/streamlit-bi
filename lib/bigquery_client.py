import base64
import json
import os

import streamlit as st
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()


@st.cache_resource  # serialized only once per worker
def _get_bq_client():
    credentials_json = base64.b64decode(
        os.environ["SERVICE_ACCOUNT_JSON_BASE64"]
    ).decode("utf-8")
    credentials_info = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info
    )
    return bigquery.Client(credentials=credentials)


bigquery_client = _get_bq_client()
