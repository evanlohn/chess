from board import Move

# meant to be run with the default board
def test_movement(board):
    #pawn movement
    m = Move('e2', 'e4', board)
    assert m.is_valid()
    m.make_move()
    assert Move('e4', 'e5', board).is_valid()
    m.undo_move()
    assert m.is_valid()

    m2 = Move('e2', 'e5', board)
    assert not m2.is_valid()

    m3 = Move('e3', 'e5', board)
    assert not m3.is_valid()

    assert not Move('e2', 'd3', board).is_valid()

    #knight movement
    m4 = Move('b1', 'c3', board)
    assert m4.is_valid()
    m4.make_move()
    
    m5 = Move('c3', 'e4', board)
    assert m5.is_valid()
    m5.make_move()
    m5.undo_move()
    assert m5.is_valid()
    m4.undo_move()


    Move('e2', 'e4', board).make_move()
    Move('d2', 'd4', board).make_move()

    #bishop movement
    m6 = Move('f1', 'c4', board)
    assert m6.is_valid()
    m6.make_move()
    m7 = Move('c4', 'f7', board) # capture (move onto opponent piece)
    assert m7.is_valid()
    assert not Move('c4', 'g8', board).is_valid() # bishops can't jump
    m7.make_move()
    m8 = Move('f7', 'b3', board)
    assert m8.is_valid()
    assert not Move('f7', 'a2', board).is_valid() # can't capture own piece
    m8.make_move()

    #rook movement
    Move('h2', 'h4', board).make_move()
    m = Move('h1', 'h3', board)
    assert m.is_valid()
    assert not Move('h1', 'h4', board).is_valid()
    m.make_move()

    assert not Move('h3', 'b3', board).is_valid() # can't capture own piece
    assert not Move('h3', 'a3', board).is_valid() # can't jump own piece
    m2 = Move('h3', 'c3', board)
    assert m2.is_valid()
    m2.make_move()
    m3 = Move('c3', 'c4', board)
    assert m3.is_valid()
    m3.make_move()
    m4 = Move('c4', 'c7', board)
    assert m4.is_valid()
    assert not Move('c4', 'c8', board).is_valid()
    m4.make_move()
    assert not Move('c7', 'd6', board).is_valid()

    # Queen Movement
    m5 = Move('d1', 'd3', board)
    assert m5.is_valid()
    m5.make_move()

    assert not Move('d3', 'c5', board).is_valid() # queen can't move like a knight!

    m6 = Move('d3', 'b5', board)
    assert m6.is_valid()
    m6.make_move()

    m7 = Move('b5', 'h5', board)
    assert m7.is_valid()
    m7.make_move()


    print('movement test passed')
