from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_cors import CORS
from flasgger import Swagger
from datetime import timedelta
import os

app = Flask(__name__)

CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "segredoJWT")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "DJ Music System API",
        "description": "API para sistema de músicas para DJ com autenticação JWT.",
        "version": "1.0.0"
    },
    "basePath": "/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Digite no formato: Bearer SEU_TOKEN_JWT"
        }
    }
}

swagger = Swagger(app, template=swagger_template)

users = []

musicas = [
    {
        "id": 1,
        "titulo": "Música A",
        "artista": "DJ A"
    },
    {
        "id": 2,
        "titulo": "Música B",
        "artista": "DJ B"
    },
    {
        "id": 3,
        "titulo": "Música C",
        "artista": "DJ C"
    },
    {
        "id": 4,
        "titulo": "Set Noturno",
        "artista": "DJ Lucas"
    }
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    """
    Registra um novo usuário
    ---
    tags:
      - Usuários
    parameters:
      - in: body
        name: body
        required: true
        description: Dados do usuário para cadastro
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: usuario@email.com
            password:
              type: string
              example: "123456"
    responses:
      201:
        description: Usuário registrado com sucesso
        examples:
          application/json:
            message: Usuário registrado com sucesso.
            user:
              id: 1
              email: usuario@email.com
      400:
        description: Dados inválidos ou usuário já cadastrado
        examples:
          application/json:
            message: Email e senha são obrigatórios.
    """
    data = request.get_json()

    if not data:
        return jsonify({"message": "Dados não enviados."}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email e senha são obrigatórios."}), 400

    user_exists = next((user for user in users if user["email"] == email), None)

    if user_exists:
        return jsonify({"message": "Usuário já cadastrado."}), 400

    user = {
        "id": len(users) + 1,
        "email": email,
        "password": password
    }

    users.append(user)

    return jsonify({
        "message": "Usuário registrado com sucesso.",
        "user": {
            "id": user["id"],
            "email": user["email"]
        }
    }), 201


@app.route("/login", methods=["POST"])
def login():
    """
    Realiza login do usuário
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        description: Dados para autenticação
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: usuario@email.com
            password:
              type: string
              example: "123456"
    responses:
      200:
        description: Login realizado com sucesso
        examples:
          application/json:
            message: Login realizado com sucesso.
            token: token_jwt_gerado
      400:
        description: Dados não enviados
        examples:
          application/json:
            message: Dados não enviados.
      401:
        description: Credenciais inválidas
        examples:
          application/json:
            message: Credenciais inválidas.
    """
    data = request.get_json()

    if not data:
        return jsonify({"message": "Dados não enviados."}), 400

    email = data.get("email")
    password = data.get("password")

    user = next(
        (
            user for user in users
            if user["email"] == email and user["password"] == password
        ),
        None
    )

    if not user:
        return jsonify({"message": "Credenciais inválidas."}), 401

    token = create_access_token(identity=user["email"])

    return jsonify({
        "message": "Login realizado com sucesso.",
        "token": token
    }), 200


@app.route("/musicas", methods=["GET"])
@jwt_required()
def listar_musicas():
    """
    Lista músicas cadastradas
    ---
    tags:
      - Músicas
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de músicas retornada com sucesso
        examples:
          application/json:
            - id: 1
              titulo: Música A
              artista: DJ A
            - id: 2
              titulo: Música B
              artista: DJ B
      401:
        description: Token ausente ou inválido
      422:
        description: Token mal formatado
    """
    return jsonify(musicas), 200


@app.route("/status", methods=["GET"])
def status():
    """
    Verifica se a API está funcionando
    ---
    tags:
      - Sistema
    responses:
      200:
        description: API funcionando corretamente
        examples:
          application/json:
            message: API do DJ Music System está funcionando.
    """
    return jsonify({
        "message": "API do DJ Music System está funcionando."
    }), 200


if __name__ == "__main__":
    app.run(debug=True)