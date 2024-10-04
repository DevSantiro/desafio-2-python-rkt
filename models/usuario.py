from db.database import db
from flask_login import UserMixin


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"
    # Definição dos campos no Banco de Dados
    id        = db.Column(db.Integer,     primary_key = True)
    usuario   = db.Column(db.String(80),  nullable = False, unique=True)
    senha     = db.Column(db.String(350), nullable = False)
    permissao = db.Column(db.String(80),  nullable = False, server_default="user")
