import numpy as np

def entropy(graph_len, obj_count):
        '''
        Args:
        graph: pd.DataFrame
        obj_count: int
        '''
        v = obj_count
        p1 = float(v) / graph_len
        p2 = 1.0 - p1

        if p1 == 0 or p1 == 1:
            return 0
        return (- p1 * np.log2(p1) - p2 * np.log2(p2))

def calculate_entropy(graph, col):
    entropy_dict_small_feature = dict()

    c = graph.groupby(col).size()

    graph_len = len(graph['title'].unique())

    c = c.to_dict()
    for k, v in c.items():
        node_entropy_self = entropy(graph_len, v)
        entropy_dict_small_feature[k] = node_entropy_self

    return entropy_dict_small_feature