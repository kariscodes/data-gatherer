# required packages: requests, bs4, lxml
import requests
from bs4 import BeautifulSoup
import parser
import target
# Progress Bar (tqdm 설치 필요)
from tqdm import tqdm
import time

def fetch_law_list(date_from, date_to):
    law_keyword_list = target.get_keyword_list()
    law_list = []

    # 시행일 법령 목록 조회 API
    url = "http://www.law.go.kr/DRF/lawSearch.do?"
    user_id = "OC=kyungho.lim"
    service_target = "&target=eflaw"
    result_type = "&type=XML"

    # 공포일자 검색
    print("법령 목록(공포일자) 검색 ")
    for law_keyword in tqdm(law_keyword_list):
        time.sleep(0.1)
        search_type = "&date"               # 공포일자 검색
        date_period = "&ancYd=" + date_from + "~" + date_to
        query_name = "&query=" + law_keyword  # 법령명에 지정한 문자열이 있는 법령 검색
        request_url = url + user_id + service_target \
                        + result_type + date_period \
                        + search_type + query_name
        result = requests.get(request_url)
        if result.content: 
            soup = BeautifulSoup(result.text, 'lxml-xml')
            items = soup.find_all("law")
            for item in items:
                law_list.append(parser.parse_law_list(item))
            
    # 시행일자 검색
    print("법령 목록(시행일자) 검색 ")
    for law_keyword in tqdm(law_keyword_list):
        time.sleep(0.1)
        # search_type = "&date"             # 시행일자 검색(date 변수를 제외함)
        date_period = "&efYd=" + date_from + "~" + date_to
        query_name = "&query=" + law_keyword  # 법령명에 지정한 문자열이 있는 법령 검색
        request_url = url + user_id + service_target \
                        + result_type + date_period \
                        + query_name
        result = requests.get(request_url)
        if result.content: 
            soup = BeautifulSoup(result.text, 'lxml-xml')
            items = soup.find_all("law")
            for item in items:
                law_list.append(parser.parse_law_list(item))    
            
    # 중복 제거
    law_list_unique = []
    for value in law_list:
        if value not in law_list_unique:
            law_list_unique.append(value)
    
    return law_list_unique

def fetch_law_list_summary(law_list_unique):
    law_contents = []

    # 시행일 법령 본문 조회 API
    url = "http://www.law.go.kr/DRF/lawService.do?"
    user_id = "OC=kyungho.lim"
    service_target = "&target=eflaw"
    result_type = "&type=XML"
    
    print("법령 본문요약 검색 ")
    for law in tqdm(law_list_unique):
        time.sleep(0.1)
        seq_id = "&MST=" + law['법령일련번호']      # 법령마스터번호(MST, 법령일련번호)
        request_url = url + user_id + service_target \
                        + result_type + seq_id
        result = requests.get(request_url)
        if result.content:   
            soup = BeautifulSoup(result.text, 'lxml-xml')
            # 일치하는 법령이 없을 경우 다음과 같은 내용이 <Law> 태그로 온다.
            # "<Law> 태그에 "일치하는 법령이 없습니다.  법령명을 확인하여 주십시오.""
            # <Law> 태그가 없어야 정상적으로 데이터가 수신된 것임.
            if soup.find("Law") == None:
                law_contents.append(soup)

    law_list_summary = []        
    for item in law_contents:   
        law_list_summary.append(parser.parse_law_list_summary(item))             
    
    return law_list_summary