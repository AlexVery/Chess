from settings import *
from helper_functions import *

class piece():
    def __init__(self, image, color, name, i, j):
        self.i, self.j = i, j
        self.image = image
        self.color = color
        self.name = name
        self.moves = set()
        self.is_king_in_moves = False
        # για να γινεται handle σε συναρτηση που βρισκει τις κινησεις που μπορει να κανει το καθε πιονι, μεσω dictionary, και αργοτερα update, γιατι οι
        #πιθανες κινησεις θα αλλαζουν με βαση το position

class pawn(piece):
    def __init__(self, i, j, image, color, name):            # i, j denote the position in the 2d list of blocks/rects
        super().__init__(image, color, name, i, j)
        self.optional_moves = set()
        self.protected = set()
        self.important_moves = set()
        self.rect = None

    def find_moves(self, black_king_pos, white_king_pos):
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
        remove_moves(self, black_king_pos, white_king_pos)

class king(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        self.is_checked = False

    def find_moves(self, black_king_pos, white_king_pos):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = position_of_black_pieces if self.color == 'black' else position_of_white_pieces
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        non_available_moves = {board_pieces[i[0], i[1]] for i in pos_to_stop if board_pieces[i[0], i[1]].name != 'king'}
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


    def update_moves(self):
        pos_to_stop = position_of_black_pieces if self.color == 'white' else position_of_white_pieces
        opposite_color_pieces = {board_pieces[i[0], i[1]] for i in pos_to_stop}
       
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
                    if (man_dist == 0):
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
                    #man_dist_from_self = manhattam_distance((opposite_color_piece.i, opposite_color_piece.j), (self.i, self.j))
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

    def find_moves(self, black_king_pos, white_king_pos):
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
        remove_moves(self, black_king_pos, white_king_pos)

class rook(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        
    def find_moves(self, black_king_pos, white_king_pos):
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
        remove_moves(self, black_king_pos, white_king_pos)

class bishop(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        
    def find_moves(self, black_king_pos, white_king_pos):
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
        remove_moves(self, black_king_pos, white_king_pos)

class knight(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        
    def find_moves(self, black_king_pos, white_king_pos):
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
        remove_moves(self, black_king_pos, white_king_pos)