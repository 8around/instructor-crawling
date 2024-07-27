from bs4 import BeautifulSoup
import re
import sys
import time
sys.path.append("../..")  # 상위 폴더로 경로 추가
from constants.index import must_include_keyword
from constants.index import must_not_include_keywords
from constants.index import any_of_keywords
from utils.index import get_soup
from utils.index import change_date
from utils.index import get_driver
from utils.index import log_error_region

detail_region = '인천광역시교육청계양도서관'

def get_html_tbody():
    tbody_list = []
    driver = get_driver()
    # 크롤링할 웹 페이지 URL
    url = "https://lib.ice.go.kr/gyeyang/board/index.do?menu_idx=87&manage_idx=108"
    
    try:
        # 웹 페이지 열기
        driver.get(url)

        page1_source = driver.page_source

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(page1_source, 'html.parser')

        # tr 요소 가져오기
        tbody1 = soup.find('tbody')

        tbody_list.append(tbody1)
    
    except Exception as e:
        print(f"{detail_region} 오류 발생: {e}")

    return tbody_list

post_list = []

def extract_post_data(title, date, link):
    title_text = title.text.strip()
    match_title = re.search('(\S.*\S)', title_text)

    date_text = date.text.strip()  # 문자열 좌우 공백 제거
    match_date = re.search('\d{4}-\d{2}-\d{2}', date_text)

    full_url = 'https://lib.ice.go.kr/gyeyang/board/view.do?menu_idx=87&manage_idx=108&board_idx=' + link

    post = get_soup(full_url)
    content = post.find('div', class_ = 'bbs-view-body')
    content = content.get_text("\n", strip=True)
    content = re.sub(r'\xa0', ' ', content) # 문자열에서 모든 \xa0 문자를 제거
    content = re.sub(r'\ufeff', ' ', content)


    if match_title:
        title_text = match_title.group()
    if match_date:
        date_text = match_date.group()

    post_list.append([title_text, content, date_text, full_url, detail_region])
    
    return post_list

try:
    tbody_list = get_html_tbody()

    for tbody in tbody_list:
        titles = tbody.select('tbody > tr > td.important.left.title.td2 > a')
        dates = tbody.select('tbody > tr > td.num.adddate.td4')

        for title, date in zip(titles, dates):
            post_list = extract_post_data(title, date, title.get('keyvalue'))
    print(post_list)
    post_list = [post for post in post_list if post[2] == str(change_date())]

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