from bs4 import BeautifulSoup
import re
import sys
import time
sys.path.append('../..')
from constants.index import must_include_keyword
from constants.index import must_not_include_keywords
from constants.index import any_of_keywords
from utils.index import get_soup
from utils.index import get_date
from utils.index import get_driver
from utils.index import log_error_region

detail_region = '한국노인종합복지관협회'
      
def get_html_tbody(page_number = 1):
    tbody_list = []
    driver = get_driver()
    # 크롤링할 웹 페이지 URL
    url = "http://www.kaswcs.or.kr/bj_board/bjbrd_list.htm?board_id=0404&board_sel_cate=&board_search_field=&board_search_key=&page=1"

    try:
        # 웹 페이지 열기
        driver.get(url)

        page1_source = driver.page_source

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(page1_source, 'html.parser')

        # tbody 요소 가져오기
        tbody1 = soup.find('tbody')

        tbody_list.append(tbody1)

        if page_number != 1:
            for i in range(2, page_number + 1):
                # XPath로 <a> 요소 찾기
                url = f"http://www.kaswcs.or.kr/bj_board/bjbrd_list.htm?board_id=0404&board_sel_cate=&board_search_field=&board_search_key=&page={i}"
                driver.get(url)

                # 페이지 이동을 위해 잠시 대기 (로딩 완료를 기다리는 것이 좋음)
                time.sleep(5)

                # 현재 페이지의 HTML 코드를 가져옵니다.
                page_source = driver.page_source

                # BeautifulSoup으로 파싱
                soup = BeautifulSoup(page_source, 'html.parser')

                # tbody 요소 가져오기
                tbody = soup.find('tbody')

                # tbody1과 tbody2를 리스트에 저장
                tbody_list.append(tbody)

    except Exception as e:
        print(f"{detail_region} 오류 발생: {e}")

    return tbody_list


post_list = []

def extract_post_data(title, link):
    title_text = title.text.strip()
    match_title = re.search('(\S.*\S)', title_text)

    full_url = 'http://www.kaswcs.or.kr/bj_board/' + link

    post = get_soup(full_url)
    content = post.find('div', class_ = 'board_view')
    content = content.get_text("\n", strip=True)

    date = post.find('div', class_ = 'board_info')
    date = date.get_text("\n", strip=True)
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    match_date = re.search(date_pattern, date)
    
    if match_title:
        title_text = match_title.group()
    if match_date:
        date_text = match_date.group()

    post_list.append([title_text, content, date_text, full_url, detail_region])
    
    return post_list

try:
    tbody_list = get_html_tbody(2)

    for tbody in tbody_list:
        titles = tbody.select('tbody > tr > td.item1 > div.title > a')

        for title in titles:
            post_list = extract_post_data(title, title.get('href'))
    
    post_list = [post for post in post_list if post[2] == str(get_date())]
    
    post_link_filtered = [
    post for post in post_list
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
