from bs4 import BeautifulSoup
import re
import sys
import time
sys.path.append("../..")  # 상위 폴더로 경로 추가
from constants.index import real_keywords
from utils.index import get_soup
from utils.index import get_date
from utils.index import get_driver
from utils.index import log_error_region

detail_region = '강남문화재단'

def get_html_tbody(page_number = 1):
    tbody_list = []
    driver = get_driver()
    # 크롤링할 웹 페이지 URL
    url = "https://www.gangnam.go.kr/office/gfac/board/gfac_chargeteacher/list.do?mid=gfac_chargeTeacher&pgno=1&keyfield=BDM_MAIN_TITLE&keyword="
    
    try:
        # 웹 페이지 열기
        driver.get(url)

        page1_source = driver.page_source

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(page1_source, 'html.parser')

        # tr 요소 가져오기
        tbody1 = soup.find('tbody', class_ = 'grid')

        tbody_list.append(tbody1)

        if page_number != 1:
            for i in range(2, page_number + 1):
                # 원하는 링크 클릭 (예: 1페이지로 이동)
                url = f"https://www.gangnam.go.kr/office/gfac/board/gfac_chargeteacher/list.do?mid=gfac_chargeTeacher&pgno={i}&keyfield=BDM_MAIN_TITLE&keyword="
                driver.get(url)
                
                # 페이지 이동을 위해 잠시 대기 (로딩 완료를 기다리는 것이 좋음)
                time.sleep(5)

                # 현재 페이지의 HTML 코드를 가져옵니다.
                page_source = driver.page_source

                # BeautifulSoup으로 파싱
                soup = BeautifulSoup(page_source, 'html.parser')

                # tbody 요소 가져오기
                tbody = soup.find('tbody', class_ = 'grid')

                # tbody1과 tbody2를 리스트에 저장
                tbody_list.append(tbody)
    
    except Exception as e:
        print(f"{detail_region} 오류 발생: {e}")

    return tbody_list

post_list = []

def extract_post_data(title, date, link):
    title_text = title.text.strip()
    match_title = re.search('(\S.*\S)', title_text)

    date_text = date.text.strip()  # 문자열 좌우 공백 제거
    match_date = re.search('\d{4}-\d{2}-\d{2}', date_text)

    full_url = 'https://www.gangnam.go.kr/' + link

    post = get_soup(full_url)
    content = post.find('div', class_ = 'post-content')
    content = content.get_text("\n", strip=True)

    if match_title:
        title_text = match_title.group()
    if match_date:
        date_text = match_date.group()

    post_list.append([title_text, content, date_text, full_url, detail_region])
    
    return post_list

try:
    tbody_list = get_html_tbody(1)

    for tbody in tbody_list:
        titles = tbody.select('tbody > tr > td.align-l.tit > a')
        dates = tbody.select(' tbody > tr > td:nth-child(5)')

        for title, date in zip(titles, dates):
            post_list = extract_post_data(title, date, title.get('href'))
    
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
        post_link_filtered = []