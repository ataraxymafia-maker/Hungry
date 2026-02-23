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

# Константы (те же, что были)
FEET_IN_METER = 3.28084
L0 = 0.0065
QNE_HPA = 1013.25
QNE_MMHG = 760
STEP_HPA = 8.3
STEP_MMHG = 11

# Все функции расчёта (перенесены без изменений)
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

# Вспомогательная функция для показа результата
def show_result_popup(title, result):
    meters_rounded = round_up_50_meters(result)
    feet_rounded = round_up_100_feet(meters_rounded)
    msg = f"{title}\n\nРезультат:\n{meters_rounded:.0f} м\n{feet_rounded:.0f} футов"
    popup = Popup(title='Результат',
                  content=Label(text=msg),
                  size_hint=(0.8, 0.5))
    popup.open()

# Класс экрана с выбором расчёта
class CalcScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = 10
        self.spacing = 10

        self.add_widget(Label(text='Выберите тип расчёта:', size_hint_y=0.1))

        # Создаем кнопки для каждого пункта
        buttons = [
            ('1. МБВ круга QFE', self.calc_1),
            ('2. МБВ круга QNH', self.calc_2),
            ('3. МБВ район QFE', self.calc_3),
            ('4. МБВ район QNH', self.calc_4),
            ('5. Безопасная ниже эшелона', self.calc_6),
            ('6. Нижний эшелон', self.calc_7),
            ('7. Высота перехода ЕС', self.calc_9),
            ('8. Grid MORA', self.calc_11),
            ('9. Эш.перехода аэродром', self.calc_8),
            ('10. Эш.перехода ЕС', self.calc_10),
        ]
        for text, callback in buttons:
            btn = Button(text=text, size_hint_y=None, height=50)
            btn.bind(on_press=callback)
            self.add_widget(btn)

    # Далее идут методы для каждого расчёта, которые открывают Popup с вводом данных
    def get_input_popup(self, title, fields, callback):
        """Универсальный popup для ввода нескольких значений"""
        content = BoxLayout(orientation='vertical', spacing=5, padding=10)
        inputs = {}
        for field in fields:
            content.add_widget(Label(text=field['label'], size_hint_y=None, height=30))
            ti = TextInput(text=field.get('default', ''), multiline=False)
            inputs[field['name']] = ti
            content.add_widget(ti)
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        btn_ok = Button(text='OK')
        btn_cancel = Button(text='Отмена')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)

        popup = Popup(title=title, content=content, size_hint=(0.9, 0.8))
        def on_ok(instance):
            # Собираем значения
            values = {}
            for name, ti in inputs.items():
                try:
                    values[name] = float(ti.text)
                except:
                    values[name] = None
            popup.dismiss()
            callback(values)
        def on_cancel(instance):
            popup.dismiss()
        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=on_cancel)
        popup.open()

    # Пункт 1
    def calc_1(self, instance):
        fields = [
            {'label': 'ΔH_преп (м)', 'name': 'dh'},
            {'label': 'Тип полёта (1-ПВП, 2-ППП)', 'name': 'ftype', 'default': '1'},
            {'label': 't_азр (°C)', 'name': 'tazr'},
            {'label': 'H_азр (м)', 'name': 'hazr'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_MBVk_QFE(vals['dh'], str(int(vals['ftype'])), vals['tazr'], vals['hazr'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('МБВ круга QFE', res)
        self.get_input_popup('МБВ круга QFE', fields, callback)

    # Пункт 2
    def calc_2(self, instance):
        fields = [
            {'label': 'H_преп (м)', 'name': 'hp'},
            {'label': 'Тип полёта (1-ПВП, 2-ППП)', 'name': 'ftype', 'default': '1'},
            {'label': 't_азр (°C)', 'name': 'tazr'},
            {'label': 'H_азр (м)', 'name': 'hazr'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_MBVk_QNH(vals['hp'], str(int(vals['ftype'])), vals['tazr'], vals['hazr'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('МБВ круга QNH', res)
        self.get_input_popup('МБВ круга QNH', fields, callback)

    # Пункт 3
    def calc_3(self, instance):
        fields = [
            {'label': 'ΔH_преп (м) 46км+9км', 'name': 'dh'},
            {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terr', 'default': '1'},
            {'label': 't_азр (°C)', 'name': 'tazr'},
            {'label': 'H_азр (м)', 'name': 'hazr'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_MBVra_QFE(vals['dh'], str(int(vals['terr'])), vals['tazr'], vals['hazr'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('МБВ район QFE', res)
        self.get_input_popup('МБВ район QFE', fields, callback)

    # Пункт 4
    def calc_4(self, instance):
        fields = [
            {'label': 'H_преп (м) 46км+9км', 'name': 'hp'},
            {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terr', 'default': '1'},
            {'label': 't_азр (°C)', 'name': 'tazr'},
            {'label': 'H_азр (м)', 'name': 'hazr'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_MBVra_QNH(vals['hp'], str(int(vals['terr'])), vals['tazr'], vals['hazr'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('МБВ район QNH', res)
        self.get_input_popup('МБВ район QNH', fields, callback)

    # Пункт 6
    def calc_6(self, instance):
        fields = [
            {'label': 'H_преп (м)', 'name': 'hp'},
            {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terr', 'default': '1'},
            {'label': 't3 (°C)', 'name': 't3'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_BN_QNH(vals['hp'], str(int(vals['terr'])), vals['t3'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('Безопасная ниже эшелона', res)
        self.get_input_popup('Безопасная ниже эшелона', fields, callback)

    # Пункт 7
    def calc_7(self, instance):
        fields = [
            {'label': 'H_преп (м)', 'name': 'hp'},
            {'label': 'Ед.давл (1-гПа, 2-мм рт.ст.)', 'name': 'units', 'default': '1'},
            {'label': 'QNH района', 'name': 'qnh'},
            {'label': 't3 (°C)', 'name': 't3'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_NE_QNE(vals['hp'], str(int(vals['units'])), vals['qnh'], vals['t3'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('Нижний эшелон', res)
        self.get_input_popup('Нижний эшелон', fields, callback)

    # Пункт 9
    def calc_9(self, instance):
        fields = [
            {'label': 'H_преп (м)', 'name': 'hp'},
            {'label': 't3 (°C)', 'name': 't3'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_perekh_ES(vals['hp'], vals['t3'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('Высота перехода ЕС', res)
        self.get_input_popup('Высота перехода ЕС', fields, callback)

    # Пункт 11
    def calc_11(self, instance):
        fields = [
            {'label': 'H_рел (м)', 'name': 'hrel'},
            {'label': 'Местность (1-равнина, 2-горы)', 'name': 'terr', 'default': '1'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_Zmin(vals['hrel'], str(int(vals['terr'])))
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('Grid MORA', res)
        self.get_input_popup('Grid MORA', fields, callback)

    # Пункт 8
    def calc_8(self, instance):
        fields = [
            {'label': 'H_перехQNH (м)', 'name': 'hp'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_eperekh_airport(vals['hp'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('Эш.перехода аэродром', res)
        self.get_input_popup('Эш.перехода аэродром', fields, callback)

    # Пункт 10
    def calc_10(self, instance):
        fields = [
            {'label': 'H_перехЕС (м)', 'name': 'hp'},
        ]
        def callback(vals):
            if None in vals.values():
                return
            res, err = calc_H_eperekh_ES(vals['hp'])
            if err:
                popup = Popup(title='Ошибка', content=Label(text=err), size_hint=(0.8,0.3))
                popup.open()
            else:
                show_result_popup('Эш.перехода ЕС', res)
        self.get_input_popup('Эш.перехода ЕС', fields, callback)

# Основной класс приложения
class HeightCalcApp(App):
    def build(self):
        return CalcScreen()

if __name__ == '__main__':
    HeightCalcApp().run()
