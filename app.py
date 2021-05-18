from werkzeug.exceptions import HTTPException
from flask import Flask, request
from flask_swagger_ui import get_swaggerui_blueprint

import numpy as np
import pandas as pd

from joblib import dump, load

from models.dialog import Dialog
import main
import utils
import bucket

import logging
from random import seed
from pathlib import Path

app = Flask(__name__)

# import database and import of the ratings
full_prop_graph = pd.read_csv("resources/wikidata_integration_small.csv")
full_prop_graph = full_prop_graph.set_index('movie_id')

ratings = pd.read_csv("resources/ratings.csv")

# import graph edge
edgelist = pd.read_csv("resources/edgelist.csv")

# get the global zscore for the movies
g_zscore = utils.generate_global_zscore(full_prop_graph, path="resources/global_properties.csv", flag=False)

dialog_path = 'resources/dialogs'

Path(dialog_path).mkdir(parents=True, exist_ok=True)

seed(42)

@app.route("/", methods = ['GET'])
def home():
    return "Access the <a href='/swagger'>documentation</a> for more details."

@app.route("/init", methods = ['GET'])
def init():
    user_id = request.args.get('userId')
    dialog = Dialog(None, user_id, g_zscore, None, edgelist)

    properties, dialog.subgraph, dialog.dialog_id = main.init_conversation(full_prop_graph, ratings, g_zscore)

    # dump(dialog, dialogpath(dialog.dialog_id))
    bucket.save_object(dialog.dialog_id, dialog)

    return { "properties":  properties.tolist(), "dialogId": dialog.dialog_id }

@app.route("/second", methods = ['POST'])
def second():
    data = request.json

    dialog_id = data['dialogId']

    # dialog = load(dialogpath(dialog_id))
    dialog = bucket.loads_object(dialog_id)

    dialog.p_chosen = data['property']

    # dump(dialog, dialogpath(dialog.dialog_id))
    bucket.save_object(dialog.dialog_id, dialog)

    return { "characteristics":  main.second_interation(dialog.subgraph, dialog.p_chosen).tolist() }

@app.route("/third", methods = ['POST'])
def third():
    data = request.json

    dialog_id = data['dialogId']

    # dialog = load(dialogpath(dialog_id))
    dialog = bucket.loads_object(dialog_id)

    dialog.o_chosen = data['object']
    
    prefered_objects, prefered_prop = main.third_interation(dialog.subgraph, dialog.o_chosen, dialog.p_chosen, ratings)

    dialog.prefered_infos(prefered_prop, prefered_objects)

    subgraph, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, "", dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist)
    
    dialog.subgraph = subgraph
    dialog.dialog_properties_infos(top, dif_properties)

    response, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, "no", dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist)

    dialog.dialog_properties_infos(top, dif_properties)
    dialog.ask = response['ask']

    # dump(dialog, dialogpath(dialog.dialog_id))
    bucket.save_object(dialog.dialog_id, dialog)

    return response

@app.route("/answer", methods = ['POST'])
def answer():
    data = request.json
    resp = data['resp']

    dialog_id = data['dialogId']

    # dialog = load(dialogpath(dialog_id))
    dialog = bucket.loads_object(dialog_id)

    response, next_step, watched, edgelist, prefered_objects, prefered_prop = main.answer(dialog.subgraph, dialog.ask, resp, dialog.watched, dialog.edgelist, dialog.prefered_objects, dialog.prefered_prop, dialog.top, dialog.dif_properties, full_prop_graph, dialog.user_id)

    dialog.dialog_infos(watched, edgelist, prefered_prop, prefered_objects)
    
    if next_step:
        dialog.subgraph = response

        response, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, resp, dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist)

        dialog.dialog_properties_infos(top, dif_properties)

        if not next_step:
            dialog.subgraph = response

            response, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, "no", dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist)

            dialog.ask = response['ask']

            dialog.dialog_properties_infos(top, dif_properties)

    # dump(dialog, dialogpath(dialog.dialog_id))
    bucket.save_object(dialog.dialog_id, dialog)

    return response

def dialogpath(dialog_id):
    return '{0}/{1}.joblib'.format(dialog_path, dialog_id)

# region ErrorHandlers
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(e)
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return { "message" : "Internal Server Error!", "status": 500 }, 500
# endregion ErrorHandlers

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