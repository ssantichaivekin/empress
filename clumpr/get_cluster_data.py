import ClusterUtil
import ClusterAgg
import shutil

import random
from pathlib import Path

def has_n_mprs(tree_file, d,t,l, nmprs):
    _, _, _, _, mpr_count = ClusterUtil.get_tree_info(str(tree_file), d,t,l)
    return mpr_count >= nmprs
    

if __name__ == "__main__":
    d = 2
    t = 3
    l = 1
    nmprs = 1000
    n = 100
    from_dir = "tests/TreeLifeData"
    to_dir = Path("tests/cluster_sample")
    fs = ClusterAgg.get_tree_files(from_dir)
    good_fs = [f for f in fs if has_n_mprs(str(f), d,t,l, nmprs)]
    sample_fs = random.sample(good_fs, n)
    for sf in sample_fs:
        new_f = to_dir / sf.name
        shutil.copy(str(sf), str(new_f))

