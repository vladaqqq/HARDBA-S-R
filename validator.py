def validate_tables_data(table1_data, table2_data, table3_data):
    errors = []

    # === Проверка заделок ===
    left = table1_data.get("Левая заделка", False)
    right = table1_data.get("Правая заделка", False)

    if not left and not right:
        errors.append("Должна быть установлена хотя бы одна заделка (левая или правая)")

    # === Таблица 'Стержни' — обязательная ===
    bars = table1_data.get("List values", [])
    if not bars:
        errors.append("Таблица 'Стержни' не должна быть пустой")
    else:
        invalid_bars = any(
            (value is None) or (str(value).strip() == "") or (str(value).strip() == "0")
            for row in bars
            for key, value in row.items()
            if key != "barNumber"
        )
        if invalid_bars:
            errors.append("Таблица 'Стержни' не может содержать пустые или нулевые значения")

    bars_count = len(bars)
    if bars_count == 0:
        return errors

    # === Таблица 'Распределенные нагрузки' ===
    dist_loads = table2_data.get("List values", [])
    for i, row in enumerate(dist_loads):
        bar_num_raw = row.get("bar_number", "")
        bar_num_str = str(bar_num_raw).strip()
        if bar_num_str == "" or bar_num_str == "0":
            continue
        try:
            bar_num = int(bar_num_str)
        except ValueError:
            errors.append(
                f"Таблица 'Распределённые нагрузки', строка {i + 1}: номер стержня должен быть числом"
            )
            continue
        if bar_num <= 0 or bar_num > bars_count:
            errors.append(
                f"Таблица 'Распределённые нагрузки', строка {i + 1}: номер стержня {bar_num} некорректен "
                f"(допустимый диапазон: 1–{bars_count})"
            )

    # === Таблица 'Сосредоточенные нагрузки' ===
    conc_loads = table3_data.get("List values", [])
    max_nodes = bars_count + 1
    for i, row in enumerate(conc_loads):
        node_num_raw = row.get("node_number", "")
        node_num_str = str(node_num_raw).strip()
        if node_num_str == "" or node_num_str == "0":
            continue
        try:
            node_num = int(node_num_str)
        except ValueError:
            errors.append(
                f"Таблица 'Сосредоточенные нагрузки', строка {i + 1}: номер узла должен быть числом"
            )
            continue
        if node_num <= 0 or node_num > max_nodes:
            errors.append(
                f"Таблица 'Сосредоточенные нагрузки', строка {i + 1}: номер узла {node_num} некорректен "
                f"(допустимый диапазон: 1–{max_nodes})"
            )

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