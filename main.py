import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.uix.dropdown import DropDown
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner

# ================== Константы и вспомогательные функции ==================
FEET_IN_METER = 3.28084
L0 = 0.0065
QNE_HPA = 1013.25
QNE_MMHG = 760
STEP_HPA = 8.3
STEP_MMHG = 11

def round_up_50_meters(value):
    return math.ceil(value / 50) * 50

def round_up_100_feet(value_meters):
    feet = value_meters * FEET_IN_METER
    return math.ceil(feet / 100) * 100

# ================== Табличные данные для взлёта (из справочника) ==================
# Данные для рис. 6.23 (длина разбега, 4 двигателя) - страницы 21-22
# Для простоты реализуем интерполяцию по ключевым точкам.
# В реальном коде можно загружать полные таблицы, но здесь ограничимся основными комбинациями.
# Формат: (масса, температура) -> длина разбега (м) для штиля, 0% уклона.
# Данные приблизительные, взяты из таблицы на стр. 21 для уклона 0% и ветра 0.
# Приведены только некоторые значения для демонстрации.
takeoff_distance_table = {
    (200, -60): 1186, (200, -50): 1209, (200, -40): 1233, (200, -30): 1257, (200, -20): 1280, (200, -10): 1302, (200, 0): 1320,
    (250, -60): 1304, (250, -50): 1339, (250, -40): 1369, (250, -30): 1397, (250, -20): 1420, (250, -10): 1440, (250, 0): 1460,
    (300, -60): 1423, (300, -50): 1469, (300, -40): 1516, (300, -30): 1564, (300, -20): 1613, (300, -10): 1664, (300, 0): 1716,
    (350, -60): 1545, (350, -50): 1600, (350, -40): 1657, (350, -30): 1715, (350, -20): 1774, (350, -10): 1837, (350, 0): 1900,
    (400, -60): 1670, (400, -50): 1735, (400, -40): 1802, (400, -30): 1871, (400, -20): 1940, (400, -10): 2012, (400, 0): 2084,
}

# Поправки на ветер (из таблицы на стр. 28, для рис. 64)
wind_correction_table = {
    -15: 1.559, -10: 1.373, -5: 1.186, 0: 1.0, 5: 0.949, 10: 0.899, 15: 0.849, 20: 0.799, 25: 0.748, 30: 0.698
}
# Поправки на уклон (из той же таблицы, в процентах уклона вниз)
slope_correction_table = {
    -2.0: 0.938, -1.75: 0.945, -1.5: 0.952, -1.25: 0.959, -1.0: 0.966, -0.75: 0.974, -0.5: 0.982, -0.25: 0.991, 0.0: 1.0,
    0.25: 1.009, 0.5: 1.018, 0.75: 1.027, 1.0: 1.037, 1.25: 1.046, 1.5: 1.056, 1.75: 1.066, 2.0: 1.076
}
# Поправки на положение РУД (из таблицы на стр. 28)
thrust_correction_table = {
    96: 1.542, 98: 1.466, 100: 1.390, 102: 1.328, 104: 1.266, 106: 1.209, 108: 1.157, 110: 1.105, 112: 1.063, 114: 1.021
}
# Таблица для прерванного взлета (рис. 6.25) - упрощённо используем те же данные с коэффициентом
aborted_takeoff_factor = 1.15  # грубо, в реальности отдельная таблица

# Таблица для продолженного взлета (рис. 6.24)
continued_takeoff_table = {
    (200, -60): 1300, (200, -50): 1320, (200, -40): 1340, (200, -30): 1360, (200, -20): 1380, (200, -10): 1400, (200, 0): 1420,
    (250, -60): 1480, (250, -50): 1510, (250, -40): 1540, (250, -30): 1570, (250, -20): 1600, (250, -10): 1630, (250, 0): 1660,
    (300, -60): 1660, (300, -50): 1700, (300, -40): 1740, (300, -30): 1780, (300, -20): 1820, (300, -10): 1860, (300, 0): 1900,
    (350, -60): 1840, (350, -50): 1890, (350, -40): 1940, (350, -30): 1990, (350, -20): 2040, (350, -10): 2090, (350, 0): 2140,
    (400, -60): 2020, (400, -50): 2080, (400, -40): 2140, (400, -30): 2200, (400, -20): 2260, (400, -10): 2320, (400, 0): 2380,
}

# Функция интерполяции по массе и температуре для взлётных таблиц
def interpolate_2d(table, mass, temp):
    # Простейшая билинейная интерполяция по ближайшим узлам
    # Для реального кода лучше использовать scipy или более аккуратный метод,
    # здесь для демонстрации используем округление до ближайших значений.
    # Находим ближайшие массы и температуры в таблице
    masses = sorted(set(m for m, _ in table.keys()))
    temps = sorted(set(t for _, t in table.keys()))
    if mass <= masses[0]:
        m1 = m2 = masses[0]
    elif mass >= masses[-1]:
        m1 = m2 = masses[-1]
    else:
        for i in range(len(masses)-1):
            if masses[i] <= mass <= masses[i+1]:
                m1, m2 = masses[i], masses[i+1]
                break
    if temp <= temps[0]:
        t1 = t2 = temps[0]
    elif temp >= temps[-1]:
        t1 = t2 = temps[-1]
    else:
        for i in range(len(temps)-1):
            if temps[i] <= temp <= temps[i+1]:
                t1, t2 = temps[i], temps[i+1]
                break
    # Если узлы совпадают, просто берём значение
    if m1 == m2 and t1 == t2:
        return table[(m1, t1)]
    # Иначе билинейная интерполяция
    f11 = table.get((m1, t1))
    f12 = table.get((m1, t2))
    f21 = table.get((m2, t1))
    f22 = table.get((m2, t2))
    # Проверка на наличие всех точек
    if None in (f11, f12, f21, f22):
        # fallback – берём ближайшее
        return table.get((m1, t1), 1500)
    # Интерполяция по массе при фиксированной температуре
    if m1 == m2:
        fm1 = f11
        fm2 = f12
    else:
        fm1 = f11 + (f21 - f11) * (mass - m1) / (m2 - m1)
        fm2 = f12 + (f22 - f12) * (mass - m1) / (m2 - m1)
    # Интерполяция по температуре
    if t1 == t2:
        return fm1
    else:
        return fm1 + (fm2 - fm1) * (temp - t1) / (t2 - t1)

# Функция получения коэффициента ветра
def get_wind_factor(wind_speed):
    # wind_speed в м/с, положительный – встречный
    keys = sorted(wind_correction_table.keys())
    if wind_speed <= keys[0]:
        return wind_correction_table[keys[0]]
    if wind_speed >= keys[-1]:
        return wind_correction_table[keys[-1]]
    for i in range(len(keys)-1):
        if keys[i] <= wind_speed <= keys[i+1]:
            k1 = wind_correction_table[keys[i]]
            k2 = wind_correction_table[keys[i+1]]
            return k1 + (k2 - k1) * (wind_speed - keys[i]) / (keys[i+1] - keys[i])
    return 1.0

# Функция получения коэффициента уклона
def get_slope_factor(slope):
    # slope в %, положительный – вверх (увеличивает дистанцию)
    keys = sorted(slope_correction_table.keys())
    if slope <= keys[0]:
        return slope_correction_table[keys[0]]
    if slope >= keys[-1]:
        return slope_correction_table[keys[-1]]
    for i in range(len(keys)-1):
        if keys[i] <= slope <= keys[i+1]:
            k1 = slope_correction_table[keys[i]]
            k2 = slope_correction_table[keys[i+1]]
            return k1 + (k2 - k1) * (slope - keys[i]) / (keys[i+1] - keys[i])
    return 1.0

# Функция получения коэффициента РУД
def get_thrust_factor(rud):
    keys = sorted(thrust_correction_table.keys())
    if rud <= keys[0]:
        return thrust_correction_table[keys[0]]
    if rud >= keys[-1]:
        return thrust_correction_table[keys[-1]]
    for i in range(len(keys)-1):
        if keys[i] <= rud <= keys[i+1]:
            k1 = thrust_correction_table[keys[i]]
            k2 = thrust_correction_table[keys[i+1]]
            return k1 + (k2 - k1) * (rud - keys[i]) / (keys[i+1] - keys[i])
    return 1.0

# ================== Физическая модель для посадки (пока упрощённая) ==================
def landing_distance(mass, temp, wind, slope, wet=False, mu=0.6):
    # Оценочная посадочная скорость (км/ч) зависит от массы. Для Ан-124 примерно V = 240 + 0.1*(mass-250)
    v_kmh = 240 + 0.1 * (mass - 250)  # при 250 т ~ 240 км/ч, при 400 т ~ 255 км/ч
    v_ms = v_kmh / 3.6
    # Среднее замедление (м/с2) для сухого бетона с реверсом (примерно 3-4 м/с2)
    a = 3.0
    # Влияние температуры (при высокой температуре плотность ниже, посадочная скорость выше – грубо)
    temp_factor = 1 + 0.002 * (temp - 15)  # на каждые 10°C около 2%
    # Влияние ветра: встречный уменьшает путевую скорость, попутный увеличивает
    wind_factor = (v_ms - wind) / v_ms  # wind положительный – встречный
    if wind_factor <= 0:
        wind_factor = 0.1  # минимум, чтобы дистанция не стала нулевой
    # Влияние уклона: положительный уклон вверх увеличивает тормозной путь
    slope_factor = 1 + 0.01 * slope  # slope в % (вверх положительный)
    # Влияние влажности: коэффициент K_mu из рис. 7.73
    if wet:
        # Линейная аппроксимация K_mu = 2.0 - 1.667*mu (при mu=0.6 -> 1.0, при mu=0.3 -> 1.5)
        K_mu = 2.0 - 1.667 * mu
    else:
        K_mu = 1.0
    # Расчёт длины пробега по формуле L = v^2 / (2*a) * поправки
    L_base = v_ms**2 / (2 * a)
    L = L_base * temp_factor * wind_factor * slope_factor * K_mu
    return L

# ================== Экран для расчёта длины пробега (посадка) ==================
class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        main_layout.add_widget(Label(text='Длина пробега (посадка)', size_hint_y=0.1, bold=True, font_size=sp(18)))

        # Поля ввода
        inputs_layout = GridLayout(cols=2, size_hint_y=0.7, spacing=dp(5), padding=dp(5))
        inputs_layout.bind(minimum_height=inputs_layout.setter('height'))

        self.mass_input = TextInput(text='300', multiline=False, input_filter='float')
        self.temp_input = TextInput(text='15', multiline=False, input_filter='float')
        self.wind_input = TextInput(text='0', multiline=False, input_filter='float')
        self.slope_input = TextInput(text='0', multiline=False, input_filter='float')
        self.surface_spinner = Spinner(text='Сухой', values=('Сухой', 'Влажный'), size_hint=(1, None), height=dp(40))

        inputs_layout.add_widget(Label(text='Посадочная масса (т):'))
        inputs_layout.add_widget(self.mass_input)
        inputs_layout.add_widget(Label(text='Температура воздуха (°C):'))
        inputs_layout.add_widget(self.temp_input)
        inputs_layout.add_widget(Label(text='Ветер (м/с, +встречный):'))
        inputs_layout.add_widget(self.wind_input)
        inputs_layout.add_widget(Label(text='Уклон ВПП (%, +вверх):'))
        inputs_layout.add_widget(self.slope_input)
        inputs_layout.add_widget(Label(text='Состояние ВПП:'))
        inputs_layout.add_widget(self.surface_spinner)

        main_layout.add_widget(inputs_layout)

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
        btn_calc = Button(text='Рассчитать', font_size=sp(16))
        btn_back = Button(text='Назад', font_size=sp(16))
        btn_layout.add_widget(btn_calc)
        btn_layout.add_widget(btn_back)
        main_layout.add_widget(btn_layout)

        btn_calc.bind(on_press=self.calculate)
        btn_back.bind(on_press=self.go_back)

        self.add_widget(main_layout)

    def calculate(self, instance):
        try:
            mass = float(self.mass_input.text)
            temp = float(self.temp_input.text)
            wind = float(self.wind_input.text)
            slope = float(self.slope_input.text)
            surface = self.surface_spinner.text
            wet = (surface == 'Влажный')
            # Можно добавить выбор mu, но пока фиксируем 0.6 для сухого, 0.4 для влажного
            mu = 0.6 if not wet else 0.4
            L = landing_distance(mass, temp, wind, slope, wet, mu)
            meters_rounded = round_up_50_meters(L)
            feet_rounded = round_up_100_feet(meters_rounded)
            details = (f"Масса: {mass} т\nТемпература: {temp}°C\nВетер: {wind} м/с\n"
                       f"Уклон: {slope}%\nПокрытие: {surface}\n\n"
                       f"Расчётная длина пробега (до округления): {L:.0f} м")
            result_msg = f"{details}\n\nОкруглено:\n{meters_rounded:.0f} м\n{feet_rounded:.0f} футов"
            popup = Popup(title='Результат', content=Label(text=result_msg, font_size=sp(14)), size_hint=(0.8, 0.6))
            popup.open()
        except Exception as e:
            popup = Popup(title='Ошибка', content=Label(text=f"Неверный ввод: {str(e)}"), size_hint=(0.8, 0.3))
            popup.open()

    def go_back(self, instance):
        self.manager.current = 'menu'

# ================== Экран для расчёта длины разбега (взлёт) ==================
class TakeoffScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        main_layout.add_widget(Label(text='Длина разбега (взлёт)', size_hint_y=0.1, bold=True, font_size=sp(18)))

        # Поля ввода
        inputs_layout = GridLayout(cols=2, size_hint_y=0.8, spacing=dp(5), padding=dp(5))
        inputs_layout.bind(minimum_height=inputs_layout.setter('height'))

        self.mass_input = TextInput(text='300', multiline=False, input_filter='float')
        self.temp_input = TextInput(text='15', multiline=False, input_filter='float')
        self.wind_input = TextInput(text='0', multiline=False, input_filter='float')
        self.slope_input = TextInput(text='0', multiline=False, input_filter='float')
        self.thrust_input = TextInput(text='110', multiline=False, input_filter='float')  # положение РУД
        self.surface_spinner = Spinner(text='Сухой', values=('Сухой', 'Влажный'), size_hint=(1, None), height=dp(40))

        inputs_layout.add_widget(Label(text='Взлётная масса (т):'))
        inputs_layout.add_widget(self.mass_input)
        inputs_layout.add_widget(Label(text='Температура воздуха (°C):'))
        inputs_layout.add_widget(self.temp_input)
        inputs_layout.add_widget(Label(text='Ветер (м/с, +встречный):'))
        inputs_layout.add_widget(self.wind_input)
        inputs_layout.add_widget(Label(text='Уклон ВПП (%, +вверх):'))
        inputs_layout.add_widget(self.slope_input)
        inputs_layout.add_widget(Label(text='Положение РУД (град УПРТ):'))
        inputs_layout.add_widget(self.thrust_input)
        inputs_layout.add_widget(Label(text='Состояние ВПП:'))
        inputs_layout.add_widget(self.surface_spinner)

        main_layout.add_widget(inputs_layout)

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
        btn_calc = Button(text='Рассчитать', font_size=sp(16))
        btn_back = Button(text='Назад', font_size=sp(16))
        btn_layout.add_widget(btn_calc)
        btn_layout.add_widget(btn_back)
        main_layout.add_widget(btn_layout)

        btn_calc.bind(on_press=self.calculate)
        btn_back.bind(on_press=self.go_back)

        self.add_widget(main_layout)

    def calculate(self, instance):
        try:
            mass = float(self.mass_input.text)
            temp = float(self.temp_input.text)
            wind = float(self.wind_input.text)
            slope = float(self.slope_input.text)
            thrust = float(self.thrust_input.text)
            surface = self.surface_spinner.text
            wet = (surface == 'Влажный')
            mu = 0.6 if not wet else 0.4

            # Базовая длина разбега по таблице (для штиля, 0 уклона, стандартной тяги)
            L_base = interpolate_2d(takeoff_distance_table, mass, temp)
            # Поправка на ветер
            wind_factor = get_wind_factor(wind)
            # Поправка на уклон
            slope_factor = get_slope_factor(slope)
            # Поправка на тягу (РУД)
            thrust_factor = get_thrust_factor(thrust)
            # Поправка на влажность (K_mu)
            K_mu = 1.0
            if wet:
                K_mu = 2.0 - 1.667 * mu
            # Полная длина разбега
            L_full = L_base * wind_factor * slope_factor * thrust_factor * K_mu

            # Прерванный взлёт (грубо)
            L_aborted = L_full * aborted_takeoff_factor

            # Продолженный взлёт (с отказом двигателя)
            L_continued_base = interpolate_2d(continued_takeoff_table, mass, temp)
            L_continued = L_continued_base * wind_factor * slope_factor * thrust_factor * K_mu

            # Округление
            L_full_r = round_up_50_meters(L_full)
            L_aborted_r = round_up_50_meters(L_aborted)
            L_continued_r = round_up_50_meters(L_continued)

            details = (f"Введённые данные:\n"
                       f"Масса: {mass} т\nТемпература: {temp}°C\nВетер: {wind} м/с\n"
                       f"Уклон: {slope}%\nРУД: {thrust}°\nПокрытие: {surface}\n\n"
                       f"Результаты (округлены до 50 м):\n"
                       f"Полная дистанция разбега: {L_full_r} м ({L_full_r*FEET_IN_METER:.0f} фут)\n"
                       f"Дистанция прерванного взлёта: {L_aborted_r} м ({L_aborted_r*FEET_IN_METER:.0f} фут)\n"
                       f"Дистанция продолженного взлёта: {L_continued_r} м ({L_continued_r*FEET_IN_METER:.0f} фут)")

            popup = Popup(title='Результат', content=Label(text=details, font_size=sp(12)), size_hint=(0.9, 0.7))
            popup.open()

        except Exception as e:
            popup = Popup(title='Ошибка', content=Label(text=f"Неверный ввод: {str(e)}"), size_hint=(0.8, 0.3))
            popup.open()

    def go_back(self, instance):
        self.manager.current = 'menu'

# ================== Главное меню (обновлённое) ==================
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        layout.add_widget(Label(text='Выберите тип расчёта:', size_hint_y=0.1, bold=True, font_size=sp(18)))

        buttons = [
            ('Длина пробега (посадка)', 'landing'),
            ('Длина разбега (взлёт)', 'takeoff'),
            ('Выход', 'exit')
        ]
        for text, screen_name in buttons:
            btn = Button(text=text, size_hint_y=None, height=dp(60), font_size=sp(16))
            if screen_name == 'exit':
                btn.bind(on_press=lambda x: App.get_running_app().stop())
            else:
                btn.bind(on_press=lambda x, sn=screen_name: self.open_screen(sn))
            layout.add_widget(btn)

        scroll = ScrollView()
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_screen(self, screen_name):
        self.manager.current = screen_name

# ================== Основное приложение ==================
class HeightCalcApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(LandingScreen(name='landing'))
        sm.add_widget(TakeoffScreen(name='takeoff'))
        return sm

if __name__ == '__main__':
    HeightCalcApp().run()
