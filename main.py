from flask import Flask
from flask import render_template, redirect
from chess import WebInterface, Board
from flask import request
from MoveHistory import MoveHistory
from copy import copy


app = Flask(__name__)
ui = WebInterface()
game = Board()
history = MoveHistory(10)


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
    ui.errmsg = ' '
    ui.btnlabel = 'MOVE'
    ui.direct = '/play'
    ui.winner = game.winner
    return redirect('/play')
    return render_template('chess.html', ui=ui)

@app.route('/play',methods=['POST', 'GET'])
def play():
    # TODO: get player move from GET request object
    # TODO: if there is no player move, render the page template

	if request.method == "POST":
		Move = request.form['player_input']
		ui.errmsg = ' '
		if not game.validation(Move):

			history.push(copy(game._position))

			start, end = game.prompt(Move)
			game.update(start,end)
			coord = game.promotepawns()
            # colour = game.get_piece(coord).colour
			if game.promotion == True:
				# ui.direct = "/promote"
				# ui.inputlabel = f'{game.turn} pawn promote to:'
				# ui.btnlabel = "PROMOTE"
				return redirect('/promote')
			ui.board = game.board_html()
			game.next_turn()
			ui.inputlabel = f'{game.turn} player: '

			return render_template('chess.html', ui=ui, game=game)
		else:
			ui.errmsg = game.validation(Move)
			return render_template('chess.html', ui=ui, game=game)
	ui.board = game.board_html()

	return render_template('chess.html', ui=ui, game=game)
    # TODO: Validate move, redirect player back to /play again if move is invalid
    # If move is valid, check for pawns to promote
    # Redirect to /promote if there are pawns to promote, otherwise 

@app.route('/promote', methods=['POST', 'GET'])
def promote():
    ui.board = game.board_html()
    ui.inputlabel = f'{game.turn} pawn promote to:'
    ui.btnlabel = "PROMOTE"
    ui.direct = "/promote"
    if request.method == "POST":
        promote = request.form['player_input']
        ui.errmsg = ' '
        if game.promoteprompt(promote) == False:
            ui.errmsg = f'Invalid promotion. Please choose from r, k, b, and q'
            return redirect('/promote')
        else:
            game.promote(promote)
            ui.board = game.board_html()
            game.next_turn()
            ui.inputlabel = f'{game.turn} player: '
            ui.btnlabel = "MOVE"
            ui.direct = "/play"
            return redirect('/play')
    return render_template('chess.html', ui=ui, game=game)

@app.route('/undo',methods=['POST', 'GET'])
def undo():
	move = history.pop()
	if move == None:
		ui.errmsg = "Invalid undo. MoveHistory is empty."
		return redirect('/play')
	game._position = move
	game.next_turn()
	ui.inputlabel = f'{game.turn} player: '
	return redirect('/play')

app.run('0.0.0.0')


