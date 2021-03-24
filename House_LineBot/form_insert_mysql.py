##在執行import MySQLdb的時候請先pip install mysqlclient 

import MySQLdb
import json

insert_str = 'INSERT INTO {table} ({{}}) VALUES ({{}})'
member_ins = 'INSERT INTO HOUSE.MEMBER ({}) VALUES ({});'
mem_ch_ins = 'INSERT INTO HOUSE.MEMBER_CHECK_BOX ({},`create_time`) VALUES ({},curdate());'
mem_fm_ins = 'INSERT INTO HOUSE.MEMBER_FORM ({},`create_time`) VALUES ({},curdate());'

update_str = 'UPDATE {table} SET {{}}'
member_upd = 'UPDATE MEMBER SET {}  '
mem_ch_upd = 'UPDATE MEMBER_CHECK_BOX SET {}  '
mem_fm_upd = 'UPDATE MEMBER_FORM SET {}  '

select_str = 'SELECT {{}} FROM {table} {{}}'
member_qur = 'SELECT {} FROM MEMBER {}'
mem_ch_qur = 'SELECT {} FROM MEMBER_CHECK_BOX {}'
mem_fm_qur = 'SELECT {} FROM MEMBER_FORM {}'

delete_str = 'DELETE FROM {table} WHERE {{}}'
member_del = 'DELETE FROM MEMBER WHERE {}'
mem_ch_del = 'DELETE FROM MEMBER_CHECK_BOX WHERE {}'
mem_fm_del = 'DELETE FROM MEMBER_FORM WHERE {}'

host='teb10303.hopto.org'
def insert_method(sql,values,cursor,needid=False):
    
    keyl = []
    insl = []
    for key,value in values.items():
        keyl.append(f'`{key}`')
        insl.append(f"'{value}'")
    
    sql = sql.format(','.join(keyl),','.join(insl))
    print(sql)
    cursor.execute(sql)
    if needid :
        return cursor.lastrowid
    

def update_method(sql,values,cursor,cond=None,cust_cond=None):
    
    upda_lis = []
    

    cond_str = ''
    for key,value in values.items():
        upda_lis.append(f"`{key}`='{value}'")
    if cust_cond:
       sql = sql.format(','.join(upda_lis)+cust_cond) 
    elif cond:
        cond_str = condti_method(cond)
        cond_str = 'where {}'.format(','.join(cond_lis))
        sql = sql.format(cond_str)
    else: 
        sql = sql.format(','.join(upda_lis))
        
    cursor.execute(sql)
    
def delete_method(sql,cursor,values):
    sql = sql.format(condti_method(values))
    cursor.execute(sql)
    pass


def select_method(sql,values,cursor,qur_all=False,cond=None,cust_cond=None):
    '''
    param sql:    sql的語法建議 \n
    param values: for select的欄位 \n
    param cursor: 連線db資訊 \n
    qur_all: 是否查出全部欄位(暫時做不到)
    param cond: for where key value值 對應column 和 value值 \n
    param cust: 使用者自定義 where 條件
    尚未完成待測試
    return list[ json 字串]
    '''
    cond_str = ''
    if cust_cond:
       sql = sql.format(','.join(values),cust_cond) 
    elif cond:
        cond_lis = condti_method(cond)
        
        cond_str = 'where {}'.format(cond_lis)
        sql = sql.format(','.join(values),cond_str)
    # if qur_all:
    
    cursor.execute(sql)
    result = cursor.fetchall()
    if not result:
        return None 
    
    qu_reses = []
    for i in result:
        qu_res={}
        for _ in range(len(i)):
            qu_res[values[_]] = i[_]
        qu_reses.append(qu_res)
    
    
    return qu_reses


def condti_method(cond):
    '''
    不須執行該程式
    '''
    cond_lis=[]
    for key,value in cond.items():
        cond_lis.append(f"`{key}`='{value}'")
    return 'and'.join(cond_lis)
    
def mem_insert(value):
    db = MySQLdb.connect(host="teb10303.hopto.org",port=3366,user="root",passwd="somewordpress",database='house',charset = 'utf8mb4')
    cursor = db.cursor()
    insert_method(member_ins,value,cursor)
    db.commit()
    db.close()


def form_kafka(consu):
    db = MySQLdb.connect(host="teb10303.hopto.org",port=3366,user="root",passwd="somewordpress",database='house',charset = 'utf8mb4')
    cursor = db.cursor()
    db.autocommit(True)
    list_key = ['direction','facility','zone']
    form_val = {}
    chbx_val = {}
    
    for key,value in json.loads(consu).items():
        # print(key,value)
        if key in list_key:
            if value:
                chbx_val[key] = []
                for item in value:
                    chbx_val[key].append(item)
                    # chbx_val[key] = item
        else:
            form_val[key] = value
    form_id = insert_method(mem_fm_ins,form_val,cursor,True)
    db.commit()
    for key,values in chbx_val.items():
        print(key,values)
        for value in values:
            insert_method(mem_ch_ins,{'type':key,'name':value,'form_id':str(form_id)},cursor)
    db.commit()
    db.close()

def select_userid_form(value):
    db = MySQLdb.connect(host=host,port=3366,user="root",passwd="somewordpress",database='house',charset = 'utf8mb4')
    cursor = db.cursor()
    result = {}
    result = select_method(mem_fm_qur,['form_id','type','parking','size_lower','size_upper','age_lower','age_upper'],cursor,cust_cond='where ' + condti_method(value) + 'order by form_id desc limit 1')
    if result:
        
        form_id = str(result[0]['form_id'])
        
        result[0]['zone'] = list(select_method(mem_ch_qur,['name'],cursor,cond={'form_id':form_id,'type':'zone'}))
    db.close()
    
    return result
    

if __name__ == '__main__':
    
    data = select_userid_form({'user_id':'U76c63b4ff5cc34277b98097ba8a2ad4f'})
    print(data)
    output = '請確認是否要查詢以下條件: \r\n 行政區:{} \r\n 型態:{} \r\n 車位:{} \r\n 坪數:40坪 \r\n 屋齡:15年 \r\n'.format('、'.join([i['name'] for i in data[0]['zone']]),'有' if data[0]['parking']== 'yes' else '無',data[0]['parking'])
    print(output)

    # select_ml_all()
    
    # user_choose_for_forum = {'User_ID':'abc','ch_zone':'中山區'}
    # mem_insert(user_choose_for_forum)
    # consumer = '''{"user_id":"kent","type":["公寓","華廈","電梯大樓","套房"],"parking":"yes","direction":["朝西","朝北","朝南","朝西北","朝東北"],"floor_lower":"3","floor_upper":"5","room_lower":"4","room_upper":"5","facility":["近公園","近市場","近學校"],"size_lower":"10","size_upper":"10","age_lower":"0","age_upper":"10","zone":["中正區","松山區","信義區","大同區","內湖區"]}'''
    # print(json.loads(consumer))
    # form_kafka(consumer)
    # db1 = MySQLdb.connect(host="localhost",port=3366,user="root",passwd="somewordpress",database='house')
    #dbconnection 建立 host 需要連線的位置,user 連線人的名稱, passwd 密碼 ,db 連到哪個schmea

    # cursor = db1.cursor()
    # 建立連線

    # sql = "show TABLES FROM HOUSE;"
    #sql指令 查詢
    #sql = "INSERT INTO `my_db`.`emp` (`EMPNO`, `ENAME`, `JOB`, `MGR`, `SAL`, `DEPTNO`) VALUES 
    # ('7000', 'test', 'CLERK', '7782', '1000.00', '10');" insert 的
    # sql = "INSERT INTO house.member (`user_id`, `ch_zone`) VALUES (%s, %s)" 
    # cursor.execute(sql,('kent','test'))
    # sql = 'select * from house.member;'
    # sql = "INSERT INTO house.member (`user_id`, `ch_zone`) VALUES ('kent','test')" 
    # sql = 'delete from house.member where `user_id`="kent";'
    # cursor.execute(sql)

    #執行指令

    # result = cursor.fetchall()
    #取得結果
    # for record in result:
        #print(str(record[0]) + str(record[1]))
    #     print(record)
    # db1.commit()

    # db1.close()
    