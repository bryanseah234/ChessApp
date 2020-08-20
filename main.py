from flask import Flask
from flask import render_template, redirect
from chess import WebInterface, Board
from flask import request


app = Flask(__name__)
ui = WebInterface()
game = Board()



@app.route('/')
def root():
    return render_template('index.html')

@app.route('/newgame')
def newgame():
    # Note that in Python, objects and variables
    # in the global space are available to
    # top-level functions
    game.start()
    ui.board = game.board_html()
    ui.inputlabel = f'{game.turn} player: '
    ui.errmsg = None
    ui.btnlabel = 'Move'
    return redirect('/play')
    return render_template('chess.html', ui=ui)

@app.route('/play',methods=['POST', 'GET'])
def play():
    # TODO: get player move from GET request object
    # TODO: if there is no player move, render the page template
	errmsg = None
	ui.errmsg = None
	try:
		if request.method == "POST":
			Move = request.form['player_input']
			ui.errmsg = None
			start, end, errmsg = game.prompt(Move)
			game.update(start,end)
			ui.board = game.board_html()
			game.next_turn()
			ui.inputlabel = f'{game.turn} player: '
	except Exception as e:
		ui.errmsg = "ERROR: " + str(e)
		return render_template('chess.html', ui=ui, game=game)
	return render_template('chess.html', ui=ui, game=game)
    # TODO: Validate move, redirect player back to /play again if move is invalid
    # If move is valid, check for pawns to promote
    # Redirect to /promote if there are pawns to promote, otherwise 

@app.route('/promote')
def promote():
    pass


app.run('0.0.0.0')


