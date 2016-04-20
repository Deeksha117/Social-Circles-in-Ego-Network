# -*- coding: utf-8 -*-

import collections
import string
import random
import csv
import sys
import matplotlib.pyplot as plt
import networkx as nx
'''
    paper : <<Fast unfolding of communities in large networks>>
'''

"""with open("www_parse.txt") as f:
	content = f.readlines()

author = {}
for row in content:
	tem = row.split("#")
	dum = tem[1].replace("\n", "")
	author[dum] = tem[0]

def get_author(author_id):	
	return author[str(author_id)]
"""
def load_graph(path,name):
    G = collections.defaultdict(dict)
    graph=nx.Graph()

    reader = csv.reader(open(path), delimiter=' ')
    for line in reader:
        if len(line) > 2:
            if float(line[2]) != 0.0:
                try:
                    a = int(line[0])
                    b = int(line[1])
                    c = float(line[2])
                except ValueError:
                    continue
        else:
            v_i = int(line[0])
            v_j = int(line[1])
            G[v_i][v_j] = 1
            G[v_j][v_i] = 1
            graph.add_edge(v_i,v_j,color='b')
            #g.add_node(node)
    nx.draw(graph)
    name=name[:-1]+"graph.png"
    plt.savefig(name) # save as png
    plt.show() # display
    return G

class Vertex():
    
    def __init__(self, vid, cid, nodes, k_in=0):
        self._vid = vid
        self._cid = cid
        self._nodes = nodes
        self._kin = k_in 

class Louvain():
    
    def __init__(self, G):
        self._G = G
        self._m = 0
        self._cid_vertices = {}
        self._vid_vertex = {}
        for vid in self._G.keys():
            self._cid_vertices[vid] = set([vid])
            self._vid_vertex[vid] = Vertex(vid, vid, set([vid]))
            self._m += sum([1 for neighbor in self._G[vid].keys() if neighbor>vid])
        
    def first_stage(self):
        print '---first stage---'
        mod_inc = False  
        visit_sequence = self._G.keys()
        random.shuffle(visit_sequence)
        while True:
            can_stop = True
            for v_vid in visit_sequence:
                v_cid = self._vid_vertex[v_vid]._cid
                k_v = sum(self._G[v_vid].values()) + self._vid_vertex[v_vid]._kin
                cid_Q = {}
                for w_vid in self._G[v_vid].keys():
                    w_cid = self._vid_vertex[w_vid]._cid
                    if w_cid in cid_Q:
                        continue
                    else:
                        tot = sum([sum(self._G[k].values())+self._vid_vertex[k]._kin for k in self._cid_vertices[w_cid]])
                        if w_cid == v_cid:
                            tot -= k_v
                        k_v_in = sum([v for k,v in self._G[v_vid].items() if k in self._cid_vertices[w_cid]])
                        delta_Q = k_v_in - k_v * tot / self._m
                        cid_Q[w_cid] = delta_Q
                    
                cid,max_delta_Q = sorted(cid_Q.items(),key=lambda item:item[1],reverse=True)[0]
                '''
                print '===================='
                print 'v_vid: ', v_vid, 'c: ',self._cid_vertices[v_cid],' neighbors: ', self._G[v_vid].keys()
                print 'k_v: ', k_v
                print 'cid: ', cid , ' c: ', self._cid_vertices[cid]
                print 'tot: ', tot
                print 'k_v_in: ', k_v_in
                print 'delta_Q: ', delta_Q
                '''
                if max_delta_Q > 0.0 and cid!=v_cid:
                    
                    self._vid_vertex[v_vid]._cid = cid
                    self._cid_vertices[cid].add(v_vid)
                    self._cid_vertices[v_cid].remove(v_vid)
                    can_stop = False
                    mod_inc = True
            if can_stop:
                break
        return mod_inc
        
    def second_stage(self):
        print '---second stage---'
        cid_vertices = {}
        vid_vertex = {}
        for cid,vertices in self._cid_vertices.items():
            if len(vertices) == 0:
                continue
            new_vertex = Vertex(cid, cid, set())
            for vid in vertices:
                new_vertex._nodes.update(self._vid_vertex[vid]._nodes)
                new_vertex._kin += self._vid_vertex[vid]._kin
                for k,v in self._G[vid].items():
                    if k in vertices:
                        new_vertex._kin += v/2.0
            #print 'cid: ', cid , ' kin: ', new_vertex._kin
            #print new_vertex._nodes
            cid_vertices[cid] = set([cid])
            vid_vertex[cid] = new_vertex
        
        G = collections.defaultdict(dict)   
        for cid1,vertices1 in self._cid_vertices.items():
            if len(vertices1) == 0:
                continue
            for cid2,vertices2 in self._cid_vertices.items():
                if cid2<=cid1 or len(vertices2)==0:
                    continue
                edge_weight = 0.0
                for vid in vertices1:
                    for k,v in self._G[vid].items():
                        if k in vertices2:
                            edge_weight += v
                #print 's1: ', vertices1, ' s2: ',vertices2, ' weight: ', edge_weight
                if edge_weight != 0:
                    G[cid1][cid2] = edge_weight
                    G[cid2][cid1] = edge_weight
        
        self._cid_vertices = cid_vertices
        self._vid_vertex = vid_vertex
        self._G = G
        
        #print '==========new Graph=========='
        #for k,v in G.items():
            #print k,v
    
    def get_communities(self):
        #print '---communities---'
        communities = []
        for vertices in self._cid_vertices.values():
            if len(vertices) != 0:
                c = set()
                #print cid,vertices
                for vid in vertices:
                    c.update(self._vid_vertex[vid]._nodes)
                communities.append(c)
                #print 'cid: ', cid, ' len: ', len(c), c
        return communities
    
    def execute(self):
        '''
        for i in range(30):
            print '-----------------------------------------'+str(i)+'--------------------------------------------'
            print self.first_stage()
            self.second_stage()
            self.get_communities()
        '''
        iter_time = 1
        while True:
            print '---'+str(iter_time)+'---'
            iter_time += 1
            mod_inc = self.first_stage()
            if mod_inc:
                self.second_stage()
            else:
                break
        return self.get_communities()


if __name__ == '__main__':
    #G = load_graph('./demo.txt')
  import os
  for file in os.listdir("./gplus"):
    z= file.find("edges")
    if z>-1:
        print(file) 
        G = load_graph('./gplus/'+file,file[:z])
        target = open("community_gplus/"+file[:z]+"community","w")
        #print G[233]
        #print sys.getsizeof(G)
        algorithm = Louvain(G)
        communities = algorithm.execute()
        for c in communities:
            for i in c:
                target.write(str(i)+",")
            target.write('\n')
        #for k,v in G.items():
            #print k,v
            
