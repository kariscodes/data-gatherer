import os
import datetime

# root 폴더 하위의 모든 파일들의 이름(file path)을 가져온다.
def getFiles(root_folder):
    os.chdir(root_folder)
    all_files = []
    for path, dirs, files in os.walk(root_folder):
        for file in files:
            if os.path.splitext(file)[1] in ['.html', '.htm']:
                file_path = os.path.join(path, file)
                all_files.append(file_path)
    return all_files

# 현재 시각: 년월일_시분초
def now_dt_str():
    now = datetime.datetime.now()
    dt = now.strftime('%Y%m%d_%H%M%S')
    return dt