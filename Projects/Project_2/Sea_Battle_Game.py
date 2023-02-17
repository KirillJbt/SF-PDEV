from random import randint
from typing import Tuple

LETTER_INDEX = "АБВГДЕЖЗИКЛМНОПРСТ"
BOARD_SIZE = 6


class GameException(Exception):
    """
    Класс игровых исключений
    """


class BoardOutsideException(GameException):
    """
    Класс исключения при выстредле за границы игровой доски
    """

    def __str__(self):
        return f'Координаты за пределами игрового поля.'


class OccupiedCellException(GameException):
    """
    Класс исключения при выстреле в занятую клетку
    """

    def __str__(self):
        return f'По этим координатам выстрел уже был.'


class CoordinateTypeException(GameException):
    """
    Класс исключения при ошибочном формате координат
    """

    def __str__(self):
        return f'Неверный формат координат'


class BoardSizeException(GameException):
    """
    Класс исключения при ошибочном формате игровой доски
    """

    def __str__(self):
        return f'Игровая доска не должна быть меньше 5х5 и не больше 16х16'


class WrongPositionShipException(GameException):
    """
    Класс исключения при неверной позиции корабля.
    """


class Cell:
    """
    Класс клеток на поле. Каждая клетка описывается параметрами:
    
        row - номер строки
        column - номер столбца
        
    Методы:
    
    __eq__ - 
    __repr__ - 
    """

    def __init__(self, row, column):
        self.row = row
        self.column = column

    def __eq__(self, other):
        return self.row == other.row and self.column == other.column

    def __repr__(self):
        return f'Cell({self.row}, {self.column})'


class Ship:
    """
    Класс корабль на игровом поле.
    
    Параметры:
    
    coord - координаты клетки, где размещён нос корабля.
    length - длина корабля.
    orientation - ориентация корабля(0 - горизонтальная/ 1 - вертикальная)
    health - количество жизней. В начале игры соответствует длине корабля.
    
    Метод:
    
    cells - возвращает список объектов класса Cell с координатами всех клеток на которых расположен корабль.
    """

    def __init__(self, coord, length, orientation):
        self.coord = coord
        self.length = length
        self.orientation = orientation
        self.health = length

    @property
    def cells(self):
        ship_coords = []
        for cell in range(self.length):
            basic_row = self.coord.row
            basic_column = self.coord.column
            if self.orientation:
                basic_row += cell
            else:
                basic_column += cell
            ship_coords.append(Cell(basic_row, basic_column))

        return ship_coords

    def hit_check(self, cell):
        return cell in self.cells


class Board:
    """Класс игровая доска.
        
    Attributes:
    ----------
        size: int
            размер игровой доски(не должна быть меньше 5х5 и не больше 10х10)

        hide: bool
            скрывает не подбитые корабли на доске компьютера. По умолчанию False.

        count: int
            счетчик уничтоженных кораблей

        mask: list
            двухмерный список, хранит состояние каждой клетки игровой доски
            ("▓" - корабль, "X" - подбитый корабль, "." - мимо/ореол корабля, " " - пустая)

        occupy_cells: list
            список занятых клеток(объектов класса Cell)
        
        ships: list
            список всех кораблей(объектов класса Ship)
        
    Methods:
    -------
        add_ship(ship)
            Случайным образом расставляет корабли на доске.

        aureole(ship, visibility=False)
            Расставляет точки вокруг каждого убитого корабля.

        outside_board(cell)
            Проверяет выходят ли координаты за границы доски. Возвращает True или False.

        shot(cell)
            Делает "выстрел" по координатам на доске. При попадании возвращает True, при промахе False.

        begin()
            Инициализирует список занятых клеток occupy_cells
        
    """

    def __init__(self, hide: bool = False, size: int = BOARD_SIZE):
        if 5 > size > 10:
            raise BoardSizeException
        self.size = size
        self.hide = hide
        self.count = 0
        self.mask = [[" "] * size for _ in range(size)]
        self.occupy_cells = []
        self.ships = []

    def add_ship(self, ship: Ship) -> None:
        """Случайным образом расставляет корабли на доске
        (если ставить не получается, вызывается исключение)

        Args:
            ship (Ship): корабль

        Raises:
            WrongPositionShipException: Если координаты за границей доски
                                        или клетка уже занята, вызывается исключение.
        """
        sign = " " if self.hide else "▓"
        for cell in ship.cells:
            if self.outside_board(cell) or cell in self.occupy_cells:
                raise WrongPositionShipException
        for cell in ship.cells:
            self.mask[cell.row][cell.column] = sign
            self.occupy_cells.append(cell)

        self.ships.append(ship)
        self.aureole(ship)

    def aureole(self, ship: Ship, visibility: bool = False) -> None:
        """Расставляет точки вокруг каждого убитого корабля, область (шириной в одну клетку), 
        в которой не может быть других кораблей.
        Если аргумент visibility не задан, оласть вокруг корабля остается заполненной пробелами.

        Args:
            ship (Ship): корабль
            visibility (bool, optional): Флаг видимости точек вокруг корабля. Defaults to False.
        """
        around_ship = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for cell in ship.cells:
            for row, column in around_ship:
                current_cell = Cell(cell.row + row, cell.column + column)
                if not (self.outside_board(current_cell)) and current_cell not in self.occupy_cells:
                    if visibility:
                        self.mask[current_cell.row][current_cell.column] = "·"
                    self.occupy_cells.append(current_cell)

    def outside_board(self, cell: Cell) -> bool:
        """Проверяет выходят ли координаты за границы доски.

        Args:
            cell (Cell): Объект класса Cell с координатами клетки.

        Returns:
            bool: Возвращает True если координаты выходят за границы доски,
                иначе возвращает False
        """
        return not ((0 <= cell.row < self.size) and (0 <= cell.column < self.size))

    def shot(self, cell: Cell) -> bool:
        """Делает "выстрел" по координатам на доске. 
        При попадании в корабль или промахе выводит соответствующее сообщение.
        В параметре mask меняет состояние клетки на "Х".
        При попадании возвращает True, при промахе False.
        
        Args:
            cell (Cell): Объект класса Cell с координатами клетки.

        Raises:
            BoardOutsideException: Если координаты выходят за границы доски вызывается исключение.
            OccupiedCellException: Если клетка отмечена "." вызывается исключение.
        Returns:
            bool: Возвращает True если есть попадание в корабль, иначе False.
        """
        if self.outside_board(cell):
            raise BoardOutsideException

        if cell in self.occupy_cells:
            raise OccupiedCellException

        self.occupy_cells.append(cell)

        for ship in self.ships:
            if cell in ship.cells:
                print(" Есть попадание!")
                ship.health -= 1
                self.mask[cell.row][cell.column] = "X"
                if ship.health == 0:
                    self.count += 1
                    self.aureole(ship, visibility=True)
                    print(" Корабль уничтожен!")
                    return True
                else:
                    print(" Корабль ранен!")
                    return True

        self.mask[cell.row][cell.column] = "."
        print(" Мимо!")
        return False

    def begin(self) -> None:
        """Инициализирует список занятых клеток occupy_cells
        """
        self.occupy_cells = []


class BoardPrint:
    """Класс "BoardPrint" формирует игровые доски в формате строки, для вывода в консоль.
        
    Attributes
    ----------
    board_user: Board
        Игровая доска для пользователя.
        
    board_computer: Board
        Игровая доска для компьютера.
        
    size: int Размер игровой доски(не должна быть меньше 5х5 и не больше 10х10). Может принимать значение от 5 до 10
    включительно. По умолчанию принимает значение константы BOARD_SIZE
        
    Methods
    -------
    __str__()
        Формирует игровые доски, необходимой формы для паравильной визуализации. Возвращает результат в виде строки.
    
    """

    def __init__(self, board_user, board_computer, size=BOARD_SIZE):
        self.board_user = board_user.mask
        self.board_computer = board_computer.mask
        self.size = size

    def __str__(self) -> str:
        size = self.size
        result = "     "
        result += "   ".join(LETTER_INDEX[:size]) + "\t\t\t\t " + "   ".join(LETTER_INDEX[:size]) + "\n"
        result += "   -" + "----" * size + "\t" * 2 + "   -" + "----" * size + "\n"
        for i, row in enumerate(zip(self.board_user, self.board_computer)):
            result += f"{i + 1:2} | " + " | ".join(row[0]) + " |" + "\t\t" + f"{i + 1:2} | " + " | ".join(
                row[1]) + " |" + "\n"
            result += "   -" + "----" * size + "\t\t" + "   -" + "----" * size + "\n"

        return result


class Player:
    """Класс описывающия действия игроков во время игры.
        
    Attributes
    ----------
        board: Board
            Игровая доска игрока делающего ход.
        opponent: Board
            Игровая доска оппонента.
        
    
    Methods
    -------    
        requesting_coordinates()
            Запрашивает координаты для "выстрела".
        
        move() Делает ход игрока. Возвращает True, если этому игроку нужен повторный ход (например, если он выстрелом
        подбил корабль).
    
    """

    def __init__(self, board, opponent):
        self.board = board
        self.opponent = opponent

    def requesting_coordinates(self) -> None:
        """Запрашивает координаты для "выстрела". Должен быть реализован в наследующих классах.
        
        Raises:
            NotImplementedError: Если метод не будет реализован в наследующих классах вызывается исключение.
        """
        raise NotImplementedError()

    def move(self) -> bool:
        """Делает ход в игре. Тут вызывается метод requesting_coordinates, производится "выстрел" по доске оппонента
        (метод Board.shot), отлавливаются игровые исключения, и если они есть, повторить ход. Метод возвращает True,
        если этому игроку нужен повторный ход (например, если он выстрелом подбил корабль).
        
        Returns:
            bool: Возвращает True, если этому игроку нужен повторный ход, иначе False.
        """
        while True:
            try:
                target = self.requesting_coordinates()
                another_move = self.opponent.shot(target)
                return another_move
            except GameException as e:
                print(e)


class AI(Player):
    """Наследующий класс Player для компьютера.
    
    Methods: ------- requesting_coordinates() Переопределенный метод для случайного выбора координат для "выстрела".
    Возвращает объект класса Cell со случайными координатами.
        
    """

    def requesting_coordinates(self) -> Cell:
        """Рандомно определяет координаты в формате (строка, столбец), согласно размерам игровой доски. Выводит
        сообщение с координатами, приведенными в буквенно-числовой вид. Создает экземпляр класса Cell с этими
        координатами и возвращает его.

        Returns:
            Cell: Клетка со случайными координатами.
        """
        coords = Cell(randint(0, BOARD_SIZE - 1), randint(0, BOARD_SIZE - 1))
        print(f" Ход компьютера: {LETTER_INDEX[coords.column]} {coords.row + 1}")
        return coords


class User(Player):
    """Наследующий класс Player для пользователя.

    Methods: ------- requesting_coordinates() Переопределенный метод для ввода координат пользователем. Возвращает
    объект класса Cell с полученными координатами.
    """

    def requesting_coordinates(self) -> Cell:
        """Запрашивает у пользователя координаты для выстрела. Формат ввода координаты привычный для пользователя
        буква-число (А1, Б3, Г5 и т. д.) Производит проверку корректности ввода. Если координаты корректны,
        преобразуются в формат (строка, столбец). Если не корректны запрашиваются заново. Возвращает экземпляр класса
        Cell, с преобразованными координатами.

        Returns:
            Cell: Клетка с полученными от пользователя координатами.
        """
        while True:
            coords = list(input(" Ваш ход: ").upper())

            if len(coords) != 2:
                print(" Введите 2 координаты! ")
                continue

            column, row = coords

            if not (row.isdigit()) or not (column.isalpha()):
                print(" Введите координаты в формате: буква число! ")
                continue

            if 1 > int(row) > BOARD_SIZE:
                print(" Такого числа на доске нет! ")
                continue

            column = LETTER_INDEX.find(column, 0, BOARD_SIZE)
            if column == -1:
                print(" Такой буквы на доске нет! ")
                continue

            return Cell(int(row) - 1, column)


class Game:
    """Основной игровой класс отвечающий за логику игрового процесса.
    
    Attributes:
    ----------
        size: int
            размер игровой доски(не должна быть меньше 5х5 и не больше 10х10)
        
    Methods:
    -------
        random_board(hide=False):
            Вызывает метод random_place пока все корабли не будут расставлены.
            Возвращает экземпляр класса Board с расставленными кораблями. 
            
        random_place(hide=False):
            Случайным образом расставляет корабли на игровой доске.
            Возвращает экземпляр класса Board с расставленными кораблями.
            
        greet():
            Выводит приветственное сообщение.

        cast_lots():
            Случайным образом выбирает делающего первый ход.
                    
        game_cycle():
            Основной игровой цикл.
            
        start():
            Запускает игру.

    
    """

    def __init__(self, size: int = BOARD_SIZE) -> None:
        self.size = size
        user_board = self.random_board()
        computer_board = self.random_board(hide=True)

        self.player_ai = AI(computer_board, user_board)
        self.player_user = User(user_board, computer_board)

    def random_board(self, hide: bool = False) -> Board:
        """Вызывает метод random_place пока все корабли не будут расставлены.
        Возвращает экземпляр класса Board с расставленными кораблями.
        Создан для того что бы уменьшить вложенность циклов и условий.

        Args:
            hide (bool, optional): Флаг скрывает расставленные корабли на доске. Defaults to False.

        Returns:
            Board: Игровая доска с расставленными кораблями.
        """
        successful_attempt, board = False, None
        while not successful_attempt:
            successful_attempt, board = self.random_place(hide)
        return board

    def random_place(self, hide: bool = False) -> Tuple[bool, Board]:
        """Случайным образом расставляет корабли, из списка ships, на игровой доске. Рандомно выбирается направление
        и координаты начальной клетки кораблей. В бесконечном цикле подсчитывается количесво попыток расстановки
        кораблей(опытным путем установлено 2000 попыток). Цикл прерывается в случае превышения указанного количества
        попыток или при удачной попытке расстановки кораблей. Так же отлавливается ошибка расстановки кораблей и
        вызывается исключение WrongPositionShipException.
        
        Args:
            hide (bool, optional): Флаг скрывает расставленные корабли на доске. Defaults to False.

        Returns:
            None: В случае невозможности расстановки кораблей.
            Board: Игровая доска с расставленными, случайным образом, кораблями.
        """
        ships = [4, 3, 2, 3, 2, 2, 1, 1, 1, 1]
        begin = 9 - self.size if self.size < 10 else 0
        board = Board(hide=hide, size=self.size)
        size = self.size - 1
        attempts = 0
        for ship_length in ships[begin::]:
            while True:
                attempts += 1
                if attempts > 2000:  # Прерывает бесконечный цикл при привышении количества попыток расставить корабли
                    return False, board

                direction = randint(0, 1)
                if direction:
                    ship = Ship(Cell(randint(0, size), randint(0, size - ship_length)), ship_length, direction)
                else:
                    ship = Ship(Cell(randint(0, size - ship_length), randint(0, size)), ship_length, direction)

                try:
                    board.add_ship(ship)
                    break
                except WrongPositionShipException:
                    pass
        board.begin()
        return True, board

    @staticmethod
    def greet():

        print("---------------------------------------------------")
        print("                                               **  ")
        print("  **   **  ****  *****   ****  **  **  ****  **  **")
        print("  *** *** **  ** **  ** **  ** ** **  **  ** **  **")
        print("  ** * ** **  ** **  ** **     ****   **  ** ** ***")
        print("  ** * ** **  ** *****  **     ****   **  ** ** ***")
        print("  **   ** **  ** **     **  ** ** **  **  ** *** **")
        print("  **   **  ****  **      ****  **  **  ****  **  **")
        print("")
        print("                              **                   ")
        print("              *****   ****  **  **                 ")
        print("              **     **  ** **  **                 ")
        print("              *****  **  ** ** ***                 ")
        print("              **  ** **  ** *** **                 ")
        print("              *****   ****  **  **                 ")
        print("---------------------------------------------------")
        print("                  формат ввода: ")
        print("             например 'А1' 'Б3' ")
        print("                 Буква - столбец  ")
        print("                 Число - строка   ")
        print("---------------------------------------------------")

    @staticmethod
    def cast_lots() -> int:
        """Случайным образом выбирает делающего первый ход.

        Returns:
            int: Если по результатам жеребьевки "выигрывает" пользователь возвращает 1, иначе 0.
        """
        player_user, player_computer = 0, 0
        while player_user == player_computer:
            for _ in range(3):
                player_user += randint(1, 6)
                player_computer += randint(1, 6)
        return 1 if player_user > player_computer else 0

    def game_cycle(self) -> None:
        """Игровой цикл, условием выхода из которого, является победа одного из игроков.
        Во время цикла результаты действий игроков выодится на экран, подсчитывается количество "подбитых" кораблей.
        Как только количество "подбитых" кораблей того или иного игрока сравняется с установленным, выводится информация
        о победившем игроке и игровой цикл останавливается.
        """
        num = self.cast_lots()
        first = "Пользователь" if num else "Компьютер"
        print(f"Первым ходит {first}!")
        while True:
            print(BoardPrint(self.player_user.board, self.player_ai.board))
            if num % 2 != 0:
                print("-" * 20)
                another_move = self.player_user.move()
            else:
                print("-" * 20)
                another_move = self.player_ai.move()

            print("-" * 20)
            if another_move:
                num -= 1

            if self.player_ai.board.count == 7:
                print("-" * 20)
                print("Поздравляю Вы выиграли!")
                break

            if self.player_user.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.game_cycle()


game = Game()
game.start()
