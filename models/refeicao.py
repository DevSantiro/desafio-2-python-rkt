from db.database import db

class Refeicao(db.Model):
    __tablename__  = "refeicao"

    id             = db.Column(db.Integer, primary_key = True)
    id_usuario     = db.Column(db.Integer,  db.ForeignKey("usuario.id"))
    nome           = db.Column(db.String(100))
    descricao      = db.Column(db.Text)
    data_hora      = db.Column(db.DateTime(timezone=True))
    pertence_dieta = db.Column(db.SmallInteger, default=1) 
