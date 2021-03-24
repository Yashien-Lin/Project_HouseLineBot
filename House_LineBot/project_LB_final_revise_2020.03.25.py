from flask import Flask, request, abort, render_template  #要取得參數值需要先匯入request套件。因為Flask是透過request來取得參數值。
import sqlite3
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

import forum_nlp as nlp
import redis_mysql_latest as red
import disgust_facility as disgust
import house_website as website
import form_insert_mysql as form_db
import def_recommendation as recommend

import pandas
import json
import requests
import time


app = Flask(__name__)   #需要宣告一個變數負責掌控serve，命名為app

line_bot_api = LineBotApi('M7sJhuMt2wJcUxBiVRYa1kUEgPl0bWEE5B3+moy8wCN9T5hV8Ak2Us+Pft5z5key1PRnn9aomlPMWDi0+XlRb0/+mti8Uj5k8hHjNyGct93DSzoDIlv/P4Y4CS11178fGhc4f4OjFrIk+BZV104HgwdB04t89/1O/w1cDnyilFU=')
# Line Channel access token
handler = WebhookHandler('e0c6bda1fbac22b6bddc875316319718')    
#Line Channel secret

line_bot_ip=''
# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # LINE會將傳遞過來的Http Request Body使用你的Line Bot Secret做SHA256加密，並且塞入X-Line-Signature這個header當中  
    # 當有人呼叫 Flask的API時，首先從請求的header中拿到X-Line-Signature


    # get request body as text
    body = request.get_data(as_text=True)                                   
    app.logger.info("Request body: " + body)
    #當LINE的一個訊息傳遞過來時，Http請求內會包含一個header。X-Line-Signature 這個header是用作訊息驗證的，   


    # 當開發者的Webhook伺服器收到以POST方式所傳送的LINE事件訊息時，必須要立即驗證該事件訊息是否真的來自LINE平台:
    try:
        handler.handle(body, signature)   #以Channel secret作為密鑰（Secret key），使用HMAC-SHA256演算法取得HTTP請求本體（HTTP request body）的文摘值（Digest value）。將上述文摘值以Base64編碼，比對編碼後的內容與X-Line-Signature項目內容值是否相同                                      
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#Tests:
@app.route("/", methods=['GET'])   #使用route()裝飾器來告訴Flask觸發函數的URL 
def rootPage():
    return 'Hello, how are you'

# user_id = []
consumer = {"user_id":"", "type":[],"parking":"", "direction":[],"price_lower":"", "price_upper":"", "floor_lower":"", "floor_upper":"","room_lower":"", "room_upper":"", \
"facility":[], "size_lower":"", "size_upper":"", "age_lower":"", "age_upper":"","zone":[]}
    
@app.route("/format", methods=['GET','POST'])  #若Flask想要接收以GET方式傳送的參數，就需要在method設定以GET方式傳送。
def formatPage():
    if request.method =='POST':           #如果HTTP請求的存取方式是POST的話，取得"使用者問卷資料"存到Kafka(json)
        user_dict = request.form         #用request.form取得Form表單中傳遞過來的值
                                                
        for i in consumer.keys():
            if len(user_dict.getlist(i)) == 1:
                consumer[i] = user_dict.getlist(i)[0]
            else:  
                consumer[i] = user_dict.getlist(i)
        
        consumer['user_id'] = user_dict.get("user_id")[:-1]
        json_consumer = json.dumps(consumer)
        form_db.form_kafka(json_consumer)

        a,b,c = website.format_form_url(user_dict)     #信義.永慶.591的url

        user_dict_id=user_dict.get("user_id")[:-1]
        red.hset_redis(redis_a= user_dict_id, #userid   
            redis_b='',
            redis_p= a, field='sinyi')
        red.hset_redis(redis_a= user_dict_id, #userid
            redis_b='',
            redis_p= b, field='yungching')
        red.hset_redis(redis_a= user_dict_id, #userid
            redis_b='',
            redis_p= c, field='591')

        return '完成填答，請回到Line點選"找房去!"'

    else :                            #else: 如果HTTP請求的存取方式是GET的話，則到filter_condition_new.html樣板 
        id = request.args.get('id')     #request.args中儲存的是url中傳遞的引數

        return render_template('filter_condition_new.html',result=id)

@app.route("/index", methods=['GET','POST'])
def ChartpPage():
    return render_template("index.html")    #使用 render_template() 將HTML的檔案透過Flask框架呈現

@app.route("/index2", methods=['GET','POST'])
def ChartpPage2():
    return render_template("index2.html")

@app.route("/index3", methods=['GET','POST'])
def ChartpPage3():
    return render_template("index3.html")    


@handler.add(MessageEvent)   #利用 handler.add這個function來幫你處理Line回傳的json資料
def handle_message(event):
    text=event.message.text

    #把每個QuickReplyButton用迴圈寫在一個List裡，就不用重複寫很多次
    zone_for_price_evaluate_no_form_data =[]
    zone_forum =[]
    zone_for_recommand =[]

    areas = ["中正區", "大同區","中山區","松山區","大安區","萬華區","信義區","士林區","北投區","內湖區","南港區","文山區"]  #Quick Reply Button的按鈕項目

    for area in areas:
        zone_for_price_evaluate_no_form_data.append(QuickReplyButton(       #若沒有填過表單的，選擇行政區按鈕
                            action=PostbackAction(
                                label=area, 
                                data=f"A{area}",
                                )
                            ))
                            
        zone_forum.append(QuickReplyButton(              #建案論壇的選擇行政區按鈕
                            action=PostbackAction(
                                label=area, 
                                data=f"F{area}",
                                )
                            )) 

        zone_for_recommand.append(QuickReplyButton(      #推薦房屋的行政區按鈕
                    action=PostbackAction(
                        label=area, 
                        data=f"R{area}",
                        )
                    ))  

    if '房價評估' in text: 
        text_message_1 = ''
        data = form_db.select_userid_form({'user_id':event.source.user_id})     #填入UserId去MySQL抓"問卷資料"
        
        if data:
            text_message_1 = f"請確認是否要查詢以下條件: \n- 行政區:{'、'.join(i['name'] for i in data[0]['zone'])} \n- 型態:{data[0]['type']} \n- 車位:{'有' if data[0]['parking']== 'yes' else '無'} \n- 坪數:{data[0]['size_lower']}-{data[0]['size_upper']}坪 \n- 屋齡:{data[0]['age_lower']}-{data[0]['age_upper']}年 \n"
            red.hset_redis(redis_a= [i['name'] for i in data[0]['zone']], redis_b=data[0]['type'], redis_c='1' if data[0]['parking']== 'yes' else '0', \
                           redis_d='40', redis_e='15')

            message = TemplateSendMessage(
            alt_text='請在手機上操作', 
            template= ConfirmTemplate(
                title='這是ConfirmTemplate',
                text= text_message_1,
                actions=[
                    PostbackAction(
                        label='是',
                        data='呼叫redis'        ## 根據表單填的條件來查詢建議價格
                    ),
                    PostbackAction(
                        label='否，重新設定',
                        data='尋找行政區'
                    )
                ]   
            ))

        else:                                  #若沒有填過表單，選擇行政區
            message = TextSendMessage(
                text = "請選擇以下行政區" ,
                quick_reply=QuickReply(
                items= zone_for_price_evaluate_no_form_data
                ))


    elif '房價走勢' in text:
        message = TemplateSendMessage(
            alt_text='請在手機上操作',
            template=ButtonsTemplate(
                thumbnail_image_url='https://www.harrisonfinance.com.au/wp-content/uploads/2017/11/%E6%8A%95%E8%B5%84%E6%88%BF.jpg',
                title='歷史房價走勢圖&預測房價走勢圖',
                text='請選擇:',
                actions=[
                        URIAction( 
                        label='預測房價走勢圖',
                        uri='https://0462c39ddbb2.ngrok.io/index'
                    ),
                    URIAction(
                        label='歷史房價走勢圖',
                        uri='https://0462c39ddbb2.ngrok.io/index2'
                    )
                ]
            )
        )


    elif '論壇' in text:
        message = TextSendMessage(
                        text = "請選擇想要瞭解的行政區" ,
                        quick_reply=QuickReply(
                        items=zone_forum 
                        ))
    
    #找房小幫手
    elif "小幫手" in text:   
        id=event.source.user_id
        message = TemplateSendMessage(
        alt_text='請在手機上操作', 
        template= ConfirmTemplate(
            title='這是ConfirmTemplate',
            text='請先選擇《以條件找房》或\n《推薦房屋物件》',
            actions=[
                MessageAction(
                    label='以條件找房',
                    text='以條件找房'
                ),
                MessageAction(
                    label='推薦房屋物件',
                    text='推薦房屋物件'
                )
            ]   
        )
    )


    elif "以條件找房" in text:      #改以條件找房
        id=event.source.user_id
        message = TemplateSendMessage(
        alt_text='請在手機上操作', 
        template= ConfirmTemplate(
            title='這是ConfirmTemplate',
            text='請先選擇《條件設定》 \n再選擇《找房去!》',
            actions=[
                URIAction(
                    label='條件設定',
                    uri=f'https://0462c39ddbb2.ngrok.io/format?id={id}'
                ),
                MessageAction(
                    label='找房去!',
                    text='找房去!'
                ),
            ]   
        )
    )
    
    elif '找房去' in text:
        a = red.hget_redis(redis_a=event.source.user_id, redis_b='',redis_c='',redis_d='',redis_e='',field='sinyi')
        b = red.hget_redis(redis_a=event.source.user_id, redis_b='',redis_c='',redis_d='',redis_e='',field='yungching')
        c = red.hget_redis(redis_a=event.source.user_id, redis_b='',redis_c='',redis_d='',redis_e='',field='591')

        message = TemplateSendMessage(
            alt_text='請在手機上操作',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://yt3.ggpht.com/ytc/AAUvwnhTLNHPCKTnF_VnlPHy00lwSisrnk4nV6P8wtkq=s900-c-k-c0x00ffffff-no-rj',
                        title ='信義房屋',
                        text ='房仲網',
                        actions=[
                            URIAction(
                                label='點我看房!',
                                uri= a     #連信義url
                                )
                            ]
                        ),
                    CarouselColumn(
                        thumbnail_image_url='https://hq.houseol.com.tw/images/StoreSub/1405_1.jpg',
                        title ='永慶房屋',
                        text ='房仲網',
                        actions=[
                            URIAction(
                                label='點我看房!',
                                uri= b       #連永慶url
                                )
                            ]
                        )
                    ]
                )
            )

    elif '推薦房屋物件' in text:
        message = TextSendMessage(
                        text = "請選擇以下行政區" ,
                        quick_reply = QuickReply(
                        items = zone_for_recommand
                        ))


    elif '熱門' in text:
        message = TemplateSendMessage(
            alt_text='請在手機上操作',
            template=ButtonsTemplate(
                thumbnail_image_url='https://png.pngtree.com/png-clipart/20210302/ourlarge/pngtree-statistics-clip-art-orange-gradient-chart-png-image_2986853.jpg',
                title='使用者熱門搜尋',
                text='請點選:',
                actions=[
                    URIAction(
                        label='熱門搜尋統計圖',
                        uri='https://0462c39ddbb2.ngrok.io/index3'
                    )
                ]
            )
        )


    elif '嫌惡設施' in text:
        message = TextSendMessage(
        text = "請透過下方定位搜尋附近嫌惡設施" ,
        quick_reply=QuickReply(
        items=[
            QuickReplyButton(
                action=LocationAction(
                    label="定位"
                ))
            ]
        )
    )

    else:
        message = TextSendMessage(text="請選擇功能選單")   

    line_bot_api.reply_message(
        event.reply_token, 
        message)    


@handler.add(PostbackEvent)   #負責處理送過來的資料
def postback_message(event):
    print('Postback_Event:',event)

    zone_for_price_evaluate_reset_condition =[]     
    areas = ["中正區", "大同區","中山區","松山區","大安區","萬華區","信義區","士林區","北投區","內湖區","南港區","文山區"]
    for area in areas:
        zone_for_price_evaluate_reset_condition.append(QuickReplyButton(         
                                    action=PostbackAction(
                                        label=area, 
                                        data=f"A{area}",
                                        )
                                    ))
    user_choose_for_predict ={'區域':'', '型態':'', '車位':'', '坪數':'', '屋齡':''}

    if event.postback.data[0] == "A":
        area = event.postback.data[1:]
        message = TextSendMessage(
                        text = "請選擇想瞭解的物件型態" ,
                        quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="公寓", 
                                    data= f"T公寓,{area}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="華廈", 
                                    data= f"T華廈,{area}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="電梯大樓", 
                                    data= f"T電梯大樓,{area}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="套房", 
                                    data= f"T套房,{area}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="透天厝", 
                                    data= f"T透天厝,{area}"
                                )
                            )
                        ]
                    ))

    #車位
    elif event.postback.data[0] == "T":
    
        parking = event.postback.data[1:]
        message = TextSendMessage(
                        text = "請選擇是否含車位" ,
                        quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="是", 
                                    data= f"P有,{parking}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="否", 
                                    data= f"P無,{parking}"   
                                )
                            )
                        ]
                    ))
    #坪數
    elif event.postback.data[0] == "P":
        size = event.postback.data[1:]
        message = TextSendMessage(
                        text = "請選擇坪數" ,
                        quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="10坪以下", 
                                    data= f"S0-10,{size}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="11-20坪", 
                                    data= f"S11-20,{size}"  
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="21-30坪", 
                                    data= f"S21-30,{size}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="31-40坪", 
                                    data= f"S31-40,{size}"  
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="41-50坪", 
                                    data= f"S41-50,{size}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="31-40坪", 
                                    data= f"S51-,{size}"  
                                )
                            )
                        ]
                    ))
                    
    #屋齡
    elif event.postback.data[0] == "S":
        age = event.postback.data[1:]
        message = TextSendMessage(
                        text = "請選擇屋齡" ,
                        quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="10年以下", 
                                    data= f"G0-10,{age}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="11-20年", 
                                    data= f"G11-20,{age}"  
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="21-30年", 
                                    data= f"G21-30,{age}"
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="31-40年", 
                                    data= f"G31-40,{age}"  
                                )
                            ),
                            QuickReplyButton(
                                action=PostbackAction(
                                    label="41年以上", 
                                    data= f"G41-,{age}"
                                )
                            )
                        ]
                    ))

    elif event.postback.data[0] == "G":
        user_choose_list = event.postback.data.split(',')
        user_choose_for_predict['屋齡'] = user_choose_list[0][1:]   
        user_choose_for_predict['坪數'] = user_choose_list[1]
        user_choose_for_predict['車位'] = user_choose_list[2]
        user_choose_for_predict['型態'] = user_choose_list[3]
        user_choose_for_predict['區域'] = user_choose_list[4]
    
        price_for_quickreply = red.getdata(user_choose_for_predict['區域'],user_choose_for_predict['型態'],'1', '40', '15')
        text_message  = f"- 行政區:{user_choose_for_predict['區域']} \n- 型態:{user_choose_for_predict['型態']} \n- 車位:{user_choose_for_predict['車位']} \n- 坪數:{user_choose_for_predict['坪數']}坪 \n- 屋齡:{user_choose_for_predict['屋齡']}年 \n**建議價格:{price_for_quickreply}萬 /坪**"

        message = TextSendMessage(
                text = text_message)


    elif event.postback.data == "尋找行政區":         #房價評估-> 重新設定條件  
        message = TextSendMessage(
        text = "請選擇以下行政區" ,
        quick_reply=QuickReply(
        items=zone_for_price_evaluate_reset_condition
        ))


    elif event.postback.data == "呼叫redis":
        text_message_2 = ''
        data = form_db.select_userid_form({'user_id':event.source.user_id})       
        print('data for form:', data)                             
        print('data[0]["type"]:',data[0]['type'])

        price_for_form=''
        message = []
        for i in data[0]['zone']:
            price_for_form=red.getdata(a=i['name'], b=data[0]['type'], c='1', d='40', e='15')
            text_message_2 = f"- 行政區: {i['name']} \n- 型態: {data[0]['type']} \n- 車位: {'有' if data[0]['parking']== 'yes' else '無'} \n- 坪數: 30-40坪 \n- 屋齡: 0-15年 \n建議價格:{price_for_form}萬 /坪"
            message.append(TextSendMessage(text = text_message_2))

    
    #建案論壇   
    elif event.postback.data[0] == "F":
        User_ID = event.source.user_id
        select_zone = event.postback.data[1:]
        output = nlp.all_step(select_zone)     #放User所選區域(模型無跑出資料的區域:松山X、士林X、北投X、內湖X、南港X)，不需存MySQL、Redis
        
        message = TemplateSendMessage(
            alt_text='請在手機上操作',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://icons.iconarchive.com/icons/graphicloads/flat-finance/256/like-icon.png',
                        title = f'網友正面評價-{select_zone}建案',  
                        text ='看看網友怎麼說',
                        actions=[
                            URIAction(
                                label='Moblie01',
                                uri=output[0]         #正面
                            ),
                            URIAction(
                                label='住展房仲網',
                                uri=output[2]         #正面
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://icons.iconarchive.com/icons/graphicloads/flat-finance/256/dislike-icon.png',
                        title =f'網友負面評價-{select_zone}建案',
                        text ='看看網友怎麼說',
                        actions=[
                            URIAction(
                                label='Moblie01',
                                uri=output[4]       #負面
                            ),
                            URIAction(
                                label='住展房仲網',
                                uri=output[6]       #負面
                            )
                        ]
                    )
                ]
            )
        )

    #推薦房屋物件: 第一次隨機給房屋物件
    elif event.postback.data[0] == "R":    
        User_ID = event.source.user_id 
        select_zone_for_recommand = event.postback.data[1:]    
        random_house = recommend.random_house(select_zone_for_recommand)

        caro_list_for_recomm = []
        for index,values in random_house.iterrows():
            caro_list_for_recomm.append(CarouselColumn(
                thumbnail_image_url= values['pictureurl'],
                title = values['name'],  
                text = f"台北市{values['area']}{values['road']}\n{int(values['room'])}房{int(values['hall'])}廳{int(values['bath'])}衛|{values['size']}坪|{values['year']}年|{values['type']}|{values['totalprice']}萬",   #路名
                actions=[
                    URIAction(
                        label='前往房仲網',
                        uri = values['houseLink']
                    ),
                    PostbackAction(
                    label='猜你喜歡',
                    data = f"Z{select_zone_for_recommand}, {values['id']}"
                    )
                ]
            ))

        message = TemplateSendMessage(
            alt_text='請在手機上操作',
            template=CarouselTemplate(
                columns=caro_list_for_recomm
            ))



    elif event.postback.data[0] =='Z':   #第二次推薦
        temp = event.postback.data.split(',')
        area = temp[0][1:]
        house_id = temp[1]
        print(area)
        print(int(house_id))
        similar_houses_list_2nd = recommend.recommendation(int(house_id), area)  
        print(similar_houses_list_2nd)

        caro_list_for_similar = []
        for index,values in similar_houses_list_2nd.iterrows():
            caro_list_for_similar.append(
                CarouselColumn(
                    thumbnail_image_url= values['pictureurl'],
                    title = values['name'],  
                    text = f"台北市{values['area']}{values['road']}\n{int(values['room'])}房{int(values['hall'])}廳{int(values['bath'])}衛|{values['size']}坪|{values['year']}年|{values['type']}|{values['totalprice']}萬",   #路名
                    actions=[
                        URIAction(
                            label='前往房仲網',
                            uri = values['houseLink']
                        )
                    ]
                ))

        message = TemplateSendMessage(
            alt_text='請在手機上操作',
            template=CarouselTemplate(
                columns = caro_list_for_similar
            ))    


    print('user_choose_for_predict:',user_choose_for_predict)

   
    line_bot_api.reply_message(
        event.reply_token,
        message)  

#位置訊息
@handler.add(MessageEvent, message=LocationMessage)   #負責處理送過來的資料
def handle_message1(event):
    print('LocationMessage:', event)
    print(event.source.user_id)
    latA=event.message.latitude
    lonA=event.message.longitude
    
    bad_location_list = disgust.location(latA, lonA)  #call location function
    print(bad_location_list)
    
    caro_list = []
    for index,values in bad_location_list.iterrows():
        caro_list.append(CarouselColumn(
            thumbnail_image_url='https://png.pngtree.com/element_our/png_detail/20181010/attention-please-concept-of-important-announcement-human-hands-hold-caution-png_133094.jpg',
            title =values['name'],  
            text =values['addr'], 
            actions=[
                URIAction(
                    label= f"前往約{values['two_point_distances']}m",
                    uri= f"http://maps.google.com/maps?saddr={latA},{lonA}&daddr={values['altitude']},{values['long']}"
                )
            ]
        ))
        
    message = TemplateSendMessage(
            alt_text='請在手機上操作',
            template=CarouselTemplate(
                columns=caro_list
            ))
  
   
    line_bot_api.reply_message(
        event.reply_token,
        message)

if __name__ == "__main__":
    app.run()
