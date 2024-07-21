'''from bs4 import BeautifulSoup
import re
import sys
import time
from selenium.webdriver.common.by import By
sys.path.append("../..")  # 상위 폴더로 경로 추가
from constants.index import real_keywords
from utils.index import get_soup
from utils.index import get_date
from utils.index import get_driver
from utils.index import log_error_region

detail_region = '경기 Free:Way'

def get_html_tbody(page_number = 1):
    ul_list = []
    driver = get_driver()
    # 크롤링할 웹 페이지 URL
    url = "https://www.gg.go.kr/free/web/woin/woin/wkrgListPage.do"
    
    try:
        # 웹 페이지 열기
        driver.get(url)

        page1_source = driver.page_source

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(page1_source, 'html.parser')

        # tr 요소 가져오기
        ul1 = soup.find('ul', class_ = 'textlist.work')
        ul1 = soup.find('body')

        ul_list.append(ul1)

        if page_number != 1:
            for i in range(2, page_number + 1):
                # 원하는 링크 클릭 (예: 1페이지로 이동)
                click_button = driver.find_element(By.XPATH, f"//button[@onclick='go_Page({i});']")
                click_button.click()
                
                # 페이지 이동을 위해 잠시 대기 (로딩 완료를 기다리는 것이 좋음)
                time.sleep(5)

                # 현재 페이지의 HTML 코드를 가져옵니다.
                page_source = driver.page_source

                # BeautifulSoup으로 파싱
                soup = BeautifulSoup(page_source, 'html.parser')

                # tbody 요소 가져오기
                ul = soup.find('ul', class_ = 'textlist.work')

                # tbody1과 tbody2를 리스트에 저장
                ul_list.append(ul)
    
    except Exception as e:
        print(f"{detail_region} 오류 발생: {e}")

    return ul_list

post_list = []

def extract_post_data(title, date):
    title_text = title.text.strip()
    match_title = re.search('(\S.*\S)', title_text)

    date_text = date.text.strip()  # 문자열 좌우 공백 제거
    match_date = re.search('\d{4}-\d{2}-\d{2}', date_text)

    full_url = ''
    content = ''

    if match_title:
        title_text = match_title.group()
    if match_date:
        date_text = match_date.group()

    post_list.append([title_text, content, date_text, full_url, detail_region])
    
    return post_list

try:
    ul_list = get_html_tbody(1)
    print(ul_list)
    for ul in ul_list:
        titles = ul.select(' ul > li > a > div.title')
        dates = ul.select('ul > li > a > div.info > div.txt.color_blue')

        for title, date in zip(titles, dates):
            post_list = extract_post_data(title, date)
    
    print(post_list)
    post_list = [post for post in post_list if post[2] == str(get_date())]
    post_link_filtered = [post for post in post_list if any(keyword in post[0] or keyword in post[1] for keyword in real_keywords)]

    for post in post_link_filtered:
        print('지역:', post[4])
        print('제목:', post[0])
        print('링크:', post[3])
        print('본문:', post[1])
        print('날짜:', post[2])

except Exception as e:
        print(f"{detail_region} 오류 발생: {e}")
        log_error_region(detail_region)
        post_list = []
        post_link_filtered = []'''