import requests
import pandas as pd
import csv
import io

BASE_URL = "https://www.listly.io/api/single?selected=1&arrange=y&href=y&header=y&file=csv&key="

API_KEYS_gangnam = [
    "3yIyUgDb", # 강남구청 - 고시공고
    "fPR4gjCr" # 강남구청 - 채용공고
]

API_KEYS_gangseo = [
    "YWJZFbz5", # 강서구청
]

API_KEYS_yangcheon = [
    "TFiL1FCv", # 양천구청
    "WmKlWMZW", # 시립청소년드림센터
    "lRNxhyGK", # 신월청소년문화센터
    "ZJ8wPkNR", # 신월종합사회복지관
    "QOrTTMMj", # 양천어르신종합복지관
    "7zCbHKcL", # 신목종합사회복지관
]

API_KEYS = API_KEYS_gangnam + API_KEYS_gangseo + API_KEYS_yangcheon

API_TOKEN = "7YqGgH2YabaLTMMofTBzD8MocZ6rl2Oq"
headers = {	"Authorization": API_TOKEN }

combined_df = pd.DataFrame()

# 각 URL에서 데이터를 받아와 결합
for key in  API_KEYS:
    url = BASE_URL + key
    response = requests.get(url=url, headers=headers)
    df = pd.read_csv(io.StringIO(response.text))
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# 결합된 데이터를 CSV 파일로 저장
combined_df.to_csv('./result_combined.csv', index=False)
