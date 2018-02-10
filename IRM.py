# -*- coding: shift_jis -*-
import random
import math
import pandas as pd
from copy import deepcopy
class cluster_class:
	def __init__(self,id,node):
		self.id = id
		self.node_list = [node.name]
	def add_node(self,node):
		self.node_list.append(node.name)
	def __repr__(self):
		return str(self.__dict__)

	def __str__(self):
		return str(self.__dict__)
	def node_delete(self,id):
		if id in self.node_id:
			self.node_id.remove(id)
	def link_cheak(self,cluster,node):
		count_1 = 0#リンク数
		count_0 = 0#非リンク数
		for i in self.node_id:#クラスタlに所属しているノードj
			for j in cluster.node_id:#クラスタkに所属しているノードi
				x = node[i].link[str(j)] #ノードiとノードjのリンク確認
				if x == 0:
					count_0 += 1
				elif x == 1:
					count_1 += 1
		return count_0,count_1
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
	def link_cheak(self,cluster):
		count_1 = 0#リンク数
		count_0 = 0#非リンク数
		for i in cluster.node_id:#クラスタlに所属しているノードj
			x = self.link[str(i)] #ノードiとノードjのリンク確認
			if x == 0:
				count_0 += 1
			elif x == 1:
				count_1 += 1
		return count_0,count_1

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
def traffic_threshold(link):
	threshold = 0.2
	for i in link.keys():
		if link[i] >= threshold:
			link[i] = 1
		else:
			link[i] = 0
def CRP(node_list,cluster_list):
	alpha = 1#CRPの定数
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
def CRP_update(node_list,cluster_list):
	key_list = []
	for key in node_list.keys():
		key_list.append(key)
	key = random.choice(key_list)#ノードリストからランダムにノードを選択
	node = node_list[key]
	cluster_delete(node,cluster_list,node_list)#ノードを所属クラスタから離脱
	prob_list = []
	prob_total = 0
	for cluster1 in cluster_list:
		prob = 1
		for cluster2 in cluster_list:
			node_count0,node_count1 = node_link_cheak(node,cluster2)#ノードとクラスタのリンク数のカウント
			cluster_count0,cluster_count1 = cluster_link_cheak(cluster1,cluster2,node_list)#クラスタとクラスタのリンク数のカウント

def cluster_link_cheak(cluster1,cluster2,node_list):
	count0 = 0
	count1 = 0
	print(cluster1.node_list)
	print(cluster2.node_list)
	for name1 in cluster1.node_list:
		for name2 in cluster2.node_list:
			link = node_list[name1].link_list[name2]
			if link == 0:
				count0 += 1
			elif link == 1:
		 		count1 += 1
	print(count0,count1)
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
if __name__ == '__main__':
	list = pd.read_csv("traffic.csv")#トラフィックリストを読み込ませる
	node_list = {}
	cluster_list = []
	result_node_list = {}
	result_cluster_list = []
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
		traffic_threshold(node.link_list)#トラフィック量を0か1に変える
	draw(node_list)#クラスタリング前のトラフィック行列を描画
	CRP(node_list,cluster_list)#事前分布
	draw_cluster(cluster_list,node_list)#クラスタリング結果描画
	CRP_update(node_list,cluster_list)
