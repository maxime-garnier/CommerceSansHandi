from flask import Flask, request, render_template
import os
import requests
from flask_swagger_ui import get_swaggerui_blueprint
from flask_caching import Cache


#Documentation
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Commerce Sans Handi"
    }
)


def create_app(test_config=None):
    app = Flask(__name__, static_url_path="/")
    app.register_blueprint(swaggerui_blueprint)

    #Cache
    config = {
        "DEBUG": True,          # some Flask specific configs
        "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
        "CACHE_DEFAULT_TIMEOUT": 300
    }
    app.config.from_mapping(config)
    cache = Cache(app)
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})

    # Variable pour API acceslibre
    key = ""
    API_acceslibre = ""

    # Variable pour API commerce
    nb_res = 20
    API_Commerce = "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/commerces-export-openstreetmap-france/records?limit=" + str(nb_res) + "&"


    @app.route("/")
    @cache.cached(timeout=50)
    def index():
        return render_template('index.html')


    @app.route("/commerces", methods=['GET'])
    @cache.cached(timeout=50)
    def all_commerces():
        all = requests.get(API_Commerce)
        results=all.json()["results"]
        indices = list(range(len(results)))
        addresses = [results[i]["address"] for i in indices]
        names = [results[i]["name"] for i in indices]
        typesA = [results[i]["type"][0].replace("_"," ") for i in indices]
        typesR = [results[i]["type"][1:] if len(results[i]["type"][0]) > 1 else [] for i in indices]
        availabilies = [0 for i in range(len(results))]
        for x in typesR :
            for y in x :
                y = y.replace("_"," ")
        return render_template('searchpage.jinja2',ind=indices,add=addresses, nam=names, typA=typesA, typR=typesR, ava=availabilies)
    

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    app.run(host='0.0.0.0', port=port)
