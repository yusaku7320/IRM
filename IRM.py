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
		count_1 = 0#�����N��
		count_0 = 0#�񃊃��N��
		for i in self.node_id:#�N���X�^l�ɏ������Ă���m�[�hj
			for j in cluster.node_id:#�N���X�^k�ɏ������Ă���m�[�hi
				x = node[i].link[str(j)] #�m�[�hi�ƃm�[�hj�̃����N�m�F
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
		count_1 = 0#�����N��
		count_0 = 0#�񃊃��N��
		for i in cluster.node_id:#�N���X�^l�ɏ������Ă���m�[�hj
			x = self.link[str(i)] #�m�[�hi�ƃm�[�hj�̃����N�m�F
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
					traffic.append(node_list[i].link_list[j])
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
	alpha = 1#CRP�̒萔
	for number,node in enumerate(node_list.values()):
		if len(cluster_list) == 0:#�e�[�u����0�̂Ƃ�
			cluster_list.append(cluster_class( len(cluster_list), node))#�V�K�N���X�^�쐬
			node.belong(cluster_list[-1])#�m�[�h�ɃN���X�^ID��ۑ�
			continue
		else:
			prob_total = 0.0
			prob_list = []
			for cluster in cluster_list:
				node_sum = len(cluster.node_list)#�N���X�^�ɏ������Ă���m�[�h��
				exit_prob = float(node_sum/(alpha + number))#number�͌��݂̃m�[�h��ID���������߁Anumber+1�Ō��݂̃m�[�h���ɂȂ�
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
if __name__ == '__main__':
	list = pd.read_csv("traffic.csv")#�g���t�B�b�N���X�g��ǂݍ��܂���
	node_list = {}
	cluster_list = []
	print(list)
	for i in list.values.tolist():#�m�[�h���X�g�̍쐬
		name = i[0]
		node_list[name] = (node_class(name))
	for  id,node in enumerate(node_list.values()):#�m�[�h�Ԃ̃g���t�B�b�N��}��
		for j in list.values.tolist():
			name = j[0]
			traffic = j[id+1]
			node.link_list[name] = traffic
	for node in node_list.values():
		traffic_threshold(node.link_list)#�g���t�B�b�N�ʂ�0��1�ɕς���
	draw(node_list)#�N���X�^�����O�O�̃g���t�B�b�N�s���`��
	CRP(node_list,cluster_list)#���O���z
	draw_cluster(cluster_list,node_list)
