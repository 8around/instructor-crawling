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


from boilerpy3 import extractors

def extract_important_content(url):
    extractor = extractors.ArticleExtractor()
    result = extractor.get_content_from_url(url)
    return result

url = 'https://www.oc.go.kr/www/selectBbsNttView.do?key=236&bbsNo=40&nttNo=167144&searchCtgry=&searchCnd=all&searchKrwd=&pageIndex=1&integrDeptCode='
url = 'http://www.suncheon.go.kr/kr/news/0006/0001/?mode=view&seq=66282'
important_content = extract_important_content(url)
print(important_content)