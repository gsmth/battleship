import os
import time
import random


def main_menu():
    """ Organize game initialization """
    text = "1: Single player \n2: Multi player \nChoose player mode"
    player_choice = menu_input_handling(text, 1, 2)

    text = "Please enter table size"
    board_size = menu_input_handling(text, 5, 10)

    text = "Please enter turn count"
    turn_count = menu_input_handling(text, 5, 50)

    battleship_game(player_choice, board_size, turn_count)


def menu_input_handling(text, range_start, range_end):
    while True:
        try:
            count = int(input(f"{text} ({range_start} - {range_end}): "))
        except ValueError:
            clear()
            print(f"Invalid input! Only numbers accepted (must be between {range_start} - {range_end})!")
            continue
        if count in list(range(range_start, range_end + 1)):
            break
        clear()
        print(f"Invalid input! (must be between {range_start} - {range_end})")
    return count


def battleship_game(player_mode, board_size, turns):
    ai_player = 0
    if player_mode == 1:
        ai_player = 2

    ship_dict = available_ships(board_size)

    ships_player_1 = placement(init_board(board_size), ship_dict)
    if ai_player:
        ships_player_2 = placement(init_board(board_size), ship_dict, True)
    else:
        waiting_screen()
        ships_player_2 = placement(init_board(board_size), ship_dict, False)

    player1_board = init_board(board_size)
    player2_board = init_board(board_size)
    player = 1
    act_result = ""
    while True:
        print_board(player1_board, player2_board, act_result, turns)
        if player == 1:
            player1_board, act_result = shooting(player1_board, ships_player_2, player)
            if has_won(player1_board, ships_player_2):
                print_game_result(player1_board, player2_board, act_result, turns, player)
                break
            player = 2
        elif player == 2:
            if player == ai_player:
                time.sleep(1)
                player2_board, act_result = shooting(player2_board, ships_player_1, player, True)
            else:
                player2_board, act_result = shooting(player2_board, ships_player_1, player, False)
            if has_won(player2_board, ships_player_1):
                print_game_result(player1_board, player2_board, act_result, turns, player)
                break
            player = 1
            turns -= 1
        if turns == 0:
            print_game_result(player1_board, player2_board, act_result, turns)
            break


def available_ships(size):
    """ According to size, provide number of ships"""
    if size in [5, 6]:
        ship_dict = {1: 1, 2: 2}
    elif size in [7, 8]:
        ship_dict = {2: 1, 3: 2, 4: 1}
    else:
        ship_dict = {2: 1, 3: 2, 4: 2, 5: 1}
    return ship_dict


def init_board(size):
    """ Initialize board according to the input size """
    board = []
    for i in range(size):
        sublist = []
        for j in range(size):
            sublist.append(0)
        board.append(sublist)
    return board


def placement(board, ships, ai_player=False):
    if not ai_player:
        print_board(board)
    user_ships = []
    for key in ships.keys():
        for count in range(ships[key]):
            while True:
                position = position_check(board, ai_player, key)
                ship = ship_check(position, key, board, ai_player)
                if len(ship) == 0:
                    continue
                user_ships.append(ship)
                board = mark(board, ship)
                if not ai_player:
                    print_board(board)
                break
    if not ai_player:
        time.sleep(3)  # delay to memorize the positions
    return user_ships


def print_board(board, board2=[], hit_result="", turn=""):
    """ Initialize board according to the input size """
    clear()
    size = len(board)
    if turn != "":
        print(f"Remaining turns: {turn}")
    upper_row = " " * 2 + " ".join(map(str, list(range(1, size + 1))))
    if board2 != []:
        player_row = f"Player1{' ' * (2 * size - 4)}"
        if size > 9:
            player_row += " "
        print(player_row + "Player2")
        upper_row += " " * 4 + " ".join(map(str, list(range(1, len(board2) + 1))))
    print(upper_row)
    for i in range(size):
        row = chr(ord('A') + i) + " " + " ".join(map(str, board[i]))
        if board2 != []:
            if size > 9:
                row += " "
            row += " " * 2 + chr(ord('A') + i) + " " + " ".join(map(str, board2[i]))
        print(row)
    print(hit_result)


def clear():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")


def position_check(board, ai_player, length=0):
    size = len(board)
    if length != 0 and not ai_player:
        print(f"Ship size: {length}")
    forbidden_positions = set()
    if length != 0:
        forbidden_positions = get_near_positions(board)
    else:
        forbidden_positions.update(list(get_near_positions(board, "M", True)))
        forbidden_positions.update(list(get_near_positions(board, "S")))
        forbidden_positions.update(list(get_near_positions(board, "H", True)))
    positions = invert_forbidden(board, forbidden_positions)
    while True:
        position = ""
        if ai_player:
            if length == 0:
                possible_positions = get_near_positions(board, "H")
                if len(possible_positions) != 0:
                    positions = list(possible_positions.intersection(set(positions)))
            position = random.choice(positions)
        else:
            position = input(f"Please enter a position (A1 - {chr(ord('A') + size - 1)}{size}): ").upper()
        if len(position) == 0:
            if not ai_player:
                print("Invalid input!")
            continue
        if not position[0].isalpha() or not position[1:].isnumeric():
            if not ai_player:
                print("Invalid input!")
            continue
        if ord(position[0]) not in list(range(ord('A'), ord('A') + size)):
            if not ai_player:
                print("Input is out of range!")
            continue
        if not ai_player:
            position = position[0] + str(int(position[1:]) - 1)
        if int(position[1:]) not in list(range(size)):
            if not ai_player:
                print("Input is out of range!")
            continue
        return position


def get_near_positions(board, symbol="X", single_pos=False):
    near_position = []
    for row_idx, row in enumerate(board):
        for col_idx, col in enumerate(row):
            if col == symbol:
                if single_pos is False:
                    for i in range(-1, 2):
                        near_position.append(f"{chr(ord('A') + row_idx)}{col_idx + i}")
                        near_position.append(f"{chr(ord('A') + row_idx + i)}{col_idx}")
                else:
                    near_position.append(f"{chr(row_idx + ord('A'))}{col_idx}")
    return set(near_position)


def invert_forbidden(board, forbidden_position):
    size = len(board)
    board_list = []
    for row in range(ord('A'), ord('A') + size):
        for col in range(size):
            board_list.append(f"{chr(row)}{col}")
    return list(set(board_list) - forbidden_position)


def waiting_screen():
    clear()
    print("Next player's placement phase")
    input("Press enter to continue")


def ship_check(position, length, board, ai_player):
    if length == 1:
        return [position]
    while True:
        ship_orientation = ""
        possible_ori = ["H", "V"]
        if not ai_player:
            ship_orientation = input("Please enter an orientation (H/V): ").upper()
        else:
            ship_orientation = random.choice(possible_ori)
        if ship_orientation not in possible_ori:
            if not ai_player:
                print("Invalid input!")
            continue
        ship = build_ship(length, ship_orientation, position)
        if ord(ship[-1][0]) not in list(range(ord('A'), ord('A') + len(board))):
            if not ai_player:
                print("In vertical position cannot place this ship")
            return []
        elif int(ship[-1][1:]) not in list(range(len(board))):
            if not ai_player:
                print("In horizontal position cannot place this ship")
            return []
        forbidden_positions = get_near_positions(board)
        for element in ship:
            if element in forbidden_positions:
                if not ai_player:
                    print("Ships are too close!")
                return []
        return ship


def build_ship(length, ship_ori, position):
    ship = []
    for i in range(length):
        if ship_ori == "H":
            ship.append(position[0] + str(int(position[1:]) + i))
        if ship_ori == "V":
            ship.append(chr(ord(position[0]) + i) + position[1:])
    return ship


def mark(board, ship, symbol="X"):
    """ Handle change on the player's board """
    if type(ship) is list:
        for coord in ship:
            board[ord(coord[0]) - ord('A')][int(coord[1:])] = symbol
    else:
        board[ord(ship[0]) - ord('A')][int(ship[1:])] = symbol
    return board


def shooting(board, ship_list, player, ai_player=False):
    print(f"{player}. Players's turn")
    position = position_check(board, ai_player)
    pos_message = "You've missed!"
    for ship in ship_list:
        if position in ship:
            board = mark(board, position, "H")
            pos_message = "You've hit a ship!"
            ship_sunk = True
            for element in ship:
                if board[ord(element[0]) - ord('A')][int(element[1:])] != "H":
                    ship_sunk = False
            if ship_sunk:
                for element in ship:
                    board = mark(board, element, "S")
                pos_message = "You've sunk a ship!"
            break
        else:
            board = mark(board, position, "M")
    return board, pos_message


def has_won(board, ship_list):
    for ship in ship_list:
        for element in ship:
            if board[ord(element[0]) - ord('A')][int(element[1:])] != "S":
                return False
    return True


def print_game_result(board1, board2, hit_result, turns, player=0):
    print_board(board1, board2, hit_result, turns)
    if player == 0:
        print("No more turns, it's a draw!")
    else:
        print(f"Player {player} wins!")
    print("Hasta la vista, baby")
    time.sleep(2)
    quit()


if __name__ == "__main__":
    main_menu()
