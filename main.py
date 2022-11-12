import sqlalchemy.orm.query
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "some secret string"

db = SQLAlchemy(app)
Bootstrap(app)


class Myform(FlaskForm):
    new_rating = StringField("rating", validators=[DataRequired()])
    new_review = StringField("review", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Addform(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Integer)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(1000))
    img_url = db.Column(db.String(1000))


# ----------------------------------------------Routes-----------------------------------------------------


@app.route("/")
def home():
    all_movie = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movie)):
        all_movie[i].ranking = len(all_movie) - i
    db.session.commit()
    return render_template("index.html", movies=all_movie)


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    form = Myform()
    if request.method == 'POST' and form.validate_on_submit():
        movie_to_update = Movie.query.get(id)
        movie_to_update.rating = form.new_rating.data
        movie_to_update.review = form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form)


@app.route("/delete/<id>", methods=["GET", "POST"])
def delete(id):
    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = Addform()
    if form.validate_on_submit() and request.method == 'POST':
        parameters = {
            'api_key': 'c0b30fc84b8673f0457e4d6b010faa63',
            'query': form.title.data
        }
        response = requests.get('https://api.themoviedb.org/3/search/movie', params=parameters)
        return render_template('select.html', response=response)
    return render_template('add.html', form=form)


@app.route("/select/<movie_id>", methods=["GET", "POST"])
def select(movie_id):
    parameters = {
        'api_key': 'c0b30fc84b8673f0457e4d6b010faa63',
    }
    data = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}', params=parameters).json()
    new_movie = Movie(
        title=data['title'],
        year=data['release_date'].split('-')[0],
        description=data['overview'],
        img_url=f'https://image.tmdb.org/t/p/original/{data["poster_path"]}'
        )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
