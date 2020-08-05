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