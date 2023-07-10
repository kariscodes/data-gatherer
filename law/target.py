# 법률명칭(full name) 또는 법률 키워드명
# law_keyword_list = ['법인세법', '교통ㆍ에너지ㆍ환경세법', '국민건강보험법', '고압가스 안전관리법']
# law_keyword_list = ['법인세법']
# law_keyword_list = ['교통ㆍ에너지ㆍ환경세법']

import os
import csv

def date_range():
    try:
        year_month  = input("연월을 입력하세요(yyyymm): ")
        assert len(year_month) == 6
        year = year_month[0:4]
        month = year_month[4:6]
        assert 1 <= int(month) <= 12
        begin_date = input("검색 시작일을 입력하세요(01~31): ")
        end_date = input("검색 종료일을 입력하세요(01~31): ")
        assert len(begin_date ) == 2
        assert len(end_date ) == 2
        assert 1 <= int(begin_date) <= 31
        assert 1 <= int(end_date) <= 31
        assert int(begin_date) <= int(end_date)
        date_from = year + month + begin_date
        date_to = year + month + end_date
        return date_from, date_to
    except AssertionError:
        sys.exit("잘못된 입력입니다. 프로그램을 종료합니다.")
    except Exception:
        sys.exit("프로그램을 종료합니다.")    
        
def get_keyword_list():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = '법령키워드.csv'
    file_path = os.path.join(dir_path, file_name) 
    keyword_list = []
    with open(file_path, 'r', encoding='utf-8') as f:
        laws = csv.reader(f)
        for law_item in laws:
            keyword_list.append(law_item[0])
    return keyword_list

if __name__ == '__main__':
    # law_keyword_list = get_keyword_list()
    date_range()
    # print(law_keyword_list)