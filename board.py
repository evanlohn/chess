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

    def in_check(self, color, king_locs=[]):
        opposing_color = other(color)
        locs = set()
        for r_ind, row in enumerate(self.board_lst):
            for c_ind, piece in enumerate(row):
                if piece:
                    if (piece.color == opposing_color):
                        locs = locs.union(piece.get_moves((r_ind, c_ind), self, include_castling=False))
                    elif len(king_locs) == 0 and piece.name == 'K':
                        king_locs = [(r_ind, c_ind)]

        return any([(king_loc in locs) for king_loc in king_locs])     

    #TODO: add to this to support side lines/analysis
    def add_move(self, mv, main_line=True):
        if self.first_move is None:
            assert self.last_move is None
            assert main_line, 'start a new game smh'
            self.first_move = MoveTree(mv)
            self.last_move = self.first_move
        else:
            self.last_move.main_line = MoveTree(mv, parent=self.last_move)
            self.last_move = self.last_move.main_line

    def delete_move(self):
        if self.first_move is None:
            return
        elif self.first_move == self.last_move:
            self.first_move = None
            self.last_move = None
        else:
            self.last_move = self.last_move.parent
            self.last_move.main_line = None

    def peek_last_move(self):
        if not self.last_move:
            return None
        return self.last_move.move

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
    def get_moves(self, sq, board, include_castling=False):
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
        Pawn.name = cls_to_name[Pawn]
        self.name = Pawn.name
        self.has_moved = False
        self.dir = 1 if color == WHITE else -1
        self.img_id = 'p'

    def get_moves(self, sq, board, include_castling=False):
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

        #en passant: requires checking the last move made (bc otherwise undoing other moves is annoying)
        prev_move = board.peek_last_move()
        def en_passant_valid(lat):
            if is_valid(lat):
                l_p = board.get_piece(lat)

                #opposite colored pawn
                if l_p and l_p.color == other(self.color) and l_p.name == self.name:

                    #just moved, advanced 2 squares
                    if prev_move.piece == l_p and abs(prev_move.src[0] - prev_move.dst[0]) == 2:
                        return True
            return False

        if prev_move is not None:
            left = (row, col - 1)
            right = (row, col + 1)
            if en_passant_valid(left):
                ret.append(one_fl)
            elif en_passant_valid(right):
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

    def get_moves(self, sq, board, include_castling=False):
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

    def get_moves(self, sq, board, include_castling=False):
        sq_inds = sq_to_inds(sq)
        offs = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        ms = set()
        for off in offs:
            ms = ms.union(add_until_piece(sq_inds, off, board, other(self.color)))
        return ms

    def register_move(self):
        self.has_moved = True

    def get_props(self):
        return self.has_moved

    def restore_props(self, props):
        self.has_moved = props

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = cls_to_name[Bishop]
        self.img_id = 'b'

    def get_moves(self, sq, board, include_castling=False):
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

    def get_moves(self, sq, board, include_castling=False):
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
        King.name = cls_to_name[King]
        self.name = King.name
        self.img_id = 'k'

    def get_moves(self, sq, board, include_castling=False):
        sq_inds = sq_to_inds(sq)
        offs = [(-1, 0), (1, 0), (0, 1), (0, -1)] + [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        ms = set()
        for off in offs:
            new_sq = add_to(sq_inds, off)
            if is_valid(new_sq) and not board.occupied(new_sq, self.color):
                ms.add(new_sq)
        if include_castling and not self.has_moved:
            k_castle_sq = add_to(sq, (0, 3))
            k_rook = board.get_piece(k_castle_sq)
            if (k_rook and not k_rook.has_moved) and (not board.occupied(add_to(sq, (0, 1)))) and (not board.occupied(add_to(sq, (0, 2)))):
                if not board.in_check(self.color, king_locs=[sq, add_to(sq, (0, 1)), add_to(sq, (0, 2))]):
                    ms.add(add_to(sq, (0,2)))

            q_castle_sq = add_to(sq, (0, -4))
            q_rook = board.get_piece(q_castle_sq)
            if (q_rook and not q_rook.has_moved) and not any([board.occupied(add_to(sq, (0, -i))) for i in range(1,4)]):
                if not board.in_check(self.color, king_locs=[sq, add_to(sq, (0, -1)), add_to(sq, (0, -2))]):
                    ms.add(add_to(sq, (0,-2)))

        return ms

    def register_move(self):
        self.has_moved = True

    def get_props(self):
        return self.has_moved

    def restore_props(self, props):
        self.has_moved = props

name_to_cls = {'p': Pawn, 'k': Knight, 'r': Rook, 'b': Bishop, 'q': Queen, 'K': King}
cls_to_name = {name_to_cls[k]: k for k in name_to_cls}


class Move:

    # src and dest must be valid squares (within the bounds of the board)
    def __init__(self, src, dst, board):
        self.src = sq_to_inds(src)
        self.dst = sq_to_inds(dst)
        self.board = board
        self.piece = self.board.get_piece(src)
        
        self.castling = (self.piece.name == King.name) and (abs(self.src[1] - self.dst[1]) == 2)
        
        self.en_passant = (self.piece.name == Pawn.name) and (abs(self.src[0] - self.dst[0]) == 1) \
                and (abs(self.src[1] - self.dst[1]) == 1) and (self.board.get_piece(dst) is None)

    def is_valid(self):
        if self.castling:
            moves = self.piece.get_moves(self.src, self.board, include_castling=True)
            return self.dst in moves
        else:
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
        # TODO: handle en passant, castling
        if self.castling:
            if self.dst[1] > self.src[1]:
                rook_sq = add_to(self.src, (0, 3))
                new_rook_sq = add_to(self.src, (0,1))
            else:
                rook_sq = add_to(self.src, (0, -4))
                new_rook_sq = add_to(self.src, (0,-1))

            self.rook = self.board.get_piece(rook_sq)
            self.board.board_lst[new_rook_sq[0]][new_rook_sq[1]] = self.rook
            self.board.board_lst[rook_sq[0]][rook_sq[1]] = None
            self.taken_piece = None
            self.old_rook_props = self.rook.get_props()
            self.rook.register_move()

        elif self.en_passant:
            self.taken_loc = (self.src[0], self.dst[1])
            self.taken_piece = self.board.get_piece(self.taken_loc)
            self.board.board_lst[self.taken_loc[0]][self.taken_loc[1]] = None
        else:
            self.taken_piece = self.board.get_piece(self.dst)

        self.old_piece_props = self.piece.get_props()
        self.piece.register_move() # might want to pass in dst? # this changes piece props (potentially)
        new_row, new_col = self.dst
        row, col = self.src
        self.board.board_lst[new_row][new_col] = self.piece
        self.board.board_lst[row][col] = None

        self.board.add_move(self)

    def undo_move(self):
        if self.castling:
            if self.dst[1] > self.src[1]:
                rook_sq = add_to(self.src, (0, 3))
                new_rook_sq = add_to(self.src, (0,1))
                
            else:
                rook_sq = add_to(self.src, (0, -4))
                new_rook_sq = add_to(self.src, (0,-1))
                
            self.board.board_lst[new_rook_sq[0]][new_rook_sq[1]] = None
            self.board.board_lst[rook_sq[0]][rook_sq[1]] = self.rook
            self.rook.restore_props(self.old_rook_props)

        elif self.en_passant:
            take_r, take_c = self.taken_loc
            self.board.board_lst[take_r][take_c] = self.taken_piece
        else:
            new_row, new_col = self.dst
            self.board.board_lst[new_row][new_col] = self.taken_piece
        row, col = self.src
        self.taken_piece = None
        self.board.board_lst[row][col] = self.piece
        self.piece.restore_props(self.old_piece_props)

        self.board.delete_move()
