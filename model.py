from random import random
from math import factorial, log

servers = []  # список серверов


def modeling(params: dict):
    """Основной алгоритм моделирования ВС"""

    global tz_max, tz_min, ts_min, ts_max, lamb, nu

    if params["mode"] == "Линейный":
        tz_min = params["tz_min"]
        tz_max = params["tz_max"]
        ts_min = params["ts_min"]
        ts_max = params["ts_max"]
        lamb = pow((tz_min + tz_max) / 2, -1)
        nu = pow((ts_min + ts_max) / 2, -1)

    else:
        t_obr = params["t_obr"]
        lamb = params["lambda"]
        nu = 1 / t_obr

    programs = []  # список, в котором будут храниться интервалы прихода заявок
    total = 0  # время работы ВС
    reject_count = 0  # количество необработанных заявок
    p0 = 0  # вероятность, что ВС не загружена
    p1 = 0  # вероятность, что загружен 1 сервер
    p2 = 0  # вероятность, что загружено 2 сервера
    programs_times = [0]  # список, который хранит время прихода и завершения заявки

    for _ in range(2):
        servers.append({
            "requests": [],  # список, который хранит завяки, обработанные сервером
            "last_request_time": 0,  # время последней обработанной заявки на сервере
            "is_busy": None,  # занят ли сервер
            "downtime": 0  # время простоя сервера
        })

    while total <= 3600:
        rand = random()  # случайное число в интервале [0 - 1)

        if params["mode"] == "Линейный":
            req_arrival_interval = (tz_max - tz_min) * rand + tz_min  # временной интервал, через который придет заявка
            req_processing_time = (ts_max - ts_min) * rand + ts_min  # время обработки заявки

        else:
            req_arrival_interval = -log(rand) / lamb
            req_processing_time = -log(rand) / nu

        actual_time = total + req_arrival_interval  # фактическое время прихода заявки в ВС

        if actual_time <= 3600:  # если время прихода заявки в ВС не больше времени, которое мы моделируем,
            programs.append({  # то добавляем текущую заявку в список
                "arrival_time": actual_time,
                "processing_time": req_processing_time
            })

        total = actual_time  # обновляем время работы ВС

    for p in range(len(programs)):  # цикл по заявкам
        for s in range(len(servers)):  # цикл по серверам

            arr_time = programs[p]["arrival_time"]
            end_proc = arr_time + programs[p]["processing_time"]

            if arr_time > servers[s]["last_request_time"]:  # если сервер свободен, расчёт вероятностей и обработка
                programs_times.extend([arr_time, end_proc])  # заявки
                programs_times.sort()
                flag = programs_times.index(arr_time)

                while flag != 0:

                    if is_busy_amount(programs_times[1]) == 0:
                        p0 += programs_times[1] - programs_times[0]
                    elif is_busy_amount(programs_times[1]) == 1:
                        p1 += programs_times[1] - programs_times[0]
                    elif is_busy_amount(programs_times[1]) == 2:
                        p2 += programs_times[1] - programs_times[0]

                    programs_times.pop(0)
                    flag = programs_times.index(arr_time)

                servers[s]["is_busy"] = False  # обновляем флаг
                servers[s]["downtime"] += arr_time - servers[s]["last_request_time"]  # обновляем время простоя сервера
                servers[s]["requests"].append(programs[p])  # добавляем заявку в список
                servers[s]["last_request_time"] = end_proc  # рассчитываем время обработки заявки на сервере
                break  # выходим из цикла, чтобы перейти к следующей заявке

            else:  # если сервер занят
                servers[s]["is_busy"] = True  # обновляем флаг

        if servers[0]["is_busy"] and servers[1]["is_busy"]:  # если оба сервера заняты
            reject_count += 1  # заявка покидает ВС необработанной

    t_p0, t_p1, t_p2, t_q, t_s, t_k, t_p_otk = theory_characteristics(lamb, nu)

    p_otk = reject_count / len(programs)  # вероятность отказа, т.е. того, что программа будет не обработанной
    q = 1 - p_otk  # относительная пропускная способность ВС – средняя доля программ, обработанных ВС
    s = lamb * q  # абсолютная пропускная способность – среднее число программ, обработанных в единицу времени

    return len(servers[0]["requests"]), len(servers[1]["requests"]), reject_count, len(programs), \
        servers[0]["downtime"], servers[1]["downtime"], p0 / total, p1 / total, p2 / total, \
        p_otk, q, s, t_p0, t_p1, t_p2, t_q, t_s, t_k, t_p_otk, params["mode"]


def theory_characteristics(lamb, nu):
    """Расчёт теоретических характеристик СМО"""

    ro = lamb / nu
    p0 = 0

    for k in range(len(servers) + 1):
        p0 += pow(ro, k) / factorial(k)

    p0 = pow(p0, -1)
    p1 = pow(ro, 1) * p0 / factorial(1)
    p2 = pow(ro, 2) * p0 / factorial(2)
    p_otk = pow(ro, 2) * p0 / factorial(2)
    q = 1 - p_otk
    s = lamb * q
    k = 0 * p0 + 1 * p1 + 2 * p2  # среднее число занятых серверов.

    return p0, p1, p2, q, s, k, p_otk


def is_busy_amount(program_time, counter=0):
    """Функция, возвращающая количество занятых серверов"""

    for i in range(len(servers)):
        if program_time <= servers[i]["last_request_time"]:
            counter += 1

    return counter
