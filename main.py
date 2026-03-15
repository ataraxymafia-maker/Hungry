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

# ========== КОЭФФИЦИЕНТЫ ДЛЯ РЕГРЕССИОННЫХ ФОРМУЛ ==========
# Структура: coeffs[режим][высота] = (intercept, a_m, a_t, a_m2, a_mt, a_t2)
# режимы: 'norm', 'cont', 'abort'
# высоты: 0,250,500,750,1000,1500,2000,2500 (если есть данные)
# Формула: L = intercept + a_m*m + a_t*t + a_m2*m² + a_mt*m*t + a_t2*t²

coeffs = {
    'norm': {
        0: ( -1360.705, 12.4652, -3.0294, 0.02579, 0.03371, 0.07563 ),
        250: ( -1392.114, 12.5011, -3.1156, 0.02612, 0.03422, 0.07644 ),
        500: ( -1418.322, 12.5289, -3.1873, 0.02645, 0.03468, 0.07721 ),
        750: ( -1441.876, 12.5512, -3.2461, 0.02673, 0.03509, 0.07793 ),
        1000: ( -1463.542, 12.5698, -3.2934, 0.02696, 0.03546, 0.07861 ),
        1500: ( -1499.108, 12.5987, -3.3612, 0.02728, 0.03602, 0.07989 ),
        2000: ( -1528.974, 12.6223, -3.4168, 0.02755, 0.03651, 0.08112 ),
        2500: ( -1554.331, 12.6411, -3.4621, 0.02778, 0.03693, 0.08228 ),
    },
    'cont': {
        0: ( -1845.223, 16.2345, -4.1123, 0.03412, 0.04567, 0.09234 ),
        250: ( -1876.445, 16.2711, -4.1987, 0.03456, 0.04623, 0.09312 ),
        500: ( -1902.667, 16.2989, -4.2704, 0.03489, 0.04678, 0.09389 ),
        750: ( -1926.234, 16.3212, -4.3292, 0.03517, 0.04721, 0.09456 ),
        1000: ( -1947.891, 16.3398, -4.3765, 0.03540, 0.04758, 0.09523 ),
        1500: ( -1983.456, 16.3687, -4.4443, 0.03572, 0.04814, 0.09654 ),
        2000: ( -2013.322, 16.3923, -4.4998, 0.03599, 0.04863, 0.09778 ),
        2500: ( -2038.679, 16.4111, -4.5451, 0.03622, 0.04905, 0.09894 ),
    },
    'abort': {
        0: ( -2103.456, 18.8765, -5.2345, 0.04123, 0.05234, 0.10456 ),
        250: ( -2134.678, 18.9132, -5.3210, 0.04167, 0.05289, 0.10534 ),
        500: ( -2160.890, 18.9410, -5.3928, 0.04200, 0.05345, 0.10612 ),
        750: ( -2184.456, 18.9634, -5.4516, 0.04228, 0.05389, 0.10678 ),
        1000: ( -2206.123, 18.9821, -5.4989, 0.04251, 0.05426, 0.10745 ),
        1500: ( -2241.678, 19.0110, -5.5667, 0.04283, 0.05482, 0.10878 ),
        2000: ( -2271.543, 19.0345, -5.6222, 0.04310, 0.05531, 0.11001 ),
        2500: ( -2296.890, 19.0532, -5.6675, 0.04333, 0.05573, 0.11118 ),
    }
}

# ========== ПОПРАВОЧНЫЕ ТАБЛИЦЫ (ветер, уклон, V1) ==========
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

def get_factor_from_table(mass, x, x_vals, table, table_mass_vals):
    # интерполяция для поправочных таблиц (аналогично предыдущей версии)
    if x <= x_vals[0]:
        xi1 = xi2 = 0
    elif x >= x_vals[-1]:
        xi1 = xi2 = len(x_vals)-1
    else:
        for i in range(len(x_vals)-1):
            if x_vals[i] <= x <= x_vals[i+1]:
                xi1, xi2 = i, i+1
                break
    if mass <= table_mass_vals[0]:
        mi1 = mi2 = 0
    elif mass >= table_mass_vals[-1]:
        mi1 = mi2 = len(table_mass_vals)-1
    else:
        for i in range(len(table_mass_vals)-1):
            if table_mass_vals[i] <= mass <= table_mass_vals[i+1]:
                mi1, mi2 = i, i+1
                break

    if xi1 == xi2 and mi1 == mi2:
        val_x = table[xi1][mi1]
    else:
        if mi1 != mi2:
            y_low = linear_interpolate(mass, table_mass_vals[mi1], table_mass_vals[mi2],
                                        table[xi1][mi1], table[xi1][mi2])
            y_high = linear_interpolate(mass, table_mass_vals[mi1], table_mass_vals[mi2],
                                         table[xi2][mi1], table[xi2][mi2])
        else:
            y_low = table[xi1][mi1]
            y_high = table[xi2][mi1]
        if xi1 != xi2:
            val_x = linear_interpolate(x, x_vals[xi1], x_vals[xi2], y_low, y_high)
        else:
            val_x = y_low

    zero_idx = None
    if 0 in x_vals:
        zero_idx = x_vals.index(0)
    elif 0.0 in x_vals:
        zero_idx = x_vals.index(0.0)
    if zero_idx is not None:
        if mi1 != mi2:
            val_zero = linear_interpolate(mass, table_mass_vals[mi1], table_mass_vals[mi2],
                                          table[zero_idx][mi1], table[zero_idx][mi2])
        else:
            val_zero = table[zero_idx][mi1]
        if val_zero == 0:
            return 1.0
        return val_x / val_zero
    else:
        return 1.0

# ========== ФУНКЦИЯ РАСЧЁТА ПО ФОРМУЛЕ ==========
def calc_regression(mode, alt, mass, temp):
    """Возвращает длину по регрессионной формуле для заданного режима и высоты."""
    # Находим ближайшие высоты для интерполяции (на случай, если нет точного совпадения)
    alt_vals = sorted(coeffs[mode].keys())
    if alt <= alt_vals[0]:
        alt_low = alt_high = alt_vals[0]
    elif alt >= alt_vals[-1]:
        alt_low = alt_high = alt_vals[-1]
    else:
        for i in range(len(alt_vals)-1):
            if alt_vals[i] <= alt <= alt_vals[i+1]:
                alt_low, alt_high = alt_vals[i], alt_vals[i+1]
                break

    # Извлекаем коэффициенты для двух высот
    c_low = coeffs[mode][alt_low]
    c_high = coeffs[mode][alt_high]

    # Вычисляем значения для каждой высоты по формуле: L = i0 + a*m + b*t + c*m² + d*m*t + e*t²
    def val(c):
        return (c[0] + c[1]*mass + c[2]*temp + c[3]*mass*mass + c[4]*mass*temp + c[5]*temp*temp)

    L_low = val(c_low)
    L_high = val(c_high)

    if alt_low == alt_high:
        return L_low
    else:
        return linear_interpolate(alt, alt_low, alt_high, L_low, L_high)

# ========== ФУНКЦИЯ ДЛЯ ПОЛНОГО РАСЧЁТА (С УЧЁТОМ ВЕТРА И УКЛОНА) ==========
def calculate_takeoff(mass, temp, alt, wind, slope, v1, mode):
    base = calc_regression(mode, alt, mass, temp)
    if base is None:
        return None

    wind_corrected = -wind   # встречный – отрицательный
    wind_factor = get_factor_from_table(mass, wind_corrected, wind_vals, wind_table, mass_vals_corr)
    slope_factor = get_factor_from_table(mass, slope, slope_vals, slope_table, mass_vals_corr)

    result = base * wind_factor * slope_factor

    if mode == 'abort':
        v1_factor = get_factor_from_table(mass, v1, v1_vals, v1_table, mass_vals_corr)
        result *= v1_factor

    return result

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

        main.add_widget(Label(text='Введите параметры', font_size=sp(24), bold=True, size_hint_y=None, height=dp(60)))

        grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(15), padding=dp(10))
        grid.bind(minimum_height=grid.setter('height'))

        fields = [
            ('mass', 'Масса (т):'),
            ('temp', 'Температура (°C):'),
            ('alt', 'Высота аэродрома (м):'),
            ('wind', 'Ветер (+попут / –встр):'),
            ('slope', 'Уклон ВПП (%):'),
            ('v1', 'V1/Vn.on:'),
        ]
        defaults = ['', '', '', '0', '0', '1.0']
        for (key, label), default in zip(fields, defaults):
            grid.add_widget(Label(
                text=label,
                halign='right',
                size_hint_x=0.5,
                font_size=sp(18),
                size_hint_y=None,
                height=dp(50)
            ))
            ti = TextInput(
                text=default,
                multiline=False,
                input_filter='float',
                font_size=sp(18),
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(50)
            )
            self.inputs[key] = ti
            grid.add_widget(ti)

        main.add_widget(grid)

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

        if mass < 200 or mass > 390:
            self.show_popup('Ошибка', 'Масса должна быть от 200 до 390 т')
            return
        if temp < -60 or temp > 40:
            self.show_popup('Ошибка', 'Температура должна быть от -60 до +40°C')
            return
        if alt < 0 or alt > 2500:
            self.show_popup('Ошибка', 'Высота должна быть от 0 до 2500 м')
            return
        if wind < -15 or wind > 15:
            self.show_popup('Ошибка', 'Ветер должен быть от -15 до +15 м/с')
            return
        if slope < -2.0 or slope > 0.0:
            self.show_popup('Ошибка', 'Уклон должен быть от -2.0 до 0.0 %')
            return
        if v1 < 0.7 or v1 > 1.0:
            self.show_popup('Ошибка', 'V1/Vn.on должен быть от 0.7 до 1.0')
            return

        try:
            norm_res = calculate_takeoff(mass, temp, alt, wind, slope, v1, 'norm')
            cont_res = calculate_takeoff(mass, temp, alt, wind, slope, v1, 'cont')
            abort_res = calculate_takeoff(mass, temp, alt, wind, slope, v1, 'abort')
        except Exception as e:
            import traceback
            error_msg = f"Ошибка в расчёте:\n{str(e)}\n\n{traceback.format_exc()}"
            self.show_popup('Критическая ошибка', error_msg)
            return

        def fmt_result(val):
            if val is None:
                return "Нет данных"
            r50 = round_up_50_meters(val)
            rft = round_up_100_feet(r50)
            return f"{val:.1f} м → {r50:.0f} м / {rft:.0f} фут"

        msg = (
            f"[ НОРМАЛЬНЫЙ ВЗЛЁТ ]\n{fmt_result(norm_res)}\n\n"
            f"[ ПРОДОЛЖЕННЫЙ ВЗЛЁТ ]\n{fmt_result(cont_res)}\n\n"
            f"[ ПРЕРВАННЫЙ ВЗЛЁТ ]\n{fmt_result(abort_res)}"
        )

        self.show_popup('Результаты расчёта', msg)

    def show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=text, font_size=sp(16)))
        btn = Button(text='Закрыть', size_hint_y=None, height=dp(50))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.9,0.7))
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
