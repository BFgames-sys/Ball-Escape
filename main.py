
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Triangle, Line
from kivy.metrics import dp

import random
import math
import colorsys
import json
import os
import time


class GameLayer(Widget):
    pass


class HudBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(8)
        self.spacing = dp(2)

        with self.canvas.before:
            Color(0, 0, 0, 0.72)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class BallEscape(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.state = "menu"

        app = App.get_running_app()
        self.save_file = os.path.join(
            app.user_data_dir,
            "ball_escape_save.json"
        )

        self.money = 0

        self.selected_skin = "player_red_circle_normal"
        self.selected_enemy = "enemy_black_circle_normal"
        self.selected_trail = "none"
        self.selected_arena = "classic"

        self.owned_skins = {self.selected_skin}
        self.owned_enemies = {self.selected_enemy}
        self.owned_trails = {"none"}
        self.owned_arenas = {"classic"}

        self.player_skins = self.generate_player_skins()
        self.enemy_skins = self.generate_enemy_skins()

        self.trails = {
            "none": {"name": "Iz Yok", "price": 0},
            "lava": {"name": "Lav Izi", "price": 15},
            "ice": {"name": "Buz Izi", "price": 20},
            "rainbow": {"name": "Gokkusagi Izi", "price": 25},
            "spark": {"name": "Kivilcim Izi", "price": 25},
            "purple": {"name": "Mor Duman", "price": 30},
            "gold": {"name": "Altin Izi", "price": 35},
            "neon": {"name": "Neon Izi", "price": 45},
            "fire_ice": {"name": "Ates + Buz", "price": 50},
            "ghost": {"name": "Hayalet Izi", "price": 55}
        }

        self.arenas = {
            "classic": {"name": "Klasik Arena", "price": 0},
            "night": {"name": "Gece Arenasi", "price": 15},
            "ocean": {"name": "Okyanus", "price": 20},
            "forest": {"name": "Orman", "price": 22},
            "lava": {"name": "Lav Gezegeni", "price": 25},
            "space": {"name": "Uzay", "price": 30},
            "ice": {"name": "Buzul", "price": 30},
            "candy": {"name": "Seker Dunyasi", "price": 35},
            "neon": {"name": "Neon Sehir", "price": 40},
            "galaxy": {"name": "Galaksi", "price": 45},
            "rainbow": {"name": "Gokkusagi Arena", "price": 50},
            "void": {"name": "Karanlik Bosluk", "price": 55}
        }

        self.speed_level = 0
        self.shield_active = False
        self.extra_life_active = False
        self.double_money_active = False
        self.small_ball_active = False
        self.slow_enemy_active = False
        self.magnet_active = False

        screen_min = min(Window.width, Window.height)

        self.normal_radius = max(dp(24), screen_min * 0.032)
        self.small_radius = self.normal_radius * 0.65
        self.enemy_radius = max(dp(21), screen_min * 0.027)
        self.star_radius = max(dp(23), screen_min * 0.028)
        self.player_radius = self.normal_radius
        self.base_speed = max(dp(9), screen_min * 0.011)

        self.player_x = Window.width / 2
        self.player_y = Window.height / 2

        self.target_x = self.player_x
        self.target_y = self.player_y

        self.lives = 3

        self.star_x = Window.width / 2
        self.star_y = Window.height / 2

        self.enemies = []

        self.enemy_timer = 0
        self.enemy_delay = 1.0

        self.invincible = False
        self.invincible_time = 0

        self.game_over = False

        self.trail_particles = []
        self.explosion_particles = []

        self.game_layer = GameLayer(size_hint=(1, 1))

        self.menu_stars = [
            (
                random.random(),
                random.random(),
                random.uniform(dp(1), dp(5))
            )
            for _ in range(85)
        ]

        self.arena_stars = [
            (
                random.random(),
                random.random(),
                random.uniform(dp(2), dp(6))
            )
            for _ in range(70)
        ]

        self.load_game()
        self.create_ui()
        self.show_menu()

        Clock.schedule_interval(
            self.update,
            1 / 60
        )

    # =====================================================
    # 216 OYUNCU KOSTUMU
    # =====================================================

    def generate_player_skins(self):

        colors = {
            "red": ("Kirmizi", (1.0, 0.08, 0.08)),
            "blue": ("Mavi", (0.10, 0.40, 1.0)),
            "green": ("Yesil", (0.10, 0.85, 0.25)),
            "purple": ("Mor", (0.70, 0.12, 0.95)),
            "pink": ("Pembe", (1.0, 0.20, 0.60)),
            "orange": ("Turuncu", (1.0, 0.45, 0.05)),
            "yellow": ("Sari", (1.0, 0.85, 0.05)),
            "white": ("Beyaz", (1.0, 1.0, 1.0)),
            "black": ("Siyah", (0.04, 0.04, 0.04)),
            "cyan": ("Turkuaz", (0.0, 0.90, 0.90)),
            "lime": ("Limon", (0.65, 1.0, 0.10)),
            "gold": ("Altin", (1.0, 0.68, 0.05))
        }

        shapes = {
            "circle": "Top",
            "square": "Kare",
            "triangle": "Ucgen",
            "diamond": "Elmas",
            "hex": "Altigen",
            "star": "Yildiz"
        }

        effects = {
            "normal": ("Normal", 0),
            "neon": ("Neon", 12),
            "blink": ("Yanip Sonen", 18)
        }

        skins = {}

        for color_key, (color_name, rgb) in colors.items():

            for shape_key, shape_name in shapes.items():

                for effect_key, (effect_name, bonus) in effects.items():

                    key = (
                        f"player_{color_key}_"
                        f"{shape_key}_{effect_key}"
                    )

                    base_price = {
                        "circle": 8,
                        "square": 10,
                        "triangle": 12,
                        "diamond": 14,
                        "hex": 16,
                        "star": 18
                    }[shape_key]

                    price = base_price + bonus

                    if key == "player_red_circle_normal":
                        price = 0

                    skins[key] = {
                        "name":
                        f"{effect_name} "
                        f"{color_name} "
                        f"{shape_name}",

                        "price": price,
                        "shape": shape_key,
                        "effect": effect_key,
                        "color": rgb
                    }

        return skins

    # =====================================================
    # 120 DUSMAN KOSTUMU
    # =====================================================

    def generate_enemy_skins(self):

        colors = {
            "black": ("Siyah", (0.03, 0.03, 0.03)),
            "white": ("Beyaz", (1.0, 1.0, 1.0)),
            "red": ("Kirmizi", (1.0, 0.10, 0.10)),
            "blue": ("Mavi", (0.10, 0.40, 1.0)),
            "green": ("Yesil", (0.10, 0.80, 0.25)),
            "purple": ("Mor", (0.70, 0.10, 0.90)),
            "orange": ("Turuncu", (1.0, 0.45, 0.05)),
            "cyan": ("Turkuaz", (0.0, 0.90, 0.90)),
            "gold": ("Altin", (1.0, 0.68, 0.05)),
            "pink": ("Pembe", (1.0, 0.20, 0.60))
        }

        shapes = {
            "circle": "Top",
            "square": "Kare",
            "triangle": "Ucgen",
            "diamond": "Elmas",
            "hex": "Altigen",
            "star": "Yildiz"
        }

        effects = {
            "normal": ("Normal", 0),
            "neon": ("Neon", 12)
        }

        skins = {}

        for color_key, (color_name, rgb) in colors.items():

            for shape_key, shape_name in shapes.items():

                for effect_key, (effect_name, bonus) in effects.items():

                    key = (
                        f"enemy_{color_key}_"
                        f"{shape_key}_{effect_key}"
                    )

                    base_price = {
                        "circle": 8,
                        "square": 10,
                        "triangle": 12,
                        "diamond": 14,
                        "hex": 16,
                        "star": 18
                    }[shape_key]

                    price = base_price + bonus

                    if key == "enemy_black_circle_normal":
                        price = 0

                    skins[key] = {
                        "name":
                        f"{effect_name} "
                        f"{color_name} "
                        f"{shape_name}",

                        "price": price,
                        "shape": shape_key,
                        "effect": effect_key,
                        "color": rgb
                    }

        return skins

    # =====================================================
    # UI
    # =====================================================

    def create_ui(self):

        self.title = Label(
            text="[b]BALL ESCAPE[/b]",
            markup=True,
            font_size="52sp",
            size_hint=(0.95, 0.15),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.83
            }
        )

        self.subtitle = Label(
            text="KAC  •  YILDIZLARI TOPLA  •  HAYATTA KAL",
            font_size="15sp",
            color=(0.75, 0.90, 1, 1),
            size_hint=(0.9, 0.08),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.73
            }
        )

        self.menu_info = Label(
            text="",
            font_size="20sp",
            color=(1, 0.87, 0.2, 1),
            size_hint=(0.90, 0.12),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.63
            }
        )

        self.start_button = Button(
            text="OYUNA BASLA",
            font_size="25sp",
            bold=True,
            size_hint=(0.62, 0.13),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.45
            },
            background_color=(
                0.08,
                0.55,
                1,
                1
            )
        )

        self.shop_button = Button(
            text="MAGAZA",
            font_size="24sp",
            bold=True,
            size_hint=(0.62, 0.13),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.26
            },
            background_color=(
                0.65,
                0.15,
                0.95,
                1
            )
        )

        self.start_button.bind(
            on_release=self.start_game
        )

        self.shop_button.bind(
            on_release=self.open_shop
        )

        # CAN + PARA AYRI SATIRLAR

        self.hud = HudBox(
            size_hint=(0.34, 0.15),
            pos_hint={
                "x": 0.015,
                "top": 0.985
            }
        )

        self.life_label = Label(
            text="CAN: 3",
            font_size="20sp",
            bold=True,
            color=(1, 0.25, 0.25, 1),
            halign="left",
            valign="middle"
        )

        self.money_label = Label(
            text="PARA: 0",
            font_size="20sp",
            bold=True,
            color=(1, 0.86, 0.08, 1),
            halign="left",
            valign="middle"
        )

        self.life_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        self.money_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        self.hud.add_widget(
            self.life_label
        )

        self.hud.add_widget(
            self.money_label
        )

        self.game_over_title = Label(
            text="OYUN BITTI!",
            font_size="42sp",
            bold=True,
            size_hint=(0.9, 0.15),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.70
            }
        )

        self.game_over_info = Label(
            text="",
            font_size="22sp",
            color=(1, 0.85, 0.1, 1),
            size_hint=(0.8, 0.10),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.57
            }
        )

        self.respawn_button = Button(
            text="YENIDEN DOG",
            font_size="23sp",
            size_hint=(0.58, 0.12),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.40
            },
            background_color=(
                0.08,
                0.72,
                0.25,
                1
            )
        )

        self.death_menu_button = Button(
            text="ANA MENU",
            font_size="23sp",
            size_hint=(0.58, 0.12),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.23
            },
            background_color=(
                0.1,
                0.4,
                1,
                1
            )
        )

        self.respawn_button.bind(
            on_release=self.respawn
        )

        self.death_menu_button.bind(
            on_release=self.return_menu
        )

    # =====================================================
    # KAYIT
    # =====================================================

    def save_game(self):

        data = {
            "money": self.money,
            "selected_skin": self.selected_skin,
            "selected_enemy": self.selected_enemy,
            "selected_trail": self.selected_trail,
            "selected_arena": self.selected_arena,
            "owned_skins": list(self.owned_skins),
            "owned_enemies": list(self.owned_enemies),
            "owned_trails": list(self.owned_trails),
            "owned_arenas": list(self.owned_arenas)
        }

        try:

            with open(
                self.save_file,
                "w"
            ) as file:

                json.dump(
                    data,
                    file
                )

        except Exception:
            pass

    def load_game(self):

        if not os.path.exists(
            self.save_file
        ):
            return

        try:

            with open(
                self.save_file,
                "r"
            ) as file:

                data = json.load(
                    file
                )

            self.money = data.get(
                "money",
                0
            )

            self.selected_skin = data.get(
                "selected_skin",
                "player_red_circle_normal"
            )

            self.selected_enemy = data.get(
                "selected_enemy",
                "enemy_black_circle_normal"
            )

            self.selected_trail = data.get(
                "selected_trail",
                "none"
            )

            self.selected_arena = data.get(
                "selected_arena",
                "classic"
            )

            self.owned_skins = set(
                data.get(
                    "owned_skins",
                    ["player_red_circle_normal"]
                )
            )

            self.owned_enemies = set(
                data.get(
                    "owned_enemies",
                    ["enemy_black_circle_normal"]
                )
            )

            self.owned_trails = set(
                data.get(
                    "owned_trails",
                    ["none"]
                )
            )

            self.owned_arenas = set(
                data.get(
                    "owned_arenas",
                    ["classic"]
                )
            )

        except Exception:
            return

        if self.selected_skin not in self.player_skins:
            self.selected_skin = (
                "player_red_circle_normal"
            )

        if self.selected_enemy not in self.enemy_skins:
            self.selected_enemy = (
                "enemy_black_circle_normal"
            )

        if self.selected_trail not in self.trails:
            self.selected_trail = "none"

        if self.selected_arena not in self.arenas:
            self.selected_arena = "classic"

        self.owned_skins.add(
            "player_red_circle_normal"
        )

        self.owned_enemies.add(
            "enemy_black_circle_normal"
        )

        self.owned_trails.add(
            "none"
        )

        self.owned_arenas.add(
            "classic"
        )

    # =====================================================
    # GOKKUSAGI
    # =====================================================

    def rainbow_color(
        self,
        offset=0
    ):

        hue = (
            (
                time.time() * 1000
                + offset
            )
            % 3000
        ) / 3000

        return colorsys.hsv_to_rgb(
            hue,
            1,
            1
        )

    # =====================================================
    # ANA MENU ARKA PLANI
    # =====================================================

    def draw_menu_background(self):

        self.game_layer.canvas.clear()

        t = time.time()

        with self.game_layer.canvas:

            Color(
                0.015,
                0.025,
                0.09,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            Color(
                0.45,
                0.05,
                0.75,
                0.20
            )

            Ellipse(
                pos=(
                    -Window.width * 0.25,
                    -Window.height * 0.18
                ),
                size=(
                    Window.width * 0.9,
                    Window.width * 0.9
                )
            )

            Color(
                0,
                0.55,
                1,
                0.15
            )

            Ellipse(
                pos=(
                    Window.width * 0.55,
                    Window.height * 0.55
                ),
                size=(
                    Window.width * 0.65,
                    Window.width * 0.65
                )
            )

            for rx, ry, size in self.menu_stars:

                alpha = (
                    0.35
                    + 0.35
                    * (
                        math.sin(
                            t * 2
                            + rx * 20
                        )
                        + 1
                    )
                    / 2
                )

                Color(
                    1,
                    1,
                    1,
                    alpha
                )

                Ellipse(
                    pos=(
                        rx * Window.width,
                        ry * Window.height
                    ),
                    size=(
                        size,
                        size
                    )
                )

            for i in range(7):

                c = self.rainbow_color(
                    i * 430
                )

                Color(
                    c[0],
                    c[1],
                    c[2],
                    0.20
                )

                radius = (
                    dp(45)
                    + i * dp(22)
                    + math.sin(
                        t * 1.4
                        + i
                    ) * dp(6)
                )

                x = (
                    Window.width * 0.5
                    + math.cos(
                        t * 0.22
                        + i
                    )
                    * Window.width
                    * 0.38
                )

                y = (
                    Window.height * 0.5
                    + math.sin(
                        t * 0.28
                        + i
                    )
                    * Window.height
                    * 0.34
                )

                Line(
                    circle=(
                        x,
                        y,
                        radius
                    ),
                    width=dp(2)
                )

    # =====================================================
    # ANA MENU
    # =====================================================

    def show_menu(
        self,
        *args
    ):

        self.state = "menu"

        self.clear_widgets()

        self.draw_menu_background()

        self.add_widget(
            self.game_layer
        )

        self.menu_info.text = (
            f"PARA: {self.money}\n"
            f"OYUN ARENASI: "
            f"{self.arenas[self.selected_arena]['name']}"
        )

        self.add_widget(
            self.title
        )

        self.add_widget(
            self.subtitle
        )

        self.add_widget(
            self.menu_info
        )

        self.add_widget(
            self.start_button
        )

        self.add_widget(
            self.shop_button
        )

    # =====================================================
    # MAGAZA
    # =====================================================

    def open_shop(
        self,
        *args
    ):

        self.state = "shop"

        self.clear_widgets()

        self.draw_menu_background()

        self.add_widget(
            self.game_layer
        )

        title = Label(
            text="MAGAZA",
            font_size="38sp",
            bold=True,
            size_hint=(0.8, 0.12),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.90
            }
        )

        cash = Label(
            text=f"PARA: {self.money}",
            font_size="21sp",
            color=(1, 0.85, 0.1, 1),
            size_hint=(0.6, 0.07),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.80
            }
        )

        self.add_widget(title)
        self.add_widget(cash)

        categories = [

            (
                "OYUNCU KOSTUMLERI 216+",
                self.open_skins
            ),

            (
                "DUSMAN KOSTUMLERI 120+",
                self.open_enemies
            ),

            (
                "IZ EFEKTLERI",
                self.open_trails
            ),

            (
                "ARENA KOSTUMLERI",
                self.open_arenas
            ),

            (
                "OZEL GUCLER",
                self.open_powers
            )
        ]

        y = 0.66

        for text, callback in categories:

            button = Button(
                text=text,
                font_size="18sp",
                size_hint=(0.72, 0.095),
                pos_hint={
                    "center_x": 0.5,
                    "center_y": y
                }
            )

            button.bind(
                on_release=callback
            )

            self.add_widget(
                button
            )

            y -= 0.115

        back = Button(
            text="ANA MENU",
            font_size="18sp",
            size_hint=(0.45, 0.08),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.055
            }
        )

        back.bind(
            on_release=self.show_menu
        )

        self.add_widget(
            back
        )

    # =====================================================
    # KAYDIRMALI MAGAZA
    # =====================================================

    def create_shop_list(
        self,
        title_text,
        items,
        owned,
        selected,
        category
    ):

        self.clear_widgets()

        self.draw_menu_background()

        self.add_widget(
            self.game_layer
        )

        title = Label(
            text=title_text,
            font_size="25sp",
            bold=True,
            size_hint=(0.95, 0.10),
            pos_hint={
                "center_x": 0.5,
                "top": 0.98
            }
        )

        cash = Label(
            text=f"PARA: {self.money}",
            font_size="19sp",
            color=(1, 0.85, 0.1, 1),
            size_hint=(0.4, 0.06),
            pos_hint={
                "x": 0.02,
                "top": 0.89
            }
        )

        self.add_widget(
            title
        )

        self.add_widget(
            cash
        )

        scroll = ScrollView(
            size_hint=(0.92, 0.69),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.46
            }
        )

        grid = GridLayout(
            cols=1,
            spacing=dp(8),
            padding=dp(8),
            size_hint_y=None
        )

        grid.bind(
            minimum_height=
            grid.setter("height")
        )

        for key, item in items.items():

            if key == selected:

                text = (
                    item["name"]
                    + " - SECILI"
                )

            elif key in owned:

                text = (
                    item["name"]
                    + " - SEC"
                )

            else:

                text = (
                    item["name"]
                    + " - "
                    + str(
                        item["price"]
                    )
                    + " PARA"
                )

            button = Button(
                text=text,
                font_size="16sp",
                size_hint_y=None,
                height=dp(68)
            )

            button.item_key = key

            if key == selected:

                button.background_color = (
                    0.1,
                    0.75,
                    0.25,
                    1
                )

            elif key in owned:

                button.background_color = (
                    0.15,
                    0.45,
                    1,
                    1
                )

            else:

                button.background_color = (
                    0.28,
                    0.30,
                    0.45,
                    1
                )

            button.bind(
                on_release=
                lambda btn,
                cat=category:
                self.buy_item(
                    cat,
                    btn.item_key
                )
            )

            grid.add_widget(
                button
            )

        scroll.add_widget(
            grid
        )

        self.add_widget(
            scroll
        )

        back = Button(
            text="GERI",
            font_size="18sp",
            size_hint=(0.42, 0.08),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.05
            }
        )

        back.bind(
            on_release=self.open_shop
        )

        self.add_widget(
            back
        )

    def open_skins(
        self,
        *args
    ):

        self.state = "skins"

        self.create_shop_list(
            "OYUNCU KOSTUMLERI",
            self.player_skins,
            self.owned_skins,
            self.selected_skin,
            "skin"
        )

    def open_enemies(
        self,
        *args
    ):

        self.state = "enemies"

        self.create_shop_list(
            "DUSMAN KOSTUMLERI",
            self.enemy_skins,
            self.owned_enemies,
            self.selected_enemy,
            "enemy"
        )

    def open_trails(
        self,
        *args
    ):

        self.state = "trails"

        self.create_shop_list(
            "IZ EFEKTLERI",
            self.trails,
            self.owned_trails,
            self.selected_trail,
            "trail"
        )

    def open_arenas(
        self,
        *args
    ):

        self.state = "arenas"

        self.create_shop_list(
            "ARENA KOSTUMLERI",
            self.arenas,
            self.owned_arenas,
            self.selected_arena,
            "arena"
        )

    def buy_item(
        self,
        category,
        key
    ):

        if category == "skin":

            items = self.player_skins
            owned = self.owned_skins

        elif category == "enemy":

            items = self.enemy_skins
            owned = self.owned_enemies

        elif category == "trail":

            items = self.trails
            owned = self.owned_trails

        else:

            items = self.arenas
            owned = self.owned_arenas

        item = items[key]

        if key not in owned:

            if self.money < item["price"]:
                return

            self.money -= item["price"]

            owned.add(
                key
            )

        if category == "skin":

            self.selected_skin = key

            self.save_game()

            self.open_skins()

        elif category == "enemy":

            self.selected_enemy = key

            self.save_game()

            self.open_enemies()

        elif category == "trail":

            self.selected_trail = key

            self.save_game()

            self.open_trails()

        else:

            self.selected_arena = key

            self.save_game()

            self.open_arenas()

    # =====================================================
    # OZEL GUCLER
    # =====================================================

    def open_powers(
        self,
        *args
    ):

        self.state = "powers"

        self.clear_widgets()

        self.draw_menu_background()

        self.add_widget(
            self.game_layer
        )

        title = Label(
            text="OZEL GUCLER - 1 TUR",
            font_size="25sp",
            bold=True,
            size_hint=(0.8, 0.10),
            pos_hint={
                "center_x": 0.5,
                "top": 0.97
            }
        )

        cash = Label(
            text=f"PARA: {self.money}",
            font_size="19sp",
            color=(1, 0.85, 0.1, 1),
            size_hint=(0.5, 0.06),
            pos_hint={
                "center_x": 0.5,
                "top": 0.87
            }
        )

        self.add_widget(
            title
        )

        self.add_widget(
            cash
        )

        powers = [

            (
                "HIZ +1 - 5 PARA",
                "speed",
                5
            ),

            (
                "KALKAN - 8 PARA",
                "shield",
                8
            ),

            (
                "+1 CAN - 10 PARA",
                "life",
                10
            ),

            (
                "2X PARA - 15 PARA",
                "double",
                15
            ),

            (
                "KUCUK TOP - 12 PARA",
                "small",
                12
            ),

            (
                "YAVAS DUSMAN - 15 PARA",
                "slow",
                15
            ),

            (
                "MIKNATIS - 12 PARA",
                "magnet",
                12
            )
        ]

        y = 0.72

        for text, power, price in powers:

            button = Button(
                text=text,
                font_size="17sp",
                size_hint=(0.70, 0.08),
                pos_hint={
                    "center_x": 0.5,
                    "center_y": y
                }
            )

            button.bind(
                on_release=
                lambda btn,
                p=power,
                pr=price:
                self.buy_power(
                    p,
                    pr
                )
            )

            self.add_widget(
                button
            )

            y -= 0.09

        back = Button(
            text="GERI",
            font_size="18sp",
            size_hint=(0.42, 0.07),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.04
            }
        )

        back.bind(
            on_release=self.open_shop
        )

        self.add_widget(
            back
        )

    def buy_power(
        self,
        power,
        price
    ):

        if self.money < price:
            return

        if power == "speed":

            if self.speed_level >= 3:
                return

            self.speed_level += 1

        elif power == "shield":

            if self.shield_active:
                return

            self.shield_active = True

        elif power == "life":

            if self.extra_life_active:
                return

            self.extra_life_active = True

        elif power == "double":

            if self.double_money_active:
                return

            self.double_money_active = True

        elif power == "small":

            if self.small_ball_active:
                return

            self.small_ball_active = True

        elif power == "slow":

            if self.slow_enemy_active:
                return

            self.slow_enemy_active = True

        elif power == "magnet":

            if self.magnet_active:
                return

            self.magnet_active = True

        self.money -= price

        self.save_game()

        self.open_powers()

    def clear_powers(self):

        self.speed_level = 0

        self.shield_active = False
        self.extra_life_active = False
        self.double_money_active = False
        self.small_ball_active = False
        self.slow_enemy_active = False
        self.magnet_active = False

    # =====================================================
    # OYUNU BASLAT
    # =====================================================

    def start_game(
        self,
        *args
    ):

        self.state = "game"

        self.clear_widgets()

        self.add_widget(
            self.game_layer
        )

        self.player_x = (
            Window.width / 2
        )

        self.player_y = (
            Window.height / 2
        )

        self.target_x = self.player_x
        self.target_y = self.player_y

        self.lives = (
            4
            if self.extra_life_active
            else 3
        )

        self.player_radius = (
            self.small_radius
            if self.small_ball_active
            else self.normal_radius
        )

        self.enemies.clear()

        self.trail_particles.clear()

        self.explosion_particles.clear()

        self.enemy_timer = 0
        self.enemy_delay = 1.0

        self.invincible = False
        self.invincible_time = 0

        self.game_over = False

        self.new_star()

        self.life_label.text = (
            f"CAN: {self.lives}"
        )

        self.money_label.text = (
            f"PARA: {self.money}"
        )

        self.add_widget(
            self.hud
        )

        self.draw_game()

    # =====================================================
    # YILDIZ
    # =====================================================

    def new_star(self):

        margin = (
            self.star_radius
            + dp(30)
        )

        self.star_x = random.uniform(
            margin,
            max(
                margin,
                Window.width - margin
            )
        )

        self.star_y = random.uniform(
            margin,
            max(
                margin,
                Window.height - margin
            )
        )

    def draw_star(
        self,
        x,
        y,
        radius
    ):

        points = []

        for i in range(10):

            angle = (
                -math.pi / 2
                + i * math.pi / 5
            )

            r = (
                radius
                if i % 2 == 0
                else radius * 0.44
            )

            points.append(
                (
                    x
                    + math.cos(angle)
                    * r,

                    y
                    + math.sin(angle)
                    * r
                )
            )

        Color(
            1,
            0.82,
            0.02,
            1
        )

        for i in range(10):

            p1 = points[i]

            p2 = points[
                (i + 1) % 10
            ]

            Triangle(
                points=[
                    x,
                    y,

                    p1[0],
                    p1[1],

                    p2[0],
                    p2[1]
                ]
            )

        Color(
            1,
            0.95,
            0.4,
            0.30
        )

        Line(
            circle=(
                x,
                y,
                radius * 1.25
            ),
            width=dp(1.4)
        )

    # =====================================================
    # SEKIL CIZ
    # =====================================================

    def draw_shape(
        self,
        shape,
        x,
        y,
        r,
        color,
        effect="normal"
    ):

        c = color

        if effect == "neon":

            Color(
                c[0],
                c[1],
                c[2],
                0.25
            )

            Ellipse(
                pos=(
                    x - r - dp(10),
                    y - r - dp(10)
                ),
                size=(
                    r * 2 + dp(20),
                    r * 2 + dp(20)
                )
            )

        if effect == "blink":

            if (
                int(
                    time.time() * 6
                ) % 2 == 0
            ):

                c = self.rainbow_color()

        Color(
            c[0],
            c[1],
            c[2],
            1
        )

        if shape == "circle":

            Ellipse(
                pos=(
                    x - r,
                    y - r
                ),
                size=(
                    r * 2,
                    r * 2
                )
            )

        elif shape == "square":

            Rectangle(
                pos=(
                    x - r,
                    y - r
                ),
                size=(
                    r * 2,
                    r * 2
                )
            )

        elif shape == "triangle":

            Triangle(
                points=[
                    x,
                    y + r,

                    x + r,
                    y - r,

                    x - r,
                    y - r
                ]
            )

        elif shape == "diamond":

            Triangle(
                points=[
                    x,
                    y + r,

                    x + r,
                    y,

                    x,
                    y - r
                ]
            )

            Triangle(
                points=[
                    x,
                    y + r,

                    x,
                    y - r,

                    x - r,
                    y
                ]
            )

        elif shape == "hex":

            pts = []

            for i in range(6):

                a = (
                    math.pi / 3
                    * i
                )

                pts.append(
                    (
                        x
                        + math.cos(a)
                        * r,

                        y
                        + math.sin(a)
                        * r
                    )
                )

            for i in range(6):

                p1 = pts[i]

                p2 = pts[
                    (i + 1) % 6
                ]

                Triangle(
                    points=[
                        x,
                        y,

                        p1[0],
                        p1[1],

                        p2[0],
                        p2[1]
                    ]
                )

        elif shape == "star":

            points = []

            for i in range(10):

                a = (
                    -math.pi / 2
                    + i * math.pi / 5
                )

                rr = (
                    r
                    if i % 2 == 0
                    else r * 0.45
                )

                points.append(
                    (
                        x
                        + math.cos(a)
                        * rr,

                        y
                        + math.sin(a)
                        * rr
                    )
                )

            for i in range(10):

                p1 = points[i]

                p2 = points[
                    (i + 1) % 10
                ]

                Triangle(
                    points=[
                        x,
                        y,

                        p1[0],
                        p1[1],

                        p2[0],
                        p2[1]
                    ]
                )

    # =====================================================
    # DUSMAN
    # =====================================================

    def create_enemy(self):

        radius = self.enemy_radius

        side = random.randint(
            0,
            3
        )

        if side == 0:

            x = random.uniform(
                0,
                Window.width
            )

            y = (
                Window.height
                + radius
            )

        elif side == 1:

            x = (
                Window.width
                + radius
            )

            y = random.uniform(
                0,
                Window.height
            )

        elif side == 2:

            x = random.uniform(
                0,
                Window.width
            )

            y = -radius

        else:

            x = -radius

            y = random.uniform(
                0,
                Window.height
            )

        angle = math.atan2(
            self.player_y - y,
            self.player_x - x
        )

        speed = random.uniform(
            dp(3),
            dp(6)
        )

        if self.slow_enemy_active:

            speed *= 0.65

        self.enemies.append(
            {
                "x": x,
                "y": y,

                "dx":
                math.cos(angle)
                * speed,

                "dy":
                math.sin(angle)
                * speed,

                "radius":
                radius
            }
        )

    # =====================================================
    # CARPISMA
    # =====================================================

    def touching(
        self,
        x1,
        y1,
        r1,
        x2,
        y2,
        r2
    ):

        return (
            math.hypot(
                x1 - x2,
                y1 - y2
            )
            <
            r1 + r2
        )

    # =====================================================
    # PATLAMA
    # =====================================================

    def create_explosion(
        self,
        x,
        y
    ):

        for _ in range(28):

            angle = random.uniform(
                0,
                math.pi * 2
            )

            speed = random.uniform(
                dp(2),
                dp(7)
            )

            self.explosion_particles.append(
                {
                    "x": x,
                    "y": y,

                    "dx":
                    math.cos(angle)
                    * speed,

                    "dy":
                    math.sin(angle)
                    * speed,

                    "life":
                    0.60,

                    "size":
                    random.uniform(
                        dp(4),
                        dp(10)
                    )
                }
            )

    # =====================================================
    # IZ
    # =====================================================

    def create_trail(self):

        if self.selected_trail == "none":
            return

        self.trail_particles.append(
            {
                "x":
                self.player_x,

                "y":
                self.player_y,

                "life":
                0.45,

                "size":
                random.uniform(
                    dp(5),
                    dp(12)
                )
            }
        )

        if len(
            self.trail_particles
        ) > 100:

            self.trail_particles.pop(
                0
            )

    def get_trail_color(self):

        key = self.selected_trail

        if key == "lava":

            return random.choice(
                [
                    (1, 0.1, 0),
                    (1, 0.45, 0),
                    (1, 0.8, 0)
                ]
            )

        if key == "ice":

            return (
                0.2,
                0.85,
                1
            )

        if key == "rainbow":

            return self.rainbow_color(
                random.randint(
                    0,
                    2000
                )
            )

        if key == "spark":

            return (
                1,
                0.9,
                0.1
            )

        if key == "purple":

            return (
                0.7,
                0.15,
                1
            )

        if key == "gold":

            return (
                1,
                0.7,
                0.05
            )

        if key == "neon":

            return self.rainbow_color()

        if key == "fire_ice":

            return random.choice(
                [
                    (1, 0.25, 0),
                    (0.1, 0.8, 1)
                ]
            )

        if key == "ghost":

            return (
                0.8,
                0.9,
                1
            )

        return (
            1,
            1,
            1
        )

    # =====================================================
    # KOSTUM GORUNUMLERI
    # =====================================================

    def get_player_visual(self):

        skin = self.player_skins[
            self.selected_skin
        ]

        return (
            skin["shape"],
            skin["color"],
            skin["effect"]
        )

    def get_enemy_visual(self):

        skin = self.enemy_skins[
            self.selected_enemy
        ]

        color = skin[
            "color"
        ]

        if (
            self.selected_arena
            in (
                "night",
                "lava",
                "space",
                "neon",
                "galaxy",
                "void"
            )
            and
            max(color) < 0.20
        ):

            color = (
                1,
                1,
                1
            )

        return (
            skin["shape"],
            color,
            skin["effect"]
        )

    # =====================================================
    # DOKUNMATIK
    # =====================================================

    def on_touch_down(
        self,
        touch
    ):

        if self.state != "game":

            return super().on_touch_down(
                touch
            )

        if self.game_over:

            return super().on_touch_down(
                touch
            )

        self.target_x = touch.x
        self.target_y = touch.y

        return True

    def on_touch_move(
        self,
        touch
    ):

        if (
            self.state == "game"
            and
            not self.game_over
        ):

            self.target_x = touch.x
            self.target_y = touch.y

            return True

        return super().on_touch_move(
            touch
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt
    ):

        if self.state != "game":

            if self.state in (
                "menu",
                "shop",
                "skins",
                "enemies",
                "trails",
                "arenas",
                "powers"
            ):

                self.draw_menu_background()

            return

        if not self.game_over:

            player_speed = (
                self.base_speed
                + self.speed_level
                * dp(2)
            )

            dx = (
                self.target_x
                - self.player_x
            )

            dy = (
                self.target_y
                - self.player_y
            )

            distance = math.hypot(
                dx,
                dy
            )

            if distance > player_speed:

                self.player_x += (
                    dx / distance
                ) * player_speed

                self.player_y += (
                    dy / distance
                ) * player_speed

            else:

                self.player_x = (
                    self.target_x
                )

                self.player_y = (
                    self.target_y
                )

            self.player_x = max(
                self.player_radius,

                min(
                    Window.width
                    - self.player_radius,

                    self.player_x
                )
            )

            self.player_y = max(
                self.player_radius,

                min(
                    Window.height
                    - self.player_radius,

                    self.player_y
                )
            )

            if distance > dp(2):

                self.create_trail()

            if self.magnet_active:

                star_distance = math.hypot(
                    self.player_x
                    - self.star_x,

                    self.player_y
                    - self.star_y
                )

                if (
                    star_distance
                    < Window.width * 0.35

                    and

                    star_distance > 1
                ):

                    self.star_x += (
                        self.player_x
                        - self.star_x
                    ) / star_distance * dp(5)

                    self.star_y += (
                        self.player_y
                        - self.star_y
                    ) / star_distance * dp(5)

            self.enemy_timer += dt

            if (
                self.enemy_timer
                >= self.enemy_delay
            ):

                self.create_enemy()

                self.enemy_timer = 0

            for enemy in self.enemies:

                enemy["x"] += (
                    enemy["dx"]
                )

                enemy["y"] += (
                    enemy["dy"]
                )

            self.enemies = [
                e
                for e in self.enemies
                if (
                    -dp(300)
                    < e["x"]
                    < Window.width
                    + dp(300)

                    and

                    -dp(300)
                    < e["y"]
                    < Window.height
                    + dp(300)
                )
            ]

            if self.touching(
                self.player_x,
                self.player_y,
                self.player_radius,

                self.star_x,
                self.star_y,
                self.star_radius
            ):

                self.money += (
                    2
                    if self.double_money_active
                    else 1
                )

                self.money_label.text = (
                    f"PARA: {self.money}"
                )

                self.save_game()

                self.new_star()

                self.enemy_delay = max(
                    0.35,
                    self.enemy_delay
                    - 0.02
                )

            if self.invincible:

                self.invincible_time -= dt

                if self.invincible_time <= 0:

                    self.invincible = False

            if not self.invincible:

                for enemy in self.enemies[:]:

                    if self.touching(
                        self.player_x,
                        self.player_y,
                        self.player_radius,

                        enemy["x"],
                        enemy["y"],
                        enemy["radius"]
                    ):

                        self.create_explosion(
                            enemy["x"],
                            enemy["y"]
                        )

                        self.enemies.remove(
                            enemy
                        )

                        if self.shield_active:

                            self.shield_active = False

                        else:

                            self.lives -= 1

                            self.invincible = True
                            self.invincible_time = 1

                        if self.lives <= 0:

                            self.lives = 0

                            self.game_over = True

                            self.clear_powers()

                            self.save_game()

                        break

        for p in self.trail_particles[:]:

            p["life"] -= dt

            p["size"] *= 0.95

            if p["life"] <= 0:

                self.trail_particles.remove(
                    p
                )

        for p in self.explosion_particles[:]:

            p["life"] -= dt

            p["x"] += p["dx"]

            p["y"] += p["dy"]

            p["size"] *= 0.94

            if p["life"] <= 0:

                self.explosion_particles.remove(
                    p
                )

        self.life_label.text = (
            f"CAN: {self.lives}"
        )

        self.money_label.text = (
            f"PARA: {self.money}"
        )

        self.draw_game()

        if self.game_over:

            if (
                self.game_over_title.parent
                is None
            ):

                self.game_over_info.text = (
                    f"TOPLAM PARA: "
                    f"{self.money}"
                )

                self.add_widget(
                    self.game_over_title
                )

                self.add_widget(
                    self.game_over_info
                )

                self.add_widget(
                    self.respawn_button
                )

                self.add_widget(
                    self.death_menu_button
                )

    # =====================================================
    # OYUN CIZ
    # =====================================================

    def draw_game(self):

        self.game_layer.canvas.clear()

        with self.game_layer.canvas:

            self.draw_arena()

            # IZ

            for p in self.trail_particles:

                c = self.get_trail_color()

                Color(
                    c[0],
                    c[1],
                    c[2],
                    0.68
                )

                Ellipse(
                    pos=(
                        p["x"]
                        - p["size"] / 2,

                        p["y"]
                        - p["size"] / 2
                    ),

                    size=(
                        p["size"],
                        p["size"]
                    )
                )

            # YILDIZ

            self.draw_star(
                self.star_x,
                self.star_y,
                self.star_radius
            )

            # DUSMAN KOSTUMU

            enemy_shape, enemy_color, enemy_effect = (
                self.get_enemy_visual()
            )

            for enemy in self.enemies:

                border = (
                    (0, 0, 0)
                    if max(enemy_color) > 0.8
                    else (1, 1, 1)
                )

                Color(
                    border[0],
                    border[1],
                    border[2],
                    0.85
                )

                Ellipse(
                    pos=(
                        enemy["x"]
                        - enemy["radius"]
                        - dp(3),

                        enemy["y"]
                        - enemy["radius"]
                        - dp(3)
                    ),

                    size=(
                        enemy["radius"] * 2
                        + dp(6),

                        enemy["radius"] * 2
                        + dp(6)
                    )
                )

                self.draw_shape(
                    enemy_shape,
                    enemy["x"],
                    enemy["y"],
                    enemy["radius"],
                    enemy_color,
                    enemy_effect
                )

            # OYUNCU KOSTUMU

            if (
                not self.invincible
                or
                int(
                    self.invincible_time
                    * 10
                ) % 2 == 0
            ):

                shape, color, effect = (
                    self.get_player_visual()
                )

                self.draw_shape(
                    shape,
                    self.player_x,
                    self.player_y,
                    self.player_radius,
                    color,
                    effect
                )

            # PATLAMA

            for p in self.explosion_particles:

                c = random.choice(
                    [
                        (1, 0.1, 0),
                        (1, 0.45, 0),
                        (1, 0.8, 0)
                    ]
                )

                Color(
                    c[0],
                    c[1],
                    c[2],
                    1
                )

                Ellipse(
                    pos=(
                        p["x"]
                        - p["size"] / 2,

                        p["y"]
                        - p["size"] / 2
                    ),

                    size=(
                        p["size"],
                        p["size"]
                    )
                )

            if self.game_over:

                Color(
                    0,
                    0,
                    0,
                    0.72
                )

                Rectangle(
                    pos=(0, 0),
                    size=Window.size
                )

    # =====================================================
    # ARENALAR SADECE OYUNDA
    # =====================================================

    def draw_arena(self):

        arena = self.selected_arena

        t = time.time()

        if arena == "classic":

            Color(
                0.82,
                0.91,
                1,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for i in range(18):

                Color(
                    0.1,
                    0.55,
                    1,
                    0.15
                )

                x = (
                    i * dp(95)
                    + math.sin(
                        t + i
                    ) * dp(15)
                ) % Window.width

                y = (
                    i * dp(135)
                ) % Window.height

                Ellipse(
                    pos=(x, y),
                    size=(
                        dp(55),
                        dp(55)
                    )
                )

        elif arena == "night":

            Color(
                0.01,
                0.015,
                0.07,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for rx, ry, size in self.arena_stars:

                Color(
                    1,
                    1,
                    1,
                    0.85
                )

                Ellipse(
                    pos=(
                        rx * Window.width,
                        ry * Window.height
                    ),
                    size=(
                        size,
                        size
                    )
                )

            Color(
                1,
                0.95,
                0.65,
                0.9
            )

            Ellipse(
                pos=(
                    Window.width
                    - dp(140),

                    Window.height
                    - dp(140)
                ),

                size=(
                    dp(90),
                    dp(90)
                )
            )

        elif arena == "ocean":

            Color(
                0.02,
                0.28,
                0.58,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for i in range(9):

                y = (
                    Window.height
                    * i / 9
                )

                wave = (
                    math.sin(
                        t * 2 + i
                    ) * dp(18)
                )

                Color(
                    0.1,
                    0.8,
                    1,
                    0.28
                )

                Line(
                    points=[
                        0,
                        y + wave,

                        Window.width,
                        y + wave
                    ],
                    width=dp(2)
                )

        elif arena == "forest":

            Color(
                0.025,
                0.24,
                0.07,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for i in range(9):

                x = (
                    i
                    * Window.width
                    / 8
                )

                Color(
                    0.28,
                    0.14,
                    0.05,
                    0.8
                )

                Rectangle(
                    pos=(x, 0),
                    size=(
                        dp(24),
                        Window.height
                    )
                )

                for j in range(4):

                    Color(
                        0.04,
                        0.55,
                        0.14,
                        0.55
                    )

                    Ellipse(
                        pos=(
                            x - dp(32),

                            j * dp(150)
                            + dp(40)
                        ),

                        size=(
                            dp(90),
                            dp(90)
                        )
                    )

        elif arena == "lava":

            Color(
                0.13,
                0.005,
                0.005,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for i in range(18):

                x = (
                    i * dp(100)
                    + t * dp(20)
                ) % Window.width

                y = (
                    i * dp(145)
                ) % Window.height

                Color(
                    1,
                    0.15,
                    0,
                    0.55
                )

                Ellipse(
                    pos=(x, y),
                    size=(
                        dp(30),
                        dp(30)
                    )
                )

        elif arena == "space":

            Color(
                0.002,
                0.002,
                0.025,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for rx, ry, size in self.arena_stars:

                Color(
                    1,
                    1,
                    1,
                    0.9
                )

                Ellipse(
                    pos=(
                        rx * Window.width,
                        ry * Window.height
                    ),
                    size=(
                        size,
                        size
                    )
                )

            Color(
                0.55,
                0.12,
                0.95,
                0.8
            )

            Ellipse(
                pos=(
                    Window.width
                    - dp(170),

                    dp(60)
                ),

                size=(
                    dp(120),
                    dp(120)
                )
            )

        elif arena == "ice":

            Color(
                0.60,
                0.88,
                1,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for i in range(14):

                x = (
                    i * dp(110)
                ) % Window.width

                y = (
                    i * dp(150)
                ) % Window.height

                Color(
                    0.9,
                    1,
                    1,
                    0.55
                )

                Triangle(
                    points=[
                        x,
                        y,

                        x + dp(40),
                        y + dp(70),

                        x + dp(80),
                        y
                    ]
                )

        elif arena == "candy":

            Color(
                1,
                0.58,
                0.76,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            candy_colors = [
                (1, 0.15, 0.55),
                (0.05, 0.8, 1),
                (1, 0.85, 0.05),
                (0.7, 0.15, 1)
            ]

            for i in range(26):

                c = candy_colors[
                    i
                    % len(candy_colors)
                ]

                x = (
                    i * dp(80)
                ) % Window.width

                y = (
                    i * dp(120)
                ) % Window.height

                Color(
                    c[0],
                    c[1],
                    c[2],
                    0.6
                )

                Ellipse(
                    pos=(x, y),
                    size=(
                        dp(30),
                        dp(30)
                    )
                )

        elif arena == "neon":

            Color(
                0.005,
                0.005,
                0.04,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            shift = (
                t * dp(25)
            ) % dp(80)

            Color(
                0,
                1,
                1,
                0.38
            )

            for x in range(
                -80,
                int(Window.width) + 80,
                80
            ):

                Line(
                    points=[
                        x + shift,
                        0,

                        x + shift,
                        Window.height
                    ],
                    width=dp(1)
                )

            Color(
                1,
                0,
                0.8,
                0.38
            )

            for y in range(
                -80,
                int(Window.height) + 80,
                80
            ):

                Line(
                    points=[
                        0,
                        y + shift,

                        Window.width,
                        y + shift
                    ],
                    width=dp(1)
                )

        elif arena == "galaxy":

            Color(
                0.055,
                0.005,
                0.15,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for rx, ry, size in self.arena_stars:

                Color(
                    0.85,
                    0.55,
                    1,
                    0.8
                )

                Ellipse(
                    pos=(
                        rx * Window.width,
                        ry * Window.height
                    ),
                    size=(
                        size,
                        size
                    )
                )

        elif arena == "rainbow":

            colors = [
                (1, 0.12, 0.12),
                (1, 0.45, 0.05),
                (1, 0.85, 0.05),
                (0.1, 0.8, 0.25),
                (0.05, 0.75, 1),
                (0.25, 0.25, 1),
                (0.7, 0.12, 1)
            ]

            band_h = (
                Window.height
                / len(colors)
            )

            for i, c in enumerate(
                colors
            ):

                Color(
                    c[0],
                    c[1],
                    c[2],
                    0.75
                )

                Rectangle(
                    pos=(
                        0,
                        i * band_h
                    ),
                    size=(
                        Window.width,
                        band_h + dp(2)
                    )
                )

        else:

            Color(
                0,
                0,
                0,
                1
            )

            Rectangle(
                pos=(0, 0),
                size=Window.size
            )

            for rx, ry, size in self.arena_stars:

                Color(
                    0.55,
                    0.12,
                    1,
                    0.75
                )

                Ellipse(
                    pos=(
                        rx * Window.width,
                        ry * Window.height
                    ),
                    size=(
                        size,
                        size
                    )
                )

    # =====================================================
    # YENIDEN DOG
    # =====================================================

    def respawn(
        self,
        *args
    ):

        self.clear_powers()

        self.start_game()

    # =====================================================
    # ANA MENU
    # =====================================================

    def return_menu(
        self,
        *args
    ):

        self.clear_powers()

        self.save_game()

        self.show_menu()


class BallEscapeApp(App):

    def build(self):

        self.title = "Ball Escape"

        return BallEscape()


BallEscapeApp().run()
