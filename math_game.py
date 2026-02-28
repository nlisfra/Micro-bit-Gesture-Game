import pygame
import os
import random
import math
from pygame import Rect

from modes import QUESTIONS_BY_OPERATION, OPERATION_INFO

SCREEN_W, SCREEN_H = 1600, 900
FPS = 60

BACKGROUND_IMG = "assets/background.jpg"
DIVISION_BG_IMG = "assets/foods/dapur.jpg"
MULTIPLICATION_BG_IMG = "assets/toys/ruangan.jpg"
MATH_TITLE_IMG = "assets/math_title.png"
TROPHY_IMG = "assets/trophy.png"
BGKU_IMG = "assets/bgkurang.jpg"

GIRAFFE_IMG = "assets/animals/giraffe.png"
BEAR_IMG = "assets/animals/bear.png"
ELEPHANT_IMG = "assets/animals/elephant.png"
RABBIT_IMG = "assets/animals/rabbit.png"
BUAYA_IMG = "assets/animals/buaya.png"

APPLE_IMG = "assets/foods/apple.png"
BANANA_IMG = "assets/foods/banana.png"
PIZZA_IMG = "assets/foods/pizza.png"
FISH_IMG = "assets/foods/fish.png"
DONUT_IMG = "assets/foods/donut.png"
PLATE_IMG = "assets/foods/plate.png"
WADAH_IMG = "assets/foods/wadah.png"

BALL_IMG = "assets/toys/ball.png"
CAR_IMG = "assets/toys/car.png"
DOLL_IMG = "assets/toys/doll.png"
BLOCK_IMG = "assets/toys/block.png"
ROBOT_IMG = "assets/toys/robot.png"
RAK_IMG = "assets/toys/rak.jpg"
KARDUS_IMG = "assets/toys/kardus.jpg"
HOME_IMG = "assets/home.png"

TUT_ICON_BACA     = "assets/baca.png"
TUT_ICON_OBJECT   = "assets/object.png"
TUT_ICON_MICROBIT = "assets/microbit.png"
TUT_ICON_JAWAB    = "assets/tanyajawab.png"

YELLOW = (255, 193, 7)
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GREEN = (84, 214, 126)
RED = (240, 80, 80)
BLUE = (52, 152, 219)
ORANGE = (243, 156, 18)
PURPLE = (142, 68, 173)

RESET_BTN_COLOR = (200, 30, 30)
RESET_BTN_HOVER = (230, 50, 50)
START_BTN_COLOR = (255, 200, 50)
START_BTN_HOVER = (255, 220, 80)
NEXT_BTN_COLOR = (100, 255, 100)
NEXT_BTN_HOVER = (130, 255, 130)

UI_BG = (255, 197, 51)
BG_FALLBACK = (100, 180, 255)
STORY_BOX_BG = (40, 100, 200)
STORY_BOX_BORDER = (255, 255, 255)
MENU_BG = (240, 248, 255)
MENU_BOX = (70, 130, 220)

SCORE_PER_CORRECT = 10
BLOCK_SIZE = (220, 130)
ANSWER_Y = 450
ANSWER_XS = [400, 800, 1200]
OBJECTS_AREA_Y = 750
OBJECTS_AREA_HEIGHT = 200
OBJECTS_BOTTOM = OBJECTS_AREA_Y + OBJECTS_AREA_HEIGHT
GROUND_LINE = OBJECTS_BOTTOM
AUTO_NEXT_DELAY_MS = 1200

TUTORIAL_DATA = {
    "addition": {
        "title": "PANDUAN PENJUMLAHAN",
        "color": (52, 152, 219),
        "steps": [
            {
                "icon_key": "baca",
                "judul": "Baca Soal Cerita",
                "isi": "Soal akan muncul di kotak biru atas layar.\nBaca baik-baik setiap baris ceritanya!",
            },
            {
                "icon_key": "microbit",
                "judul": "Goyang Micro:bit",
                "isi": "Goyang micro:bit untuk memunculkan hewan\nsatu per satu sesuai cerita.",
            },
            {
                "icon_key": "object",
                "judul": "Gerakkan Tangan",
                "isi": "Tekan tombol A di micro:bit lalu\ngerakkan tangan untuk memprediksi\njawaban yang benar.",
            },
            {
                "icon_key": "jawab",
                "judul": "Submit Jawaban",
                "isi": "Tekan tombol B di micro:bit untuk\nsubmit jawaban. Benar +10 poin,\nsalah tetap 0!",
            },
        ],
    },
    "subtraction": {
        "title": "PANDUAN PENGURANGAN",
        "color": (231, 76, 60),
        "steps": [
            {
                "icon_key": "baca",
                "judul": "Baca Soal Cerita",
                "isi": "Soal cerita akan tampil di kotak biru atas.\nPerhatikan berapa hewan yang ada di awal!",
            },
            {
                "icon_key": "microbit",
                "judul": "Goyang Micro:bit",
                "isi": "Goyang micro:bit untuk memunculkan semua\nhewan sesuai jumlah di cerita.",
            },
            {
                "icon_key": "object",
                "judul": "Gerakkan Tangan",
                "isi": "Tekan tombol A di micro:bit lalu\ngerakkan tangan untuk memprediksi\njawaban yang benar.",
            },
            {
                "icon_key": "jawab",
                "judul": "Submit Jawaban",
                "isi": "Tekan tombol B di micro:bit untuk\nsubmit jawaban. Benar +10 poin,\nsalah tetap 0!",
            },
        ],
    },
    "multiplication": {
        "title": "PANDUAN PERKALIAN",
        "color": (39, 174, 96),
        "steps": [
            {
                "icon_key": "baca",
                "judul": "Baca Soal Cerita",
                "isi": "Soal akan muncul di kotak biru atas layar.\nBaca baik-baik setiap baris ceritanya!",
            },
            {
                "icon_key": "microbit",
                "judul": "Goyang Micro:bit",
                "isi": "Goyang micro:bit untuk memunculkan rak\nsatu per satu sesuai jumlah kelompok.",
            },
            {
                "icon_key": "object",
                "judul": "Gerakkan Tangan",
                "isi": "Tekan tombol A di micro:bit lalu\ngerakkan tangan untuk memprediksi\njawaban yang benar.",
            },
            {
                "icon_key": "jawab",
                "judul": "Submit Jawaban",
                "isi": "Tekan tombol B di micro:bit untuk\nsubmit jawaban. Benar +10 poin,\nsalah tetap 0!",
            },
        ],
    },
    "division": {
        "title": "PANDUAN PEMBAGIAN",
        "color": (142, 68, 173),
        "steps": [
            {
                "icon_key": "baca",
                "judul": "Baca Soal Cerita",
                "isi": "Soal akan muncul di kotak biru atas layar.\nBaca baik-baik setiap baris ceritanya!",
            },
            {
                "icon_key": "microbit",
                "judul": "Goyang Micro:bit",
                "isi": "Goyang micro:bit untuk memunculkan\nmakanan satu per satu sesuai cerita.",
            },
            {
                "icon_key": "object",
                "judul": "Gerakkan Tangan",
                "isi": "Tekan tombol A di micro:bit lalu\ngerakkan tangan untuk memprediksi\njawaban yang benar.",
            },
            {
                "icon_key": "jawab",
                "judul": "Submit Jawaban",
                "isi": "Tekan tombol B di micro:bit untuk\nsubmit jawaban. Benar +10 poin,\nsalah tetap 0!",
            },
        ],
    },
}


def load_image_safe(path, size=None):
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception:
            img = pygame.image.load(path)
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    return None

def load_font_try(names_sizes):
    found = None
    for name in ["Jersey20-Regular.ttf", "jersey20.ttf"]:
        if os.path.exists(name):
            found = name
            break
    fonts = {}
    for key, size in names_sizes.items():
        if found:
            fonts[key] = pygame.font.Font(found, size)
        else:
            fonts[key] = pygame.font.SysFont("Arial", size, bold=True)
    return fonts

def draw_rounded_rect(surf, rect, color, radius=12, border_color=None, border_w=0):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border_color and border_w > 0:
        pygame.draw.rect(surf, border_color, rect, width=border_w, border_radius=radius)

def format_mmss(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"


class GameObject:
    def __init__(self, img, x, y, obj_type):
        self.image = img
        self.type = obj_type
        self.target_x = x
        self.target_y = y
        self.x = x
        self.y = y - 50
        self.alpha = 0
        self.appearing = True
        self.scale = 0.5
        self.removing = False
        self.total_groups = 0
        self.items_per_group = 0
        self.object_type = None
        self.leaving = False
        self.leave_speed = 4
        self.gone = False
        if img:
            self.width = img.get_width()
            self.height = img.get_height()
        else:
            self.width = 120
            self.height = 120

    def update(self):
        if self.appearing:
            self.alpha = min(255, self.alpha + 15)
            self.scale = min(1.0, self.scale + 0.05)
            if self.y < self.target_y:
                self.y += 3
            if self.alpha >= 255 and self.scale >= 1.0 and self.y >= self.target_y:
                self.appearing = False
                self.y = self.target_y
        if self.leaving:
            self.x += self.leave_speed
            self.leave_speed = min(self.leave_speed + 0.5, 14)
            if self.x > SCREEN_W + 150:
                self.gone = True
        if self.removing:
            self.alpha -= 15
            if self.alpha <= 0:
                self.alpha = 0

    def draw(self, surf):
        if self.image and self.alpha > 0:
            scaled_w = int(self.width * self.scale)
            scaled_h = int(self.height * self.scale)
            scaled_img = pygame.transform.smoothscale(self.image, (scaled_w, scaled_h))
            scaled_img.set_alpha(self.alpha)
            draw_x = int(self.x - scaled_w / 2)
            draw_y = int(self.y - scaled_h)
            surf.blit(scaled_img, (draw_x, draw_y))


class MultiplicationGroup:
    def __init__(self, container_img, item_img, x, y):
        self.container_img = container_img
        self.item_img = item_img
        self.target_x = x
        self.target_y = y
        self.x = x
        self.y = y + 80
        self.alpha = 0
        self.scale = 0.6
        self.appearing = True
        self.items_to_fill = 0
        self.current_items = 0
        self.fill_timer = 0
        self.width = 240
        self.height = 200

    def start_fill(self, total_items):
        self.items_to_fill = total_items
        self.current_items = 0
        self.fill_timer = 0

    def update(self, dt):
        if self.appearing:
            self.alpha = min(255, self.alpha + 20)
            self.scale = min(1.0, self.scale + 0.05)
            self.y -= 6
            if self.y <= self.target_y:
                self.y = self.target_y
            if self.alpha >= 255 and self.scale >= 1.0:
                self.appearing = False
        if self.current_items < self.items_to_fill:
            self.fill_timer += dt
            if self.fill_timer > 300:
                self.current_items += 1
                self.fill_timer = 0

    def draw(self, surf):
        base = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if self.container_img:
            cont = pygame.transform.smoothscale(self.container_img, (220, 120))
            base.blit(cont, (10, 70))
        cols = 4
        start_x = 40
        start_y = 85
        spacing_x = 40
        spacing_y = 35
        for i in range(self.current_items):
            col = i % cols
            row = i // cols
            item = pygame.transform.smoothscale(self.item_img, (45, 45))
            base.blit(item, (start_x + col * spacing_x, start_y + row * spacing_y))
        scaled = pygame.transform.smoothscale(
            base, (int(self.width * self.scale), int(self.height * self.scale))
        )
        scaled.set_alpha(self.alpha)
        draw_x = int(self.x - scaled.get_width() / 2)
        draw_y = int(self.y - scaled.get_height())
        surf.blit(scaled, (draw_x, draw_y))


class AnswerBlock:
    def __init__(self, cx, cy, w, h):
        self.cx = cx
        self.y = cy
        self.w = w
        self.h = h
        self.text = ""
        self.is_correct = False
        self.selected_color = None
        self.visible = False

    def rect(self):
        return Rect(int(self.cx - self.w / 2), int(self.y - self.h / 2), self.w, self.h)

    def draw(self, surf, font):
        if not self.visible:
            return
        r = self.rect()
        color = self.selected_color if self.selected_color else YELLOW
        pygame.draw.rect(surf, color, r, border_radius=18)
        pygame.draw.rect(surf, (90, 90, 90), r, width=2, border_radius=18)
        txt_surf = font.render(str(self.text), True, BLACK)
        surf.blit(txt_surf, txt_surf.get_rect(center=r.center))


class OperationCard:
    def __init__(self, x, y, w, h, operation_id, operation_info):
        self.base_rect = Rect(x, y, w, h)
        self.rect = self.base_rect.copy()
        self.operation_id = operation_id
        self.info = operation_info
        self.hover = False
        self.anim_scale = 1.0

    def update(self, global_time):
        pulse = 1.0 + 0.025 * math.sin(global_time * 0.004)
        if self.hover:
            pulse += 0.05
        self.anim_scale = pulse
        w = int(self.base_rect.width * self.anim_scale)
        h = int(self.base_rect.height * self.anim_scale)
        self.rect = Rect(
            self.base_rect.centerx - w // 2,
            self.base_rect.centery - h // 2,
            w, h
        )


class MathGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game Matematika Cerita")

        info = pygame.display.Info()
        global SCREEN_W, SCREEN_H
        SCREEN_W, SCREEN_H = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.NOFRAME)
        self.clock = pygame.time.Clock()

        sizes = {
            "ui": 28, "ui_small": 20, "btn": 44, "story": 38,
            "answer": 52, "tutorial": 32, "tutorial_small": 24,
            "go_title": 54, "go_big": 46, "menu_title": 48, "menu_desc": 24,
            "tut_title": 52, "tut_step": 30, "tut_body": 26,
        }
        fonts = load_font_try(sizes)
        self.font_ui            = fonts["ui"]
        self.font_ui_small      = fonts["ui_small"]
        self.font_button        = fonts["btn"]
        self.font_story         = fonts["story"]
        self.font_answer        = fonts["answer"]
        self.font_tutorial      = fonts["tutorial"]
        self.font_tutorial_small= fonts["tutorial_small"]
        self.font_go_title      = fonts["go_title"]
        self.font_go_big        = fonts["go_big"]
        self.font_menu_title    = fonts["menu_title"]
        self.font_menu_desc     = fonts["menu_desc"]
        self.font_tut_title     = fonts["tut_title"]
        self.font_tut_step      = fonts["tut_step"]
        self.font_tut_body      = fonts["tut_body"]

        self.bg_img               = load_image_safe(BACKGROUND_IMG, (SCREEN_W, SCREEN_H))
        self.division_bg_img      = load_image_safe(DIVISION_BG_IMG, (SCREEN_W, SCREEN_H))
        self.multiplication_bg_img= load_image_safe(MULTIPLICATION_BG_IMG, (SCREEN_W, SCREEN_H))
        self.title_img            = load_image_safe(MATH_TITLE_IMG, (950, 330))
        self.trophy_img           = load_image_safe(TROPHY_IMG, (180, 180))
        self.bgku_img             = load_image_safe(BGKU_IMG, (SCREEN_W, SCREEN_H))

        self.giraffe_img  = load_image_safe(GIRAFFE_IMG,  (190, 270))
        self.bear_img     = load_image_safe(BEAR_IMG,     (170, 150))
        self.elephant_img = load_image_safe(ELEPHANT_IMG, (200, 170))
        self.rabbit_img   = load_image_safe(RABBIT_IMG,   (100, 120))
        self.buaya_img    = load_image_safe(BUAYA_IMG,    (180, 120))

        self.apple_img  = load_image_safe(APPLE_IMG,  (100, 100))
        self.banana_img = load_image_safe(BANANA_IMG, (120, 100))
        self.fish_img   = load_image_safe(FISH_IMG,   (120, 80))
        self.donut_img  = load_image_safe(DONUT_IMG,  (100, 100))
        self.pizza_img  = load_image_safe(PIZZA_IMG,  (120, 120))
        self.plate_img  = load_image_safe(PLATE_IMG,  (120, 120))
        self.wadah_img  = load_image_safe(WADAH_IMG,  (120, 120))

        self.ball_img   = load_image_safe(BALL_IMG,   (130, 130))
        self.car_img    = load_image_safe(CAR_IMG,    (180, 115))
        self.doll_img   = load_image_safe(DOLL_IMG,   (130, 190))
        self.block_img  = load_image_safe(BLOCK_IMG,  (145, 145))
        self.robot_img  = load_image_safe(ROBOT_IMG,  (155, 180))
        self.rak_img    = load_image_safe(RAK_IMG,    (290, 240))
        self.kardus_img = load_image_safe(KARDUS_IMG, (290, 240))
        self.rak3_img   = self.rak_img
        self.home_img   = load_image_safe(HOME_IMG,   (220, 200))

        _icon_size = (80, 80)
        self.tut_icon_baca     = load_image_safe(TUT_ICON_BACA,     _icon_size)
        self.tut_icon_object   = load_image_safe(TUT_ICON_OBJECT,   _icon_size)
        self.tut_icon_microbit = load_image_safe(TUT_ICON_MICROBIT, _icon_size)
        self.tut_icon_jawab    = load_image_safe(TUT_ICON_JAWAB,    _icon_size)

        self.state = "main_menu"
        self.selected_operation = None

        self.tutorial_step       = 0
        self.tutorial_btn_rect   = None
        self.tutorial_back_rect  = None
        self.tutorial_btn_hover  = False
        self.tutorial_back_hover = False

        self.operation_cards = []
        card_w, card_h = 420, 260
        card_margin = 40
        start_x = SCREEN_W // 2 - (card_w * 2 + card_margin) // 2
        start_y = 250
        operations = [
            ("addition",       0, 0),
            ("subtraction",    1, 0),
            ("multiplication", 0, 1),
            ("division",       1, 1)
        ]
        for op_id, col, row in operations:
            x = start_x + col * (card_w + card_margin)
            y = start_y + row * (card_h + card_margin)
            card = OperationCard(x, y, card_w, card_h, op_id, OPERATION_INFO[op_id])
            self.operation_cards.append(card)

        self.score = 0
        self.question_index = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.current_questions = []
        self.game_start_ms = 0
        self.game_end_ms = 0

        self.start_btn_rect    = Rect(SCREEN_W // 2 - 190, 600, 360, 90)
        self.back_btn_rect     = Rect(50, 50, 150, 50)
        self.play_btn_rect     = Rect(SCREEN_W // 2 - 150, 750, 300, 70)
        self.tutorial_next_btn = None
        self.reset_rect        = None
        self.restart_rect      = None

        self.start_hover         = False
        self.back_hover          = False
        self.reset_hover         = False
        self.play_hover          = False
        self.tutorial_next_hover = False

        self.microbit = None

        self.current_question  = None
        self.objects_on_screen = []
        self.line_index        = 0
        self.spawn_queue       = []
        self.spawned_total     = 0
        self.total_target      = 0

        self.is_subtracting_phase   = False
        self.subtract_amount        = 0
        self.objects_to_remove      = []
        self.subtract_trigger_timer = 0

        self.is_dividing_phase   = False
        self.division_targets    = []
        self.division_index      = 0
        self.division_containers = []
        self.division_finished   = False

        self.is_multiplying_phase  = False
        self.multiplication_groups = []
        self.current_group_index   = 0
        self.group_spawn_timer     = 0

        self.blocks = [AnswerBlock(cx, ANSWER_Y, BLOCK_SIZE[0], BLOCK_SIZE[1]) for cx in ANSWER_XS]
        self.show_answers       = False
        self.waiting_for_answer = False
        self.answer_confirmed   = False

        self.auto_next_active = False
        self.auto_next_timer  = 0
        self.last_shake_time   = 0
        self.shake_debounce_ms = 300

        self.play_back_rect  = Rect(30, 90, 0, 0)
        self.play_back_hover = False
        self.show_exit_confirm = False
        self.exit_alpha        = 0

        self.exit_yes_rect = Rect(SCREEN_W//2 - 170, SCREEN_H//2 + 40, 140, 60)
        self.exit_no_rect  = Rect(SCREEN_W//2 + 30,  SCREEN_H//2 + 40, 140, 60)
        self.exit_yes_hover = False
        self.exit_no_hover  = False

    def is_ready_to_answer(self):
        return self.show_answers and self.waiting_for_answer and (not self.answer_confirmed)

    def _safe_write_microbit(self, text_line: str):
        if not self.microbit:
            return
        try:
            if self.microbit.ser and self.microbit.ser.is_open:
                self.microbit.ser.write((text_line + "\n").encode())
                self.microbit.ser.flush()
        except:
            pass

    def _build_spawn_queue(self, q):
        queue = []
        for per_line in q.get("spawn_per_line", []):
            for obj in per_line:
                t = obj.get("type")
                c = int(obj.get("count", 0))
                queue.extend([t] * c)
        return queue

    def load_question(self, idx):
        if idx >= len(self.current_questions):
            self.state = "gameover"
            self.game_end_ms = pygame.time.get_ticks()
            self._safe_write_microbit("GAME_OVER")
            self.reset_microbit_state()
            return

        self.current_question  = self.current_questions[idx]
        self.objects_on_screen = []
        self.spawned_total     = 0
        self.line_index        = 0

        self.is_subtracting_phase   = False
        self.objects_to_remove      = []
        self.subtract_amount        = 0
        self.subtract_trigger_timer = 0

        self.is_dividing_phase   = False
        self.division_targets    = []
        self.division_index      = 0
        self.division_containers = []
        self.division_finished   = False

        self.is_multiplying_phase  = False
        self.multiplication_groups = []
        self.current_group_index   = 0
        self.group_spawn_timer     = 0

        operation = self.current_question["operation"]
        if operation == "multiplication":
            self.total_groups    = self.current_question["groups"]
            self.items_per_group = self.current_question["per_group"]
            self.object_type     = self.current_question["object_type"]
            self.spawned_total   = 0
            self.objects_on_screen.clear()
            self.multiplication_groups = []
            self.is_multiplying_phase  = False
            self.total_target = self.total_groups
            print("\n🔄 RESET MULTIPLICATION STATE")
            print("   total_groups =", self.total_groups)
            print("   spawned_total =", self.spawned_total)
            self.start_multiplication_phase()
        else:
            self.spawn_queue  = self._build_spawn_queue(self.current_question)
            self.total_target = len(self.spawn_queue)

        self.show_answers       = False
        self.waiting_for_answer = False
        self.answer_confirmed   = False
        for b in self.blocks:
            b.visible        = False
            b.selected_color = None

        self.auto_next_active = False
        self.auto_next_timer  = 0

        if self.microbit:
            self.microbit.game_state    = "SPAWNING"
            self.microbit.spawned_count = 0
            self.microbit.total_animals = self.total_target
            self.microbit._reset_detection_state()
            self._safe_write_microbit("RESET")
            pygame.time.delay(100)
            if self.total_target > 0:
                self._safe_write_microbit(f"TOTAL:{self.total_target}")
                pygame.time.delay(100)
            self._safe_write_microbit("COUNT:0")
            print(f"🎮 Microbit direset: state=SPAWNING, total={self.total_target}")

        op_name = OPERATION_INFO[self.current_question['operation']]['name']
        print(f"\n📚 Soal {idx + 1}/{len(self.current_questions)} dimuat")
        print(f"   Operasi: {op_name}")
        print("   Goyang micro:bit untuk spawn objek!")

    def start_game(self):
        if not self.selected_operation:
            return
        self.state             = "play"
        self.score             = 0
        self.question_index    = 0
        self.correct_count     = 0
        self.wrong_count       = 0
        self.current_questions = QUESTIONS_BY_OPERATION[self.selected_operation]
        self.game_start_ms     = pygame.time.get_ticks()
        self.game_end_ms       = self.game_start_ms
        self.load_question(0)

    def reset_to_first(self):
        self.start_game()

    def next_question(self):
        self.question_index += 1
        self.load_question(self.question_index)

    def next_line(self):
        if not self.current_question:
            return
        if self.show_answers or self.answer_confirmed:
            return
        if self.line_index < len(self.current_question["lines"]) - 1:
            self.line_index += 1
            operation       = self.current_question["operation"]
            last_line_index = len(self.current_question["lines"]) - 1
            if operation == "addition":
                if self.line_index == last_line_index:
                    if self.spawned_total >= self.total_target:
                        self.show_answer_blocks()
                    else:
                        print("⚠️ Belum spawn semua objek!")
                        self.line_index -= 1
            elif operation == "subtraction":
                if self.line_index == 1:
                    self.start_subtraction_phase()
                elif self.line_index == last_line_index:
                    if not self.is_subtracting_phase:
                        self.show_answer_blocks()
            elif operation == "division":
                if self.line_index == 1:
                    if self.spawned_total < self.total_target:
                        print("⚠️ Belum spawn semua makanan!")
                        self.line_index -= 1
                        return
                    self.start_division_phase()
                elif self.line_index == last_line_index:
                    if self.division_finished:
                        self.show_answer_blocks()
            elif operation == "multiplication":
                if self.line_index == 1:
                    if self.spawned_total < self.total_groups:
                        print(f"⚠️ Rak belum lengkap! {self.spawned_total}/{self.total_groups}")
                        self.line_index -= 1
                        return
                    print("📦 Mengisi rak...")
                    for group in self.objects_on_screen:
                        if isinstance(group, MultiplicationGroup):
                            group.start_fill(self.items_per_group)
                elif self.line_index == last_line_index:
                    self.show_answer_blocks()
        else:
            self._try_show_answers()

    def spawn_next_object(self):
        if self.current_question["operation"] == "multiplication":
            if not self.is_multiplying_phase:
                return False
            if self.spawned_total >= self.total_groups:
                return False
            spacing_x = SCREEN_W / (self.total_groups + 1)
            x = spacing_x * (self.spawned_total + 1)
            y = OBJECTS_AREA_Y + 40
            item_map = {
                "ball": self.ball_img, "car": self.car_img,
                "doll": self.doll_img, "block": self.block_img, "robot": self.robot_img,
            }
            container_map = {
                "ball": self.rak_img, "car": self.kardus_img,
                "doll": self.rak_img, "block": self.rak_img, "robot": self.rak_img,
            }
            item_img      = item_map.get(self.object_type)
            container_img = container_map.get(self.object_type) or self.rak_img
            if not container_img:
                print("❌ Container image None! (rak_img juga tidak ada)")
                return False
            group = MultiplicationGroup(container_img, item_img, x, y)
            self.objects_on_screen.append(group)
            self.spawned_total += 1
            print(f"📦 Rak muncul: {self.spawned_total}/{self.total_groups}")
            return True

        img_map = {
            "giraffe": self.giraffe_img, "bear": self.bear_img,
            "elephant": self.elephant_img, "rabbit": self.rabbit_img,
            "buaya": self.buaya_img, "apple": self.apple_img,
            "banana": self.banana_img, "pizza": self.pizza_img,
            "fish": self.fish_img, "donut": self.donut_img,
        }
        if not self.spawn_queue:
            return False
        obj_type        = self.spawn_queue.pop(0)
        img             = img_map.get(obj_type)
        total_on_screen = len(self.objects_on_screen)
        max_per_row     = 8
        total_rows      = (self.total_target + max_per_row - 1) // max_per_row
        row             = total_on_screen // max_per_row
        col             = total_on_screen % max_per_row
        start_x         = 150
        end_x           = SCREEN_W - 150
        available_width = end_x - start_x
        items_in_row    = min(max_per_row, self.total_target - row * max_per_row)
        spacing_x       = available_width / (items_in_row + 1)
        x               = start_x + spacing_x * (col + 1)
        spacing_y       = OBJECTS_AREA_HEIGHT / (total_rows + 1)
        y               = OBJECTS_AREA_Y + spacing_y * (row + 1)
        obj = GameObject(img, x, y, obj_type)
        self.objects_on_screen.append(obj)
        self.spawned_total += 1
        self._safe_write_microbit(f"COUNT:{self.spawned_total}")
        self._try_show_answers()
        return True

    def start_subtraction_phase(self):
        if self.is_subtracting_phase:
            return
        if self.spawned_total < self.total_target:
            return
        print("➖ Memulai fase pengurangan...")
        self.is_subtracting_phase   = True
        self.subtract_trigger_timer = 0
        answer                      = self.current_question["answer"]
        initial_total               = self.spawned_total
        self.subtract_amount        = initial_total - answer
        self.objects_to_remove      = self.objects_on_screen[-self.subtract_amount:]

    def start_multiplication_phase(self):
        if self.is_multiplying_phase:
            return
        print("✖ Memulai fase spawn rak...")
        self.is_multiplying_phase = True
        self.spawned_total        = 0
        self.objects_on_screen    = []
        print(f"   Target rak: {self.total_groups}")

    def start_division_phase(self):
        self.division_containers.clear()
        if self.is_dividing_phase:
            return
        if self.spawned_total < self.total_target:
            return
        print("🍽 Memulai fase pembagian...")
        self.is_dividing_phase = True
        divisor   = self.current_question["divisor"]
        center_y  = OBJECTS_AREA_Y - 20
        spacing_x = SCREEN_W / (divisor + 1)
        self.division_targets = []
        for i in range(divisor):
            x = spacing_x * (i + 1)
            y = center_y
            self.division_targets.append((x, y))
            container_img = (
                self.plate_img if self.current_question["theme"] == "foods"
                else self.wadah_img
            )
            container           = GameObject(container_img, x, y + 60, "container")
            container.alpha     = 255
            container.scale     = 1.0
            container.appearing = False
            self.division_containers.append(container)

    def reset_microbit_state(self, clear_history=False):
        if not self.microbit:
            return
        try:
            self.microbit.game_state    = "IDLE"
            self.microbit.spawned_count = 0
            self.microbit.total_animals = 0
            self.microbit._reset_detection_state()
            if clear_history:
                self.microbit.question_history.clear()
            print("🔄 Microbit state di-reset")
        except Exception as e:
            print(f"⚠️ Reset microbit error: {e}")

    def _try_show_answers(self):
        if self.show_answers or self.answer_confirmed:
            return
        if not self.current_question:
            return
        all_spawned       = (self.spawned_total >= self.total_target)
        last_line_reached = (self.line_index >= len(self.current_question["lines"]) - 1)
        if all_spawned and last_line_reached:
            print(f"\n✅ [READY] Semua objek ({self.spawned_total}) & baris terakhir tercapai → Tampilkan jawaban!\n")
            self.show_answer_blocks()

    def on_shake(self):
        now = pygame.time.get_ticks()
        if now - self.last_shake_time < self.shake_debounce_ms:
            return
        self.last_shake_time = now
        if self.state != "play":
            return
        if not self.current_question:
            return
        operation = self.current_question["operation"]
        if operation == "multiplication":
            if not self.is_multiplying_phase:
                print("⚠️ Belum masuk fase multiplication")
                return
            if self.spawned_total >= self.total_groups:
                print("⚠️ Semua rak sudah muncul")
                return
            spawned = self.spawn_next_object()
            if spawned:
                print(f"📦 Rak muncul: {self.spawned_total}/{self.total_groups}")
        else:
            if self.spawned_total >= self.total_target:
                print("⚠️ Semua objek sudah spawn")
                return
            spawned = self.spawn_next_object()
            if spawned:
                print(f"🐾 Objek muncul: {self.spawned_total}/{self.total_target}")

    def show_answer_blocks(self):
        if self.show_answers:
            return
        correct = self.current_question["answer"]
        wrongs  = self.current_question["wrong_answers"]
        options = [correct] + wrongs
        random.shuffle(options)
        for i, block in enumerate(self.blocks):
            block.text           = options[i]
            block.visible        = True
            block.selected_color = None
            block.is_correct     = (options[i] == correct)
        self.show_answers       = True
        self.waiting_for_answer = True
        self._safe_write_microbit("COUNT_DONE")
        pygame.time.delay(200)
        if self.microbit:
            self.microbit.send_ready_to_answer()
            self.microbit.game_state = "READY"
        print(f"\n🎯 JAWABAN SIAP DIPILIH! (state: READY)")

    def handle_answer(self, block_index):
        if not self.waiting_for_answer:
            return
        block = self.blocks[block_index]
        if block.is_correct:
            block.selected_color = GREEN
            self.score          += SCORE_PER_CORRECT
            self.correct_count  += 1
            self._safe_write_microbit("CORRECT")
            if self.microbit:
                self.microbit.send_correct_feedback()
            print(f"\n✅ JAWABAN BENAR. (pilih: {block.text})")
        else:
            block.selected_color = RED
            self.wrong_count    += 1
            self._safe_write_microbit("WRONG")
            if self.microbit:
                self.microbit.send_wrong_feedback()
            print(f"\n❌ JAWABAN SALAH. (pilih: {block.text})")
        print(f"   Jawaban benar: {self.current_question['answer']}\n")
        self.waiting_for_answer = False
        self.answer_confirmed   = True
        if self.microbit and hasattr(self.microbit, 'game_state'):
            self.microbit.game_state = "IDLE"
            print("🎮 Microbit state: IDLE (menunggu soal berikutnya)")
        self.auto_next_active = True
        self.auto_next_timer  = 0

    def on_microbit_answer(self, idx):
        if not self.is_ready_to_answer():
            return
        if 0 <= idx < len(self.blocks):
            self.handle_answer(idx)

    def update(self, dt):
        for obj in self.objects_on_screen:
            if isinstance(obj, MultiplicationGroup):
                obj.update(dt)
            else:
                obj.update()

        if self.auto_next_active:
            self.auto_next_timer += dt
            if self.auto_next_timer >= AUTO_NEXT_DELAY_MS:
                self.auto_next_active = False
                self.next_question()

        if self.state == "operation_menu":
            global_time = pygame.time.get_ticks()
            for card in self.operation_cards:
                card.update(global_time)

        if self.is_subtracting_phase:
            if self.objects_to_remove:
                self.subtract_trigger_timer += dt
                if self.subtract_trigger_timer >= 280:
                    self.subtract_trigger_timer = 0
                    obj = self.objects_to_remove.pop(0)
                    if not obj.leaving and not obj.gone:
                        obj.leaving     = True
                        obj.leave_speed = 4 + random.randint(0, 3)
            all_gone      = all(o.gone for o in self.objects_on_screen if isinstance(o, GameObject) and o.leaving)
            triggered_all = (len(self.objects_to_remove) == 0)
            if triggered_all and all_gone:
                self.objects_on_screen = [
                    o for o in self.objects_on_screen
                    if not (isinstance(o, GameObject) and o.gone)
                ]
                self.is_subtracting_phase = False
                print("➖ Pengurangan selesai!")

        if self.is_dividing_phase:
            if self.division_index < len(self.objects_on_screen):
                obj           = self.objects_on_screen[self.division_index]
                total_groups  = len(self.division_targets)
                group_index   = self.division_index % total_groups
                base_x, base_y= self.division_targets[group_index]
                position_in_group = self.division_index // total_groups
                offset_x = (position_in_group % 2) * 35 - 18
                offset_y = -(position_in_group // 2) * 35
                target_x = base_x + offset_x
                target_y = base_y + offset_y
                obj.x += (target_x - obj.x) * 0.15
                obj.y += (target_y - obj.y) * 0.15
                if abs(obj.x - target_x) < 4 and abs(obj.y - target_y) < 4:
                    self.division_index += 1
            if self.division_index >= len(self.objects_on_screen):
                print("🍽 Pembagian selesai!")
                self.is_dividing_phase = False
                self.division_finished = True

        if self.show_exit_confirm:
            self.exit_alpha = min(180, self.exit_alpha + 15)
        else:
            self.exit_alpha = max(0, self.exit_alpha - 15)

    # =====================================================================
    # TUTORIAL
    # =====================================================================
    def draw_tutorial(self):
        op   = self.selected_operation
        data = TUTORIAL_DATA[op]
        steps= data["steps"]
        color= data["color"]

        if op == "division" and self.division_bg_img:
            self.screen.blit(self.division_bg_img, (0, 0))
        elif op == "multiplication" and self.multiplication_bg_img:
            self.screen.blit(self.multiplication_bg_img, (0, 0))
        elif op == "subtraction" and self.bgku_img:
            self.screen.blit(self.bgku_img, (0, 0))
        elif self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(MENU_BG)

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        self.screen.blit(overlay, (0, 0))

        judul_surf = self.font_tut_title.render(data["title"], True, WHITE)
        judul_bg   = Rect(SCREEN_W//2 - judul_surf.get_width()//2 - 40, 28,
                          judul_surf.get_width() + 80, judul_surf.get_height() + 22)
        draw_rounded_rect(self.screen, judul_bg, color, radius=20)
        pygame.draw.rect(self.screen, WHITE, judul_bg, width=2, border_radius=20)
        self.screen.blit(judul_surf, judul_surf.get_rect(center=judul_bg.center))

        card_w   = 340
        card_h   = 310
        gap      = 28
        total_w  = card_w * 4 + gap * 3
        start_cx = SCREEN_W // 2 - total_w // 2
        card_y   = 130

        icon_img_map = {
            "baca":     self.tut_icon_baca,
            "object":   self.tut_icon_object,
            "microbit": self.tut_icon_microbit,
            "jawab":    self.tut_icon_jawab,
        }

        def render_wrapped(font, text, text_color, center_x, start_y, max_w, line_h, max_y):
            words = text.split(" ")
            lines = []
            current = ""
            for word in words:
                test = (current + " " + word).strip()
                if font.size(test)[0] <= max_w:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
            y = start_y
            for line in lines:
                if y + line_h > max_y:
                    break
                surf = font.render(line, True, text_color)
                self.screen.blit(surf, surf.get_rect(center=(center_x, y)))
                y += line_h
            return y

        for i, step in enumerate(steps):
            cx = start_cx + i * (card_w + gap)
            card_rect = Rect(cx, card_y, card_w, card_h)

            if i == self.tutorial_step:
                highlight = Rect(cx - 4, card_y - 4, card_w + 8, card_h + 8)
                draw_rounded_rect(self.screen, highlight, WHITE, radius=24)

            alpha_val = 255 if i == self.tutorial_step else 160
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            r, g, b   = color
            pygame.draw.rect(card_surf, (r, g, b, alpha_val), card_surf.get_rect(), border_radius=20)
            pygame.draw.rect(card_surf, (255, 255, 255, 200), card_surf.get_rect(), width=2, border_radius=20)
            self.screen.blit(card_surf, card_rect.topleft)

            num_surf = self.font_tut_title.render(str(i + 1), True, WHITE)
            self.screen.blit(num_surf, num_surf.get_rect(center=(cx + 36, card_y + 36)))

            icon_img = icon_img_map.get(step.get("icon_key"))
            if icon_img:
                icon_rect = icon_img.get_rect(center=(cx + card_w // 2, card_y + 80))
                self.screen.blit(icon_img, icon_rect)

            padding     = 18
            max_text_w  = card_w - padding * 2
            card_bottom = card_y + card_h - 8

            render_wrapped(
                self.font_tut_step, step["judul"], WHITE,
                cx + card_w // 2,
                card_y + 138,
                max_text_w,
                32,
                card_y + 175
            )

            pygame.draw.line(self.screen, (255, 255, 255, 120),
                             (cx + 20, card_y + 163), (cx + card_w - 20, card_y + 163), 1)

            isi_y  = card_y + 185
            line_h = 29
            for raw_line in step["isi"].split("\n"):
                isi_y = render_wrapped(
                    self.font_tut_body, raw_line, WHITE,
                    cx + card_w // 2,
                    isi_y,
                    max_text_w,
                    line_h,
                    card_bottom
                )
                if isi_y >= card_bottom:
                    break

        dot_y  = card_y + card_h + 22
        dot_cx = SCREEN_W // 2
        dot_r  = 7
        dot_gap= 22
        for i in range(len(steps)):
            dx = dot_cx + (i - len(steps)//2) * dot_gap + (dot_gap//2 if len(steps) % 2 == 0 else 0)
            col_dot = WHITE if i == self.tutorial_step else (150, 150, 150)
            pygame.draw.circle(self.screen, col_dot, (dx, dot_y), dot_r if i == self.tutorial_step else 5)

        back_w, back_h = 200, 62
        back_x = 50
        back_y = SCREEN_H - back_h - 40
        self.tutorial_back_rect = Rect(back_x, back_y, back_w, back_h)
        back_col = (100, 100, 100) if not self.tutorial_back_hover else (130, 130, 130)
        draw_rounded_rect(self.screen, self.tutorial_back_rect, back_col, radius=30)
        pygame.draw.rect(self.screen, WHITE, self.tutorial_back_rect, width=2, border_radius=30)
        bt = self.font_tut_body.render("< Kembali", True, WHITE)
        self.screen.blit(bt, bt.get_rect(center=self.tutorial_back_rect.center))

        btn_w, btn_h = 300, 72
        btn_x = SCREEN_W - btn_w - 50
        btn_y = SCREEN_H - btn_h - 30
        self.tutorial_btn_rect = Rect(btn_x, btn_y, btn_w, btn_h)

        is_last = (self.tutorial_step == len(steps) - 1)
        label   = "MULAI BERMAIN!" if is_last else "Lanjut >"
        btn_col = (255, 180, 0) if (is_last and self.tutorial_btn_hover) else \
                  (255, 150, 0) if is_last else \
                  (60, 180, 60) if self.tutorial_btn_hover else (40, 160, 40)

        sh = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 40))
        self.screen.blit(sh, (btn_x + 5, btn_y + 6))

        draw_rounded_rect(self.screen, self.tutorial_btn_rect, btn_col, radius=36)
        pygame.draw.rect(self.screen, WHITE, self.tutorial_btn_rect, width=2, border_radius=36)
        bt2 = self.font_tut_step.render(label, True, WHITE)
        self.screen.blit(bt2, bt2.get_rect(center=self.tutorial_btn_rect.center))

        kb = self.font_tut_body.render("Tekan > / < untuk navigasi   |   ENTER untuk mulai", True, (200, 200, 200))
        self.screen.blit(kb, kb.get_rect(center=(SCREEN_W // 2, SCREEN_H - 18)))


    def draw_main_menu(self):
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((100, 180, 120))
        if self.title_img:
            tr = self.title_img.get_rect(center=(SCREEN_W // 2, 280))
            self.screen.blit(self.title_img, tr)
        else:
            t = self.font_story.render("GAME MATEMATIKA CERITA", True, (255, 230, 0))
            self.screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 200)))

        pulse    = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.005)
        base_w   = self.start_btn_rect.width
        base_h   = self.start_btn_rect.height
        btn_surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
        btn_color= START_BTN_HOVER if self.start_hover else START_BTN_COLOR
        pygame.draw.rect(btn_surf, btn_color, btn_surf.get_rect(), border_radius=28)
        pygame.draw.rect(btn_surf, (200, 150, 30), btn_surf.get_rect(), width=3, border_radius=28)
        txt = self.font_button.render("MULAI", True, BLACK)
        btn_surf.blit(txt, txt.get_rect(center=(base_w // 2, base_h // 2)))
        scaled = pygame.transform.smoothscale(btn_surf, (int(base_w * pulse), int(base_h * pulse)))
        x = self.start_btn_rect.centerx - scaled.get_width()  // 2
        y = self.start_btn_rect.centery - scaled.get_height() // 2
        self.screen.blit(scaled, (x, y))

    def draw_operation_menu(self):
        if self.selected_operation == "division" and self.division_bg_img:
            self.screen.blit(self.division_bg_img, (0, 0))
        elif self.selected_operation == "subtraction" and self.bgku_img:
            self.screen.blit(self.bgku_img, (0, 0))
        elif self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(MENU_BG)

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 40))
        self.screen.blit(overlay, (0, 0))

        back_color  = (220, 220, 220) if self.back_hover else (180, 180, 180)
        back_shadow = Rect(self.back_btn_rect.x + 6, self.back_btn_rect.y + 8,
                           self.back_btn_rect.width, self.back_btn_rect.height)
        shadow_surf = pygame.Surface((self.back_btn_rect.width, self.back_btn_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 90), shadow_surf.get_rect(), border_radius=20)
        self.screen.blit(shadow_surf, back_shadow.topleft)
        draw_rounded_rect(self.screen, self.back_btn_rect, back_color, radius=20,
                          border_color=(80, 80, 80), border_w=2)
        arrow = self.font_ui.render("<", True, BLACK)
        self.screen.blit(arrow, arrow.get_rect(midleft=(self.back_btn_rect.x + 15, self.back_btn_rect.centery)))
        back_text = self.font_ui.render("Kembali", True, BLACK)
        self.screen.blit(back_text, back_text.get_rect(midleft=(self.back_btn_rect.x + 45, self.back_btn_rect.centery)))

        title      = self.font_menu_title.render("PILIH OPERASI MATEMATIKA", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_W // 2, 130))
        bg_rect    = Rect(title_rect.left - 60, title_rect.top - 25,
                          title_rect.width + 120, title_rect.height + 50)
        draw_rounded_rect(self.screen, bg_rect, WHITE, radius=50,
                          border_color=(220, 220, 220), border_w=3)
        self.screen.blit(title, title_rect)

        for card in self.operation_cards:
            card_surf  = pygame.Surface((card.base_rect.width, card.base_rect.height), pygame.SRCALPHA)
            base_color = card.info["color"]
            if card.hover:
                base_color = tuple(min(c + 25, 255) for c in base_color)
            pygame.draw.rect(card_surf, base_color, card_surf.get_rect(), border_radius=35)
            pygame.draw.rect(card_surf, (60, 60, 60), card_surf.get_rect(), width=2, border_radius=35)
            icon_font = pygame.font.Font(None, 95)
            icon = icon_font.render(card.info["icon"], True, WHITE)
            card_surf.blit(icon, icon.get_rect(center=(card.base_rect.width // 2, card.base_rect.height // 2 - 50)))
            name = self.font_ui.render(card.info["name"], True, WHITE)
            card_surf.blit(name, name.get_rect(center=(card.base_rect.width // 2, card.base_rect.height // 2 + 10)))
            desc = self.font_ui_small.render(card.info["desc"], True, WHITE)
            card_surf.blit(desc, desc.get_rect(center=(card.base_rect.width // 2, card.base_rect.height // 2 + 45)))
            scaled      = pygame.transform.smoothscale(card_surf, (card.rect.width, card.rect.height))
            shadow_rect = Rect(card.rect.x + 10, card.rect.y + 12, card.rect.width, card.rect.height)
            sh_surf     = pygame.Surface((card.rect.width, card.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(sh_surf, (0, 0, 0, 90), sh_surf.get_rect(), border_radius=35)
            self.screen.blit(sh_surf, shadow_rect.topleft)
            self.screen.blit(scaled, card.rect.topleft)

    def draw_play(self):
        if self.selected_operation == "division" and self.division_bg_img:
            self.screen.blit(self.division_bg_img, (0, 0))
        elif self.selected_operation == "multiplication" and self.multiplication_bg_img:
            self.screen.blit(self.multiplication_bg_img, (0, 0))
        elif self.selected_operation == "subtraction" and self.bgku_img:
            self.screen.blit(self.bgku_img, (0, 0))
        elif self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))

        score_surf = self.font_ui.render(f"Skor : {self.score}", True, BLACK)
        padx, pady = 25, 12
        bw = score_surf.get_width() + padx * 2
        bh = score_surf.get_height() + pady * 2
        bx, by = 30, 20
        pygame.draw.rect(self.screen, UI_BG, (bx, by, bw, bh), border_radius=30)
        pygame.draw.rect(self.screen, (90, 90, 90), (bx, by, bw, bh), 2, border_radius=30)
        self.screen.blit(score_surf, (bx + padx, by + pady))

        back_text = self.font_ui_small.render("Menu", True, BLACK)
        padx, pady = 25, 12
        bw = back_text.get_width() + padx * 2
        bh = back_text.get_height() + pady * 2
        bx, by = 30, 90
        self.play_back_rect = Rect(bx, by, bw, bh)
        back_color = UI_BG if not self.play_back_hover else (255, 220, 90)
        pygame.draw.rect(self.screen, back_color, self.play_back_rect, border_radius=30)
        pygame.draw.rect(self.screen, (90, 90, 90), self.play_back_rect, 2, border_radius=30)
        self.screen.blit(back_text, (bx + padx, by + pady))

        total_q   = len(self.current_questions)
        soal_surf = self.font_ui.render(f"Soal : {self.question_index + 1}/{total_q}", True, BLACK)
        rtxt      = self.font_ui.render("Reset", True, WHITE)
        rpadx, rpady = 24, 10
        rw = rtxt.get_width() + rpadx * 2
        rh = rtxt.get_height() + rpady * 2
        margin = 30
        ry = 20
        rx = SCREEN_W - rw - margin
        btn_col = RESET_BTN_HOVER if self.reset_hover else RESET_BTN_COLOR
        pygame.draw.rect(self.screen, btn_col, (rx, ry, rw, rh), border_radius=25)
        pygame.draw.rect(self.screen, (90, 90, 90), (rx, ry, rw, rh), 2, border_radius=25)
        self.screen.blit(rtxt, (rx + rpadx, ry + rpady))
        self.reset_rect = Rect(rx, ry, rw, rh)
        soal_padx, soal_pady = 20, 10
        soal_bw = soal_surf.get_width() + soal_padx * 2
        soal_bh = soal_surf.get_height() + soal_pady * 2
        soal_bx = rx - soal_bw - 15
        soal_by = ry
        pygame.draw.rect(self.screen, UI_BG, (soal_bx, soal_by, soal_bw, soal_bh), border_radius=25)
        pygame.draw.rect(self.screen, (90, 90, 90), (soal_bx, soal_by, soal_bw, soal_bh), 2, border_radius=25)
        self.screen.blit(soal_surf, (soal_bx + soal_padx, soal_by + soal_pady))

        if self.current_question:
            box_w = 1100
            box_x = SCREEN_W // 2 - box_w // 2
            box_y = 120
            box_h = 150
            story_box = Rect(box_x, box_y, box_w, box_h)
            draw_rounded_rect(self.screen, story_box, STORY_BOX_BG,
                              radius=20, border_color=STORY_BOX_BORDER, border_w=5)
            current_line = self.current_question["lines"][self.line_index]
            story_surf   = self.font_story.render(current_line, True, WHITE)
            self.screen.blit(story_surf, story_surf.get_rect(center=(SCREEN_W // 2, box_y + box_h // 2)))

        for b in self.blocks:
            b.draw(self.screen, self.font_answer)

        if (self.selected_operation == "subtraction"
                and self.current_question
                and self.home_img
                and self.is_subtracting_phase):
            soal_teks = " ".join(self.current_question.get("lines", [])).lower()
            if "rumah" in soal_teks or "kandang" in soal_teks:
                hw = self.home_img.get_width()
                hh = self.home_img.get_height()
                hx = SCREEN_W - hw - 10
                hy = SCREEN_H - hh - 10
                self.screen.blit(self.home_img, (hx, hy))

        if hasattr(self, "division_containers"):
            for c in self.division_containers:
                c.draw(self.screen)

        for obj in self.objects_on_screen:
            obj.draw(self.screen)

        if self.exit_alpha > 0:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.exit_alpha))
            self.screen.blit(overlay, (0, 0))
            box_w, box_h = 500, 250
            box = Rect(SCREEN_W//2 - box_w//2, SCREEN_H//2 - box_h//2, box_w, box_h)
            draw_rounded_rect(self.screen, box, WHITE, radius=25)
            title = self.font_story.render("Yakin kembali ke menu?", True, BLACK)
            self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 40)))
            yes_color = (200, 60, 60) if self.exit_yes_hover else (170, 40, 40)
            draw_rounded_rect(self.screen, self.exit_yes_rect, yes_color, radius=18)
            yes_text = self.font_ui.render("Ya", True, WHITE)
            self.screen.blit(yes_text, yes_text.get_rect(center=self.exit_yes_rect.center))
            no_color = (100, 180, 100) if self.exit_no_hover else (70, 150, 70)
            draw_rounded_rect(self.screen, self.exit_no_rect, no_color, radius=18)
            no_text = self.font_ui.render("Tidak", True, WHITE)
            self.screen.blit(no_text, no_text.get_rect(center=self.exit_no_rect.center))

    def _draw_check_icon(self, x, y, size, kind="check"):
        r  = Rect(x, y, size, size)
        bg = (0, 170, 0) if kind == "check" else (200, 50, 50)
        pygame.draw.rect(self.screen, bg, r, border_radius=6)
        pygame.draw.rect(self.screen, (10, 10, 10), r, 2, border_radius=6)
        if kind == "check":
            pygame.draw.line(self.screen, WHITE, (x+size*0.22, y+size*0.55), (x+size*0.45, y+size*0.75), 5)
            pygame.draw.line(self.screen, WHITE, (x+size*0.44, y+size*0.75), (x+size*0.80, y+size*0.28), 5)
        else:
            pygame.draw.line(self.screen, WHITE, (x+size*0.25, y+size*0.25), (x+size*0.75, y+size*0.75), 5)
            pygame.draw.line(self.screen, WHITE, (x+size*0.75, y+size*0.25), (x+size*0.25, y+size*0.75), 5)

    def draw_gameover(self):
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((245, 245, 245))

        card_w, card_h = 980, 600
        card_x = SCREEN_W // 2 - card_w // 2
        card_y = SCREEN_H // 2 - card_h // 2
        card   = Rect(card_x, card_y, card_w, card_h)
        shadow = Rect(card_x + 8, card_y + 10, card_w, card_h)
        sh_surf= pygame.Surface((shadow.w, shadow.h), pygame.SRCALPHA)
        sh_surf.fill((0, 0, 0, 40))
        self.screen.blit(sh_surf, shadow.topleft)
        draw_rounded_rect(self.screen, card, WHITE, radius=26, border_color=(25, 25, 25), border_w=2)

        if self.selected_operation:
            op_info  = OPERATION_INFO[self.selected_operation]
            op_name  = op_info['name']
            op_color = op_info['color']
        else:
            op_name  = "Matematika"
            op_color = BLACK

        if self.trophy_img:
            tr = self.trophy_img.get_rect(center=(SCREEN_W // 2, card_y + 95))
            self.screen.blit(self.trophy_img, tr)

        title = self.font_go_title.render(f"PERMAINAN {op_name} SELESAI!", True, op_color)
        self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, card_y + 190)))

        elapsed_sec = int((self.game_end_ms - self.game_start_ms) / 1000)
        waktu_str   = format_mmss(max(0, elapsed_sec))
        left_x  = card_x + 150
        row_y0  = card_y + 255
        row_gap = 42

        clock_txt = self.font_ui.render("Waktu :", True, BLACK)
        self.screen.blit(clock_txt, (left_x, row_y0))
        waktu_val = self.font_ui.render(waktu_str, True, BLACK)
        self.screen.blit(waktu_val, (card_x + card_w - 180, row_y0))

        self._draw_check_icon(left_x, row_y0 + row_gap + 2, 28, kind="check")
        benar_txt = self.font_ui.render("Soal Benar :", True, BLACK)
        self.screen.blit(benar_txt, (left_x + 40, row_y0 + row_gap))
        benar_val = self.font_ui.render(f"{self.correct_count}/{len(self.current_questions)}", True, BLACK)
        self.screen.blit(benar_val, (card_x + card_w - 180, row_y0 + row_gap))

        self._draw_check_icon(left_x, row_y0 + row_gap * 2 + 2, 28, kind="x")
        salah_txt = self.font_ui.render("Soal Salah :", True, BLACK)
        self.screen.blit(salah_txt, (left_x + 40, row_y0 + row_gap * 2))
        salah_val = self.font_ui.render(f"{self.wrong_count}", True, BLACK)
        self.screen.blit(salah_val, (card_x + card_w - 180, row_y0 + row_gap * 2))

        sep_y = card_y + 380
        pygame.draw.line(self.screen, (20, 20, 20), (card_x + 120, sep_y), (card_x + card_w - 120, sep_y), 3)
        total_label = self.font_go_big.render("TOTAL SKOR :", True, BLACK)
        self.screen.blit(total_label, (card_x + 120, sep_y + 28))
        total_val = self.font_go_big.render(str(self.score), True, BLACK)
        self.screen.blit(total_val, total_val.get_rect(midright=(card_x + card_w - 120, sep_y + 60)))

        btn_w, btn_h = 420, 86
        btn_x = SCREEN_W // 2 - btn_w // 2
        btn_y = card_y + card_h - 120
        self.restart_rect = Rect(btn_x, btn_y, btn_w, btn_h)
        mx, my  = pygame.mouse.get_pos()
        hover   = self.restart_rect.collidepoint(mx, my)
        btn_col = (110, 110, 110) if not hover else (130, 130, 130)
        bshadow  = Rect(btn_x + 6, btn_y + 7, btn_w, btn_h)
        sh_surf2 = pygame.Surface((bshadow.w, bshadow.h), pygame.SRCALPHA)
        sh_surf2.fill((0, 0, 0, 40))
        self.screen.blit(sh_surf2, bshadow.topleft)
        draw_rounded_rect(self.screen, self.restart_rect, btn_col, radius=45)
        btn_text = self.font_button.render("Kembali ke Menu", True, WHITE)
        self.screen.blit(btn_text, btn_text.get_rect(center=self.restart_rect.center))

    def run(self):
        running = True
        while running:
            dt     = self.clock.tick(FPS)
            mx, my = pygame.mouse.get_pos()

            if self.state == "main_menu":
                self.start_hover = self.start_btn_rect.collidepoint(mx, my)
            elif self.state == "operation_menu":
                self.back_hover = self.back_btn_rect.collidepoint(mx, my)
                self.play_hover = self.play_btn_rect.collidepoint(mx, my) if self.selected_operation else False
                for card in self.operation_cards:
                    card.hover = card.rect.collidepoint(mx, my)
            elif self.state == "tutorial":
                if self.tutorial_btn_rect:
                    self.tutorial_btn_hover  = self.tutorial_btn_rect.collidepoint(mx, my)
                if self.tutorial_back_rect:
                    self.tutorial_back_hover = self.tutorial_back_rect.collidepoint(mx, my)
            elif self.state == "play":
                self.reset_hover     = self.reset_rect.collidepoint(mx, my) if self.reset_rect else False
                self.play_back_hover = self.play_back_rect.collidepoint(mx, my)
                if self.show_exit_confirm:
                    self.exit_yes_hover = self.exit_yes_rect.collidepoint(mx, my)
                    self.exit_no_hover  = self.exit_no_rect.collidepoint(mx, my)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "main_menu":
                        if self.start_btn_rect.collidepoint(mx, my):
                            self.state = "operation_menu"

                    elif self.state == "operation_menu":
                        if self.back_btn_rect.collidepoint(mx, my):
                            self.state = "main_menu"
                            self.selected_operation = None
                        for card in self.operation_cards:
                            if card.rect.collidepoint(mx, my):
                                self.selected_operation = card.operation_id
                                print(f"📊 Operasi dipilih: {card.info['name']}")
                                self.reset_microbit_state(clear_history=True)
                                self.tutorial_step = 0
                                self.state = "tutorial"
                                break

                    elif self.state == "tutorial":
                        steps = TUTORIAL_DATA[self.selected_operation]["steps"]
                        if self.tutorial_btn_rect and self.tutorial_btn_rect.collidepoint(mx, my):
                            if self.tutorial_step < len(steps) - 1:
                                self.tutorial_step += 1
                            else:
                                self.start_game()
                        if self.tutorial_back_rect and self.tutorial_back_rect.collidepoint(mx, my):
                            if self.tutorial_step > 0:
                                self.tutorial_step -= 1
                            else:
                                self.state = "operation_menu"
                                self.selected_operation = None

                    elif self.state == "play":
                        if self.show_exit_confirm:
                            if self.exit_yes_rect.collidepoint(mx, my):
                                self.show_exit_confirm  = False
                                self.state              = "operation_menu"
                                self.selected_operation = None
                                self.objects_on_screen.clear()
                                self.reset_microbit_state(clear_history=True)
                                self.show_answers       = False
                                self.waiting_for_answer = False
                                self.answer_confirmed   = False
                                continue
                            if self.exit_no_rect.collidepoint(mx, my):
                                self.show_exit_confirm = False
                                continue
                        if self.play_back_rect.collidepoint(mx, my):
                            self.show_exit_confirm = True
                        elif self.show_answers and self.waiting_for_answer:
                            for i, block in enumerate(self.blocks):
                                if block.visible and block.rect().collidepoint(mx, my):
                                    self.handle_answer(i)
                        elif self.reset_rect and self.reset_rect.collidepoint(mx, my):
                            self.reset_to_first()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.state == "tutorial":
                        steps = TUTORIAL_DATA[self.selected_operation]["steps"]
                        if event.key in (pygame.K_RIGHT, pygame.K_RETURN):
                            if self.tutorial_step < len(steps) - 1:
                                self.tutorial_step += 1
                            else:
                                self.start_game()
                        elif event.key == pygame.K_LEFT:
                            if self.tutorial_step > 0:
                                self.tutorial_step -= 1
                            else:
                                self.state = "operation_menu"
                                self.selected_operation = None
                    elif self.state == "play":
                        if event.key == pygame.K_SPACE:
                            self.on_shake()
                        if event.key == pygame.K_RIGHT:
                            self.next_line()
                    elif self.state == "gameover":
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.state              = "operation_menu"
                            self.selected_operation = None
                            self.reset_microbit_state(clear_history=True)

            if self.state == "gameover":
                if pygame.mouse.get_pressed()[0]:
                    if self.restart_rect and self.restart_rect.collidepoint(mx, my):
                        self.state              = "operation_menu"
                        self.selected_operation = None
                        self.reset_microbit_state(clear_history=True)

            self.update(dt)

            if self.state == "main_menu":
                self.draw_main_menu()
            elif self.state == "operation_menu":
                self.draw_operation_menu()
            elif self.state == "tutorial":
                self.draw_tutorial()
            elif self.state == "play":
                self.draw_play()
            elif self.state == "gameover":
                self.draw_gameover()

            pygame.display.flip()

        pygame.quit()