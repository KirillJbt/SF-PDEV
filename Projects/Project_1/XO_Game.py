import random
import time

remaining_moves = 9  # remaining number of moves
cell_number = None
board = {}  # game board
board_hint = {}  # a board with hints of cell numbers
name_player0 = ""
name_player1 = ""
who_playing0 = ""
who_playing1 = ""
win_cells = {1, 3, 5, 7, 9}


def get_welcome():
    print("")
    print("\t\tWelcome to the XO game")
    print("")
    print("To move to the desired cell, enter its number.")
    print("")
    print(f"\t\t\tCELL NUMBERS")
    print(f"\t\t\t-------------")
    print(f"\t\t\t| 7 | 8 | 9 |")
    print(f"\t\t\t-------------")
    print(f"\t\t\t| 4 | 5 | 6 |")
    print(f"\t\t\t-------------")
    print(f"\t\t\t| 1 | 2 | 3 |")
    print(f"\t\t\t-------------")
    print("")


def get_board():
    """
        Creates a blank field and a field with hints with cell numbers
    """
    for c in range(1, 10):
        board[c] = " "
        board_hint[c] = str(c)


def cast_lots():
    """
        Randomly selects who plays for "X" and who plays for "0"

    Returns:
        tuple(str, str): signs "X" or "0" for each player
    """
    player_one, player_two = 0, 0
    while player_one == player_two:
        for _ in range(3):
            player_one += random.randint(1, 6)
            player_two += random.randint(1, 6)
    return ('X', '0') if player_one > player_two else ('0', 'X')


def input_valid(text, rm_cells):
    """
        Checks which characters are entered by the players. Only numbers are checked
    corresponding to free cells or 0 for exits from the game.


    Args:
        text (str): Text output to the console before the request
        rm_cells (list): List of free cells

    Returns:
        int: Number of cell selection or game type selection
    """
    while True:
        result = input(text)
        if result.isdigit() and (int(result) in rm_cells or result == "0"):
            return int(result)
        print("Enter one digit from the remaining cell numbers or 0 for quit!")


def board_print():
    """
    Outputs the playing field to the console in text format. The cells are filled with the corresponding symbols
    containing in dictionaries "board" and "board_hint".
    """
    print(f"CELL NUMBERS\t\t    BOARD  ")
    print(f"-------------\t\t-------------")
    print(f"| {board_hint[7]} | {board_hint[8]} | {board_hint[9]} |\t\t| {board[7]} | {board[8]} | {board[9]} |")
    print(f"-------------\t\t-------------")
    print(f"| {board_hint[4]} | {board_hint[5]} | {board_hint[6]} |\t\t| {board[4]} | {board[5]} | {board[6]} |")
    print(f"-------------\t\t-------------")
    print(f"| {board_hint[1]} | {board_hint[2]} | {board_hint[3]} |\t\t| {board[1]} | {board[2]} | {board[3]} |")
    print(f"-------------\t\t-------------")


def get_empty_cells(board_mask):
    """
        Searches for empty cells on the game board

    Args:
        board_mask (dict): A game board in the form of a dictionary

    Returns:
        list: List with empty cell numbers
    """
    cells_empty = [x[0] for x in list(board_mask.items()) if x[1] == ' ']
    return cells_empty


def get_winning(board_mask):
    """
        The players' winnings are checked after the next move

    Args:
        board_mask (dict): A game board in the form of a dictionary

    Returns:
        bool: The result of checking the winning moves
    """
    win_lines = (
        (1, 2, 3),  # - top horizontal line
        (4, 5, 6),  # - middle  horizontal line
        (7, 8, 9),  # - bottom horizontal line
        (1, 4, 7),  # - left vertical line
        (2, 5, 8),  # - middle vertical line
        (3, 6, 9),  # - right vertical line
        (1, 5, 9),  # - \ line
        (3, 5, 7)  # - / line
    )
    x_cells = {x[0] for x in board_mask.items() if x[1] == 'X'}  # set of cells closed by "X"
    o_cells = {x[0] for x in board_mask.items() if x[1] == '0'}  # set of cells closed by "0"
    for line in win_lines:
        if len(x_cells.intersection(line)) == 3 or len(o_cells.intersection(line)) == 3:
            return True
    return False


def ai_easy(empty_cells):
    """
        "AI" implementing computer moves, as a second player, at the "easy" difficulty level.
    The selection is made randomly from the list of free cells.

    Args:
        empty_cells (list): List with empty cell numbers

    Returns:
        int: Randomly selected number from the list
    """
    return random.choice(empty_cells)


def get_best_move(board_mask, player=True):
    """
    The Minimax algorithm is recursive. The key idea of the algorithm in relation to games is to find the best move.
    1. The function returns the score if a terminal state is found (win — 10, loss -10, draw — 0 points).
    2. If no terminal state is found, the function passes through all the free cells of the field, makes moves in them
      and recursively calls the minimax function on behalf of the opponent for each of its moves.
    3. The function evaluates the best score for the current player at this stage and returns this score.
      The best score for a move for a human player is -10, for a move for a computer player 10 4.
      As a result, the function returns a number with the number of the cell, the move to which brings the most points.

    Args:
        board_mask (dict): A game board in the form of a dictionary
        player (bool, optional): Flag - The Human Player is True, the Computer Player is False. Defaults to True.

    Returns: list: [Score(int), Number(int)] A list of two elements: Score - the number of points per turn;
                                                                    Number - the number with the cell number
    """
    rm_cells = get_empty_cells(board_mask)
    game_over = get_winning(board_mask)
    if game_over and player:  # score if human move
        return [-10, None]
    elif game_over and not player:  # score if computer move
        return [10, None]
    elif not rm_cells:  # score if drawn
        return [0, None]

    best_move = ''
    if player:
        best_score = -float('Inf')
    else:
        best_score = float('Inf')

    for cell in get_empty_cells(board_mask):
        board_mask[cell] = players[player]['sign']
        res = get_best_move(board_mask, not player)[0]
        board_mask[cell] = ' '

        if player and res > best_score:
            best_score = res
            best_move = cell
        elif not player and res < best_score:
            best_score = res
            best_move = cell

    return [best_score, best_move]


get_welcome()

game_type = input_valid("Enter \"1\" for game Human >-< Computer "
                        "or enter \"2\" for game Human >-< Human "
                        "or \"5\": ", [1, 2, 5])

if game_type == 1:
    game_type = input_valid("Difficulty of the game: \"0\" - easy / \"1\" - normal / \"2\" - impossible: ", [0, 1, 2])
    game_type = 3 if game_type == 2 else game_type

if game_type == 0:
    name_player0 = input("What is your name? ")
    name_player1 = 'Calculator'
    who_playing0 = 'human'
    who_playing1 = 'ai_easy'
elif game_type == 1:
    name_player0 = input("What is your name? ")
    name_player1 = 'Computer'
    who_playing0 = 'human'
    who_playing1 = 'ai_normal'
elif game_type == 2:
    name_player0 = input("Enter the name of the first player: ")
    name_player1 = input("Enter the name of the second player: ")
    who_playing0 = 'human'
    who_playing1 = 'human'
elif game_type == 3:
    name_player0 = input("What is your name? ")
    name_player1 = 'Agent Smith'
    who_playing0 = 'human'
    who_playing1 = 'ai_impossible'
else:
    name_player0 = 'Calculator1'
    name_player1 = 'Calculator2'
    who_playing0 = 'ai_easy'
    who_playing1 = 'ai_easy'
    delay = 2

players = {
    0: {
        'who_playing': who_playing0,
        'name': name_player0,
        'win': 0,
        'sign': ''
    },
    1: {
        'who_playing': who_playing1,
        'name': name_player1,
        'win': 0,
        'sign': ''
    }
}
get_board()
players[0]['sign'], players[1]['sign'] = cast_lots()
print("")
print(f"{players[0]['name']} is playing - {players[0]['sign']}")
print("")
print(f"{players[1]['name']} is playing - {players[1]['sign']}")
print("")

if players[0]['sign'] == 'X':
    whose_move = 0
else:
    whose_move = 1

print("We play up to 3 wins")
print("")

while abs(players[0]['win'] - players[1]['win']) < 3:
    board_print()
    print(f"Game score:\t{players[0]['name']}: {players[0]['win']}\t-\t{players[1]['name']}: {players[1]['win']}")
    print("")
    print(f"{players[whose_move]['name']}'s move")
    print("")
    remaining_cells = get_empty_cells(board)
    if players[whose_move]['who_playing'] == 'human':  # player's move
        cell_number = input_valid("Enter the cell number (0 for quit): ", remaining_cells)
        if cell_number == 0:  # exiting the game
            if input_valid("Are you giving up?(1-Yes/0-No): ", [0, 1]):
                print("")
                print("The game is over")
                break
            continue
    elif players[whose_move]['who_playing'] == 'ai_easy':  # computer's move difficulty: easy
        cell_number = ai_easy(remaining_cells)
        time.sleep(random.uniform(1, 2))
    elif players[whose_move]['who_playing'] == 'ai_normal':  # computer's move difficulty: normal
        if remaining_moves >= 8:
            cell_number = random.choice(tuple(win_cells.intersection(remaining_cells)))
        else:
            cell_number = get_best_move(board)[1]
    elif players[whose_move]['who_playing'] == 'ai_impossible':  # computer's move difficulty: impossible
        cell_number = get_best_move(board)[1]

    board[cell_number] = players[whose_move]['sign']
    board_hint[cell_number] = ' '

    if get_winning(board):
        if players[whose_move]['sign'] == '0':
            players[0]['sign'], players[1]['sign'] = players[1]['sign'], players[0]['sign']
        board_print()
        players[whose_move]['win'] += 1
        print("")
        print(f"{players[whose_move]['name']} is the winner!")
        print("")
        remaining_moves = 9
        get_board()
        continue

    whose_move = 0 if whose_move else 1
    remaining_moves -= 1

    if remaining_moves == 0:
        board_print()
        print("The game is drawn")
        print("")
        remaining_moves = 9
        get_board()
        players[0]['sign'], players[1]['sign'] = cast_lots()
        print(f"{players[0]['name']} is playing - {players[0]['sign']}")
        print(f"{players[1]['name']} is playing - {players[1]['sign']}")
        if players[0]['sign'] == 'X':
            whose_move = 0
        else:
            whose_move = 1

if cell_number != 0 and players[1]['who_playing'] == 'human':
    if players[0]['win'] > players[1]['win']:
        champion = players[0]['name']
    else:
        champion = players[1]['name']
    print(f"Congratulations {champion} is the CHAMPION!!!")

elif cell_number != 0 and players[1]['who_playing'] != 'human':
    if players[0]['win'] > players[1]['win']:
        print(f"Congratulations {players[0]['name']} is the CHAMPION!!!")
    else:
        print(f"{players[0]['name']}, you've lost!")
