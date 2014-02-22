from flask import Blueprint, abort
from flask import request, redirect, render_template, Response, url_for, current_app as app


main = Blueprint('main', __name__)
@main.route('/')
def index():
    return render_template("desktop/home.html")

