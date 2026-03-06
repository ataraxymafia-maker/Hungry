class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = {}

        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))

        grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(10), padding=dp(10))
        grid.bind(minimum_height=grid.setter('height'))

        fields = [
            ('mass', 'Масса (200-390 т):'),
            ('temp', 'Температура (-60...+40°C):'),
            ('alt', 'Высота аэродрома (0-2500 м):'),
            ('wind', 'Ветер (-15...+15 м/с):'),
            ('slope', 'Уклон ВПП (-2.0...+0.0%):'),
            ('v1', 'V1/Vn.on (0.7-1.0):'),
        ]
        for key, label in fields:
            grid.add_widget(Label(
                text=label,
                halign='right',
                size_hint_x=0.4,
                font_size=sp(16)
            ))
            ti = TextInput(
                text='1.0' if key == 'v1' else '',
                multiline=False,
                input_filter='float',
                size_hint_x=0.6,
                font_size=sp(16),
                height=dp(40)
            )
            self.inputs[key] = ti
            grid.add_widget(ti)

        main_layout.add_widget(grid)

        btn_layout = BoxLayout(size_hint_y=0.2, spacing=dp(15), padding=dp(10))
        btn_calc = Button(text='Рассчитать', font_size=sp(18))
        btn_back = Button(text='Назад', font_size=sp(18))
        btn_layout.add_widget(btn_calc)
        btn_layout.add_widget(btn_back)
        main_layout.add_widget(btn_layout)

        btn_calc.bind(on_press=self.calculate)
        btn_back.bind(on_press=self.go_back)

        self.add_widget(main_layout)

    def calculate(self, instance):
        try:
            mass = float(self.inputs['mass'].text.replace(',', '.'))
            temp = float(self.inputs['temp'].text.replace(',', '.'))
            alt = float(self.inputs['alt'].text.replace(',', '.'))
            wind = float(self.inputs['wind'].text.replace(',', '.'))
            slope = float(self.inputs['slope'].text.replace(',', '.'))
            v1 = float(self.inputs['v1'].text.replace(',', '.'))
        except ValueError:
            self.show_popup('Ошибка', 'Введите все числовые значения (используйте точку или запятую)')
            return

        # Проверка диапазонов (ноль допускается)
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

        # Расчёт всех трёх режимов
        norm_res = calculate_takeoff(mass, temp, alt, wind, slope, v1, 'norm')
        cont_res = calculate_takeoff(mass, temp, alt, wind, slope, v1, 'cont')
        abort_res = calculate_takeoff(mass, temp, alt, wind, slope, v1, 'abort')

        def fmt_result(val):
            if val is None or math.isnan(val):
                return "Нет данных"
            r50 = round_up_50_meters(val)
            rft = round_up_100_feet(r50)
            return f"{val:.1f} м → {r50:.0f} м / {rft:.0f} фут"

        msg = (
            f"[ НОРМАЛЬНЫЙ ВЗЛЁТ ]\n{fmt_result(norm_res)}\n\n"
            f"[ ПРОДОЛЖЕННЫЙ ВЗЛЁТ ]\n{fmt_result(cont_res)}\n\n"
            f"[ ПРЕРВАННЫЙ ВЗЛЁТ ]\n{fmt_result(abort_res)}"
        )

        self.show_popup('Результаты расчёта', msg, size=(0.9, 0.7))

    def go_back(self, instance):
        self.manager.current = 'menu'

    def show_popup(self, title, text, size=(0.8, 0.5)):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=text, font_size=sp(14), halign='left', valign='top'))
        btn_close = Button(text='Закрыть', size_hint_y=0.2, font_size=sp(14))
        content.add_widget(btn_close)
        popup = Popup(title=title, content=content, size_hint=size, auto_dismiss=False)
        btn_close.bind(on_press=popup.dismiss)
        popup.open()
