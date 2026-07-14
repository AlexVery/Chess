import sys
import pygame
from button import *

# DisplayText class is used to display important UI elements:
# for example when the players try to log in using the same
# username, a message appears informing them that it is not
# possible and the two usernames must be distinct
# y is the top of the text's rect, width the width of the screen
# backgr_color is a keyword argument determining whether a rect with
# the specified color will be displayed behind the text. In case it
# it remains None, no rect will be drawn
class DisplayText():
    def __init__(self, text, text_sz, width, y, text_color, backgr_color=None):
        self.text = text
        self.text_sz = text_sz
        self.text_col = text_color
        self.backgr_color = backgr_color
        self.display_backgr = backgr_color is not None
        self.w, self.y = width, y
        self.display = False
        
        self.font = pygame.font.SysFont("Arial", self.text_sz, True)
        self.text_rend = self.font.render(self.text, True, self.text_col)
        self.text_rend_w, self.text_rend_h = self.text_rend.get_size()
        self.rect = pygame.Rect(self.w // 2 - self.text_rend_w // 2, self.y, self.text_rend_w, self.text_rend_h)
        
    # condition determines whether the text is going to be displayed,
    # for the example mentioned above the condition would be: username1 == username2
    def update(self, condition):
        self.display = condition
        
    def draw(self, screen):
        if self.display:
            if self.display_backgr:
                pygame.draw.rect(screen, self.backgr_color, self.rect)
            screen.blit(self.text_rend, self.rect)

# block class represents a square of the 8x8 board
class block():
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = [color]

#pos1 ans pos2 must be tuples: (x,y)
def manhattam_distance(pos1, pos2):   
    return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

def set_move(bp, i, j):    #bp = board_player
    move_piece(bp, (i, j))

# check whether king is attacked by any enemy piece
def is_king_checked(board_piece, cur_game_state):
    pos_of_opposite_color = cur_game_state.position_of_black_pieces if (board_piece.color == 'white') else cur_game_state.position_of_white_pieces
    non_available_moves = {cur_game_state.board_pieces[i[0], i[1]] for i in pos_of_opposite_color}
    for nam in non_available_moves:
        moves_to_check = nam.important_moves if nam.name == 'pawn' else nam.moves 
        if (board_piece.i, board_piece.j) in moves_to_check:
            board_piece.is_checked = True
            break
    else:
        board_piece.is_checked = False

def move_piece(board_piece, move):
    board_piece.i, board_piece.j = move[0], move[1]
    board_piece.moved = True
    board_piece.promote()
    board_piece.rect.topleft = (board_piece.i * 100 + 15, board_piece.j * 100 + 15)

# draw images of the captured pawns to the right of the board
def draw_images_of_captured(offset_captured, cur_game_state):  # cur_game_state = GameState object
    pygame.draw.rect(cur_game_state.screen, pygame.Color('tan3'), (800, 0, 200, 800))
    start_y = 30

    j = 0
    for wp in cur_game_state.white_captured_piece:
        im = pygame.transform.scale(cur_game_state.white_captured_piece[wp][0], cur_game_state.pieces_sz_captured)
        cur_game_state.screen.blit(im, (820, start_y + offset_captured[1] * j))
        j += 1

    j = 0
    for wp in cur_game_state.black_captured_piece:
        im = pygame.transform.scale(cur_game_state.black_captured_piece[wp][0], cur_game_state.pieces_sz_captured)
        cur_game_state.screen.blit(im, (910, start_y + offset_captured[1] * j))
        j += 1

def draw_captured(count, exit_condition, cur_game_state):
    
    username = (cur_game_state.username1 if ((count%2) == 0) else cur_game_state.username2)
    # the player who wins is the one who made the last move resulting in the checkmate,
    # being reflected by exit_condition: -1 = black won, 1 = white won, 0 = draw
    username_won_dict = {
        1 : cur_game_state.username1,
        -1 : cur_game_state.username2
    }
    username_won = username_won_dict.get(exit_condition, None)
    turn_text = username + ("'s turn")
    # exit_condition comes from the play function and means:
    # 0 = draw, -1 = black won, 1 = white won, None = no result decided yet
    result_text = "Draw" if (exit_condition == 0) else (username_won + " won!") if (exit_condition is not None) else ""
    
    text_to_render, color_to_render = turn_text, pygame.Color("white" if ((count%2) == 0) else "black")
    text_to_render, color_to_render = ((text_to_render, color_to_render) if (not result_text) else 
                                       (result_text, pygame.Color("white" if (exit_condition == 1) else "black" if (exit_condition == -1) else "midnightblue")))
    
    font_turn = pygame.sysfont.SysFont("Arial", 13, True)
    font_turn_txt = font_turn.render(text_to_render, True, color_to_render)
    
    txt1_w, txt1_h = font_turn.size(cur_game_state.username1 + "'s turn")
    txt2_w, txt2_h = font_turn.size(cur_game_state.username2 + "'s turn")
    text_exit_w, text_exit_h = font_turn.size(result_text)
    
    txt_w, txt_h = (txt1_w, txt1_h) if (count % 2 == 0) else (txt2_w, txt2_h)
    txt_w, txt_h = (txt_w, txt_h) if (not result_text) else (text_exit_w, text_exit_h)
    # the value of the offset is the size of the captured pieces (40x40) +
    # + a 0.25 offset so the space between them appears smooth
    offset_captured = (1.25 * cur_game_state.pieces_sz_captured[0], 1.25 * cur_game_state.pieces_sz_captured[1])
    
    draw_images_of_captured(offset_captured, cur_game_state)
    for c in enumerate(cur_game_state.white_captured_piece):
        text = cur_game_state.font.render(f'{cur_game_state.white_captured_piece[c[1]][1]}', True, pygame.Color('white'))
        cur_game_state.screen.blit(text, (870, cur_game_state.pieces_sz_captured[1] + offset_captured[1] * c[0]))
        
    for c in enumerate(cur_game_state.black_captured_piece):
        text = cur_game_state.font.render(f'{cur_game_state.black_captured_piece[c[1]][1]}', True, pygame.Color('white'))
        cur_game_state.screen.blit(text, (960, cur_game_state.pieces_sz_captured[1] + offset_captured[1] * c[0]))
        
    # we first need to calculate the difference between the half moves performed and the threshold for the
    # fifty move rule, same for seventy five rule move
    dif_fifty = cur_game_state.fifty_moves_rule-cur_game_state.count
    dif_seventyfive = cur_game_state.seventyfive_moves_rule-cur_game_state.count
    
    fifty_move_rule_txt = (f"50-move rule in {dif_fifty} moves") if (dif_fifty > 0) else ("50-move rule available")
    seventyfive_move_rule_txt = (f"75-move rule in {dif_seventyfive} moves") if (dif_seventyfive > 0) else "75-move rule activated" 
    move_texts = ["Half-moves: " + str(cur_game_state.count), fifty_move_rule_txt, seventyfive_move_rule_txt]
    
    if (not cur_game_state.no_pawns_moved) or (not cur_game_state.no_captured_piece):
        move_texts = move_texts[:1]
    
    side_rect_center = cur_game_state.res[0]-cur_game_state.block_sz[0]
    turn_rect_y = cur_game_state.pieces_sz_captured[1] + offset_captured[1] * 5 + txt_h
    
    move_texts_y_off = txt_h * 1.5
    move_texts_rends = [font_turn.render(text, True, pygame.Color("white")) for text in move_texts]
    move_texts_rects = [rend.get_rect() for rend in move_texts_rends]
    for i, rect in enumerate(move_texts_rects):
        rect.topleft = (side_rect_center-rect.width//2, turn_rect_y + move_texts_y_off * (i+2))
        
    cur_game_state.screen.blit(font_turn_txt, (side_rect_center-txt_w//2, turn_rect_y))
    
    for rend, rect in zip(move_texts_rends, move_texts_rects):
        cur_game_state.screen.blit(rend, rect)

def change_captured(pos, cur_game_state):
    color = cur_game_state.board_pieces[pos].color
    captured = cur_game_state.white_captured_piece if color == 'white' else cur_game_state.black_captured_piece
    if cur_game_state.board_pieces[pos].name == 'queen' or cur_game_state.board_pieces[pos].name == 'pawn':
        captured[cur_game_state.board_pieces[pos].name][1] += 1
    else:
        captured[cur_game_state.board_pieces[pos].name[1:]][1] += 1

# used to initialise the board
def create_and_place_pieces(cur_game_state):
    cur_game_state.board_pieces.clear()
    cur_game_state.position_of_black_pieces.clear()
    cur_game_state.position_of_white_pieces.clear()
    block_size = cur_game_state.block_sz    # block size
    
    for i in range(8):
            start = block_size[0] if i % 2 == 0 else 0
            left_for_white = start - block_size[0] if start else start + block_size[0]
            for j in range(4):
                if i % 2 == 0:
                    cur_game_state.block_list[i].append(block(left_for_white, i*block_size[0], block_size[0], block_size[1], pygame.Color('white')))
                    cur_game_state.block_list[i].append(block(start, i*block_size[0], block_size[0], block_size[1], pygame.Color('sienna4')))
                else:
                    cur_game_state.block_list[i].append(block(start, i*block_size[0], block_size[0], block_size[1], pygame.Color('sienna4')))
                    cur_game_state.block_list[i].append(block(left_for_white, i*block_size[0], block_size[0], block_size[1], pygame.Color('white')))
                start += block_size[0]* 2
                left_for_white += block_size[0] * 2

    for i in range(8):
        p1 = cur_game_state.pawn(i, 1, pygame.image.load(cur_game_state.black_piece_images[-1]).convert_alpha(), 'black', 'pawn', cur_game_state.to_place)
        p2 = cur_game_state.pawn(i, 6, pygame.image.load(cur_game_state.white_piece_images[-1]).convert_alpha(), 'white', 'pawn', cur_game_state.to_place)
        cur_game_state.board_pieces[(i,1)] = p1
        cur_game_state.board_pieces[(i,6)] = p2
        cur_game_state.position_of_black_pieces.add((i, 1))
        cur_game_state.position_of_white_pieces.add((i, 6))

    i = 0
    for name in cur_game_state.to_place:
        p1 = cur_game_state.to_place[name][2](i, 0, pygame.image.load(cur_game_state.to_place[name][0]).convert_alpha(), 'black', name)
        if p1.name == 'king':
            cur_game_state.black_king_pos = (i, 0)
        p2 = cur_game_state.to_place[name][2](i, 7, pygame.image.load(cur_game_state.to_place[name][1]).convert_alpha(), 'white', name)
        if p2.name == 'king':
            cur_game_state.white_king_pos = (i,7)
        cur_game_state.board_pieces[(i,0)] = p1
        cur_game_state.board_pieces[(i,7)] = p2
        cur_game_state.position_of_black_pieces.add((i, 0))
        cur_game_state.position_of_white_pieces.add((i, 7))
        i += 1

    for row in cur_game_state.block_list:
        for column in row:
            pygame.draw.rect(cur_game_state.screen, column.color[-1], column.rect)

    img_offset = ((block_size[0]-cur_game_state.pieces_sz_board[0])//2, (block_size[1]-cur_game_state.pieces_sz_board[1])//2)

    for p in cur_game_state.board_pieces:
        cur_game_state.screen.blit(cur_game_state.board_pieces[p].image, (cur_game_state.board_pieces[p].i * block_size[0] + img_offset[0], 
                                                           cur_game_state.board_pieces[p].j * block_size[1] + img_offset[1]))
        cur_game_state.board_pieces[p].rect = cur_game_state.board_pieces[p].image.get_rect()
        cur_game_state.board_pieces[p].rect.topleft = (cur_game_state.board_pieces[p].i * block_size[0] + img_offset[0], 
                                                       cur_game_state.board_pieces[p].j * block_size[1] + img_offset[1])
        cur_game_state.board_pieces[p].find_moves(cur_game_state)

# used when a pawn reaches the end of the board and must be promoted
def select_promotion(screen, end_screen, res, clock, imgs, color):
    # text to be used as display : text to search in the to_place dict (used to initialise the pieces)
    promotion_list = ["queen", "rook", "bishop", "knight"]
    
    dim_surface = pygame.Surface(res, pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 150))
    end_screen.blit(dim_surface, (0, 0))
    end_img = pygame.Surface(res)
    end_img.blit(end_screen, (0,0))
    
    font = pygame.font.SysFont("Arial", 24, True)
    
    rect_sz = (res[0]*0.5, res[1]*0.65)
    rect = pygame.Rect(res[0]//2-rect_sz[0]//2, res[1]//2-rect_sz[1]//2, *rect_sz)
    
    imgs_sz = (40, 40)
    pieces_imgs = imgs[color]  # 0 = black, 1 = white
    pieces_imgs = {key : pygame.transform.scale(pieces_imgs[key][0], imgs_sz) for key in promotion_list}
    imgs_rects = []
    
    # colors
    text_color = "white" if (color) else "black"  # color = 0 means black, otherwise white
    rect_color = "white" if (not color) else "black"
    hover_press_colors = [["gray", "darkgray"], ["gray50", "gray40"]]
    
    texts = ["Choose a promotion for the pawn:", *promotion_list]
    texts_rends = [font.render(text, True, pygame.Color(text_color)) for text in texts]
    texts_rects = [pygame.Rect(rect.centerx-texts_rends[0].get_width()//2, rect.top+texts_rends[0].get_height()*1.25, *texts_rends[0].get_size())]
    
    for i, text_rend in enumerate(texts_rends[1:]):
        topleftx = rect.left + rect.width * 0.3 #rect.centerx - (imgs_sz[0] * 1.1 + text_rend.get_width()) // 2
        toplefty = texts_rects[i].bottom + imgs_sz[1] * 1.1
        imgs_rects.append(pygame.Rect(topleftx, toplefty, *imgs_sz))
        texts_rects.append(pygame.Rect(topleftx + imgs_sz[0] * 2, toplefty + imgs_sz[1] // 2 - text_rend.get_height() // 2, *text_rend.get_size()))
        
    rects_to_check = texts_rects[1:]
    rects_active = [False for _ in range(len(rects_to_check))]
    rects_hover = [False for _ in range(len(rects_to_check))]
    
    buttons_sz = (150, 50)
    confirm_button = Button(rect.centerx-buttons_sz[0]//2, rect.bottom-buttons_sz[1]*1.5, buttons_sz[0], buttons_sz[1], "Confirm", lambda : None)
    
    running = True
    while running:
        
        clock.tick(60)
        screen.fill(0)
        screen.blit(end_img, (0,0))
        
        # update
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1):
                # we have to make sure that the list does not get erased when clicking on the confirm button,
                # therefore we need to maintain the list when a rect is active and we now click 'confirm'
                rects_active = [rec.collidepoint(mouse_pos) for rec in rects_to_check] if not confirm_button.rect.collidepoint(mouse_pos) else rects_active
            elif event.type == pygame.MOUSEMOTION:
                rects_hover = [rec.collidepoint(mouse_pos) for rec in rects_to_check]
        
        # draw
        pygame.draw.rect(screen, pygame.Color(rect_color), rect)
        
        # it has to be called after the drawing of the main rect (acting as a window)
        if any(rects_active): 
            confirm_button.update(events)
            confirm_button.draw(screen)
            if confirm_button.pressed: return promotion_list[rects_active.index(True)]
        
        for rec, actv_rec, hover_rec in zip(rects_to_check, rects_active, rects_hover):
            colr = rect_color if not (hover_rec or actv_rec) else hover_press_colors[color][0] if (hover_rec) else hover_press_colors[color][1]
            pygame.draw.rect(screen, pygame.Color(colr), rec)
        
        screen.blit(texts_rends[0], texts_rects[0])
        for img, imgs_rect, text_rend, text_rect in zip(pieces_imgs.values(), imgs_rects, texts_rends[1:], texts_rects[1:]):
            screen.blit(img, imgs_rect)
            screen.blit(text_rend, text_rect)
        
        pygame.display.flip()

# change the promoted pawn to the user-selected piece
def handle_promotion(events_list, cur_game_state):
    
    board_pieces_index = (events_list[-1][0]//cur_game_state.block_sz[0], events_list[-1][1]//cur_game_state.block_sz[1])
    board_piece = cur_game_state.board_pieces[board_pieces_index]
    color = board_piece.color
    color_index = 0 if color == "black" else 1
    
    # promotion dict makes sure we get the right key for the to_place dict,
    # which initialises the newly promoted piece
    promotion_dict = {
        "queen" : "queen", 
        "rook" : "lrook", 
        "bishop" : "lbishop", 
        "knight" : "lknight"
    }
    
    if board_piece.can_promote:
        prmt_pcs = promotion_dict[select_promotion(cur_game_state.screen, cur_game_state.screen, cur_game_state.res, cur_game_state.clock, 
                                                   cur_game_state.pieces_imgs, color_index)]
        cur_game_state.board_pieces[(board_piece.i, board_piece.j)] = (
            board_piece.to_place[prmt_pcs][2](board_piece.i, board_piece.j, pygame.image.load(board_piece.to_place[prmt_pcs][color_index]).convert_alpha(), 
                                              color, prmt_pcs)
        )
        
        board_piece = cur_game_state.board_pieces[(board_piece.i, board_piece.j)]
        
        piece_offset = ((cur_game_state.block_sz[0]-cur_game_state.pieces_sz_board[0])//2, (cur_game_state.block_sz[1]-cur_game_state.pieces_sz_board[1])//2)
        
        board_piece.rect = board_piece.image.get_rect()
        board_piece.rect.topleft = (board_piece.i * cur_game_state.block_sz[0] + piece_offset[0], board_piece.j * cur_game_state.block_sz[1] + piece_offset[1])
        board_piece.find_moves(cur_game_state)

def draw(cur_game_state):
    for row in cur_game_state.block_list:
        for column in row:
            pygame.draw.rect(cur_game_state.screen, column.color[-1], column.rect)
    if cur_game_state.board_pieces[cur_game_state.white_king_pos].is_checked:
        pygame.draw.rect(cur_game_state.screen, pygame.Color('red'), cur_game_state.block_list[cur_game_state.white_king_pos[1]][cur_game_state.white_king_pos[0]].rect)
    if cur_game_state.board_pieces[cur_game_state.black_king_pos].is_checked:
        pygame.draw.rect(cur_game_state.screen, pygame.Color('red'), cur_game_state.block_list[cur_game_state.black_king_pos[1]][cur_game_state.black_king_pos[0]].rect)
        
    # the offset needed for the pieces to be centered around the square,
    # which is equal to 1/4 of the image size. The board is 8x8 with each
    # square being 100x100 in width x height. The pieces images are 60x60,
    # therefore an offset of 20 is needed for them to be centered in the
    # squares
    img_offset = ((cur_game_state.block_sz[0]-cur_game_state.pieces_sz_board[0])//2, (cur_game_state.block_sz[1]-cur_game_state.pieces_sz_board[1])//2)
    
    for p in cur_game_state.board_pieces:
        board_piece_rect = (cur_game_state.board_pieces[p].i * cur_game_state.block_sz[0] + img_offset[0], 
                            cur_game_state.board_pieces[p].j * cur_game_state.block_sz[1] + img_offset[1])
        cur_game_state.screen.blit(cur_game_state.board_pieces[p].image, board_piece_rect)
        cur_game_state.board_pieces[p].rect = cur_game_state.board_pieces[p].image.get_rect()
        cur_game_state.board_pieces[p].rect.topleft = board_piece_rect

# used to determine whether we have a draw or a checkmate
def num_of_pieces_with_moves(king, cur_game_state):
    pos_of_pieces = cur_game_state.position_of_black_pieces if (king.color == 'black') else cur_game_state.position_of_white_pieces
    pieces = {cur_game_state.board_pieces[pos] for pos in pos_of_pieces}
    count = 0
    for p in pieces:
        if p.moves:
            count += 1
    return count

def active_pieces(board_pieces, pos_of_pieces):
    return {pos : board_pieces[pos] for pos in pos_of_pieces}

def available_pieces(num_of_move, cur_game_state):
    if num_of_move % 2 == 0:
        return active_pieces(cur_game_state.board_pieces, cur_game_state.position_of_white_pieces)
    else:
        return active_pieces(cur_game_state.board_pieces, cur_game_state.position_of_black_pieces)

def is_in_same_diagonal(p1, p2):
    man_dist = manhattam_distance(p1, p2)//2
    if man_dist == abs(p1[0] - p2[0]) and man_dist == abs(p1[1] - p2[1]):
        return True
    return False

def print_available_moves(board_piece, cur_game_state):
    valid_moves = []
    draw_list = []
    opposite_color_pos = cur_game_state.position_of_black_pieces if (board_piece.color == 'white') else cur_game_state.position_of_white_pieces
    for i in board_piece.moves:
        color = pygame.Color('green')
        valid_moves.append(cur_game_state.block_list[i[1]][i[0]])
        if (i[0], i[1]) in opposite_color_pos:
            color = pygame.Color('red')
            #print(board_pieces.keys())
            if (cur_game_state.board_pieces[(i[0], i[1])].name == 'king') and (cur_game_state.board_pieces[(i[0], i[1])].color != board_piece.color):
                valid_moves.pop()
                continue
        draw_list.append((color, cur_game_state.block_list[i[1]][i[0]]))
        #pygame.draw.circle(screen, color, block_list[i[1]][i[0]].rect.center, 10)
    return valid_moves, draw_list

# r is the radius of the circles
# rects is a list of rects next to whom the circles will be drawn,
# which also determines the number of circles to br drawn
# cols is a list of colors indicating whether or not a requirement
# is met, if so the boolean value is True and the color green, else red
# direction is a string among: 'l', 'r', 't', 'b' that each corresponds to
# the respective rect x or y value. 
# sign is an int either -1 or 1 used to configure the sign of the product
# num is an integer used in the multiplication
# colors is a tuple, because python operates with references, if a default argument
# is a list, there is a chance that it might get altered in a function call, something
# not desired. Tuples are immutable ombjects, therefore no such danger exists
def draw_circles(r, rects, cols, screen, direction, sign, num, w=0, colors=("green", "red")):
    
    for rect, req in zip(rects, cols):
        direction_dict = {
            "l" : rect.left,
            "r" : rect.right,
            "t" : rect.top,
            "b" : rect.bottom
        }
        # the diameter of the circle is 2*r, 3*r ensures a space is left between the circle and the rect
        pygame.draw.circle(screen, pygame.Color(colors[0] if req else colors[1]), (direction_dict[direction]+r*sign*num, rect.centery), r, width=w)  

def username_input(cur_game_state, us1, us2, event_list, app_state):
    screen = cur_game_state.screen
    screen_res = cur_game_state.res
    box1_active = app_state.box1_active
    box2_active = app_state.box2_active
    valid_usernames = app_state.valid_usernames
    valid_codes = app_state.valid_codes
    
    username1 = us1
    username2 = us2
    valid1 = (len(username1) < 21) and (len(username1) > 2)
    valid2 = (len(username2) < 21) and (len(username2) > 2)
    valid_usernames = [valid1, valid2]
    rec_w, rec_h = 250, 50
    rec1, rec2 = (pygame.Rect(screen_res[0]*(0.65-0.05*valid_usernames[0]), screen_res[1]*0.3, rec_w, rec_h),             
                pygame.Rect(screen_res[0]*(0.65-0.05*valid_usernames[1]), screen_res[1]*0.3+rec_h*2, rec_w, rec_h))
    
    # -0.05*valid_usernames[0] moves the rect to the left, to make move for the "Sign in" / "Log in" button
    
    font = pygame.font.SysFont("Arial", 20, True)
    
    box1_txt = "Enter name for Player A (plays with White pieces) : "
    box2_txt = "Enter name for Player B (plays with Black pieces) : "
    rend1_txt = font.render(box1_txt, True, pygame.Color("white"))
    rend2_txt = font.render(box2_txt, True, pygame.Color("black"))
    
    rects = [rec1, rec2]
    
    # update
    mouse_pos = pygame.mouse.get_pos()
    
    for evt in event_list:
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_BACKSPACE:
                if box1_active:
                    username1 = username1[:-1]
                elif box2_active:
                    username2 = username2[:-1]
            elif evt.unicode.isalpha() or evt.unicode.isnumeric() or (evt.unicode == " "):
                if box1_active:
                    username1 += evt.unicode
                    username1 = username1[:20]
                elif box2_active:
                    username2 += evt.unicode
                    username2 = username2[:20]
        elif (evt.type == pygame.MOUSEBUTTONDOWN) and (evt.button == 1):
            box1_active = rec1.collidepoint(mouse_pos)
            box2_active = rec2.collidepoint(mouse_pos)
            
    # draw
    screen.fill(pygame.Color("saddlebrown"))
    
    pygame.draw.rect(screen, pygame.Color("white") if (not box1_active) else pygame.Color("gray"), rec1)
    pygame.draw.rect(screen, pygame.Color("white") if (not box2_active) else pygame.Color("gray"), rec2)
    
    bw1, bh1 = font.size(box1_txt)
    bw2, bh2 = font.size(box2_txt)
    screen.blit(rend1_txt, (rec1.left-bw1*1.1, rec1.centery-bh1//2, bw1, bh1))
    screen.blit(rend2_txt, (rec2.left-bw2*1.1, rec2.centery-bh2//2, bw2, bh2))
    
    text1_rend = font.render(username1, True, pygame.Color("black"))
    text2_rend = font.render(username2, True, pygame.Color("black"))
    
    w1, h1 = font.size(username1)
    w2, h2 = font.size(username2)
    screen.blit(text1_rend, (rec1.centerx-w1//2, rec1.centery-h1//2, rec1.w, rec1.h))
    screen.blit(text2_rend, (rec2.centerx-w2//2, rec2.centery-h2//2, rec2.w, rec2.h))
    
    # the circles to the left of the username rects are meant to represent the state
    # of the log in/sign up for each player, red meaning an action is required, green
    # for the opposite
    draw_circles(14, rects, valid_codes, screen, 'l', -1, 2)
    
    # update exit loop variables
                    
    valid1 = (len(username1) < 21) and (len(username1) > 2)
    valid2 = (len(username2) < 21) and (len(username2) > 2)
    valid_usernames = [valid1, valid2]
        
    return username1, username2, valid_usernames, box1_active, box2_active
    
# save_game_data_function is used to store the game data
def play(cur_game_state, game_data):
    
    # main_menu and draw buttons
    main_menu, draw_button = cur_game_state.initialise_game()
    
    exit_condition = None   # if it is assigned any value of -1, 0, 1 the main while loop finishes

    moves = []
    events_list = []
    draw_list = []
    
    block_sz = cur_game_state.block_sz
    
    while exit_condition is None:
        
        cur_game_state.clock.tick(60)
        event_list = pygame.event.get()
        
        for event in event_list:
            
            if event.type == pygame.QUIT:
                cur_game_state.save_game_data(game_data)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                events_list.append(mouse_pos)
                
                if len(events_list) == 1:
                    
                    moves, draw_list = cur_game_state.handle_piece_selection(mouse_pos, events_list)
                        
                if len(events_list) == 2:
                    
                    draw_list = []
                    
                    # moves[2] = bp = board piece => the piece that user moved
                    cur_game_state.execute_move(moves, events_list, block_sz, moves[2])

        if cur_game_state.draw_button_active: draw_button.update(event_list)
        main_menu.update(event_list)
        if main_menu.pressed: return "R"

        exit_condition = cur_game_state.evaluate_game_state(cur_game_state)
        
        cur_game_state.render_game(draw_list, main_menu, draw_button, exit_condition)

        pygame.display.flip()
        
    return exit_condition
    
# side_x_width : the width of the side rect used to display the captured
# pieces and the current player who must make a move 
def try_again(cur_game_state):
    screen = cur_game_state.screen
    end_img = cur_game_state.screen
    res = cur_game_state.res
    side_x_width = cur_game_state.res[0]*0.2
    button_size = (cur_game_state.b_w*1.5, cur_game_state.b_h)
    clock = cur_game_state.clock
    
    dim_surface = pygame.Surface(res, pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 25))
    end_img.blit(dim_surface, (0, 0))
    end_screen = pygame.Surface(res)
    end_screen.blit(end_img, (0,0))
    
    main_menu = Button((res[0]-side_x_width//2) - button_size[0]//2, res[1]-button_size[1]*2, *button_size, "Main Menu", lambda : None)
    play_again = Button(main_menu.rect.left, main_menu.rect.top-button_size[1]*2, *button_size, "Play Again", lambda : None)
    
    while True:
        
        clock.tick(60)
        screen.fill(pygame.Color("saddlebrown"))
        
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                return -1
        
        if main_menu.pressed:
            return 0
        if play_again.pressed:
            return 1
        
        screen.blit(end_screen, (0,0))
        main_menu.update(events)
        play_again.update(events)
        
        main_menu.draw(screen)
        play_again.draw(screen)
        
        pygame.display.flip()
