import requests
from bs4 import BeautifulSoup
import re
import pandas

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


# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# headers = {'User-Agent': USER_AGENT}

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
        sliced_text = doc_text[a.start()-100:a.start()]
        trimmed_text = sliced_text.replace(" ","")     # 문서에 있는 모든 공백 제거
        unit = get_unit(trimmed_text)
        if unit != None:
            return unit
    for a in re.finditer("퇴직급여채무", doc_text):
        sliced_text = doc_text[a.start()-100:a.start()]
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
    try:
        doc_data = pandas.read_html(doc_url)
    except ValueError:
        val_a = val_b = 0.0
        return  val_a, val_b
    # except pandas.errors.EmptyDataError:
    #     val_a = val_b = 0.0
    #     return  val_a, val_b
    for df in doc_data:
        row = df.shape[0]
        for i in range(0, row):
            item = str(df.iloc[i,0])
            # if item.__contains__('확정급여채무의 현재가치') or item.__contains__('확정급여부채의 현재가치') or item.__contains__('퇴직급여채무'):
            if item.__contains__('확정급여채무의 현재가치') or item.__contains__('확정급여부채의 현재가치') or \
                item.__contains__('확정급여채무 현재가치') or item.__contains__('확정급여부채 현재가치') or \
                item.__contains__('퇴직급여채무'):                
                # print(i, type(df.iloc[i,1]), df.iloc[i,1])
                if len(item) <= 30:
                    str_a = str(df.iloc[i,1])
                    if str_a == item: val_a = -1.0      # 값 찾기 오류
                    elif str_a == "-": val_a = 0.0
                    else: val_a += str2num(str_a)       # 값을 합한다.
            elif item.__contains__('사외적립자산의 공정가치'):
                # print(i, type(df.iloc[i,1]), df.iloc[i,1])                            
                if len(item) <= 30:
                    str_b = str(df.iloc[i,1])
                    if str_b == item: val_b = -1.0      # 값 찾기 오류
                    elif str_b == "-": val_b = 0.0
                    else: val_b = str2num(str_b)
            else:
                continue    
        if (val_a != 0.0) and (val_b != 0.0):
            break   
    return val_a, val_b