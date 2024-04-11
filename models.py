from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ModelClothing(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    material_consumption = db.Column(db.Numeric)
    description = db.Column(db.Text)
    photos = db.relationship('ModelPhoto', backref='model_clothing', lazy=True)
    additional_info = db.relationship('AdditionalInfoForModelClothing', backref='model_clothing', uselist=False, lazy=True)


class ModelPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_clothing_id = db.Column(db.Integer, db.ForeignKey('model_clothing.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)


class AdditionalInfoForModelClothing(db.Model):
    model_clothing_id = db.Column(db.Integer, db.ForeignKey('model_clothing.id'), primary_key=True, autoincrement=False, unique=True, index=True)
    care_instructions = db.Column(db.Text)
    materials = db.Column(db.Text)
    cost = db.Column(db.Numeric)


class Pattern(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    sizes = db.Column(db.String(255))
    photo = db.Column(db.String(255))


class ModelPattern(db.Model):
    model_clothing_id = db.Column(db.Integer, db.ForeignKey('model_clothing.id'), primary_key=True, autoincrement=False)
    pattern_id = db.Column(db.Integer, db.ForeignKey('pattern.id'), primary_key=True, autoincrement=False)
