from pathlib import Path
import os
import fetch
import msword
import target

if __name__ == '__main__':
    # 날짜는 특정월 내에서 일자 구간 지정
    # date_from, date_to의 년월이 같은 경우에만 검색 실행
    date_from, date_to = target.date_range()
    # date_from = '20230101'    
    # date_to = '20230131'
    
    law_list_unique = []
    law_list_summary = []
    
    law_list_unique = fetch.fetch_law_list(date_from, date_to)
    law_list_summary = fetch.fetch_law_list_summary(law_list_unique)
    
    doc = msword.create_word(law_list_summary, date_from, date_to)
    
    # (디렉토리가 없는 경우) 디렉토리 생성
    os.chdir("./law")
    dir_name = 'Doc'
    Path(dir_name).mkdir(exist_ok=True)
    file_name = '시행공포법령' + "_" + date_from + "_" + date_to + ".docx"
    file_path = Path.joinpath(Path.cwd(), dir_name, file_name)    
    
    try:
        doc.save(file_path)
        print(file_path)
    except PermissionError:
        print("Permission denied. Close the file and try it again.")