import requests
import pandas as pd
import csv
import io

API_URLS = ["https://www.listly.io/api/single?key=3yIyUgDb&selected=1&arrange=y&href=n&header=y&file=csv",
						"https://www.listly.io/api/single?key=fPR4gjCr&selected=1&arrange=y&href=y&header=y&file=csv",
						]
API_TOKEN = "7YqGgH2YabaLTMMofTBzD8MocZ6rl2Oq"
headers = {	"Authorization": API_TOKEN }

combined_df = pd.DataFrame()

# 각 URL에서 데이터를 받아와 결합
for url in API_URLS:
    
    response = requests.get(url=url, headers=headers)
    df = pd.read_csv(io.StringIO(response.text))
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# 결합된 데이터를 CSV 파일로 저장
combined_df.to_csv('./result_combined.csv', index=False)
