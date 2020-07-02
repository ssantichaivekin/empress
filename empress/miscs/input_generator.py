import itertools
import os
import random

from empress import input_reader
random.seed(1)

def generate_all_recon_input(n_leaves: int) -> input_reader.ReconInput:
    """
    Create an iterable of all possible ReconInput object with specified number of host/parasite leaves.
    """
    for host_dict in _generate_all_host_dict(n_leaves):
        for parasite_dict in _generate_all_parasite_dict(n_leaves):
            for mapping in _generate_all_tip_mapping(host_dict, parasite_dict):
                yield input_reader.ReconInput(host_dict, None, parasite_dict, None, mapping)

def generate_random_recon_input(n_leaves: int) -> input_reader.ReconInput:
    """
    Randomly create one ReconInput object with specified number of host/parasite leaves.
    The randomization is not guaranteed to be uniform.
    """
    host_dict = _generate_random_host_dict(n_leaves)
    parasite_dict = _generate_random_parasite_dict(n_leaves)
    mapping = _generate_random_tip_mapping(host_dict, parasite_dict)
    return input_reader.ReconInput(host_dict, None, parasite_dict, None, mapping)


def _generate_all_host_dict(n_leaves):
    yield from _generate_all_trees(n_leaves, 'hTop', 'h')

def _generate_all_parasite_dict(n_leaves):
    yield from _generate_all_trees(n_leaves, 'pTop', 'p')

def _generate_all_trees(n_leaves: int, top_name: str, prefix: str):
    """
    We don't actually generate all possible trees in this
    format. In the code, you will see that we only generate a right-heavy
    tree, meaning that the right subtree has equal or greater number of
    nodes than the left subtree. We do this to reduce the number of trees
    that are isomorphic to one another.
    """
    tree_dict = {}
    if n_leaves == 1:
        tree_dict[top_name] = ('Top', prefix + '0', None, None)
        yield tree_dict.copy()
    else:
        left_start = 1
        left_name = prefix + str(left_start)
        mid = n_leaves // 2
        for left_n_leaves in range(1, mid+1):
            right_n_leaves = n_leaves - left_n_leaves
            right_start = 2 * left_n_leaves
            right_name = prefix + str(right_start)
            bot_name = prefix + '0'
            tree_dict[top_name] = ('Top', bot_name, (bot_name, left_name), (bot_name, right_name))
            for left_tree_dict in _generate_all_trees_helper(left_n_leaves, bot_name, prefix, left_start):
                for right_tree_dict in _generate_all_trees_helper(right_n_leaves, bot_name, prefix, right_start):
                    new_tree_dict = tree_dict.copy()
                    new_tree_dict.update(left_tree_dict)
                    new_tree_dict.update(right_tree_dict)
                    yield new_tree_dict

def _generate_all_trees_helper(n_leaves: int, parent: str, prefix: str, start: int):
    tree_dict = {}
    this_name = prefix + str(start)
    if n_leaves == 1:
        tree_dict[(parent, this_name)] = (parent, this_name, None, None)
        yield tree_dict.copy()
    else:
        left_start = start + 1
        left_name = prefix + str(left_start)
        mid = n_leaves // 2
        for left_n_leaves in range(1, mid + 1):
            right_n_leaves = n_leaves - left_n_leaves
            right_start = start + 1 + (2 * left_n_leaves - 1)
            right_name = prefix + str(right_start)
            tree_dict[(parent, this_name)] = (parent, this_name, (this_name, left_name), (this_name, right_name))
            for left_tree_dict in _generate_all_trees_helper(left_n_leaves, this_name, prefix, left_start):
                for right_tree_dict in _generate_all_trees_helper(right_n_leaves, this_name, prefix, right_start):
                    new_tree_dict = tree_dict.copy()
                    new_tree_dict.update(left_tree_dict)
                    new_tree_dict.update(right_tree_dict)
                    yield new_tree_dict

def _generate_random_host_dict(n_leaves):
    return _generate_random_trees(n_leaves, 'hTop', 'h')

def _generate_random_parasite_dict(n_leaves):
    return _generate_random_trees(n_leaves, 'pTop', 'p')

def _generate_random_trees(n_leaves: int, top_name: str, prefix: str):
    """
    We don't actually generate all possible trees in this
    format. In the code, you will see that we only generate a right-heavy
    tree, meaning that the right subtree has equal or greater number of
    nodes than the left subtree. We do this to reduce the number of trees
    that are isomorphic to one another.
    """
    tree_dict = {}
    if n_leaves == 1:
        tree_dict[top_name] = ('Top', prefix + '0', None, None)
        return tree_dict
    else:
        left_start = 1
        left_name = prefix + str(left_start)
        mid = n_leaves // 2
        left_n_leaves = random.randint(1, mid)
        right_n_leaves = n_leaves - left_n_leaves
        right_start = 2 * left_n_leaves
        right_name = prefix + str(right_start)
        bot_name = prefix + '0'
        tree_dict[top_name] = ('Top', bot_name, (bot_name, left_name), (bot_name, right_name))
        left_tree_dict = _generate_random_trees_helper(left_n_leaves, bot_name, prefix, left_start)
        right_tree_dict = _generate_random_trees_helper(right_n_leaves, bot_name, prefix, right_start)
        tree_dict.update(left_tree_dict)
        tree_dict.update(right_tree_dict)
        return tree_dict

def _generate_random_trees_helper(n_leaves: int, parent: str, prefix: str, start: int):
    tree_dict = {}
    this_name = prefix + str(start)
    if n_leaves == 1:
        tree_dict[(parent, this_name)] = (parent, this_name, None, None)
        return tree_dict
    else:
        left_start = start + 1
        left_name = prefix + str(left_start)
        mid = n_leaves // 2
        left_n_leaves = random.randint(1, mid)
        right_n_leaves = n_leaves - left_n_leaves
        right_start = start + 1 + (2 * left_n_leaves - 1)
        right_name = prefix + str(right_start)
        tree_dict[(parent, this_name)] = (parent, this_name, (this_name, left_name), (this_name, right_name))
        left_tree_dict = _generate_random_trees_helper(left_n_leaves, this_name, prefix, left_start)
        right_tree_dict = _generate_random_trees_helper(right_n_leaves, this_name, prefix, right_start)
        tree_dict.update(left_tree_dict)
        tree_dict.update(right_tree_dict)
        return tree_dict

def _generate_all_tip_mapping(host_dict, parasite_dict):
    """
    Return an iterator to all possible parasite tree to
    host tree mapping. Each mapping is represented in lists of tuples.
    Each tuple is of the form (parasiteLeaf, hostLeaf).
    The list contains |parasiteLeaf| == |hostLeaf| elements.
    """
    host_leaves = input_reader.ReconInput._leaves_from_tree_dict(host_dict)
    parasite_leaves = input_reader.ReconInput._leaves_from_tree_dict(parasite_dict)
    for host_leaves_permuted in itertools.product(host_leaves, repeat=len(parasite_leaves)):
        mapping = {}
        for i, key in enumerate(sorted(parasite_leaves)):
            mapping[key] = host_leaves_permuted[i]
        yield mapping

def _generate_random_tip_mapping(host_dict, parasite_dict):
    host_leaves = input_reader.ReconInput._leaves_from_tree_dict(host_dict)
    parasite_leaves = input_reader.ReconInput._leaves_from_tree_dict(parasite_dict)
    mapping = {}
    for key in parasite_leaves:
        mapping[key] = random.choice(host_leaves)
    return mapping
