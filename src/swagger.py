from flask_swagger_ui import get_swaggerui_blueprint

from __main__ import app

swagger_url = '/swagger'

api_url = '/static/swagger.json'

swagger_blueprint = get_swaggerui_blueprint(
    swagger_url,
    api_url,
    config={
        'app_name': "CRS-API-recommender"
    }
)

app.register_blueprint(swagger_blueprint)