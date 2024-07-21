from bs4 import BeautifulSoup
import re
import sys
import time
sys.path.append("../..")  # 상위 폴더로 경로 추가
from constants.index import real_keywords
from utils.index import get_soup
from utils.index import change_date
from utils.index import get_3_days_ago_date
import math
from utils.index import get_driver
from utils.index import log_error_region

contents = []

def get_html_tbody2():
    ul_list = []
    driver = get_driver()
    
    for keyword in real_keywords:
      url = f"https://www.gov.kr/portal/locgovNews?srchOrder=&sido=&signgu=&srchArea=&srchSidoArea=&srchStDtFmt={get_3_days_ago_date()}&srchEdDtFmt={change_date()}&srchTxt={keyword}&initSrch=false"
      
      # 웹 페이지 열기
      driver.get(url)

      page1_source = driver.page_source

      # BeautifulSoup으로 파싱
      soup1 = BeautifulSoup(page1_source, 'html.parser')

      time.sleep(4)

      # tbody 요소 가져오기
      ul = soup1.find('ul', class_='line-b')

      # tbody1과 tbody2를 리스트에 저장
      ul_list.append(ul)

      # page_number
      page_number = soup1.find('span', class_='sum')
      page_number = page_number.get_text(strip=True)
      page_number = page_number.replace(',', '')  # 4자리 넘어가면 쉼표 생겨서 쉼표 제거하는 코드
      page_number = int(page_number)
      page_number = page_number / 10
      page_number = math.ceil(page_number)

      for i in range(2, page_number + 1):
         url = f"https://www.gov.kr/portal/locgovNews?srchOrder=&sido=&signgu=&srchArea=&srchSidoArea=&srchStDtFmt={get_3_days_ago_date()}&srchEdDtFmt={change_date()}&srchTxt={keyword}&initSrch=false&pageIndex={i}"
         driver.get(url)

         # 현재 페이지의 HTML 코드를 가져옵니다.
         page_source = driver.page_source

        # BeautifulSoup으로 파싱
         soup = BeautifulSoup(page_source, 'html.parser')
        
         time.sleep(4)

         # tbody 요소 가져오기
         ul = soup.find('ul', class_='line-b')

         # tbody1과 tbody2를 리스트에 저장
         ul_list.append(ul)

         time.sleep(4)

    ul_list = [item for item in ul_list if item is not None]

    return ul_list     

post_list = []

def extract_post_data(title, date, link, region):
    title_text = title.text.strip()
    match_title = re.search('(\S.*\S)', title_text)
    date_text = date.text.strip()  # 문자열 좌우 공백 제거
    date_text = date_text.split()[-1] # "등록일" 다음의 날짜 부분 추출
    date_text = date_text.replace('.', '-') # 정부24의 경우, 23.09.14 이런 식이라서 23-09-14로 가져오기
    match_date = re.search('\d{4}-\d{2}-\d{2}', date_text)
    link = title.get('href')
    full_url = 'https://www.gov.kr' + link
    post = get_soup(full_url)
    
    content = post.find('div', class_='view-contents')
    content = content.get_text("\n", strip=True)
    content = re.sub(r'\xa0', ' ', content) # 문자열에서 모든 \xa0 문자를 제거
    
    region = post.find('div', class_= 'view-title')
    region = region.find('strong')
    region = region.get_text(strip=True)
    region = re.sub(r'\xa0', ' ', region) # 문자열에서 모든 \xa0 문자를 제거
    
    if match_title:
        title_text = match_title.group()
    if match_date:
        date_text = match_date.group()
    
    post_list.append([title_text, content, date_text, full_url, region])
    
    return post_list

def remove_duplicate_titles(post_list):
    # 각 제목의 등장 횟수를 저장하는 딕셔너리 생성
    title_count = {}
    
    # 중복 제거된 post_list를 저장할 새로운 리스트
    new_post_list = []
    
    # post_list를 순회하면서 중복된 제목 여부 확인
    for post in post_list:
        title = post[0]  # 제목은 리스트의 첫 번째 요소
        
        # 딕셔너리에 제목이 이미 등장한 경우 중복이므로 카운트 증가
        if '강사' in title and '모집' in title:
            # 딕셔너리에 제목이 이미 등장한 경우 중복이므로 카운트 증가
            title_count[title] = title_count.get(title, 0) + 1
            
            # 중복이 아닌 경우에만 new_post_list에 추가
            if title_count[title] == 1:
                new_post_list.append(post)
    
    return new_post_list

try:
    ul_list = get_html_tbody2()

    for ul in ul_list:
        titles = ul.select('dl dt a')
        dates = ul.select('span:contains("등록일")')
        regions = ul.select('div.sorting-area')

        for title, date, region in zip(titles, dates, regions):
            post_list = extract_post_data(title, date, title.get('href'), region)

    result_list = remove_duplicate_titles(post_list)

    # 결과 확인
    for post in result_list:    
        print('지역:', post[4])
        print('제목:', post[0])
        print('링크:', post[3])
        print('본문:', post[1])
        print('날짜:', post[2])
    
except Exception as e:
        print(f"정부24 오류 발생: {e}")
        log_error_region('전국 정부24')
        post_list = []