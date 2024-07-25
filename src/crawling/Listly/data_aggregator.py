import requests
import pandas as pd
import io
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from boilerpy3 import extractors
from api_keys import API_KEYS

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
        df = df.iloc[:, :3]

    # 컬럼 이름 변경
    df.columns = ['title', 'link', 'date']

    # content 빈 컬럼 추가
    df['content'] = ""
    
    # date 컬럼 형식 변경
    def add_current_year(date_str):
        try:
            if date_str.startswith('작성일'):
                return date_str.replace('작성일', '').strip()
            
            # 시간 정보만 있는 경우 처리
            if len(date_str.split(':')) == 3:
                current_date = datetime.now().strftime('%Y-%m-%d')
                date_str = f"{current_date} {date_str}"
                return pd.to_datetime(date_str, format='%Y-%m-%d %H:%M:%S', errors='coerce').strftime('%Y-%m-%d')

            date = pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
            if pd.isnull(date):
                date = pd.to_datetime(date_str, format='%Y.%m.%d', errors='coerce')
            if pd.isnull(date):
            # "MM.DD" 형식 처리
                if len(date_str.split('.')) == 2:
                    current_year = datetime.now().year
                    date = pd.to_datetime(f"{current_year}.{date_str}", format='%Y.%m.%d', errors='coerce')
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

combined_df = fetch_data(API_KEYS, BASE_URL, API_TOKEN)


# 결합된 데이터를 CSV 파일로 저장
combined_df.to_csv('./result_combined.csv', index=False)