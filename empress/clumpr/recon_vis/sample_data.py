       
       
host_dict1 = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm4')),
('m0', 'm1'): ('m0', 'm1', ('m1', 'm2'), ('m1', 'm3')),
('m0', 'm4'): ('m0', 'm4', None, None),
('m1', 'm2'): ('m1', 'm2', None, None),
('m1', 'm3'): ('m1', 'm3', None, None)}

parasite_dict1 = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n4')),
('n0', 'n1'): ('n0', 'n1', ('n1', 'n2'), ('n1', 'n3')),
('n0', 'n4'): ('n0', 'n4', None, None),
('n1', 'n2'): ('n1', 'n2', None, None),
('n1', 'n3'): ('n1', 'n3', None, None)}

recon_dict1 = { ('n0', 'm0'): [('S', ('n1', 'm1'), ('n4', 'm4'))],
('n1', 'm1'): [('S', ('n2', 'm2'), ('n3', 'm3'))],
('n2', 'm2'): [('C', (None, None), (None, None))],
('n3', 'm3'): [('C', (None, None), (None, None))],
('n4', 'm4'): [('C', (None, None), (None, None))]}


recon_dict2 = { ('n0', 'm1'): [('T', ('n1', 'm1'), ('n4', 'm4'))],
('n1', 'm1'): [('D', ('n2', 'm1'), ('n3', 'm1'))],
('n2', 'm1'): [('L', ('n2', 'm2'), (None, None))],
('n3', 'm1'): [('L', ('n3', 'm3'), (None, None))],
('n2', 'm2'): [('C', (None, None), (None, None))],
('n3', 'm3'): [('C', (None, None), (None, None))],
('n4', 'm4'): [('C', (None, None), (None, None))]}
