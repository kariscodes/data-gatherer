# 날짜 문자열 YYYYMMDD를 YYYY. MM. DD 문자열로 변환하기
# 예: 20230104 => 2023. 1. 4 (공백 삽입, 01의 경우 0 없애기) 
def format_date(date_string):
    y = date_string[0:4].lstrip("0")
    m = date_string[4:6].lstrip("0")
    d = date_string[6:8].lstrip("0")
    formatted_string = y + ". " + m + ". " + d + "."
    return formatted_string

def format_number(number_string):
    formatted_number = "제" + number_string.lstrip("0") + "호"
    return formatted_number