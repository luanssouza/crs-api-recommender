from werkzeug.exceptions import HTTPException
from flask import Flask, request
from flask_swagger_ui import get_swaggerui_blueprint

import numpy as np
import pandas as pd

import main
import utils

from random import seed

app = Flask(__name__)

# import database and import of the ratings
full_prop_graph = pd.read_csv("resources/wikidata_integration_small.csv")
full_prop_graph = full_prop_graph.set_index('movie_id')

ratings = pd.read_csv("resources/1851_movies_ratings.txt", sep='\t', header=None)
ratings.columns = ['user_id', 'movie_id', 'rating']

edgelist = pd.DataFrame(columns=['origin', 'destination'])
ratings['origin'] = ['U' + x for x in ratings['user_id'].astype(str)]
ratings['destination'] = ['M' + x for x in ratings['movie_id'].astype(str)]
edgelist = pd.concat([edgelist, ratings[['origin', 'destination']]])


sub_graph = []
top = []
dif_properties = []

watched = []
prefered_objects = []
prefered_prop = []
user_id = ''

p_chosen = ""
o_chosen = ""

seed(42)

# get the global zscore for the movies
g_zscore = utils.generate_global_zscore(full_prop_graph, path="resources/global_properties.csv", flag=False)

@app.route("/", methods = ['GET'])
def home():
    return "Access the <a href='/swagger'>documentation</a> for more details."

@app.route("/init", methods = ['GET'])
def init():
    global sub_graph
    properties, sub_graph = main.init_conversation(full_prop_graph, ratings, g_zscore)  

    return { "properties":  properties.tolist() }

@app.route("/second", methods = ['POST'])
def second():
    data = request.json
    global p_chosen
    p_chosen = data['property']

    return { "characteristics":  main.second_interation(sub_graph, data['property']).tolist() }

@app.route("/third", methods = ['POST'])
def third():
    data = request.json
    global watched, prefered_objects, prefered_prop, user_id, sub_graph, top, dif_properties
    watched, prefered_objects, prefered_prop, user_id = main.third_interation(sub_graph, data['object'], p_chosen, ratings)

    global o_chosen
    o_chosen = data['object']

    sub_graph, next_step, top, dif_properties = main.conversation(full_prop_graph, sub_graph, "", g_zscore, watched, prefered_objects, prefered_prop, user_id, p_chosen, data['object'], edgelist)
    
    response, next_step, top, dif_properties = main.conversation(full_prop_graph, sub_graph, "no", g_zscore, watched, prefered_objects, prefered_prop, user_id, p_chosen, data['object'], edgelist)
    return response

@app.route("/answer", methods = ['POST'])
def answer():
    data = request.json
    resp = data['resp']
    ask = data['ask']
    global sub_graph
    global watched, edgelist, prefered_objects, prefered_prop, top, dif_properties

    response, next_step, watched, edgelist, prefered_objects, prefered_prop = main.answer(sub_graph, ask, resp, watched, edgelist, prefered_objects, prefered_prop, top, dif_properties, full_prop_graph, user_id)
    
    if next_step:
        sub_graph = response
        response, next_step, top, dif_properties = main.conversation(full_prop_graph, sub_graph, resp, g_zscore, watched, prefered_objects, prefered_prop, user_id, p_chosen, o_chosen, edgelist)
        if not next_step:
            sub_graph = response
            response, next_step, top, dif_properties = main.conversation(full_prop_graph, sub_graph, "no", g_zscore, watched, prefered_objects, prefered_prop, user_id, p_chosen, o_chosen, edgelist)

    return response

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return { "message" : "Internal Server Error!", "status": 500 }, 500

# region SWAGGER CONFIG
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "CRS-API-recommender"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT)
# endregion

if __name__ == "__main__":
    # app.run()
    app.run(debug=True)