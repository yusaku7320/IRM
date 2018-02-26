# -*- coding: shift_jis -*-
from numpy.random import *
from numpy import *
import math
import pandas as pd
from copy import deepcopy
from gurobipy import *
class cluster_class:
	def __init__(self,id,node):
		self.id = id
		self.node_list = [node.name]
		self.cluster_map = []
	def add_node(self,node):
		self.node_list.append(node.name)
	def __repr__(self):
		return str(self.__dict__)

	def __str__(self):
		return str(self.__dict__)
class node_class:
	def __init__(self,name):
		self.name = name
		self.cluster_id = None
		self.link_list = {}
	def __repr__(self):
		return str(self.__dict__)
	def __str__(self):
		return str(self.__dict__)
	def belong(self,cluster):
		self.cluster_id = cluster.id
def draw(model):
		columns = []
		index = []
		list = []
		for i in model.values():
			columns += [i.name]
			index += [i.name]
			list.append(i.link_list)
		df_sample = pd.DataFrame(list).T
		df_sample.columns = columns
		df_sample.index = index
		print(df_sample)
		print()
def draw_cluster(cluster_list,node_list):
	columns = []
	index = []
	list = []
	for cluster in cluster_list:
		columns += ["|"]
		index += ["-"]
		columns += cluster.node_list
		index += cluster.node_list
	for i in columns:
		traffic = []
		for j in index:
			if i == "|":
				traffic.append("|")
			else:
				if j == "-":
					traffic.append("-")
				else:
					traffic.append(node_list[j].link_list[i])
		list.append(traffic)
	df_sample1 = pd.DataFrame(list).T
	df_sample1.columns = columns
	df_sample1.index = index
	print(df_sample1)
	print()
def traffic_threshold(link,threshold):
	for i in link.keys():
		if link[i] >= threshold:
			link[i] = 1
		else:
			link[i] = 0
def CRP(node_list,cluster_list,alpha):
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



def CRP_update(node_list,cluster_list,alpha,beta):
	key_list = []
	for key in node_list.keys():
		key_list.append(key)
	key = random.choice(key_list)#ノードリストからランダムにノードを選択
	node = node_list[key]
	cluster_delete(node,cluster_list,node_list)#ノードを所属クラスタから離脱
	prob_list,prob_total  = exit_prob(node,cluster_list,node_list,alpha,beta)
	new_prob = new_probability(node,cluster_list,node_list,alpha,beta)
	prob_list.append(new_prob)
	prob_total += new_prob
	clustering(node,cluster_list,prob_list,prob_total)

def clustering(node,cluster_list,prob_list,prob_total):
	p = random.uniform(0, prob_total)
	prob_sum = 0
	for id,prob in enumerate(prob_list):
		prob_sum += prob
		if p < prob_sum:
			if id != len(prob_list)-1:
				node.belong(cluster_list[id])
				cluster_list[id].add_node(node)
				break
			else:
				cluster_list.append(cluster_class(id,node))
				node.belong(cluster_list[-1])
def new_probability(node,cluster_list,node_list,alpha,beta):
	new_prob = 1
	for cluster in cluster_list:
		node_count0,node_count1 = node_link_cheak(node,cluster)#ノードとクラスタのリンク数のカウント
		new_x = beta_function(beta + node_count1, beta + node_count0 )
		new_y = beta_function(beta,beta)
		new_prob = new_prob * new_x/new_y
	new_z = (alpha/(len(node_list.values()) -1 + alpha))
	new_prob = new_z * new_prob
	return new_prob
def exit_prob(node,cluster_list,node_list,alpha,beta):
	prob_list = []
	prob_total = 0
	for cluster1 in cluster_list:
		prob = 1
		for cluster2 in cluster_list:
			node_count0,node_count1 = node_link_cheak(node,cluster2)#ノードとクラスタのリンク数のカウント
			cluster_count0,cluster_count1 = cluster_link_cheak(cluster1,cluster2,node_list)#クラスタとクラスタのリンク数のカウント
			x = beta_function(beta + node_count1 + cluster_count1 , beta+ node_count0 + cluster_count0)
			y = beta_function(beta + cluster_count1 , beta + cluster_count0)
			prob = prob * (x/y)
		z = len(cluster1.node_list)/(len(node_list.values()) -1 + alpha)
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
	for name1 in cluster1.node_list:
		for name2 in cluster2.node_list:
			link = node_list[name1].link_list[name2]
			if link == 0:
				count0 += 1
			elif link == 1:
		 		count1 += 1
	return count0,count1
def node_link_cheak(node,cluster):
	count0 = 0
	count1 = 0
	for name in cluster.node_list:
		link = node.link_list[name]
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
def after_prob(node_list,cluster_list,alpha,beta):
	cluster_prob = cluster_probability(cluster_list,node_list,alpha)#P(S1|α)の確率
	beta_prob = 1#総乗の計算のため1
	for cluster1 in cluster_list:
		for cluster2 in cluster_list:
			cluster_count0,cluster_count1 = cluster_link_cheak(cluster1,cluster2,node_list)
			x = beta_function(cluster_count1 + beta , cluster_count0 + beta)
			y = beta_function(beta , beta)
			beta_prob = beta_prob * x/y
	prob = cluster_prob * cluster_prob * beta_prob
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
	return pd.read_csv("kanto_kansai_traffic.csv")
def draw_map(cluster_list,node_list,beta):
	columns = []
	index = []
	list = []
	for cluster in cluster_list:
		columns += ["|"]
		index += ["-"]
		columns += [cluster.id]
		index += [cluster.id]
	for i in columns:
		traffic = []
		for j in index:
			if i == "|":
				traffic.append("|")
			else:
				if j == "-":
					traffic.append("-")
				else:
					cluster_MAP = MAP(cluster_list[j],cluster_list[i],node_list,beta)
					traffic.append(cluster_MAP)
		list.append(traffic)
	df_sample1 = pd.DataFrame(list).T
	df_sample1.columns = columns
	df_sample1.index = index
	print(df_sample1)
	print()
def MAP(cluster1,cluster2,node_list,beta):
	count0,count1 = cluster_link_cheak(cluster1,cluster2,node_list)
	x = count1 + beta
	y = count0 + count1 + 2*beta
	cluster1.cluster_map.append(x/y)
	cluster2.cluster_map.append(x/y)
	return x/y
def optimization(cluster1,cluster2):
	model = Model("map")

	x,y,t = {},{},{}
	for j in range(len(cluster2)):
		for i in range(len(cluster1)):
			x[i,j] = model.addVar(vtype = "B")
	for i in range(len(cluster1)):
		for j in range(len(cluster2)):
			y[j,i] = model.addVar(vtype = "B")

	model.update()

	for i in range(len(cluster1)):
		model.addConstr(quicksum(x[i,j] for j in range(len(cluster2))) == 1)
	for j in range(len(cluster2)):
		model.addConstr(quicksum(y[j,i] for i in range(len(cluster1))) == 1)

	model.setObjective(quicksum)
if __name__ == '__main__':
	list = kanto_kansai()#トラフィックリストを読み込ませる
	node_list = {}
	cluster_list = []
	result_node_list = {}
	result_cluster_list = []
	prob_max = 0
	step = 300
	beta = 1
	alpha = 1
	threshold = 0.07
	print(list)
	for i in list.values.tolist():#ノードリストの作成
		name = i[0]
		node_list[name] = (node_class(name))
	for  id,node in enumerate(node_list.values()):#ノード間のトラフィックを挿入
		for j in list.values.tolist():
			name = j[0]
			traffic = j[id+1]
			node.link_list[name] = traffic
	for node in node_list.values():
		traffic_threshold(node.link_list,threshold)#トラフィック量を0か1に変える
	draw(node_list)#クラスタリング前のトラフィック行列を描画
	CRP(node_list,cluster_list,alpha)#事前分布
	draw_cluster(cluster_list,node_list)#クラスタリング結果描画
	for i in range(step):
		CRP_update(node_list,cluster_list,alpha,beta)
		prob = after_prob(node_list,cluster_list,alpha,beta)#事後確率算出
		if prob > prob_max:
			result_node_list = deepcopy(node_list)
			result_cluster_list = deepcopy(cluster_list)
			prob_max = prob
			draw_cluster(result_cluster_list,result_node_list)
	draw_cluster(result_cluster_list,result_node_list)
	draw_map(result_cluster_list,result_node_list,beta)
	for cluster in result_cluster_list:
		print(cluster.node_list)
	for cluster in result_cluster_list:
		print(cluster.cluster_map)
