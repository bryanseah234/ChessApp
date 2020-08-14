# import flask, random

# app = flask.Flask(__name__)

# @app.route('/')
# def home():
# 	return flask.render_template('home.html')

# @app.route('/<colour>')
# def color(colour):
# 	if colour[:2] == '0x': colour = '#' + colour[2:]
# 	return flask.render_template('index.html', colour=colour)

# @app.route('/random')
# def rand():
# 	colour = '#'
# 	for i in range(6):
# 		colour += str(hex(random.randint(0,15)))[-1]
# 	return flask.render_template('index.html', colour=colour)

# @app.route('/colour', methods=['GET', 'POST'])
# def search():
# 	colour = flask.request.form['colour'].replace(' ','').lower()
# 	if colour[0] == '#':
# 	  colour = '0x'+ colour[1:]
# 	return flask.redirect("/" + colour)

# @app.route("/favicon.ico")
# def favicon():
#   return flask.send_file("favicon.ico")

# app.run('0.0.0.0')

# from flask import Flask
# from flask import request, render_template
# from chess import WebInterface, Board

# app = Flask(__name__)
# ui = WebInterface()

# @app.route('/')
# def root():
#     return render_template('index.html')

# @app.route('/newgame')
# def newgame():
#     ui.board = Board()
#     ui.inputlabel = f'{game.turn} player: '
#     ui.btnlabel = 'Move'
#     return render_template('chess.html', ui=ui)

# app.run('0.0.0.0')

from flask import Flask
from flask import request, render_template
render_template('index.html')