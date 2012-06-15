# -*- coding: utf-8 -*-
"""
pydot example 1
@author: Federico Cáceres
@url: http://pythonhaven.wordpress.com/2009/12/09/generating_graphs_with_pydot
"""
import pydot 

graph = pydot.Dot(graph_type='graph')

for i in range(3):
    edge = pydot.Edge("king", "lord%d" % i)
    graph.add_edge(edge)

vassal_num = 0
for i in range(3):
    for j in range(2):
        edge = pydot.Edge("lord%d" % i, "vassal%d" % vassal_num)
        graph.add_edge(edge)
        vassal_num += 1

graph.write_png('graphviz_ex_1.png')
