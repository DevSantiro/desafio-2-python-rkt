import hashlib
import os

from flask       import Flask, jsonify, request
from db.database import db
from datetime    import datetime

# Models
from models.usuario  import Usuario
from models.refeicao import Refeicao

# Autenticacoes
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

# Iniciando o APP
app = Flask(__name__)

# Variaveis do APP
app.config['SECRET_KEY']              = "developBySantiro_2024-10-02"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE')

# Instanciando o Objeto de Login do Flask
login_manager = LoginManager()

# Iniciando a instancia do Banco com o APP
db.init_app(app)

# Registrando o Login com o APP
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, user_id)


@app.route("/login", methods=["POST"])
def login():
    data     = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        # Login
        user = Usuario.query.filter_by(usuario=username).first()

        if user and user.senha == hashlib.md5(password.encode('utf-8')).hexdigest():
            login_user(user)
            return jsonify({"message": "Autenticado com sucesso"}), 200

    return jsonify({"message": "Credenciais inválidas"}), 400


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"}), 200

@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username and password:
        senha = hashlib.md5(password.encode('utf-8')).hexdigest()
        user = Usuario(usuario=username, senha=senha)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 200
    
    return jsonify({"message": "Dados inválidos"}), 400

@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def get_user(id_user):
    user = db.session.get(Usuario, id_user)

    if user:
        return jsonify({"username": user.usuario})
    
    return jsonify({"message": "Usuário não encontrado"}), 401

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def put_user(id_user):
    data = request.get_json()
    user = db.session.get(Usuario, id_user)

    if user and data.get("password"):
        user.senha = data.get("password")
        db.session.commit()

        return jsonify({"message": f"Usuário {id_user}: {user.usuario} atualizado com sucesso!"})
    
    return jsonify({"message": "Usuário não encontrado"}), 404

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = db.session.get(Usuario, id_user)

    if id_user == current_user.id:
        return jsonify({"message": "Não é permitido deletar o próprio usuário"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": f"Usuário {id_user}: {user.usuario} deletado com sucesso!"})
    
    return jsonify({"message": "Usuário não encontrado"}), 404

@app.route("/snacks", methods=["GET"])
@login_required
def get_refeicoes():
    refeicoes = Refeicao.query.filter_by(id_usuario=current_user.id).all()

    if refeicoes:
        lista_refeicoes = []

        for refeicao in refeicoes:
            lista_refeicoes.append({
                "nome":           refeicao.nome,
                "descricao":      refeicao.descricao,
                "data_hora":      refeicao.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
                "pertence_dieta": refeicao.pertence_dieta
            })

        return jsonify(lista_refeicoes)

    return jsonify({"message": "Refeições não encontradas!"}), 404

@app.route("/snack/<int:id_refeicao>", methods=["GET"])
@login_required
def get_refeicao_by_id(id_refeicao):

    refeicao = Refeicao.query.filter_by(id=id_refeicao, id_usuario=current_user.id).first()

    if refeicao:
        return jsonify({
            "nome":           refeicao.nome,
            "descricao":      refeicao.descricao,
            "data_hora":      refeicao.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
            "pertence_dieta": refeicao.pertence_dieta
        })

    return jsonify({"message": "Refeição não encontrada!"}), 404

@app.route("/snack/<int:id_refeicao>", methods=["PUT"])
@login_required
def put_refeicao_by_id(id_refeicao):
    data = request.json

    nome           = data.get("nome")
    descricao      = data.get("descricao")
    data_hora      = data.get("data_hora")
    pertence_dieta = data.get("pertence_dieta")

    if nome and descricao and data_hora and pertence_dieta:
        refeicao = db.session.get(Refeicao, id_refeicao)

        if refeicao:
            refeicao.nome           = nome
            refeicao.descricao      = descricao
            refeicao.data_hora      = data_hora
            refeicao.pertence_dieta = pertence_dieta
            db.session.commit()

            return jsonify({"message": f"refeição: {refeicao.nome} atualizada com sucesso!"}), 200

        else:
            return jsonify({"message": "refeição não encontrada!"}), 404

    return jsonify({"message": "Dados inválidos!"}), 400


@app.route("/snack/<int:id_refeicao>", methods=["DELETE"])
@login_required
def delete_refeicao_by_id(id_refeicao):
    data = request.json

    nome           = data.get("nome")
    descricao      = data.get("descricao")
    data_hora      = data.get("data_hora")
    pertence_dieta = data.get("pertence_dieta")

    if nome and descricao and data_hora and pertence_dieta:
        refeicao = db.session.get(Refeicao, id_refeicao)

        if refeicao:
            db.session.delete(refeicao)
            db.session.commit()

            return jsonify({"message": f"refeição: {refeicao.nome} removida com sucesso!"}), 200

        else:
            return jsonify({"message": "refeição não encontrada!"}), 404

    return jsonify({"message": "Dados inválidos!"}), 400


@app.route("/snack", methods=["POST"])
@login_required
def post():
    data = request.json

    nome           = data.get("nome")
    descricao      = data.get("descricao")
    data_hora      = data.get("data_hora")
    pertence_dieta = data.get("pertence_dieta", 1)

    if nome and descricao and data_hora:
        refeicao = Refeicao(
            id_usuario=current_user.id,
            nome=nome,
            descricao=descricao,
            data_hora=data_hora,
            pertence_dieta=pertence_dieta
        )

        db.session.add(refeicao)
        db.session.commit()
        
        return jsonify({"message": "refeição cadastrada com sucesso"}), 200

    return jsonify({"message": "Dados inválidos!"}), 400



if __name__ == "__main__":
    app.run(debug=True)
