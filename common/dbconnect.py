import json
import pymysql
from urllib.parse import quote
from sqlalchemy import create_engine

def db_connect(server_db_name):
    with open("D:\PythonProject\data-gatherer\common\config.json", "r") as f:
        config = json.load(f)
    if server_db_name in config["DB_CONFIG"]:
        db_config = config["DB_CONFIG"][server_db_name]
    # if dbname != config.SEED_TEST_DB_CONFIG['dbname']:
    #     raise ValueError("Could not find DB with the given name")
        conn = pymysql.connect(host = db_config["host"],
                               user = db_config["user"],
                               password = db_config["password"],
                               db = db_config["dbname"])
    else:
        pass
    return conn

def db_engine(server_db_name):
    with open("D:\PythonProject\data-gatherer\common\config.json", "r") as f:
        config = json.load(f)
    if server_db_name in config["DB_CONFIG"]:
        db_config = config["DB_CONFIG"][server_db_name]
        # MySQL Connector using pymysql
        pymysql.install_as_MySQLdb()
        db_url = f'mysql+pymysql://{db_config["user"]}:{quote(db_config["password"])}@{db_config["host"]}:{db_config["port"]}/{db_config["dbname"]}' #경로 설정
        # engine = create_engine(db_url, encoding='utf-8') #연결
        # engine = create_engine(db_url, encoding='euckr') #연결
        # engine = create_engine(db_url, echo=False) #연결
        engine = create_engine(db_url) #연결
    else:
        pass
    return engine