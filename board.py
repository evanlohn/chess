# a simple chess board state stored as a 2-D array

all_ranks = ''.join([str(i + 1) for i in range(8)])
all_files = 'abcdefgh'
WHITE = 'W'
BLACK = 'B'

def sq_to_inds(sq):
    return all_ranks.index(sq[1]), all_files.index(sq[0])

class Board:

    def __init__(self, config):
        self.board_lst = [[None for i in all_files] for j in all_ranks]
        for color in config:
            for piece in config[color]:
                cls = name_to_cls[piece]
                for loc in config[color][piece]:
                    row, col = sq_to_inds(loc)
                    self.board_lst[row][col] = cls(color) 
        
    def __str__(self):
        s = ''
        for row in self.board_lst[::-1]:
            for piece in row:
                if piece:
                    s += str(piece)
                else:
                    s += 'xx'
                s += ' '
            s += '\n'
        return s

class Piece:
    def __init__(self, color):
        self.color = color
        self.name = ''

    def __str__(self):
        return self.color + self.name

    def __repr__(self):
        return str(self)

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Pawn]
        self.has_moved = False

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Knight]

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
        self.name = cls_to_name[Rook]


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Bishop]


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Queen]

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
        self.name = cls_to_name[King]

name_to_cls = {'p': Pawn, 'k': Knight, 'r': Rook, 'b': Bishop, 'q': Queen, 'K': King}
cls_to_name = {name_to_cls[k]: k for k in name_to_cls}
