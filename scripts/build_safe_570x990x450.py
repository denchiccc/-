"""
Скрипт генерации 3D-модели металлического взломостойкого сейфа
с внешними габаритами: Ширина 570 мм, Высота 990 мм, Глубина 450 мм
для САПР «Базис-Мебельщик».

Строго соблюдает правила ориентации по осям Базиса:
  X — Ширина (0.0 .. 570.0 мм)
  Y — Высота (0.0 .. 990.0 мм, основание лежит строго на плоскости пола Y = 0.0)
  Z — Глубина (0.0 .. 450.0 мм, задняя стенка на Z = 0.0, выступающий штурвал на Z = 450.0 мм)
"""
import os
import math
import build123d as bd

# Габаритные размеры по ТЗ:
WIDTH = 570.0    # X
HEIGHT = 990.0   # Y
DEPTH = 450.0    # Z (по выступающему штурвалу)
BODY_DEPTH = 415.0 # Z корпуса

# Цветовая палитра:
COLOR_BODY_GRAPHITE = bd.Color(0.28, 0.29, 0.31)   # Графитовый муар корпуса
COLOR_DOOR_ANTHRACITE = bd.Color(0.33, 0.34, 0.36) # Антрацит дверного полотна
COLOR_BLACK_PLASTIC = bd.Color(0.15, 0.15, 0.15)   # Черный пластик клавиатуры замка
COLOR_CHROME = bd.Color(0.80, 0.80, 0.83)          # Хромированная полированная сталь
COLOR_STEEL = bd.Color(0.65, 0.65, 0.68)           # Оцинкованная сталь (полки, опоры)
COLOR_GOLD = bd.Color(0.85, 0.68, 0.22)            # Латунь / золото (сертификационный шильдик)

def create_safe():
    # -------------------------------------------------------------------------
    # 1. КОРПУС СЕЙФА (Korpus)
    # Габариты корпуса:
    #   X in [0.0 .. 570.0]
    #   Y in [0.0 .. 990.0]
    #   Z in [0.0 .. 415.0]
    # Толщина стенок: 45 мм.
    # Внутренняя камера: X in [45 .. 525], Y in [45 .. 945], Z in [45 .. 415]
    # -------------------------------------------------------------------------
    outer_box = bd.Box(WIDTH, HEIGHT, BODY_DEPTH, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN))
    
    # Внутренняя камера (полость)
    chamber_box = bd.Box(
        WIDTH - 90.0,
        HEIGHT - 90.0,
        BODY_DEPTH - 45.0 + 1.0, # сквозной проем спереди
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)
    ).move(bd.Location((45.0, 45.0, 45.0)))

    # Уступ притвора по периметру двери (ступенчатая защитная четверть):
    # Коробка притвора под дверь толщиной 40 мм (Z in [375.0 .. 416.0])
    # Ширина проема двери: X in [47.5 .. 522.5], Y in [47.5 .. 942.5]
    korpus_solid = outer_box - chamber_box

    # Скруглим внешние вертикальные ребра корпуса R = 4 мм для эстетики
    try:
        vert_edges = korpus_solid.edges().filter_by(bd.Axis.Z).filter_by(
            lambda e: e.bounding_box().min.X < 5 or e.bounding_box().max.X > WIDTH - 5
        )
        korpus_solid = bd.fillet(vert_edges, radius=4.0)
    except Exception:
        pass

    korpus_part = bd.Part(korpus_solid.wrapped)
    korpus_part.label = "Korpus"
    korpus_part.color = COLOR_BODY_GRAPHITE

    # -------------------------------------------------------------------------
    # 2. МАССИВНАЯ ДВЕРЬ СЕЙФА (Dver)
    # Полотно двери:
    #   X in [48.0 .. 522.0] (ширина 474 мм)
    #   Y in [48.0 .. 942.0] (высота 894 мм)
    #   Z in [375.0 .. 415.0] (толщина 40 мм)
    # Зазор 3 мм по периметру
    # -------------------------------------------------------------------------
    door_box = bd.Box(
        474.0, 894.0, 40.0,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)
    ).move(bd.Location((48.0, 48.0, 375.0)))

    # Небольшая фаска по контуру лицевой панели двери
    try:
        front_face_d = door_box.faces().filter_by(bd.Axis.Z).sort_by(bd.Axis.Z)[-1]
        door_box = bd.chamfer(front_face_d.edges(), length=2.0)
    except Exception:
        pass

    door_part = bd.Part(door_box.wrapped)
    door_part.label = "Dver"
    door_part.color = COLOR_DOOR_ANTHRACITE

    # -------------------------------------------------------------------------
    # 3. ЭЛЕКТРОННЫЙ КОДОВЫЙ ЗАМОК (Zamok_Elektronny)
    # Расположен в верхней половине двери:
    # Центр: X = 285.0 мм, Y = 660.0 мм
    # Корпус замка: Z in [415.0 .. 430.0]
    # -------------------------------------------------------------------------
    lock_housing = bd.Box(
        90.0, 130.0, 14.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).move(bd.Location((285.0, 660.0, 415.0)))
    try:
        lock_housing = bd.fillet(lock_housing.edges().filter_by(bd.Axis.Z), radius=10.0)
    except Exception:
        pass

    # Хромированная рамка дисплея / окантовка
    lock_bezel = bd.Box(
        78.0, 118.0, 2.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).move(bd.Location((285.0, 660.0, 429.0)))

    # Кнопки клавиатуры (3х4 матрица)
    keypad_buttons = []
    for row in range(4):
        for col in range(3):
            bx = 285.0 + (col - 1) * 18.0
            by = 640.0 + (1.5 - row) * 16.0
            btn = bd.Cylinder(radius=4.5, height=2.0).move(bd.Location((bx, by, 430.0)))
            keypad_buttons.append(btn)

    # Индикаторные светодиоды сверху
    led1 = bd.Cylinder(radius=2.0, height=2.0).move(bd.Location((270.0, 705.0, 430.0)))
    led2 = bd.Cylinder(radius=2.0, height=2.0).move(bd.Location((300.0, 705.0, 430.0)))

    lock_solid = lock_housing + lock_bezel
    for btn in keypad_buttons:
        lock_solid = lock_solid + btn
    lock_solid = lock_solid + led1 + led2

    lock_part = bd.Part(lock_solid.wrapped)
    lock_part.label = "Zamok_Elektronny"
    lock_part.color = COLOR_BLACK_PLASTIC

    # -------------------------------------------------------------------------
    # 4. ПОВОРОТНЫЙ ШТУРВАЛ РИГЕЛЬНОЙ СИСТЕМЫ (Ruchka_Rigeley)
    # Центр: X = 285.0 мм, Y = 480.0 мм
    # Ступица D=45 мм, Z in [415.0 .. 435.0]
    # 3 луча со сферическими наконечниками, вылет ровно до Z = 450.0 мм!
    # -------------------------------------------------------------------------
    CX = 285.0
    CY = 480.0

    hub_base = bd.Cylinder(radius=22.5, height=20.0).move(bd.Location((CX, CY, 425.0)))
    hub_cap = bd.Cylinder(radius=18.0, height=10.0).move(bd.Location((CX, CY, 440.0)))
    handle_solid = hub_base + hub_cap

    R_spoke = 65.0
    for angle_deg in [90.0, 210.0, 330.0]:
        rad = math.radians(angle_deg)
        dx = math.cos(rad)
        dy = math.sin(rad)
        
        # Шарик на конце луча: Z-центр 442, радиус 8 -> максимум Z = 450.0!
        bx = CX + R_spoke * dx
        by = CY + R_spoke * dy
        bz = 442.0
        ball = bd.Sphere(radius=8.0).move(bd.Location((bx, by, bz)))

        # Цилиндрический стержень луча
        mx = CX + (20.0 + R_spoke) / 2.0 * dx
        my = CY + (20.0 + R_spoke) / 2.0 * dy
        mz = 436.0
        rod_len = R_spoke - 20.0
        rod = bd.Cylinder(radius=5.0, height=rod_len).rotate(bd.Axis.Y, 90).rotate(bd.Axis.Z, angle_deg).move(bd.Location((mx, my, mz)))
        handle_solid = handle_solid + rod + ball

    handle_part = bd.Part(handle_solid.wrapped)
    handle_part.label = "Ruchka_Rigeley"
    handle_part.color = COLOR_CHROME

    # -------------------------------------------------------------------------
    # 5. НАРУЖНЫЕ ПЕТЛИ СЕЙФА (Petlya_Verhnyaya, Petlya_Nizhnyaya)
    # Усиленные точеные петли справа:
    # Ось петли: X = 538.0 мм, Z = 415.0 мм, радиус 13 мм (X in [525 .. 551])
    # -------------------------------------------------------------------------
    def make_heavy_hinge(pos_y, label):
        # Нижняя полупетля (к корпусу): высота 38 мм
        barrel_bot = bd.Cylinder(radius=13.0, height=38.0).move(bd.Location((538.0, pos_y - 20.0, 415.0)))
        # Шайба скольжения латунная/стальная: толщина 4 мм
        washer = bd.Cylinder(radius=14.0, height=4.0).move(bd.Location((538.0, pos_y + 1.0, 415.0)))
        # Верхняя полупетля (к двери): высота 38 мм
        barrel_top = bd.Cylinder(radius=13.0, height=38.0).move(bd.Location((538.0, pos_y + 22.0, 415.0)))
        # Приварные пластины к корпусу и двери
        wing_body = bd.Box(16.0, 32.0, 10.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).move(bd.Location((538.0, pos_y - 20.0, 408.0)))
        wing_door = bd.Box(16.0, 32.0, 10.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).move(bd.Location((538.0, pos_y + 22.0, 408.0)))
        
        hinge_solid = barrel_bot + washer + barrel_top + wing_body + wing_door
        p = bd.Part(hinge_solid.wrapped)
        p.label = label
        p.color = COLOR_CHROME
        return p

    petlya_top = make_heavy_hinge(800.0, "Petlya_Verhnyaya")
    petlya_bot = make_heavy_hinge(180.0, "Petlya_Nizhnyaya")

    # -------------------------------------------------------------------------
    # 6. ВНУТРЕННИЙ ТРЕЙЗЕР (Treyzer)
    # Запираемое отделение в верхней части сейфа:
    # Y in [750.0 .. 940.0] (высота 190 мм)
    # X in [50.0 .. 520.0], Z in [50.0 .. 370.0]
    # -------------------------------------------------------------------------
    tr_body = bd.Box(470.0, 190.0, 320.0, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).move(bd.Location((50.0, 750.0, 50.0)))
    tr_void = bd.Box(464.0, 184.0, 317.0, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).move(bd.Location((53.0, 753.0, 50.0)))
    tr_box = tr_body - tr_void

    # Дверца трейзера
    tr_door = bd.Box(460.0, 180.0, 4.0, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).move(bd.Location((55.0, 755.0, 363.0)))
    # Замочек трейзера
    tr_lock = bd.Cylinder(radius=9.0, height=6.0).move(bd.Location((460.0, 845.0, 367.0)))
    tr_keyhole = bd.Box(2.0, 8.0, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).move(bd.Location((460.0, 845.0, 368.0)))

    treyzer_solid = tr_box + tr_door + (tr_lock - tr_keyhole)
    treyzer_part = bd.Part(treyzer_solid.wrapped)
    treyzer_part.label = "Treyzer"
    treyzer_part.color = bd.Color(0.42, 0.43, 0.45)

    # -------------------------------------------------------------------------
    # 7. СЪЕМНЫЕ ПОЛКИ (Polka_1, Polka_2)
    # Металлические полки на полкодержателях
    # -------------------------------------------------------------------------
    polka1 = bd.Box(470.0, 15.0, 315.0, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).move(bd.Location((50.0, 320.0, 50.0)))
    polka1_part = bd.Part(polka1.wrapped)
    polka1_part.label = "Polka_1"
    polka1_part.color = COLOR_STEEL

    polka2 = bd.Box(470.0, 15.0, 315.0, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).move(bd.Location((50.0, 530.0, 50.0)))
    polka2_part = bd.Part(polka2.wrapped)
    polka2_part.label = "Polka_2"
    polka2_part.color = COLOR_STEEL

    # -------------------------------------------------------------------------
    # 8. ОПОРНЫЕ ПЛАСТИНЫ ОСНОВАНИЯ (Nozhki_Opornye)
    # 4 плоские стальные опоры Y in [0.0 .. 5.0]
    # -------------------------------------------------------------------------
    def make_foot(pos_x, pos_z, label):
        plate = bd.Box(60.0, 5.0, 60.0, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).move(bd.Location((pos_x, 0.0, pos_z)))
        p = bd.Part(plate.wrapped)
        p.label = label
        p.color = COLOR_STEEL
        return p

    n1 = make_foot(50.0, 50.0, "Opora_Zadnyaya_Levaya")
    n2 = make_foot(520.0, 50.0, "Opora_Zadnyaya_Pravaya")
    n3 = make_foot(50.0, 365.0, "Opora_Perednyaya_Levaya")
    n4 = make_foot(520.0, 365.0, "Opora_Perednyaya_Pravaya")

    # -------------------------------------------------------------------------
    # 9. СЕРТИФИКАЦИОННЫЙ ШИЛЬДИК (Shildik_Sertifikat)
    # Латунная табличка на двери: X = 285.0, Y = 820.0, Z in [415.0 .. 417.0]
    # -------------------------------------------------------------------------
    shildik = bd.Box(80.0, 25.0, 1.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).move(bd.Location((285.0, 820.0, 415.0)))
    shildik_part = bd.Part(shildik.wrapped)
    shildik_part.label = "Shildik_Sertifikat"
    shildik_part.color = COLOR_GOLD

    # -------------------------------------------------------------------------
    # КОРНЕВАЯ СБОРКА ФУРНИТУРЫ (Furnitura_Assembly)
    # -------------------------------------------------------------------------
    assembly = bd.Compound(
        label="Furnitura_Assembly",
        children=[
            korpus_part,
            door_part,
            lock_part,
            handle_part,
            petlya_top,
            petlya_bot,
            treyzer_part,
            polka1_part,
            polka2_part,
            n1, n2, n3, n4,
            shildik_part
        ]
    )

    return assembly

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    asm = create_safe()

    step_path = "output/safe_570x990x450.step"
    bd.export_step(asm, step_path)
    print(f"Exported STEP to {step_path}")

    # Создаем также стандартное короткое имя
    step_short = "output/safe.step"
    bd.export_step(asm, step_short)
    print(f"Exported STEP to {step_short}")

    bb = asm.bounding_box()
    print("Габариты сборки сейфа:")
    print(f"  X (Ширина): min={bb.min.X:.2f}, max={bb.max.X:.2f}, размер={bb.size.X:.2f} мм")
    print(f"  Y (Высота): min={bb.min.Y:.2f}, max={bb.max.Y:.2f}, размер={bb.size.Y:.2f} мм")
    print(f"  Z (Глубина): min={bb.min.Z:.2f}, max={bb.max.Z:.2f}, размер={bb.size.Z:.2f} мм")

    print("\nДетали сборки:")
    for c in asm.children:
        b = c.bounding_box()
        print(f"  - {c.label:26s}: X=[{b.min.X:.1f}..{b.max.X:.1f}] Y=[{b.min.Y:.1f}..{b.max.Y:.1f}] Z=[{b.min.Z:.1f}..{b.max.Z:.1f}]")
