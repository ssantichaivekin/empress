import Histogram
import HistogramMain

import argparse
from pathlib import Path
import numpy as np
import signal
from scipy import stats
import sys
import operator
from functools import reduce

def process_args():
    # Required arguments - input file, D T L costs
    parser = argparse.ArgumentParser("")
    parser.add_argument("--input", metavar="<filename>", required=True,
        help="The path to a folder of .newick files.")
    parser.add_argument("-d", type=int, metavar="<duplication_cost>", required=True,
        help="The relative cost of a duplication.")
    parser.add_argument("-t", type=int, metavar="<transfer_cost>", required=True,
        help="The relative cost of a transfer.")
    parser.add_argument("-l", type=int, metavar="<loss_cost>", required=True,
        help="The relative cost of a loss.")
    parser.add_argument("--timeout", type=int, metavar="<seconds>", required=False, default=300,
        help="The amount of time a single tree file can run before timing out.")
    parser.add_argument("--min-mprs", type=int, metavar="<#MPRs>", required=False, default=10000,
        help="The minimum number of MPRs a reconciliation must have to use it.")
    args = parser.parse_args()
    return args

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError

def sample_hist(hist, n):
    s_v = sum(hist.values())
    # Do not sample if the histogram is smaller than the desired sample size
    if s_v < n:
        # The population for each key
        key_population = [[k]*v for k,v in list(hist.items())]
        # Flatten that list
        r = reduce(operator.concat, key_population)
        return r
    else:
        k = list(hist.keys())
        v = list(hist.values())
        # Convert v to a probability distribution
        p_v = [float(i)/s_v for i in v]
        # would use random.choices in 3.6
        return np.random.choice(k, n, p=p_v)

def hierarchical_cluster(hists):
    pass

#TODO: consider smoothing
# Although smoothing will remove even/odd parity differences.
def hist_to_array(hist):
    n = max(hist.keys())
    l = []
    for i in range(n):
        if i in hist:
            l.append(hist[i])
        else:
            l.append(0)
    return np.array(l)

# Shift-invariant Jensen-Shannon distance
def array_dist(a1, a2):
    # Begin by aligning the arrays via correlation
    c = np.correlate(a1, a2, mode='same')
    m = np.argmax(c)[0]
    shift = np.array([0] * m)
    l1 = len(a1)
    l2 = len(a2)
    if l1 < l2:
        new_a1 = np.concatenate(shift, a1)
        new_a2 = a2
    else:
        new_a1 = a1
        new_a2 = np.concatenate(shift, a2)
    return scipy.spatial.distance.jensenshannon(new_a1, new_a2)

def find_hists(pathstr, d, t, l, timeout=10, min_mprs=0, normalize=False, zero_loss=False):
    p = Path(pathstr)
    all_files = [f for f in p.glob("**/*") if f.is_file()]
    tree_files = [f for f in all_files if f.suffix == ".newick"]
    filenames = []
    histograms = []
    times = []
    for (i, f) in enumerate(tree_files):
        sys.stdout.write("{}/{}\r".format(i, len(tree_files)))
        sys.stdout.flush()
        # Time out if it's taking too long to calculate the histogram
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        try:
            hist, time = HistogramMain.calc_histogram(str(f), d,t,l, True, normalize, zero_loss)
        except TimeoutError:
            print("")
            print(("{} timed out".format(f)))
            continue
        except AssertionError:
            print("")
            print(("{} asserted".format(f)))
            continue
        signal.alarm(0)
        h_d = hist.histogram_dict
        s_v = sum(h_d.values())
        # 20 is the minimum sample size for statistical testing to make sense
        # Also make sure it has above the minimum number of MPRs
        if s_v >= 20 and h_d[0] > min_mprs:
            filenames.append(f)
            histograms.append(hist)
            times.append(time)
    print("")
    return filenames, histograms, times

def normality(hist_sample):
    # p is 1-probability of rejecting null hypothesis
    # So if p < 0.05 we can say with 95% confidence that the sample is not normal
    _,p = stats.normaltest(hist_sample)
    return p

def normal_sort(names, hists):
    samples = [sample_hist(h, 10000) for h in hists]
    normalities = [normality(s) for s in samples]
    z = list(zip(names, hists, samples, normalities))
    z = sorted(z, key=lambda x: x[3])
    return z

if __name__ == "__main__":
    args = process_args()
    names, hists, times = find_hists(args.input, args.d, args.t, args.l, timeout=args.timeout, min_mprs=10000, normalize=True, zero_loss=True)
    print("DATA")
    # Compute the timing information
    print("Timing:")
    for i in range(len(names)):
        print((str(names[i]), times[i]))
    time_mean = np.mean(times)
    time_std = np.std(times)
    time_max = np.max(times)
    print("Time:")
    print(("Mean: {}".format(time_mean)))
    print(("Standard Deviation: {}".format(time_std)))
    print(("Maximum: {}".format(time_max)))
    # Find the mean and standard deviation of the histograms
    all_hists = Histogram.Histogram.sum(hists)
    m = all_hists.mean()
    s = all_hists.standard_deviation()
    print("Distance:")
    print(("Mean: {}".format(m)))
    print(("Standard Deviation: {}".format(s)))
    # Sort them by normality
    hist_ds = [h.histogram_dict for h in hists]
    l = normal_sort(names, hist_ds)
    print("Normality:")
    for i in l:
        print((str(i[0]), i[3]))
 
