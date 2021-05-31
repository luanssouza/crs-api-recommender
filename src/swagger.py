from flask_swagger_ui import get_swaggerui_blueprint

swagger_url = '/swagger'

api_url = '/static/swagger.json'

swagger_blueprint = get_swaggerui_blueprint(
    swagger_url,
    api_url,
    config={
        'app_name': "CRS-API-recommender"
    }
)