# -*- coding: shift_jis -*-
from numpy.random import *
from numpy import *
import math
import pandas as pd
from copy import deepcopy
from gurobipy import *
from collections import OrderedDict
class cluster_class:
	def __init__(self,id,node):
		self.id = id
		self.node_list = [node.name]
		self.cluster_map = []
		self.type = node.type
	def add_node(self,node):
		self.node_list.append(node.name)
	def __repr__(self):
		return str(self.__dict__)

	def __str__(self):
		return str(self.__dict__)
class node_class:
	def __init__(self,name,type):
		self.name = name
		self.cluster_id = None
		self.type = type
	def __repr__(self):
		return str(self.__dict__)
	def __str__(self):
		return str(self.__dict__)
	def belong(self,cluster):
		self.cluster_id = cluster.id
def draw(traffic_list,columns,index):
		list = []
		for i in columns:
			traffic = []
			for j in index:
				traffic.append(traffic_list[i,j])
			list.append(traffic)
		df_sample = pd.DataFrame(list).T
		df_sample.columns = columns
		df_sample.index = index
		print(df_sample)
		print()
def draw_cluster(cluster_list_row,cluster_list_column,traffic_list):
	columns = []
	index = []
	list = []
	for cluster in cluster_list_row:
		index += ["-"]
		index += cluster.node_list
	for cluster in cluster_list_column:
		columns += ["|"]
		columns += cluster.node_list
	for i in columns:
		traffic = []
		for j in index:
			if i == "|":
				traffic.append("|")
			else:
				if j == "-":
					traffic.append("-")
				else:
					traffic.append(traffic_list[j,i])
		list.append(traffic)
	df_cluster = pd.DataFrame(list).T
	df_cluster.columns = columns
	df_cluster.index = index
	print(df_cluster)
	df_cluster.to_csv("result.csv")
	print()
def traffic_threshold(link,threshold):
	traffic_list = OrderedDict()
	for i,j in link.keys():
		if link[i,j] >= threshold:
			traffic_list[i,j] = 1
		else:
			traffic_list[i,j] = 0
	return traffic_list
def CRP(traffic_list,node_list,cluster_list,alpha):
	for number,node in enumerate(node_list.values()):
		if len(cluster_list) == 0:#テーブルが0のとき
			cluster_list.append(cluster_class( len(cluster_list), node))#新規クラスタ作成
			node.belong(cluster_list[-1])#ノードにクラスタIDを保存
			continue
		else:
			prob_total = 0.0
			prob_list = []
			for cluster in cluster_list:
				node_sum = len(cluster.node_list)#クラスタに所属しているノード数
				exit_prob = float(node_sum/(alpha + number))#numberは現在のノードのIDを示すため、number+1で現在のノード数になる
				prob_list.append(exit_prob)
				prob_total += exit_prob
			new_prob = float(alpha) / (alpha + number )
			prob_list.append(new_prob)
			prob_total += new_prob
			clustering(node,cluster_list,prob_list,prob_total)



def CRP_update(node_list,cluster_list1,cluster_list2,traffic_list,alpha,beta):
	key_list = []
	for key in node_list.keys():
		key_list.append(key)
	key = random.choice(key_list)#ノードリストからランダムにノードを選択
	node = node_list[key]
	cluster_delete(node,cluster_list1,node_list)#ノードを所属クラスタから離脱
	prob_list,prob_total  = exit_prob(node,cluster_list1,cluster_list2,traffic_list,node_list,alpha,beta)
	new_prob = new_probability(node,cluster_list1,traffic_list,node_list,alpha,beta)
	prob_list.append(new_prob)
	prob_total += new_prob
	clustering(node,cluster_list1,prob_list,prob_total)

def clustering(node,cluster_list,prob_list,prob_total):
	p = random.uniform(0, prob_total)
	prob_sum = 0
	for id,prob in enumerate(prob_list):
		prob_sum += prob
		if p < prob_sum:
			if id != (len(prob_list) - 1 ):
				node.belong(cluster_list[id])
				cluster_list[id].add_node(node)
				break
			else:
				cluster_list.append(cluster_class(id,node))
				node.belong(cluster_list[-1])
def new_probability(node,cluster_list,traffic_list,node_list,alpha,beta):
	new_prob = 1
	for cluster in cluster_list:
		node_count0,node_count1 = node_link_cheak(node,cluster,traffic_list)#ノードとクラスタのリンク数のカウント
		new_x = beta_function(beta + node_count1, beta + node_count0 )
		new_y = beta_function(beta,beta)
		new_prob = new_prob * (new_x/new_y)
	new_z = alpha/(len(node_list) -1 + alpha)
	new_prob = new_z * new_prob
	return new_prob
def exit_prob(node,cluster_list1,cluster_list2,traffic_list,node_list,alpha,beta):
	prob_list = []
	prob_total = 0
	for cluster1 in cluster_list1:
		prob = 1
		for cluster2 in cluster_list2:
			node_count0,node_count1 = node_link_cheak(node,cluster2,traffic_list)#ノードとクラスタのリンク数のカウント
			cluster_count0,cluster_count1 = cluster_link_cheak(cluster1,cluster2,traffic_list)#クラスタとクラスタのリンク数のカウント
			x = beta_function(beta + node_count1 + cluster_count1 , beta+ node_count0 + cluster_count0)
			y = beta_function(beta + cluster_count1 , beta + cluster_count0)
			prob = prob * (x/y)
		z = len(cluster1.node_list)/(len(node_list) -1 + alpha)
		prob = prob* z
		prob_list.append(prob)
		prob_total += prob
	return prob_list,prob_total
def beta_function(a,b):
	beta = math.gamma(a) * math.gamma(b) / math.gamma(a + b)#ベータ関数beta(a,b)
	return beta
def cluster_link_cheak(cluster1,cluster2,node_list):
	count0 = 0
	count1 = 0
	if cluster1.type == "row":
		for name1 in cluster1.node_list:
			for name2 in cluster2.node_list:
				link = traffic_list[name1,name2]
				if link == 0:
					count0 += 1
				elif link == 1:
			 		count1 += 1
	if cluster1.type == "column":
		for name1 in cluster1.node_list:
			for name2 in cluster2.node_list:
				link = traffic_list[name2,name1]
				if link == 0:
					count0 += 1
				elif link == 1:
			 		count1 += 1
	return count0,count1
def node_link_cheak(node,cluster,traffic_list):
	count0 = 0
	count1 = 0
	if node.type == "row":
		for name in cluster.node_list:
			link = traffic_list[node.name,name]
			if link == 0:
				count0 += 1
			elif link == 1:
				count1 += 1
	if node.type == "column":
		for name in cluster.node_list:
			link = traffic_list[name,node.name]
			if link == 0:
				count0 += 1
			elif link == 1:
				count1 += 1
	return count0,count1
def cluster_delete(node,cluster_list,node_list):
	id = node.cluster_id#ノードが所属しているクラスタのID
	cluster_list[id].node_list.remove(node.name)#ノードを削除
	node.cluster_id = None
	if len(cluster_list[id].node_list) == 0: #ノード数が0になったらクラスタ削除
		del cluster_list[id] #クラスタを削除
		for cluster in cluster_list:#各クラスタのidを更新
			cluster.id = cluster_list.index(cluster)
			for node_id in cluster.node_list:
				node_list[node_id].cluster_id = cluster.id#各ノードの所属クラスタのidを更新
def after_prob(node_list_row,node_list_column,cluster_list_row,cluster_list_column,traffic_list,alpha,beta):
	cluster_prob_row = cluster_probability(cluster_list_row,node_list_row,alpha)#P(S1|α)の確率
	cluster_prob_column = cluster_probability(cluster_list_column,node_list_column,alpha)#P(S1|α)の確率
	beta_prob = 1#総乗の計算のため1
	for cluster1 in cluster_list_row:
		for cluster2 in cluster_list_column:
			cluster_count0,cluster_count1 = cluster_link_cheak(cluster1,cluster2,traffic_list)
			x = beta_function(cluster_count1 + beta , cluster_count0 + beta)
			y = beta_function(beta , beta)
			beta_prob = beta_prob * x/y
	prob = cluster_prob_row * cluster_prob_column * beta_prob
	return prob
def cluster_probability(cluster_list,node_list,alpha):
	x=1#総乗のため1にする
	y=1#階乗のため1にする
	for cluster in cluster_list:
		x = x * math.factorial(len(cluster.node_list)-1)
	for i in range(len(node_list)):
		y = y * (alpha + i )
	prob = (alpha ** len(cluster_list)) * x/y
	return prob
def kanto():
	return pd.read_csv("kanto_traffic.csv")
def kansai():
	return pd.read_csv("kansai_traffic.csv")
def kanto_kansai():
	return pd.read_csv("kanto_kansai_traffic.csv",index_col=0)
def draw_map(cluster_list_row,cluster_list_column,traffic_list,beta):
	columns = []
	index = []
	list = []
	for cluster in cluster_list_row:
		index += ["-"]
		index += [cluster.id]
	for cluster in cluster_list_column:
		columns += ["|"]
		columns += [cluster.id]
	for i in columns:
		traffic = []
		for j in index:
			if i == "|":
				traffic.append("|")
			else:
				if j == "-":
					traffic.append("-")
				else:
					cluster_MAP = MAP(cluster_list_row[int(j)],cluster_list_column[int(i)],traffic_list,beta)
					traffic.append(cluster_MAP)
		list.append(traffic)
	df_map = pd.DataFrame(list).T
	df_map.columns = columns
	df_map.index = index
	print(df_map)
	df_map.to_csv("map.csv")
	print()
def MAP(cluster1,cluster2,traffic_list,beta):
	count0,count1 = cluster_link_cheak(cluster1,cluster2,traffic_list)
	x = count1 + beta
	y = count0 + count1 + 2*beta
	cluster1.cluster_map.append(x/y)
	return x/y
def optimization(cluster1,cluster2):
	model = Model("map")
	list = []
	x,y,t = {},{},{}
	I = len(cluster1)
	J = len(cluster2)
	for cluster in cluster1:
		for id,prob in enumerate(cluster.cluster_map):
			t[cluster.id,id] = prob
	for j in range(J):
		for i in range(I):
			x[i,j] = model.addVar(vtype = "B")
	for i in range(I):
		for j in range(J):
			y[j,i] = model.addVar(vtype = "B")

	model.update()

	for i in range(I):
		model.addConstr(quicksum(x[i,j] for j in range(J)) == 1)
	for j in range(J):
		model.addConstr(quicksum(y[j,i] for i in range(I)) == 1)
	model.setObjective(quicksum(x[i,j]*y[i,j]*t[i,j]for i in range(I) for j in range(J)),GRB.MAXIMIZE)
	model.optimize()
	for j in range(J):
		for i in range(I):
			if x[i,j].X == 1:
				list.append((i,j))
			print(i,j,x[i,j].X)
	return list

if __name__ == '__main__':
	list = kanto_kansai()#トラフィックリストを読み込ませる
	node_list_row = OrderedDict()
	node_list_column = OrderedDict()
	cluster_list_row = []
	cluster_list_column = []
	result_cluster_list_row = []
	result_cluster_list_column = []
	TM = OrderedDict()
	prob_max = 0
	step = 3000
	beta = 1
	alpha = 1
	threshold = 0.07
	assignment_list = []
	print(list)
	for id in list.index:#ノードリストの作成
		node_list_row[str(id)] = (node_class(str(id),"row"))
	for id in list.columns:#ノードリストの作成
		node_list_column[str(id)] = (node_class(str(id),"column"))
	for id1,value1 in enumerate(list.index):#ノード間のトラフィックを挿入
		for id2,value2 in enumerate(list.columns):
				traffic = list.iloc[id1][id2]
				TM[value1,value2] = traffic
	traffic_list = traffic_threshold(TM,threshold)#トラフィック量を0か1に変える
	draw(traffic_list,list.columns,list.index)#クラスタリング前のトラフィック行列を描画
	CRP(traffic_list,node_list_row,cluster_list_row,alpha)#事前分布
	CRP(traffic_list,node_list_column,cluster_list_column,alpha)#事前分布
	draw_cluster(cluster_list_row,cluster_list_column,traffic_list)#クラスタリング結果描画
	for i in range(step):
		CRP_update(node_list_row,cluster_list_row,cluster_list_column,traffic_list,alpha,beta)
		CRP_update(node_list_column,cluster_list_column,cluster_list_row,traffic_list,alpha,beta)
		prob = after_prob(node_list_row,node_list_column,cluster_list_row,cluster_list_column,traffic_list,alpha,beta)#事後確率算出
		if prob > prob_max:
			result_cluster_list_row = deepcopy(cluster_list_row)
			result_cluster_list_column = deepcopy(cluster_list_column)
			prob_max = prob
	draw_cluster(result_cluster_list_row,result_cluster_list_column,traffic_list)
	draw_map(result_cluster_list_row,result_cluster_list_column,traffic_list,beta)
	assignment_list = optimization(result_cluster_list_row,result_cluster_list_column)
