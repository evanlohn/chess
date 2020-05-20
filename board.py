# a simple chess board state stored as a 2-D array

all_ranks = ''.join([str(i + 1) for i in range(8)])
all_files = 'abcdefgh'
WHITE = 'W'
BLACK = 'B'
BOTH = 'WB'

def other(color):
    if color == WHITE:
        return BLACK
    elif color == BLACK:
        return WHITE
    return BOTH

def is_valid(sq):
    if type(sq) == str:
        return (sq[0] in all_files) and (sq[1] in all_ranks)
    return (0 <= sq[0] < len(all_files)) and (0 <= sq[1] < len(all_ranks))

def sq_to_inds(sq):
    if type(sq) == str:
        return all_ranks.index(sq[1]), all_files.index(sq[0])
    return sq

class Board:

    def __init__(self, config):
        self.board_lst = [[None for i in all_files] for j in all_ranks]
        for color in config:
            for piece in config[color]:
                cls = name_to_cls[piece]
                for loc in config[color][piece]:
                    row, col = sq_to_inds(loc)
                    self.board_lst[row][col] = cls(color) 
        self.first_move = None
        self.last_move = None

    def get_piece(self, sq):
        row, col = sq_to_inds(sq)
        return self.board_lst[row][col]
        
    def occupied(self, sq, color=BOTH):
        row, col = sq_to_inds(sq)
        piece = self.board_lst[row][col]
        return (piece is not None) and (piece.color in color)

    def in_check(self, color):
        opposing_color = other(color)
        locs = set()
        for r_ind, row in enumerate(self.board_lst):
            for c_ind, piece in enumerate(row):
                if piece:
                    if (piece.color == opposing_color):
                        locs = locs.union(piece.get_moves((r_ind, c_ind), self))
                    elif piece.name == 'K':
                        king_loc = (r_ind, c_ind)
        return king_loc in locs        



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

class MoveTree:
    def __init__(self, mv, parent=None):
        self.move = mv
        self.main_line = None
        self.parent = parent
        self.aux_lines = [] # unused for now; could be used later to allow analysis

class Piece:

    img_pth = './images/Chess_{}{}t60.png'

    def __init__(self, color):
        self.color = color
        self.name = ''
        self.img_id = ''

    def get_img(self):
        return Piece.img_pth.format(self.img_id, 'l' if self.color == WHITE else 'd')

    # returns all valid moves for a piece to make, following all rules of chess EXCEPT ensuring no check is present after the move.
    def get_moves(self, sq, board):
        return []

    def get_props(self):
        return []

    def restore_props(self, props):
        pass

    def register_move(self):
        pass

    def __str__(self):
        return self.color + self.name

    def __repr__(self):
        return str(self)

class Pawn(Piece):

    

    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Pawn]
        self.has_moved = False
        self.dir = 1 if color == WHITE else -1
        self.img_id = 'p'

    def get_moves(self, sq, board):
        ret = []
        row, col = sq_to_inds(sq)
        # one forward
        one_f = (row + self.dir, col)
        if not board.occupied(one_f):
            ret.append(one_f)

        two_f = (row + 2 * self.dir, col)
        if not self.has_moved and not board.occupied(two_f):
            ret.append(two_f)

        one_fl = (row + self.dir, col - 1)
        if is_valid(one_fl) and board.occupied(one_fl, color=other(self.color)):
            ret.append(one_fl)

        one_fr = (row + self.dir, col + 1)
        if is_valid(one_fr) and board.occupied(one_fr, color=other(self.color)):
            ret.append(one_fr)
        return set(ret)

    def register_move(self):
        self.has_moved = True

    def get_props(self):
        return self.has_moved

    def restore_props(self, props):
        self.has_moved = props

def add_to(sq, off):
    return (sq[0] + off[0], sq[1] + off[1])

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Knight]
        self.img_id = 'n'

    def get_moves(self, sq, board):
        #why do smth clever when u can hardcode lol
        sq_inds = sq_to_inds(sq)
        offs = [(-2,1), (-2, -1), (-1, 2), (-1, -2), (1,2), (1, -2), (2, 1), (2, -1)]
        ms = set()
        for off in offs:
            new_sq = add_to(sq_inds, off)
            if is_valid(new_sq) and not board.occupied(new_sq, color=self.color):
                ms.add(new_sq)
        return ms

def add_until_piece(sq, off, board, opposing_color):
    ray = []
    curr = add_to(sq, off)
    while is_valid(curr) and not board.occupied(curr):
        ray.append(curr)
        curr = add_to(curr, off)

    if is_valid(curr) and board.occupied(curr, color=opposing_color):
        ray.append(curr)
    return set(ray)

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
        self.name = cls_to_name[Rook]
        self.img_id = 'r'

    def get_moves(self, sq, board):
        sq_inds = sq_to_inds(sq)
        offs = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        ms = set()
        for off in offs:
            ms = ms.union(add_until_piece(sq_inds, off, board, other(self.color)))
        return ms

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Bishop]
        self.img_id = 'b'

    def get_moves(self, sq, board):
        sq_inds = sq_to_inds(sq)
        offs = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        ms = set()
        for off in offs:
            ms = ms.union(add_until_piece(sq_inds, off, board, other(self.color)))
        return ms


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Queen]
        self.img_id = 'q'

    def get_moves(self, sq, board):
        sq_inds = sq_to_inds(sq)
        offs = [(-1, 0), (1, 0), (0, 1), (0, -1)] + [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        ms = set()
        for off in offs:
            ms = ms.union(add_until_piece(sq_inds, off, board, other(self.color)))
        return ms

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
        self.name = cls_to_name[King]
        self.img_id = 'k'

    def get_moves(self, sq, board):
        sq_inds = sq_to_inds(sq)
        offs = [(-1, 0), (1, 0), (0, 1), (0, -1)] + [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        ms = set()
        for off in offs:
            new_sq = add_to(sq_inds, off)
            if is_valid(new_sq) and not board.occupied(new_sq, self.color):
                ms.add(new_sq)
        return ms

name_to_cls = {'p': Pawn, 'k': Knight, 'r': Rook, 'b': Bishop, 'q': Queen, 'K': King}
cls_to_name = {name_to_cls[k]: k for k in name_to_cls}


class Move:

    # src and dest must be valid squares (within the bounds of the board)
    def __init__(self, src, dst, board):
        self.src = sq_to_inds(src)
        self.dst = sq_to_inds(dst)
        self.board = board

    def is_valid(self):
        self.piece = self.board.get_piece(self.src)
        if not self.piece:
            return False
        moves = self.piece.get_moves(self.src, self.board)
        #print(moves, self.dst)

        # check that the move follows the rules of piece movement
        if self.dst not in moves:
            return False

        self.make_move()
        in_check = self.board.in_check(self.piece.color)
        self.undo_move()
        return not in_check


    def make_move(self):
        self.piece = self.board.get_piece(self.src)
        self.taken_piece = self.board.get_piece(self.dst)
        self.old_piece_props = self.piece.get_props()
        self.piece.register_move() # might want to pass in dst? # this changes piece props (potentially)
        new_row, new_col = self.dst
        row, col = self.src
        self.board.board_lst[new_row][new_col] = self.piece
        self.board.board_lst[row][col] = None

    def undo_move(self):
        new_row, new_col = self.dst
        row, col = self.src
        self.board.board_lst[new_row][new_col] = self.taken_piece
        self.taken_piece = None
        self.board.board_lst[row][col] = self.piece
        self.piece.restore_props(self.old_piece_props)

