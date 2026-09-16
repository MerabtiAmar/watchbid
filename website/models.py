from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150))
    tel = db.Column(db.String(10))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    produits = db.relationship('Watch', cascade="all, delete-orphan", backref='user')
    bids = db.relationship('Bid', cascade="all, delete-orphan", backref='user')

class Watch(db.Model):
    id_watch = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(50))
    marque = db.Column(db.String(50))
    categorie = db.Column(db.String(50))
    annee = db.Column(db.Integer)
    prix = db.Column(db.Float)
    dateStart = db.Column(db.Date)
    dateEnd = db.Column(db.Date)
    desc = db.Column(db.String(300))
    detail = db.Column(db.String(300))
    img1 = db.Column(db.String(100))
    img2 = db.Column(db.String(100))
    img3 = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bids = db.relationship('Bid', cascade="all, delete-orphan", backref='watch')

    def current_max_offer(self):
        max_offer = db.session.query(func.max(Bid.offer)).filter(Bid.id_product == self.id_watch).scalar()
        return max_offer if max_offer else 0

class Bid(db.Model):
    id_bid = db.Column(db.Integer, primary_key = True)
    id_product = db.Column(db.Integer, db.ForeignKey('watch.id_watch'))
    id_buyer = db.Column(db.Integer, db.ForeignKey('user.id'))
    offer = db.Column(db.Float)




