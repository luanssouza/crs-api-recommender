import numpy as np
import pandas as pd
import networkx as nx

import utils

def order_movies_by_pop(sub_graph: pd.DataFrame, ratings: pd.DataFrame):
    """
    Function that order the movies based on its' popularity
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param ratings: ratings dataset in the format user_id, movie_id, rating
    :return: ordered movies on a DataFrame
    """
    ordered_movies = pd.DataFrame(index=sub_graph.index.unique(), columns=['value'])
    for m in sub_graph.index.unique():
        ordered_movies.at[m] = len(ratings[(ratings['movie_id'] == m)])

    return ordered_movies.sort_values(by=['value'], ascending=False)

def order_props(sub_graph: pd.DataFrame, global_zscore: dict, properties: list, weight_vec: list):
    """
    Function that order the properties based on the entropy of the property, the relevance of the value locally
    normalized measured by the zscore of the count of the property on the sub graph and the relevance of the value
    globally measured by the  zscore of the count of the property on the full graph
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param global_zscore: dictionary of all properties on the dataset (full graph)
        prop and obj keys and count and zscores as columns
    :param properties: properties list that the user has liked in the past. The list has tuples (property, value), e.g.
        (actor, Di Caprio); (producer, Disney); etc
    :param weight_vec: vector of weigths for the entropy and local and global relevance respectively
        the size of this list is 3 always
    :return: ordered properties on a DataFrame
    """

    # make slice of subgraph of just property and obj
    sub_slice = sub_graph[['prop', 'obj']]

    # calculate zscore locally
    split_dfs = pd.DataFrame(columns=['prop', 'obj', 'count'])
    for prop in sub_slice['prop'].unique():
        df_prop = sub_slice[sub_slice['prop'] == prop]
        df_lzscore = df_prop.copy()
        df_lzscore['count'] = df_prop.groupby('obj').transform('count')
        df_lzscore['local_zscore'] = (df_lzscore['count'] - df_lzscore['count'].mean()) / df_lzscore['count'].std()
        split_dfs = pd.concat([split_dfs, df_lzscore])

    split_dfs['global_zscore'] = split_dfs.apply(lambda x: global_zscore['global_zscore'][(x['prop'], x['obj'])], axis=1)

    # calculate entropy and create entropy column
    entrs = utils.calculate_entropy(sub_graph)
    split_dfs['h'] = split_dfs.apply(lambda x: entrs[x['prop']], axis=1)

    # generate zscore for the entropy
    split_dfs['h_zscore'] = (split_dfs['h'] - split_dfs['h'].mean()) / split_dfs['h'].std()

    # replace na when std is nan to 0
    split_dfs = split_dfs.fillna(0)

    # sum the zscores for the total value
    split_dfs['value'] = (weight_vec[0] * split_dfs['h_zscore']) + \
                         (weight_vec[1] * split_dfs['local_zscore']) + \
                         (weight_vec[2] * split_dfs['global_zscore'])

    # remove the favorites to not show again
    for t in properties:
        split_dfs = split_dfs[(split_dfs['prop'] != t[0]) & (split_dfs['obj'] != t[1])]

    return split_dfs.sort_values(by=['value'], ascending=False)


def shrink_graph(sub_graph: pd.DataFrame, prop: str, obj: str):
    """
    Function that shrinks the graph to a sub graph based on the property and value passed on the parameters.
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param prop: property the user is looking for
    :param obj: value of property the user is looking for
    :return: shirked graph of the one passed as parameter
    """
    shrinked = sub_graph[(sub_graph['prop'] == prop) & (sub_graph['obj'] == obj)]

    for movie_id in shrinked.index.unique():
        shrinked = pd.concat([shrinked, sub_graph.loc[movie_id]])

    return shrinked.sort_index()


def order_movies_by_pagerank(sub_graph: pd.DataFrame, edgelist: pd.DataFrame,  watched: list, objects: list,
                             weight_vec: list, use_objs=False):
    """
    Function that order the movies based on its' pagerank on the graph. The adj matrix is created on the
    WikidataIntegration project, in the adjacency_matrix.py
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param edgelist: edge list of users and movies from the dataset. The dataframe has two columns, the origin of the
        edge and the destination
    :param watched: movies that the user watched
    :param objects: objects (e.g. Martin Scorsese, Leonardo Di Caprio, Bred Pitt, Disney, etc) on the graph that
        the user liked
    :param weight_vec: list with size two and sum equal to one with the weights of the personalization to the watched
    movies and the rest of the nodes
    :param use_objs: boolean value to use on the pagerank or not the objects list that the user liked
    :return: ordered movies on a DataFrame
    """

    # append edgelist that only hast movies and user edges and add the movies to values on the wikidata edges
    copy = sub_graph.copy()
    copy['origin'] = ['M' + x for x in copy.index.astype(str)]
    copy['destination'] = copy['obj_code']
    full_edgelist = pd.concat([edgelist, copy[['origin', 'destination']]])

    # create graph
    G = nx.from_pandas_edgelist(full_edgelist, 'origin', 'destination')

    # get movie codes for the watched movies
    movie_codes = ['M' + str(x) for x in watched]

    # if user did not watched any movies and dont want to use the prop values on the personalized PR
    # then personalization is none
    # else create personalization and assign weights on personalization dict
    preferences = movie_codes
    personalization = {}
    if not use_objs and (len(preferences) == 0):
        personalization = None
    elif use_objs:
        preferences = preferences + objects

    if personalization is not None:
        value_watched = weight_vec[0] / len(preferences)
        value_all = weight_vec[1] / (G.number_of_nodes() - len(preferences))

        for node in G.nodes:
            if node in preferences:
                personalization[node] = value_watched
            else:
                personalization[node] = value_all

    # calculate pagerank
    pr_np = nx.pagerank_scipy(G, personalization=personalization, max_iter=1000)

    # order movies
    ordered_movies = pd.DataFrame(index=sub_graph.index.unique(), columns=['value'])
    for m in sub_graph.index.unique():
        movie_code = 'M' + str(m)
        ordered_movies.at[m] = pr_np[movie_code]

    return ordered_movies.sort_values(by=['value'], ascending=False)