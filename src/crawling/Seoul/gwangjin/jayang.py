from bs4 import BeautifulSoup
import re
import sys
import time
from selenium.webdriver.common.by import By
sys.path.append('../../..')
from constants.index import must_include_keyword
from constants.index import must_not_include_keywords
from constants.index import any_of_keywords
from utils.index import get_soup
from utils.index import get_date
from utils.index import get_driver
from utils.index import log_error_region

detail_region = '자양종합사회복지관'

def get_html_tbody(page_number=1):
    tbody_list = []
    driver = get_driver()
    
    try:
        for i in range(1, page_number + 1):
            url = f"https://www.jayang.or.kr/main/sub.html?page={i}&boardID=www21&keyfield=subject&key=%EA%B0%95%EC%82%AC&bCate="
            driver.get(url)
            time.sleep(2)  # 페이지 로드를 기다리기 위해 충분한 시간 대기

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            tbody = soup.find('tbody')

            if tbody:
                tbody_list.append(tbody)

            else:
                print(f"Page {i}: No tbody found")

    except Exception as e:
        print(f"{detail_region} 오류 발생: {e}")

    finally:
        driver.quit()

    return tbody_list

post_list = []

def extract_post_data(title, date, link):
    title_text = title.text.strip()
    match_title = re.search('(\S.*\S)', title_text)

    date_text = date.text.strip()
    match_date = re.search('\d{4}-\d{2}-\d{2}', date_text)

    parts = link.split(',')
    num = parts[1].strip().strip("'")
    full_url = f'https://www.jayang.or.kr/main/sub.html?Mode=view&boardID=www21&num={num}&page=1&keyfield=subject&key=%EA%B0%95%EC%82%AC&bCate='

    try:
        post = get_soup(full_url)
        #content = post.find('html')
        #content = content.get_text("\n", strip=True)
        content = ''
        if match_title:
            title_text = match_title.group()
        if match_date:
            date_text = match_date.group()

        post_list.append([title_text, content, date_text, full_url, detail_region])

    except Exception as e:
        print(f"Error extracting post data: {e}")

    return post_list

try:
    tbody_list = get_html_tbody(1)

    for tbody in tbody_list:
        titles = tbody.select('tbody > tr > td.AB_tdLeft > div.tdLeftSubject > a')
        dates = tbody.select('tbody > tr > td:nth-child(4) > p')

        for title, date in zip(titles, dates):
            post_list = extract_post_data(title, date, title.get('onclick'))
    
    print(post_list)
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
