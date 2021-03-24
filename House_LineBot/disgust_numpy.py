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
    distance = round(distance, 4)
    return str(distance)

def getDistancesres(latA, lonA, latB, lonB, check):
    result = []
    for x in range(len(latA.split(';'))):
        value = getDistance(float(latA.split(';')[x]), float(lonA.split(';')[x]), float(latB), float(lonB))
        if  check > float(value):
            result.append(value)
    
    return ';'.join(result)
    # return False if len(result)==0 else True

# def getDistancescheck(latA, lonA, latB, lonB, check):
#     result = []
#     for x in range(len(latA.split(';'))):
#         value = getDistance(float(latA.split(';')[x]), float(lonA.split(';')[x]), float(latB), float(lonB))
#         if  check > float(value):
#             result.append(value)
    
#     # return ';'.join(result)
#     return False if len(result)==0 else True


path  = './data/disgus/'
pathCount = './data/count/'
pathMerge = path+'merge/'  
for i in range(14,15):
    left = pd.read_csv('./data/temp/address{}0001_{}0000.csv'.format(i,i+1))
    right = pd.read_csv(pathMerge+'mergeTemp.csv')
    for i in right:
    # m = pd.concat([pd.concat([left]*len(right)).sort_index().reset_index(drop=True),pd.concat([right]*len(left)).reset_index(drop=True) ], 1)
    m=pd.DataFarm()
    starttime=time.time()
    m['distancess']=m.apply(lambda ser: getDistancesres(str(ser['Response_Y']), str(ser['Response_X']), str(ser['altitude']), str(ser['long']),ser['distance']),axis=1)
    # m['distance-true']=m.apply(lambda ser: getDistancescheck(str(ser['Response_Y']), str(ser['Response_X']), str(ser['altitude']), str(ser['long']),ser['distance']),axis=1)
    endtime=time.time()
    cost_time = endtime - starttime
    print('处理完成，程序运行时间： {}秒'.format(float('%.2f' % cost_time)))

    indexNames = m[m['distancess']==False].index
    print(indexNames)
    m.drop(indexNames, inplace=True)

    m.to_csv('./data/tempout/address{}0001_{}0000_x2.csv'.format(i,i+1),index=False)
