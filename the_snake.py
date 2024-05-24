from random import choice
from typing import List, Tuple, Union

import pygame


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
SCREEN_CENTER = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс объектов игрового поля."""

    def __init__(
            self,
            body_color: Union[Tuple[int, int, int], None] = None,
            position: Union[Tuple[int, int], None] = SCREEN_CENTER,
    ) -> None:
        self.body_color = body_color
        self.position = position

    def draw(self) -> None:
        """
        Отрисовывает Объект на игровом поле.
        Переопределяется в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Объект Яблоко."""

    def __init__(
            self,
            body_color: Tuple[int, int, int] = APPLE_COLOR
    ) -> None:
        super().__init__(body_color, None)
        self.randomize_position([SCREEN_CENTER])

    def draw(self) -> None:
        """Отрисовывает Яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(
            self,
            exclude_positions: List[tuple[int, int]]
    ) -> None:
        """
        Устанавливает для Яблока случайную позицию на игровом поле,
        исключая попадание Яблока на позицию Змейки.
        'exclude_positions' - список координат Змейки.
        """
        free_positions = [
            (x, y)
            for x in range(0, SCREEN_WIDTH - GRID_SIZE + 1, GRID_SIZE)
            for y in range(0, SCREEN_HEIGHT - GRID_SIZE + 1, GRID_SIZE)
            if (x, y) not in exclude_positions
        ]
        self.position = choice(free_positions)


class Snake(GameObject):
    """Объект Змейка."""

    DEFAULT_LENGTH = 1

    def __init__(
        self,
        body_color: Tuple[int, int, int] = SNAKE_COLOR,
        position: Tuple[int, int] = SCREEN_CENTER
    ) -> None:
        super().__init__(body_color, position)

        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.length = Snake.DEFAULT_LENGTH
        self.positions = [self.position]
        self.is_crash = False  # Признак столкновения

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след."""
        # Отрисовка туловища змейки.
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки если туловища нет.
        if self.length == self.DEFAULT_LENGTH:
            head_position = self.get_head_position()
            head_rect = pygame.Rect(head_position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, head_rect)
            pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента.
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """
        Обновляет позицию змейки, добавляя новую голову
        в начало списка positions и удаляя последний элемент,
        если длинна змейки не увеличилась.
        """
        dx, dy = self.get_head_position()

        if self.direction == RIGHT:
            dx = dx + GRID_SIZE
            if dx == SCREEN_WIDTH:
                dx = 0
        elif self.direction == LEFT:
            dx -= GRID_SIZE
            if dx < 0:
                dx = SCREEN_WIDTH - GRID_SIZE
        elif self.direction == DOWN:
            dy += GRID_SIZE
            if dy == SCREEN_HEIGHT:
                dy = 0
        elif self.direction == UP:
            dy -= GRID_SIZE
            if dy < 0:
                dy = SCREEN_HEIGHT - GRID_SIZE

        if (dx, dy) in self.positions:
            self.reset()
            return

        self.positions.insert(0, (dx, dy))
        self.last = self.positions[-1]

        if len(self.positions) > self.length:
            self.positions.pop()

    def increase(self) -> None:
        """Увеличивает длинну Змейки, иммитируя поедание Яблока."""
        self.length += 1

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
        self.positions = [SCREEN_CENTER]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.last = None

        self.is_crash_toggle()

    def is_crash_toggle(self):
        """Переключатель признака столкновения."""
        self.is_crash = not self.is_crash


def handle_keys(game_object) -> None:
    """
    Обрабатывает нажатия клавиш, чтобы
    изменить направление движения змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Фукция запускает основной цикл игры."""
    # Инициализация PyGame:
    pygame.init()

    # Создание и отрисовка начального положения яблока и змейки.
    snake = Snake()
    apple = Apple()
    apple.draw()
    snake.draw()
    pygame.display.update()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        snake.draw()
        apple.draw()
        pygame.display.update()

        # Проверка на столкновение с собой
        if snake.is_crash:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.is_crash_toggle()
            continue
        # Проверка на съедание яблока
        if snake.get_head_position() == apple.position:
            snake.increase()
            apple.randomize_position(snake.positions)


if __name__ == '__main__':
    main()
