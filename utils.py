import numpy as np
import pandas as pd
from scipy.stats import entropy

def prop_most_pop(sub_graph: pd.DataFrame, prop: str):
    """
    Function that returns the most popular values for property prop
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param prop: property the user is looking for
    :return: list of the ten most popular values of property
    """
    return sub_graph[(sub_graph['prop'] == prop)]['obj'].value_counts().index.values[:10]


def calculate_entropy(sub_graph: pd.DataFrame):
    """
    Function that calculates the entropy for all properties
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :return: entropies of properties on dictionary
    """
    entropies = {}
    for prop in sub_graph['prop'].value_counts().index:
        o_values = sub_graph[(sub_graph['prop'] == prop)]['obj'].value_counts()
        denom = sum(o_values.values)
        prob = []
        for value in o_values.index:
            num = o_values[value]
            prob.append(num / denom)

        entropies[prop] = entropy(prob, base=2)

    return entropies


def generate_global_zscore(full_graph: pd.DataFrame, path: str, flag=False):
    """
    Function that generates a dictionary with all the zscore of movies. If flag is true, generate file,
    else only reads the file
    :param full_graph: full graph of the movie dataset
    :param path: path to save the generated DataFrame
    :param flag: True to generate file of DataFrame with global zscores, False to read it
    :return: dictionary with prop and obj keys and count and zscores as columns
    """
    if flag:
        full_slice = full_graph[['prop', 'obj']]
        full_split_dfs = pd.DataFrame(columns=['prop', 'obj', 'count', 'global_zscore'])
        for prop in full_slice['prop'].unique():
            df_prop = full_slice[full_slice['prop'] == prop]
            df_gzscore = df_prop.copy()
            df_gzscore['count'] = df_prop.groupby('obj').transform('count')
            df_gzscore['global_zscore'] = (df_gzscore['count'] - df_gzscore['count'].mean()) / df_gzscore['count'].std()
            full_split_dfs = pd.concat([full_split_dfs, df_gzscore])

        full_split_dfs.to_csv(path, mode='w', header=True, index=False)

    return pd.read_csv(path, usecols=['prop', 'obj', 'count', 'global_zscore']).set_index(['prop', 'obj']).to_dict()
