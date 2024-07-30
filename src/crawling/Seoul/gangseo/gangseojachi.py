from bs4 import BeautifulSoup
import re
import sys
import time
from selenium.webdriver.common.by import By
sys.path.append("../../..")  # 상위 폴더로 경로 추가
from constants.index import must_include_keyword
from constants.index import must_not_include_keywords
from constants.index import any_of_keywords
from utils.index import get_date
from utils.index import get_driver
from utils.index import log_error_region

detail_region = '강서자치회관'

contents = []

def get_html_tbody():
    tbody_list = []
    driver = get_driver()

    # 크롤링할 웹 페이지 URL
    url = "https://jachi.gangseo.seoul.kr/cpage/board/cpageNewsList"
    
    try:
        # 웹 페이지 열기
        driver.get(url)

        page1_source = driver.page_source

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(page1_source, 'html.parser')

        # tr 요소 가져오기
        tbody1 = soup.find('tbody')

        tbody_list.append(tbody1)
    
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:goBoardView(')]")

        for i in range(10):    
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:goBoardView(')]")
            links[i].click()
            time.sleep(3)

            soup2 = BeautifulSoup(driver.page_source, 'html.parser')
            content = soup2.find('section', class_ = 'view-cont')
            content = content.get_text("\n", strip=True)
            content = re.sub(r'\xa0', ' ', content) # 문자열에서 모든 \xa0 문자를 제거
            contents.append(content)

            driver.back()

            time.sleep(3)


    except Exception as e:
        print(f"{detail_region} 오류 발생: {e}")

    return tbody_list

post_list = []

def extract_post_data(title, date):
    title_text = title.text.strip()
    match_title = re.search('(\S.*\S)', title_text)

    date_text = date.text.strip()  # 문자열 좌우 공백 제거
    match_date = re.search('\d{4}-\d{2}-\d{2}', date_text)

    if match_title:
        title_text = match_title.group()
    if match_date:
        date_text = match_date.group()

    post_list.append([title_text, date_text])
    
    return post_list

try:
    tbody_list = get_html_tbody()

    for tbody in tbody_list:
        titles = tbody.select('tbody > tr > td.link-in > a')
        dates = tbody.select(' tbody > tr > td:nth-child(3)')

        for title, date in zip(titles, dates):
            post_list = extract_post_data(title, date)
    
    final_post_list = []

    # post_list와 contents 리스트를 결합
    for post, content in zip(post_list, contents):
        title, date = post
        link = ''
        final_post_list.append([title, content, date, link, detail_region])

    final_post_list = [post for post in final_post_list if post[2] == str(get_date())]
    
    post_link_filtered = [
    post for post in final_post_list
    if must_include_keyword in (post[0]) and 
       any(keyword in (post[0]) for keyword in any_of_keywords) and 
       not any(keyword in (post[0]) for keyword in must_not_include_keywords)
]
    
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
        post_link_filtered = []