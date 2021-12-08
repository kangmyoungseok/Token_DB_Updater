import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = '''CREATE TABLE comment (
    id int NOT NULL,
    token_id char(50),
    name varchar(250) NOT NULL,
    comment varchar(500) NOT NULL,
    datetime datetime NOT NULL,
    PRIMARY KEY (id)
) CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    '''
cursor.execute(sql)
conn.commit()
conn.close()