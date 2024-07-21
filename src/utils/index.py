from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from selenium import webdriver
import os
import openai
import joblib
import pandas as pd
import csv
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

def get_soup(url):
      # SSL 검증 비활성화
      requests.packages.urllib3.disable_warnings()
      res = requests.get(url, verify=False, timeout = 4000)
      res.encoding = 'utf-8'
      if res.status_code == 200:
            return BeautifulSoup(res.text, 'html.parser')
      else:
           print('get_soup 함수 실행 중 에러가 발생했습니다.')

# 크롤링하는 사이트의 date가 -으로 되어 있는 경우   
def get_date():
    today = datetime.today()
    today_date = today.date()
    return today_date

# 크롤링하는 사이트의 date가 .으로 되어 있는 경우    
def change_date():
    today_date = get_date()
    today_date = str(today_date)
    date_text = today_date.replace('-', '.')
    return date_text

def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    return driver

error_regions = []  # 오류 지역을 저장할 리스트를 초기화

def log_error_region(region_name):
    global error_regions  # error_regions 리스트를 전역 변수로 사용

    error_regions.append(region_name)

load_dotenv()

slack_token_main = os.getenv('slack_token_main')
client_main = WebClient(token=slack_token_main)

slack_token_dev = os.getenv('slack_token_dev')
client_dev = WebClient(token=slack_token_dev)

chatgpt_api_key = os.getenv('chatgpt_api_key')
openai.api_key = chatgpt_api_key

def do_classfication_using_chatgpt(post):
    post.append('')


def checking_duplicate():
    current_date = datetime.now().strftime('%Y%m%d')

    file_path = os.getcwd()+f'/src/classification/datas/program_crawling_{current_date}.csv'

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, encoding = 'utf-8')

        except pd.errors.EmptyDataError:
            print("데이터가 없습니다.")

        except Exception as e:
            print(f"에러 발생: {e}")
    else:
        # 파일이 없을 경우 빈 데이터프레임 생성
        df = pd.DataFrame()
        df['titles'] = []

        print("파일이 존재하지 않습니다.")

    return df

def checking_town():

    file_path = os.getcwd()+f'/src/classification/datas/town_crawling.csv'

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, encoding = 'utf-8')

        except pd.errors.EmptyDataError:
            print("데이터가 없습니다.")

        except Exception as e:
            print(f"에러 발생: {e}")
    else:
        # 파일이 없을 경우 빈 데이터프레임 생성
        df = pd.DataFrame()
        df['name'] = []

        print("파일이 존재하지 않습니다.")

    return df


def send_slack_messages_main(posts, region_name):
    response = None  # 초기에 response를 None으로 설정
    df = checking_duplicate()
    titles = df.iloc[:, 0]

    df2 = checking_town()
    names = df2.iloc[:, 0]
    
    if region_name != '그린대로 농촌마을':
        post1 = [post for post in posts if post[0] not in titles.values]
        if not post1:
            try:
                    response = client_main.chat_postMessage(
                        channel=os.getenv('channel_main'),
                        text=f'오늘 {region_name} 지역에는 키워드에 해당하는 게시물이 없습니다. 에러가 발생한 지역은 {error_regions}과 같습니다. \n {region_name} 완료!!!' 
                    )
            except SlackApiError as e:
                    assert e.response["error"]
        else:
            for post in post1:
                try:
                    if len(post) == 5:
                        #classification_using_RandomForestClassifier(post)
                        do_classfication_using_chatgpt(post)
                        # post 리스트의 길이가 5 이상인 경우
                        response = client_main.chat_postMessage(
                            channel=os.getenv('channel_main'),
                            text=f'''
                            지역: {post[4]}\n제목: {post[0]}\n링크: {post[3]}\n본문: {post[1]}\n날짜: {post[2]}\n분류: {post[5]}\n 에러가 발생한 지역은 {error_regions}과 같습니다. \n {region_name} 완료!!!
                            '''
                        )
                    else:
                        print('중복 제거 완료')

                except SlackApiError as e:
                    assert e.response["error"]

    else:
        post1 = [post for post in posts if post[0] not in names.values]
        if not post1:
            try:
                    response = client_main.chat_postMessage(
                        channel=os.getenv('channel_main'),
                        text=f'오늘 {region_name} 사이트에는 새롭게 추가된 마을이 없습니다. 에러가 발생한 지역은 {error_regions}과 같습니다. \n {region_name} 완료!!!' 
                    )
            except SlackApiError as e:
                    assert e.response["error"]
        else:
            for post in post1:
                try:
                    if len(post) == 5:
                        #classification_using_RandomForestClassifier(post)
                        do_classfication_using_chatgpt(post)
                        # post 리스트의 길이가 5 이상인 경우
                        response = client_main.chat_postMessage(
                            channel=os.getenv('channel_main'),
                            text=f'''
                            지역: {post[1]}\n마을명: {post[0]}\n모집 인원: {post[4]}\n신청 기간: {post[3]}\n입주가능일: {post[2]}\n분류: {post[5]}\n 에러가 발생한 지역은 {error_regions}과 같습니다. \n {region_name} 완료!!!
                            '''
                        )
                    else:
                        print('중복 제거 완료')

                except SlackApiError as e:
                    assert e.response["error"]

                
    return response  # response를 반환

def send_slack_messages_dev(posts, region_name):
    response = None  # 초기에 response를 None으로 설정
    if not posts:
        try:
            response = client_dev.chat_postMessage(
                channel=os.getenv('channel_dev'),
                text=f'오늘 {region_name} 지역에는 키워드에 해당하는 게시물이 없습니다. 에러가 발생한 지역은 {error_regions}과 같습니다. \n {region_name} 완료!!!' 
            )
        except SlackApiError as e:
            assert e.response["error"]
    else:
        for post in posts:
            try:
                if len(post) == 5:
                    do_classfication_using_chatgpt(post)
                    # post 리스트의 길이가 5 이상인 경우
                    response = client_dev.chat_postMessage(
                        channel=os.getenv('channel_dev'),
                        text=f'''
                        지역: {post[4]}\n제목: {post[0]}\n링크: {post[3]}\n본문: {post[1]}\n날짜: {post[2]}\n분류: {post[5]}\n 에러가 발생한 지역은 {error_regions}과 같습니다. \n {region_name} 완료!!!
                        '''
                    )

            except SlackApiError as e:
                assert e.response["error"]
                
    return response  # response를 반환

