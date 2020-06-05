import ReconRender

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

ReconRender.render_tree(host_tree_1, parasite_tree_1, reconciliation_1)
ReconRender.main()