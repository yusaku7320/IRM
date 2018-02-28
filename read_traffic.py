# -*- coding: shift_jis -*-
from xml.etree import ElementTree
import pandas as pd
from numpy import *
traffic_list = {}
data = []
columns =[]
count = 0
index = []
traffic = ElementTree.parse('traffic.xml')#読み取らせる
root = traffic.getroot()
print(root.tag)
print(root.attrib)
for child in root:
    print(child.tag)
child = root.find("IntraTM")
print(child.attrib)
for grandchild in child:
    id1 = int(grandchild.attrib["id"])
    count += 1
    print("grandchild:",id1)
    for great_grandchild in grandchild:
        id2 = int(great_grandchild.attrib["id"])
        print("great_grandchild:",id2)
        print(great_grandchild.text)
        traffic_list[id1,id2]=float(great_grandchild.text)
print(traffic_list)
for i in range(1,count+1):
    columns.append(i)
    index.append(i)
    list = []
    for j in range(1,count+1):
        cheak = traffic_list.get((i,j), None)
        if cheak == None:
            traffic_list[i,j] = 0
        list.append(traffic_list[i,j])
    data.append(list)
print(data)
df = pd.DataFrame(data,columns,index)
print(df)
df.to_csv("traffic_model.csv")
