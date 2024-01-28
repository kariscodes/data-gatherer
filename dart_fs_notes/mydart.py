import requests
from bs4 import BeautifulSoup
import re
import pandas
import math

# USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.3904.108 Safari/537.36'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

api_key = 'f2e08d4ed3de0ba3d5cbf59c04c223e02b1751a2'
params = {
    'crtfc_key': api_key,
}

# def html_download(url, fn=None):
#     r = requests.get(url, stream=True, headers={'User-Agent': USER_AGENT})
#     if r.status_code != 200:
#         return False
#     with open(fn, "wb") as f:
#         for chunk in r.iter_content(chunk_size=4096):
#             f.write(chunk) if chunk else None
#     return True

# from fake_useragent import UserAgent
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context


# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# headers = {'User-Agent': USER_AGENT}

# 검색 우선순위를 고려한 순서로 리스트 구성
TARGET_KEYWORDS = [
    '순확정급여부채', '순확정급여채무', '순확정급여자산',
    '퇴직급여부채', '퇴직급여채무', '퇴직급여제도',    
    '퇴직급여충당부채',
    '퇴직급여',
    '확정급여부채', '확정급여채무', '확정급여제도',
    '종업원급여', '종업원 급여',
    '비용의 성격별 내역', '비용의 성격별 분류', '수익과 비용의 분석',
    '기타부채',
]
        
def cleanPage(page):
    # span tag 제거
    page = re.sub('<(span|SPAN).*?>', '', page, 0).strip()
    page = re.sub('</(span|SPAN)>', '', page, 0).strip()
        
    # 줄바꿈없는 공백(Non-breaking Space) 표식 제거
    page = page.replace("&nbsp;", " ")
    
    return page

def get_document(doc_url):
    # 재무제표 주석 url의 문서 가져오기
    try:
        response = requests.get(doc_url)
        # response = requests.get(doc_url, params=params, headers={'User-Agent': USER_AGENT})    
        if response.status_code != 200:     # URL GET '200 정상'
            return None
            
        page = cleanPage(response.text)
        # soup = BeautifulSoup(page, features="lxml")
        soup = BeautifulSoup(page, 'html.parser')
    except Exception:
        err_msg = traceback.format_exc()
        print(err_msg)

    return soup
    
def get_subtitles(soup):        
    # tags = soup.find_all('p')
    tags = soup.find_all(string = True)
    subtitle_list = []
    prev_number = 0
    for t in tags:
        subjects1 = re.findall('\d+[.]+\s+[^0-9]+', t.text)  # 숫자+'.'+공백+숫자가아닌모든문자열     
        subjects2 = re.findall('\d+[.]+[^0-9]+', t.text)  # 숫자+'.'+숫자가아닌모든문자열
        subjects_all = subjects1 + subjects2
        subjects = list(set(subjects_all))      # 중복 제거
        if len(subjects) > 0:
            for s in subjects:
                subtitle_list.append(s)               
    
    ordered_subtitle_list = []
    prev_no = 0             
    for s in subtitle_list:
        this_no = int(s.split(".")[0])
        if this_no == prev_no + 1 or this_no == prev_no + 2 or this_no == prev_no + 3:
            ordered_subtitle_list.append(s)
            prev_no = this_no

    return ordered_subtitle_list

def find_section_title(subtitle_list):
    if len(subtitle_list) == 0:
        return None
    
    section_title = None
    for keyword in TARGET_KEYWORDS:
        if section_title is None:
            for subtitle in subtitle_list:
                if subtitle.__contains__(keyword):
                    section_title = subtitle
                    break
        else:
            break    

    if section_title is None:
        return None
    
    return section_title

def get_section_html(soup, subtitle_list, section_title):
    idx = 0
    idx = subtitle_list.index(section_title)
    next_title = subtitle_list[idx + 1]
    # 문서에서 해당 Section 시작위치와 종료위치 찾기
    doc_html = soup.prettify()
    p0 = doc_html.find(section_title)
    p1 = doc_html.find(next_title)
    section_html = doc_html[p0:p1]     # 문서 Slicing
    return section_html

# 금액 단위 찾기
def get_unit(text):
    if '(단위:백만원)' in text or '[단위:백만원]' in text: unit = '백만원'
    elif '(단위:천원)' in text or '[단위:천원]' in text: unit = '천원'
    elif '(단위:원)' in text or '[단위:원]' in text: unit = '원'
    else: unit = None   
    return unit

# 콤마와 괄호를 제거한다.
def str2num(x):
    if "," in x: x = x.replace(",","")
    if "(-)" in x: x = x.replace("(-)","")    
    if x.startswith("("): x = x.lstrip("(")
    if x.endswith(")"): x = x.rstrip(")")
    return float(x)

def find_unit_from_section(str_doc):
    unit = None
    trimmed_text = str_doc.replace(" ","")     # 문서에 있는 모든 공백 제거
    unit = get_unit(trimmed_text)         
    return unit    

def find_item_from_section(html_doc):
    val_a = val_b = 0.0
    item_result = None                    
    try:
        doc_data = pandas.read_html(html_doc)
    except ValueError:
        val_a = val_b = 0.0
        item_result = "No Contents"
        return  val_a, val_b, item_result
    # except pandas.errors.EmptyDataError:
    #     val_a = val_b = 0.0
    #     return  val_a, val_b
    for df in doc_data:
        row = df.shape[0]
        for i in range(0, row):
            item = str(df.iloc[i,0])
            if item.__contains__('확정급여채무의 현재가치') or item.__contains__('확정급여부채의 현재가치') or \
                item.__contains__('확정급여채무 현재가치') or item.__contains__('확정급여부채 현재가치') or \
                item.__contains__('적립형 의무의 현재가치') or item.__contains__('퇴직급여채무의 현재가치') or \
                item == '확정급여채무(기말)' or item == '퇴직급여채무' or item == '퇴직급여충당부채':
                # item.__contains__('확정급여채무') or item.__contains__('퇴직급여채무') or item.__contains__('퇴직급여충당부채') or \               
                if item_result is None:
                    item_result = item
                else:
                    item_result = item_result + ", " + item 
                if len(item) <= 30:
                    if isinstance(df.iloc[i,1], float) and math.isnan(df.iloc[i,1]):
                        val_a = -1.0                        # 값 찾기 오류
                    else:                        
                        str_a = str(df.iloc[i,1])
                        if str_a == item: val_a = -1.0      # 값 찾기 오류
                        elif str_a == "-": val_a += 0.0
                        else: val_a += str2num(str_a)       # 값을 합한다.
            elif item.__contains__('사외적립자산의 공정가치') or item.__contains__('사외적립자산 공정가치'):
                #  item == '사외적립자산':
                #  item == '퇴직연금운용자산' or item == '사외적립자산':
                if item_result is None:
                    item_result = item
                else:
                    item_result = item_result + ", " + item                                            
                if len(item) <= 30:
                    if isinstance(df.iloc[i,1], float) and math.isnan(df.iloc[i,1]):
                        val_b = -1.0                        # 값 찾기 오류
                    else:                                       
                        str_b = str(df.iloc[i,1])
                        if str_b == item: val_b = -1.0      # 값 찾기 오류
                        elif str_b == "-": val_b += 0.0
                        else: val_b = str2num(str_b)
            else:
                continue    
        if (val_a != 0.0) and (val_b != 0.0):
            break   
    return val_a, val_b, item_result

def html_download(url, fn=None):
    # user_agent = UserAgent()
    # headers = {'User-Agent': user_agent.random}
    # r = requests.get(url, params=params, headers=headers)
    r = requests.get(url, params=params, headers={'User-Agent': USER_AGENT})
    if r.status_code != 200:
        return False
    with open(fn, "wb") as f:
        for chunk in r.iter_content(chunk_size=4096):
            f.write(chunk) if chunk else None
    return True


"""
아래의 함수는 사용하지 않음
"""
# 재무제표 주석 문서에서 사용된 금액 단위 찾기
def find_unit(doc_url, url=True):
    unit = None
    # doc url
    if url:
        response = requests.get(doc_url)
        if response.status_code != 200:     # URL GET '200 정상'
            return None
        soup = BeautifulSoup(response.text, features="lxml")
    # html file         
    else:
        soup = BeautifulSoup(doc_url, 'html.parser')

    doc_text = soup.text
    # 확정급여채무의 현재가치, 확정급여부채의 현재가치, 확정급여채무 현재가치, 확정급여부채 현재가치
    for a in re.finditer(r"확정급여+[가-힣]+ 현재가치", doc_text):
    # for a in re.finditer(r"확정급여+[가-힣]+현재가치", doc_text):            
        sliced_text = doc_text[a.start()-500:a.start()]
        # print(sliced_text)
        trimmed_text = sliced_text.replace(" ","")     # 문서에 있는 모든 공백 제거
        unit = get_unit(trimmed_text)
        if unit != None:
            return unit
    for a in re.finditer("퇴직급여채무", doc_text):
        sliced_text = doc_text[a.start()-500:a.start()]
        trimmed_text = sliced_text.replace(" ","")     # 문서에 있는 모든 공백 제거
        unit = get_unit(trimmed_text)
        if unit != None:
            return unit     
    for a in re.finditer("확정급여채무(기말)", doc_text):
        sliced_text = doc_text[a.start()-500:a.start()]
        trimmed_text = sliced_text.replace(" ","")     # 문서에 있는 모든 공백 제거
        unit = get_unit(trimmed_text)
        if unit != None:
            return unit
    for a in re.finditer("퇴직급여충당부채", doc_text):
        sliced_text = doc_text[a.start()-500:a.start()]
        trimmed_text = sliced_text.replace(" ","")     # 문서에 있는 모든 공백 제거
        unit = get_unit(trimmed_text)
        if unit != None:
            return unit                       
    for a in re.finditer("적립형 의무의 현재가치", doc_text):
        sliced_text = doc_text[a.start()-500:a.start()]
        trimmed_text = sliced_text.replace(" ","")     # 문서에 있는 모든 공백 제거
        unit = get_unit(trimmed_text)
        if unit != None:
            return unit     
    else:
        unit = None   
        
    return unit    

# 재무제표 주석 문서에서 특정 항목의 금액 찾기
def find_item(doc_url):
    val_a = val_b = 0.0
    item_result = None                    
    try:
        doc_data = pandas.read_html(doc_url)
    except ValueError:
        val_a = val_b = 0.0
        item_result = "No Contents"
        return  val_a, val_b, item_result
    # except pandas.errors.EmptyDataError:
    #     val_a = val_b = 0.0
    #     return  val_a, val_b
    for df in doc_data:
        row = df.shape[0]
        for i in range(0, row):
            item = str(df.iloc[i,0])
            if item.__contains__('확정급여채무의 현재가치') or item.__contains__('확정급여부채의 현재가치') or \
                item.__contains__('확정급여채무 현재가치') or item.__contains__('확정급여부채 현재가치') or \
                item.__contains__('적립형 의무의 현재가치') or item.__contains__('퇴직급여채무의 현재가치') or \
                item == '확정급여채무(기말)' or item == '퇴직급여채무' or item == '퇴직급여충당부채':
                # item.__contains__('확정급여채무') or item.__contains__('퇴직급여채무') or item.__contains__('퇴직급여충당부채') or \               
                if item_result is None:
                    item_result = item
                else:
                    item_result = item_result + ", " + item 
                if len(item) <= 30:
                    if isinstance(df.iloc[i,1], float) and math.isnan(df.iloc[i,1]):
                        val_a = -1.0                        # 값 찾기 오류
                    else:                        
                        str_a = str(df.iloc[i,1])
                        if str_a == item: val_a = -1.0      # 값 찾기 오류
                        elif str_a == "-": val_a += 0.0
                        else: val_a += str2num(str_a)       # 값을 합한다.
            elif item.__contains__('사외적립자산의 공정가치') or item.__contains__('사외적립자산 공정가치'):
                #  item == '사외적립자산':
                #  item == '퇴직연금운용자산' or item == '사외적립자산':
                if item_result is None:
                    item_result = item
                else:
                    item_result = item_result + ", " + item                                            
                if len(item) <= 30:
                    if isinstance(df.iloc[i,1], float) and math.isnan(df.iloc[i,1]):
                        val_b = -1.0                        # 값 찾기 오류
                    else:                                       
                        str_b = str(df.iloc[i,1])
                        if str_b == item: val_b = -1.0      # 값 찾기 오류
                        elif str_b == "-": val_b += 0.0
                        else: val_b = str2num(str_b)
            else:
                continue    
        if (val_a != 0.0) and (val_b != 0.0):
            break   
    return val_a, val_b, item_result