import requests
from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from elasticsearch import Elasticsearch
import xml.etree.ElementTree as ET
from unidecode import unidecode

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)
app.config['MONGO_URI'] = 'mongodb://mongodb/dbtargetdatachallenge'
mongo = PyMongo(app)

SWAGGER_URL = '/docs'
API_URL = "http://localhost:5000/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'Target Challenge API': "API de Autenticação"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

es = Elasticsearch('http://elasticsearch:9200')
es.indices.delete(index='logs', ignore=[400, 404])
es.indices.create(index='logs', ignore=400)

@app.after_request
def log_request(response):
    data = {
        'timestamp': datetime.utcnow(),
        'method': request.method,
        'path': request.path,
        'status_code': response.status_code,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string
    }
    es.index(index='logs', body=data)
    return response

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username != 'admin' or password != 'admin':
        return jsonify({"message": "Credenciais inválidas"}), 401
    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({"message": "Acesso permitido"}), 200

@app.route('/users', methods=['POST'])
def create_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return {'error': 'Os campos de usuário e a senha são obrigatórios'}, 400

    if mongo.db.users.find_one({'username': username}):
        return {'error': 'O nome de usuário já está em uso'}, 400

    hashed_password = generate_password_hash(password)
    user_id = mongo.db.users.insert_one({'username': username, 'password': hashed_password}).inserted_id

    response = jsonify({
        '_id': str(user_id),
        'username': username,
        'password': password
    })

    response.status_code = 201
    return response



@app.route('/users', methods=['GET'])
def get_allusers():
    users_collection = mongo.db.users
    users = list(users_collection.find())
    if users:
        response = json_util.dumps(users)
        return Response(response, mimetype="application/json"), 200
    else:
        return {'error': 'Nenhum usuário cadastrado'}, 400


@app.route('/users/<id>', methods=['GET'])
def get_userbyid(id):
    users_collection = mongo.db.users
    user = users_collection.find_one({'_id': ObjectId(id)})

    if user:
        response = json_util.dumps(user)
        return Response(response, mimetype="application/json"), 200
    else:
        return {'error': 'Usuário não encontrado'}, 400
    

@app.route('/endereco', methods=['POST'])
def endereco():

    # GET_CEP()
    cep = request.json['cep']
    responseApiCep = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    endereco = responseApiCep.json()
    # 

    # GET_CITYID()
    # 
    # O `unidecode` está em uso pois caso a cidade tivesse acentuação, a api não retornava nada na busca
    # já que só pesquisa sem acentuação.
    # por exemplo `São Paulo` não funcionava, então com unidecode `Sao Paulo` a api retorna valor (id)
    # 
    cidade = unidecode(endereco['localidade'])
    responseApiCodigoCidade = requests.get(f'http://servicos.cptec.inpe.br/XML/listaCidades?city={cidade}')
    xmlCityCode = responseApiCodigoCidade.content
    rootCityCode = ET.fromstring(xmlCityCode)  
    city = rootCityCode.find('cidade')
    if city is None:
        print('Nenhuma cidade encontrada')
        return {'error': 'Cidade não encontrada'}, 400
    id = city.find('id').text
    # 
    
    # GET_WEATHERFORECAST()
    responseApiPrevisao = requests.get(f'http://servicos.cptec.inpe.br/XML/cidade/{id}/previsao.xml')
    xmlWeatherForecast = responseApiPrevisao.content
    rootWeatherForecast = ET.fromstring(xmlWeatherForecast)
    atualization = rootWeatherForecast.find('atualizacao').text
    weatherForecastList = []
    for previsao in rootWeatherForecast.iter('previsao'):
        weatherForecastList.append({
            'dia': previsao.find('dia').text,
            'tempo': previsao.find('tempo').text,
            'maxima': previsao.find('maxima').text,
            'minima': previsao.find('minima').text,
            'iuv': previsao.find('iuv').text
        })
    # 

    output = {
            "cep": cep,
            "logradouro": endereco['logradouro'],
            "complemento": endereco['complemento'],
            "bairro": endereco['bairro'],
            "localidade": endereco['localidade'],
            "uf": endereco['uf'],
            "ibge": endereco['ibge'],
            "gia": endereco['gia'],
            "ddd": endereco['ddd'],
            "siafi": endereco['siafi'],
            "cidadeCode": id,
            "atualizacao": atualization,
            "previsoes": weatherForecastList
        }
            
    return jsonify(output), 200

@app.route('/logs', methods=['GET'])
def get_all_logs():
    logs = search_all_logs()
    return jsonify(logs), 200

def search_all_logs():
    search_query = {
        "query": {
            "match_all": {}
        }
    }

    search_results = es.search(index="logs", body=search_query)

    logs = []
    for hit in search_results['hits']['hits']:
        logs.append(hit['_source'])
    
    return logs

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)