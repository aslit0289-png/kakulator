import json
import os

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.animation import Animation
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.core.window import Window


HISTORY_FILE = os.path.join(os.path.expanduser("~"), "physics_history.json")


UNITS = {
    "distance": {"м": 1.0, "км": 1000.0, "см": 0.01},
    "time": {"с": 1.0, "мин": 60.0, "ч": 3600.0},
    "mass": {"кг": 1.0, "г": 0.001, "т": 1000.0},
    "speed": {"м/с": 1.0, "км/ч": 1 / 3.6},
    "acceleration": {"м/с²": 1.0},
    "volume": {"м³": 1.0, "л": 0.001},
    "force": {"Н": 1.0, "кН": 1000.0},
    "area": {"м²": 1.0, "см²": 0.0001},
    "work": {"Дж": 1.0, "кДж": 1000.0},
    "voltage": {"В": 1.0, "кВ": 1000.0},
    "resistance": {"Ом": 1.0, "кОм": 1000.0},
    "impulse": {"кг·м/с": 1.0},
    "spring": {"Н/м": 1.0},
    "energy": {"Дж": 1.0, "кДж": 1000.0},
    "density": {"кг/м³": 1.0},
    "depth": {"м": 1.0, "см": 0.01},
    "temp": {"°C": 1.0},
    "current": {"А": 1.0, "мА": 0.001},
    "capacitance": {"Ф": 1.0, "мкФ": 0.000001},
    "induction": {"Тл": 1.0, "мТл": 0.001},    "charge": {"Кл": 1.0, "мкКл": 0.000001, "нКл": 0.000000001},
}


CONVERT_CATEGORIES = {
    "Длина": "distance",
    "Время": "time",
    "Масса": "mass",
    "Скорость": "speed",
    "Объём": "volume",
    "Сила": "force",
    "Площадь": "area",
    "Работа / Энергия": "work",
    "Напряжение": "voltage",
    "Сопротивление": "resistance",
    "Ток": "current",
    "Ёмкость": "capacitance",
    "Магнитная индукция": "induction",
}


FORMULAS = {
    "Скорость (v)": {
        "fields": [("S", "Расстояние", "distance"), ("t", "Время", "time")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "м/с", "result_key": "speed",
        "formula": "v = S / t", "fact": "Исаак Ньютон считал скорость мгновенной: v = ds/dt.", "zero": [1],
    },
    "Расстояние (S)": {
        "fields": [("v", "Скорость", "speed"), ("t", "Время", "time")],
        "calc": lambda vals: vals[0] * vals[1],
        "result_unit": "м", "result_key": "distance",
        "formula": "S = v × t", "fact": "Свет за 1 секунду проходит 299 792 км.", "zero": None,
    },
    "Время (t)": {
        "fields": [("S", "Расстояние", "distance"), ("v", "Скорость", "speed")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "с", "result_key": "time",
        "formula": "t = S / v", "fact": "Звук в воздухе летит со скоростью ~343 м/с.", "zero": [1],
    },
    "Сила (F)": {
        "fields": [("m", "Масса", "mass"), ("a", "Ускорение", "acceleration")],
        "calc": lambda vals: vals[0] * vals[1],
        "result_unit": "Н", "result_key": "force",
        "formula": "F = m × a", "fact": "Второй закон Ньютона.", "zero": None,
    },
    "Плотность (ρ)": {
        "fields": [("m", "Масса", "mass"), ("V", "Объём", "volume")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "кг/м³", "result_key": "density",
        "formula": "ρ = m / V", "fact": "Плотность воды 1000 кг/м³, железа — 7874 кг/м³.", "zero": [1],
    },
    "Ускорение (a)": {
        "fields": [("v", "Скорость", "speed"), ("t", "Время", "time")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "м/с²", "result_key": "acceleration",
        "formula": "a = v / t", "fact": "Гравитация Земли даёт ускорение 9,8 м/с².", "zero": [1],
    },
    "Энергия (E)": {
        "fields": [("m", "Масса", "mass"), ("v", "Скорость", "speed")],
        "calc": lambda vals: vals[0] * vals[1] * vals[1] / 2,
        "result_unit": "Дж", "result_key": "energy",
        "formula": "E = m × v² / 2", "fact": "Кинетическая энергия автомобиля 1000 кг на 20 м/с = 200 000 Дж.", "zero": None,
    },
    "Работа (A)": {
        "fields": [("F", "Сила", "force"), ("S", "Расстояние", "distance")],
        "calc": lambda vals: vals[0] * vals[1],
        "result_unit": "Дж", "result_key": "work",
        "formula": "A = F × S", "fact": "Поднять 1 кг на 1 метр — работа примерно 9,8 Дж.", "zero": None,
    },
    "Давление (p)": {
        "fields": [("F", "Сила", "force"), ("S", "Площадь", "area")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "Па", "result_key": None,
        "formula": "p = F / S", "fact": "Атмосферное давление — 101 325 Па.", "zero": [1],
    },
    "Мощность (N)": {
        "fields": [("A", "Работа", "work"), ("t", "Время", "time")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "Вт", "result_key": None,
        "formula": "N = A / t", "fact": "Мощность лампочки 60 Вт = 60 Дж работы за 1 секунду.", "zero": [1],
    },
    "Закон Ома (I)": {
        "fields": [("U", "Напряжение", "voltage"), ("R", "Сопротивление", "resistance")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "А", "result_key": "current",
        "formula": "I = U / R", "fact": "Закон Георга Ома (1827).", "zero": [1],
    },
    "Импульс (p)": {
        "fields": [("m", "Масса", "mass"), ("v", "Скорость", "speed")],
        "calc": lambda vals: vals[0] * vals[1],
        "result_unit": "кг·м/с", "result_key": "impulse",
        "formula": "p = m × v", "fact": "Импульс — это «количество движения».", "zero": None,
    },
    "Закон Гука (F)": {
        "fields": [("k", "Жёсткость", "spring"), ("x", "Удлинение", "distance")],
        "calc": lambda vals: vals[0] * vals[1],
        "result_unit": "Н", "result_key": "force",
        "formula": "F = k × x", "fact": "Сила упругости пропорциональна удлинению.", "zero": None,
    },
    "Теплота (Q)": {
        "fields": [("m", "Масса", "mass"), ("dt", "Изменение t°", "temp")],
        "calc": lambda vals: 4200 * vals[0] * vals[1],
        "result_unit": "Дж", "result_key": "work",
        "formula": "Q = c × m × dt", "fact": "Удельная теплоёмкость воды c = 4200 Дж/(кг·°C).", "zero": None,
    },
    "Центростремительное (a)": {
        "fields": [("v", "Скорость", "speed"), ("R", "Радиус", "distance")],
        "calc": lambda vals: vals[0] * vals[0] / vals[1],
        "result_unit": "м/с²", "result_key": "acceleration",
        "formula": "a = v² / R", "fact": "При повороте на 20 м/с и радиусе 10 м — ускорение 40 м/с².", "zero": [1],
    },
    "Давление жидкости (p)": {
        "fields": [("h", "Глубина", "depth"), ("r", "Плотность", "density")],
        "calc": lambda vals: vals[0] * vals[1] * 9.8,
        "result_unit": "Па", "result_key": None,
        "formula": "p = r × g × h", "fact": "На глубине 10 м давление воды 98 кПа.", "zero": None,
    },
    "Средняя скорость (v)": {
        "fields": [
            ("S1", "Путь 1", "distance"), ("t1", "Время 1", "time"),
            ("S2", "Путь 2", "distance"), ("t2", "Время 2", "time"),
        ],
        "calc": lambda vals: (vals[0] + vals[2]) / (vals[1] + vals[3]),
        "result_unit": "м/с", "result_key": "speed",
        "formula": "v = (S1 + S2) / (t1 + t2)", "fact": "Средняя скорость — это весь путь, делённый на всё время.", "zero": [1, 3],
    },
    "Работа через мощность (A)": {
        "fields": [("N", "Мощность", None), ("t", "Время", "time")],
        "calc": lambda vals: vals[0] * vals[1],
        "result_unit": "Дж", "result_key": "work",
        "formula": "A = N × t", "fact": "Работа = мощность × время. 100 Вт за 10 с = 1000 Дж.", "zero": None,
    },
    "Полная энергия (E)": {
        "fields": [("m", "Масса", "mass"), ("v", "Скорость", "speed"), ("h", "Высота", "distance")],
        "calc": lambda vals: vals[0] * vals[1] * vals[1] / 2 + vals[0] * 9.8 * vals[2],
        "result_unit": "Дж", "result_key": "energy",
        "formula": "E = m×v²/2 + m×g×h", "fact": "Полная механическая энергия = кинетическая + потенциальная.", "zero": None,
    },
    "Объём (V)": {
        "fields": [("m", "Масса", "mass"), ("r", "Плотность", "density")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "м³", "result_key": "volume",
        "formula": "V = m / r", "fact": "Объём = масса / плотность. 1 кг воды = 0,001 м³.", "zero": [1],
    },
    "Мощность тока (P)": {
        "fields": [("U", "Напряжение", "voltage"), ("I", "Сила тока", "current")],
        "calc": lambda vals: vals[0] * vals[1],
        "result_unit": "Вт", "result_key": None,
        "formula": "P = U × I", "fact": "Мощность тока = напряжение × сила тока. 220 В × 5 А = 1100 Вт.", "zero": None,
    },
    "Электроёмкость (C)": {
        "fields": [("q", "Заряд", None), ("U", "Напряжение", "voltage")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "Ф", "result_key": "capacitance",
        "formula": "C = q / U", "fact": "1 фарад — огромная ёмкость. Обычные конденсаторы — микрофарады.", "zero": [1],
    },
    "Магнитная индукция (B)": {
        "fields": [("F", "Сила", "force"), ("I", "Ток", "current")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "Тл", "result_key": "induction",
        "formula": "B = F / (I × l)", "fact": "Магнитная индукция Земли ~0,00005 Тл. У магнита — до 1 Тл.", "zero": [1],
    },    "Закон Кулона (F)": {
        "fields": [("q1", "Заряд 1", None), ("q2", "Заряд 2", "charge")],
        "calc": lambda vals: 9e9 * vals[0] * vals[1] / (1.0 * 1.0),
        "result_unit": "Н", "result_key": None,
        "formula": "F = k × q1 × q2 / r²",
        "fact": "k = 9×10^5 Н·м²/Кл². Сила между двумя зарядами по 1 Кл на расстоянии 1 м — 9 млрд Н.",
        "zero": None,
    },
    "Энергия вращения (E)": {
        "fields": [("I", "Момент инерции", None), ("ω", "Угл. скорость", None)],
        "calc": lambda vals: vals[0] * vals[1] * vals[1] / 2,
        "result_unit": "Дж", "result_key": "energy",
        "formula": "E = I × ω² / 2",
        "fact": "Кинетическая энергия вращения. Для диска I = m×r²/2.",
        "zero": None,
    },
    "Тонкая линза (f)": {
        "fields": [("d", "Расстояние до объекта", "distance"), ("F", "Фокус", "distance")],
        "calc": lambda vals: 1 / (1 / vals[0] + 1 / vals[1]) if vals[1] != 0 else 0,
        "result_unit": "м", "result_key": "distance",
        "formula": "1/f = 1/d + 1/F",
        "fact": "Формула тонкой линзы. Если объект ближе фокуса — изображение мнимое.",
        "zero": [0, 1],
    },
    "Скорость волны (v)": {
        "fields": [("λ", "Длина волны", "distance"), ("T", "Период", "time")],
        "calc": lambda vals: vals[0] / vals[1],
        "result_unit": "м/с", "result_key": "speed",
        "formula": "v = λ / T",
        "fact": "Скорость волны = длина волны / период. Звук 343 м/с при λ = 1 м → T = 0,003 с.",
        "zero": [1],
    },
}


TEXT = (1, 1, 1, 1)
SUBTEXT = (0.75, 0.75, 0.75, 1)
FACT = (0.6, 0.6, 0.65, 1)
ACCENT = (0.29, 0.56, 0.85, 1)
CARD_BG = (0.15, 0.2, 0.3, 1)
UNIT_BTN = (0.22, 0.22, 0.27, 1)


class PhysicsScreen(MDScreen):
    current_formula = StringProperty("Скорость (v)")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entries = []
        self.unit_values = []
        self.unit_keys = []
        self.history = []
        self.history_menu = None
        self._load_history()
        self._build_ui() 
        
    def _go_converter(self, *args):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "converter"
    def _load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.history = data[-10:]
        except Exception:
            self.history = []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _build_ui(self):
        scroll = MDScrollView()
        root = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))

        title_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(70), spacing=dp(4))
        title_box.add_widget(MDLabel(
            text="Калькулятор физики", font_style="H4", halign="center",
            theme_text_color="Custom", text_color=TEXT, bold=True, size_hint_y=None, height=dp(52),
        ))
        line = MDBoxLayout(size_hint=(0.35, None), height=dp(3), pos_hint={"center_x": 0.5}, md_bg_color=ACCENT)
        title_box.add_widget(line)
        root.add_widget(title_box)

        top = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(4))
        top.add_widget(MDLabel(size_hint_x=0.7))
        self.converter_btn = MDIconButton(
            icon="swap-horizontal", theme_text_color="Custom", text_color=TEXT,
            on_release=self._go_converter,
        )
        top.add_widget(self.converter_btn)
        self.history_btn = MDIconButton(
            icon="history", theme_text_color="Custom", text_color=TEXT, on_release=self._open_history,
        )
        top.add_widget(self.history_btn)
        root.add_widget(top)

        self.menu_btn = MDRaisedButton(
            text=self.current_formula, pos_hint={"center_x": 0.5}, size_hint=(1, None),
            height=dp(56), md_bg_color=ACCENT, font_size="16sp", on_release=self._open_menu,
        )
        root.add_widget(self.menu_btn)

        self.fields_box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(120))
        root.add_widget(self.fields_box)

        calc_btn = MDRaisedButton(
            text="Рассчитать", pos_hint={"center_x": 0.5}, size_hint=(0.85, None),
            height=dp(56), md_bg_color=ACCENT, font_size="16sp",
        )
        calc_btn.bind(on_release=self._on_calc_press)
        root.add_widget(calc_btn)

        self.result_card = MDCard(
            radius=[dp(22)] * 4, md_bg_color=CARD_BG, padding=dp(16),
            size_hint=(1, None), height=dp(170), opacity=0, elevation=2,
        )
        result_inner = MDBoxLayout(orientation="vertical", spacing=dp(6))
        self.result_label = MDLabel(text="Результат", font_style="H6", halign="center",
                                    theme_text_color="Custom", text_color=SUBTEXT,
                                    size_hint_y=None, height=dp(28))
        self.result_value = MDLabel(text="—", font_style="H3", halign="center",
                                    theme_text_color="Custom", text_color=ACCENT,
                                    size_hint_y=None, height=dp(56))
        self.formula_label = MDLabel(text="", halign="center", theme_text_color="Custom",
                                     text_color=SUBTEXT, size_hint_y=None, height=dp(24))
        self.fact_label = MDLabel(text="", halign="center", theme_text_color="Custom",
                                  text_color=FACT, size_hint_y=None, height=dp(52))
        result_inner.add_widget(self.result_value)
        result_inner.add_widget(self.formula_label)
        result_inner.add_widget(self.fact_label)
        self.result_card.add_widget(result_inner)
        root.add_widget(self.result_card)

        reset_btn = MDFlatButton(
            text="Очистить", pos_hint={"center_x": 0.5}, theme_text_color="Custom",
            text_color=SUBTEXT, font_size="16sp", size_hint=(0.6, None), height=dp(48),
        )
        reset_btn.bind(on_release=lambda x: self.clear_all())
        root.add_widget(reset_btn)

        scroll.add_widget(root)
        self.add_widget(scroll)

        self._update_fields("Скорость (v)")
        self._build_menu()

    def _build_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": name,
             "on_release": lambda x=name: self._select_formula(x)}
            for name in FORMULAS.keys()
        ]
        self.menu = MDDropdownMenu(caller=self.menu_btn, items=menu_items, width_mult=5)

    def _open_menu(self, *args):
        self.menu.open()

    def _select_formula(self, name):
        self.menu.dismiss()
        self.current_formula = name
        self.menu_btn.text = name
        self._update_fields(name)
        self._hide_result()

    def _update_fields(self, mode):
        self.fields_box.clear_widgets()
        formula = FORMULAS[mode]
        fields = formula["fields"]
        self.entries = []
        self.unit_values = []
        self.unit_keys = []

        row_height = dp(72)
        self.fields_box.height = row_height * len(fields) + dp(10) * (len(fields) - 1)

        for symbol, name, unit_key in fields:
            row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                              size_hint_y=None, height=row_height, opacity=0)
            row.add_widget(MDLabel(
                text=symbol, font_style="H5", theme_text_color="Custom",
                text_color=ACCENT, size_hint_x=None, width=dp(50), halign="center",
            ))
            entry = MDTextField(
                hint_text=name, mode="rectangle", size_hint_x=0.55,
                font_size="16sp", line_color_focus=ACCENT,
            )
            row.add_widget(entry)
            self.entries.append(entry)

            if unit_key is not None:
                default_unit = list(UNITS[unit_key].keys())[0]
                unit_btn = MDRaisedButton(
                    text=default_unit, size_hint_x=None, width=dp(80), height=dp(48),
                    md_bg_color=UNIT_BTN, font_size="15sp",
                )
                self.unit_values.append(default_unit)
                self.unit_keys.append(unit_key)
                row.add_widget(unit_btn)

                menu_ref = [None]
                def make_handler(u, b, i, mref):
                    def handler(*args):
                        self._select_unit(u, b, i, mref[0])
                    return handler
                unit_items = []
                for u in UNITS[unit_key].keys():
                    unit_items.append({
                        "viewclass": "OneLineListItem", "text": u,
                        "on_release": make_handler(u, unit_btn, len(self.unit_values) - 1, menu_ref),
                    })
                unit_menu = MDDropdownMenu(caller=unit_btn, items=unit_items, width_mult=3)
                menu_ref[0] = unit_menu
                unit_btn.bind(on_release=lambda x, m=unit_menu: m.open())
            else:
                self.unit_values.append(None)
                self.unit_keys.append(None)
                row.add_widget(MDLabel(size_hint_x=None, width=dp(80)))

            self.fields_box.add_widget(row)
            Animation(opacity=1, duration=0.25).start(row)

    def _select_unit(self, unit, btn, idx, menu=None):
        btn.text = unit
        if idx < len(self.unit_values):
            self.unit_values[idx] = unit
        if menu is not None:
            menu.dismiss()

    def _animate_press(self, button):
        try:
            anim = Animation(opacity=0.7, duration=0.08)
            anim.bind(on_complete=lambda *a: Animation(opacity=1, duration=0.12).start(button))
            anim.start(button)
        except Exception:
            pass

    def _on_calc_press(self, button):
        self._animate_press(button)
        self.calculate()

    def _show_result_animated(self):
        try:
            self.result_card.opacity = 0
            Animation(opacity=1, duration=0.35).start(self.result_card)
        except Exception:
            self.result_card.opacity = 1

    def _hide_result(self):
        try:
            Animation(opacity=0, duration=0.25).start(self.result_card)
        except Exception:
            self.result_card.opacity = 0

    def calculate(self):
        mode = self.current_formula
        formula = FORMULAS[mode]
        values_si = []
        raw_inputs = []
        try:
            for i, entry in enumerate(self.entries):
                val = float(entry.text)
                key = self.unit_keys[i]
                unit = self.unit_values[i]
                coef = UNITS[key][unit] if key else 1.0
                values_si.append(val * coef)
                raw_inputs.append((entry.text, unit if unit else ""))
        except ValueError:
            self._show_error("Введите числа во все поля!")
            return
        zero_indices = formula.get("zero")
        if zero_indices:
            for idx in zero_indices:
                if values_si[idx] == 0:
                    self._show_error("Делитель не может быть 0!")
                    return
        result_si = formula["calc"](values_si)
        result_unit = formula["result_unit"]
        result_value = result_si

        if formula["result_key"] == "speed" and len(values_si) == 2:
            if self.unit_keys[0] == "distance" and self.unit_values[0] == "км" and self.unit_values[1] == "ч":
                result_value = result_si * 3.6
                result_unit = "км/ч"
        elif formula["result_key"] == "distance" and len(values_si) == 2:
            if self.unit_keys[0] == "speed" and self.unit_values[0] == "км/ч" and self.unit_values[1] == "ч":
                result_value = result_si / 1000
                result_unit = "км"
        elif formula["result_key"] == "time" and len(values_si) == 2:
            if (self.unit_keys[0] == "distance" and self.unit_values[0] == "км"
                    and self.unit_keys[1] == "speed" and self.unit_values[1] == "км/ч"):
                result_value = result_si / 3600
                result_unit = "ч"

        self.result_label.text = mode.split("(")[0].strip()
        self.result_value.text = f"{result_value:.2f} {result_unit}"
        self.formula_label.text = f"Формула: {formula['formula']}"
        self.fact_label.text = formula["fact"]
        self.result_value.text_color = ACCENT

        self.history.append({"formula": mode, "inputs": raw_inputs,
                             "result": f"{result_value:.2f} {result_unit}"})
        if len(self.history) > 10:
            self.history = self.history[-10:]
        self._save_history()
        self._show_result_animated()

    def _show_error(self, msg):
        self.result_label.text = "Ошибка"
        self.result_value.text = msg
        self.formula_label.text = ""
        self.fact_label.text = ""
        self.result_value.text_color = (1, 0.3, 0.3, 1)
        self._show_result_animated()

    def clear_all(self):
        for entry in self.entries:
            entry.text = ""
        self._hide_result()

    def _open_history(self, *args):
        if self.history_menu:
            try:
                self.history_menu.dismiss()
            except Exception:
                pass
        if not self.history:
            items = [{"viewclass": "OneLineListItem", "text": "История пуста", "on_release": lambda: None}]
        else:
            items = []
            for idx, record in enumerate(reversed(self.history)):
                short = record["formula"].split("(")[0].strip()
                text = f"{short}: {record['result']}"
                real_idx = len(self.history) - 1 - idx
                items.append({"viewclass": "OneLineListItem", "text": text,
                              "on_release": (lambda i=real_idx: self._restore_from_history(i))})
        self.history_menu = MDDropdownMenu(caller=self.history_btn, items=items, width_mult=6)
        self.history_menu.open()

    def _restore_from_history(self, index):
        if self.history_menu:
            try:
                self.history_menu.dismiss()
            except Exception:
                pass
        if index < 0 or index >= len(self.history):
            return
        record = self.history[index]
        mode = record["formula"]
        if mode != self.current_formula:
            self.current_formula = mode
            self.menu_btn.text = mode
            self._update_fields(mode)
        inputs = record["inputs"]
        for i, entry in enumerate(self.entries):
            if i < len(inputs):
                text_val, unit_val = inputs[i]
                entry.text = text_val
                if i < len(self.unit_values) and self.unit_values[i] != unit_val and unit_val:
                    self.unit_values[i] = unit_val
        self._show_result_animated()
class ConverterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_category_name = "Длина"
        self.from_unit = "м"
        self.to_unit = "км"
        self.category_menu = None
        self.from_menu = None
        self.to_menu = None
        self._build_ui()
    def _go_back(self, *args):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "calculator"
    def _build_ui(self):
        scroll = MDScrollView()
        root = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))

        title_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(70), spacing=dp(4))
        title_box.add_widget(MDLabel(
            text="Конвертер единиц", font_style="H4", halign="center",
            theme_text_color="Custom", text_color=TEXT, bold=True,
            size_hint_y=None, height=dp(52),
        ))
        line = MDBoxLayout(size_hint=(0.35, None), height=dp(3),
                           pos_hint={"center_x": 0.5}, md_bg_color=ACCENT)
        title_box.add_widget(line)
        root.add_widget(title_box)

        back_btn = MDFlatButton(
            text="<Назад", theme_text_color="Custom", text_color=ACCENT,
            font_size="18sp", size_hint=(0.4, None), height=dp(44),
            pos_hint={"center_x": 0.5},
        )
        back_btn.bind(on_release=self._go_back)
        root.add_widget(back_btn)

        self.category_btn = MDRaisedButton(
            text="Длина", pos_hint={"center_x": 0.5}, size_hint=(1, None),
            height=dp(56), md_bg_color=ACCENT, font_size="16sp",
        )
        self.category_btn.bind(on_release=lambda x: self.category_menu.open())
        root.add_widget(self.category_btn)
        self._build_category_menu()

        self.value_input = MDTextField(
            hint_text="Значение (например, 20)", mode="rectangle",
            font_size="18sp", size_hint_y=None, height=dp(64),
            line_color_focus=ACCENT,
        )
        root.add_widget(self.value_input)

        units_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(8))
        self.from_btn = MDRaisedButton(
            text="м", size_hint=(0.48, None), height=dp(56),
            md_bg_color=UNIT_BTN, font_size="16sp",
        )
        self.from_btn.bind(on_release=lambda x: self.from_menu.open())
        units_row.add_widget(self.from_btn)

        units_row.add_widget(MDLabel(
            text=">", halign="center", theme_text_color="Custom",
            text_color=ACCENT, font_style="H5", size_hint_x=None, width=dp(40),
        ))

        self.to_btn = MDRaisedButton(
            text="км", size_hint=(0.48, None), height=dp(56),
            md_bg_color=UNIT_BTN, font_size="16sp",
        )
        self.to_btn.bind(on_release=lambda x: self.to_menu.open())
        units_row.add_widget(self.to_btn)
        root.add_widget(units_row)

        self._build_from_menu()
        self._build_to_menu()

        convert_btn = MDRaisedButton(
            text="Перевести", pos_hint={"center_x": 0.5}, size_hint=(0.85, None),
            height=dp(56), md_bg_color=ACCENT, font_size="16sp",
        )
        convert_btn.bind(on_release=self._do_convert)
        root.add_widget(convert_btn)

        self.convert_result_card = MDCard(
            radius=[dp(22)] * 4, md_bg_color=CARD_BG, padding=dp(16),
            size_hint=(1, None), height=dp(130), opacity=0, elevation=2,
        )
        result_inner = MDBoxLayout(orientation="vertical", spacing=dp(6))
        self.convert_result_label = MDLabel(
            text="Результат", font_style="H6", halign="center",
            theme_text_color="Custom", text_color=SUBTEXT,
            size_hint_y=None, height=dp(28),
        )
        self.convert_result_value = MDLabel(
            text="—", font_style="H3", halign="center",
            theme_text_color="Custom", text_color=ACCENT,
            size_hint_y=None, height=dp(56),
        )
        result_inner.add_widget(self.convert_result_label)
        result_inner.add_widget(self.convert_result_value)
        self.convert_result_card.add_widget(result_inner)
        root.add_widget(self.convert_result_card)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def _build_category_menu(self):
        items = [{"viewclass": "OneLineListItem", "text": name,
                  "on_release": (lambda x=name: self._select_category(x))}
                 for name in CONVERT_CATEGORIES.keys()]
        self.category_menu = MDDropdownMenu(
            caller=self.category_btn, items=items, width_mult=5,
        )

    def _select_category(self, name):
        self.category_menu.dismiss()
        self.current_category_name = name
        self.category_btn.text = name

        key = CONVERT_CATEGORIES[name]
        units = list(UNITS[key].keys())
        self.from_unit = units[0]
        self.to_unit = units[1] if len(units) > 1 else units[0]
        self.from_btn.text = self.from_unit
        self.to_btn.text = self.to_unit

        self._build_from_menu()
        self._build_to_menu()

    def _build_from_menu(self):
        key = CONVERT_CATEGORIES[self.current_category_name]
        items = [{"viewclass": "OneLineListItem", "text": u,
                  "on_release": (lambda x=u: self._select_from(x))}
                 for u in UNITS[key].keys()]
        self.from_menu = MDDropdownMenu(caller=self.from_btn, items=items, width_mult=3)

    def _build_to_menu(self):
        key = CONVERT_CATEGORIES[self.current_category_name]
        items = [{"viewclass": "OneLineListItem", "text": u,
                  "on_release": (lambda x=u: self._select_to(x))}
                 for u in UNITS[key].keys()]
        self.to_menu = MDDropdownMenu(caller=self.to_btn, items=items, width_mult=3)

    def _select_from(self, unit):
        self.from_menu.dismiss()
        self.from_unit = unit
        self.from_btn.text = unit

    def _select_to(self, unit):
        self.to_menu.dismiss()
        self.to_unit = unit
        self.to_btn.text = unit

    def _do_convert(self, *args):
        try:
            value = float(self.value_input.text)
        except ValueError:
            self.convert_result_label.text = "Ошибка"
            self.convert_result_value.text = "Введите число!"
            self.convert_result_value.text_color = (1, 0.3, 0.3, 1)
            self._show_convert_result()
            return

        key = CONVERT_CATEGORIES[self.current_category_name]
        units = UNITS[key]
        si_value = value * units[self.from_unit]
        result = si_value / units[self.to_unit]

        self.convert_result_label.text = f"{value:g} {self.from_unit} ="
        self.convert_result_value.text = f"{result:.4g} {self.to_unit}"
        self.convert_result_value.text_color = ACCENT
        self._show_convert_result()

    def _show_convert_result(self):
        try:
            self.convert_result_card.opacity = 0
            Animation(opacity=1, duration=0.35).start(self.convert_result_card)
        except Exception:
            self.convert_result_card.opacity = 1


class PhysicsApp(MDApp):
    title = "Калькулятор физики"

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "400"
        Window.softinput_mode = "below_target"

        sm = ScreenManager()
        sm.add_widget(PhysicsScreen(name="calculator"))
        sm.add_widget(ConverterScreen(name="converter"))
        return sm


if __name__ == "__main__":
    PhysicsApp().run()