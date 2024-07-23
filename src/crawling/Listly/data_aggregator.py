import requests
import pandas as pd
import io
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from boilerpy3 import extractors

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
    
    # 데이터 검수
    #combined_df = filter_data(combined_df)

    # 본문 내용 추가
    #combined_df['content'] = combined_df['link'].apply(extract_important_content)
    

    return combined_df

def preprocess_data(df, region):
    # 4번째 컬럼 삭제
    if df.shape[1] >= 4:
        df = df.drop(df.columns[3], axis=1)
    
    # 컬럼 이름 변경
    df.columns = ['title', 'link', 'date']

    # content 빈 컬럼 추가
    df['content'] = ""
    
    # date 컬럼 형식 변경
    def add_current_year(date_str):
        try:
            date = pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
            if pd.isnull(date):
                date = pd.to_datetime(date_str, format='%Y.%m.%d', errors='coerce')
            if pd.isnull(date):
                current_year = datetime.now().year
                date = pd.to_datetime(f"{current_year}-{date_str}", format='%Y-%m-%d', errors='coerce')
            return date.strftime('%Y-%m-%d')
        except Exception:
            return None

    df['date'] = df['date'].apply(add_current_year)

    # 컬럼 순서 변경
    df = df[['title', 'content', 'date', 'link']]
    
    # region 컬럼 추가
    df['region'] = region
    
    return df

def filter_data(df):
    today = datetime.today() - timedelta(days=19)
    yesterday = today - timedelta(days=1)

    # 날짜 필터링: 오늘 또는 하루 전인 데이터만 남김
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df[(df['date'] >= yesterday) & (df['date'] <= today)]
    
    # 제목 필터링: "강사"와 "모집" 두 단어가 모두 포함된 경우만 남김
    df = df[df['title'].str.contains('강사') & df['title'].str.contains('모집|채용|공고')]
    
    return df

def extract_important_content(url):
    try:
        extractor = extractors.ArticleExtractor()
        result = extractor.get_content_from_url(url)

        return result
    except Exception as e:
        return ""  # 예외 발생 시 빈 본문 반환

API_KEYS_gangnam = {
    "3yIyUgDb": "강남구청 - 고시공고",
    "fPR4gjCr": "강남구청 - 채용공고",
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
    "SwnyfuHk": "성내종합사회복지관"
}

API_KEYS_guri = {
    "z4yGxEY0": "구리시청-모집공고"
}

API_KEYS = {**API_KEYS_gangnam, **API_KEYS_yangcheon, **API_KEYS_gangdong}

combined_df = fetch_data(API_KEYS, BASE_URL, API_TOKEN)


# 결합된 데이터를 CSV 파일로 저장
combined_df.to_csv('./result_combined.csv', index=False)