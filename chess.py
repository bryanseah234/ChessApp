class WebInterface:
    def __init__(self):
        self.inputlabel = None
        self.btnlabel = None
        self.errmsg = None
        self.board = None



class MoveError(Exception):
    '''Custom error for invalid moves.'''
    pass


class BasePiece:
    def __init__(self,colour):
        if type(colour) != str:
            raise TypeError('colour argument must be str')
        elif colour.lower() not in {'white','black'}:
            raise ValueError('colour must be {white,black}')
        else:
            self.colour = colour

    def __repr__(self):
        return f'BasePiece({repr(self.colour)})'
    
    def __str__(self):
        try:
            return f'{self.colour} {self.name}'
        except NameError:
            return f'{self.colour} piece'

    @staticmethod
    def vector(start, end):
        x = end[0] - start[0]
        y = end[1] - start[1]
        dist = abs(x) + abs(y)
        return x, y, dist


class King(BasePiece):
    name = 'king'
    def __repr__(self):
        return f'King({repr(self.colour)})'
    
    def isvalid(self, start: tuple, end: tuple):
        '''King can move 1 step horizontally or vertically.'''
        x, y, dist = self.vector(start, end)
        return dist == 1


class Queen(BasePiece):
    name = 'queen'
    def __repr__(self):
        return f'Queen({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if (x != 0 and y != 0 and abs(x) == abs(y)) \
                or (x == 0 and y != 0) \
                or (y == 0 and x != 0):
            return True
        else:
            return False


class Bishop(BasePiece):
    name = 'bishop'
    def __repr__(self):
        return f'Bishop({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if x != 0 and y != 0 and abs(x) == abs(y):
            return True
        else:
            return False


class Knight(BasePiece):
    name = 'knight'
    def __repr__(self):
        return f'Knight({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if dist == 3 and 0 < abs(x) < 3 and 0 < abs(y) < 3:
            return True
        else:
            return False


class Rook(BasePiece):
    name = 'rook'
    def __repr__(self):
        return f'Rook({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple, **kwargs):
        x, y, dist = self.vector(start, end)
        if kwargs.get('castling', False):
            if self.colour == 'white':
                row = 0
            elif self.colour == 'black':
                row = 7
            if start[1] != end[1] != row:
                return False
            elif not((start[0] == 0 and end[0] == 3)
                   or (start[0] == 7 and end[0] == 5)):
                return False
            else:
                return True
        else:
            if (x == 0 and y != 0) or (y == 0 and x != 0):
                return True
            else:
                return False


class Pawn(BasePiece):
    name = 'pawn'
    def __repr__(self):
        return f'Pawn({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple, **kwargs):
        x, y, dist = self.vector(start, end)
        xmove = 1 if kwargs.get('capture', False) else 0
        if x == xmove:
            if self.colour == 'black' and y == -1 \
                    or self.colour == 'white' and y == 1:
                return True
        return False


class Board:
    '''
    ATTRIBUTES

    turn <{'white', 'black'}>
        The current player's colour.
    
    winner <{'white', 'black', None}>
        The winner (if game has ended).
        If game has not ended, returns None

    checkmate <{'white', 'black', None}>
        Whether any player is checkmated.

    METHODS
    
    start()
        Start a game. White goes first.

    display()
        Print the game board.

    prompt(colour)
        Prompt the player for input.

    next_turn()
        Go on to the next player's turn.

    isvalid(start, end)
        Checks if the move (start -> end) is valid for this turn.

    update(start, end)
        Carries out the move (start -> end) and updates the board.
    '''
    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', False)
        self._position = {}
        self.winner = None
        self.checkmate = None
    
    def coords(self):
        return list(self._position.keys())

    def pieces(self):
        return list(self._position.values())

    def add(self, coord: tuple, piece):
        self._position[coord] = piece

    def move(self, start, end):
        piece = self.get_piece(start)
        self.remove(start)
        self.add(end, piece)
        self.get_piece(end).notmoved = False

    def remove(self, pos):
        del self._position[pos]

    def castle(self, start, end):
        '''Carry out castling move (assuming move is validated)'''
        self.move(start, end)
        # Move the king
        row = start[1]
        if start[0] == 0:
            self.move((4, row), (2, row))
        elif start[0] == 7:
            self.move((4, row), (6, row))

    def get_piece(self, coord):
        '''
        Retrieves the piece at `coord`.
        `coord` is assumed to be a 2-ple of ints representing
        (col,row).

        Return:
        BasePiece instance
        or None if no piece found
        '''
        return self._position.get(coord, None)

    def alive(self, colour, name):
        for piece in self.pieces():
            if piece.colour == colour and piece.name == name:
                return True
        return False
    
    def promotepawns(self, PieceClass=None):
        for coord in self.coords():
            row = coord[1]
            piece = self.get_piece(coord)
            for opprow, colour in zip([0, 7], ['black', 'white']):
                if row == opprow and piece.name == 'pawn' \
                        and piece.colour == colour:
                    if PieceClass is None:
                        PieceClass = self.promoteprompt()
                    promoted_piece = PieceClass(colour)
                    self.remove(coord)
                    self.add(coord, promoted_piece)

    def king_and_rook_unmoved(self, colour, rook_coord):
        row = rook_coord[1]
        king = self.get_piece((4, row))
        rook = self.get_piece(rook_coord)
        return king.notmoved and rook.notmoved

    def no_pieces_between_king_and_rook(self, colour, rook_coord):
        row = rook_coord[1]
        rook_col = rook_coord[0]
        if rook_col == 0:
            columns = (1, 2, 3)
        elif rook_col == 7:
            columns = (5, 6)
        else:
            raise MoveError('Invalid move: castling from {rook_coord}')
        for col in columns:
            if self.get_piece((col, row)) is not None:
                return False
        return True

    def movetype(self, start, end):
        '''
        Determines the type of board move by:
        1. Checking if the player is moving a piece of their
           own colour
        2. Checking if the piece at `start` and the piece at
           `end` are the same colour
        3. Checking if the move is valid for that piece type

        Returns:
        'move' for normal moves
        'capture' for captures
        'castling' for rook castling
        None for invalid moves
        '''
        if self.debug:
            print(f'== movetype({start}, {end}) ==')
        if start is None or end is None:
            return None
        start_piece = self.get_piece(start)
        end_piece = self.get_piece(end)
        if self.debug:
            print(f'START_PIECE: {start_piece}')
            print(f'END_PIECE: {end_piece}')
        if start_piece is None \
                or start_piece.colour != self.turn:
            return None
        if end_piece is not None:
            if end_piece.colour != start_piece.colour:
                return 'capture'
            # handle special cases
            elif start_piece.name == 'pawn' \
                    and end_piece.colour != start_piece.colour \
                    and start_piece.isvalid(start, end, capture=True):
                return 'capture'
            else:
                return None
        else:  # end piece is None
            if start_piece.name == 'rook' \
                    and start_piece.isvalid(start, end, castling=True) \
                    and self.king_and_rook_unmoved(self.turn, start) \
                    and self.no_pieces_between_king_and_rook(self.turn, start):
                return 'castling'
            elif start_piece.isvalid(start, end):
                return 'move'
            else:
                return None
        return True

    @classmethod
    def promoteprompt(cls):
        choice = input(f'Promote pawn to '
                    '(r=Rook, k=Knight, b=Bishop, '
                    'q=Queen): ').lower()
        if choice not in 'rkbq':
            return cls.promoteprompt()
        elif choice == 'r':
            return Rook
        elif choice == 'k':
            return Knight
        elif choice == 'b':
            return Bishop
        elif choice == 'q':
            return Queen

    def printmove(self, start, end, **kwargs):
        startstr = f'{start[0]}{start[1]}'
        endstr = f'{end[0]}{end[1]}'
        print(f'{self.get_piece(start)} {startstr} -> {endstr}', end='')
        if kwargs.get('capture', False):
            print(f' captures {self.get_piece(end)}')
        elif kwargs.get('castling', False):
            print(f' (castling)')
        else:
            print('')

    def start(self):
        colour = 'black'
        self.add((0, 7), Rook(colour))
        self.add((1, 7), Knight(colour))
        self.add((2, 7), Bishop(colour))
        self.add((3, 7), Queen(colour))
        self.add((4, 7), King(colour))
        self.add((5, 7), Bishop(colour))
        self.add((6, 7), Knight(colour))
        self.add((7, 7), Rook(colour))
        for x in range(0, 8):
            self.add((x, 6), Pawn(colour))

        colour = 'white'
        self.add((0, 0), Rook(colour))
        self.add((1, 0), Knight(colour))
        self.add((2, 0), Bishop(colour))
        self.add((3, 0), Queen(colour))
        self.add((4, 0), King(colour))
        self.add((5, 0), Bishop(colour))
        self.add((6, 0), Knight(colour))
        self.add((7, 0), Rook(colour))
        for x in range(0, 8):
            self.add((x, 1), Pawn(colour))
        
        self.turn = 'white'

        for piece in self.pieces():
            piece.notmoved = True

    def display(self):
        '''
        Displays the contents of the board.
        Each piece is represented by two letters.
        First letter is the colour (W for white, B for black).
        Second letter is the name (Starting letter for each piece).
        '''
        if self.debug:
            print('== DEBUG MODE ON ==')
        # helper function to generate symbols for piece
        def sym(piece):
            colour_sym = piece.colour[0].upper()
            piece_sym = piece.name[0].upper()
            return f'{colour_sym}{piece_sym}'

        # Row 7 is at the top, so print in reverse order
        print(' ' * 4, end='')
        print('  '.join([f'{i:2}' for i in range(8)]), end='\n\n')
        for row in range(7, -1, -1):
            print(f'{row:2}  ', end='')
            for col in range(8):
                coord = (col, row)  # tuple
                if coord in self.coords():
                    piece = self.get_piece(coord)
                    print(f'{sym(piece)}', end='')
                else:
                    piece = None
                    print('  ', end='')
                if col == 7:     # Put line break at the end
                    print('')
                else:            # Print two spaces between pieces
                    print('  ', end='')
            print(' '*15)
            if self.checkmate is not None:
                print(f'{self.checkmate} is checkmated!')

    def prompt(self):
        if self.debug:
            print('== PROMPT ==')
        def valid_format(inputstr):
            return len(inputstr) == 5 and inputstr[2] == ' ' \
                and inputstr[0:1].isdigit() \
                and inputstr[3:4].isdigit()

        def valid_num(inputstr):
            for char in (inputstr[0:1] + inputstr[3:4]):
                if char not in '01234567':
                    return False
            return True

        def split_and_convert(inputstr):
            '''Convert 5-char inputstr into start and end tuples.'''
            start, end = inputstr.split(' ')
            start = (int(start[0]), int(start[1]))
            end = (int(end[0]), int(end[1]))
            return (start, end)

        while True:
            inputstr = input(f'{self.turn.title()} player: ')
            if not valid_format(inputstr):
                print('Invalid move. Please enter your move in the '
                      'following format: __ __, _ represents a digit.')
            elif not valid_num(inputstr):
                print('Invalid move. Move digits should be 0-7.')
            else:
                start, end = split_and_convert(inputstr)
                if self.movetype(start, end) is None:
                    print('Invalid move. Please make a valid move.')
                else:
                    return start, end

    def update(self, start, end):
        '''
        Update board according to requested move.
        If an opponent piece is at end, capture it.
        '''
        if self.debug:
            print('== UPDATE ==')
        movetype = self.movetype(start, end)
        if movetype is None:
            raise MoveError(f'Invalid move ({self.printmove(start, end)})')
        elif movetype == 'castling':
            self.printmove(start, end, castling=True)
            self.castle(start, end)
        elif movetype == 'capture':
            self.printmove(start, end, capture=True)
            self.remove(end)
            self.move(start, end)
        elif movetype == 'move':
            self.printmove(start, end)
            self.move(start, end)
        else:
            raise MoveError('Unknown error, please report '
                             f'(movetype={repr(movetype)}).')
        self.promotepawns()
        if not self.alive('white', 'king'):
            self.winner = 'black'
        elif not self.alive('black', 'king'):
            self.winner = 'white'

    def next_turn(self):
        if self.debug:
            print('== NEXT TURN ==')
        if self.turn == 'white':
            self.turn = 'black'
        elif self.turn == 'black':
            self.turn = 'white'