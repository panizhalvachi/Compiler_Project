#!/usr/bin/env python
# coding: utf-8

# In[23]:


import typing
class DFA:
    def __init__(self):
        self.final_nodes = set()
        self.start_nodes = set()
        self.nodes_edges = dict()
        self.nodes_edges: typing.Dict[typing.Dict]
        self.token_type = dict()
        self.reset_node = 0
        self.current_node = 0
        
    def add_node(self, node_id: int, is_start_node: bool,  is_final_node: bool, token_type: str):
        if is_final_node:
            self.final_nodes.add(node_id)
            self.token_type[node_id] = token_type
        if is_start_node:
            self.start_nodes.add(node_id)
        self.nodes_edges[node_id]= dict()
        
    def add_edge(self, from_node: int, to_node: int, chars: typing.Set):
        edges_dict = self.nodes_edges[from_node]
        for char in chars:
            edges_dict[char] = to_node    
                
    def init_traversal(self, start_node: int):
        self.reset_node = start_node
        self.current_node = start_node
    
    def transition(self, current_node: int, char: str):
        edges_dict = self.nodes_edges[from_node]
        if (char in edges_dict) and (current_node not in final_nodes):
            return edges_dict[char]    


# In[ ]:





# In[ ]:




