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

# ========== КОЭФФИЦИЕНТЫ РЕГРЕССИИ ==========
# Нормальный взлёт: полином 2 степени (стабильный)
coeffs_norm = {
    'intercept': 1461.520634,
    'mass': -7.407039,
    'temp': -7.718992,
    'alt': -0.398332,
    'mass2': 0.023179,
    'temp2': 0.148785,
    'alt2': 0.000070,
    'mass_temp': 0.060576,
    'mass_alt': 0.002263,
    'temp_alt': 0.003566,
}

# Продолженный взлёт: полином 3 степени (точный)
coeffs_cont = {
    'intercept': -441.768617,
    'mass': 17.858076,
    'temp': -1.918218,
    'alt': 0.269282,
    'mass2': -0.065985,
    'temp2': -0.061381,
    'alt2': -0.000057,
    'mass_temp': -0.025130,
    'mass_alt': -0.002291,
    'temp_alt': -0.000749,
    'mass3': 0.000103,
    'temp3': 0.003205,
    'alt3': 0.000000,
    'mass2_temp': 0.000158,
    'mass2_alt': 0.000007,
    'temp2_mass': 0.000801,
    'temp2_alt': 0.000089,
    'alt2_mass': 0.000000,
    'alt2_temp': 0.000001,
    'mass_temp_alt': 0.000018,
}

# Прерванный взлёт: полином 3 степени (точный)
coeffs_abort = {
    'intercept': 1414.422454,
    'mass': -1.159001,
    'temp': -5.126535,
    'alt': -0.087734,
    'mass2': 0.013586,
    'temp2': -0.163205,
    'alt2': -0.000062,
    'mass_temp': 0.033130,
    'mass_alt': 0.001183,
    'temp_alt': -0.003183,
    'mass3': -0.000004,
    'temp3': 0.004234,
    'alt3': 0.000000,
    'mass2_temp': 0.000012,
    'mass2_alt': 0.000000,
    'temp2_mass': 0.000938,
    'temp2_alt': 0.000111,
    'alt2_mass': 0.000000,
    'alt2_temp': 0.000001,
    'mass_temp_alt': 0.000026,
}

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
    # ... (та же функция, что и раньше, можно оставить без изменений)
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

# ========== ФУНКЦИИ РАСЧЁТА ==========
def calc_norm(mass, temp, alt):
    c = coeffs_norm
    return (c['intercept'] +
            c['mass'] * mass +
            c['temp'] * temp +
            c['alt'] * alt +
            c['mass2'] * mass * mass +
            c['temp2'] * temp * temp +
            c['alt2'] * alt * alt +
            c['mass_temp'] * mass * temp +
            c['mass_alt'] * mass * alt +
            c['temp_alt'] * temp * alt)

def calc_cont(mass, temp, alt):
    c = coeffs_cont
    return (c['intercept'] +
            c['mass'] * mass +
            c['temp'] * temp +
            c['alt'] * alt +
            c['mass2'] * mass * mass +
            c['temp2'] * temp * temp +
            c['alt2'] * alt * alt +
            c['mass_temp'] * mass * temp +
            c['mass_alt'] * mass * alt +
            c['temp_alt'] * temp * alt +
            c['mass3'] * mass * mass * mass +
            c['temp3'] * temp * temp * temp +
            c['alt3'] * alt * alt * alt +
            c['mass2_temp'] * mass * mass * temp +
            c['mass2_alt'] * mass * mass * alt +
            c['temp2_mass'] * temp * temp * mass +
            c['temp2_alt'] * temp * temp * alt +
            c['alt2_mass'] * alt * alt * mass +
            c['alt2_temp'] * alt * alt * temp +
            c['mass_temp_alt'] * mass * temp * alt)

def calc_abort(mass, temp, alt):
    c = coeffs_abort
    return (c['intercept'] +
            c['mass'] * mass +
            c['temp'] * temp +
            c['alt'] * alt +
            c['mass2'] * mass * mass +
            c['temp2'] * temp * temp +
            c['alt2'] * alt * alt +
            c['mass_temp'] * mass * temp +
            c['mass_alt'] * mass * alt +
            c['temp_alt'] * temp * alt +
            c['mass3'] * mass * mass * mass +
            c['temp3'] * temp * temp * temp +
            c['alt3'] * alt * alt * alt +
            c['mass2_temp'] * mass * mass * temp +
            c['mass2_alt'] * mass * mass * alt +
            c['temp2_mass'] * temp * temp * mass +
            c['temp2_alt'] * temp * temp * alt +
            c['alt2_mass'] * alt * alt * mass +
            c['alt2_temp'] * alt * alt * temp +
            c['mass_temp_alt'] * mass * temp * alt)

def calculate_takeoff(mass, temp, alt, wind, slope, v1, mode):
    wind_corrected = -wind
    if mode == 'norm':
        base = calc_norm(mass, temp, alt)
    elif mode == 'cont':
        base = calc_cont(mass, temp, alt)
    else:
        base = calc_abort(mass, temp, alt)

    wind_factor = get_factor_from_table(mass, wind_corrected, wind_vals, wind_table, mass_vals_corr)
    slope_factor = get_factor_from_table(mass, slope, slope_vals, slope_table, mass_vals_corr)
    result = base * wind_factor * slope_factor

    if mode == 'abort':
        v1_factor = get_factor_from_table(mass, v1, v1_vals, v1_table, mass_vals_corr)
        result *= v1_factor

    return result

# ========== ЭКРАНЫ (интерфейс без изменений) ==========
# ... (весь код экранов из предыдущей версии, он остаётся тем же)
