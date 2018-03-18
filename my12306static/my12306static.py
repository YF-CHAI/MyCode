# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 21:29:59 2018

@author: DELL
"""

import urllib, urllib2, sys
import ssl
import json
import xlwt
import xlrd
import xlutils
from xlrd import open_workbook
from xlutils.copy import copy

import time
import random
import os #判断数据文件是否存在
#import chardet

class train_info:
    def __init__(self):
        self.train_num = ''
        self.travel_time = 0

def getQuoteFromStr(str):
    str = urllib.quote(str)
    print(str+' from getQuoteFromStr')
    return str

def joinFromToStringQuery(date_time,from_A,to_B):
    from_A = urllib.quote(from_A)
    to_B = urllib.quote(to_B)
    #query_str = 'date='+date_time+'&from='+from_A+'&to='+to_B
    query_str = 'date='+date_time+'&end='+to_B+'&start='+from_A
    #print(query_str)
    return query_str


def readCityNamefromFile(file_name):
    city_list = []
    with open(file_name,'r+') as f:
        try:
            for line in f.readlines():
                city = line.strip()
                city_list.append(city)
                
            for i in range(len(city_list)):
                print(city_list[i])
                #print('hello')
                
        finally:
            f.close()
            return city_list


def get_content(querys):
    #host = 'https://tra.market.alicloudapi.com'
    #path = '/train'
    host = 'http://jisutrain.market.alicloudapi.com'
    path = '/train/ticket'
    method = 'GET'
    appcode = 'eb9d746752ce449a915f193b1e2f4e9e'
    bodys = {}
    url = host + path + '?' + querys
    request = urllib2.Request(url)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    #ctx = ssl.create_default_context()
    #ctx.check_hostname = False
    #ctx.verify_mode = ssl.CERT_NONE
    #response = urllib2.urlopen(request, context=ctx)
    #利用多次循环结构处理urlopen的异常
    #！！！！！！！！！！！！！！！！！！！！！！！！！#
    try_num = 50#尝试连接url五次，避免网络不稳定的异常
    data = '{"status":"203","msg":"没有信息","result":""}'
    for try_num in range(try_num):
    #while True:
        try:
            
            response = None
            response = urllib2.urlopen(request)
            content = response.read()
            response.close()
            #print(content)
            #code = chardet.detect(content)
            #print(code)
            data = json.loads(content,encoding="UTF-8")            
            #time.sleep(random.randint(1,3))
            #time.sleep(1)
            return data
        except urllib2.URLError as e:  
            if hasattr(e, "code"): 
                #print "The server couldn't fulfill the request"  
                print "Error code:", e.code  
                print "Return content:", e.read()
                #time.sleep(1)
                if(response != None):
                    response.close()
            elif hasattr(e, "reason"):  
                #print "Failed to reach the server"  
                print "The reason:", e.reason 
                #time.sleep(random.randint(1,3))
                #time.sleep(1)
                if(response != None):
                    response.close()
            else:
                if(response != None):
                    response.close()
    return None

        #except:
            #print('get_content():something has wrong')
            #time.sleep(random.randint(1,3))
            #continue
        #finally:
            #print('I have tried 3 times, it still not work')
            #return None
        
#找到两站点之间包含有“C,D,G”的最短时间的车次和花费时间        
def findThefitdata(data):
    if data == None:
        Nodata = train_info()
        Nodata.train_num = 'NotExist'
        Nodata.travel_time = 99999
        return Nodata

    query_result = data['result']
    fastTrainNum = 'NotExist'
    fastTrainTime = 99999 #MAX Travel time about a week, use as Marco
    #print(query_result)
    for each_item in query_result:
        total_time = each_item['costtime']
        train_number = each_item['trainno']
        #print(isinstance(train_number,unicode))#to test train_number是否是Unicode类型
        time_str = unicode(total_time).encode("utf-8")#将总时间转为str
        time_total_int = totalTimeStrToint(time_str)
        tn_str = unicode(train_number).encode("utf-8")#将uniconde转为str
        if tn_str.find('G')!=-1:
            if time_total_int < fastTrainTime:
                fastTrainNum = tn_str
                fastTrainTime = time_total_int
                continue
                
        elif tn_str.find('D')!=-1:
            if time_total_int < fastTrainTime:
                fastTrainNum = tn_str
                fastTrainTime = time_total_int
                continue
     
        elif tn_str.find('C')!=-1:
            if time_total_int < fastTrainTime:
                fastTrainNum = tn_str
                fastTrainTime = time_total_int
                continue
    
    #print(fastTrainNum,fastTrainTime)
    tmp = train_info()
    tmp.train_num = fastTrainNum
    tmp.travel_time = fastTrainTime
    return tmp

            
    
    #first = query_result[0]['totalTime']
    #print(first)
    
def totalTimeStrToint(totalTime_str):
    #total_str = str(totalTime_str)
    hour = totalTime_str.split(':')[0]
    minitue = totalTime_str.split(':')[1]
    #print(hour)
    #print(minitue)
    totalTime = int(hour)*60 + int(minitue)
    #print('The total time is: '+str(totalTime))
    return totalTime
    

#TODO:将totalTime返回的字符串时间变成整型时间----OK
    
#TODO：根据totalTime以及列车编号(C,D,G)筛选所需条目----OK
    
#TODO：通过遍历capitalCity_list来得到站点i到其他n-1个站点的最短时间(C,D,G)

#作为主函数来用
def get_train_infoto_file():
    file_name = 'province_name.txt'
    data_file = 'static_data.xls'
    capitalCity_list = readCityNamefromFile(file_name) 
    #for i in range(len(capitalCity_list)):
    #for j in range(len(capitalCity_list)):
    #wb = xlwt.Workbook()
    #sh = wb.add_sheet('train_info')
    if os.path.isfile(data_file) == False:
        wb = xlwt.Workbook()
        sh = wb.add_sheet('train_info')
        for q in range(len(capitalCity_list)):
            sh.write(0,q+1,capitalCity_list[q].decode("utf-8"))
            sh.write(q+1,0,capitalCity_list[q].decode("utf-8"))
        wb.save(data_file)
    rb = xlrd.open_workbook(data_file)
    rs = rb.sheet_by_index(0)
    wb = copy(rb)
    ws = wb.get_sheet(0)
    for i in range(len(capitalCity_list)):
        for j in range(len(capitalCity_list)):
            if i != j:
                #print('From:{0},To:{1}'\
                      #.format(capitalCity_list[i],capitalCity_list[j]))
                datetime = '2018-03-18'
                querys = joinFromToStringQuery(datetime,\
                                capitalCity_list[i],\
                                capitalCity_list[j])
                tinfo = train_info()
                data = get_content(querys)
                tinfo = findThefitdata(data)
                print('From:{0},To:{1},fastest No.:{2},time:{3} min'\
                      .format(capitalCity_list[i],\
                              capitalCity_list[j],\
                              tinfo.train_num,\
                              tinfo.travel_time))
                ws.write(i+1,j+1,tinfo.travel_time)
    wb.save(data_file) 
    print('mission complete!\n')
                


#main() function 
if __name__ == '__main__':
    get_train_infoto_file()



