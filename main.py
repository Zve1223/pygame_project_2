from __future__ import annotations
from typing import TypeVar

import os
import pygame
from pygame import Surface, Vector2, Color, Rect
from time import time as now
from random import random, randint
from math import sin, cos, pi

pygame.init()
WIN_SIZE = (720, 720)
screen = pygame.display.set_mode(WIN_SIZE)

LEFT_TOP, MIDDLE_TOP, RIGHT_TOP = (0.0, 0.0), (0.5, 0.0), (1.0, 0.0)
LEFT_CENTER, MIDDLE_CENTER, RIGHT_CENTER = (0.0, 0.5), (0.5, 0.5), (1.0, 0.5)
LEFT_BOTTOM, MIDDLE_BOTTOM, RIGHT_BOTTOM = (0.0, 1.0), (0.5, 1.0), (1.0, 1.0)

font16 = pygame.font.Font('./minecraft.ttf', 16)
font32 = pygame.font.Font('./minecraft.ttf', 32)


def load_image(file_path: str, color_key: Color | int | None = None) -> Surface:
    if not os.path.isfile(file_path):
        print(f'Файл с изображением "{file_path}" не найден')
        exit()

    image = pygame.image.load(file_path)

    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()

    return image


def game_exit() -> None:
    pygame.quit()
    exit()


class Image:
    name: str
    is_selected: bool
    __source: Surface
    image: Surface
    position: Vector2
    size: tuple[float, float]
    rotation: float
    is_active: bool
    alignment: tuple[float, float]

    def __init__(self, name: str, image: Surface, alignment: tuple[float, float] = LEFT_TOP) -> None:
        self.name = name
        self.__source = image
        self.image = image
        self.position = Vector2(0.0, 0.0)
        self.size = image.get_size()
        self.rotation = 0.0
        self.is_active = True
        self.alignment = alignment

    def move(self, x: float, y: float) -> None:
        self.position += Vector2(x, y)

    def set_pos(self, x: float, y: float) -> None:
        self.position = Vector2(x, y)

    def resize(self, x: float, y: float) -> None:
        self.size = (x, y)
        self.apply_changes()

    def rotate(self, angle: float) -> None:
        self.rotation += angle
        self.apply_changes()

    def set_rotation(self, angle: float) -> None:
        self.rotation = angle
        self.apply_changes()

    def apply_changes(self) -> None:
        self.image = pygame.transform.scale(self.__source, self.size)
        self.image = pygame.transform.rotate(self.image, self.rotation)

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    @property
    def w(self) -> float:
        return self.image.get_size()[0]

    @property
    def h(self) -> float:
        return self.image.get_size()[1]

    @property
    def rect(self) -> Rect:
        return Rect(*self.left_top, self.w, self.h)

    @property
    def left_top(self) -> Vector2:
        return Vector2(self.x - self.alignment[0] * self.w, self.y - self.alignment[1] * self.h)

    def set_active(self, is_active: bool) -> None:
        self.is_active = is_active

    def show(self) -> None:
        self.is_active = True

    def hide(self) -> None:
        self.is_active = False

    def __contains__(self, point: tuple[float, float]) -> bool:
        if self.is_active is False:
            return False
        return 0 <= point[0] - self.position.x <= self.size[0] and 0 <= point[1] - self.position.y <= self.size[1]

    def mouse_button_down(self, button: int) -> None:
        pass

    def mouse_button_up(self, button: int) -> None:
        pass

    def mouse_enter(self) -> None:
        pass

    def mouse_on(self) -> None:
        pass

    def mouse_exit(self) -> None:
        pass

    def intersects(self, other) -> bool:
        if self.is_active is False:
            return False
        x1, y1, w1, h1 = self.rect
        x2, y2, w2, h2 = other.rect
        return not (x1 >= x2 + w2 or y1 >= y2 + h2 or x1 + w1 <= x2 or y1 + h1 <= y2)

    def mouse_button_down_check(self, button: int) -> None:
        if self.is_active and self.is_selected and pygame.mouse.get_pos() in self:
            self.mouse_button_down(button)

    def mouse_button_up_check(self, button: int) -> None:
        if self.is_active and self.is_selected and pygame.mouse.get_pos() in self:
            self.mouse_button_up(button)

    def mouse_move_check(self) -> None:
        if self.is_active is False:
            return
        if pygame.mouse.get_pos() in self:
            if self.is_selected:
                self.mouse_on()
            else:
                self.is_selected = True
                self.mouse_enter()
        else:
            if self.is_selected:
                self.is_selected = False
                self.mouse_exit()

    def delete(self) -> None:
        pass

    def update(self) -> None:
        pass

    def draw(self) -> None:
        if self.is_active is False:
            return
        screen.blit(self.image, self.rect)


class Sprite(Image):
    frames: list[Surface]
    current_frame: int

    def __init__(self, name: str, *images: Surface) -> None:
        super(Sprite, self).__init__(name, images[0])
        self.frames = list(images)
        self.current_frame = 0

    def add_frame(self, image: Surface) -> None:
        self.frames.append(image)

    def replace_frame(self, image: Surface, index: int) -> None:
        if index in range(len(self.frames)):
            self.frames[index] = image

    def delete_frame(self, index: int) -> None:
        if index in range(len(self.frames)):
            self.frames.pop(index)
            if index <= self.current_frame:
                self.current_frame -= 1
                self.image = self.frames[self.current_frame]

    def set_current_frame(self, index: int) -> None:
        if index in range(len(self.frames)):
            self.current_frame = index
            self.image = self.frames[self.current_frame]


class Button(Sprite):
    functions_down: dict = {pygame.BUTTON_LEFT: None,
                            pygame.BUTTON_RIGHT: None}
    functions_up: dict = {pygame.BUTTON_LEFT: None,
                          pygame.BUTTON_RIGHT: None}

    def __init__(self, name: str, image: Surface, selected: Surface, pressed: Surface) -> None:
        super(Button, self).__init__(name, image, selected, pressed)
        self.functions_down = Button.functions_down.copy()
        self.functions_up = Button.functions_up.copy()
        self.is_selected = False

    def set_function_down(self, button: int, function: ()) -> None:
        self.functions_down[button] = function

    def set_function_up(self, button: int, function: ()) -> None:
        self.functions_up[button] = function

    def mouse_enter(self) -> None:
        self.set_current_frame(1)

    def mouse_exit(self) -> None:
        self.set_current_frame(0)

    def mouse_button_down(self, button: int) -> None:
        self.set_current_frame(2)
        if self.functions_down[button] is not None:
            self.functions_down[button]()

    def mouse_button_up(self, button: int) -> None:
        self.set_current_frame(1)
        if self.functions_up[button] is not None:
            self.functions_up[button]()


_T = TypeVar('_T', bound=Image)


class Container:
    __game_objects: list[_T | Container, ...]
    __index: int

    def __init__(self, *game_objects: _T | Container) -> None:
        self.__game_objects = list(game_objects)
        self.__index = 0

    def __next__(self) -> _T:
        if self.__index + 1 < len(self.__game_objects):
            self.__index += 1
            return self.__game_objects[self.__index]
        raise StopIteration

    def __iter__(self):
        self.__index = 0
        return self

    def __len__(self) -> int:
        return len(self.__game_objects)

    def __getitem__(self, index: int) -> _T:
        return self.__game_objects[index]

    def __setitem__(self, index: int, value: _T) -> None:
        self.__game_objects[index] = value

    def sort(self, key: ()) -> None:
        self.__game_objects = sorted(self.__game_objects, key=key)

    def copy(self) -> Container:
        return Container(*self.__game_objects)

    def add_object(self, game_object: _T | Container) -> None:
        self.__game_objects.append(game_object)

    def remove_object(self, game_object: _T | Container) -> None:
        game_object.delete()
        self.__game_objects.remove(game_object)

    def set_active(self, is_active: bool) -> None:
        for game_object in self.__game_objects:
            game_object.set_active(is_active)

    def show(self) -> None:
        for game_object in self.__game_objects:
            game_object.show()

    def hide(self) -> None:
        for game_object in self.__game_objects:
            game_object.hide()

    def mouse_move_check(self) -> None:
        for game_object in self.__game_objects:
            game_object.mouse_move_check()

    def mouse_button_down_check(self, button: int) -> None:
        for game_object in self.__game_objects:
            game_object.mouse_button_down_check(button)

    def mouse_button_up_check(self, button: int) -> None:
        for game_object in self.__game_objects:
            game_object.mouse_button_up_check(button)

    def delete(self) -> None:
        for game_object in self.__game_objects:
            game_object.delete()
        self.__game_objects.clear()

    def update(self) -> None:
        for game_object in self.__game_objects:
            game_object.update()

    def draw(self) -> None:
        for game_object in self.__game_objects:
            game_object.draw()


def menu() -> int:
    global current_level, clock, delta_time, MAX_FPS

    def start() -> None:
        start_menu.hide()
        level_menu.show()

    def go_to_level_1() -> None:
        global current_level
        current_level = 1

    def go_to_level_2() -> None:
        global current_level
        current_level = 2

    def go_to_level_3() -> None:
        global current_level
        current_level = 3

    start_button = Button('start_button',
                          load_image('./textures/Start_Button_01.png'),
                          load_image('./textures/Start_Button_02.png'),
                          load_image('./textures/Start_Button_03.png'))
    start_button.move((WIN_SIZE[0] - start_button.w) / 2, WIN_SIZE[1] / 2 - start_button.h / 2 - 8)
    start_button.set_function_up(pygame.BUTTON_LEFT, start)
    exit_button = Button('exit_button',
                         load_image('./textures/Exit_Button_01.png'),
                         load_image('./textures/Exit_Button_02.png'),
                         load_image('./textures/Exit_Button_03.png'))
    exit_button.move((WIN_SIZE[0] - exit_button.w) / 2, WIN_SIZE[1] / 2 + exit_button.h / 2 + 8)
    exit_button.set_function_up(pygame.BUTTON_LEFT, game_exit)
    start_menu = Container(start_button, exit_button)

    level_1_button = Button('level_1_button',
                            load_image('./textures/Level_Button_01.png'),
                            load_image('./textures/Level_Button_02.png'),
                            load_image('./textures/Level_Button_03.png'))
    level_1_button.move((WIN_SIZE[0] - level_1_button.w) / 2, WIN_SIZE[1] / 2 - level_1_button.h / 2 * 3 - 8)
    level_1_button.set_function_up(pygame.BUTTON_LEFT, go_to_level_1)
    level_2_button = Button('level_2_button',
                            load_image('./textures/Level_Button_01.png'),
                            load_image('./textures/Level_Button_02.png'),
                            load_image('./textures/Level_Button_03.png'))
    level_2_button.move((WIN_SIZE[0] - level_2_button.w) / 2, WIN_SIZE[1] / 2 - level_2_button.h / 2)
    level_2_button.set_function_up(pygame.BUTTON_LEFT, go_to_level_2)
    level_3_button = Button('level_3_button',
                            load_image('./textures/Level_Button_01.png'),
                            load_image('./textures/Level_Button_02.png'),
                            load_image('./textures/Level_Button_03.png'))
    level_3_button.move((WIN_SIZE[0] - level_3_button.w) / 2, WIN_SIZE[1] / 2 + level_3_button.h / 2 + 8)
    level_3_button.set_function_up(pygame.BUTTON_LEFT, go_to_level_3)



    level_menu = Container(level_1_button, level_2_button, level_3_button)
    level_menu.hide()

    hierarchy.add_object(start_menu)
    hierarchy.add_object(level_menu)

    while True:
        if current_level != 0:
            return current_level

        clock.tick(MAX_FPS)
        start_time = now()

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    game_exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            return 0
                case pygame.MOUSEMOTION:
                    hierarchy.mouse_move_check()
                case pygame.MOUSEBUTTONDOWN:
                    hierarchy.mouse_button_down_check(event.button)
                case pygame.MOUSEBUTTONUP:
                    hierarchy.mouse_button_up_check(event.button)

        hierarchy.update()
        hierarchy.draw()

        pygame.display.flip()

        delta_time = now() - start_time


# -------------------------------- Level 1 --------------------------------


def level_1() -> int:
    global current_level, clock, delta_time, MAX_FPS

    def win() -> None:
        global current_level
        current_level = 0

    def start_new_game() -> None:
        balls.delete()
        bricks.delete()
        upgrades.delete()

        spawn_bricks()
        spawn_ball()

        Ball.radius = 16.0
        Ball.speed = 256.0
        board.resize(128, 16)
        board.move(pygame.mouse.get_pos()[0] - board.w / 2.0, WIN_SIZE[1] - board.h - 4.0)

    # ---------------- Bricks ----------------

    def spawn_bricks() -> None:
        bricks.delete()

        brick_offset = (4, 4)
        brick_size = (32, 16)
        row_count = WIN_SIZE[1] // 2 // (brick_size[1] + brick_offset[1])
        column_count = WIN_SIZE[0] // (brick_size[0] + brick_offset[0])
        brick_offset = (WIN_SIZE[0] / column_count - brick_size[0], WIN_SIZE[1] / 2 / row_count - brick_size[1])

        for x in range(column_count):
            for y in range(row_count):
                brick = Image(f'brick_{x}_{y}', brick_image)
                brick.move(brick_offset[0] * (x + 0.5) + brick_size[0] * x,
                           brick_offset[1] * (y + 0.5) + brick_size[1] * y)
                brick.resize(*brick_size)
                bricks.add_object(brick)

    bricks = Container()
    brick_image = load_image('./textures/Brick.png')

    # ---------------- Balls ----------------

    class Ball(Image):
        image = load_image('textures/Ball.png')
        radius: float = 16.0
        speed: float = 256.0

        angle: float

        def __init__(self) -> None:
            super(Ball, self).__init__('ball', Ball.image)
            self.angle = -(random() * pi / 2.0 + pi / 4.0)
            self.resize(Ball.radius * 2.0, Ball.radius * 2.0)

        def set_rotation(self, angle: float) -> None:
            self.angle = angle

        def intersects(self, other) -> bool:
            x, y, w, h = other.rect
            center = (self.x + self.w / 2.0, self.y + self.h / 2.0)

            x = max(x, min(center[0], x + w))
            y = max(y, min(center[1], y + h))
            distance = (x - center[0]) ** 2 + (y - center[1]) ** 2
            return distance <= Ball.radius ** 2

        def update(self) -> None:
            move = Vector2(cos(self.angle), sin(self.angle)) * Ball.speed * delta_time
            if move:
                self.position += move.clamp_magnitude(WIN_SIZE[0] / 2.0)
            if self.x <= 0.0 or WIN_SIZE[0] <= self.x + self.w:
                self.angle = pi - self.angle
                self.position.x = max(0.0, min(self.position.x, WIN_SIZE[0] - self.w))
            if self.y <= 0.0:
                self.angle = -self.angle
                self.position.y = 0.0

            for brick in bricks:
                if self.intersects(brick):
                    self.angle = -abs(self.angle % (pi * 2.0))
                    if randint(0, 19) == 0:
                        upgrades.add_object(Upgrade(randint(0, 2), brick.position))
                    bricks.remove_object(brick)
                    if len(bricks) == 0:
                        win()
                    break

            if self.intersects(board):
                ratio = (self.x + self.w / 2.0 - board.left_top.x + Ball.radius) / (board.w + Ball.radius * 2.0)
                self.angle = pi + ratio * pi

            if self.y >= WIN_SIZE[1]:
                balls.remove_object(self)
                if len(balls) == 0:
                    start_new_game()

    def spawn_ball(x: float = WIN_SIZE[0] / 2.0 - Ball.radius,
                   y: float = WIN_SIZE[1] - Ball.radius * 6.0,
                   angle: float = -pi / 2.0) -> None:
        ball = Ball()
        ball.move(x, y)
        if angle is not None:
            ball.set_rotation(angle)
        balls.add_object(ball)

    balls = Container()

    # ---------------- Board ----------------

    class Board(Image):
        def update(self) -> None:
            destination = Vector2(pygame.mouse.get_pos()[0], WIN_SIZE[1] - self.h - 4.0)
            destination.x = max(board.w / 2.0, min(destination.x, WIN_SIZE[0] - board.w / 2.0))
            self.position = self.position.lerp(destination, min(1.0, delta_time * 10.0))

    board = Board('board', load_image('./textures/Brick.png'), MIDDLE_TOP)

    # ---------------- Upgrades ----------------

    class Upgrade(Image):
        upgrade_images = (load_image('textures/Ball_Upgrade_01.png'),
                          load_image('textures/Ball_Upgrade_02.png'),
                          load_image('textures/Ball_Upgrade_03.png'))
        type: int

        def __init__(self, type: int, position: Vector2) -> None:
            super(Upgrade, self).__init__(f'upgrade_{type}', Upgrade.upgrade_images[type])
            self.resize(32, 32)
            self.move(position.x, position.y)
            self.type = type

        def update(self) -> None:
            self.move(0, 100 * delta_time)
            if self.intersects(board):
                match self.type:
                    case 0:
                        if len(balls) < 128:
                            for ball in balls.copy():
                                spawn_ball(ball.x, ball.y, random() * pi * 2.0)
                                spawn_ball(ball.x, ball.y, random() * pi * 2.0)
                    case 1:
                        if len(balls) < 128:
                            for _ in range(3):
                                spawn_ball(board.x + board.w / 2.0,
                                           board.y - Ball.radius * 2.0,
                                           -(random() * pi / 2.0 + pi / 4.0))
                    case 2:
                        board.resize(board.w + 16.0, board.h)
                upgrades.remove_object(self)

    upgrades = Container()

    # ---------------- Start ----------------

    hierarchy.add_object(balls)
    hierarchy.add_object(bricks)
    hierarchy.add_object(board)
    hierarchy.add_object(upgrades)
    start_new_game()

    # ---------------- Loop ----------------

    while True:
        if current_level != 1:
            return current_level
        clock.tick(MAX_FPS)

        start_time = now()

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    game_exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            return 0

        hierarchy.update()
        hierarchy.draw()

        pygame.display.flip()

        delta_time = max(now() - start_time, 1.0 / MAX_FPS)


# -------------------------------- Level 2 --------------------------------


def level_2() -> int:
    global current_level, clock, delta_time, MAX_FPS

    def win() -> None:
        global current_level
        current_level = 0

    def start_new_game() -> None:
        global timer
        timer = 0.0
        player.score = 0
        player.set_pos(WIN_SIZE[0] / 2.0, floor.y - player.h)
        player.reset_upgrades()
        bullets.delete()
        balls.delete()
        upgrades.delete()

    floor = Image('floor', load_image('./textures/Brick.png'), MIDDLE_TOP)
    floor.resize(WIN_SIZE[0] * 2.0, WIN_SIZE[1] / 8.0)
    floor.move(WIN_SIZE[0] / 2.0, WIN_SIZE[1] - floor.h)

    # ---------------- Player ----------------

    class Player(Image):
        image = load_image('./textures/hopper.png')
        background = load_image('./textures/Brick.png')
        max_laser_timer = 10.0
        max_shield_timer = 10.0

        damage: int

        bullet_speed: float
        bullet_timer: float

        is_shield: bool
        shield_timer: float

        is_laser: bool
        laser_timer: float

        is_move: bool

        score: int
        text: Surface

        def __init__(self) -> None:
            super(Player, self).__init__('player', Player.image, MIDDLE_TOP)
            self.resize(26 * 2, 26 * 2)
            self.background = pygame.transform.scale(Player.background, self.size)
            self.position = Vector2(WIN_SIZE[0] / 2.0, floor.y - self.h)

            self.damage = 100

            self.bullet_speed = 1
            self.bullet_timer = 0.0

            self.shield_timer = 0.0

            self.laser_timer = 0.0

            self.is_move = False

            self.score = 0
            self.text = font32.render(f'{self.score:>8}/1000', False, (255, 255, 255))

        def update(self) -> None:
            if self.is_move:
                self.position.x = max(self.w / 2.0, min(pygame.mouse.get_pos()[0] * 1.0, WIN_SIZE[0] - self.w / 2.0))

            if self.laser_timer > 0.0:
                pygame.draw.rect(screen, (255, 0, 0),
                                 (self.left_top.x + self.w / 4.0, 0.0, self.w / 2.0, WIN_SIZE[1]))
                pygame.draw.rect(screen, (255, 127, 127),
                                 (self.left_top.x + self.w / 3.0, 0.0, self.w / 3.0, WIN_SIZE[1]))
            elif self.is_move:
                if player.bullet_timer >= 1.0 / player.bullet_speed:
                    player.bullet_timer %= 1.0 / player.bullet_speed
                    bullets.add_object(Bullet())
                player.bullet_timer += delta_time

            spawn_cooldown = abs(sin(timer * pi / 20.0)) * 2.0 + 1.0
            if Ball.spawn_timer >= spawn_cooldown:
                Ball.spawn_timer -= spawn_cooldown
                balls.add_object(Ball())
            Ball.spawn_timer += delta_time

            player.shield_timer = max(player.shield_timer - delta_time, 0.0)
            player.laser_timer = max(player.laser_timer - delta_time, 0.0)

        def reset_upgrades(self) -> None:
            self.laser_timer = 0.0
            self.shield_timer = 0.0
            self.bullet_speed = 1.0
            self.damage = 1

        def add_score(self, score: int) -> None:
            self.score += score
            if self.score >= 1000:
                win()
            self.text = font32.render(f'{self.score:>8}/1000', False, (255, 255, 255))

        def draw(self) -> None:
            if self.is_active is False:
                return
            screen.blit(self.background, self.left_top)
            super(Player, self).draw()
            screen.blit(self.text, self.text.get_rect().move(16.0, 16.0))
            if player.shield_timer >= 2.0 or 0.0 < player.shield_timer % 1.0 < 0.25:
                pygame.draw.circle(screen, (255, 255, 255), (player.x, floor.y), player.w * 2, width=16)

    player = Player()

    # ---------------- Bullet ----------------

    class Bullet(Image):
        image = load_image('./textures/gold_nugget.png')

        def __init__(self) -> None:
            super(Bullet, self).__init__('bullet', Bullet.image, MIDDLE_TOP)
            self.resize(10, 14)
            self.move(player.x, player.y)

        def update(self) -> None:
            self.move(0, -256.0 * delta_time)
            if self.y + self.h <= 0.0:
                bullets.remove_object(self)

    bullets = Container()

    # ---------------- Ball ----------------

    class Ball(Image):
        image = load_image('textures/Ball.png')
        bonus_image = load_image('./textures/heart_of_the_sea.png')
        g = 160.0

        spawn_timer = 0.0

        velocity: Vector2
        radius: float
        health: int
        text: Surface
        type: int

        damage_cooldown: float

        def __init__(self, parameters: tuple[int, bool, Vector2] | None = None) -> None:
            self.velocity = Vector2(random() * 16.0 + 16.0, 0.0)

            if parameters is not None:
                self.type = parameters[0]
                super(Ball, self).__init__('ball', Ball.image if self.type != 2 else Ball.bonus_image, MIDDLE_CENTER)
                side = parameters[1]
                if side:
                    self.velocity *= -1
                self.position = parameters[2]
                self.radius = 64 if self.type != 0 else 32
            else:
                self.type = 0 if random() >= 0.1 else (1 if random() >= 0.1 else 2)
                super(Ball, self).__init__('ball', Ball.image if self.type != 2 else Ball.bonus_image, MIDDLE_CENTER)
                side = random() > 0.5

                self.radius = 64 if self.type != 0 else 32
                if side:
                    self.position.x = randint(WIN_SIZE[0] + int(self.radius), WIN_SIZE[0] * 2 - int(self.radius))
                    self.velocity *= -1
                else:
                    self.position.x = randint(-WIN_SIZE[0] + int(self.radius), -int(self.radius))
                ratio = (abs(self.velocity.x) - 16.0) / 16.0 / 2.0
                self.position.y = (floor.y - self.h) * ratio

            self.resize(self.radius * 2, self.radius * 2)

            self.health = round(timer / 32.0 + 1.0)
            self.text = font32.render(str(self.health), False, (255, 255, 255))
            self.damage_cooldown = 0.0

        def hit(self, damage: int) -> None:
            if self.damage_cooldown > 0.0:
                return
            player.add_score(min(damage, self.health))
            self.health -= damage
            self.text = font32.render(str(self.health), False, (255, 255, 255))
            if self.health <= 0:
                balls.remove_object(self)
                if random() < 0.05 or self.type == 2:
                    upgrades.add_object(Upgrade(randint(0, 3), self.position))
                if self.type == 1:
                    balls.add_object(Ball((0, True, self.position + Vector2(-self.radius / 2.0, 0.0))))
                    balls.add_object(Ball((0, False, self.position + Vector2(self.radius / 2.0, 0.0))))

        def intersects(self, other) -> bool:
            x, y, w, h = other.rect

            x = max(x, min(self.x, x + w))
            y = max(y, min(self.y, y + h))

            distance = (x - self.x) ** 2 + (y - self.y) ** 2
            return distance <= self.radius * self.radius

        def update(self) -> None:
            self.position += self.velocity * delta_time
            self.velocity.y += Ball.g * delta_time
            self.rotate(2.0 * pi * -self.velocity.x / (2.0 * pi * self.radius))

            if self.x + self.radius > WIN_SIZE[0] * 2 or -WIN_SIZE[0] > self.x - self.radius:
                balls.remove_object(self)
                return

            if self.y + self.radius >= floor.y:
                self.velocity.y = -abs(self.velocity.y)

            if self.intersects(player) and player.shield_timer == 0.0:
                start_new_game()

            for bullet in bullets:
                if self.intersects(bullet):
                    bullets.remove_object(bullet)
                    self.hit(player.damage)

            if player.laser_timer > 0.0 and abs(self.x - player.x) < self.radius + player.w / 2.0:
                self.hit(player.damage)
                self.damage_cooldown = 0.5

            self.damage_cooldown = max(self.damage_cooldown - delta_time, 0.0)

        def draw(self) -> None:
            if self.is_active is False:
                return
            super(Ball, self).draw()
            screen.blit(self.text, self.text.get_rect(center=self.position))

    balls = Container()

    # ---------------- Upgrade ----------------

    class Upgrade(Image):
        images = (load_image('./textures/Bullet_Upgrade_01.png'),
                  load_image('./textures/Bullet_Upgrade_02.png'),
                  load_image('./textures/Bullet_Upgrade_03.png'),
                  load_image('./textures/Bullet_Upgrade_04.png'))
        g: float = 160.0

        type: int
        velocity: Vector2

        def __init__(self, type: int, position: Vector2) -> None:
            super(Upgrade, self).__init__(f'upgrade_{type}', Upgrade.images[type], MIDDLE_TOP)
            self.velocity = Vector2(0.0, 0.0)
            self.position = position
            self.type = type
            self.resize(32, 32)

        def update(self) -> None:
            self.position.y += self.velocity.y * delta_time
            self.velocity.y += Upgrade.g * delta_time

            if self.x >= WIN_SIZE[1]:
                upgrades.remove_object(self)
                return

            if self.intersects(player):
                match self.type:
                    case 0:
                        player.bullet_speed *= 1.1
                    case 1:
                        player.damage += 1
                    case 2:
                        player.laser_timer = player.max_laser_timer
                    case 3:
                        player.shield_timer = player.max_shield_timer
                upgrades.remove_object(self)

    upgrades = Container()

    # ---------------- Start ----------------

    hierarchy.add_object(upgrades)
    hierarchy.add_object(bullets)
    hierarchy.add_object(player)
    hierarchy.add_object(balls)
    hierarchy.add_object(floor)
    start_new_game()

    # ---------------- Loop ----------------

    timer = 0.0
    while True:
        if current_level != 2:
            return current_level
        clock.tick(MAX_FPS)

        start_time = now()

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    game_exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            return 0
                case pygame.MOUSEBUTTONDOWN:
                    player.is_move = True
                case pygame.MOUSEBUTTONUP:
                    player.is_move = False

        hierarchy.update()
        hierarchy.draw()

        pygame.display.flip()

        delta_time = max(now() - start_time, 1.0 / MAX_FPS)
        timer += delta_time


# -------------------------------- Level 2 --------------------------------


def level_3() -> int:
    global current_level, clock, delta_time, MAX_FPS

    def win() -> None:
        global current_level
        current_level = 0

    def start_new_game() -> None:
        cells.sort(key=lambda x: x.mass)

    food = Container()
    cells = Container()
    entities = Container()

    # ---------------- Cell ----------------

    class Cell(Image):
        empty_image = pygame.transform.scale(load_image('./textures/Ball.png'), (0, 0))

        food_timer: float = 0.0
        food_cooldown: float = 1.0

        entity: Entity

        mass: int
        radius: float
        sqr_radius: float
        point_count: int
        points: list[Vector2, ...]
        speed: float

        color: Color
        border_color: Color

        text: Surface

        @classmethod
        def get_predators(cls, mass: int) -> list:
            index = len(cells) - 1
            while cells[index].mass > mass + 1024 and index + 1 < len(cells):
                index += 1
            return cells[index + 1:]

        @classmethod
        def get_near_predators(cls, mass: int, position: Vector2) -> list:
            return list(filter(lambda x: position.distance_squared_to(x.position) <= x.sqr_radius * 16.0,
                               cls.get_predators(mass)))

        @classmethod
        def get_preys(cls, mass: int) -> list:
            index = 0
            while cells[index].mass + 1024 < mass:
                index += 1
            return cells[:index]

        @classmethod
        def get_near_preys(cls, mass: int, position: Vector2) -> list:
            return list(filter(lambda x: position.distance_squared_to(x.position) <= cls.get_radius(mass) ** 2 * 16.0,
                               cls.get_preys(mass)))

        @classmethod
        def get_nearest_prey(cls, mass: int, position: Vector2) -> Cell:
            return min(cls.get_preys(mass), key=lambda x: position.distance_squared_to(x.position))

        @classmethod
        def get_most_perspective_prey(cls, mass: int, position: Vector2) -> Cell:
            return max(Cell.get_near_preys(mass, position), key=lambda x: x.mass)

        @classmethod
        def get_radius(cls, mass: int) -> float:
            return (mass / pi) ** 0.5

        @classmethod
        def get_point_count(cls, radius: float) -> int:
            return round(2.0 * pi * radius / 10.0 + 8.0)

        def __init__(self, entity: Entity, position: Vector2, color: Color, mass: int = 16) -> None:
            super(Cell, self).__init__('cell', Cell.empty_image, MIDDLE_CENTER)
            self.entity = entity
            cells.add_object(self)

            self.position = position
            self.color = color
            if color.r * color.g * color.b > 127 * 127 * 127:
                self.border_color = color.lerp((0, 0, 0), 0.25)
            else:
                self.border_color = color.lerp((0, 0, 0), 0.25)
            self.mass = mass

            self.radius = Cell.get_radius(self.mass)
            self.sqr_radius = self.radius * self.radius
            self.point_count = Cell.get_point_count(self.mass)
            self.points = [self.position.copy() for _ in range(self.point_count)]

            self.speed = 1024.0 / self.mass ** 0.5

            self.update_text()

        @property
        def inv_color(self) -> Color:
            return Color(255 - self.color.r, 255 - self.color.g, 255 - self.color.b)

        def update_text(self) -> None:
            self.text = font16.render(str(self.mass), False, self.inv_color)

        def intersects(self, other: Cell) -> bool:
            return self.position.distance_squared_to(other.position) < (self.radius + other.radius) ** 2

        def change_mass(self, change: int) -> None:
            self.mass += change
            self.update_text()
            self.update_values()

        def update_values(self) -> None:
            self.radius = Cell.get_radius(self.mass)
            self.sqr_radius = self.radius * self.radius
            self.point_count = Cell.get_point_count(self.mass)
            for _ in range(self.point_count - len(self.points)):
                self.points.append(self.points[-1].copy())
            self.speed = 1024.0 / self.mass ** 0.5
            cells.sort(key=lambda x: x.mass)

        def move_points(self) -> None:
            for n, point in enumerate(self.points):
                angle = n / self.point_count * pi * 2.0
                destination = Vector2(cos(angle), sin(angle)) * self.radius + self.position
                destination.x = max(0.0, min(destination.x, WIN_SIZE[0]))
                destination.y = max(0.0, min(destination.y, WIN_SIZE[1]))
                if 0.0 < self.position.distance_squared_to(destination) <= self.sqr_radius / 4.0:
                    destination = (destination - self.position).normalize() * (self.radius / 2.0) + self.position
                self.points[n] = point.lerp(destination, min(delta_time * 2.0, 1.0))

        def move_cell(self, destination: Vector2) -> None:
            if self.position == destination:
                return
            direction = (destination - self.position).clamp_magnitude(self.speed * delta_time)
            self.position += direction
            for point in self.points:
                point += direction

        def update(self):
            self.move_cell(self.entity.destination)
            self.position.x = max(0.0, min(self.position.x, WIN_SIZE[0]))
            self.position.y = max(0.0, min(self.position.y, WIN_SIZE[1]))
            self.move_points()

        def draw(self) -> None:
            pygame.draw.polygon(screen, self.color, self.points)
            pygame.draw.polygon(screen, self.border_color, self.points, width=4)
            if self.mass >= 1024.0:
                screen.blit(self.text, self.text.get_rect(center=self.position))

    class Entity(Image):
        cell_count: int
        cells: list[Cell, ...]
        color: Color
        destination: Vector2

        def __init__(self, position: Vector2 | None = None, color: Color | None = None, mass: int = 16) -> None:
            super(Entity, self).__init__('Entity', Cell.empty_image)

            if position is None:
                self.position = Vector2(randint(0, WIN_SIZE[0]), randint(0, WIN_SIZE[1]))
            else:
                self.position = position

            if color is None:
                # x, y = random() * pi, random() * pi
                # self.color = Color(
                #     int(abs(cos(x) * sin(y)) ** 0.5 * 255) & int(abs(cos(x) * sin(x)) ** 0.5 * 255),
                #     int(abs(cos(x) * sin(y)) ** 0.5 * 255) & int(abs(cos(y) * sin(x)) ** 0.5 * 255),
                #     int(abs(cos(x) * sin(y)) ** 0.5 * 255) & int(abs(cos(y) * sin(y)) ** 0.5 * 255)
                # )
                self.color = Color(randint(0, 255), randint(0, 255), randint(0, 255))
            else:
                self.color = color

            self.cell_count = 2
            self.cells = [Cell(self, self.position + Vector2(i, i), self.color, mass) for i in range(2)]

            self.destination = self.position

        def add_direction(self, direction: Vector2, coefficient: float) -> None:
            self.destination += direction * coefficient

        def push_away(self) -> None:
            if self.cell_count == 1:
                return
            for i, cell1 in enumerate(self.cells):
                for cell2 in self.cells[i + 1:]:
                    if not cell1.intersects(cell2):
                        continue
                    direction = cell2.position - cell1.position
                    if direction.x == 0 or direction == 0:
                        continue

                    mass = cell1.mass + cell2.mass
                    distance = cell1.radius + cell2.radius - direction.magnitude()
                    direction.scale_to_length(distance)

                    cell1.move_cell(-direction * (cell2.mass / mass))
                    cell2.move_cell(direction * (cell2.mass / mass))

        def update(self) -> None:
            for cell in self.cells:
                cell.update()

    class Player(Entity):
        def update(self) -> None:
            super(Player, self).update()

            self.destination = Vector2(pygame.mouse.get_pos())
            for cell in self.cells:

                preys = [i for i in cells if i.mass * 1.125 < cell.mass]
                if len(preys) > 0:
                    prey = min(preys, key=lambda x: x.position.distance_squared_to(cell.position))
                    if prey.position.distance_squared_to(cell.position) <= cell.sqr_radius / 4.0:
                        cell.change_mass(prey.mass)
                        cells.remove_object(prey)

            if Cell.food_timer >= Cell.food_cooldown:
                Cell.food_timer -= Cell.food_cooldown
            Cell.food_timer += delta_time

            self.push_away()

    player = Player(Vector2(WIN_SIZE[0] / 2.0, WIN_SIZE[1] / 2.0), Color(255, 0, 0), 4096)
    entities.add_object(player)

    class Enemy(Entity):
        def update(self) -> None:
            super(Enemy, self).update()

            for cell in self.cells:
                predators = Cell.get_near_predators(cell.mass, cell.position)
                if len(predators) > 0:
                    target = Vector2(0.0, 0.0)
                    for i in predators:
                        target -= i
                    self.add_direction(target, 2.0)
                    continue

                preys = Cell.get_near_preys(cell.mass, cell.position)
                if len(preys) > 0:
                    prey = max(preys, key=lambda x: x.mass)
                    self.add_direction(prey.position, 1.0 / self.cell_count * 2.0)
                    continue

    for _ in range(10):
        entities.add_object(Enemy(mass=512))

    # ---------------- Start ----------------

    hierarchy.add_object(entities)
    hierarchy.add_object(cells)
    start_new_game()

    # ---------------- Loop ----------------

    while True:
        if current_level != 3:
            return current_level
        clock.tick(MAX_FPS)

        start_time = now()

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    game_exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            return 0

        hierarchy.update()
        hierarchy.draw()

        pygame.display.flip()

        delta_time = max(now() - start_time, 1.0 / MAX_FPS)


levels = (menu, level_1, level_2, level_3)
current_level = 0
hierarchy = Container()
MAX_FPS = 144
delta_time = 1.0 / MAX_FPS
clock = pygame.time.Clock()

while True:
    current_level = levels[current_level]()
    hierarchy.delete()
