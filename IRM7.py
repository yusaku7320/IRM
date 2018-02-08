# -*- coding: shift_jis -*-
import random
import math
import pandas as pd
from copy import deepcopy
class IRM:
	def __init__(self,node1,node2):
		self.result_cluster1 = []#クラスタのリスト作成
		self.result_cluster2 = []#クラスタのリスト作成
		self.cluster1 = []#仮のクラスタリスト
		self.cluster2 = []
		self.node1 = node1
		self.node2 = node2
		self.result_node1 = []
		self.result_node2 = []
		self.a = 1#CRPのパラメータ
		self.b0 = 1#ベータ関数のパラメータ
		self.b1  = 1
		self.b = 1
		self.p_max = 0 #事後確率
	def exe(self):
		#クラスタkの初期化
		self.CRP(self.cluster1, self.node1)
		#self.CRP(self.cluster2, self.node2)
		self.cluster2 = deepcopy(self.cluster1)
		self.csv(self.cluster1,self.cluster2,self.node1,self.node2)#初期クラスタリング表示
		no_update_count = 0
		#クラスタリングを更新するため、仮のクラスタとノードを使用する
		#while no_update_count < 30:#30回更新がなければ終了。
		for i in range(3000):
			#クラスタkとノードiのアップデート
			self.CRP_update(self.cluster1, self.node1, self.cluster2, self.node2)
			#self.CRP_update(self.test_cluster2, self.test_node2, self.test_cluster1, self.test_node1)
			self.cluster2 = deepcopy(self.cluster1)
			self.node2 = deepcopy(self.node1)
			prob = self.after_prob(self.cluster1, self.cluster2, self.node1, self.node2)#事後確率を求める
			if prob > self.p_max:#求めた事後確率が最大事後確率を超えた場合
				#no_update_count = 0
				#最大事後確率、潜在変数など全て更新
				self.p_max = prob
				self.result_cluster1 = deepcopy(self.cluster1)
				self.result_cluster2 = deepcopy(self.cluster2)
				self.result_node1 = deepcopy(self.node1)
				self.result_node2 = deepcopy(self.node2)
				print(self.p_max)
				self.csv(self.cluster1,self.cluster2,self.node1,self.node2)#結果
				self.csv1(self.cluster1,self.cluster2)
		print(self.p_max)
		self.csv(self.result_cluster1,self.result_cluster2,self.result_node1,self.result_node2)#結果
		self.csv1(self.result_cluster1,self.result_cluster2)
	def beta(self,a,b):
		beta = math.gamma(a) * math.gamma(b) / math.gamma(a + b)#ベータ関数beta(a,b)
		return beta
	def CRP(self,cluster_list,node_list):
		now = 0
		for i in range(len(node_list)):
			now += 1#現在のノード数が1つ増える
			if(i == 0):#初めのノードは新しいクラスタ作成
				cluster_list.append(cluster(0,node_list[0]))
				node_list[0].add_cluster(cluster_list[0])
				continue
			else:
				prob_total = 0.0
				prob_list = []
				for j in range(len(cluster_list)):
					exit_prob = float(len(cluster_list[j].node_id))/(self.a + now -1 )
					prob_list.append(exit_prob)
					prob_total += exit_prob
				new_prob = float(self.a) / (self.a + now -1 )
				prob_list.append(new_prob)
				prob_total += new_prob
				p = random.uniform(0, prob_total)
				prob_sum = 0
				for id,prob in enumerate(prob_list):
					prob_sum += prob
					if p < prob_sum:
						if id != len(prob_list)-1:
							node_list[i].add_cluster(cluster_list[id])
							cluster_list[id].add_node(node_list[i])
							break
						else:
							cluster_list.append(cluster(id,node_list[i]))
							node_list[i].add_cluster(cluster_list[-1])
	def CRP_update(self,cluster1,node1,cluster2,node2):
		i = random.choice(node1)
		self.cluster_delete(cluster1,i,node1)
		prob_list = []
		prob_total = 0
		for j in cluster1:
			prob = 1
			for k in cluster2:
				node_count0,node_count1 = i.link_cheak(k)#ノードiからクラスタkのノードへのリンク数
				cluster_count0,cluster_count1 = j.link_cheak(k,node1)#クラスタjからクラスタkのノードへのリンク数
				x = self.beta(self.b1 + node_count1 + cluster_count1 , self.b0+ node_count0 + cluster_count0)
				y = self.beta(self.b1 + cluster_count1 , self.b0+ cluster_count0)
				prob = prob * (x/y)
			z = (len(j.node_id)/(len(self.node1) -1 +self.a))
			prob = prob* z
			prob_list.append(prob)
			prob_total += prob
		new_prob = 1
		for k in cluster2:
			count0,count1 = i.link_cheak(k)
			new_x = self.beta(self.b1 + count1, self.b0 + count0 )
			new_y = self.beta(self.b1, self.b0)
			new_prob = new_prob * x/y
		new_z = ((self.a)/(len(self.node1) -1 +self.a))
		new_prob = new_z * new_prob
		prob_list.append(new_prob)
		prob_total += new_prob
		p = random.uniform(0, prob_total)
		prob_sum = 0
		for id,prob in enumerate(prob_list):
			prob_sum += prob
			if p < prob_sum:
				if id != len(prob_list)-1:
					cluster1[id].add_node(i)
					i.add_cluster(cluster1[id])
					break
				else:
					cluster1.append(cluster(id,i))
					i.add_cluster(cluster1[-1])
	def after_prob(self,cluster1,cluster2,node1,node2):
		cluster1_prob = self.cluster_prob(cluster1,node1)#P(S1|α)の確率
		cluster2_prob = self.cluster_prob(cluster2,node2)#P(S2|α)の確率
		beta_prob = 1#総乗の計算のため1
		for i in cluster1:
			for j in cluster2:
				cluster_count0,cluster_count1 = i.link_cheak(j,node1)#クラスタkからクラスタlのノードへのリンク数
				x = self.beta(cluster_count1 + self.b1 , cluster_count0 + self.b0)
				y = self.beta(self.b1 , self.b0)
				beta_prob = beta_prob * x/y

		prob = cluster1_prob * cluster2_prob * beta_prob
		return prob
	def cluster_prob(self,cluster,node):
		x=1#総乗のため1にする
		y=1#階乗のため1にする
		for i in cluster:
			x = x * math.factorial(len(i.node_id)-1)
		for i in range(len(node)):
			y = y * (self.a + i )
		prob = (self.a ** len(cluster)) * x/y
		return prob
	def MAP(self,cluster1,cluster2):
		count0,count1 = cluster1.link_cheak(cluster2,self.node1)
		x = count1 + self.b
		y = count0 + count1 + 2*self.b

		return x/y
	def csv(self,cluster1,cluster2,node1,node2):
		columns = []
		index = []
		list = []
		for i in cluster2:
			columns += ["|"]
			columns += i.node_id
		for i in cluster1:
			index += ["―"]
			index += i.node_id
		for i in columns:
			a = []
			for j in index:
				if j == "―":
					a.append("―")
				else:
					if i == "|":
						a.append("|")
					else:
						a.append(node1[j].link[str(i)])
			list.append(a)
		df_sample = pd.DataFrame(list).T
		df_sample.columns = columns
		df_sample.index = index
		print(df_sample)
		print()
		#df_sample.to_csv("sample.csv")
	def csv1(self,cluster1,cluster2):
		columns = []
		index = []
		list = []
		for i in cluster2:
			columns += ["|"]
			columns += [i.id]
		for i in cluster1:
			index += ["―"]
			index += [i.id]
		for i in columns:
			a = []
			for j in index:
				if j == "―":
					a.append("―")
				else:
					if i == "|":
						a.append("|")
					else:
						MAP = self.MAP(cluster1[j],cluster2[i])
						a.append(MAP)
			list.append(a)
		df_sample1 = pd.DataFrame(list).T
		df_sample1.columns = columns
		df_sample1.index = index
		print(df_sample1)
		print()
		#df_sample.to_csv("sample.csv")

	def cluster_delete(self,cluster,node_id,node):
		id = node_id.cluster_id#ノードの所属しているクラスタid
		cluster[id].node_delete(node_id.id)#クラスタidからノード削除
		if len(cluster[id].node_id) == 0:#もしクラスタidにノードが所属していなければ削除
			del cluster[id]
			for i in range(len(cluster)) :#各クラスタのidを更新
				cluster[i].id = i
				for j in cluster[i].node_id:
					node[j].cluster_id = cluster[i].id#各ノードの所属クラスタのidを更新

class cluster:
	def __init__(self,id,node):
		self.id = id
		self.node_id = [node.id]
	def add_node(self,node):
		self.node_id.append(node.id)
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
class node:
	def __init__(self,id):
		self.id = id
		self.cluster_id = None
		self.link = {}
	def __repr__(self):
		return str(self.__dict__)
	def __str__(self):
		return str(self.__dict__)
	def add_cluster(self,cluster):
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

def node_create(number):
	node_list = []
	for i in range(number):
		node_list.append(node(i))
	return node_list
def rand_link(node1,node2):
	for i in range(len(node1)):
		for j in range(len(node2)):
			if i == j:
				node1[i].link[str(j)] = 0
				node2[j].link[str(i)] = 0
			else:
				rand = random.randint(0,1)
				node1[i].link[str(j)] = rand
				node2[j].link[str(i)] = rand
def draw(node1,node2):
		columns = []
		index = []
		list = []
		columns += ["|"]
		index += ["―"]
		for i in node2:
			columns += [i.id]
		for i in node1:
			index += [i.id]
		for i in columns:
			a = []
			for j in index:
				if j == "―":
					a.append("―")
				else:
					if i == "|":
						a.append("|")
					else:
						a.append(node1[j].link[str(i)])
			list.append(a)
		df_sample = pd.DataFrame(list).T
		df_sample.columns = columns
		df_sample.index = index
		print(df_sample)
		print()
def example_link1(node1,node2):
	link_example = pd.read_csv("example2.csv")

	for id_1,i in enumerate(link_example.values.tolist()):
		for id_2,link in enumerate(i):
			node1[id_1].link[str(id_2)] = link
			node2[id_2].link[str(id_1)] = link
def example_link2(node1,node2):
	link_example = pd.read_csv("example.csv")
	for id_1,i in enumerate(link_example.values.tolist()):
		for id_2,link in enumerate(i):
			node1[id_1].link[str(id_2)] = link
			node2[id_2].link[str(id_1)] = link
def example_link3(node1,node2):
	link_example = pd.read_csv("example1.csv")
	for id_1,i in enumerate(link_example.values.tolist()):
		for id_2,link in enumerate(i):
			node1[id_1].link[str(id_2)] = link
			node2[id_2].link[str(id_1)] = link
if __name__ == '__main__':
	node1_number = 8#行数S
	node2_number = 8#列数
	node1_list = node_create(node1_number)#行ノード作成
	node2_list = node_create(node2_number)#列ノード作成
	#example_link2(node1_list,node2_list)#ノード数を9にすること
	#example_link3(node1_list,node2_list)#ノード数を9にすること
	#rand_link(node1_list,node2_list)#0と1でランダムにリンクを作成
	example_link1(node1_list,node2_list)
	draw(node1_list,node2_list)
	sample = IRM(node1_list,node2_list)
	sample.exe()
