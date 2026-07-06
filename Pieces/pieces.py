from helper_functions import *
import copy

class piece():
    def __init__(self, image, color, name, i, j):
        self.i, self.j = i, j
        self.image = image
        self.color = color
        self.name = name
        self.moves = set()
        self.is_king_in_moves = False
        self.can_promote = False
        self.moved = False
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        for key, value in self.__dict__.items():
            if key == "image":
                setattr(new, key, value)      # reuse the same Surface
            else:
                setattr(new, key, copy.deepcopy(value, memo))

        return new
    
    # dummy function, useful to maintain readeability in the code
    def promote(self):
        pass
    
    def check_is_king_in_moves(self, board_piece, black_king_pos, white_king_pos):
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
    
    # handle_move makes the move and stores the necessary data, while making
    # changes to important data structures (like the two sets containing the 
    # positions of each color's pieces)
    # bpc = board_pieces copy, scp = current piece,
    # pbp = positions of black pieces, pwp = position of white pieces
    
    def handle_move(self, bpc, scp, pbp, pwp, move):
        position_of_same_color_pieces = pbp if bpc[scp].color == 'black' else pwp
        position_of_opposite_color_pieces = pbp if bpc[scp].color == 'white' else pwp
        position_of_same_color_pieces.remove((bpc[scp].i, bpc[scp].j))
        set_move(bpc[scp], *move, black_king_pos, white_king_pos, pbp, pwp, bpc)
    
        board_pieces_index = move
        
        if board_pieces_index in position_of_opposite_color_pieces:
            position_of_opposite_color_pieces.remove(board_pieces_index)
        position_of_same_color_pieces.add(move)
        bpc[board_pieces_index] = bpc[scp]
        del bpc[scp]
    
    def remove_reveal_king_moves(self, count, board_pieces, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces):
        # the king's moves should not get altered , ONLY the rest of the pieces determine
        # whether a move reveals the king and thus should be deleted, as it is not valid
        if self.name == "king": return
        
        color = "black" if (count % 2 != 0) else "white"
        
        board_pieces_c = copy.deepcopy(board_pieces)
        scp = self.i, self.j
        
        remove_list = []

        for move in copy.copy(self.moves):
            bpc = copy.deepcopy(board_pieces_c)        # bcp = board_pieces copy
            pbp = copy.copy(position_of_black_pieces)
            pwp = copy.copy(position_of_white_pieces)
            same_colored_king = [key for key in bpc if (bpc[key].name == "king") and (bpc[key].color == color)][0]
            same_colored_king = bpc[same_colored_king]
            
            self.handle_move(bpc, scp, pbp, pwp, move)
            
            for board_piece in bpc:
                bpc[board_piece].find_moves(black_king_pos, white_king_pos, pbp, pwp, bpc)
            
                self.check_is_king_in_moves(bpc[board_piece], black_king_pos, white_king_pos)
                if bpc[board_piece].is_king_in_moves and (bpc[board_piece].color != color):
                    opposite_king_pos = black_king_pos if (bpc[board_piece].color == "white") else white_king_pos
                    if move != opposite_king_pos:
                        remove_list.append((scp, move))
                
        for scp, move in remove_list:
            board_pieces[scp].moves.discard(move)

class pawn(piece):
    def __init__(self, i, j, image, color, name, to_place_dict):            # i, j denote the position in the 2d list of blocks/rects
        super().__init__(image, color, name, i, j)
        self.optional_moves = set()
        self.protected = set()
        self.important_moves = set()
        self.rect = None
        self.to_place = to_place_dict
        self.en_passant_turn_count = 0
        self.en_passant_move = None

    def promote(self):
        if (self.j == 0) or (self.j == 7):
            self.can_promote = True
    
    def capture_en_passant(self, difx, dify, position_of_black_pieces, position_of_white_pieces, move, count):
        pieces_to_check = position_of_black_pieces if (self.color == "black") else position_of_white_pieces
        #print(difx, dify, move in pieces_to_check, count, self.en_passant_turn_count)
        #return (difx == 1) and (dify == 1) and (move not in pieces_to_check) and (abs(count-self.en_passant_turn_count) == 1)
        return (difx == 1) and (dify == 1) and (abs(count-self.en_passant_turn_count) == 1)
        
    def handle_en_passant(self, position_of_black_pieces, position_of_white_pieces, board_pieces, move, dif_y, count):
        # a list of tuples: the first part of each tuple is the position of the pawn eligible to perform
        # the en passant move, the second is the position it will end up if the move is made and the last
        # is the position of the pawn captured
        return_moves = []
        
        if dif_y == 2:
            pieces_to_use = position_of_black_pieces if (self.color == "white") else position_of_white_pieces
            pawns_to_check = {pos for pos in pieces_to_use if board_pieces[pos].name == "pawn"}
            
            # if the current pawn moving two squares from its initial position is black, then
            # the y_offset for the opposite color pawns must be -1, because they are moving from
            # y = 6 (max is 7, because the board is 8x8, thus 0-7 indexed for both the x and y
            # axis) to y = 0. For the black pieces the movement is the opposite, moving from
            # y = 1 to y = 7. The y_offset must be opposite to the relative of the movement of the
            # enemy pawn. This function acts as a trigger for the neighbouring opposite pawn,
            # enabling them to perform the en passant move
            y_offset = -1 if (self.color == "black") else 1
            
            if move[0] - 1 > 0:
                if (move[0]-1, move[1]) in pawns_to_check:
                    return_moves.append(((move[0]-1, move[1]), (move[0], move[1]+y_offset), (move)))
            if move[0] + 1 < 8:
                if (move[0]+1, move[1]) in pawns_to_check:
                    return_moves.append(((move[0]+1, move[1]), (move[0], move[1]+y_offset), (move)))
                    
        #if (self.en_passant_turn_count == 0) and (len(return_moves) > 0):
        #    self.en_passant_turn_count = count
                    
        return return_moves

    def find_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces):
        self.moves.clear()
        self.protected.clear()
        self.important_moves.clear()
        op_king_pos = black_king_pos if self.color == 'white' else white_king_pos

        if self.color == 'black':
            if self.j + 1 <= 7:
                if (self.i, self.j+1) not in position_of_white_pieces and ((self.i, self.j+1) not in position_of_black_pieces):
                    self.moves.add((self.i, self.j+1))
                    if self.j == 1 and ((self.i, self.j+2) not in position_of_white_pieces) and ((self.i, self.j+2) not in position_of_black_pieces):
                        self.moves.add((self.i, self.j+2))
                        self.optional_moves.add((self.i, self.j+2))
                
                if self.i + 1 <= 7 and (self.i+1, self.j+1) not in position_of_black_pieces:
                    if (self.i+1, self.j+1) in position_of_white_pieces:
                        self.moves.add((self.i+1, self.j+1))
                    self.important_moves.add((self.i+1, self.j+1))
                
                if self.i - 1 >= 0 and (self.i-1, self.j+1) not in position_of_black_pieces:
                    if (self.i-1, self.j+1) in position_of_white_pieces:
                        self.moves.add((self.i-1, self.j+1))
                    self.important_moves.add((self.i-1, self.j+1))
               
            if self.i + 1 <= 7 and self.j+1 <= 7 and (self.i+1, self.j+1) in position_of_black_pieces:
                    self.protected.add((self.i+1, self.j+1))
            if self.i - 1 >= 0 and self.j+1 <= 7 and (self.i-1, self.j+1) in position_of_black_pieces:
                    self.protected.add((self.i-1, self.j+1))
        elif self.color == 'white':
            if self.j - 1 >= 0:
                if (self.i, self.j-1) not in position_of_black_pieces and ((self.i, self.j-1) not in position_of_white_pieces):
                    self.moves.add((self.i, self.j-1))
                    if self.j == 6 and ((self.i, self.j-2) not in position_of_black_pieces) and ((self.i, self.j-2) not in position_of_white_pieces):
                        self.moves.add((self.i, self.j-2))
                        self.optional_moves.add((self.i, self.j-2))
                
                if self.i + 1 <= 7 and (self.i+1, self.j-1) not in position_of_white_pieces:
                    if (self.i+1, self.j-1) in position_of_black_pieces:
                        self.moves.add((self.i+1, self.j-1))
                    self.important_moves.add((self.i+1, self.j-1))
               
                if self.i - 1 >= 0 and (self.i-1, self.j-1) not in position_of_white_pieces:
                    if (self.i-1, self.j-1) in position_of_black_pieces:
                        self.moves.add((self.i-1, self.j-1))
                    self.important_moves.add((self.i-1, self.j-1))
                
            if self.i + 1 <= 7 and self.j-1 >= 0 and (self.i+1, self.j-1) in position_of_white_pieces:
                    self.protected.add((self.i+1, self.j-1))
            if self.i - 1 >= 0 and self.j-1 >= 0 and (self.i-1, self.j-1) in position_of_white_pieces:
                    self.protected.add((self.i-1, self.j-1))
        
        if op_king_pos in self.moves:
            self.is_king_in_moves = True
        else:
            self.is_king_in_moves = False
        #remove_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)

class king(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        self.is_checked = False
        self.done_castling = False
        self.step_counter = 0   # to track the number of moves, it is vital to the castling calculation, any step
                                # counter larger than 1, results in the castling being classified as invalid (must 
                                # be the first king's move)
        self.castling = {
            "white" : {
                "left_rook_pos" : (7, 7),
                "right_rook_pos" : (0, 7),
                "left_castling_pos" : (6, 7),
                "right_castling_pos" : (2, 7),
                "left_pos_to_check" : [(4, 7), (5, 7), (6, 7)],
                "right_pos_to_check" : [(4, 7), (3, 7), (2, 7)],
                "left_rook_castling_pos" : (5, 7),
                "right_rook_castling_pos" : (3, 7)
            },
            "black" : {
                "left_rook_pos" : (7, 0),
                "right_rook_pos" : (0, 0),
                "left_castling_pos" : (6, 0),
                "right_castling_pos" : (2, 0),
                "left_pos_to_check" : [(4, 0), (5, 0), (6, 0)],
                "right_pos_to_check" : [(4, 0), (3, 0), (2, 0)],
                "left_rook_castling_pos" : (5, 0),
                "right_rook_castling_pos" : (3, 0)
            }
        }
        
    def change_rook_castling(self, board_pieces, position_of_black_pieces, position_of_white_pieces, move):   
        
        # perform the castling move for the respective rook, only if the move (king move) is either 
        # the left or the right king castling move
        
        castling = self.castling[self.color]
        
        if (move == castling["left_castling_pos"]) and (self.step_counter == 1):  # and (move in board_pieces) ensures the piece hasn't been captured yet
            self.handle_move(board_pieces, castling['left_rook_pos'], position_of_black_pieces, position_of_white_pieces, castling["left_rook_castling_pos"])
        if (move == castling["right_castling_pos"]) and (self.step_counter == 1):
            self.handle_move(board_pieces, castling['right_rook_pos'], position_of_black_pieces, position_of_white_pieces, castling["right_rook_castling_pos"])

    def remove_invalid_castling_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces):
        pos_to_avoid = position_of_black_pieces if self.color == 'black' else position_of_white_pieces
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        non_available_moves = {board_pieces[i[0], i[1]] for i in pos_to_stop if board_pieces[i[0], i[1]].name != 'king'}
        
        if not self.moved:
            # get the castling dict according to the king's color
            castling = self.castling[self.color]
            
            # a list containig two individual lists that hold the positions we have to check
            # for the left and right castling respectively. A castling move is only valid if
            # the king doesn't leave, cross over or end up in a square attacked by enemy pieces.
            # Neither the king nor the respective rook must have moved and the squares between
            # them are empty
            castling_pos = [castling["left_pos_to_check"], castling["right_pos_to_check"]]
            
            left_castling_pos, right_castling_pos = castling_pos
            
            check_left_empty = all([(pos not in pos_to_stop) and (pos not in pos_to_avoid) for pos in left_castling_pos if (pos != (self.i, self.j))])
            check_right_empty = all([(pos not in pos_to_stop) and (pos not in pos_to_avoid) for pos in right_castling_pos if (pos != (self.i, self.j))])
            
            check_left_not_attacked = all([all([(pos not in (bp.moves if (bp.name != 'pawn') else bp.important_moves)) 
                                           for pos in left_castling_pos]) for bp in non_available_moves])
            check_right_not_attacked = all([all([(pos not in (bp.moves if (bp.name != 'pawn') else bp.important_moves)) 
                                           for pos in right_castling_pos]) for bp in non_available_moves])
            
            left_castling_valid = check_left_empty and check_left_not_attacked
            right_castling_valid = check_right_empty and check_right_not_attacked 
            
            if self.is_checked:
                self.moves.discard(castling["left_castling_pos"])
                self.moves.discard(castling["right_castling_pos"])
                        
            if (not left_castling_valid):
                self.moves.discard(castling["left_castling_pos"])
            
            if (not right_castling_valid):
                self.moves.discard(castling["right_castling_pos"])

    def find_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = position_of_black_pieces if self.color == 'black' else position_of_white_pieces
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        non_available_moves = {board_pieces[i[0], i[1]] for i in pos_to_stop if board_pieces[i[0], i[1]].name != 'king'}
        
         # handle castling
        if not self.moved:
            # get the castling dict according to the king's color
            castling = self.castling[self.color]
            
            left_rook = board_pieces.get(castling["left_rook_pos"])
            right_rook = board_pieces.get(castling["right_rook_pos"])
            # a list containig two individual lists that hold the positions we have to check
            # for the left and right castling respectively. A castling move is only valid if
            # the king doesn't leave, cross over or end up in a square attacked by enemy pieces.
            # Neither the king nor the respective rook must have moved and the squares between
            # them are empty
            castling_pos = [castling["left_pos_to_check"], castling["right_pos_to_check"]]
            
            if (left_rook is not None) and (left_rook.name == "lrook") and (not left_rook.moved):
                self.moves.add(castling["left_castling_pos"])
            if (right_rook is not None) and (right_rook.name == "rrook") and (not right_rook.moved):
                self.moves.add(castling["right_castling_pos"])
            
            self.remove_invalid_castling_moves(black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)
        
        if self.i + 1 <= 7 and ((self.i+1, self.j) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i+1, self.j) in moves:
                    break
            else:
                self.moves.add((self.i+1, self.j))
        elif self.i + 1 <= 7 and ((self.i+1, self.j) in pos_to_avoid):
            self.protected.add((self.i+1, self.j))
            
        if self.j + 1 <= 7 and self.i + 1 <= 7 and ((self.i+1, self.j+1) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i+1, self.j+1) in moves:
                    break
            else:
                self.moves.add((self.i+1, self.j+1))
            
        elif self.j + 1 <= 7 and self.i + 1 <= 7 and ((self.i+1, self.j+1) in pos_to_avoid):
            self.protected.add((self.i+1, self.j+1))
        if self.j - 1 >= 0 and self.i + 1 <= 7 and ((self.i+1, self.j-1) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i+1, self.j-1) in moves:
                    break
            else:
                self.moves.add((self.i+1, self.j-1))
                
        elif self.j - 1 >= 0 and self.i + 1 <= 7 and ((self.i+1, self.j-1) in pos_to_avoid):
            self.protected.add((self.i+1, self.j-1))
        if self.i - 1 >= 0 and ((self.i-1, self.j) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i-1, self.j) in moves:
                    break
            else:
                self.moves.add((self.i-1, self.j))
            
        elif self.i - 1 >= 0 and ((self.i-1, self.j) in pos_to_avoid):
            self.protected.add((self.i-1, self.j))
        if self.j + 1 <= 7 and self.i - 1 >= 0 and ((self.i-1, self.j+1) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i-1, self.j+1) in moves:
                    break
            else:
                self.moves.add((self.i-1, self.j+1))
                
        elif self.j + 1 <= 7 and self.i - 1 >= 0 and ((self.i-1, self.j+1) in pos_to_avoid):
            self.protected.add((self.i-1, self.j+1))
        if self.j - 1 >= 0 and self.i - 1 >= 0 and ((self.i-1, self.j-1) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i-1, self.j-1) in moves:
                    break
            else:
                self.moves.add((self.i-1, self.j-1))
                
        elif self.j - 1 >= 0 and self.i - 1 >= 0 and ((self.i-1, self.j-1) in pos_to_avoid):
            self.protected.add((self.i-1, self.j-1))
        if self.j + 1 <= 7 and ((self.i, self.j+1) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i, self.j+1) in moves:
                    break
            else:
                self.moves.add((self.i, self.j+1))
           
        elif self.j + 1 <= 7 and ((self.i, self.j+1) in pos_to_avoid):
            self.protected.add((self.i, self.j+1))
        if self.j - 1 >= 0 and ((self.i, self.j-1) not in pos_to_avoid):
            for nam in non_available_moves:
                moves = nam.moves if nam.name != 'pawn' else nam.important_moves
                if (self.i, self.j-1) in moves:
                    break
            else:
                self.moves.add((self.i, self.j-1))
           
        elif self.j - 1 >= 0 and ((self.i, self.j-1) in pos_to_avoid):
            self.protected.add((self.i, self.j-1))


    def update_moves(self, position_of_black_pieces, position_of_white_pieces, board_pieces):
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        opposite_color_pieces = {board_pieces[i[0], i[1]] for i in pos_to_stop}
       
        self.remove_invalid_castling_moves(black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)
       
        for opposite_color_piece in opposite_color_pieces:
            if opposite_color_piece.name == 'queen' and opposite_color_piece.is_king_in_moves and self.is_checked:
                if self.i == opposite_color_piece.i:
                    if self.is_checked and (self.i, self.j-1) in self.moves and (self.i, self.j-1) != (opposite_color_piece.i, opposite_color_piece.j):
                        self.moves.remove((self.i, self.j-1))
                    if self.is_checked and (self.i, self.j+1) in self.moves and (self.i, self.j+1) != (opposite_color_piece.i, opposite_color_piece.j):
                        self.moves.remove((self.i, self.j+1))
                if self.j == opposite_color_piece.j and opposite_color_piece.is_king_in_moves:
                    if self.is_checked and (self.i-1, self.j) in self.moves and (self.i-1, self.j) != (opposite_color_piece.i, opposite_color_piece.j):
                        self.moves.remove((self.i-1, self.j))
                    if self.is_checked and (self.i+1, self.j) in self.moves and (self.i+1, self.j) != (opposite_color_piece.i, opposite_color_piece.j):
                        self.moves.remove((self.i+1, self.j))

                man_dist = manhattam_distance((self.i, self.j), (opposite_color_piece.i, opposite_color_piece.j))//2

                if (man_dist == abs(self.i-opposite_color_piece.i)) and (man_dist == abs(self.j-opposite_color_piece.j)):
                    man_dist1 = manhattam_distance((self.i-1, self.j-1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    man_dist2 = manhattam_distance((self.i-1, self.j+1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    man_dist3 = manhattam_distance((self.i+1, self.j-1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    man_dist4 = manhattam_distance((self.i+1, self.j+1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    if (self.i-1, self.j-1) in self.moves and (man_dist1 == abs(self.i-1-opposite_color_piece.i)) and (man_dist1 == abs(self.j-1-opposite_color_piece.j)):
                        self.moves.remove((self.i-1, self.j-1))
                    if (self.i-1, self.j+1) in self.moves and (man_dist2 == abs(self.i-1-opposite_color_piece.i)) and (man_dist2 == abs(self.j+1-opposite_color_piece.j)):
                        self.moves.remove((self.i-1, self.j+1))
                    if (self.i+1, self.j-1) in self.moves and (man_dist3 == abs(self.i+1-opposite_color_piece.i)) and (man_dist3 == abs(self.j-1-opposite_color_piece.j)):
                        self.moves.remove((self.i+1, self.j-1))
                    if (self.i+1, self.j+1) in self.moves and (man_dist4 == abs(self.i+1-opposite_color_piece.i)) and (man_dist4 == abs(self.j+1-opposite_color_piece.j)):
                        self.moves.remove((self.i+1, self.j+1))
                    if (man_dist == 1):
                        self.moves.add((opposite_color_piece.i, opposite_color_piece.j))
                
                if self.is_checked and (manhattam_distance((self.i, self.j), (opposite_color_piece.i, opposite_color_piece.j))//2 == 0):
                    if (self.i-1, self.j-1) in self.moves and ((self.i-1)==opposite_color_piece.i or (self.j-1)==opposite_color_piece.j):
                        self.moves.remove((self.i-1, self.j-1))
                    if (self.i-1, self.j+1) in self.moves and ((self.i-1)==opposite_color_piece.i or (self.j+1)==opposite_color_piece.j):
                        self.moves.remove((self.i-1, self.j+1))
                    if (self.i+1, self.j-1) in self.moves and ((self.i+1)==opposite_color_piece.i or (self.j-1)==opposite_color_piece.j):
                        self.moves.remove((self.i+1, self.j-1))
                    if (self.i+1, self.j+1) in self.moves and ((self.i+1)==opposite_color_piece.i or (self.j+1)==opposite_color_piece.j):
                        self.moves.remove((self.i+1, self.j+1))
                
            elif (opposite_color_piece.name == 'rbishop' or opposite_color_piece.name == 'lbishop') and opposite_color_piece.is_king_in_moves and self.is_checked:
                man_dist = manhattam_distance((self.i, self.j), (opposite_color_piece.i, opposite_color_piece.j))//2
                if (man_dist == abs(self.i-opposite_color_piece.i)) and (man_dist == abs(self.j-opposite_color_piece.j)) and self.is_checked:
                    man_dist1 = manhattam_distance((self.i-1, self.j-1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    man_dist2 = manhattam_distance((self.i-1, self.j+1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    man_dist3 = manhattam_distance((self.i+1, self.j-1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    man_dist4 = manhattam_distance((self.i+1, self.j+1), (opposite_color_piece.i, opposite_color_piece.j))//2
                    if (self.i-1, self.j-1) in self.moves and (man_dist1 == abs(self.i-1-opposite_color_piece.i)) and (man_dist1 == abs(self.j-1-opposite_color_piece.j)):
                        self.moves.remove((self.i-1, self.j-1))
                    if (self.i-1, self.j+1) in self.moves and (man_dist2 == abs(self.i-1-opposite_color_piece.i)) and (man_dist2 == abs(self.j+1-opposite_color_piece.j)):
                        self.moves.remove((self.i-1, self.j+1))
                    if (self.i+1, self.j-1) in self.moves and (man_dist3 == abs(self.i+1-opposite_color_piece.i)) and (man_dist3 == abs(self.j-1-opposite_color_piece.j)):
                        self.moves.remove((self.i+1, self.j-1))
                    if (self.i+1, self.j+1) in self.moves and (man_dist4 == abs(self.i+1-opposite_color_piece.i)) and (man_dist4 == abs(self.j+1-opposite_color_piece.j)):
                        self.moves.remove((self.i+1, self.j+1))
                if (man_dist <= 1):
                    self.moves.add((opposite_color_piece.i, opposite_color_piece.j))
                
            elif opposite_color_piece.name == 'rrook' or opposite_color_piece.name == 'lrook':
                if self.is_checked and opposite_color_piece.is_king_in_moves:
                    directions = [(-1, -1), (0, -1), (1, -1), (1, 0), (-1, 0), (-1, 1), (0, 1), (1, 1)]
                    man_dist = manhattam_distance((opposite_color_piece.i, opposite_color_piece.j), (self.i, self.j))
                    for direction in directions:
                        move = (direction[0] + self.i, direction[1] + self.j)
                        if self.is_checked and (move[0] == opposite_color_piece.i or move[1] == opposite_color_piece.j):
                            if move in self.moves:
                                if move == (opposite_color_piece.i, opposite_color_piece.j) and man_dist == 1:
                                    continue
                                self.moves.remove(move)

            elif opposite_color_piece.name == 'king':
                directions = [(-1, -1), (0, -1), (1, -1), (1, 0), (-1, 0), (-1, 1), (0, 1), (1, 1)]
                for direction in directions:
                    man_dist = manhattam_distance((opposite_color_piece.i, opposite_color_piece.j), (self.i+direction[0], self.j+direction[1]))

                    if (self.i+direction[0] == opposite_color_piece.i or self.j+direction[1] == opposite_color_piece.j) and man_dist == 1:
                        if (self.i+direction[0], self.j+direction[1]) in self.moves:
                            self.moves.remove((self.i+direction[0], self.j+direction[1]))
                    elif (self.i+direction[0] != opposite_color_piece.i and self.j+direction[1] != opposite_color_piece.j) and (man_dist == 2 or man_dist == 1):
                        if (self.i+direction[0], self.j+direction[1]) in self.moves:
                            self.moves.remove((self.i+direction[0], self.j+direction[1]))

        for opposite_color_piece in opposite_color_pieces:
            for prot in opposite_color_piece.protected:
                if prot in self.moves:
                    self.moves.remove(prot)

class queen(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None

    def find_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = position_of_black_pieces if self.color == 'black' else position_of_white_pieces
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        op_king_pos = black_king_pos if self.color == 'white' else white_king_pos

        for i in range(1, 8):
            if self.i + i <= 7 and (self.i+i, self.j) not in pos_to_avoid:
                self.moves.add((self.i+i, self.j))
                if (self.i+i, self.j) in pos_to_stop:
                    break
            elif self.i + i <= 7 and (self.i+i, self.j) in pos_to_avoid:
                self.protected.add((self.i+i, self.j))
                break
        for i in range(1, 8):
            if self.i - i >= 0 and (self.i-i, self.j) not in pos_to_avoid:
                self.moves.add((self.i-i, self.j))
                if (self.i-i, self.j) in pos_to_stop:
                    break
            elif self.i - i >= 0 and (self.i-i, self.j) in pos_to_avoid:
                self.protected.add((self.i-i, self.j))
                break
        for i in range(1, 8):
            if self.i + i <= 7:
                
                if self.j + i <= 7 and (self.i+i, self.j+i) not in pos_to_avoid:
                    self.moves.add((self.i+i, self.j+i))
                    if (self.i+i, self.j+i) in pos_to_stop:
                        break
                elif self.j + i <= 7 and (self.i+i, self.j+i) in pos_to_avoid:
                    self.protected.add((self.i+i, self.j+i))
                    break
                    
        for i in range(1, 8):
            if self.i + i <= 7:
                if self.j - i >= 0 and (self.i+i, self.j-i) not in pos_to_avoid:
                    self.moves.add((self.i+i, self.j-i))
                    if (self.i+i, self.j-i) in pos_to_stop:
                        break
                elif self.j - i >= 0 and (self.i+i, self.j-i) in pos_to_avoid:
                    self.protected.add((self.i+i, self.j-i))
                    break
                    
        for i in range(1, 8):
            if self.i - i >= 0:
                #pos_to_avoid.add((self.i-i, self.j))
                if self.j + i <= 7 and (self.i-i, self.j+i) not in pos_to_avoid:
                    self.moves.add((self.i-i, self.j+i))
                    if (self.i-i, self.j+i) in pos_to_stop:
                        break
                elif self.j + i <= 7 and (self.i-i, self.j+i) in pos_to_avoid:
                    self.protected.add((self.i-i, self.j+i))
                    break
                    
        for i in range(1, 8):
            if self.i - i >= 0:
                if self.j - i >= 0 and (self.i-i, self.j-i) not in pos_to_avoid:
                    self.moves.add((self.i-i, self.j-i))
                    if (self.i-i, self.j-i) in pos_to_stop:
                        break
                elif self.j - i >= 0 and (self.i-i, self.j-i) in pos_to_avoid:
                    self.protected.add((self.i-i, self.j-i))
                    break
                    
        for j in range(1, 8):
            if self.j + j <= 7 and (self.i, self.j+j) not in pos_to_avoid:
                self.moves.add((self.i, self.j+j))
                if (self.i, self.j+j) in pos_to_stop:
                    break
            elif self.j + j <= 7 and (self.i, self.j+j) in pos_to_avoid:
                self.protected.add((self.i, self.j+j))
                break
                
        for j in range(1, 8):
            if self.j - j >= 0 and (self.i, self.j-j) not in pos_to_avoid:
                self.moves.add((self.i, self.j-j))
                if (self.i, self.j-j) in pos_to_stop:
                    break
            elif self.j - j >= 0 and (self.i, self.j-j) in pos_to_avoid:
                self.protected.add((self.i, self.j-j))
                break
                
        if op_king_pos in self.moves:
            self.is_king_in_moves = True
        else:
            self.is_king_in_moves = False
        #remove_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)

class rook(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        
    def find_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = position_of_black_pieces if self.color == 'black' else position_of_white_pieces
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        op_king_pos = white_king_pos if self.color == 'black' else black_king_pos

        for i in range(1, 8):
            if self.i - i >= 0 and (self.i-i, self.j) not in pos_to_avoid:
                self.moves.add((self.i-i, self.j))
                if (self.i-i, self.j) in pos_to_stop:
                    break
            elif self.i - i >= 0 and (self.i-i, self.j) in pos_to_avoid:
                self.protected.add((self.i-i, self.j))
                break
        for i in range(1, 8):
        
            if self.i + i <= 7 and (self.i+i, self.j) not in pos_to_avoid:
                self.moves.add((self.i+i, self.j))
                if (self.i+i, self.j) in pos_to_stop:
                    break
            elif self.i + i <= 7 and (self.i+i, self.j) in pos_to_avoid:
                self.protected.add((self.i+i, self.j))
                break
                
        for i in range(1, 8):
            if self.j + i <= 7 and (self.i, self.j+i) not in pos_to_avoid:
                self.moves.add((self.i, self.j+i))
                if (self.i, self.j+i) in pos_to_stop:
                    break
            elif self.j + i <= 7 and (self.i, self.j+i) in pos_to_avoid:
                self.protected.add((self.i, self.j+i))
                break
                
        for i in range(1, 8):
            if self.j - i >= 0 and (self.i, self.j-i) not in pos_to_avoid:
                self.moves.add((self.i, self.j-i))
                if (self.i, self.j-i) in pos_to_stop:
                    break
            elif self.j - i >= 0 and (self.i, self.j-i) in pos_to_avoid:
                self.protected.add((self.i, self.j-i))
                break
            
        if op_king_pos in self.moves:
            self.is_king_in_moves = True
        else:
            self.is_king_in_moves = False
        #remove_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)

class bishop(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        
    def find_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = position_of_black_pieces if self.color == 'black' else position_of_white_pieces
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        op_king_pos = white_king_pos if self.color == 'black' else black_king_pos

        for i in range(1, 8):
            if self.i + i <= 7:
                if self.j + i <= 7 and (self.i+i, self.j+i) not in pos_to_avoid:
                    self.moves.add((self.i+i, self.j+i))
                    if (self.i+i, self.j+i) in pos_to_stop:
                        break
                elif self.j + i <= 7 and (self.i+i, self.j+i) in pos_to_avoid:
                    self.protected.add((self.i+i, self.j+i))
                    break
            
        for i in range(1, 8):
            if self.i + i <= 7:
                if self.j - i >= 0 and (self.i+i, self.j-i) not in pos_to_avoid:
                    self.moves.add((self.i+i, self.j-i))
                    if (self.i+i, self.j-i) in pos_to_stop:
                        break
                elif self.j - i >= 0 and (self.i+i, self.j-i) in pos_to_avoid:
                    self.protected.add((self.i+i, self.j-i))
                    break
        
        for i in range(1, 8):
            if self.i - i >= 0:
                if self.j + i <= 7 and (self.i-i, self.j+i) not in pos_to_avoid:
                    self.moves.add((self.i-i, self.j+i))
                    if (self.i-i, self.j+i) in pos_to_stop:
                        break
                elif self.j + i <= 7 and (self.i-i, self.j+i) in pos_to_avoid:
                    self.protected.add((self.i-i, self.j+i))
                    break
                    
        for i in range(1, 8):
            if self.i - i >= 0:
                if self.j - i >= 0 and (self.i-i, self.j-i) not in pos_to_avoid:
                    self.moves.add((self.i-i, self.j-i))
                    if (self.i-i, self.j-i) in pos_to_stop:
                        break
                elif self.j - i >= 0 and (self.i-i, self.j-i) in pos_to_avoid:
                    self.protected.add((self.i-i, self.j-i))
                    break
                    
        if op_king_pos in self.moves:
            self.is_king_in_moves = True
        else:
            self.is_king_in_moves = False
        #remove_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)

class knight(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        
    def find_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = position_of_black_pieces if self.color == 'black' else position_of_white_pieces
        op_king_pos = white_king_pos if self.color == 'black' else black_king_pos

        if self.i - 1 >= 0:
            if self.j + 2 <= 7 and (self.i-1, self.j+2) not in pos_to_avoid:
                self.moves.add((self.i-1, self.j+2))
                
            elif self.j + 2 <= 7 and (self.i-1, self.j+2) in pos_to_avoid:
                self.protected.add((self.i-1, self.j+2))
            if self.j -2 >= 0 and (self.i-1, self.j-2) not in pos_to_avoid:
                self.moves.add((self.i-1, self.j-2))
                
            elif self.j -2 >= 0 and (self.i-1, self.j-2) in pos_to_avoid:
                self.protected.add((self.i-1, self.j-2))
        if self.i + 1 <= 7:
            if self.j + 2 <= 7 and (self.i+1, self.j+2) not in pos_to_avoid:
                self.moves.add((self.i+1, self.j+2))
                
            elif self.j + 2 <= 7 and (self.i+1, self.j+2) in pos_to_avoid:
                self.protected.add((self.i+1, self.j+2))
            if self.j - 2 >= 0 and (self.i+1, self.j-2) not in pos_to_avoid:
                self.moves.add((self.i+1, self.j-2))
                
            elif self.j - 2 >= 0 and (self.i+1, self.j-2) in pos_to_avoid:
                self.protected.add((self.i+1, self.j-2))
        if self.i - 2 >= 0:
            if self.j - 1 >= 0 and (self.i-2, self.j-1) not in pos_to_avoid:
                self.moves.add((self.i-2, self.j-1))
                
            elif self.j - 1 >= 0 and (self.i-2, self.j-1) in pos_to_avoid:
                self.protected.add((self.i-2, self.j-1))
            if self.j + 1 <= 7 and (self.i-2, self.j+1) not in pos_to_avoid:
                self.moves.add((self.i-2, self.j+1))
                
            elif self.j + 1 <= 7 and (self.i-2, self.j+1) in pos_to_avoid:
                self.protected.add((self.i-2, self.j+1))
        if self.i + 2 <= 7:
            if self.j + 1 <= 7 and (self.i+2, self.j+1) not in pos_to_avoid:
                self.moves.add((self.i+2, self.j+1))
                
            elif self.j + 1 <= 7 and (self.i+2, self.j+1) in pos_to_avoid:
                self.protected.add((self.i+2, self.j+1))
            if self.j - 1 >= 0 and (self.i+2, self.j-1) not in pos_to_avoid:
                self.moves.add((self.i+2, self.j-1))
                
            elif self.j - 1 >= 0 and (self.i+2, self.j-1) in pos_to_avoid:
                self.protected.add((self.i+2, self.j-1))
                
        if op_king_pos in self.moves:
            self.is_king_in_moves = True
        else:
            self.is_king_in_moves = False
        #remove_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)
        
black_king_pos = (4, 0)
white_king_pos = (4, 7)

position_of_black_pieces = set()
position_of_white_pieces = set()
board_pieces = {}

black_piece_images = [r'C:\Users\avery\Pictures\bK.png', r'C:\Users\avery\Pictures\bQ.png', r'C:\Users\avery\Pictures\bR.png', r'C:\Users\avery\Pictures\bB.png',
                r'C:\Users\avery\Pictures\bN.png', r'C:\Users\avery\Pictures\bp.png']
white_piece_images = [r'C:\Users\avery\Pictures\wK.png', r'C:\Users\avery\Pictures\wQ.png', r'C:\Users\avery\Pictures\wR.png', r'C:\Users\avery\Pictures\wB.png',
                r'C:\Users\avery\Pictures\wN.png', r'C:\Users\avery\Pictures\wp.png']

pieces = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']

to_place = {'r' + pieces[2]: (black_piece_images[2], white_piece_images[2], rook), 
            'r' + pieces[4]: (black_piece_images[4], white_piece_images[4], knight), 
            'r' + pieces[3]: (black_piece_images[3], white_piece_images[3], bishop), 
            pieces[1]: (black_piece_images[1], white_piece_images[1], queen), 
            pieces[0]: (black_piece_images[0], white_piece_images[0], king), 
            'l' + pieces[3]: (black_piece_images[3], white_piece_images[3], bishop), 
            'l' + pieces[4]: (black_piece_images[4], white_piece_images[4], knight), 
            'l' + pieces[2]: (black_piece_images[2], white_piece_images[2], rook)}

white_captured_piece = {'pawn' : [pygame.image.load(white_piece_images[-1]).convert_alpha(), 0], 
                        'knight' : [pygame.image.load(white_piece_images[4]).convert_alpha(), 0], 
                        'bishop' : [pygame.image.load(white_piece_images[3]).convert_alpha(), 0], 
                        'rook' : [pygame.image.load(white_piece_images[2]).convert_alpha(), 0], 
                        'queen' : [pygame.image.load(white_piece_images[1]).convert_alpha(), 0]}

black_captured_piece = {'pawn' : [pygame.image.load(black_piece_images[-1]).convert_alpha(), 0], 
                        'knight' : [pygame.image.load(black_piece_images[4]).convert_alpha(), 0], 
                        'bishop' : [pygame.image.load(black_piece_images[3]).convert_alpha(), 0], 
                        'rook' : [pygame.image.load(black_piece_images[2]).convert_alpha(), 0], 
                        'queen' : [pygame.image.load(black_piece_images[1]).convert_alpha(), 0]}
