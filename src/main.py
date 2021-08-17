import numpy as np
import pandas as pd
from random import randint

from src import utils, graph

def init_conversation(full_prop_graph, ratings, g_zscore, movie_rate, age, age_auth):
    sub_graph = full_prop_graph.copy()

    sub_graph = graph.remove_films_by_age(age, age_auth, movie_rate, sub_graph)
    # sub_graph['prop'].unique()
    return utils.show_props(sub_graph, 0.33), sub_graph

def second_interation(sub_graph, p_chosen):
    return utils.prop_most_pop(sub_graph, p_chosen)

def third_interation(sub_graph, o_chosen, p_chosen, ratings):

    # create vectors of movies and objects of preference and set seed and user id
    prefered_objects = [sub_graph[(sub_graph['prop'] == p_chosen) & (sub_graph['obj'] == o_chosen)]['obj_code'].unique()[0]]
    prefered_prop = [(p_chosen, o_chosen)]

    return prefered_objects, prefered_prop

def conversation(full_prop_graph, sub_graph, resp, g_zscore, watched, prefered_objects, prefered_prop, user_id, p_chosen, o_chosen, edgelist, bandit):

    if len(sub_graph) == 0 or len(sub_graph.index.unique()) == 0:
        return { "response": "There are no movies that corresponds to your preferences on our database or you already watched them all"}, True, [], []
    # while user did not like recommendation or property suggestion do not shrink graph again
    # or if sub graph is empty there are no entries or there are no movies, recommendation fails
    if resp == "no" or resp == "watched":
        # choose action and ask if user liked it
        ask = 0 if bandit.pull() else 1

        # if ask suggest new property
        if not ask and len(sub_graph.index.unique()) > 1:
            # show most relevant property
            # top_p = graph.order_props_relevance(sub_graph, g_zscore, prefered_prop, [1/3, 1/3, 1/3])
            top_p = graph.order_props_pr(sub_graph, g_zscore, edgelist, watched, prefered_objects, prefered_prop,
                                         [0.8, 0.2], [1/3, 1/3, 1/3], True)

            dif_properties = top_p.drop_duplicates()#[:5]
            attributes = []
            for i in range(0, len(dif_properties)):
                p_topn = str(dif_properties.iloc[i]['prop'])
                o_topn = str(dif_properties.iloc[i]['obj'])
                attributes.append({ "id": i+1, "property": p_topn, "object": o_topn})

            return { "attributes":  attributes, "ask": ask }, True, top_p, dif_properties

        # if ask != 0 recommend movie
        else:
            top_m = graph.order_movies_by_pagerank(sub_graph, edgelist, watched, prefered_objects, [0.8, 0.2], True)

            # case if all movies with properties were recommended but no movies were accepted by user
            if len(top_m.index) == 0:
                return { "response": "You have already watched all the movies with the properties you liked :("}, True, [], []

            rec = full_prop_graph.loc[top_m.index[0]]['title'].unique()[0]
            m_id = str(top_m.index[0])
            imdb_id = full_prop_graph.loc[top_m.index[0]]['imdbId'].unique()[0]
            props = []

            for i in range(0, len(prefered_prop)):
                t = prefered_prop[i]
                props.append({ "id": i+1, "property": str(t[0]), "object": str(t[1])})

            return { "recommendation": rec, "properties": props, "ask": ask, "movie_id": m_id, "imdbId": imdb_id }, True, top_m, []

    else:
        return graph.shrink_graph(sub_graph, p_chosen, o_chosen), False, [], []

def recommend(full_prop_graph, sub_graph, watched, prefered_objects, prefered_prop, edgelist):
    top_m = graph.order_movies_by_pagerank(sub_graph, edgelist, watched, prefered_objects, [0.8, 0.2], True)

    # case if all movies with properties were recommended but no movies were accepted by user
    if len(top_m.index) == 0:
        return { "response": "You have already watched all the movies with the properties you liked :("}, True, [], []

    rec = full_prop_graph.loc[top_m.index[0]]['title'].unique()[0]
    m_id = str(top_m.index[0])
    imdb_id = full_prop_graph.loc[top_m.index[0]]['imdbId'].unique()[0]
    props = []

    for i in range(0, len(prefered_prop)):
        t = prefered_prop[i]
        props.append({ "id": i+1, "property": str(t[0]), "object": str(t[1])})

    return { "recommendation": rec, "properties": props, "ask": 1, "movie_id": m_id, "imdbId": imdb_id }, top_m, []

def answer(sub_graph, ask, ans, watched, edgelist, prefered_objects, prefered_prop, top, dif_properties, full_prop_graph, user_id):
    if ask == 0:
        return properties(sub_graph, ans, watched, edgelist, prefered_objects, prefered_prop, top, dif_properties)
    else:
        return recommendation(sub_graph, ans, watched, edgelist, prefered_objects, prefered_prop, top, full_prop_graph, user_id)
    

def properties(sub_graph, resp, watched, edgelist, prefered_objects, prefered_prop, top_p, dif_properties):

    reward = 0

    # if user chose prop, get the prop, the obj and obj code and append it to the favorties properties
    # else remove all prop from graph
    if resp != "no":
        if isinstance(resp, str) and len(resp) > 1:
            #resp  = resp[:1]
            resp = resp.split(")")[0]
        p_chosen = str(dif_properties.iloc[int(resp) - 1]['prop'])
        o_chosen = str(dif_properties.iloc[int(resp) - 1]['obj'])
        o_chose_code = str(sub_graph[(sub_graph['prop'] == p_chosen) & (sub_graph['obj'] == o_chosen)]['obj_code'].unique()[0])
        prefered_objects.append(o_chose_code)
        prefered_prop.append((p_chosen, o_chosen))
        if resp == 1:
            reward = 1
    
        sub_graph = graph.shrink_graph(sub_graph, p_chosen, o_chosen)
    # else:
    #     for index, row in dif_properties.iterrows():
    #         p = row[0]
    #         o = row[1]
    #         sub_graph = sub_graph.loc[(sub_graph['obj'] != o)]
                
    return sub_graph, True, watched, edgelist, prefered_objects, prefered_prop, reward

def recommendation(sub_graph, resp, watched, edgelist, prefered_objects, prefered_prop, top_m, full_prop_graph, user_id):
    
    m_id = top_m.index[0]
    rec = full_prop_graph.loc[m_id]['title'].unique()[0]
    imdb_id = full_prop_graph.loc[m_id]['imdbId'].unique()[0]

    reward = 0

    if resp == "yes":
        return { "recommendation": rec, "movie_id": str(m_id), "imdbId": imdb_id }, False, watched, edgelist, prefered_objects, prefered_prop, reward
    else:
        if resp == "watched":
            reward = 1
            watched.append(m_id)
            edgelist = edgelist.append({"origin": user_id, "destination": 'M' + str(m_id)}, ignore_index=True)

        top_m = top_m.drop(m_id)
        sub_graph = sub_graph.drop(m_id)
    
    # updated bandit based on the response of the user
    return sub_graph, True, watched, edgelist, prefered_objects, prefered_prop, reward