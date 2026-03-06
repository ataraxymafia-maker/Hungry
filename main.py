import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp

# ========== ЭКРАНЫ ==========

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.add_widget(Label(text='Главное меню', font_size=sp(24), bold=True, size_hint_y=0.2))
        btn_takeoff = Button(text='Взлётные характеристики', size_hint_y=0.2, font_size=sp(18))
        btn_exit = Button(text='Выход', size_hint_y=0.2, font_size=sp(18))
        btn_takeoff.bind(on_press=lambda x: setattr(self.manager, 'current', 'type'))
        btn_exit.bind(on_press=lambda x: App.get_running_app().stop())
        layout.add_widget(btn_takeoff)
        layout.add_widget(btn_exit)
        self.add_widget(layout)

class CalcTypeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.add_widget(Label(text='Выберите тип расчёта', font_size=sp(22), bold=True, size_hint_y=0.2))
        btn_norm = Button(text='Нормальный взлёт', size_hint_y=0.2, font_size=sp(18))
        btn_cont = Button(text='Продолженный взлёт', size_hint_y=0.2, font_size=sp(18))
        btn_abort = Button(text='Прерванный взлёт', size_hint_y=0.2, font_size=sp(18))
        btn_back = Button(text='Назад в меню', size_hint_y=0.2, font_size=sp(18))
        btn_norm.bind(on_press=lambda x: self.goto_input('norm'))
        btn_cont.bind(on_press=lambda x: self.goto_input('cont'))
        btn_abort.bind(on_press=lambda x: self.goto_input('abort'))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_norm)
        layout.add_widget(btn_cont)
        layout.add_widget(btn_abort)
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def goto_input(self, calc_type):
        self.manager.get_screen('input').set_calc_type(calc_type)
        self.manager.current = 'input'

class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calc_type = 'norm'
        self.inputs = {}

        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))

        # Заголовок
        self.title_label = Label(text='Нормальный взлёт', font_size=sp(20), bold=True, size_hint_y=0.1)
        main_layout.add_widget(self.title_label)

        # Поля ввода
        grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(10), padding=dp(10))
        grid.bind(minimum_height=grid.setter('height'))

        fields = [
            ('mass', 'Масса, т'),
            ('temp', 'Температура, °C'),
            ('alt', 'Высота аэродрома, м'),
            ('wind', 'Ветер, м/с'),
            ('slope', 'Уклон ВПП, %'),
        ]
        for key, label in fields:
            grid.add_widget(Label(text=label, halign='right', size_hint_x=0.4, font_size=sp(16)))
            ti = TextInput(
                text='',
                multiline=False,
                input_filter='float',
                font_size=sp(16),
                height=dp(40)
            )
            self.inputs[key] = ti
            grid.add_widget(ti)

        # Поле V1 (только для прерванного)
        self.v1_label = Label(text='V1/Vn.on', halign='right', size_hint_x=0.4, font_size=sp(16))
        self.v1_input = TextInput(
            text='1.0',
            multiline=False,
            input_filter='float',
            font_size=sp(16),
            height=dp(40)
        )
        grid.add_widget(self.v1_label)
        grid.add_widget(self.v1_input)
        self.inputs['v1'] = self.v1_input

        main_layout.add_widget(grid)

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=dp(15), padding=dp(10))
        btn_calc = Button(text='Рассчитать', font_size=sp(18))
        btn_back = Button(text='Назад', font_size=sp(18))
        btn_layout.add_widget(btn_calc)
        btn_layout.add_widget(btn_back)
        main_layout.add_widget(btn_layout)

        btn_calc.bind(on_press=self.calculate)
        btn_back.bind(on_press=self.go_back)

        self.add_widget(main_layout)

    def set_calc_type(self, calc_type):
        self.calc_type = calc_type
        titles = {'norm': 'Нормальный взлёт', 'cont': 'Продолженный взлёт', 'abort': 'Прерванный взлёт'}
        self.title_label.text = titles[calc_type]
        if calc_type == 'abort':
            self.v1_label.opacity = 1
            self.v1_input.opacity = 1
            self.v1_input.disabled = False
        else:
            self.v1_label.opacity = 0
            self.v1_input.opacity = 0
            self.v1_input.disabled = True

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

        # Заглушка расчёта
        msg = (f"Введено:\n"
               f"Масса: {mass} т\n"
               f"Температура: {temp} °C\n"
               f"Высота: {alt} м\n"
               f"Ветер: {wind} м/с\n"
               f"Уклон: {slope} %\n"
               f"V1/Vn.on: {v1}")
        self.show_popup('Результат (тест)', msg)

    def go_back(self, instance):
        self.manager.current = 'type'

    def show_popup(self, title, text, size=(0.8, 0.5)):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=text, font_size=sp(14)))
        btn_close = Button(text='Закрыть', size_hint_y=0.3, font_size=sp(14))
        content.add_widget(btn_close)
        popup = Popup(title=title, content=content, size_hint=size, auto_dismiss=False)
        btn_close.bind(on_press=popup.dismiss)
        popup.open()

class TakeoffApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(CalcTypeScreen(name='type'))
        sm.add_widget(InputScreen(name='input'))
        return sm

if __name__ == '__main__':
    TakeoffApp().run()
