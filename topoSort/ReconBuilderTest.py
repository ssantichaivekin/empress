import ReconBuilder

# a reconciliation with temporal inconsistency
host_tree_1 = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm4')),
('m0', 'm1'): ('m0', 'm1', ('m1', 'm2'), ('m1', 'm3')),
('m0', 'm4'): ('m0', 'm4', ('m4', 'm5'), ('m4', 'm6')),
('m1', 'm2'): ('m1', 'm2', None, None),
('m1', 'm3'): ('m1', 'm3', None, None),
('m4', 'm5'): ('m4', 'm5', None, None),
('m4', 'm6'): ('m4', 'm6', None, None)}

parasite_tree_1 = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n5')),
('n0', 'n1'): ('n0', 'n1', ('n1', 'n2'), ('n1', 'n3')),
('n1', 'n3'): ('n1', 'n3', ('n3', 'n4'), ('n3', 'n6')),
('n1', 'n2'): ('n1', 'n2', None, None),
('n3', 'n4'): ('n3', 'n4', None, None),
('n0', 'n5'): ('n0', 'n5', None, None),
('n3', 'n6'): ('n3', 'n6', None, None),}

reconciliation_1 = { ('n0', 'm1'): [('T', ('n1', 'm1'), ('n5', 'm5'))],
('n1', 'm1'): [('L', ('n1', 'm2'), (None, None))],
('n1', 'm2'): [('T', ('n2', 'm2'), ('n3', 'm4'))],
('n2', 'm2'): [('C', (None, None), (None, None))],
('n4', 'm5'): [('C', (None, None), (None, None))],
('n5', 'm5'): [('C', (None, None), (None, None))],
('n6', 'm6'): [('C', (None, None), (None, None))],
('n3', 'm4'): [('S', ('n4', 'm5'), ('n6', 'm6'))]}

# a reconciliation with no temporal inconsistency with duplication on a leave
host_tree_2 = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
('m0', 'm1'): ('m0', 'm1', None, None),
('m0', 'm2'): ('m0', 'm2', ('m2', 'm3'), ('m2', 'm4')),
('m2', 'm3'): ('m2', 'm3', None, None),
('m2', 'm4'): ('m2', 'm4', None, None)}

parasite_tree_2 = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n2')),
('n0', 'n1'): ('n0', 'n1', None, None),
('n0', 'n2'): ('n0', 'n2', ('n2', 'n3'), ('n2', 'n4')),
('n2', 'n3'): ('n2', 'n3', None, None),
('n2', 'n4'): ('n2', 'n4', None, None)}

reconciliation_2 = { ('n0', 'm4'): [('D', ('n1', 'm4'), ('n2', 'm4'))],
('n1', 'm4'): [('C', (None, None), (None, None))],
('n2', 'm4'): [('D', ('n3', 'm4'), ('n4', 'm4'))],
('n3', 'm4'): [('C', (None, None), (None, None))],
('n4', 'm4'): [('C', (None, None), (None, None))]}

# a reconciliation with another type of temporal inconsistency
host_tree_3 = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
('m0', 'm1'): ('m0', 'm1', ('m1', 'm3'), ('m1', 'm4')),
('m1', 'm3'): ('m1', 'm3', None, None),
('m1', 'm4'): ('m1', 'm4', None, None),
('m0', 'm2'): ('m0', 'm2', None, None)}

parasite_tree_3 = { 'pTop': ('Top', 'n0', ('n0', 'n4'), ('n0', 'n2')),
('n0', 'n4'): ('n0', 'n4', None, None),
('n0', 'n2'): ('n0', 'n2', ('n2', 'n5'), ('n2', 'n3')),
('n2', 'n5'): ('n2', 'n5', None, None),
('n2', 'n3'): ('n2', 'n3', ('n3', 'n1'), ('n3', 'n6')),
('n3', 'n1'): ('n3', 'n1', None, None),
('n3', 'n6'): ('n3', 'n6', None, None)}

reconciliation_3 = { ('n0', 'm4'): [('T', ('n4', 'm4'), ('n2', 'm2'))],
('n2', 'm2'): [('T', ('n5', 'm2'), ('n3', 'm1'))],
('n3', 'm1'): [('S', ('n1', 'm3'), ('n6', 'm4'))],
('n1', 'm3'): [('C', (None, None), (None, None))],
('n4', 'm4'): [('C', (None, None), (None, None))],
('n5', 'm2'): [('C', (None, None), (None, None))],
('n6', 'm4'): [('C', (None, None), (None, None))]}

# a reconciliation that is temporally consistent with more interwoven order
host_tree_4 = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm4')),
('m0', 'm1'): ('m0', 'm1', ('m1', 'm2'), ('m1', 'm3')),
('m0', 'm4'): ('m0', 'm4', ('m4', 'm5'), ('m4', 'm6')),
('m1', 'm2'): ('m1', 'm2', None, None),
('m1', 'm3'): ('m1', 'm3', None, None),
('m4', 'm5'): ('m4', 'm5', None, None),
('m4', 'm6'): ('m4', 'm6', None, None)}

parasite_tree_4 = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n2')),
('n0', 'n1'): ('n0', 'n1', ('n1', 'n5'), ('n1', 'n6')),
('n0', 'n2'): ('n0', 'n2', ('n2', 'n3'), ('n2', 'n4')),
('n1', 'n5'): ('n1', 'n5', None, None),
('n1', 'n6'): ('n1', 'n6', None, None),
('n3', 'n7'): ('n3', 'n7', None, None),
('n3', 'n8'): ('n3', 'n8', None, None),
('n2', 'n3'): ('n2', 'n3', ('n3', 'n7'), ('n3', 'n8')),
('n2', 'n4'): ('n2', 'n4', None, None),}

reconciliation_4 = { ('n0', 'm0'): [('S', ('n1', 'm1'), ('n2', 'm4'))],
('n1', 'm1'): [('S', ('n5', 'm2'), ('n6', 'm3'))],
('n2', 'm4'): [('T', ('n4', 'm4'), ('n3', 'm1'))],
('n4', 'm4'): [('L', ('n4', 'm6'), (None, None))],
('n4', 'm6'): [('C', (None, None), (None, None))],
('n3', 'm1'): [('S', ('n7', 'm2'), ('n8', 'm3'))],
('n7', 'm2'): [('C', (None, None), (None, None))],
('n8', 'm3'): [('C', (None, None), (None, None))],
('n5', 'm2'): [('C', (None, None), (None, None))],
('n6', 'm3'): [('C', (None, None), (None, None))]}

def check_topological_order(temporal_graph, ordering_dict):
  """ Check the ordering_dict orders the nodes in temporal_graph in topological order"""
  
  for node_tuple in temporal_graph:
    for node_tuple_child in temporal_graph[node_tuple]:
      is_child_leaf = bool(node_tuple_child not in ordering_dict)
      # leaves are not ordered
      if is_child_leaf:
        continue
      assert(ordering_dict[node_tuple] < ordering_dict[node_tuple_child])

def print_order_in_tree(tree_node):
  """ Print the orders of the nodes rooted at this tree_node """

  if tree_node.layout != None:
    print(tree_node.layout.col, end=" ")
  if not tree_node.is_leaf:
    print_order_in_tree(tree_node.left_node)
    print_order_in_tree(tree_node.right_node)

def tester():
  """ Tester for topological_order and build_trees_with_temporal_order """

  host_list = [host_tree_1, host_tree_2, host_tree_3, host_tree_4]
  parasite_list = [parasite_tree_1, parasite_tree_2, parasite_tree_3, parasite_tree_4]
  reconciliation_list = [reconciliation_1, reconciliation_2, reconciliation_3, reconciliation_4]

  for host_tree, parasite_tree, reconciliation in zip(host_list, parasite_list, reconciliation_list):
    temporal_graph = ReconBuilder.build_temporal_graph(host_tree, parasite_tree, reconciliation)
    ordering_dict = ReconBuilder.topological_order(temporal_graph)
    print(ordering_dict)
    # if there is no temporal inconsistency
    if ordering_dict != None:
      check_topological_order(temporal_graph, ordering_dict)

    host, parasite = ReconBuilder.build_trees_with_temporal_order(host_tree, parasite_tree, reconciliation)
    print_order_in_tree(host.root_node)
    print_order_in_tree(parasite.root_node)
    print()
