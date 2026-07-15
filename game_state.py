import pygame
from button import *
from helper_functions import * 
from pieces import *
import pickle

# Acts as the game engine of the chess game, it performs multiple operations, including:
# handling of the initialisation info of the game, avoiding to use globals and
# simplifing the passing of the arguments into functions, now a function only
# needs this object to access the game's info.
class GameState():
    def __init__(self):
        self.data_file_name = "chess_game_data"
        
        self.res = res = (1000, 800)
        self.screen = pygame.display.set_mode(size=res)
        self.block_sz = (100, 100)
        self.block_list = [[] for _ in range(8)]
        self.font1 = pygame.font.SysFont('Arial', 30)
        self.font = pygame.font.SysFont('Arial', 15)
        self.clock = pygame.time.Clock()

        self.pieces_sz_captured = (40, 40)
        self.pieces_sz_board = (60, 60)
        
        self.pieces_sz_offset = ((self.block_sz[0]-self.pieces_sz_board[0])//2, (self.block_sz[1]-self.pieces_sz_board[1])//2)
        self.b_w, self.b_h = 100, 50
        self.first_time = True
        self.username1, self.username2 = "PlayerA", "PlayerB"
        
        self.black_king_pos = (4, 0)
        self.white_king_pos = (4, 7)

        self.position_of_black_pieces = set()
        self.position_of_white_pieces = set()
        self.board_pieces = {}

        self.black_piece_images = [r'C:\Users\avery\Pictures\bK.png', r'C:\Users\avery\Pictures\bQ.png', r'C:\Users\avery\Pictures\bR.png', r'C:\Users\avery\Pictures\bB.png',
                        r'C:\Users\avery\Pictures\bN.png', r'C:\Users\avery\Pictures\bp.png']
        self.white_piece_images = [r'C:\Users\avery\Pictures\wK.png', r'C:\Users\avery\Pictures\wQ.png', r'C:\Users\avery\Pictures\wR.png', r'C:\Users\avery\Pictures\wB.png',
                        r'C:\Users\avery\Pictures\wN.png', r'C:\Users\avery\Pictures\wp.png']

        self.pieces = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']

        # needed in helper function, because the initialisation of the pawns and the rest of the pieces
        # is handled differently
        self.pawn = pawn

        self.to_place = {'r' + self.pieces[2]: (self.black_piece_images[2], self.white_piece_images[2], rook), 
                    'r' + self.pieces[4]: (self.black_piece_images[4], self.white_piece_images[4], knight), 
                    'r' + self.pieces[3]: (self.black_piece_images[3], self.white_piece_images[3], bishop), 
                    self.pieces[1]: (self.black_piece_images[1], self.white_piece_images[1], queen), 
                    self.pieces[0]: (self.black_piece_images[0], self.white_piece_images[0], king), 
                    'l' + self.pieces[3]: (self.black_piece_images[3], self.white_piece_images[3], bishop), 
                    'l' + self.pieces[4]: (self.black_piece_images[4], self.white_piece_images[4], knight), 
                    'l' + self.pieces[2]: (self.black_piece_images[2], self.white_piece_images[2], rook)}

        self.white_captured_piece = {'pawn' : [pygame.image.load(self.white_piece_images[-1]).convert_alpha(), 0], 
                                'knight' : [pygame.image.load(self.white_piece_images[4]).convert_alpha(), 0], 
                                'bishop' : [pygame.image.load(self.white_piece_images[3]).convert_alpha(), 0], 
                                'rook' : [pygame.image.load(self.white_piece_images[2]).convert_alpha(), 0], 
                                'queen' : [pygame.image.load(self.white_piece_images[1]).convert_alpha(), 0]}

        self.black_captured_piece = {'pawn' : [pygame.image.load(self.black_piece_images[-1]).convert_alpha(), 0], 
                                'knight' : [pygame.image.load(self.black_piece_images[4]).convert_alpha(), 0], 
                                'bishop' : [pygame.image.load(self.black_piece_images[3]).convert_alpha(), 0], 
                                'rook' : [pygame.image.load(self.black_piece_images[2]).convert_alpha(), 0], 
                                'queen' : [pygame.image.load(self.black_piece_images[1]).convert_alpha(), 0]}
        
        self.pieces_imgs = [self.black_captured_piece, self.white_captured_piece]
        
        self.count = 0
        
        # needed for the 50, 75 rule
        self.no_pawns_moved = True
        self.no_captured_piece = True
        self.fifty_moves_rule = 100
        self.seventyfive_moves_rule = 150
        
        self.draw_possible = False
        self.draw_button_active = False
        self.draw_button = None
        
        self.en_passant_moves = []
        self.position_counts = {}
    
    def initialise_game(self):
        
        self.count = 0
        
        self.no_pawns_moved = True
        self.no_captured_piece = True
        
        self.draw_possible = False
        self.draw_button_active = False
        
        self.en_passant_moves = []
        self.position_counts = {}
        
        create_and_place_pieces(self)
        set_captured_to_zero(self.white_captured_piece, self.black_captured_piece)
        
        draw_captured(0, None, self)
        draw(self)
        
        side_x_width = self.res[0]*0.2
        button_size = (self.b_w*1.5, self.b_h)
        main_menu = Button((self.res[0]-side_x_width//2) - button_size[0]//2, self.res[1]-button_size[1]*2, *button_size, "Main Menu", lambda : None)
        self.draw_button = Button((self.res[0]-side_x_width//2) - button_size[0]//2, self.res[1]-button_size[1]*6, *button_size, "Draw", lambda : None)
        
        return main_menu, self.draw_button
    
    def handle_piece_selection(self, mouse_pos, events_list):
        moves, draw_list = [], []
        for bp in available_pieces(self.count, self):
            if self.board_pieces[bp].rect.collidepoint(mouse_pos):
                pam, draw_list = print_available_moves(self.board_pieces[bp], self)
                moves = (pam, self.board_pieces[bp], bp)
                break
        else:
            events_list.clear()
            
        return moves, draw_list
    
    def execute_move(self, moves, events_list, block_sz, bp):
        
        for b in moves[0]:
            if b.rect.collidepoint(events_list[-1]):
            
                self.count += 1
                
                position_of_same_color_pieces = self.position_of_black_pieces if (moves[1].color == 'black') else self.position_of_white_pieces
                position_of_opposite_color_pieces = self.position_of_black_pieces if (moves[1].color == 'white') else self.position_of_white_pieces
                position_of_same_color_pieces.remove((moves[1].i, moves[1].j))
                
                # needed for the en passant method
                dif_x = abs(moves[1].i - events_list[-1][0]//block_sz[0])
                dif_y = abs(moves[1].j - events_list[-1][1]//block_sz[1])
                
                set_move(moves[1], events_list[-1][0]//block_sz[0], events_list[-1][1]//block_sz[1])
            
                board_pieces_index = (events_list[-1][0]//block_sz[0], events_list[-1][1]//block_sz[1])
                
                if board_pieces_index in position_of_opposite_color_pieces:
                    position_of_opposite_color_pieces.remove(board_pieces_index)
                    change_captured(board_pieces_index, self)
                    
                position_of_same_color_pieces.add((moves[1].i, moves[1].j))
                self.board_pieces[board_pieces_index] = self.board_pieces[bp]
                del self.board_pieces[bp]

                # handle the unbound error, incase no en passant moves are found
                pawn_en_passant_moves = []

                if self.board_pieces[board_pieces_index].name == 'king':
                    if self.board_pieces[board_pieces_index].color == 'black':
                        self.black_king_pos = (self.board_pieces[board_pieces_index].i, self.board_pieces[board_pieces_index].j)
                    elif self.board_pieces[board_pieces_index].color == 'white':
                        self.white_king_pos = (self.board_pieces[board_pieces_index].i, self.board_pieces[board_pieces_index].j)
                        
                    self.board_pieces[board_pieces_index].step_counter += 1
                    self.board_pieces[board_pieces_index].change_rook_castling(self, (moves[1].i, moves[1].j))
                
                elif self.board_pieces[board_pieces_index].name == "pawn":
                    pawn_en_passant_moves = self.board_pieces[board_pieces_index].handle_en_passant(self, (moves[1].i, moves[1].j), 
                                                                                                                dif_y, self.count)
                    if self.board_pieces[board_pieces_index].capture_en_passant(dif_x, dif_y, self, (moves[1].i, moves[1].j), self.count):
                        
                        pawn_index = self.board_pieces[board_pieces_index].en_passant_move
                        
                        position_of_opposite_color_pieces.remove(pawn_index)
                        change_captured(pawn_index, self)
                        del self.board_pieces[pawn_index]

                handle_promotion(events_list, self)

                events_list.clear()

                for b in self.board_pieces:
                    self.board_pieces[b].find_moves(self)
                    
                for b in list(self.board_pieces.keys()):
                    self.board_pieces[b].remove_reveal_king_moves(self.count, self)

                for move in pawn_en_passant_moves:
                    en_passant_pawn = self.board_pieces[move[0]]
                    en_passant_pawn.moves.add(move[1])
                    en_passant_pawn.en_passant_move = move[2]
                    if (en_passant_pawn.en_passant_turn_count == 0):
                        en_passant_pawn.en_passant_turn_count = self.count

                # needed to calculate the hash value for the three and fivefold repetitions
                self.en_passant_moves = pawn_en_passant_moves

                is_king_checked(self.board_pieces[self.black_king_pos], self)
                is_king_checked(self.board_pieces[self.white_king_pos], self)
                
                self.update_threefold()
                
                break
            
        else:
                        
            events_list.clear()
            
    def get_castling_rights_kings(self):
        
        white_king = self.board_pieces[self.white_king_pos]
        black_king = self.board_pieces[self.black_king_pos]
        
        return (white_king.left_castling_available, 
                white_king.right_castling_available,
                black_king.left_castling_available,
                black_king.right_castling_available)
            
    def get_position_key(self):
        
        board_state = tuple(sorted(self.board_pieces.items()))
        side_to_move = self.count % 2
        castling_rights = self.get_castling_rights_kings()
        en_passant_squares = tuple(self.en_passant_moves)
        
        return (
            board_state,
            side_to_move,
            castling_rights,
            en_passant_squares,
        )
        
    def check_insufficient_material(self, cur_game_state):
        black_pieces_remaining = active_pieces(cur_game_state.board_pieces, cur_game_state.position_of_black_pieces)
        white_pieces_remaining = active_pieces(cur_game_state.board_pieces, cur_game_state.position_of_white_pieces)
        
        black_pieces_names = {cur_game_state.board_pieces[bp].name for bp in black_pieces_remaining}
        white_pieces_names = {cur_game_state.board_pieces[bp].name for bp in white_pieces_remaining}
        
        black_bishop_active = any([key in black_pieces_names for key in ("lbishop", "rbishop")])
        white_bishop_active = any([key in white_pieces_names for key in ("lbishop", "rbishop")])
        same_colored_bishops = (all(["lbishop" in pieces_rem for pieces_rem in (black_pieces_names, white_pieces_names)]) or 
                                all(["rbishop" in pieces_rem for pieces_rem in (black_pieces_names, white_pieces_names)]))
        
        black_knight_active = any([key in black_pieces_names for key in ("lknight", "rknight")])
        white_knight_active = any([key in white_pieces_names for key in ("lknight", "rknight")])
        
        one_piece_rem_white = len(white_pieces_remaining) == 1
        one_piece_rem_black = len(black_pieces_remaining) == 1
        two_pieces_rem_white = len(white_pieces_remaining) == 2
        two_pieces_rem_black = len(black_pieces_remaining) == 2
        
        # case 1 = king vs king
        # the kings are the only pieces that cannot be captured and thus never get deleted from the board_pieces dict,
        # meaning that when the length of either sub-dict (of white and black pieces) is equal to one, only the king
        # remains
        only_kings_remaining = one_piece_rem_white and one_piece_rem_black
        
        # case 2 = king and bishop vs king
        king_bishop_remaining = ((two_pieces_rem_white and white_bishop_active and one_piece_rem_black) or 
                                 (two_pieces_rem_black and black_bishop_active and one_piece_rem_white))
        
        # case 3 = king and knight vs king
        king_knight_remaining = ((two_pieces_rem_white and white_knight_active and one_piece_rem_black) or 
                                 (two_pieces_rem_black and black_knight_active and one_piece_rem_white))
        
        # case 4 = king and bishop vs king and bishop of the same color as the opponent's bishop
        kings_bishops_remaining = ((two_pieces_rem_white and white_bishop_active and 
                                    two_pieces_rem_black and black_bishop_active) and 
                                   same_colored_bishops)
        
        return only_kings_remaining or king_bishop_remaining or king_knight_remaining or kings_bishops_remaining
            
    def fifty_seventyfive_move_rule(self, cur_game_state):
        
        self.no_pawns_moved = all([not cur_game_state.board_pieces[bp].moved for bp in cur_game_state.board_pieces if cur_game_state.board_pieces[bp].name == "pawn"])
        self.no_captured_piece = len(cur_game_state.board_pieces) == 32
        
        self.draw_possible = self.no_pawns_moved and self.no_captured_piece
        self.draw_button_active = self.draw_possible and (cur_game_state.count >= self.fifty_moves_rule)
        
        if self.draw_possible and (cur_game_state.count >= self.fifty_moves_rule) and self.draw_button.pressed:
            return True
        
        if (cur_game_state.count == self.seventyfive_moves_rule) and self.draw_possible:
            return True
        
        return False
            
    def check_stalemate(self, num, num2):
        # white pieces stalemate
        if ((num == 0) and (not self.board_pieces[self.white_king_pos].is_checked)):
            return True
        
         # black pieces stalemate
        if ((num2 == 0) and (not self.board_pieces[self.black_king_pos].is_checked)):
            return True
        
        return False
    
    def get_repetition_num(self):
        
        key = self.get_position_key()
        return self.position_counts.get(key, 0)
    
    def update_threefold(self):
        
        key = self.get_position_key()
        self.position_counts[key] = self.position_counts.get(key, 0) + 1
        
    def check_threefold(self):
        
        if any([3 <= val < 5 for val in self.position_counts.values()]):
            self.draw_button_active = True
            if self.draw_button.pressed:
                return True
        
        if any([val == 5 for val in self.position_counts.values()]):
            return True
        
        return False
        
    def check_draw(self, num, num2, cur_game_state):
        
        return (self.check_stalemate(num, num2) or 
                self.check_insufficient_material(cur_game_state) or
                self.fifty_seventyfive_move_rule(cur_game_state) or
                self.check_threefold())
            
    # method to check whether the game must be terminated (ckeckmate or draw reached)
    def evaluate_game_state(self, cur_game_state):
        num = num_of_pieces_with_moves(self.board_pieces[self.white_king_pos], self)
        num2 = num_of_pieces_with_moves(self.board_pieces[self.black_king_pos], self)

        exit_condition = None

        if (num2 == 0) and self.board_pieces[self.black_king_pos].is_checked:
            self.first_time = False
            exit_condition = 1
        if (num == 0) and self.board_pieces[self.white_king_pos].is_checked:
            self.first_time = False
            exit_condition = -1
        if self.check_draw(num, num2, cur_game_state):
            self.first_time = False
            exit_condition = 0
            
        return exit_condition
    
    def render_game(self, draw_list, main_menu, draw_button, exit_condition):
        self.screen.fill(pygame.Color("saddlebrown"))
        
        draw(self)
        for color, square in draw_list:
            pygame.draw.circle(self.screen, color,square.rect.center, 10)
        draw_captured(self.count, exit_condition, self)
        
        main_menu.draw(self.screen)
        
        if self.draw_button_active: draw_button.draw(self.screen)
        
    def save_username(self, indx, usrnm):
        if indx == 0:
            self.username1 = usrnm
        elif indx == 1:
            self.username2 = usrnm
    
    def save_game_data(self, game_data):
        with open(self.data_file_name, "wb") as f:
            pickle.dump(game_data, f)
        
    # store_h2h_data_new_dict handles the storing of the head to head and
    # overall statistics of the players.
    def store_h2h_data(self, game_data, username1, username2, white_won):
        
        # just to avoid any errors, the value of whit_won must be a value from
        # this set: -1, 0, 1. The None value indicates the play function returned
        # before the completion of the game.
        if white_won is not None:
            played_again_h2h = game_data[username1]["H2H"] .get(username2, None)
            played_again_h2h_p2 = game_data[username2]["H2H"].get(username1, None)
            
            dict_player1 = game_data[username1]
            dict_player2 = game_data[username2]
            head_2_head_dict_player1 = played_again_h2h if (played_again_h2h is not None) else {}
            head_2_head_dict_player2 = played_again_h2h_p2 if (played_again_h2h_p2 is not None) else {}
            
            if played_again_h2h is None: 
                game_data[username1]["H2H"][username2] = {
                    "games_played" : 1,
                    "games_won" : 0,
                    "games_drawn" : 0,
                    "games_lost" : 0,
                    "W %" : 0.0
                }
                
                game_data[username2]["H2H"][username1] = {
                    "games_played" : 1,
                    "games_won" : 0,
                    "games_drawn" : 0,
                    "games_lost" : 0,
                    "W %" : 0.0
                }
                
                head_2_head_dict_player1 = game_data[username1]["H2H"][username2]
                head_2_head_dict_player2 = game_data[username2]["H2H"][username1]
                
            else:
                head_2_head_dict_player1["games_played"] += 1
                head_2_head_dict_player2["games_played"] += 1
            
            dict_player1["games_played"] += 1
            dict_player2["games_played"] += 1
            
            if white_won == -1:
                head_2_head_dict_player1["games_lost"] += 1
                dict_player1["games_lost"] += 1
                head_2_head_dict_player2["games_won"] += 1
                dict_player2["games_won"] += 1
            elif white_won == 1:
                head_2_head_dict_player1["games_won"] += 1
                dict_player1["games_won"] += 1
                head_2_head_dict_player2["games_lost"] += 1
                dict_player2["games_lost"] += 1
            else:
                head_2_head_dict_player1["games_drawn"] += 1
                dict_player1["games_drawn"] += 1
                head_2_head_dict_player2["games_drawn"] += 1
                dict_player2["games_drawn"] += 1
                
            dict_player1["W %"] = dict_player1["games_won"] / dict_player1["games_played"] * 100
            dict_player2["W %"] = dict_player2["games_won"] / dict_player2["games_played"] * 100
            head_2_head_dict_player1["W %"] = head_2_head_dict_player1["games_won"] / head_2_head_dict_player1["games_played"] * 100
            head_2_head_dict_player2["W %"] = head_2_head_dict_player2["games_won"] / head_2_head_dict_player2["games_played"] * 100
