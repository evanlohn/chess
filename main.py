import tkinter as tk
import argparse
from board import all_ranks, all_files, WHITE, BLACK, Board, Move
from tests import test_movement

def parse_config(config_pth):
    pass



#NOTE: the keys in this dicctionary MUST match with the keys in name_to_cls in board.py
default_chess_positions = {WHITE: {'b': ['c1', 'f1'], 'k': ['b1', 'g1'], 'r': ['a1', 'h1'], 'q': ['d1'], 'K': ['e1']},
                            BLACK: {'b': ['c8', 'f8'], 'k': ['b8', 'g8'], 'r': ['a8', 'h8'], 'q': ['d8'], 'K': ['e8']}}
default_chess_positions[WHITE]['p'] = [f + '2' for f in all_files]
default_chess_positions[BLACK]['p'] = [f + '7' for f in all_files]


def parse_missing(white, black):
    dct = {WHITE: set(), BLACK: set()}

    color_to_rank = {WHITE: (1,2), BLACK: (8, 7)}
    

    def add_to_miss(ms, miss, ranks):

        rank, pawn_rank = ranks
        def get_piece_loc(piece, queen_file, king_file):
            default_pos = queen_file + str(rank)
            if (len(piece) > 1 and piece[1].lower() == 'k') or (default_pos in miss):
                return king_file + str(rank)
            return default_pos
            
        pieces = ms.split(',')
        for piece in pieces:
            if not piece:
                continue
            p_char = piece[0].lower()
            if p_char == 'r' or p_char == 'c': # rook or castle
                miss.add(get_piece_loc(piece, 'a', 'h'))
            elif p_char == 'k' or p_char =='h': # knight or horse
                miss.add(get_piece_loc(piece, 'b', 'g'))
            elif p_char == 'b':                 #bishop
                miss.add(get_piece_loc(piece, 'c', 'f'))
            elif p_char == 'q':                 # queen
                miss.add('d' + str(rank))
            elif p_char == 'p':                 # pawn
                assert len(piece) == 2 and piece[1] in all_files, 'pawn spec {} invalid'.format(piece)
                miss.add(piece[1] + str(pawn_rank))
            else:
                print('unrecognized piece spec: {}'.format(piece))

    add_to_miss(white, dct[WHITE], color_to_rank[WHITE])
    add_to_miss(black, dct[BLACK], color_to_rank[BLACK])
    return dct
    
def get_config(all_missing_pieces):
    new_config = {WHITE: {}, BLACK: {}}
    def copy_with_missing(color):
        defaults = default_chess_positions[color]
        new_dct = new_config[color]
        missing_pieces = all_missing_pieces[color]
        for piece in defaults:
            new_dct[piece] = [loc for loc in defaults[piece] if loc not in missing_pieces]

    copy_with_missing(WHITE)
    copy_with_missing(BLACK)
    return new_config
    
def setup_board(config):
    #print(config)
    #print(default_chess_positions)
    board = Board(config)
    return board
    pass


def main():
    parser = argparse.ArgumentParser(description='Process chess configuration')
    parser.add_argument('--white', default='', help='the pieces white is missing')
    parser.add_argument('--black', default='', help='the pieces black is missing')
    parser.add_argument('--config', default='', help='the config file (for complicated board)')
    args = parser.parse_args()

    if args.config:
        b_config = parse_config(args.config)
    else:
        all_missing = parse_missing(args.white, args.black)
        b_config = get_config(all_missing)

    board = setup_board(b_config)
    test_movement(board)




if __name__ == '__main__':
    main()
