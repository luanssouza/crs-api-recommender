
from flask import Flask, request

import numpy as np
import pandas as pd

from joblib import dump, load

from src.bandit.bandit_factory import bandit_factory
from src.models.dialog import Dialog
from src import main, utils, bucket

from random import seed
from pathlib import Path

app = Flask(__name__)

from src.errorHandlers import error_blueprint
from src.swagger import swagger_blueprint

app.register_blueprint(swagger_blueprint)
app.register_blueprint(error_blueprint)

# import database and import of the ratings
full_prop_graph = pd.read_csv("resources/wikidata_integration_small.csv")
full_prop_graph = full_prop_graph.set_index('movie_id')

ratings = pd.read_csv("resources/ratings.csv")

# import graph edge
edgelist = pd.read_csv("resources/edgelist.csv")

# get the global zscore for the movies
# g_zscore = utils.generate_global_zscore(full_prop_graph, path="resources/global_properties.csv", flag=False)
g_zscore = utils.generate_global_zscore(full_prop_graph, edgelist, path="resources/global_properties.csv", flag=True)

movie_rate = pd.read_csv("resources/rated_movies.csv", index_col="movie_id")
dialog_path = 'resources/dialogs'

Path(dialog_path).mkdir(parents=True, exist_ok=True)

np.random.RandomState(42)

@app.route("/", methods = ['GET'])
def home():
    return "Access the <a href='/swagger'>documentation</a> for more details."

@app.route("/init", methods = ['POST'])
def init():
    data = request.json

    print("data: {0}".format(data))
    
    dialog_id = data['dialogId']

    age = int(data['age']) if "age" in data else 18
    age_auth = data['ageAuth'] if "ageAuth" in data else 0


    # create bandit to decide when to ask and recommend
    ban = bandit_factory()

    dialog = Dialog(dialog_id, "U7315", g_zscore, None, edgelist, ban)

    properties, dialog.subgraph = main.init_conversation(full_prop_graph, ratings, g_zscore, movie_rate, age, age_auth)

    # dump(dialog, dialogpath(dialog.dialog_id))
    bucket.save_object(dialog.dialog_id, dialog)

    return { "properties":  properties, "dialogId": dialog.dialog_id }

@app.route("/second", methods = ['POST'])
def second():
    data = request.json

    print("data: {0}".format(data))

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

    print("data: {0}".format(data))

    dialog_id = data['dialogId']

    # dialog = load(dialogpath(dialog_id))
    dialog = bucket.loads_object(dialog_id)

    dialog.o_chosen = data['object']
    
    prefered_objects, prefered_prop = main.third_interation(dialog.subgraph, dialog.o_chosen, dialog.p_chosen, ratings)

    dialog.prefered_infos(prefered_prop, prefered_objects)

    subgraph, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, "", dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist, dialog.bandit)
    
    dialog.subgraph = subgraph
    dialog.dialog_properties_infos(top, dif_properties)

    response, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, "no", dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist, dialog.bandit)

    dialog.dialog_properties_infos(top, dif_properties)
    dialog.ask = response['ask']

    # dump(dialog, dialogpath(dialog.dialog_id))
    bucket.save_object(dialog.dialog_id, dialog)

    return response

@app.route("/answer", methods = ['POST'])
def answer():
    data = request.json

    print("data: {0}".format(data))

    resp = data['resp']

    dialog_id = data['dialogId']

    # dialog = load(dialogpath(dialog_id))
    dialog = bucket.loads_object(dialog_id)

    response, next_step, watched, edgelist, prefered_objects, prefered_prop, reward = main.answer(dialog.subgraph, dialog.ask, resp, dialog.watched, dialog.edgelist, dialog.prefered_objects, dialog.prefered_prop, dialog.top, dialog.dif_properties, full_prop_graph, dialog.user_id)

    dialog.dialog_infos(watched, edgelist, prefered_prop, prefered_objects, reward)
    
    if next_step:
        dialog.subgraph = response

        response, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, resp, dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist, dialog.bandit)

        dialog.dialog_properties_infos(top, dif_properties)

        if not next_step:
            dialog.subgraph = response

            response, next_step, top, dif_properties = main.conversation(full_prop_graph, dialog.subgraph, "no", dialog.g_zscore, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.user_id, dialog.p_chosen, dialog.o_chosen, dialog.edgelist, dialog.bandit)

            dialog.ask = response['ask']

            dialog.dialog_properties_infos(top, dif_properties)
        else:
            dialog.ask = response['ask']

    # dump(dialog, dialogpath(dialog.dialog_id))
    bucket.save_object(dialog.dialog_id, dialog)

    return response

@app.route("/recommend", methods = ['POST'])
def recommend():
    data = request.json

    print("data: {0}".format(data))

    dialog_id = data['dialogId']

    dialog = bucket.loads_object(dialog_id)

    response, top, dif_properties = main.recommend(full_prop_graph, dialog.subgraph, dialog.watched, dialog.prefered_objects, dialog.prefered_prop, dialog.edgelist)

    dialog.dialog_properties_infos(top, dif_properties)
    dialog.ask = response['ask']

    bucket.save_object(dialog.dialog_id, dialog)

    return response

def dialogpath(dialog_id):
    return '{0}/{1}.joblib'.format(dialog_path, dialog_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '5000'))