# Streamlit business intelligence

## How to use BigQuery

GCP上でサービスアカウントを作成して、JSONファイルをダウンロードしてください。
サービスアカウントには、以下の2つの権限を付与してください。

- BigQuery Job User
- BigQuery Read Session User

### サービスアカウントのJSONファイルを使用して認証する方法

以下のように環境変数にJSONファイルのパスを指定することで使用することができます。

```python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./squadbase-demo.json"
```

### 環境変数を使って認証をする方法 (推奨)

クラウドにデプロイする際に上記の方法では、サービスアカウントのJSONファイルをソースコードに含める必要があります。
これはセキュリティ上良くないので、以下のように環境変数で管理できるようにする方法が推奨です。

まず事前準備として以下の方法でJSONの中身をBase64でエンコードします。

##### macOSの場合

```shell
base64 -i squadbase-demo.json | tr -d '\n'

```

##### Linuxの場合

```shell
base64 squadbase-demo.json | tr -d '\n'
```

##### Windowsの場合

PowerShellを使う

```shell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("squadbase-demo.json"))
```

コマンドプロンプトでWSLを使う

```
base64 squadbase-demo.json | tr -d '\n'
```

#### 環境変数に追加

次に環境変数として`.env`に以下のように追加してください。

```env
SERVICE_ACCOUNT_JSON_BASE64="エンコードした文字列"
```

以下のようにPythonから環境変数を使用して認証することができます。

```python
import os
import json
import base64
from google.oauth2 import service_account
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

credentials_json = base64.b64decode(os.getenv('SERVICE_ACCOUNT_JSON_BASE64')).decode('utf-8')
credentials_info = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = bigquery.Client(credentials=credentials, project=credentials_info["project_id"])

```