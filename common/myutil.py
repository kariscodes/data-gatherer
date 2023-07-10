from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_previous_day():
    # 현재일-1일
    prev_date = datetime.now() + relativedelta(days=-1)
    prev_date_str = prev_date.strftime("%Y%m%d")
    return prev_date_str

def get_next_day(date_str):
    dt_last_date = datetime.strptime(date_str, '%Y%m%d')       # 날짜형으로 변환
    dt_start_date = dt_last_date + relativedelta(days=+1)
    next_date_str = dt_start_date.strftime("%Y%m%d")               # 문자형으로 변환
    return next_date_str