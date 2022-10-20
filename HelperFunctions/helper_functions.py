from settings import *
import pygame

#pos1 ans pos2 must be tuples: (x,y)
def manhattam_distance(pos1, pos2):   
    return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

def set_move(bp, i, j, black_king_pos, white_king_pos):    #bp = board_player
    move_piece(bp, (i, j), black_king_pos, white_king_pos)

def is_king_checked(board_piece):
    pos_of_opposite_color = position_of_black_pieces if board_piece.color == 'white' else position_of_white_pieces
    non_available_moves = {board_pieces[i[0], i[1]] for i in pos_of_opposite_color}
    for nam in non_available_moves:
        moves_to_check = nam.important_moves if nam.name == 'pawn' else nam.moves 
        if (board_piece.i, board_piece.j) in moves_to_check:
            board_piece.is_checked = True
            break
    else:
        board_piece.is_checked = False

def is_king_in_moves(board_piece, black_king_pos, white_king_pos):
    if board_piece.color == 'white':
        if black_king_pos in board_piece.moves:
            board_piece.is_king_in_moves = True
        else:
            board_piece.is_king_in_moves = False
    else:
        if white_king_pos in board_piece.moves:
            board_piece.is_king_in_moves = True
        else:
            board_piece.is_king_in_moves = False

def move_piece(board_piece, move, black_king_pos, white_king_pos):
    board_piece.i, board_piece.j = move[0], move[1] 
    board_piece.rect.topleft = (board_piece.i * 100 + 15, board_piece.j * 100 + 15)
    board_piece.find_moves(black_king_pos, white_king_pos)
    #το (5,3) πχ ειναι σωστο για το block_list, αν πατησουμε στο (6,3), ομως αν ειχαμε κανει αναθεση μονο με moves ή με αντιθετη σειρα, θα κατεληγε σε λαθος τετραγωνο->(500, 300), αρα πρεπει να το βαλουμε αναποδα

def draw(black_king_pos, white_king_pos):
    for row in block_list:
        for column in row:
            pygame.draw.rect(screen, column.color[-1], column.rect)
    if board_pieces[white_king_pos].is_checked:
        pygame.draw.rect(screen, pygame.Color('red'), block_list[white_king_pos[1]][white_king_pos[0]].rect)
    if board_pieces[black_king_pos].is_checked:
        pygame.draw.rect(screen, pygame.Color('red'), block_list[black_king_pos[1]][black_king_pos[0]].rect)
    for p in board_pieces:
        screen.blit(board_pieces[p].image, (board_pieces[p].i * 100 + 15, board_pieces[p].j * 100 + 15))
        board_pieces[p].rect = board_pieces[p].image.get_rect()
        board_pieces[p].rect.topleft = (board_pieces[p].i * 100 + 15, board_pieces[p].j * 100 + 15)

def check_for_other_piece(board_piece, num):
    pos_to_ckeck = position_of_white_pieces if board_piece.color == 'white' else position_of_black_pieces
    pieces_to_check = {board_pieces[p] for p in pos_to_ckeck if board_pieces[p].name in ('lbishop', 'rbishop', 'rrook', 'lrook', 'queen') and board_pieces[p] != board_piece}
    for piece in pieces_to_check:
        if piece.i == board_piece.i and num == 1:
            return True
        elif piece.j == board_piece.j and num == 2:
            return True
        elif is_in_same_diagonal((board_piece.i, board_piece.j), (piece.i, piece.j)) and num == 3:
            return True
    return False

def remove_moves(board_piece, black_king_pos, white_king_pos):
    '''
    remove moves that leave the king checked
    '''
    pos_to_ckeck = position_of_white_pieces if board_piece.color == 'black' else position_of_black_pieces
    pieces_to_check = {board_pieces[p] for p in pos_to_ckeck if board_pieces[p].name in ('lbishop', 'rbishop', 'rrook', 'lrook', 'queen')}
    king_to_check = black_king_pos if board_piece.color == 'black' else white_king_pos
    for piece in pieces_to_check:
        if piece.name == 'queen':
            if piece.i == board_piece.i and board_piece.i == king_to_check[0] and (board_piece.i, board_piece.j) in piece.moves and not check_for_other_piece(board_piece, 1):
                for m in list(board_piece.moves):
                    if m[0] != piece.i:
                        board_piece.moves.remove(m)
            elif piece.j == board_piece.j and board_piece.j == king_to_check[1] and (board_piece.i, board_piece.j) in piece.moves and not check_for_other_piece(board_piece, 2):
                for m in list(board_piece.moves):
                    if m[1] != piece.j:
                        board_piece.moves.remove(m)
            elif is_in_same_diagonal((board_piece.i, board_piece.j), (piece.i, piece.j)) and (board_piece.i, board_piece.j) in piece.moves:
                if is_in_same_diagonal(king_to_check, (piece.i, piece.j)) and not check_for_other_piece(board_piece, 3):
                    for m in list(board_piece.moves):
                        if not is_in_same_diagonal(m, (piece.i, piece.j)) or (m[0] == board_piece.i or m[1] == board_piece.j):
                            board_piece.moves.remove(m)

        elif (piece.name == 'lbishop' or piece.name == 'rbishop') and (board_piece.i, board_piece.j) in piece.moves:
            if is_in_same_diagonal((board_piece.i, board_piece.j), (piece.i, piece.j)) and not check_for_other_piece(board_piece, 3):
                if is_in_same_diagonal(king_to_check, (piece.i, piece.j)):
                    for m in list(board_piece.moves):
                        if not is_in_same_diagonal(m, (piece.i, piece.j)):
                            board_piece.moves.remove(m)

        elif piece.name == 'lrook' or piece.name == 'rrook':
            if (piece.i == board_piece.i) and (board_piece.i == king_to_check[0]) and ((board_piece.i, board_piece.j) in piece.moves) and not check_for_other_piece(board_piece, 1):
                for m in list(board_piece.moves):
                    if m[0] != piece.i:
                        board_piece.moves.remove(m)
            elif (piece.j == board_piece.j) and (board_piece.j == king_to_check[1]) and ((board_piece.i, board_piece.j) in piece.moves) and not check_for_other_piece(board_piece, 2):
                for m in list(board_piece.moves):
                    if m[1] != piece.j:
                        board_piece.moves.remove(m)

def remove_moves_if_king_is_checked(board_piece, black_king_pos, white_king_pos):
    pos_to_check = position_of_white_pieces if board_piece.color == 'black' else position_of_black_pieces
    pieces_to_check = {board_pieces[p] for p in pos_to_check}
    king_to_check = black_king_pos if board_piece.color == 'black' else white_king_pos
    for piece in pieces_to_check:
        if piece.name == 'queen':
            min_i, min_j = min(piece.i, king_to_check[0]), min(piece.j, king_to_check[1])
            max_i, max_j = max(piece.i, king_to_check[0]), max(piece.j, king_to_check[1])
            if piece.i == king_to_check[0] and piece.is_king_in_moves:
                for m in list(board_piece.moves):
                    if m[0] != piece.i or (m[1] < min_j or m[1] > max_j):
                        if m != (piece.i, piece.j):
                            board_piece.moves.remove(m)
            elif piece.j == king_to_check[1] and piece.is_king_in_moves:
                for m in list(board_piece.moves):
                    if m[1] != piece.j or (m[0] < min_i or m[0] > max_i):
                        if m != (piece.i, piece.j):
                            board_piece.moves.remove(m)
        
            elif is_in_same_diagonal(king_to_check, (piece.i, piece.j)) and piece.is_king_in_moves:
                for m in list(board_piece.moves):
                    if not is_in_same_diagonal(m, (piece.i, piece.j)) or not is_in_same_diagonal(m, king_to_check) or (m[0] < min_i or m[0] > max_i) or (m[1] < min_j or m[1] > max_j):
                        board_piece.moves.remove(m)

        elif (piece.name == 'lbishop' or piece.name == 'rbishop') and piece.is_king_in_moves:
            min_i, min_j = min(piece.i, king_to_check[0]), min(piece.j, king_to_check[1])
            max_i, max_j = max(piece.i, king_to_check[0]), max(piece.j, king_to_check[1])
            if is_in_same_diagonal(king_to_check, (piece.i, piece.j)):
                for m in list(board_piece.moves):
                    if not is_in_same_diagonal(m, (piece.i, piece.j)) or not is_in_same_diagonal(m, king_to_check) or (m[0] < min_i or m[0] > max_i) or (m[1] < min_j or m[1] > max_j):
                        board_piece.moves.remove(m)

        elif piece.name == 'lrook' or piece.name == 'rrook':
            if board_piece.i == king_to_check[0] and piece.is_king_in_moves:
                for m in list(board_piece.moves):
                    min_i, min_j = min(piece.i, king_to_check[0]), min(piece.j, king_to_check[1])
                    max_i, max_j = max(piece.i, king_to_check[0]), max(piece.j, king_to_check[1])
                    if m[0] != piece.i or (m[1] < min_j or m[1] > max_j):
                        board_piece.moves.remove(m)
            elif board_piece.j == king_to_check[1] and piece.is_king_in_moves:
                for m in list(board_piece.moves):
                    min_i, min_j = min(piece.i, king_to_check[0]), min(piece.j, king_to_check[1])
                    max_i, max_j = max(piece.i, king_to_check[0]), max(piece.j, king_to_check[1])
                    if m[1] != piece.j or (m[0] < min_i or m[0] > max_i):
                        board_piece.moves.remove(m)

        elif piece.name == 'lknight' or piece.name == 'rknight':
            for m in list(board_piece.moves):
                if m != (piece.i, piece.j) and piece.is_king_in_moves:
                    board_piece.moves.remove(m)
                    
        elif piece.name == 'pawn':
            for m in list(board_piece.moves):
                if m != (piece.i, piece.j) and piece.is_king_in_moves:
                    board_piece.moves.remove(m)

def find_pieces_if_king_is_checked(king, black_king_pos, white_king_pos):
    pos_to_check = position_of_black_pieces if king.color == 'black' else position_of_white_pieces
    pieces_to_check = {board_pieces[p] for p in pos_to_check if board_pieces[p].name != 'king'}
    
    for piece in pieces_to_check:
        remove_moves_if_king_is_checked(piece, black_king_pos, white_king_pos)

def num_of_pieces_with_moves(king):
    pos_of_pieces = position_of_black_pieces if king.color == 'black' else position_of_white_pieces
    pieces = {board_pieces[pos] for pos in pos_of_pieces}
    count = 0
    for p in pieces:
        if p.moves:
            count += 1
    return count

def available_pieces(num_of_move):
    if num_of_move % 2 == 0:
        return {pos:board_pieces[pos] for pos in position_of_white_pieces}
    else:
        return {pos:board_pieces[pos] for pos in position_of_black_pieces}

def is_in_same_diagonal(p1, p2):
    man_dist = manhattam_distance(p1, p2)//2
    if man_dist == abs(p1[0] - p2[0]) and man_dist == abs(p1[1] - p2[1]):
        return True
    return False

def print_available_moves(board_piece):
    valid_moves = []
    opposite_color_pos = position_of_black_pieces if board_piece.color == 'white' else position_of_white_pieces
    for i in board_piece.moves:
        color = pygame.Color('green')
        valid_moves.append(block_list[i[1]][i[0]])
        if (i[0], i[1]) in opposite_color_pos:
            color = pygame.Color('red')
            #print(board_pieces.keys())
            if board_pieces[(i[0], i[1])].name == 'king' and board_pieces[(i[0], i[1])].color != board_piece.color:
                valid_moves.pop()
                continue
        pygame.draw.circle(screen, color, block_list[i[1]][i[0]].rect.center, 10)
    return valid_moves