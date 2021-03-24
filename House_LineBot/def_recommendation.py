import pandas as pd
from sklearn import preprocessing
from sklearn.metrics.pairwise import euclidean_distances

#設定他
def recommendation(idd ,area):
    
    # data = pd.read_csv("./sinyi_clean.csv")
    # data1 = data[["size", "totlefloor", "floor", "year", "room", "hall", "bath", "unitprice"]]
    data = pd.read_csv("./house3_all.csv")
    data = data[data['area'] == area]
    data = data.drop(data[data['floor'].str.count(r'(^B.*)')==1].index).reset_index()
    data1 = data[["size", "totlefloor", "floor", "year", "room", "hall", "bath","totalprice"]].fillna(0)
    #找出input的id的index
    input_index = data[data['id'] == idd].index.item()
    
    
    ###做標準化
    #建立MinMaxScaler物件
    minmax = preprocessing.MinMaxScaler()
    # 資料標準化
    data_minmax = minmax.fit_transform(data1)
    # data_minmax_dataframe = pd.DataFrame(data_minmax, columns = ["size", "totlefloor", "floor", "year", "room", "hall", "bath", "unitprice"])
    data_minmax_dataframe = pd.DataFrame(data_minmax, columns = ["size", "totlefloor", "floor", "year", "room", "hall", "bath", "totalprice"])
    
    
    ###計算歐式距離
    idd = []
    houseLink = []
    pictureurl = []
    name = []
    values = [] 
    area = []
    road = []
    room = []
    hall = []
    bath = []
    size = []
    year = []
    house_type = []
    totalprice = []
    for i in range(0, len(data_minmax_dataframe)):
        if i is not input_index:
            idd.append(data["id"][i])
            houseLink.append(data["houseLink"][i])
            pictureurl.append(data["pictureurl"][i])
            name.append(data['name'][i])
            area.append(data['area'][i])
            road.append(data['road'][i])
            room.append(data['room'][i])
            hall.append(data['hall'][i])
            bath.append(data['bath'][i])
            size.append(data['size'][i])
            year.append(data['year'][i])
            house_type.append(data['type'][i])
            totalprice.append(data['totalprice'][i])
            value = euclidean_distances(data_minmax_dataframe.values[input_index].reshape(1,-1), data_minmax_dataframe.values[i].reshape(1,-1))[0][0]
            values.append(value)

    column = ['id','houseLink', 'pictureurl', 'name','value']  # 'size','room','hall', 'bath'
    df = pd.DataFrame(columns = column)

    df['id'] = idd
    df['houseLink'] = houseLink
    df['pictureurl'] = pictureurl
    df['name'] = name
    df['value'] = values  
    df['area'] = area
    df['road'] = road
    df['room'] = room
    df['hall'] = hall
    df['bath'] = bath
    df['size'] = size
    df['year'] = year
    df['type'] = house_type
    df['totalprice'] = totalprice

    
    # df = data[data['id'] == df['id']][['area','road','room','hall','bath','size','year','type','totalprice']]

    # f"台北市{values['area']}{values['road']}\n{int(values['room'])}房{int(values['hall'])}廳{int(values['bath'])}衛|{values['size']}坪|{values['year']}年|{values['type']}|{values['totalprice']}萬",
    
    
    ###計算前3名
    id_output = df.nsmallest(3,'value')['id'].tolist()
    houseLink_output = df.nsmallest(3,'value')['houseLink'].tolist()
    pictureurl_output = df.nsmallest(3,'value')['pictureurl'].tolist()
    value_output = df.nsmallest(3,'value')['value'].tolist()
    
    top_1_id = id_output[0]
    top_1_houseLink = houseLink_output[0]
    top_1_pictureurl = pictureurl_output[0]
    top_1_value = value_output[0]
    
    top_2_id = id_output[1]
    top_2_houseLink = houseLink_output[1]
    top_2_pictureurl = pictureurl_output[1]
    top_2_value = value_output[1]
    
    
    top_3_id = id_output[2]
    top_3_houseLink = houseLink_output[2]
    top_3_pictureurl = pictureurl_output[2]
    top_3_value = value_output[2]


    # return (top_1_id, top_1_houseLink, top_1_pictureurl, top_1_value, top_2_id, top_2_houseLink, top_2_pictureurl, top_2_value, top_3_id, top_3_houseLink, top_3_pictureurl, top_3_value)
    return df.sort_values(by=['value']).head(3).reset_index()
    
def random_house(area=None):
    data = pd.read_csv("./house3_all.csv")
    if area :
        return data[data['area'] == area ].sample(n=3)
    else:
        return data.sample(n=3)
if '__main__' ==__name__:
    print(recommendation(30,'內湖區'))
    # print(random_house())
    # print(random_house('內湖區'))


# print(recommendation(10))
# print(recommendation(15))

#使用他

##假設使用者選擇的房屋ID
# houseID = "60359D"
# houseID = 10
# result = recommendation(houseID)
# print(result)


# ##top1 id, houseLink, pictureurl, value
# print(result[0], result[1], result[2], result[3])


# ##top2 id, houseLink, pictureurl, value
# print(result[4], result[5], result[6], result[7])


# ##top3 id, houseLink, pictureurl, value
# print(result[8], result[9], result[10], result[11])