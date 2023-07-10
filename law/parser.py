def parse_law_list(item):
    try:
        return {
            "법령일련번호" : item.find("법령일련번호").get_text(),
            "법령ID" : item.find("법령ID").get_text(),
            "법령명한글" : item.find("법령명한글").get_text(),
            "법령약칭명" : item.find("법령약칭명").get_text(),
            "제개정구분명" : item.find("제개정구분명").get_text(),
            "공포일자" : item.find("공포일자").get_text(),
            "시행일자" : item.find("시행일자").get_text(),
            "소관부처명" : item.find("소관부처명").get_text(),
        }
    except AttributeError as e:
        return {
            "법령일련번호" : None,
            "법령ID" : None,
            "법령명한글" : None,
            "법령약칭명" : None,
            "제개정구분명" : None,
            "공포일자" : None,           
            "시행일자" : None, 
            "소관부처명" : None,
        }
        
def parse_law_list_summary(item):
    try:
        return {
            "법령ID" : item.find("법령ID").get_text(),
            "법령명_한글" : item.find("법령명_한글").get_text(),
            "법종구분" : item.find("법종구분").get_text(),
            "제개정구분" : item.find("제개정구분").get_text(),
            "공포번호" : item.find("공포번호").get_text(),
            "공포일자" : item.find("공포일자").get_text(),
            "시행일자" : item.find("시행일자").get_text(),
            "소관부처명" : item.find("소관부처명").get_text(),
            "제개정이유내용" : item.find("제개정이유내용").get_text(),
        }        
    except AttributeError as e:
        return {
            "법령ID" : None,
            "법령명_한글" : None,
            "법종구분" : None,
            "제개정구분" : None,
            "공포번호" : None,
            "공포일자" : None,           
            "시행일자" : None, 
            "소관부처명" : None,
            "제개정이유내용" : None,
        }
