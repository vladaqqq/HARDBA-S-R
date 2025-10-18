def validate_tables_data(table1_data, table2_data, table3_data):
    errors = []

    #проверка количества стержней
    bars_count = len(table1_data["List values"])
    if bars_count == 0:
        errors.append("Таблица 'Стержни' не должна быть пустой")
        return errors  # Прерываем если нет стержней

    #проверка номеров стержней в распределенных нагрузках
    for i, row_data in enumerate(table2_data["List values"]):
        bar_num_str = row_data.get("bar_number", "0")
        bar_num = int(bar_num_str)
        if bar_num > bars_count:
            errors.append(
                f"Строка {i + 1} распределенных нагрузок: номер стержня {bar_num} "
                f"превышает количество стержней ({bars_count})")

    #проверка номеров узлов в сосредоточенных нагрузках
    max_nodes = bars_count + 1
    for i, row_data in enumerate(table3_data["List values"]):
        node_num_str = row_data.get("node_number", "0")
        node_num = int(node_num_str)
        if node_num > max_nodes:
            errors.append(
                f"Строка {i + 1} сосредоточенных нагрузок: номер узла {node_num} "
                f"превышает максимально возможный ({max_nodes})")

    return errors


def validate_tables_data_on_open(table1_data, table2_data, table3_data):
    errors = []

    #проверка наличия данных
    if not table1_data or "List values" not in table1_data:
        errors.append("Отсутствуют данные таблицы 'Стержни'")
        return errors

    if not table2_data or "List values" not in table2_data:
        errors.append("Отсутствуют данные таблицы 'Распределенные нагрузки'")
        return errors

    if not table3_data or "List values" not in table3_data:
        errors.append("Отсутствуют данные таблицы 'Сосредтотченные нагрузки'")
        return errors

    #проверка количества стержней
    bars_count = len(table1_data["List values"])
    if bars_count == 0:
        errors.append("Таблица 'Стержни' не должна быть пустой")
        return errors

    #проверка номеров стержней в распределенных нагрузках
    for i, row_data in enumerate(table2_data["List values"]):
        bar_num_str = row_data.get("bar_number", "0")
        bar_num = int(bar_num_str)
        if bar_num > bars_count:
            errors.append(
                f"Строка {i + 1} распределенных нагрузок: номер стержня {bar_num} "
                f"превышает количество стержней ({bars_count})")
        if bar_num < 0:
            errors.append(
                f"Строка {i + 1} распределенных нагрузок: номер стержня '{bar_num}' "
                f"не может быть отрицательным")

    #проверка номеров узлов в сосредоточенных нагрузках
    max_nodes = bars_count + 1
    for i, row_data in enumerate(table3_data["List values"]):
        node_num_str = row_data.get("node_number", "0")
        node_num = int(node_num_str)
        if node_num > max_nodes:
            errors.append(
                f"Строка {i + 1} сосредоточенных нагрузок: номер узла '{node_num}' "
                f"превышает максимально возможный ({max_nodes})")
        if node_num < 0:
             errors.append(
                f"Строка {i + 1} сосредоточенных нагрузок: номер узла {node_num} "
                f"не может быть отрицательным")

    for i, row_data in enumerate(table1_data["List values"]):
        bar_num = i + 1

        # Длина
        length_str = row_data.get("lenght", "0")
        length = float(length_str)
        if length <= 0:
            errors.append(f"Стержень {bar_num}: длина должна быть положительной")

        # Площадь сечения
        area_str = row_data.get("cross_section", "0")
        area = float(area_str)
        if area < 0:
            errors.append(f"Стержень {bar_num}: площадь сечения не может быть отрицательной")

        # Модуль упругости
        modulus_str = row_data.get("modulus_of_elasticity", "0")
        modulus = float(modulus_str)
        if modulus < 0:
            errors.append(f"Стержень {bar_num}: модуль упругости не может быть отрицательным")

        # Напряжение
        pressure_str = row_data.get("pressure", "0")
        pressure = float(pressure_str)
        if pressure < 0:
            errors.append(f"Стержень {bar_num}: напряжение не может быть отрицательным")
    return errors