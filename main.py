import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def round_up_50_meters(value):
    return math.ceil(value / 50) * 50

def round_up_100_feet(value_meters):
    feet = value_meters * 3.28084
    return math.ceil(feet / 100) * 100

def linear_interpolate(x, x0, x1, y0, y1):
    if x0 == x1:
        return y0
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def bilinear_interpolate(x, y, x_vals, y_vals, grid):
    # ... (функция билинейной интерполяции, уже есть в предыдущих кодах)
    # Для краткости пропущена, но должна быть здесь
    pass

# ========== ДИАПАЗОНЫ ==========
mass_vals = [200, 210, 220, 230, 240, 250, 260, 270, 280, 290,
             300, 310, 320, 330, 340, 350, 360, 370, 380, 390]
temp_vals_norm_cont = [-60, -50, -40, -30, -20, -10, 0, 5, 10, 15, 20, 25, 30, 35, 40]
temp_vals_abort = [-40, -30, -20, -10, 0, 5, 10, 15, 20, 25, 30, 35, 40]
alt_vals_takeoff = [0, 250, 500, 750, 1000, 1500, 2000, 2500]

# ========== ТАБЛИЦЫ ==========
# Здесь должны быть все таблицы norm_tables, cont_tables, abort_tables из предыдущего финального кода.
# Из-за ограничения длины я их не привожу, но они обязательны.

# ========== ПОПРАВОЧНЫЕ ТАБЛИЦЫ ==========
mass_vals_corr = [200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350]

wind_vals = [-15,-10,-5,0,5,10,15]
wind_table = [
    [1559,1713,1866,2020,2173,2326,2479,2632,2785,2938,3092,3245,3398,3551,3704,3857],
    [1373,1508,1644,1780,1915,2051,2186,2322,2457,2593,2728,2864,2999,3135,3270,3406],
    [1186,1304,1422,1540,1658,1776,1894,2012,2130,2248,2366,2484,2602,2720,2838,2956],
    [1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500],
    [ 949,1049,1149,1249,1349,1450,1542,1635,1727,1820,1913,2005,2098,2191,2284,2377],
    [ 899, 999,1098,1198,1299,1400,1485,1570,1656,1741,1826,1912,1997,2083,2169,2255],
    [ 849, 948,1047,1147,1248,1350,1428,1506,1584,1662,1740,1818,1896,1975,2054,2133]
]

slope_vals = [-2.0,-1.75,-1.5,-1.25,-1.0,-0.75,-0.5,-0.25,0.0]
slope_table = [
    [ 938,1006,1100,1191,1292,1393,1490,1567,1670,1750,1850,1913,1992,2096,2160,2250],
    [ 945,1018,1113,1204,1305,1406,1503,1580,1683,1765,1864,1933,2016,2119,2188,2278],
    [ 952,1029,1125,1216,1317,1418,1515,1592,1695,1780,1878,1952,2040,2143,2215,2305],
    [ 959,1041,1138,1229,1330,1431,1528,1605,1708,1795,1892,1972,2064,2167,2243,2333],
    [ 966,1052,1150,1241,1342,1443,1540,1617,1720,1810,1905,1991,2088,2190,2270,2360],
    [ 974,1065,1163,1255,1357,1458,1555,1638,1740,1833,1929,2019,2116,2218,2303,2395],
    [ 981,1077,1176,1269,1373,1476,1575,1660,1762,1856,1954,2047,2145,2249,2337,2432],
    [ 988,1088,1188,1284,1390,1495,1595,1682,1785,1880,1979,2075,2174,2280,2370,2468],
    [ 995,1100,1200,1300,1406,1513,1615,1704,1808,1904,2005,2104,2204,2312,2404,2504]
]

v1_vals = [0.70,0.75,0.80,0.85,0.90,0.95,1.00]
v1_table = [
    [1142,1272,1402,1532,1663,1794,1926,2059,2191,2324,2456,2588,2721,2853,2986,3118],
    [1111,1238,1364,1491,1618,1746,1874,2002,2131,2257,2387,2516,2644,2772,2901,3030],
    [1083,1206,1328,1451,1574,1697,1821,1945,2069,2192,2316,2440,2563,2687,2811,2936],
    [1058,1176,1294,1412,1530,1648,1767,1886,2004,2123,2242,2360,2479,2597,2716,2835],
    [1036,1148,1261,1374,1486,1599,1712,1825,1938,2051,2164,2277,2390,2503,2616,2729],
    [1016,1123,1230,1336,1443,1550,1657,1763,1870,1977,2084,2190,2297,2404,2511,2618],
    [1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500]
]

# ========== ФУНКЦИИ РАСЧЁТА ==========
def get_base_length(mass, temp, alt, table_dict, temp_vals):
    # ... (функция должна быть определена)
    return 1000  # заглушка

def get_factor_from_table(mass, x, x_vals, table, table_mass_vals):
    # ... (заглушка)
    return 1.0

def calculate_takeoff(mass, temp, alt, wind, slope, v1, calc_type):
    # заглушка, потом заменим на реальную
    return mass + temp + alt + wind + slope

# ========== ЭКРАНЫ ==========

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        layout.add_widget(Label(text='Главное меню', font_size=sp(28), bold=True, size_hint_y=0.3))
        btn_start = Button(text='Взлётные характеристики', font_size=sp(22), size_hint_y=0.2)
        btn_start.bind(on_press=lambda x: setattr(self.manager, 'current', 'input'))
        layout.add_widget(btn_start)
        self.add_widget(layout)

class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = {}

        root = ScrollView()
        main = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint_y=None)
        main.bind(minimum_height=main.setter('height'))

        # Заголовок
        main.add_widget(Label(text='Введите параметры', font_size=sp(24), bold=True, size_hint_y=None, height=dp(60)))

        # Поля ввода
        grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(15), padding=dp(10))
        grid.bind(minimum_height=grid.setter('height'))

        fields = [
            ('mass', 'Масса (т):'),
            ('temp', 'Температура (°C):'),
            ('alt', 'Высота аэродрома (м):'),
            ('wind', 'Ветер (м/с):'),
            ('slope', 'Уклон ВПП (%):'),
            ('v1', 'V1/Vn.on:'),
        ]
        for key, label in fields:
            grid.add_widget(Label(
                text=label,
                halign='right',
                size_hint_x=0.4,
                font_size=sp(18),
                size_hint_y=None,
                height=dp(50)
            ))
            ti = TextInput(
                text='1.0' if key == 'v1' else '',
                multiline=False,
                input_filter='float',
                font_size=sp(18),
                size_hint_y=None,
                height=dp(50)
            )
            self.inputs[key] = ti
            grid.add_widget(ti)

        main.add_widget(grid)

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(20))
        btn_calc = Button(text='Рассчитать', font_size=sp(20))
        btn_back = Button(text='Назад', font_size=sp(20))
        btn_layout.add_widget(btn_calc)
        btn_layout.add_widget(btn_back)
        main.add_widget(btn_layout)

        btn_calc.bind(on_press=self.calculate)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))

        root.add_widget(main)
        self.add_widget(root)

    def calculate(self, instance):
        try:
            mass = float(self.inputs['mass'].text.replace(',', '.'))
            temp = float(self.inputs['temp'].text.replace(',', '.'))
            alt = float(self.inputs['alt'].text.replace(',', '.'))
            wind = float(self.inputs['wind'].text.replace(',', '.'))
            slope = float(self.inputs['slope'].text.replace(',', '.'))
            v1 = float(self.inputs['v1'].text.replace(',', '.'))
        except ValueError:
            self.show_popup('Ошибка', 'Введите все числовые значения')
            return

        # Здесь будут реальные расчёты
        norm = 1000 + mass * 0.1
        cont = 1200 + mass * 0.1
        abort = 1400 + mass * 0.1

        msg = (f"НОРМАЛЬНЫЙ: {norm:.1f} м\n"
               f"ПРОДОЛЖЕННЫЙ: {cont:.1f} м\n"
               f"ПРЕРВАННЫЙ: {abort:.1f} м")
        self.show_popup('Результаты', msg)

    def show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=text, font_size=sp(16)))
        btn = Button(text='Закрыть', size_hint_y=None, height=dp(50))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8,0.5))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class TakeoffApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(InputScreen(name='input'))
        return sm

if __name__ == '__main__':
    TakeoffApp().run()
