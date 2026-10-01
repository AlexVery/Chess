from helper_functions import *
import copy


class piece:
    def __init__(self, image, color, name, i, j):
        self.i, self.j = i, j
        self.image = image
        self.color = color
        self.name = name
        self.moves = set()
        self.is_king_in_moves = False
        self.can_promote = False
        self.moved = False

    # check_is_king_in_moves checks whether the enemy king is within the piece's moves
    # and stores the result in a boolean variable
    def check_is_king_in_moves(self, op_king_pos):
        if op_king_pos in self.moves:
            self.is_king_in_moves = True
        else:
            self.is_king_in_moves = False

    def add_moves(self, moves_to_check, pos_to_avoid, pos_to_stop):
        for pd in moves_to_check:
            for move in pd:
                if (0 <= move[0] < 8) and (0 <= move[1] < 8):
                    if move not in pos_to_avoid:
                        self.moves.add(move)
                        if move in pos_to_stop:
                            break
                    elif move in pos_to_avoid:
                        self.protected.add(move)
                        break

    def snapshot(self):
        # fields that make/unmake-move logic can mutate; subclasses extend this
        immutable_fields = (
            "i",
            "j",
            "moved",
            "can_promote",
            "is_checked",
            "done_castling",
            "step_counter",
            "en_passant_turn_count",
            "en_passant_move",
            "is_king_in_moves",
        )
        mutable_fields = ("moves", "protected", "optional_moves")
        return {f: getattr(self, f) for f in immutable_fields if hasattr(self, f)} | {
            f: getattr(self, f).copy() for f in mutable_fields if hasattr(self, f)
        }

    def restore(self, snap):
        for f, v in snap.items():
            setattr(self, f, v)

    # dummy function, useful to maintain readeability in the code
    def promote(self):
        pass

    def get_valid_moves(self, moves, cur_game_state):
        pos_white = cur_game_state.position_of_white_pieces
        pos_black = cur_game_state.position_of_black_pieces
        same_color_pieces = pos_white if (self.color == "white") else pos_black
        valid_moves = set()
        for direction in moves:
            for move in direction:
                if (
                    (move not in same_color_pieces)
                    and (0 <= move[0] < 8)
                    and (0 <= move[1] < 8)
                ):
                    valid_moves.add(move)
        return valid_moves

    # handle_move makes the move and stores the necessary data, while making
    # changes to important data structures (like the two sets containing the
    # positions of each color's pieces)
    # bpc = board_pieces copy, scp = current piece,
    # pbp = positions of black pieces, pwp = position of white pieces

    def undo_move(self, scp, move, cur_game_state, undo_dict):
        position_of_same_color_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        position_of_opposite_color_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        position_of_same_color_pieces.remove(scp)

        position_of_same_color_pieces.add(move)

        if undo_dict["captured"] is not None:
            position_of_opposite_color_pieces.add(scp)

    def handle_move(self, scp, move, cur_game_state):
        position_of_same_color_pieces = (
            cur_game_state.position_of_black_pieces
            if (cur_game_state.board_pieces[scp].color == "black")
            else cur_game_state.position_of_white_pieces
        )
        position_of_opposite_color_pieces = (
            cur_game_state.position_of_black_pieces
            if (cur_game_state.board_pieces[scp].color == "white")
            else cur_game_state.position_of_white_pieces
        )
        position_of_same_color_pieces.remove(
            (cur_game_state.board_pieces[scp].i, cur_game_state.board_pieces[scp].j)
        )
        set_move(cur_game_state.board_pieces[scp], *move)
        board_pieces_index = move

        if board_pieces_index in position_of_opposite_color_pieces:
            position_of_opposite_color_pieces.remove(board_pieces_index)
        position_of_same_color_pieces.add(move)
        cur_game_state.board_pieces[board_pieces_index] = cur_game_state.board_pieces[
            scp
        ]
        del cur_game_state.board_pieces[scp]

    def change_move(self, scp, move, cur_game_state):
        undo_dict = {"from": scp, "to": move, "captured": None}

        position_of_same_color_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        position_of_opposite_color_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        position_of_same_color_pieces.remove(scp)
        board_pieces_index = move

        if board_pieces_index in position_of_opposite_color_pieces:
            undo_dict["captured"] = board_pieces_index
            position_of_opposite_color_pieces.remove(board_pieces_index)
        position_of_same_color_pieces.add(move)

        return undo_dict

    def remove_reveal_king_moves(self, count, cur_game_state):
        # the king's moves should not get altered , ONLY the rest of the pieces determine
        # whether a move reveals the king and thus should be deleted, as it is not valid
        if self.name == "king":
            return

        color = "black" if (count % 2 != 0) else "white"

        scp = self.i, self.j
        remove_list = []
        copied_state = cur_game_state
        same_color_king = (
            cur_game_state.white_king_pos
            if (color == "white")
            else cur_game_state.black_king_pos
        )

        for move in copy.copy(self.moves):
            bpc = copied_state.board_pieces  # bcp = board_pieces copy

            undo_dict = self.change_move(scp, move, copied_state)
            dif_color_pieces = (
                cur_game_state.position_of_black_pieces
                if (self.color != "black")
                else cur_game_state.position_of_white_pieces
            )

            for board_piece in dif_color_pieces:
                if bpc[board_piece].color == color:
                    continue
                attacks_king = bpc[board_piece].attacks_square(
                    same_color_king, cur_game_state
                )
                if attacks_king:
                    remove_list.append((scp, move))

            self.undo_move(move, scp, copied_state, undo_dict)

        for scp, move in remove_list:
            cur_game_state.board_pieces[scp].moves.discard(move)


class pawn(piece):
    def __init__(
        self, i, j, image, color, name, to_place_dict
    ):  # i, j denote the position in the 2d list of blocks/rects
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

    def capture_en_passant(self, difx, dify, cur_game_state, move, count):
        return (
            (difx == 1)
            and (dify == 1)
            and (abs(count - self.en_passant_turn_count) == 1)
        )

    def handle_en_passant(self, cur_game_state, move, dif_y, count):
        # a list of tuples: the first part of each tuple is the position of the pawn eligible to perform
        # the en passant move, the second is the position it will end up if the move is made and the last
        # is the position of the captured pawn
        return_moves = []

        if dif_y == 2:
            pieces_to_use = (
                cur_game_state.position_of_black_pieces
                if (self.color == "white")
                else cur_game_state.position_of_white_pieces
            )
            pawns_to_check = {
                pos
                for pos in pieces_to_use
                if cur_game_state.board_pieces[pos].name == "pawn"
            }

            # if the current pawn moving two squares from its initial position is black, then
            # the y_offset for the opposite color pawns must be -1, because they are moving from
            # y = 6 (max is 7, because the board is 8x8, thus 0-7 indexed for both the x and y
            # axis) to y = 0. For the black pieces the movement is the opposite, moving from
            # y = 1 to y = 7. The y_offset must be opposite to the relative of the movement of the
            # enemy pawn. This function acts as a trigger for the neighbouring opposite pawn,
            # enabling them to perform the en passant move
            y_offset = -1 if (self.color == "black") else 1
            # positions to check for possible en passant available pawns
            pos_left = (move[0] - 1, move[1])
            pos_right = (move[0] + 1, move[1])

            if pos_left[0] > 0:
                if pos_left in pawns_to_check:
                    return_moves.append(
                        (pos_left, (move[0], move[1] + y_offset), (move))
                    )
            if pos_right[0] < 8:
                if pos_right in pawns_to_check:
                    return_moves.append(
                        (pos_right, (move[0], move[1] + y_offset), (move))
                    )

        return return_moves

    def attacks_square(self, square, cur_game_state):
        possible_moves = (
            [(-1, -1), (1, -1)] if (self.color != "black") else [(-1, 1), (1, 1)]
        )
        moves_to_check = [
            (self.i + move_x, self.j + move_y) for (move_x, move_y) in possible_moves
        ]
        valid_moves = self.get_valid_moves([moves_to_check], cur_game_state)
        return square in valid_moves

    def find_moves(self, cur_game_state):
        self.moves.clear()
        self.protected.clear()
        self.important_moves.clear()
        op_king_pos = (
            cur_game_state.black_king_pos
            if (self.color == "white")
            else cur_game_state.white_king_pos
        )

        if self.color == "black":
            if self.j + 1 <= 7:
                if (
                    self.i,
                    self.j + 1,
                ) not in cur_game_state.position_of_white_pieces and (
                    (self.i, self.j + 1) not in cur_game_state.position_of_black_pieces
                ):
                    self.moves.add((self.i, self.j + 1))
                    if (
                        (self.j == 1)
                        and (
                            (self.i, self.j + 2)
                            not in cur_game_state.position_of_white_pieces
                        )
                        and (
                            (self.i, self.j + 2)
                            not in cur_game_state.position_of_black_pieces
                        )
                    ):
                        self.moves.add((self.i, self.j + 2))
                        self.optional_moves.add((self.i, self.j + 2))

                if (self.i + 1 <= 7) and (
                    (self.i + 1, self.j + 1)
                    not in cur_game_state.position_of_black_pieces
                ):
                    if (
                        self.i + 1,
                        self.j + 1,
                    ) in cur_game_state.position_of_white_pieces:
                        self.moves.add((self.i + 1, self.j + 1))
                    self.important_moves.add((self.i + 1, self.j + 1))

                if (self.i - 1 >= 0) and (
                    (self.i - 1, self.j + 1)
                    not in cur_game_state.position_of_black_pieces
                ):
                    if (
                        self.i - 1,
                        self.j + 1,
                    ) in cur_game_state.position_of_white_pieces:
                        self.moves.add((self.i - 1, self.j + 1))
                    self.important_moves.add((self.i - 1, self.j + 1))

            if (
                (self.i + 1 <= 7)
                and (self.j + 1 <= 7)
                and (
                    (self.i + 1, self.j + 1) in cur_game_state.position_of_black_pieces
                )
            ):
                self.protected.add((self.i + 1, self.j + 1))
            if (
                (self.i - 1 >= 0)
                and (self.j + 1 <= 7)
                and (
                    (self.i - 1, self.j + 1) in cur_game_state.position_of_black_pieces
                )
            ):
                self.protected.add((self.i - 1, self.j + 1))
        elif self.color == "white":
            if self.j - 1 >= 0:
                if (
                    (self.i, self.j - 1) not in cur_game_state.position_of_black_pieces
                ) and (
                    (self.i, self.j - 1) not in cur_game_state.position_of_white_pieces
                ):
                    self.moves.add((self.i, self.j - 1))
                    if (
                        (self.j == 6)
                        and (
                            (self.i, self.j - 2)
                            not in cur_game_state.position_of_black_pieces
                        )
                        and (
                            (self.i, self.j - 2)
                            not in cur_game_state.position_of_white_pieces
                        )
                    ):
                        self.moves.add((self.i, self.j - 2))
                        self.optional_moves.add((self.i, self.j - 2))

                if (self.i + 1 <= 7) and (
                    (self.i + 1, self.j - 1)
                    not in cur_game_state.position_of_white_pieces
                ):
                    if (
                        self.i + 1,
                        self.j - 1,
                    ) in cur_game_state.position_of_black_pieces:
                        self.moves.add((self.i + 1, self.j - 1))
                    self.important_moves.add((self.i + 1, self.j - 1))

                if (self.i - 1 >= 0) and (
                    (self.i - 1, self.j - 1)
                    not in cur_game_state.position_of_white_pieces
                ):
                    if (
                        self.i - 1,
                        self.j - 1,
                    ) in cur_game_state.position_of_black_pieces:
                        self.moves.add((self.i - 1, self.j - 1))
                    self.important_moves.add((self.i - 1, self.j - 1))

            if (
                (self.i + 1 <= 7)
                and (self.j - 1 >= 0)
                and (
                    (self.i + 1, self.j - 1) in cur_game_state.position_of_white_pieces
                )
            ):
                self.protected.add((self.i + 1, self.j - 1))
            if (
                (self.i - 1 >= 0)
                and (self.j - 1 >= 0)
                and (
                    (self.i - 1, self.j - 1) in cur_game_state.position_of_white_pieces
                )
            ):
                self.protected.add((self.i - 1, self.j - 1))

        self.check_is_king_in_moves(op_king_pos)
        # remove_moves(self, black_king_pos, white_king_pos, position_of_black_pieces, position_of_white_pieces, board_pieces)


class king(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        self.is_checked = False
        self.done_castling = False
        self.step_counter = 0  # to track the number of moves, it is vital to the castling calculation, any step
        # counter larger than 1, results in the castling being classified as invalid (must
        # be the first king's move)
        self.castling = {
            "white": {
                "left_rook_pos": (7, 7),
                "right_rook_pos": (0, 7),
                "left_castling_pos": (6, 7),
                "right_castling_pos": (2, 7),
                "left_pos_to_check": [(4, 7), (5, 7), (6, 7)],
                "right_pos_to_check": [(4, 7), (3, 7), (2, 7)],
                "left_rook_castling_pos": (5, 7),
                "right_rook_castling_pos": (3, 7),
            },
            "black": {
                "left_rook_pos": (7, 0),
                "right_rook_pos": (0, 0),
                "left_castling_pos": (6, 0),
                "right_castling_pos": (2, 0),
                "left_pos_to_check": [(4, 0), (5, 0), (6, 0)],
                "right_pos_to_check": [(4, 0), (3, 0), (2, 0)],
                "left_rook_castling_pos": (5, 0),
                "right_rook_castling_pos": (3, 0),
            },
        }

        self.directions = [
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
        ]

    def change_rook_castling(self, cur_game_state, move):

        # perform the castling move for the respective rook, only if the move (king move) is either
        # the left or the right king castling move

        castling = self.castling[self.color]

        if (move == castling["left_castling_pos"]) and (
            self.step_counter == 1
        ):  # and (move in board_pieces) ensures the piece hasn't been captured yet
            self.handle_move(
                castling["left_rook_pos"],
                castling["left_rook_castling_pos"],
                cur_game_state,
            )
        if (move == castling["right_castling_pos"]) and (self.step_counter == 1):
            self.handle_move(
                castling["right_rook_pos"],
                castling["right_rook_castling_pos"],
                cur_game_state,
            )

    def remove_invalid_castling_moves(self, cur_game_state):
        pos_to_avoid = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        pos_to_stop = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        non_available_moves = {
            cur_game_state.board_pieces[i[0], i[1]]
            for i in pos_to_stop
            if cur_game_state.board_pieces[i[0], i[1]].name != "king"
        }

        if not self.moved:
            # get the castling dict according to the king's color
            castling = self.castling[self.color]

            # a list containig two individual lists that hold the positions we have to check
            # for the left and right castling respectively. A castling move is only valid if
            # the king doesn't leave, cross over or end up in a square attacked by enemy pieces.
            # Neither the king nor the respective rook must have moved and the squares between
            # them are empty
            castling_pos = [
                castling["left_pos_to_check"],
                castling["right_pos_to_check"],
            ]

            left_castling_pos, right_castling_pos = castling_pos

            check_left_empty = all(
                [
                    (pos not in pos_to_stop) and (pos not in pos_to_avoid)
                    for pos in left_castling_pos
                    if (pos != (self.i, self.j))
                ]
            )
            check_right_empty = all(
                [
                    (pos not in pos_to_stop) and (pos not in pos_to_avoid)
                    for pos in right_castling_pos
                    if (pos != (self.i, self.j))
                ]
            )

            check_left_not_attacked = all(
                [
                    all(
                        [
                            (
                                pos
                                not in (
                                    bp.moves
                                    if (bp.name != "pawn")
                                    else bp.important_moves
                                )
                            )
                            for pos in left_castling_pos
                        ]
                    )
                    for bp in non_available_moves
                ]
            )
            check_right_not_attacked = all(
                [
                    all(
                        [
                            (
                                pos
                                not in (
                                    bp.moves
                                    if (bp.name != "pawn")
                                    else bp.important_moves
                                )
                            )
                            for pos in right_castling_pos
                        ]
                    )
                    for bp in non_available_moves
                ]
            )

            left_castling_valid = check_left_empty and check_left_not_attacked
            right_castling_valid = check_right_empty and check_right_not_attacked

            if self.is_checked:
                self.moves.discard(castling["left_castling_pos"])
                self.moves.discard(castling["right_castling_pos"])

            if not left_castling_valid:
                self.moves.discard(castling["left_castling_pos"])

            if not right_castling_valid:
                self.moves.discard(castling["right_castling_pos"])

    def attacks_square(self, square, cur_game_state):
        moves_to_check = [
            (self.i + move_x, self.j + move_y) for (move_x, move_y) in self.directions
        ]
        valid_moves = self.get_valid_moves([moves_to_check], cur_game_state)
        return square in valid_moves

    def handle_castling_move(self, cur_game_state):
        # handle castling
        if not self.moved:
            # get the castling dict according to the king's color
            castling = self.castling[self.color]

            left_rook = cur_game_state.board_pieces.get(castling["left_rook_pos"])
            right_rook = cur_game_state.board_pieces.get(castling["right_rook_pos"])
            # a list containig two individual lists that hold the positions we have to check
            # for the left and right castling respectively. A castling move is only valid if
            # the king doesn't leave, cross over or end up in a square attacked by enemy pieces.
            # Neither the king nor the respective rook must have moved and the squares between
            # them are empty

            if (
                (left_rook is not None)
                and (left_rook.name == "lrook")
                and (not left_rook.moved)
            ):
                self.moves.add(castling["left_castling_pos"])
            if (
                (right_rook is not None)
                and (right_rook.name == "rrook")
                and (not right_rook.moved)
            ):
                self.moves.add(castling["right_castling_pos"])

            self.remove_invalid_castling_moves(cur_game_state)

    def find_moves(self, cur_game_state):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        pos_to_stop = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        non_available_moves = {
            cur_game_state.board_pieces[i[0], i[1]] for i in pos_to_stop
        }

        self.handle_castling_move(cur_game_state)

        possible_moves = [
            (move_x + self.i, move_y + self.j) for (move_x, move_y) in self.directions
        ]

        for pm in possible_moves:
            if (0 <= pm[0] < 8) and (0 <= pm[1] < 8):
                if pm not in pos_to_avoid:
                    undo_dict = self.change_move((self.i, self.j), pm, cur_game_state)
                    for nam in non_available_moves:
                        attacks_king = nam.attacks_square(pm, cur_game_state)
                        if attacks_king:
                            break
                    else:
                        self.moves.add(pm)
                    self.undo_move(pm, (self.i, self.j), cur_game_state, undo_dict)
                elif pm in pos_to_avoid:
                    self.protected.add(pm)


class queen(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        self.directions = (
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
        )

    def attacks_square(self, square, cur_game_state):
        possible_moves = [
            [(j * i[0], j * i[1]) for j in range(1, 8)] for i in self.directions
        ]
        moves_to_check = [
            [(self.i + move_x, self.j + move_y) for (move_x, move_y) in direction]
            for direction in possible_moves
        ]
        enemy_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        friend_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        moves_to_keep = []
        for direction in moves_to_check:
            for i, move in enumerate(direction):
                if move in enemy_pieces:
                    moves_to_keep.append(direction[: i + 1])
                    break
                if move in friend_pieces:
                    moves_to_keep.append(direction[:i])
                    break
            else:
                moves_to_keep.append(direction)
        valid_moves = self.get_valid_moves(moves_to_keep, cur_game_state)
        # print(self.name, self.color, self.i, self.j, valid_moves, square)
        return square in valid_moves

    def find_moves(self, cur_game_state):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        pos_to_stop = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        op_king_pos = (
            cur_game_state.black_king_pos
            if (self.color == "white")
            else cur_game_state.white_king_pos
        )

        possible_moves = [
            [(j * i[0], j * i[1]) for j in range(1, 8)] for i in self.directions
        ]
        moves_to_check = [
            [(self.i + move_x, self.j + move_y) for (move_x, move_y) in direction]
            for direction in possible_moves
        ]

        self.add_moves(moves_to_check, pos_to_avoid, pos_to_stop)

        self.check_is_king_in_moves(op_king_pos)


class rook(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        self.directions = ((1, 0), (0, 1), (-1, 0), (0, -1))

    def attacks_square(self, square, cur_game_state):
        possible_moves = [
            [(j * i[0], j * i[1]) for j in range(1, 8)] for i in self.directions
        ]
        moves_to_check = [
            [(self.i + move_x, self.j + move_y) for (move_x, move_y) in direction]
            for direction in possible_moves
        ]
        enemy_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        friend_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        moves_to_keep = []
        for direction in moves_to_check:
            for i, move in enumerate(direction):
                if move in enemy_pieces:
                    moves_to_keep.append(direction[: i + 1])
                    break
                if move in friend_pieces:
                    moves_to_keep.append(direction[:i])
                    break
            else:
                moves_to_keep.append(direction)
        valid_moves = self.get_valid_moves(moves_to_keep, cur_game_state)

        return square in valid_moves

    def find_moves(self, cur_game_state):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        pos_to_stop = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        op_king_pos = (
            cur_game_state.white_king_pos
            if (self.color == "black")
            else cur_game_state.black_king_pos
        )

        possible_moves = [
            [(j * i[0], j * i[1]) for j in range(1, 8)] for i in self.directions
        ]
        moves_to_check = [
            [(self.i + move_x, self.j + move_y) for (move_x, move_y) in direction]
            for direction in possible_moves
        ]

        self.add_moves(moves_to_check, pos_to_avoid, pos_to_stop)

        self.check_is_king_in_moves(op_king_pos)


class bishop(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        self.directions = ((1, 1), (-1, 1), (-1, -1), (1, -1))

    def attacks_square(self, square, cur_game_state):
        possible_moves = [
            [(j * i[0], j * i[1]) for j in range(1, 8)] for i in self.directions
        ]
        moves_to_check = [
            [(self.i + move_x, self.j + move_y) for (move_x, move_y) in direction]
            for direction in possible_moves
        ]
        enemy_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        friend_pieces = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        moves_to_keep = []
        for direction in moves_to_check:
            for i, move in enumerate(direction):
                if move in enemy_pieces:
                    moves_to_keep.append(direction[: i + 1])
                    break
                if move in friend_pieces:
                    moves_to_keep.append(direction[:i])
                    break
            else:
                moves_to_keep.append(direction)
        valid_moves = self.get_valid_moves(moves_to_keep, cur_game_state)

        return square in valid_moves

    def find_moves(self, cur_game_state):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        pos_to_stop = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_white_pieces
        )
        op_king_pos = (
            cur_game_state.white_king_pos
            if (self.color == "black")
            else cur_game_state.black_king_pos
        )

        possible_moves = [
            [(j * i[0], j * i[1]) for j in range(1, 8)] for i in self.directions
        ]
        moves_to_check = [
            [(self.i + move_x, self.j + move_y) for (move_x, move_y) in direction]
            for direction in possible_moves
        ]

        self.add_moves(moves_to_check, pos_to_avoid, pos_to_stop)

        self.check_is_king_in_moves(op_king_pos)


class knight(piece):
    def __init__(self, i, j, image, color, name):
        super().__init__(image, color, name, i, j)
        self.protected = set()
        self.rect = None
        self.directions = [
            (2, -1),
            (2, 1),
            (1, 2),
            (-1, 2),
            (-2, 1),
            (-2, -1),
            (-1, -2),
            (1, -2),
        ]

    def attacks_square(self, square, cur_game_state):
        moves_to_check = [
            (self.i + move_x, self.j + move_y) for (move_x, move_y) in self.directions
        ]
        valid_moves = self.get_valid_moves([moves_to_check], cur_game_state)
        return square in valid_moves

    def find_moves(self, cur_game_state):
        self.moves.clear()
        self.protected.clear()
        pos_to_avoid = (
            cur_game_state.position_of_black_pieces
            if (self.color == "black")
            else cur_game_state.position_of_white_pieces
        )
        pos_to_stop = (
            cur_game_state.position_of_black_pieces
            if (self.color == "white")
            else cur_game_state.position_of_black_pieces
        )
        op_king_pos = (
            cur_game_state.white_king_pos
            if (self.color == "black")
            else cur_game_state.black_king_pos
        )

        possible_moves = [
            [(j * i[0], j * i[1]) for j in range(1, 2)] for i in self.directions
        ]
        moves_to_check = [
            [(self.i + move_x, self.j + move_y) for (move_x, move_y) in direction]
            for direction in possible_moves
        ]

        self.add_moves(moves_to_check, pos_to_avoid, pos_to_stop)

        self.check_is_king_in_moves(op_king_pos)


def set_captured_to_zero(white_captured_piece, black_captured_piece):
    for key in white_captured_piece:
        white_captured_piece[key][1] = 0
    for key in black_captured_piece:
        black_captured_piece[key][1] = 0
