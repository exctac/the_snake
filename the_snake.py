from random import choice, randrange
from typing import List, Tuple, Union

import pygame as pg


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
SCREEN_CENTER = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Клавиши управления змейкой
SNAKE_CONTROL = (
    pg.K_LEFT,
    pg.K_RIGHT,
    pg.K_UP,
    pg.K_DOWN,
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Список возможных направлений движения,
# в зависимости от текущего направления и нажатой клавиши.
DIRECTIONS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет фона инфоблока - серый:
GAME_OVER_BG_COLOR = (52, 52, 52)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Клавиши изменнения скорости
SPEED_CONTROL = {
    pg.K_KP_PLUS: 4,
    pg.K_KP_MINUS: -4,
}
SPEED_MAX = 25
SPEED_MIN = 1

# Скорость движения змейки по умолчанию:
speed = 15

# Флаг окончания игры
game_over = False

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка. Выход (ESC) | Скорость (NUM +/- )')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс объектов игрового поля."""

    def __init__(
            self,
            body_color: Union[Tuple[int, int, int], None] = None,
    ) -> None:
        self.body_color = body_color
        self.position: Tuple[int, int] = SCREEN_CENTER

    def draw(self) -> None:
        """
        Отрисовывает Объект на игровом поле.
        Переопределяется в дочерних классах.
        """
        raise NotImplementedError(f'Определите метод "draw" в '
                                  f'классе "{self.__class__.__name__}".')

    @staticmethod
    def draw_rectangle(
            position: Tuple[int, int],
            width: int,
            height: int,
            body_color: Tuple[int, int, int],
            border_color: Union[Tuple[int, int, int], None] = None,
    ):
        """
        Отрисовывает прямоугольник по заданным параметрам:
        'position': коодинаты;
        'width': ширина;
        'height': высота;
        'body_color': цвет фона;
        'border_color': цветом рамки.
        """
        rect = (pg.Rect(position, (width, height)))
        pg.draw.rect(screen, body_color, rect)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rect, width=1)


class Apple(GameObject):
    """Объект Яблоко."""

    def __init__(
            self,
            body_color: Tuple[int, int, int] = APPLE_COLOR,
            exclude_positions: List[Tuple[int, int]] = None,
    ) -> None:
        super().__init__(body_color)
        self.randomize_position(exclude_positions or [])

    def draw(self) -> None:
        """Отрисовывает Яблоко на игровом поле."""
        self.draw_rectangle(self.position, GRID_SIZE, GRID_SIZE,
                            self.body_color, BORDER_COLOR)

    def randomize_position(
            self,
            exclude_positions: List[Tuple[int, int]] = None
    ) -> None:
        """
        Устанавливает для Яблока случайную позицию на игровом поле,
        исключая попадание Яблока на позицию Змейки.
        'exclude_positions' - список координат Змейки.
        """
        while True:
            self.position = (
                randrange(0, SCREEN_WIDTH - GRID_SIZE + 1, GRID_SIZE),
                randrange(0, SCREEN_HEIGHT - GRID_SIZE + 1, GRID_SIZE),
            )
            if self.position not in exclude_positions:
                break


class Snake(GameObject):
    """Объект Змейка."""

    DEFAULT_LENGTH = 1
    MAX_LENGTH = 20

    def __init__(
            self,
            body_color: Tuple[int, int, int] = SNAKE_COLOR,
    ) -> None:
        super().__init__(body_color)

        self.direction = RIGHT
        self.last = None
        self.length = self.DEFAULT_LENGTH
        self.positions = [self.position]

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след."""
        # Отрисовка головы змейки если туловища нет.
        self.draw_rectangle(self.get_head_position(), GRID_SIZE, GRID_SIZE,
                            self.body_color, BORDER_COLOR)

        # Затирание последнего сегмента.
        if self.last:
            self.draw_rectangle(self.last, GRID_SIZE, GRID_SIZE,
                                BOARD_BACKGROUND_COLOR)

    def update_direction(self, event_key: int) -> None:
        """Обновляет направление движения змейки."""
        self.direction = DIRECTIONS.get(
            (self.direction, event_key),
            self.direction,
        )

    def move(self) -> None:
        """
        Обновляет позицию змейки, добавляя новую голову
        в начало списка positions и удаляя последний элемент,
        если длинна змейки не увеличилась.
        """
        position_x, position_y = self.get_head_position()
        direction_x, direction_y = self.direction

        self.positions.insert(0, (
            (position_x + (direction_x * GRID_SIZE)) % SCREEN_WIDTH,
            (position_y + (direction_y * GRID_SIZE)) % SCREEN_HEIGHT,
        ))

        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы Змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def reset(self) -> None:
        """
        Сбрасывает Змейку в начальное состояние
        после столкновения с собой.
        """
        self.length = self.DEFAULT_LENGTH
        self.positions = [self.position]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.last = None


def update_speed(event_key: int) -> None:
    """Обновляет скорость движения змейки."""
    global speed

    new_speed = speed + SPEED_CONTROL[event_key]
    if SPEED_MIN <= new_speed <= SPEED_MAX:
        speed = new_speed


def handle_keys(game_object) -> bool:
    """Обрабатывает нажатия клавиш для управления игрой."""
    global game_over

    for event in pg.event.get():
        if event.type == pg.QUIT:  # Выход из игры.
            return False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:  # Выход из игры.
                return False
            elif event.key in SNAKE_CONTROL:  # Изменение направления змейки.
                game_object.update_direction(event.key)
            elif event.key in SPEED_CONTROL:  # Изменение скорости змейки.
                update_speed(event.key)
            elif game_over and event.key == pg.K_r:  # Рестарт игры.
                game_over = False

    return True


def draw_message(text: str,
                 font_size: int,
                 font_color: tuple[int, int, int],
                 margin_top: int) -> None:
    """
    Выводит сообщение, центрируя его по ширине экрана.

    'text': текст сообщения;
    'font_size': размер шрифта;
    'font_color': цвет шрифта;
    'margin_top': отступ от верхнего края окна.
    """
    font = pg.font.SysFont('arial.ttf', font_size)
    text = font.render(text, True, font_color)
    margin_left = (SCREEN_WIDTH - text.get_width()) // 2
    screen.blit(text, (margin_left, margin_top))


def main() -> None:
    """Фукция запускает основной цикл игры."""
    global game_over

    # Инициализация PyGame:
    pg.init()
    # Создание и отрисовка змейки, начальное положение центр экрана.
    snake = Snake()
    snake.draw()
    # Создание и отрисовка Яблока, исключая появление на змейке.
    apple = Apple(exclude_positions=snake.positions)
    apple.draw()
    pg.display.update()

    while True:
        clock.tick(speed)

        if not handle_keys(snake):
            break

        # Пауза игры, до ее рестарта.
        if game_over:
            continue

        # Проверка на победу в игре.
        if snake.length == snake.MAX_LENGTH and not game_over:
            game_over = True

            # Вывод сообщения о завершении игры.
            screen.fill(GAME_OVER_BG_COLOR)
            draw_message('Победа!',
                         72, APPLE_COLOR, 180)
            draw_message('Для перезапуска игры нажмите клавишу <R>.',
                         32, BOARD_BACKGROUND_COLOR, 240)
            pg.display.update()

            # Сброс настроек зейки и яблока по дефолту.
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)

            continue

        snake.move()

        head_position = snake.get_head_position()
        if (head_position in snake.positions[3:]
                or head_position == snake.last):
            # Проверка на столкновение с телом и хвостом. Пояснение.
            # Столкновение произойдёт при длинне змейки >= 4.
            # Если длинна > 4. Столкновение с телом или хвостом.
            # Если длинна змейки будет = 4, то столкновение может произойти
            # лишь с хвостом. Однако этого не произойдет, так как до данного
            # условия в `snake.move()` уже расчитано новое положение головы,
            # а хвост, с который голова может укусить уже удалён из
            # `snake.positions` и записан в snake.last. Поэтому необходимо
            # проверить столкновение с хвостом.
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)
        elif head_position == apple.position:  # Проверка на съедание яблока
            snake.length += 1
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
