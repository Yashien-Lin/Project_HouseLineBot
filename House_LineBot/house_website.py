def format_form_url(formRequest):


    #行政區
    sinyi_zone = {'中正區': '100', '松山區': '105', '信義區': '110', '大同區': '103', '內湖區': '114', '大安區': '106', '士林區': '111', '南港區': '115', '中山區': '104', '萬華區': '108', '北投區': '112', '文山區': '116'}

    yungching_zone = {'中正區': '台北市-中正區', '松山區': '台北市-松山區', '信義區': '台北市-信義區', '大同區': '台北市-大同區', '內湖區': '台北市-內湖區', '大安區': '台北市-大安區', '士林區': '台北市-士林區', '南港區': '台北市-南港區', '中山區': '台北市-中山區', '萬華區': '台北市-萬華區', '北投區': '台北市-北投區', '文山區': '台北市-文山區'}

    house591_zone = {'區域不限': '', '中正區': '1', '大同區': '2', '中山區': '3', '松山區': '4', '大安區': '5', '萬華區': '6', '信義區': '7', '士林區': '8', '北投區': '9', '內湖區': '10', '南港區': '11', '文山區': '12'}

    #型態
    sinyi_type = {'型態不限': '',
    '公寓': 'apartment',
    '華廈': 'huaxia',
    '電梯大樓': 'dalou',
    '套房': 'flat',
    '別墅': 'townhouse-villa',
    '透天厝': 'townhouse-villa'}
    yungching_type = {'型態不限': '', '公寓': '無電梯公寓', '華廈': '電梯大廈', '電梯大樓': '電梯大廈','套房': '','透天厝': '透天別墅', '別墅': '透天別墅'}
    house591_type = {'型態不限': '0', '公寓': '1', '華廈': '2', '電梯大樓': '2', '透天厝': '3', '別墅': '4', '套房': ''}

    #座向
    sinyi_direction = {'朝東': 'east', '朝南': 'south', '朝北': 'north', '朝西': 'west', '朝東南': 'easts', '朝東北': 'eastn', '朝西南': 'wests', '朝西北': 'westn'}
    yungching_direction = {'朝西': '西', '朝東': '東', '朝北': '北', '朝南': '南', '朝西北': '西北', '朝東北': '東北', '朝東南': '東南', '朝西南': '西南'}
    house591_direction = {'朝西': '1', '朝東': '2', '朝北': '3', '朝南': '4', '朝西北': '5', '朝東北': '6', '朝東南': '7', '朝西南': '8'}

    #設施
    sinyi_facility = {'無障礙空間': '15', '近捷運': '17', '近學校': '19', '近公園': '16', '近市場': '18','近醫療機構':''}
    yungching_facility = {'近公園': '近公園', '近捷運': '近捷運','近市場': '近市場', '近學校': '近學校', '近醫療機構': '近醫療機構','無障礙空間':''}
    house591_facility = {'近公園': 'park', '近市場': 'market', '近學校': 'school', '近醫療機構': 'hospital', '無障礙空間': '', '近捷運': ''}


    sinyi_type_all=list()
    yungching_type_all=list()
    house591_type_all=list()

    sinyi_parking = ''
    yungching_parking = ''

    sinyi_direction_all=list()
    yungching_direction_all=list()
    house591_direction_all=list()

    sinyi_floor_all=[]
    yungching_floor_all=[]
    house591_floor_all=[]

    sinyi_room_all=[]
    yungching_room_all=[]
    house591_room_all=[]

    sinyi_facility_all=[]
    yungching_facility_all=[]
    house591_facility_all=[]

    sinyi_price_all= []
    yungching_price_all= []
    house591_price_all= []

    sinyi_size_all= []
    yungching_size_all= []
    house591_size_all= []

    sinyi_age_all= []
    yungching_age_all= []
    house591_age_all= []

    sinyi_zone_all= []
    yungching_zone_all= []
    house591_zone_all= []

    consumer = [{"user_id":"", "type":[],"parking":"", "direction":[], "floor_lower":"", "floor_upper":"","room_lower":"", "room_upper":"", "facility":[], "size_lower":"", "size_upper":"", "age_lower":"",
 "age_upper":"","zone":[]}]

    all_key=['type','parking','direction','floor_lower','floor_upper','room_lower','room_upper'
    ,'facility', 'price_lower', 'price_upper' ,'size_lower','size_upper','age_lower','age_upper','zone']
    ##這個要先加

    house591_room_all_StrInList=[]
    room_upper=0
    room_lower_591=1
    value=''
    for key in all_key:
        if key == 'type':
            for value in formRequest.getlist(key):
                if sinyi_type[value] not in sinyi_type_all:
                    sinyi_type_all.append(sinyi_type[value])
                if yungching_type[value] not in yungching_type_all:
                    yungching_type_all.append(yungching_type[value])
                if house591_type[value] not in house591_type_all:
                    house591_type_all.append(house591_type[value])
        
        elif key =='parking': 
            value = formRequest.get(key)
            if value == 'yes':
                sinyi_parking ='plane-auto-mix-mechanical-firstfloor-tower-other-yesparking/'
                yungching_parking = 'y_park/'
            elif value == 'no':
                sinyi_parking = 'noparking/'
                yungching_parking = 'n_park/'
        
        elif key == 'direction':
            for value in formRequest.getlist(key):
                sinyi_direction_all.append(sinyi_direction[value])
                yungching_direction_all.append(yungching_direction[value])
                house591_direction_all.append(house591_direction[value])
        
        elif key == 'floor_lower':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_floor_all.append(value)
            yungching_floor_all.append(value)
            house591_floor_all.append(value)
        elif key == 'floor_upper':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_floor_all.append(value)
            yungching_floor_all.append(value)
            house591_floor_all.append(value)
        
        elif key == 'room_lower':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_room_all.append(value)
            yungching_room_all.append(value)
            room_lower_591 = int(value)

        elif key == 'room_upper':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_room_all.append(value)
            yungching_room_all.append(value)
            # room_upper = int(value)
            if int(value) >5:
                value = "5" 
            for i in range(room_lower_591 ,int(value) + 1):
                house591_room_all.append(i)
            house591_room_all_StrInList = list("".join('%s' %id for id in house591_room_all)) #遍歷list的元素，把他轉化成字串
            # print(value)
            # print(type(value))
            # print('house591_room_all:',house591_room_all)
            # print('room lower:', room_lower_591)

        elif key == 'facility':
            for value in formRequest.getlist(key):
                sinyi_facility_all.append(sinyi_facility[value]) if sinyi_facility[value] !='' else None
                yungching_facility_all.append(yungching_facility[value]) if yungching_facility[value] !='' else None
                house591_facility_all.append(house591_facility[value]) if house591_facility[value] !='' else None        
            if '無障礙空間' in value:
                yungching_facility_all.append("_sp/_as/")
            else:
                yungching_facility_all.append("_sp/")

        elif key == 'size_lower':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_size_all.append(value)
            yungching_size_all.append(value)
            house591_size_all.append(value)
        elif key == 'size_upper':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_size_all.append(value)
            yungching_size_all.append(value)
            house591_size_all.append(value)

        elif key == 'age_lower':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_age_all.append(value)
            yungching_age_all.append(value)
            house591_age_all.append(value)

        elif key == 'age_upper':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_age_all.append(value)
            yungching_age_all.append(value)
            house591_age_all.append(value)  

        elif key == 'zone':
            for value in formRequest.getlist(key):
                sinyi_zone_all.append(sinyi_zone[value])
                yungching_zone_all.append(yungching_zone[value])
                house591_zone_all.append(house591_zone[value])           



        elif key == 'price_lower':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_price_all.append(value)
            yungching_price_all.append(value)
            house591_price_all.append(value)  

        elif key == 'price_upper':
            value = formRequest.get(key)
            if value == '':
                continue
            sinyi_price_all.append(value)
            yungching_price_all.append(value)
            house591_price_all.append(value)  
   
    # print(sinyi_zone_all)
    sinyi_type_all_connect= '-'.join(sinyi_zone_all) + '-zip/' + '-'.join(sinyi_price_all) + '-price/' + '-'.join(sinyi_type_all) + "-type/" + '-'.join(sinyi_size_all) + "-area/" + '-'.join(sinyi_age_all) + "-year/" + '-'.join(sinyi_room_all) + '-room/' + '-'.join(sinyi_facility_all) + '-tags/' + '-'.join(sinyi_direction_all) + '-house-front/' + '-'.join(sinyi_floor_all) + '-floor/' + sinyi_parking
    yungching_type_all_connect=','.join(yungching_zone_all) + '_c/' + '-'.join(yungching_price_all) + '_price/' + '-'.join(yungching_size_all) + "_pin/" + '-'.join(yungching_age_all) + "_age/" + ','.join(yungching_type_all) + "_type/" + ','.join(yungching_direction_all) + '_dt/' + '-'.join(yungching_floor_all) + '_fr/' + '-'.join(yungching_room_all) + '_rm/' + yungching_parking + ','.join(yungching_facility_all)
    house591_type_all_connect='&shape=' + ','.join(house591_type_all) + "&direction=" + ','.join(house591_direction_all) + "&pattern=" + ','.join(house591_room_all_StrInList) + '&floor=' +'$_'.join(house591_floor_all)+'$' + "&life=" + ','.join(house591_facility_all) + "&price=" + '$_'.join(house591_price_all)+'$' + "&houseage=" + "$_".join(house591_age_all) + "$" + "&area=" + "$_".join(house591_size_all) + "$" + "&section=" + ','.join(house591_zone_all)    
                                                                                                                                                                                                                                                                                                                                                      
    
    sinyi_url = "https://www.sinyi.com.tw/buy/list/{}Taipei-city/Taipei-R-mrtline/03-mrt/default-desc/index".format(sinyi_type_all_connect)
    yungching_url = "https://buy.yungching.com.tw/region/{}".format(yungching_type_all_connect)
    house591_url = "https://sale.591.com.tw/?shType=list&regionid=1" + house591_type_all_connect 


    # print(sinyi_url)
    # print(yungching_url)
    # print(house591_url)
    return  sinyi_url,yungching_url,house591_url