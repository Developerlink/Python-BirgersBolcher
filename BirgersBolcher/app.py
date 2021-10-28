"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy #pip install -U Flask-SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import InputRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from random import choice

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisasecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candydrop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Color(db.Model):
    __tablename__ = 'colors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    candydrops = db.relationship('CandyDrop', backref='color', lazy=True, uselist=False)

    def __repr__(self):
        return self.name

class Sourness(db.Model):
    __tablename__ = 'sournesses'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(250), nullable=False)
    candydrops = db.relationship('CandyDrop', backref='sourness', lazy=True, uselist=False)

    def __repr__(self):
        return self.value


class Strength(db.Model):
    __tablename__ = 'strengths'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(250), nullable=False)
    candydrops = db.relationship('CandyDrop', backref='strength', lazy=True, uselist=False)

    def __repr__(self):
        return self.value

class Type(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    candydrops = db.relationship('CandyDrop', backref='type', lazy=True, uselist=False)

    def __repr__(self):
        return self.name

class CandyDrop(db.Model):
    __tablename__ = 'candydrops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    material_cost = db.Column(db.Integer, nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey('colors.id'), nullable=False) #Using the table name!
    sourness_id = db.Column(db.Integer, db.ForeignKey('sournesses.id'), nullable=False)
    strength_id = db.Column(db.Integer, db.ForeignKey('strengths.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=False)

    def __repr__(self):
        return f"CandyDrop(name:'{self.name}', weight:'{self.weight}', material_cost:'{self.material_cost}', " \
               f"color: '{self.color_id}', sourness: '{self.sourness_id}' strength: '{self.strength_id}', type: '{self.type_id}')"




app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

def color_choices():
    return db.session.query(Color).all()

def sourness_choices():
    return db.session.query(Sourness).all()

def strength_choices():
    return Strength.query.all()

def type_choices():
    return Type.query.all()

class CandyDropForm(FlaskForm):
    name = StringField('Candy Drop Name', validators=[InputRequired()])
    color = QuerySelectField("Color", validators=[InputRequired()], query_factory=color_choices)
    weight = IntegerField("Weight in grams", validators=[InputRequired()])
    sourness = QuerySelectField("Sourness", query_factory=sourness_choices, validators=[InputRequired()])
    strength = QuerySelectField("Srength", query_factory=strength_choices, validators=[InputRequired()])
    type = QuerySelectField("Type", query_factory=type_choices, validators=[InputRequired()])
    material_cost = IntegerField('Material cost in "cents"', validators=[InputRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def home():
    all_candies = CandyDrop.query.all()
    red_candies = db.session.query(CandyDrop).join(Color).filter(Color.name == 'Rød').all()
    red_blue_candies = db.session.query(CandyDrop).join(Color).filter(db.or_(Color.name == 'Rød', Color.name == 'Blå')).all()
    not_red_candies = db.session.query(CandyDrop).join(Color).filter(Color.name != 'Rød').order_by(CandyDrop.name.asc()).all()
    starting_b_candies = db.session.query(CandyDrop).filter(CandyDrop.name.like('b%')).all()
    containing_e_candies = db.session.query(CandyDrop).filter(CandyDrop.name.like('%e%')).all()
    weight_less_10_candies = db.session.query(CandyDrop).filter(CandyDrop.weight < 10).order_by(CandyDrop.weight.asc()).all()
    weight_between_10_12_candies = db.session.query(CandyDrop).filter(10 <= CandyDrop.weight, CandyDrop.weight <= 12).all()
    top_3_heaviest_candies = db.session.query(CandyDrop).order_by(CandyDrop.weight.desc()).limit(3).all()
    random_candy = db.session.query(CandyDrop).order_by(func.random()).first()
    return render_template('index.html', all_candies=all_candies, red_candies=red_candies, red_blue_candies=red_blue_candies,
                           not_red_candies=not_red_candies, starting_b_candies=starting_b_candies, containing_e_candies=containing_e_candies,
                           weight_less_10_candies=weight_less_10_candies, weight_between_10_12_candies=weight_between_10_12_candies,
                           top_3_heaviest_candies=top_3_heaviest_candies, random_candy=random_candy)

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = CandyDropForm()
    if form.validate_on_submit():
        name = form.name.data
        weight = form.weight.data
        material_cost = form.material_cost.data
        color_id = form.color.data.id
        sourness_id = form.sourness.data.id
        strength_id = form.strength.data.id
        type_id = form.type.data.id
        new_candydrop = CandyDrop(
            name=name,
            weight=weight,
            material_cost=material_cost,
            color_id=color_id,
            sourness_id=sourness_id,
            strength_id=strength_id,
            type_id=type_id
        )
        db.session.add(new_candydrop)
        db.session.commit()
        return redirect(url_for('add'))
    return render_template('add.html', form=form)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def hello():
    """Renders a sample page."""
    return render_template("index.html")

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
