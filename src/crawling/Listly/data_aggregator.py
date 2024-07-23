import requests
import pandas as pd
import io
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('BASE_URL')
API_TOKEN = os.getenv('API_TOKEN')

def fetch_data(api_keys, base_url, api_token):
    headers = {"Authorization": api_token}
    combined_df = pd.DataFrame()

    # 각 URL에서 데이터를 받아와 결합
    for key, region in api_keys.items():
        url = base_url + key
        response = requests.get(url=url, headers=headers)
        df = pd.read_csv(io.StringIO(response.text))

        # 데이터 전처리
        df = preprocess_data(df, region)
        
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    return combined_df

def preprocess_data(df, region):
    # 4번째 컬럼 삭제
    if df.shape[1] >= 4:
        df = df.drop(df.columns[3], axis=1)
    
    # 컬럼 이름 변경
    df.columns = ['title', 'link', 'date']
    
    # content 빈 컬럼 추가
    df['content'] = ""
    
    # 컬럼 순서 변경
    df = df[['title', 'content', 'date', 'link']]
    
    # region 컬럼 추가
    df['region'] = region
    
    return df

# 날짜로 먼저 1차 검수 (1일 전까지)


# 키워드로 2차 검수




API_KEYS_gangnam = {
    "3yIyUgDb": "강남구청 - 고시공고",
    "fPR4gjCr": "강남구청 - 채용공고",
}

API_KEYS_gangseo = {
    "YWJZFbz5": "강서구청",
}

API_KEYS_yangcheon = {"TFiL1FCv": "양천구청",
    "WmKlWMZW": "시립청소년드림센터",
    "lRNxhyGK": "신월청소년문화센터",
    "ZJ8wPkNR": "신월종합사회복지관",
    "QOrTTMMj": "양천어르신종합복지관",
    "7zCbHKcL": "신목종합사회복지관",
}

API_KEYS_gangdong = {
    "BgzCFdJv": "강동구청",
}


API_KEYS = {**API_KEYS_gangnam, **API_KEYS_gangseo, **API_KEYS_yangcheon, **API_KEYS_gangdong}

combined_df = fetch_data(API_KEYS, BASE_URL, API_TOKEN)


# 결합된 데이터를 CSV 파일로 저장
combined_df.to_csv('./result_combined.csv', index=False)