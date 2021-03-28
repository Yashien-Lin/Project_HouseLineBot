import pymysql
import redis


#redredis存跟拿資料

# redis_host= 'teb10303.hopto.org'  
redis_host= 'localhost'
def hset_redis(redis_a, redis_b='', redis_c='', redis_d='', redis_e='', redis_p='', field='predict'):
    pool = redis.ConnectionPool(host = redis_host, port = 6379) 
    r = redis.Redis(connection_pool=pool)
    r.hset("{}{}{}{}{}".format(redis_a, redis_b, redis_c, redis_d, redis_e), field, '{}'.format(redis_p))
    #存資料:
    #input: redis_a, redis_b, redis_c='', redis_d='', redis_e='', 'predict', redis_p
    #input:  大安區, 華廈, '1', '40', '20', 'predict', '50.8'
    #     (地區、型態、車位、坪數、屋齡, 'predict', 預測價格)

    #input:  userid, 房仲網類別, uri
    #input:(redis_a=user_dict_id, redis_b='', field='sinyi', redis_p= a(url)

    #通過其內部Map的Key(Redis裡稱內部Map的key為field),也就是通過key(用戶ID) + field(屬性標籤)就可以操作對應屬性數據。
    # 格式：hset key field value
    # 示例：hset myhash username root
    # 作用：设置hash里一个字段的值

def hget_redis(redis_a, redis_b, redis_c, redis_d, redis_e, field='predict'):
    pool = redis.ConnectionPool(host = redis_host, port = 6379) 
    r = redis.Redis(connection_pool=pool)
    
    try:
        hg =  r.hget("{}{}{}{}{}".format(redis_a, redis_b, redis_c, redis_d, redis_e), field).decode()  #Redis取出的資料type是bytes, 要decode()才會拿到str
        ## hset {key:[{field:value},{field:value}]}
    except Exception as e:
        print(e)
        hg = None
    return hg


#跟mysql拿資料
def con_mysql(sql_a, sql_b, redis_c, redis_d, redis_e):
    db = pymysql.connect(
        host = 'teb10303.hopto.org',
        user = 'root',
        passwd = 'somewordpress',
        port = 3366,
        db = 'house',
        charset = 'utf8mb4')
    cursor = db.cursor()
    # cursor.execute("SELECT * FROM ml where address = '{}' and building = '{}'".format(sql_a, sql_b))
    cursor.execute("SELECT * FROM ml where area = '{}' and type = '{}' and `parking` = '{}' and `ping` = '{}' and `age` = '{}'".format(sql_a, sql_b, redis_c, redis_d, redis_e))
    data = cursor.fetchall()
    db.close()

    if data:
        print(data)
        return data[0][5]      
    else:
        return None
        

def getdata(a, b, c, d, e):

    response = hget_redis(a, b, c, d, e)
    
    if response:        #如果Redis有資料，就回覆價格
        return response
        # print('response:', response)
    else :              #如果Redis沒有資料
        # if b == '所有型態':   #若b為"所有型態"
        #     ans = select_ml_all(a)  #ans為所有型態的價格
        ans = con_mysql(a, b, c, d, e)   #去mysql找
        print(ans)
        if ans:    #若ans有值
            hset_redis(a, b, c, d, e, ans, field='predict')   #存回Redis
            return ans    #並傳回ans
        else:                #若ans沒有值
            return '查無此資料'   #傳回'查無此資料'

print(getdata('信義區','公寓','1','40','15'))
