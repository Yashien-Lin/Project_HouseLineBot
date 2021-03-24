import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt, ceil
import math
import time

def getDistance(latA, lonA, latB, lonB):
    ra = 6378140  # 赤道半徑
    rb = 6356755  # 極半徑
    flatten = (ra - rb) / ra  # Partial rate of the earth
    # change angle to radians
    radLatA = math.radians(latA)
    radLonA = math.radians(lonA)
    radLatB = math.radians(latB)
    radLonB = math.radians(lonB)

    pA = math.atan(rb / ra * math.tan(radLatA))
    pB = math.atan(rb / ra * math.tan(radLatB))
    x = math.acos(math.sin(pA) * math.sin(pB) + math.cos(pA) * math.cos(pB) * math.cos(radLonA - radLonB))
    c1 = (math.sin(x) - x) * (math.sin(pA) + math.sin(pB)) ** 2 / math.cos(x / 2) ** 2
    c2 = (math.sin(x) + x) * (math.sin(pA) - math.sin(pB)) ** 2 / math.sin(x / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (x + dr)
    # print(distance)
    distance = round(distance,2)
    return int(distance)

def location(latA, lonA):
    
    df = pd.read_csv('./mergeTemp.csv')
    df['two_point_distances']=df.apply(lambda ser: getDistance(latA,lonA, ser['altitude'], ser['long']),axis=1)
    df = df.sort_values(by=['two_point_distances'])

    # print(df.head(10))


    # bad_list = []
    x = df[df['two_point_distances']<=1000]
    return x.head(10)

# print(abc(25.05078885080105, 121.57780434643969))

# for index,i in x.iterrows():
#     row = i['name'],i['addr'],i['two_point_distances']
    # bad_list.append(list(row))

# print(bad_list)
# print(bad_list[4][0])