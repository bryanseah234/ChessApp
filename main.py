import os
from flask import Flask
from flask import render_template, redirect
from docs.chess import WebInterface, Board
from flask import request
from docs.MoveHistory import MoveHistory
from copy import copy


# app = Flask(__name__ )
app = Flask(__name__, template_folder='docs/templates', static_folder='docs/static')
ui = WebInterface()
game = Board()
history = MoveHistory(10)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/newgame', methods=['POST','GET'])
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
    game.winner = None
    ui.winner = game.winner
    return redirect('/play')


@app.route('/play',methods=['POST', 'GET'])
def play():
    # TODO: get player move from GET request object
    # TODO: if there is no player move, render the page template
	if request.method == "GET":
		pass
	elif request.method == "POST":
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
			elif game.winner != None:
				ui.endgame = "disabled"
				ui.direct = "/newgame"
				ui.errmsg = game.msg
				ui.btnlabel = "NEW GAME"
				ui.board = game.board_html()
				return render_template('chess.html', ui=ui, game=game)
			ui.board = game.board_html()
			game.next_turn()
			ui.inputlabel = f'{game.turn} player: '
			ui.errmsg = game.msg
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
    ui.inputlabel = f'{game.turn} pawn promote to (Please choose from r, k, b, or q):'
    ui.btnlabel = "PROMOTE"
    ui.direct = "/promote"
    if request.method == "POST":
        promote = request.form['player_input']
        ui.errmsg = ' '
        if game.promoteprompt(promote) == False:
            ui.errmsg = f'Invalid promotion. Please choose from r, k, b, or q'
            return redirect('/promote')
        else:
            game.promote(promote)
            ui.board = game.board_html()
            game.next_turn()
            ui.inputlabel = f'{game.turn} player: '
            ui.btnlabel = "MOVE"
            ui.direct = "/play"
            ui.errmsg = game.msg
            return redirect('/play')
    return render_template('chess.html', ui=ui, game=game)

@app.route('/undo',methods=['POST', 'GET'])
def undo():
	move = history.pop()
	if move == None:
		ui.errmsg = "Invalid undo. MoveHistory is empty."
		return redirect('/play')
	game._position = move
	if ui.direct == "/promote":
		ui.btnlabel = "MOVE"
		ui.direct = "/play"
		ui.inputlabel = f'{game.turn} player: '
		game.msg = ' '
		ui.errmsg = game.msg
		return redirect('/play')
	game.next_turn()	
	ui.inputlabel = f'{game.turn} player: '
	game.msg = ' '
	ui.errmsg = game.msg
	return redirect('/play')

app.run('0.0.0.0')


