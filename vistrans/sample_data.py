       
#Tests 1 and 2
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



#Test 3
host_dict3 = { 'hTop': ('Top', 'm0', ('m0', 'm1'), ('m0', 'm2')),
('m0', 'm1'): ('m0', 'm1', ('m1', 'm3'), ('m1', 'G. bursarius')),
('m0', 'm2'): ('m0', 'm2', ('m2', 'T. bottae'), ('m2', 'T. talpoides')),
('m1', 'm3'): ('m1', 'm3', ('m3', 'm4'), ('m3', 'O. hispidus')),
('m3', 'm4'): ('m3', 'm4', ('m4', 'm5'), ('m4', 'O. cavator')),
('m4', 'm5'): ('m4', 'm5', ('m5', 'm6'), ('m5', 'O. underwoodi')),
('m5', 'm6'): ('m5', 'm6', ('m6', 'O. heterodus'), ('m6', 'O. cherriei')),
('m1', 'G. bursarius'): ('m1', 'G. bursarius', None, None),
('m2', 'T. bottae'): ('m2', 'T. bottae', None, None),
('m2', 'T. talpoides'): ('m2', 'T. talpoides', None, None),
('m3', 'O. hispidus'): ('m3', 'O. hispidus', None, None),
('m4', 'O. cavator'): ('m4', 'O. cavator', None, None),
('m5', 'O. underwoodi'): ('m5', 'O. underwoodi', None, None),
('m6', 'O. heterodus'): ('m6', 'O. heterodus', None, None),
('m6', 'O. cherriei'): ('m6', 'O. cherriei', None, None)
}

parasite_dict3 = { 'pTop': ('Top', 'n0', ('n0', 'n1'), ('n0', 'n2')),
('n0', 'n1'): ('n0', 'n1', ('n1', 'n4'), ('n1', 'n3')),
('n0', 'n2'): ('n0', 'n2', ('n2', 'T. minor'), ('n2', 'T. wardi')),
('n1', 'n3'): ('n1', 'n3', ('n3', 'n8'), ('n3', 'G. thomomyus')),
('n1', 'n4'): ('n1', 'n4', ('n4', 'n5'), ('n4', 'G. chapini')),
('n3', 'n8'): ('n3', 'n8', ('n8', 'G. actuosi'), ('n8', 'G. ewingi')),
('n4', 'n5'): ('n4', 'n5', ('n5', 'n6'), ('n5', 'n7')),
('n5', 'n6'): ('n5', 'n6', ('n6', 'G. costaricensis'), ('n6', 'G. cherriei')),
('n5', 'n7'): ('n5', 'n7', ('n7', 'G. setzeri'), ('n7', 'G. panamensis')),
('n2', 'T. minor'): ('n2', 'T. minor', None, None),
('n2', 'T. wardi'): ('n2', 'T. wardi', None, None),
('n3', 'G. thomomyus'): ('n3', 'G. thomomyus', None, None),
('n4', 'G. chapini'): ('n4', 'G. chapini', None, None),
('n6', 'G. costaricensis'): ('n6', 'G. costaricensis', None, None),
('n6', 'G. cherriei'): ('n6', 'G. cherriei', None, None),
('n7', 'G. setzeri'): ('n7', 'G. setzeri', None, None),
('n7', 'G. panamensis'): ('n7', 'G. panamensis', None, None),
('n8', 'G. actuosi'): ('n8', 'G. actuosi', None, None),
('n8', 'G. ewingi'): ('n8', 'G. ewingi', None, None)
}

recon_dict3 = { 
    ('n0', 'm0'): [('D', ('n1', 'm0'), ('n2', 'm0'))],
    ('n1', 'm0'): [('S', ('n4', 'm1'), ('n3', 'm2'))],
    ('n2', 'm0'): [('L', ('n2', 'm2'), (None, None))],
    ('n2', 'm2'): [('S', ('T. minor', 'T. bottae'), ('T. wardi', 'T. talpoides'))],
    ('n3', 'm2'): [('S', ('n8', 'T. bottae'), ('G. thomomyus', 'T. talpoides'))],
    ('n4', 'm1'): [('L', ('n4', 'm3'), (None, None))],
    ('n4', 'm3'): [('S', ('n5', 'm4'), ('G. chapini', 'O. hispidus'))],
    ('n5', 'm4'): [('L', ('n5', 'm5'), (None, None))],
    ('n5', 'm5'): [('S', ('n6', 'm6'), ('n7', 'O. underwoodi'))],
    ('n6', 'm6'): [('S', ('G. costaricensis', 'O. heterodus'), ('G. cherriei', 'O. cherriei'))],
    ('n7', 'O. underwoodi'): [('T', ('G. setzeri', 'O. underwoodi'), ('G. panamensis', 'O. cavator'))],
    ('n8', 'T. bottae'): [('T', ('G. actuosi', 'T. bottae'), ('G. ewingi', 'G. bursarius'))],

    ('T. wardi', 'T. talpoides'): [('C', (None, None), (None, None))],
    ('G. thomomyus', 'T. talpoides'): [('C', (None, None), (None, None))],
    ('T. minor', 'T. bottae'): [('C', (None, None), (None, None))],
    ('G. actuosi', 'T. bottae'): [('C', (None, None), (None, None))],
    ('G. ewingi', 'G. bursarius'): [('C', (None, None), (None, None))],
    ('G. chapini', 'O. hispidus'): [('C', (None, None), (None, None))],
    ('G. panamensis', 'O. cavator'): [('C', (None, None), (None, None))],
    ('G. setzeri', 'O. underwoodi'): [('C', (None, None), (None, None))],
    ('G. cherriei', 'O. cherriei'): [('C', (None, None), (None, None))],
    ('G. costaricensis', 'O. heterodus'): [('C', (None, None), (None, None))]
}

