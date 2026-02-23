import math

# Константы
FEET_IN_METER = 3.28084
L0 = 0.0065  # температурный градиент, °C/м
QNE_HPA = 1013.25  # гПа
QNE_MMHG = 760  # мм рт.ст.
STEP_HPA = 8.3  # м/гПа
STEP_MMHG = 11  # м/мм рт.ст.

def round_up_50_meters(value):
    """Округление вверх с кратностью 50 метров"""
    return math.ceil(value / 50) * 50

def round_up_100_feet(value_meters):
    """Перевод в футы и округление вверх с кратностью 100 футов"""
    feet = value_meters * FEET_IN_METER
    return math.ceil(feet / 100) * 100

def print_result(meters, details):
    """Вывод подробного решения, затем результата в метрах и футах с округлением"""
    meters_rounded = round_up_50_meters(meters)
    feet_rounded = round_up_100_feet(meters_rounded)

    print("\n📌 ПОДРОБНОЕ РЕШЕНИЕ:")
    print(details)
    print("\n✅ ИТОГОВЫЙ РЕЗУЛЬТАТ (с округлением):")
    print(f"   {meters_rounded:.0f} м (округлено до 50 м вверх)")
    print(f"   {feet_rounded:.0f} футов (округлено до 100 футов вверх)")

def input_float(prompt):
    """Безопасный ввод числа с плавающей точкой"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Ошибка: введите число (можно с десятичной точкой).")

def input_choice(prompt, options):
    """Ввод с проверкой на допустимые варианты"""
    while True:
        val = input(prompt).strip()
        if val in options:
            return val
        print(f"❌ Введите один из вариантов: {', '.join(options)}")

def show_formula(title, formula):
    """Вывод формулы и названия расчёта"""
    print(f"\n--- {title} ---")
    print(f"Формула:\n{formula}")

# ========== Пункт 1: относительная МБВ круга (QFE) ==========
def calc_H_MBVk_QFE():
    show_formula("Относительная МБВ круга полётов (QFE)", 
                 "H_МБВкQFE = ΔH_преп + МЗВ + ΔH_t\n"
                 "где ΔH_t = H * (15 - t0) / (273 + t0 - 0.5 * L0 * (H + H_зр))\n"
                 "      H = ΔH_преп + МЗВ\n"
                 "      t0 = t_азр + L0 * H_азр")

    ΔH_prep = input_float("Относительная высота наивысшего препятствия ΔH_преп (м): ")
    print("Тип полёта:")
    print("  1 - ПВП (МЗВ = 100 м)")
    print("  2 - ППП (МЗВ = 200 м)")
    flight_type = input_choice("Выберите 1 или 2: ", ["1", "2"])
    MZV = 100 if flight_type == "1" else 200
    H = ΔH_prep + MZV

    t_azr = input_float("Минимальная температура на аэродроме t_азр (°C): ")
    H_azr = input_float("Абсолютная высота низшего порога ВПП H_азр (м): ")
    t0 = t_azr + L0 * H_azr

    denominator = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denominator <= 0:
        print("❌ Ошибка: знаменатель формулы температурной поправки <= 0. Проверьте исходные данные.")
        return

    ΔH_t = H * (15 - t0) / denominator
    result = ΔH_prep + MZV + ΔH_t

    details = (f"1. ΔH_преп = {ΔH_prep:.2f} м\n"
               f"2. МЗВ = {MZV} м (тип полёта: {'ПВП' if flight_type=='1' else 'ППП'})\n"
               f"3. H = ΔH_преп + МЗВ = {ΔH_prep:.2f} + {MZV} = {H:.2f} м\n"
               f"4. t0 = t_азр + L0 * H_азр = {t_azr:.2f} + {L0} * {H_azr:.2f} = {t0:.2f} °C\n"
               f"5. Знаменатель: 273 + t0 - 0.5*L0*(H + H_зр) = 273 + {t0:.2f} - 0.5*{L0}*({H:.2f} + {H_azr:.2f}) = {denominator:.4f}\n"
               f"6. Температурная поправка ΔH_t = H * (15 - t0) / знаменатель = {H:.2f} * (15 - {t0:.2f}) / {denominator:.4f} = {ΔH_t:.2f} м\n"
               f"7. Искомая высота (до округления): ΔH_преп + МЗВ + ΔH_t = {ΔH_prep:.2f} + {MZV} + {ΔH_t:.2f} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 2: абсолютная МБВ круга (QNH) ==========
def calc_H_MBVk_QNH():
    show_formula("Абсолютная МБВ круга полётов (QNH)", 
                 "H_МБВкQNH = H_преп + МЗВ + ΔH_t\n"
                 "где ΔH_t – температурная поправка (см. пункт 1)")

    H_prep = input_float("Абсолютная высота наивысшего препятствия H_преп (м): ")
    print("Тип полёта:")
    print("  1 - ПВП (МЗВ = 100 м)")
    print("  2 - ППП (МЗВ = 200 м)")
    flight_type = input_choice("Выберите 1 или 2: ", ["1", "2"])
    MZV = 100 if flight_type == "1" else 200
    H = H_prep + MZV

    t_azr = input_float("Минимальная температура на аэродроме t_азр (°C): ")
    H_azr = input_float("Абсолютная высота низшего порога ВПП H_азр (м): ")
    t0 = t_azr + L0 * H_azr

    denominator = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denominator <= 0:
        print("❌ Ошибка: знаменатель формулы температурной поправки <= 0. Проверьте исходные данные.")
        return

    ΔH_t = H * (15 - t0) / denominator
    result = H_prep + MZV + ΔH_t

    details = (f"1. H_преп = {H_prep:.2f} м\n"
               f"2. МЗВ = {MZV} м (тип полёта: {'ПВП' if flight_type=='1' else 'ППП'})\n"
               f"3. H = H_преп + МЗВ = {H_prep:.2f} + {MZV} = {H:.2f} м\n"
               f"4. t0 = t_азр + L0 * H_азр = {t_azr:.2f} + {L0} * {H_azr:.2f} = {t0:.2f} °C\n"
               f"5. Знаменатель: 273 + t0 - 0.5*L0*(H + H_зр) = 273 + {t0:.2f} - 0.5*{L0}*({H:.2f} + {H_azr:.2f}) = {denominator:.4f}\n"
               f"6. Температурная поправка ΔH_t = H * (15 - t0) / знаменатель = {H:.2f} * (15 - {t0:.2f}) / {denominator:.4f} = {ΔH_t:.2f} м\n"
               f"7. Искомая высота (до округления): H_преп + МЗВ + ΔH_t = {H_prep:.2f} + {MZV} + {ΔH_t:.2f} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 3: относительная МБВ в районе аэродрома (QFE) ==========
def calc_H_MBVra_QFE():
    show_formula("Относительная МБВ в районе аэродрома (QFE)", 
                 "H_МБВраQFE = ΔH_преп + МЗВ + ΔH_t\n"
                 "где ΔH_t – температурная поправка (см. пункт 1)")

    ΔH_prep = input_float("Относительная высота наивысшего препятствия ΔH_преп (м) в радиусе 46 км от КТА + буфер 9 км: ")
    print("Тип местности:")
    print("  1 - Равнинная/холмистая (МЗВ = 300 м)")
    print("  2 - Горная (МЗВ = 600 м)")
    terrain = input_choice("Выберите 1 или 2: ", ["1", "2"])
    MZV = 300 if terrain == "1" else 600
    H = ΔH_prep + MZV

    t_azr = input_float("Минимальная температура на аэродроме t_азр (°C): ")
    H_azr = input_float("Абсолютная высота низшего порога ВПП H_азр (м): ")
    t0 = t_azr + L0 * H_azr

    denominator = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denominator <= 0:
        print("❌ Ошибка: знаменатель формулы температурной поправки <= 0. Проверьте исходные данные.")
        return

    ΔH_t = H * (15 - t0) / denominator
    result = ΔH_prep + MZV + ΔH_t

    details = (f"1. ΔH_преп = {ΔH_prep:.2f} м\n"
               f"2. МЗВ = {MZV} м (местность: {'равнинная/холмистая' if terrain=='1' else 'горная'})\n"
               f"3. H = ΔH_преп + МЗВ = {ΔH_prep:.2f} + {MZV} = {H:.2f} м\n"
               f"4. t0 = t_азр + L0 * H_азр = {t_azr:.2f} + {L0} * {H_azr:.2f} = {t0:.2f} °C\n"
               f"5. Знаменатель: 273 + t0 - 0.5*L0*(H + H_зр) = 273 + {t0:.2f} - 0.5*{L0}*({H:.2f} + {H_azr:.2f}) = {denominator:.4f}\n"
               f"6. Температурная поправка ΔH_t = H * (15 - t0) / знаменатель = {H:.2f} * (15 - {t0:.2f}) / {denominator:.4f} = {ΔH_t:.2f} м\n"
               f"7. Искомая высота (до округления): ΔH_преп + МЗВ + ΔH_t = {ΔH_prep:.2f} + {MZV} + {ΔH_t:.2f} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 4: абсолютная МБВ в районе аэродрома (QNH) ==========
def calc_H_MBVra_QNH():
    show_formula("Абсолютная МБВ в районе аэродрома (QNH)", 
                 "H_МБВраQNH = H_преп + МЗВ + ΔH_t\n"
                 "где ΔH_t – температурная поправка (см. пункт 1)")

    H_prep = input_float("Абсолютная высота наивысшего препятствия H_преп (м) в радиусе 46 км от КТА + буфер 9 км: ")
    print("Тип местности:")
    print("  1 - Равнинная/холмистая (МЗВ = 300 м)")
    print("  2 - Горная (МЗВ = 600 м)")
    terrain = input_choice("Выберите 1 или 2: ", ["1", "2"])
    MZV = 300 if terrain == "1" else 600
    H = H_prep + MZV

    t_azr = input_float("Минимальная температура на аэродроме t_азр (°C): ")
    H_azr = input_float("Абсолютная высота низшего порога ВПП H_азр (м): ")
    t0 = t_azr + L0 * H_azr

    denominator = 273 + t0 - 0.5 * L0 * (H + H_azr)
    if denominator <= 0:
        print("❌ Ошибка: знаменатель формулы температурной поправки <= 0. Проверьте исходные данные.")
        return

    ΔH_t = H * (15 - t0) / denominator
    result = H_prep + MZV + ΔH_t

    details = (f"1. H_преп = {H_prep:.2f} м\n"
               f"2. МЗВ = {MZV} м (местность: {'равнинная/холмистая' if terrain=='1' else 'горная'})\n"
               f"3. H = H_преп + МЗВ = {H_prep:.2f} + {MZV} = {H:.2f} м\n"
               f"4. t0 = t_азр + L0 * H_азр = {t_azr:.2f} + {L0} * {H_azr:.2f} = {t0:.2f} °C\n"
               f"5. Знаменатель: 273 + t0 - 0.5*L0*(H + H_зр) = 273 + {t0:.2f} - 0.5*{L0}*({H:.2f} + {H_azr:.2f}) = {denominator:.4f}\n"
               f"6. Температурная поправка ΔH_t = H * (15 - t0) / знаменатель = {H:.2f} * (15 - {t0:.2f}) / {denominator:.4f} = {ΔH_t:.2f} м\n"
               f"7. Искомая высота (до округления): H_преп + МЗВ + ΔH_t = {H_prep:.2f} + {MZV} + {ΔH_t:.2f} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 6: абсолютная безопасная высота ниже нижнего эшелона (QNH района) ==========
def calc_H_BN_QNH():
    show_formula("Абсолютная безопасная высота ниже нижнего эшелона (QNH района)", 
                 "H_БНQNH = (H_преп + МЗВ) × (285 / (273 + t_3))\n"
                 "где H_преп – абсолютная высота наивысшего препятствия в полосе не менее 16 км (по 8 км в обе стороны)")

    H_prep = input_float("Абсолютная высота наивысшего препятствия H_преп (м): ")
    print("Тип местности:")
    print("  1 - Равнинная/холмистая (МЗВ = 300 м)")
    print("  2 - Горная (МЗВ = 600 м)")
    terrain = input_choice("Выберите 1 или 2: ", ["1", "2"])
    MZV = 300 if terrain == "1" else 600
    t3 = input_float("Наименьшая температура воздуха у земли t3 (°C): ")

    base = H_prep + MZV
    factor = 285 / (273 + t3)
    result = base * factor

    details = (f"1. H_преп = {H_prep:.2f} м\n"
               f"2. МЗВ = {MZV} м (местность: {'равнинная/холмистая' if terrain=='1' else 'горная'})\n"
               f"3. H_преп + МЗВ = {H_prep:.2f} + {MZV} = {base:.2f} м\n"
               f"4. Множитель 285/(273 + t3) = 285 / (273 + {t3:.2f}) = {factor:.4f}\n"
               f"5. Искомая высота (до округления): ({H_prep:.2f} + {MZV}) * {factor:.4f} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 7: нижний безопасный эшелон (QNE) ==========
def calc_H_NE_QNE():
    show_formula("Нижний безопасный эшелон (QNE)", 
                 "H_НЭQNE ≥ (H_преп + МЗВ + ΔH_бар) × (285 / (273 + t_3))\n"
                 "где ΔH_бар = (QNE - QNH_района) × Δh\n"
                 "      Δh: 8.3 м/гПа при QNE=1013.2 гПа, 11 м/мм рт.ст. при QNE=760 мм рт.ст.")

    H_prep = input_float("Абсолютная высота наивысшего препятствия H_преп (м): ")
    MZV = 600  # по документу для п.7 МЗВ = 2000 футов = 600 м

    print("Единицы давления:")
    print("  1 - гПа (QNE = 1013.2)")
    print("  2 - мм рт.ст. (QNE = 760)")
    press_units = input_choice("Выберите 1 или 2: ", ["1", "2"])
    QNH_raiona = input_float("Минимальное давление QNH района: ")

    if press_units == "1":
        delta_h = STEP_HPA
        QNE = QNE_HPA
    else:
        delta_h = STEP_MMHG
        QNE = QNE_MMHG

    delta_H_bar = (QNE - QNH_raiona) * delta_h
    t3 = input_float("Наименьшая температура воздуха у земли t3 (°C): ")

    base = H_prep + MZV + delta_H_bar
    factor = 285 / (273 + t3)
    result = base * factor

    details = (f"1. H_преп = {H_prep:.2f} м\n"
               f"2. МЗВ = {MZV} м (фиксированный для эшелона)\n"
               f"3. ΔH_бар = (QNE - QNH_района) × Δh = ({QNE} - {QNH_raiona}) * {delta_h} = {delta_H_bar:.2f} м\n"
               f"4. H_преп + МЗВ + ΔH_бар = {H_prep:.2f} + {MZV} + {delta_H_bar:.2f} = {base:.2f} м\n"
               f"5. Множитель 285/(273 + t3) = 285 / (273 + {t3:.2f}) = {factor:.4f}\n"
               f"6. Искомая высота эшелона (до округления): {base:.2f} * {factor:.4f} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 9: абсолютная высота перехода района ЕС ОрВД ==========
def calc_H_perekh_ES():
    show_formula("Абсолютная высота перехода района ЕС ОрВД", 
                 "H_перехЕС = (H_преп + 600) × (285 / (273 + t_3))")

    H_prep = input_float("Абсолютная высота наивысшего препятствия H_преп (м): ")
    t3 = input_float("Минимальная температура воздуха у земли t3 (°C): ")

    base = H_prep + 600
    factor = 285 / (273 + t3)
    result = base * factor

    details = (f"1. H_преп = {H_prep:.2f} м\n"
               f"2. МЗВ = 600 м (фиксированный)\n"
               f"3. H_преп + 600 = {base:.2f} м\n"
               f"4. Множитель 285/(273 + t3) = 285 / (273 + {t3:.2f}) = {factor:.4f}\n"
               f"5. Искомая высота (до округления): {base:.2f} * {factor:.4f} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 11: минимальная абсолютная высота в зоне (grid MORA) ==========
def calc_H_Zmin():
    show_formula("Минимальная абсолютная высота в зоне (grid MORA)", 
                 "H_Змин = H_рел + МЗВ")

    H_rel = input_float("Абсолютная высота наивысшего препятствия в ячейке H_рел (м): ")
    print("Тип местности:")
    print("  1 - Равнинная/холмистая (МЗВ = 300 м)")
    print("  2 - Горная (МЗВ = 600 м)")
    terrain = input_choice("Выберите 1 или 2: ", ["1", "2"])
    MZV = 300 if terrain == "1" else 600

    result = H_rel + MZV

    details = (f"1. H_рел = {H_rel:.2f} м\n"
               f"2. МЗВ = {MZV} м (местность: {'равнинная/холмистая' if terrain=='1' else 'горная'})\n"
               f"3. Искомая высота (до округления): {H_rel:.2f} + {MZV} = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 8: высота эшелона перехода в районе аэродрома (упрощённо) ==========
def calc_H_eperekh_airport():
    show_formula("Высота эшелона перехода в районе аэродрома (упрощённо)", 
                 "H_эперехQNH ≥ H_перехQNH + 300\n"
                 "(при условии, что давление QNH аэродрома равно QNE)")

    H_perekh = input_float("Абсолютная высота перехода H_перехQNH (м): ")
    result = H_perekh + 300

    details = (f"1. H_перехQNH = {H_perekh:.2f} м\n"
               f"2. Переходной слой = 300 м (фиксированный)\n"
               f"3. Искомая высота эшелона перехода (до округления): {H_perekh:.2f} + 300 = {result:.2f} м")

    print_result(result, details)

# ========== Пункт 10: высота эшелона перехода в районе ЕС ОрВД ==========
def calc_H_eperekh_ES():
    show_formula("Высота эшелона перехода в районе ЕС ОрВД", 
                 "H_эперехЕС = H_перехЕС + 300\n"
                 "(при условии, что давление QNE)")

    H_perekh_es = input_float("Абсолютная высота перехода района ЕС H_перехЕС (м): ")
    result = H_perekh_es + 300

    details = (f"1. H_перехЕС = {H_perekh_es:.2f} м\n"
               f"2. Переходной слой = 300 м (фиксированный)\n"
               f"3. Искомая высота эшелона перехода (до округления): {H_perekh_es:.2f} + 300 = {result:.2f} м")

    print_result(result, details)

# ========== Главное меню ==========
def main():
    while True:
        print("\n" + "="*70)
        print("          РАСЧЁТ БЕЗОПАСНЫХ ВЫСОТ (ФП ИВП, Приложение №2)")
        print("="*70)
        print("Выберите тип расчёта:")
        print("  1. Относительная МБВ круга полётов (QFE) – п.1")
        print("  2. Абсолютная МБВ круга полётов (QNH) – п.2")
        print("  3. Относительная МБВ в районе аэродрома (QFE) – п.3")
        print("  4. Абсолютная МБВ в районе аэродрома (QNH) – п.4")
        print("  5. Абсолютная безопасная высота ниже нижнего эшелона – п.6")
        print("  6. Нижний безопасный эшелон – п.7")
        print("  7. Абсолютная высота перехода района ЕС ОрВД – п.9")
        print("  8. Минимальная абсолютная высота в зоне (grid MORA) – п.11")
        print("  9. Высота эшелона перехода в районе аэродрома – п.8")
        print(" 10. Высота эшелона перехода в районе ЕС ОрВД – п.10")
        print("  0. Выход")
        print("="*70)

        choice = input("Введите номер пункта (0-10): ").strip()

        if choice == "0":
            print("Выход из программы.")
            break
        elif choice == "1":
            calc_H_MBVk_QFE()
        elif choice == "2":
            calc_H_MBVk_QNH()
        elif choice == "3":
            calc_H_MBVra_QFE()
        elif choice == "4":
            calc_H_MBVra_QNH()
        elif choice == "5":
            calc_H_BN_QNH()
        elif choice == "6":
            calc_H_NE_QNE()
        elif choice == "7":
            calc_H_perekh_ES()
        elif choice == "8":
            calc_H_Zmin()
        elif choice == "9":
            calc_H_eperekh_airport()
        elif choice == "10":
            calc_H_eperekh_ES()
        else:
            print("❌ Неверный выбор. Пожалуйста, введите номер от 0 до 10.")

        input("\nНажмите Enter, чтобы продолжить...")

if __name__ == "__main__":
    main()
