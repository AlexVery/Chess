import pickle
import pygame
import sys
import math
from button import *
from helper_functions import *

data_file_name = "chess_game_data"

# game_data is supposed to be a dictionary holding the game_data information.
# For illustrative purposes the dictionary looks like this:
# {
#   "AlexBatmanFan2" : {
#   "password" : "Example!Password",
#   "games_played" : 13,
#   "games_won" : 8,
#   "games_lost" : 2,
#   "games_drawn" : 3,        ! important : the sum of the games won, lost and drawn must equal the total games played
#   "W %" : 0.615 (8/13),
#   "H2H" : {               ! this dictionary stores the head to head statistics against players and usernames are used as dictionary keys
#       "Bob23" : {
#           "games_played" : 4,
#           "games_won" : 2,
#           ...
#           },   => the dict holds the game info data against each opponent, similar to the main dict
#       ...
#       }
#   },
#   ...
# }


def register_user(username, game_data, cur_game_state):
    end_screen = cur_game_state.screen
    screen = cur_game_state.screen
    res = cur_game_state.res
    clock = cur_game_state.clock

    user_data = {
        "password": "",
        "games_played": 0,
        "games_won": 0,
        "games_lost": 0,
        "games_drawn": 0,
        "W %": 0.0,
        "H2H": {},
    }

    dim_surface = pygame.Surface(res, pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 150))
    end_screen.blit(dim_surface, (0, 0))
    end_img = pygame.Surface(res)
    end_img.blit(end_screen, (0, 0))
    rect_sz = res[0] // 2, res[1] * 0.75
    rect = pygame.Rect(
        res[0] // 2 - rect_sz[0] // 2, res[1] // 2 - rect_sz[1] // 2, *rect_sz
    )
    input_rect_sz = (350, 50)

    password_valid = False
    return_to_menu = False
    box1_active = False
    box2_active = False
    password = ""
    password_conf = ""
    show_password = False
    show_password_conf = False

    font_title = pygame.font.SysFont("Arial", 24, True)
    font_text = pygame.font.SysFont("Arial", 16, True)
    text_rend_space = font_text.size("A")
    tab_rend_width = text_rend_space[0] * 4  # normally the tab = 4 space characters
    # calculate the tab space for the specific font size so that the text appears indented:
    # Password Requirements:
    #   At least 8 characters long, ...

    texts = [
        "Sign up",
        "Password Requirements:",
        "At least 8 characters long",
        "At most 20 characters long",
        "At least 3 of the following:",
        "An uppercase letter e.g. A",
        "A lowercase letter e.g. b",
        "A number (0-9)",
        "A symbol among the following: !, @, #, $, and %",
        "Confirm password",
    ]

    font_texts = [font_title] + [font_text] * (
        len(texts) - 1
    )  # avoids writing [font_title, font_text, font_text, ...]
    text_identation = [0, 0, 1, 1, 1, 2, 2, 2, 2, 0]  # 1 means indented by one tab

    texts_rends = [
        font.render(text, True, pygame.Color("white"))
        for font, text in zip(font_texts, texts)
    ]
    texts_rects = [
        pygame.Rect(
            rect.centerx - texts_rends[0].get_width() // 2,
            rect.top + texts_rends[0].get_height() * 1.25,
            *texts_rends[0].get_size(),
        )
    ]

    for i in range(1, len(texts_rends) - 1):
        texts_rects.append(
            pygame.Rect(
                rect.left + 0.05 * rect.width + text_identation[i] * tab_rend_width,
                texts_rects[i - 1].bottom + text_rend_space[1],
                *text_rend_space,
            )
        )

    rect1 = pygame.Rect(
        rect.centerx - input_rect_sz[0] // 2,
        texts_rects[-1].bottom + input_rect_sz[1],
        *input_rect_sz,
    )
    texts_rects.append(
        pygame.Rect(
            rect.centerx - texts_rends[-1].get_width() // 2,
            rect1.bottom + texts_rends[-1].get_height(),
            *texts_rends[-1].get_size(),
        )
    )

    rect2 = pygame.Rect(
        rect.centerx - input_rect_sz[0] // 2,
        rect.bottom - 2 * input_rect_sz[1],
        *input_rect_sz,
    )
    input_rects = [rect1, rect2]

    # rect 3 and 4 are responsible for the visibility of the password, pressing them displays/hides
    # the password
    rect3 = pygame.Rect(
        rect1.right + input_rect_sz[1] * 0.25,
        rect1.top,
        input_rect_sz[1],
        input_rect_sz[1],
    )
    rect3_hover = False
    rect4 = pygame.Rect(
        rect2.right + input_rect_sz[1] * 0.25,
        rect2.top,
        input_rect_sz[1],
        input_rect_sz[1],
    )
    rect4_hover = False

    symbols_allowed = {"!", "@", "#", "$", "%"}
    # using lambdas is a good way of passing an argument, in this case the password and checking
    # whether the necessary requirements are met
    password_requirements = [
        lambda x: len(x) > 7,
        lambda x: len(x) < 21,
        lambda x: any([char.isupper() for char in x]),
        lambda x: any([char.islower() for char in x]),
        lambda x: any([char.isdigit() for char in x]),
        lambda x: any([char in symbols_allowed for char in x]),
    ]
    # x and y ensures that both passwords are not blank

    password_requirements_met = [False for _ in range(len(password_requirements) + 1)]

    password_texts = [password, password_conf]
    password_rends = [
        font_title.render(passwrd, True, pygame.Color("black"))
        for passwrd in password_texts
    ]
    password_hide_rends = [
        font_title.render(len(passwrd) * "*", True, pygame.Color("black"))
        for passwrd in password_texts
    ]
    password_rends = [
        [pass1, pass2] for pass1, pass2 in zip(password_hide_rends, password_rends)
    ]
    password_rects = [
        [
            pygame.Rect(
                pass_rect.centerx - pswrd_rend.get_width() // 2,
                pass_rect.centery - pswrd_rend.get_height() // 2,
                *pswrd_rend.get_size(),
            )
            for pass_rect, pswrd_rend in zip(input_rects, password_rend)
        ]
        for password_rend in password_rends
    ]

    password_check = lambda x, y: (len(x) > 0) and (x == y)

    buttons_sz = (150, 50)
    back_button = Button(
        rect.left, rect.bottom, buttons_sz[0], buttons_sz[1], "Return", lambda: None
    )
    confirm_button = Button(
        rect.right - buttons_sz[0],
        rect.bottom,
        buttons_sz[0],
        buttons_sz[1],
        "Confirm",
        lambda: None,
    )

    while (not password_valid) and (not return_to_menu):
        clock.tick(60)
        screen.fill(0)
        screen.blit(end_img, (0, 0))

        events = pygame.event.get()

        # update
        mouse_pos = pygame.mouse.get_pos()
        rect3_hover = rect3.collidepoint(mouse_pos)
        rect4_hover = rect4.collidepoint(mouse_pos)
        password_requirements_met1 = [pr(password) for pr in password_requirements] + [
            password_check(password, password_conf)
        ]

        back_button.update(events)

        password_requirements_met = (
            password_requirements_met1[:2]
            + [sum(password_requirements_met1[2:]) >= 3]
            + password_requirements_met1[2:]
        )
        if sum(password_requirements_met[:3] + [password_requirements_met[-1]]) == 4:
            user_data["password"] = password
            confirm_button.update(events)
            confirm_button.draw(screen)

        if any([confirm_button.pressed, back_button.pressed]):
            return confirm_button.pressed, back_button.pressed, user_data

        password_texts = [password, password_conf]
        password_rends = [
            font_title.render(passwrd, True, pygame.Color("black"))
            for passwrd in password_texts
        ]
        password_hide_rends = [
            font_title.render(len(passwrd) * "*", True, pygame.Color("black"))
            for passwrd in password_texts
        ]
        password_rends = [
            [pass1, pass2] for pass1, pass2 in zip(password_hide_rends, password_rends)
        ]
        # because we want the first rect for both the "*" and the normal format of the first password
        # and the second for the second, so the list looks like this:
        # password_rends = [["*****", "12@aA"], ["*****", "12@aA"]]
        # password_rects = [[rect 1 centered around the "*" format of the password, rect 1 centered around the "12@aA" format of the password],
        #                   [rect 2 centered arounf the "*" format of the confirm password, rect 2 centered around the "12@aA" format of the confirm password]]
        password_rects = [
            [
                pygame.Rect(
                    input_rects[i].centerx - pswrd_rend.get_width() // 2,
                    input_rects[i].centery - pswrd_rend.get_height() // 2,
                    *pswrd_rend.get_size(),
                )
                for pswrd_rend in password_rend
            ]
            for i, password_rend in enumerate(password_rends)
        ]

        for event in events:
            if event.type == pygame.QUIT:
                save_game_data(game_data)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if box1_active:
                        password = password[:-1]
                    elif box2_active:
                        password_conf = password_conf[:-1]
                elif (
                    event.unicode.isdigit()
                    or event.unicode.isalpha()
                    or (event.unicode in symbols_allowed)
                ):
                    if box1_active:
                        password += event.unicode
                        password = password[:20]
                    elif box2_active:
                        password_conf += event.unicode
                        password_conf = password_conf[:20]
            elif (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
                box1_active = rect1.collidepoint(mouse_pos)
                box2_active = rect2.collidepoint(mouse_pos)
                if rect3_hover:
                    show_password = not show_password
                if rect4_hover:
                    show_password_conf = not show_password_conf
        # draw
        back_button.draw(screen)

        pygame.draw.rect(screen, pygame.Color("black"), rect)
        pygame.draw.rect(
            screen, pygame.Color("white" if not box2_active else "gray"), rect2
        )
        pygame.draw.rect(
            screen, pygame.Color("white" if not box1_active else "gray"), rect1
        )

        for trend, trect in zip(texts_rends, texts_rects):
            screen.blit(trend, trect)

        # indx takes the values of show_password and show_password_conf, a value of 0 means the "*" format
        # will be used, else a value of 1 shows the actual password
        for i, indx in enumerate([show_password, show_password_conf]):
            screen.blit(password_rends[i][indx], password_rects[i][indx])

        draw_circles(10, texts_rects[2:], password_requirements_met, screen, "l", -1, 3)

        # show/hide icons for password and confirm password
        draw_circles(
            rect3.width // 4,
            [rect3],
            [not rect3_hover],
            screen,
            "l",
            1,
            2,
            w=4,
            colors=("white", "white"),
        )
        pygame.draw.arc(
            screen, pygame.Color("white"), rect3, math.pi * 2, math.pi, width=5
        )
        if not show_password:
            pygame.draw.line(
                screen, pygame.Color("white"), rect3.topleft, rect3.bottomright, width=4
            )

        draw_circles(
            rect4.width // 4,
            [rect4],
            [not rect4_hover],
            screen,
            "l",
            1,
            2,
            w=4,
            colors=("white", "white"),
        )
        pygame.draw.arc(
            screen, pygame.Color("white"), rect4, math.pi * 2, math.pi, width=5
        )
        if not show_password_conf:
            pygame.draw.line(
                screen, pygame.Color("white"), rect4.topleft, rect4.bottomright, width=4
            )

        pygame.display.flip()


def log_in_user(username, game_data, cur_game_state):
    end_screen = cur_game_state.screen
    screen = cur_game_state.screen
    res = cur_game_state.res
    clock = cur_game_state.clock

    dim_surface = pygame.Surface(res, pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 150))
    end_screen.blit(dim_surface, (0, 0))
    end_img = pygame.Surface(res)
    end_img.blit(end_screen, (0, 0))
    rect_sz = res[0] // 2, res[1] * 0.35
    rect = pygame.Rect(
        res[0] // 2 - rect_sz[0] // 2, res[1] // 2 - rect_sz[1] // 2, *rect_sz
    )
    input_rect_sz = (350, 50)

    password_valid = False
    return_to_menu = False
    box1_active = False
    password = ""
    show_password = False

    font_title = pygame.font.SysFont("Arial", 24, True)
    font_text = pygame.font.SysFont("Arial", 16, True)
    text_rend_space = font_text.size("A")

    texts = ["Log in", "Type in the password for  " + "'" + username + "'"]
    font_texts = [font_title] + [font_text] * (
        len(texts) - 1
    )  # avoids writing [font_title, font_text, font_text, ...]
    texts_rends = [
        font.render(text, True, pygame.Color("white"))
        for font, text in zip(font_texts, texts)
    ]
    texts_rects = [
        pygame.Rect(
            rect.centerx - texts_rends[0].get_width() // 2,
            rect.top + texts_rends[0].get_height() * 1.25,
            *texts_rends[0].get_size(),
        )
    ]
    for i in range(1, len(texts_rends)):
        texts_rects.append(
            pygame.Rect(
                rect.centerx - texts_rends[i].get_width() // 2,
                texts_rects[i - 1].bottom + text_rend_space[1] * 2,
                *text_rend_space,
            )
        )

    rect1 = pygame.Rect(
        rect.centerx - input_rect_sz[0] // 2,
        texts_rects[-1].bottom + input_rect_sz[1],
        *input_rect_sz,
    )
    # rect2 is supposed to be the placeholder for the show/hide password icon and is used to check for
    # possible collision with the mouse (this determines the icon's color)
    rect2 = pygame.Rect(
        rect1.right + input_rect_sz[1] * 0.25,
        rect1.top,
        input_rect_sz[1],
        input_rect_sz[1],
    )
    rect2_hover = False

    password_rends = [
        font_title.render(passwrd, True, pygame.Color("black"))
        for passwrd in ["*" * len(password), password]
    ]
    password_rects = [
        pygame.Rect(
            rect1.centerx - pswrd_rend.get_width() // 2,
            rect1.centery - pswrd_rend.get_height() // 2,
            *pswrd_rend.get_size(),
        )
        for pswrd_rend in password_rends
    ]

    buttons_sz = (150, 50)
    back_button = Button(
        rect.left, rect.bottom, buttons_sz[0], buttons_sz[1], "Return", lambda: None
    )
    confirm_button = Button(
        rect.right - buttons_sz[0],
        rect.bottom,
        buttons_sz[0],
        buttons_sz[1],
        "Confirm",
        lambda: None,
    )

    symbols_allowed = {"!", "@", "#", "$", "%"}
    stored_password = game_data[username]["password"]

    while (not password_valid) and (not return_to_menu):
        clock.tick(60)
        screen.fill(0)
        screen.blit(end_img, (0, 0))

        events = pygame.event.get()

        # update
        mouse_pos = pygame.mouse.get_pos()
        rect2_hover = rect2.collidepoint(mouse_pos)

        back_button.update(events)

        if password == stored_password:
            confirm_button.update(events)
            confirm_button.draw(screen)

        if any([confirm_button.pressed, back_button.pressed]):
            return confirm_button.pressed, back_button.pressed, game_data[username]

        password_rends = [
            font_title.render(passwrd, True, pygame.Color("black"))
            for passwrd in ["*" * len(password), password]
        ]
        password_rects = [
            pygame.Rect(
                rect1.centerx - pswrd_rend.get_width() // 2,
                rect1.centery - pswrd_rend.get_height() // 2,
                *pswrd_rend.get_size(),
            )
            for pswrd_rend in password_rends
        ]

        for event in events:
            if event.type == pygame.QUIT:
                save_game_data(game_data)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if box1_active:
                        password = password[:-1]
                elif (
                    event.unicode.isdigit()
                    or event.unicode.isalpha()
                    or (event.unicode in symbols_allowed)
                ):
                    if box1_active:
                        password += event.unicode
                        password = password[:20]
            elif (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
                box1_active = rect1.collidepoint(mouse_pos)
                if rect2_hover:
                    show_password = not show_password

        # draw
        back_button.draw(screen)

        pygame.draw.rect(screen, pygame.Color("black"), rect)
        pygame.draw.rect(
            screen, pygame.Color("white" if not box1_active else "gray"), rect1
        )

        for trend, trect in zip(texts_rends, texts_rects):
            screen.blit(trend, trect)

        # for pass_rend, pass_rect in zip(password_rends, password_rects):
        screen.blit(password_rends[show_password], password_rects[0])

        # hide/show password icon
        draw_circles(
            rect2.width // 4,
            [rect2],
            [not rect2_hover],
            screen,
            "l",
            1,
            2,
            w=4,
            colors=("white", "white"),
        )
        pygame.draw.arc(
            screen, pygame.Color("white"), rect2, math.pi * 2, math.pi, width=5
        )
        if not show_password:
            pygame.draw.line(
                screen, pygame.Color("white"), rect2.topleft, rect2.bottomright, width=4
            )

        pygame.display.flip()


def handle_username_password(username, game_data, cur_game_state):
    if username not in game_data:
        return register_user(username, game_data, cur_game_state)
    else:
        return log_in_user(username, game_data, cur_game_state)


def save_game_data(game_data):
    with open(data_file_name, "wb") as f:
        pickle.dump(game_data, f)


def open_game_data():
    with open(data_file_name, "rb") as f:
        game_file = pickle.load(f)
        return game_file
