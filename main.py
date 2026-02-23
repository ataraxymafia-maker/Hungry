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
from kivy.metrics import dp

# Константы
FEET_IN_METER = 3.28084
L0 = 0.0065
QNE_HPA = 1013.25
QNE_MMHG = 760
STEP_HPA = 8.3
STEP_MMHG = 11

# Все функции расчёта (те же, без изменений)
def round_up_50_meters(value):
    return math.ceil(value / 50) * 50

def round_up_100_feet(value_meters):
    feet = value_meters * FEET_IN_METER
    return math.ceil(feet / 100) * 100

def calc_H_MBVk_QFE(dH_prep, flight_type, t_azr, H_azr):
    MZV = 100 if flight_type == "1" else 200
    H = dH_prep + MZV
    t0 = t_azr + L0 * H_azr
    denom = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denom <= 0:
        return None, "Ошибка: знаменатель <=0"
    dH_t = H * (15 - t0) / denom
    res = dH_prep + MZV + dH_t
    return res, None

def calc_H_MBVk_QNH(H_prep, flight_type, t_azr, H_azr):
    MZV = 100 if flight_type == "1" else 200
    H = H_prep + MZV
    t0 = t_azr + L0 * H_azr
    denom = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denom <= 0:
        return None, "Ошибка: знаменатель <=0"
    dH_t = H * (15 - t0) / denom
    res = H_prep + MZV + dH_t
    return res, None

def calc_H_MBVra_QFE(dH_prep, terrain, t_azr, H_azr):
    MZV = 300 if terrain == "1" else 600
    H = dH_prep + MZV
    t0 = t_azr + L0 * H_azr
    denom = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denom <= 0:
        return None, "Ошибка: знаменатель <=0"
    dH_t = H * (15 - t0) / denom
    res = dH_prep + MZV + dH_t
    return res, None

def calc_H_MBVra_QNH(H_prep, terrain, t_azr, H_azr):
    MZV = 300 if terrain == "1" else 600
    H = H_prep + MZV
    t0 = t_azr + L0 * H_azr
    denom = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denom <= 0:
        return None, "Ошибка: знаменатель <=0"
    dH_t = H * (15 - t0) / denom
    res = H_prep + MZV + dH_t
    return res, None

def calc_H_BN_QNH(H_prep, terrain, t3):
    MZV = 300 if terrain == "1" else 600
    base = H_prep + MZV
    factor = 285 / (273 + t3)
    res = base * factor
    return res, None

def calc_H_NE_QNE(H_prep, units, QNH_raiona, t3):
    MZV = 600
    if units == "1":
        delta_h = STEP_HPA
        QNE = QNE_HPA
    else:
        delta_h = STEP_MMHG
        QNE = QNE_MMHG
    delta_H_bar = (QNE - QNH_raiona) * delta_h
    base = H_prep + MZV + delta_H_bar
    factor = 285 / (273 + t3)
    res = base * factor
    return res, None

def calc_H_perekh_ES(H_prep, t3):
    base = H_prep + 600
    factor = 285 / (273 + t3)
    res = base * factor
    return res, None

def calc_H_Zmin(H_rel, terrain):
    MZV = 300 if terrain == "1" else 600
    res = H_rel + MZV
    return res, None

def calc_H_eperekh_airport(H_perekh):
    res = H_perekh + 300
    return res, None

def calc_H_eperekh_ES(H_perekh_es):
    res = H_perekh_es + 300
    return res, None

# Экран с формулой и вводом
class CalcScreen(Screen):
    def __init__(self, calc_name, formula_text, fields, calc_func, **kwargs):
        super().__init__(**kwargs)
        self.calc_func = calc_func
        self.fields = fields
        self.inputs = {}

        main_layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))

        # Заголовок
        main_layout.add_widget(Label(text=calc_name, size_hint_y=0.1, bold=True))

        # Формула (прокручиваемый текст)
        formula_label = Label(text=formula_text, size_hint_y=0.2, halign='left', valign='top')
        formula_label.bind(size=lambda s, w: s.setter('text_size')(s, (w, None)))
        scroll = ScrollView(size_hint_y=0.2)
        scroll.add_widget(formula_label)
        main_layout.add_widget(scroll)

        # Поля ввода
        grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(5), padding=dp(5))
        grid.bind(minimum_height=grid.setter('height'))
        for field in fields:
            grid.add_widget(Label(text=field['label'], halign='right', size_hint_x=0.4))
            ti = TextInput(text=field.get('default', ''), multiline=False, input_filter='float', size_hint_x=0.6)
            self.inputs[field['name']] = ti
            grid.add_widget(ti)
        main_layout.add_widget(grid)

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
        btn_calc = Button(text='Рассчитать')
        btn_back = Button(text='Назад')
        btn_layout.add_widget(btn_calc)
        btn_layout.add_widget(btn_back)
        main_layout.add_widget(btn_layout)

        btn_calc.bind(on_press=self.calculate)
        btn_back.bind(on_press=self.go_back)
        self.add_widget(main_layout)

    def calculate(self, instance):
        values = {}
        for name, ti in self.inputs.items():
            try:
                values[name] = float(ti.text)
            except ValueError:
                self.show_error("Ошибка ввода", f"Поле '{name}' должно быть числом")
                return
        res, err = self.calc_func(**values)
        if err:
            self.show_error("Ошибка расчёта", err)
        else:
            meters_rounded = round_up_50_meters(res)
            feet_rounded = round_up_100_feet(meters_rounded)
            msg = f"Результат (до округления): {res:.1f} м\n\nОкруглено:\n{meters_rounded:.0f} м\n{feet_rounded:.0f} футов"
            self.show_result(msg)

    def show_error(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.8, 0.3))
        popup.open()

    def show_result(self, msg):
        popup = Popup(title='Результат', content=Label(text=msg), size_hint=(0.8, 0.5))
        popup.open()

    def go_back(self, instance):
        self.manager.current = 'menu'

# Главное меню
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(5))

        layout.add_widget(Label(text='Выберите тип расчёта:', size_hint_y=0.1, bold=True))

        # Список расчётов: (название, имя экрана, формула, поля, функция)
        self.calc_list = [
            {
                'name': 'Относительная МБВ круга полётов (QFE) – п.1',
                'screen_name': 'calc1',
                'formula': "H_МБВкQFE = ΔH_преп + МЗВ + ΔH_t\n"
                           "где ΔH_t = H*(15-t0)/(273+t0-0.5*L0*(H+H_азр))\n"
                           "H = ΔH_преп + МЗВ, t0 = t_азр + L0*H_азр",
                'fields': [
                    {'label': 'ΔH_преп (м)', 'name': 'dH_prep'},
                    {'label': 'Тип полёта (1-ПВП, 2-ППП)', 'name': 'flight_type', 'default': '1'},
                    {'label': 't_азр (°C)', 'name': 't_azr'},
                    {'label': 'H_азр (м)', 'name': 'H_azr'},
                ],
                'func': lambda dH_prep, flight_type, t_azr, H_azr: calc_H_MBVk_QFE(dH_prep, str(int(flight_type)), t_azr, H_azr)
            },
            {
                'name': 'Абсолютная МБВ круга полётов (QNH) – п.2',
                'screen_name': 'calc2',
                'formula': "H_МБВкQNH = H_преп + МЗВ + ΔH_t\n"
                           "ΔH_t – по той же формуле, что в п.1",
                'fields': [
                    {'label': 'H_преп (м)', 'name': 'H_prep'},
                    {'label': 'Тип полёта (1-ПВП, 2-ППП)', 'name': 'flight_type', 'default': '1'},
                    {'label': 't_азр (°C)', 'name': 't_azr'},
                    {'label': 'H_азр (м)', 'name': 'H_azr'},
                ],
                'func': lambda H_prep, flight_type, t_azr, H_azr: calc_H_MBVk_QNH(H_prep, str(int(flight_type)), t_azr, H_azr)
            },
            {
                'name': 'Относительная МБВ в районе аэродрома (QFE) – п.3',
                'screen_name': 'calc3',
                'formula': "H_МБВраQFE = ΔH_преп + МЗВ + ΔH_t\n"
                           "МЗВ: равнина/холмы – 300 м, горы – 600 м",
                'fields': [
                    {'label': 'ΔH_преп (м) 46км+9км', 'name': 'dH_prep'},
                    {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terrain', 'default': '1'},
                    {'label': 't_азр (°C)', 'name': 't_azr'},
                    {'label': 'H_азр (м)', 'name': 'H_azr'},
                ],
                'func': lambda dH_prep, terrain, t_azr, H_azr: calc_H_MBVra_QFE(dH_prep, str(int(terrain)), t_azr, H_azr)
            },
            {
                'name': 'Абсолютная МБВ в районе аэродрома (QNH) – п.4',
                'screen_name': 'calc4',
                'formula': "H_МБВраQNH = H_преп + МЗВ + ΔH_t",
                'fields': [
                    {'label': 'H_преп (м) 46км+9км', 'name': 'H_prep'},
                    {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terrain', 'default': '1'},
                    {'label': 't_азр (°C)', 'name': 't_azr'},
                    {'label': 'H_азр (м)', 'name': 'H_azr'},
                ],
                'func': lambda H_prep, terrain, t_azr, H_azr: calc_H_MBVra_QNH(H_prep, str(int(terrain)), t_azr, H_azr)
            },
            {
                'name': 'Абсолютная безопасная высота ниже нижнего эшелона – п.6',
                'screen_name': 'calc6',
                'formula': "H_БНQNH = (H_преп + МЗВ) × 285/(273 + t_3)",
                'fields': [
                    {'label': 'H_преп (м)', 'name': 'H_prep'},
                    {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terrain', 'default': '1'},
                    {'label': 't3 (°C)', 'name': 't3'},
                ],
                'func': lambda H_prep, terrain, t3: calc_H_BN_QNH(H_prep, str(int(terrain)), t3)
            },
            {
                'name': 'Нижний безопасный эшелон (QNE) – п.7',
                'screen_name': 'calc7',
                'formula': "H_НЭQNE = (H_преп + 600 + ΔH_бар) × 285/(273 + t3)\n"
                           "ΔH_бар = (QNE - QNH_района) × Δh\n"
                           "Δh = 8.3 м/гПа или 11 м/мм рт.ст.",
                'fields': [
                    {'label': 'H_преп (м)', 'name': 'H_prep'},
                    {'label': 'Ед.давл (1-гПа, 2-мм рт.ст.)', 'name': 'units', 'default': '1'},
                    {'label': 'QNH района', 'name': 'qnh'},
                    {'label': 't3 (°C)', 'name': 't3'},
                ],
                'func': lambda H_prep, units, qnh, t3: calc_H_NE_QNE(H_prep, str(int(units)), qnh, t3)
            },
            {
                'name': 'Абсолютная высота перехода района ЕС ОрВД – п.9',
                'screen_name': 'calc9',
                'formula': "H_перехЕС = (H_преп + 600) × 285/(273 + t3)",
                'fields': [
                    {'label': 'H_преп (м)', 'name': 'H_prep'},
                    {'label': 't3 (°C)', 'name': 't3'},
                ],
                'func': lambda H_prep, t3: calc_H_perekh_ES(H_prep, t3)
            },
            {
                'name': 'Минимальная абсолютная высота в зоне (grid MORA) – п.11',
                'screen_name': 'calc11',
                'formula': "H_Змин = H_рел + МЗВ",
                'fields': [
                    {'label': 'H_рел (м)', 'name': 'H_rel'},
                    {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terrain', 'default': '1'},
                ],
                'func': lambda H_rel, terrain: calc_H_Zmin(H_rel, str(int(terrain)))
            },
            {
                'name': 'Высота эшелона перехода в районе аэродрома – п.8',
                'screen_name': 'calc8',
                'formula': "H_эперехQNH = H_перехQNH + 300",
                'fields': [
                    {'label': 'H_перехQNH (м)', 'name': 'H_perekh'},
                ],
                'func': lambda H_perekh: calc_H_eperekh_airport(H_perekh)
            },
            {
                'name': 'Высота эшелона перехода в районе ЕС ОрВД – п.10',
                'screen_name': 'calc10',
                'formula': "H_эперехЕС = H_перехЕС + 300",
                'fields': [
                    {'label': 'H_перехЕС (м)', 'name': 'H_perekh_es'},
                ],
                'func': lambda H_perekh_es: calc_H_eperekh_ES(H_perekh_es)
            },
        ]

        # Создаем кнопки меню
        for calc in self.calc_list:
            btn = Button(text=calc['name'], size_hint_y=None, height=dp(50))
            btn.calc_info = calc
            btn.bind(on_press=self.open_calc)
            layout.add_widget(btn)

        # Кнопка выхода (закрыть приложение)
        btn_exit = Button(text='Выход', size_hint_y=None, height=dp(50))
        btn_exit.bind(on_press=lambda x: App.get_running_app().stop())
        layout.add_widget(btn_exit)

        scroll = ScrollView()
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_calc(self, instance):
        info = instance.calc_info
        # Создаём экран с калькулятором, если ещё не создан
        if not self.manager.has_screen(info['screen_name']):
            screen = CalcScreen(
                name=info['screen_name'],
                calc_name=info['name'],
                formula_text=info['formula'],
                fields=info['fields'],
                calc_func=info['func']
            )
            self.manager.add_widget(screen)
        self.manager.current = info['screen_name']

class HeightCalcApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        return sm

if __name__ == '__main__':
    HeightCalcApp().run()
