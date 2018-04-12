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
		self.traffic = None
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
	def __repr__(self):
		return str(self.__dict__)
	def __str__(self):
		return str(self.__dict__)
	def belong(self,cluster):
		self.cluster_id = cluster.id
class controller_class:
	def __init__(self,id,capacity):
		self.id = id
		self.switch_list = []
		self.capacity = capacity
		self.request_count = 0
		self.other_count = 0
		self.result_prob = 0
	def __repr__(self):
		return str(self.__dict__)
	def __str__(self):
		return str(self.__dict__)
class switch_class:
	def __init__(self,id,connection,retention_time):
		self.id = id
		self.connection = connection
		self.retention_time = retention_time
	def __repr__(self):
		return str(self.__dict__)
	def __str__(self):
		return str(self.__dict__)
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
def draw_cluster(cluster_list,traffic_list):
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
					traffic.append(traffic_list[j,i])
		list.append(traffic)
	df_sample1 = pd.DataFrame(list).T
	df_sample1.columns = columns
	df_sample1.index = index
	print(df_sample1)
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
def cluster_link_cheak(cluster1,cluster2,traffic_list):
	count0 = 0
	count1 = 0
	for name1 in cluster1.node_list:
		for name2 in cluster2.node_list:
			link = traffic_list[name1,name2]
			if link == 0:
				count0 += 1
			elif link == 1:
		 		count1 += 1
	return count0,count1
def node_link_cheak(node,cluster,traffic_list):
	count0 = 0
	count1 = 0
	for name in cluster.node_list:
		link = traffic_list[node.name,name]
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
def after_prob(node_list,cluster_list,traffic_list,alpha,beta):
	cluster_prob = cluster_probability(cluster_list,node_list,alpha)#P(S1|α)の確率
	beta_prob = 1#総乗の計算のため1
	for cluster1 in cluster_list:
		for cluster2 in cluster_list:
			cluster_count0,cluster_count1 = cluster_link_cheak(cluster1,cluster2,traffic_list)
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
	return pd.read_csv("kanto_kansai_traffic.csv",index_col=0)
def draw_map(cluster_list,traffic_list,beta):
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
					cluster_MAP = MAP(cluster_list[j],cluster_list[i],traffic_list,beta)
					traffic.append(cluster_MAP)
		list.append(traffic)
	df_sample1 = pd.DataFrame(list).T
	df_sample1.columns = columns
	df_sample1.index = index
	print(df_sample1)
	print()
def MAP(cluster1,cluster2,traffic_list,beta):
	count0,count1 = cluster_link_cheak(cluster1,cluster2,traffic_list)
	x = count1 + beta
	y = count0 + count1 + 2*beta
	cluster1.cluster_map.append(x/y)
	return x/y
def optimization(cluster1_list,cluster2_list,controller,traffic_list):
	model = Model("map")
	x,y,t = OrderedDict(),OrderedDict(),OrderedDict()
	I = len(cluster1_list)
	J = len(cluster2_list)
	for cluster1 in cluster1_list:
		for cluster2 in cluster2_list:
			t[cluster1.id,cluster2.id] = traffic_amount(cluster1,cluster2,traffic_list)
	for j in range(J):
		for i in range(I):
			x[i,j] = model.addVar(vtype = "B")
	for i in range(I):
		for j in range(J):
			y[j,i] = model.addVar(vtype = "B")
	print(t)
	model.update()

	for i in range(I):
		model.addConstr(quicksum(x[i,j] for j in range(J)) == 1)
	for j in range(J):
		model.addConstr(quicksum(y[j,i] for i in range(I)) == 1)
	model.setObjective(quicksum(x[i,j]*y[j,i]*t[i,j]for i in range(I) for j in range(J)),GRB.MAXIMIZE)
	model.optimize()
	for j in range(J):
		for i in range(I):
			print(i,j,x[i,j].X)
def traffic_amount(cluster1,cluster2,traffic_list):
	amount = 0
	if cluster1.id != cluster2.id:
		for node1 in cluster1.node_list:
			for node2 in cluster1.node_list:
				amount += traffic_list[node1,node2]
		for node1 in cluster2.node_list:
			for node2 in cluster2.node_list:
				amount += traffic_list[node1,node2]
		for node1 in cluster1.node_list:
			for node2 in cluster2.node_list:
				amount += traffic_list[node1,node2]
	else:
		for node1 in cluster1.node_list:
			for node2 in cluster2.node_list:
				amount += traffic_list[node1,node2]
	return amount
def controller_assignment(controller_list,result_cluster_list):
	for switch in result_cluster_list[0].node_list:
		controller_list[0].switch_list.append(switch)
	for switch in result_cluster_list[1].node_list:
		controller_list[1].switch_list.append(switch)
	for switch in result_cluster_list[2].node_list:
		controller_list[1].switch_list.append(switch)
def simulation(controller_list,switch_list,traffic_list,simulation_time):
	for time in range(simulation_time):
		for controller in controller_list:
			transmission(controller,switch_list,traffic_list)
def transmission(controller,switch_list,traffic_list):
	for id1 in controller.switch_list:
		for id2 in switch_list.keys():
			request = int(traffic_list[id1,id2]/(switch_list[id1].connection * switch_list[id1].retention_time))
			controller.request_count += request
			cheak = id2 in controller.switch_list
			if cheak == False:
				controller.other_count += request
def random_controller_assignment(controller_list,switch_list):
	for id in switch_list.keys():
		controller = random.choice(controller_list)
		controller.switch_list.append(id)
def result_probability(controller_list):
	prob = 0
	result_prob = 0
	for controller in controller_list:
		prob += controller.request_count
	for controller in controller_list:
		controller.result_prob = controller.other_count/prob
	for controller in controller_list:
		result_prob += controller.result_prob
	return result_prob
def result_csv(proposed_result,random_result):

	data = {("ランダムな割り当て"):{"不一致確率":random_result},
			"提案手法":{"不一致確率":proposed_result}}
	df = pd.DataFrame(data)
	print(f)
	df.to_csv("result.csv")
if __name__ == '__main__':
	list = kanto_kansai()#トラフィックリストを読み込ませる
	node_list = OrderedDict()
	cluster_list = []
	result_node_list = OrderedDict()
	result_cluster_list = []
	controller_list = []
	random_controller_list = []
	switch_list = OrderedDict()
	random_switch_list = OrderedDict()
	prob_max = 0#最大事後確率
	step = 3000#IRMステップ数
	beta = 1
	alpha = 1
	threshold = 700#トラフィック量の閾値
	traffic_list = OrderedDict()
	observation_data = OrderedDict()
	controller_number = 2
	switch_connection = 0.16#160bps
	switch_retention_time = 600
	controller_capacity = 7800000
	simulation_time = 3600
	proposed_result = 0
	random_result = 0
	print(list)
	for id in list.index:#ノードリストの作成
		node_list[str(id)] = (node_class(str(id)))
	for id1,value1 in enumerate(list.index):#ノード間のトラフィックを挿入
		for id2,value2 in enumerate(list.columns):
				traffic = list.iloc[id1][id2]
				traffic_list[value1,value2] = traffic
	observation_data = traffic_threshold(traffic_list,threshold)#トラフィック量を0か1に変える
	draw(observation_data,list.columns,list.index)#クラスタリング前のトラフィック行列を描画
	CRP(observation_data,node_list,cluster_list,alpha)#事前分布
	draw_cluster(cluster_list,observation_data)#クラスタリング結果描画
	for i in range(step):
		CRP_update(node_list,cluster_list,cluster_list,observation_data,alpha,beta)
		prob = after_prob(node_list,cluster_list,observation_data,alpha,beta)#事後確率算出
		if prob > prob_max:
			result_node_list = deepcopy(node_list)
			result_cluster_list = deepcopy(cluster_list)
			prob_max = prob
	draw_cluster(result_cluster_list,observation_data)
	draw_map(result_cluster_list,observation_data,beta)
	for node in node_list.values():
		switch_list[node.name] = switch_class(node.name,switch_connection,switch_retention_time)
	for controller in range(controller_number):
		controller_list.append(controller_class(controller,controller_capacity))
	random_switch_list = deepcopy(switch_list)
	random_controller_list = deepcopy(controller_list)
	controller_assignment(controller_list,result_cluster_list)
	random_controller_assignment(random_controller_list,random_switch_list)
	simulation(controller_list,switch_list,traffic_list,simulation_time)
	simulation(random_controller_list,random_switch_list,traffic_list,simulation_time)
	proposed_result = result_probability(controller_list)
	random_result = result_probability(random_controller_list)
	all_random_request = 0
	other_random_request = 0
	all_proposed_request = 0
	other_proposed_request = 0
	for controller in random_controller_list:
		print("ランダムコントローラ",controller.id)
		print(controller.switch_list)
		print("総リクエスト数",controller.request_count)
		all_random_request += controller.request_count
		print("不一致リクエスト数",controller.other_count)
		other_random_request += controller.other_count
		print("不一致確率",controller.result_prob)
	for controller in controller_list:
		print("提案コントローラ",controller.id)
		print(controller.switch_list)
		print("総リクエスト数",controller.request_count)
		all_proposed_request += controller.request_count
		print("不一致リクエスト数",controller.other_count)
		other_proposed_request += controller.other_count
		print("不一致確率",controller.result_prob)
	print("ランダムな割り当ての不一致確率は",other_random_request/(all_random_request))
	print("提案手法の不一致確率は",other_proposed_request/all_proposed_request)
	#result_csv(proposed_result,random_result)
	#optimization(result_cluster_list,result_cluster_list,controller,traffic_list)
