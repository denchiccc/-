import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
sys.stdout.reconfigure(encoding='utf-8')

from build123d import *

def build_glass_lock_assembly():
    print("Построение накладного металлического замка для стеклянных дверей (модель 805)...")

    # =========================================================================
    # РАЗМЕРЫ С ЧЕРТЕЖА (мм):
    # Корпус: ширина 48.0 мм, высота 35.0 мм, толщина 6.5 мм, нижние углы R=4 мм
    # Ручка-колокольчик: вылет 19.0 мм, передний диаметр Ø19.0 мм, вогнутость R13
    # Ригель: ширина 17.8 мм, толщина 2.6 мм, вылет 10.0 мм (общая высота с ригелем 45.0 мм)
    # Скоба: L-профиль толщиной 1.5 мм, верхняя полка 8.0 мм, зазор под стекло 9.5 мм
    # Ответная планка: 50.0 х 15.0 х 1.6 мм, паз 20.0 х 4.0 мм, отверстия Ø3 мм (межосевое 38 мм)
    # =========================================================================

    X_WIDTH = 48.0
    Y_HEIGHT = 35.0
    T_BODY = 6.5
    
    # Центр цилиндра и ригеля (по замерам чертежа: 16.0 мм от левого края корпуса)
    X_CENTER = 16.0
    Y_CENTER = 17.5
    
    # Координаты Z для слоев
    Z_VINT_HEAD = 0.0
    Z_SKOBA_BACK = 2.0
    Z_SKOBA_INNER = 3.5    # Толщина скобы 1.5 мм
    Z_GLASS_FRONT = 13.0   # Зазор под стекло 9.5 мм (3.5 .. 13.0)
    Z_BODY_FRONT = 19.5    # Толщина корпуса 6.5 мм (13.0 .. 19.5)
    Z_KNOB_FRONT = 38.5    # Вылет ручки 19.0 мм (19.5 .. 38.5)

    # -------------------------------------------------------------------------
    # 1. Korpus_Zamka (Основной металлический корпус 48х35х6.5 мм)
    # Z = 13.0 .. 19.5 мм. Нижние углы скруглены R=4 мм.
    # -------------------------------------------------------------------------
    with BuildPart() as body_builder:
        # Профиль лицевой панели корпуса замка в плоскости XY
        with BuildSketch(Plane.XY.offset(Z_GLASS_FRONT)) as sk_body:
            with BuildLine():
                Line((0, Y_HEIGHT), (X_WIDTH, Y_HEIGHT))
                Line((X_WIDTH, Y_HEIGHT), (X_WIDTH, 4.0))
                RadiusArc((X_WIDTH, 4.0), (X_WIDTH - 4.0, 0), 4.0)
                Line((X_WIDTH - 4.0, 0), (4.0, 0))
                RadiusArc((4.0, 0), (0, 4.0), 4.0)
                Line((0, 4.0), (0, Y_HEIGHT))
            make_face()

        extrude(sk_body.sketch, amount=T_BODY)

        # Паз под ригель сверху (X_CENTER, Y: 18.0 .. 35.0, Z: 13.0 .. 16.0)
        with Locations(Location((X_CENTER, Y_HEIGHT, Z_GLASS_FRONT + 1.4))):
            Box(18.6, 34.0, 3.0, align=(Align.CENTER, Align.MAX, Align.CENTER), mode=Mode.SUBTRACT)

        # Отверстие под механизм цилиндра (Ø15.0 мм)
        with Locations(Location((X_CENTER, Y_CENTER, Z_GLASS_FRONT))):
            Cylinder(radius=15.0 / 2.0, height=T_BODY + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Небольшая эстетичная фаска 0.4 мм по лицевому периметру
        face_front = body_builder.faces().sort_by(Axis.Z)[-1]
        chamfer(face_front.outer_wire().edges(), length=0.4)

    korpus = body_builder.part
    korpus.label = "Korpus_Zamka"
    korpus.color = Color(0.75, 0.75, 0.78)  # Полированный хром

    # -------------------------------------------------------------------------
    # 2. Ruchka_Kolokolchik (Фигурная поворотная ручка колокольчик R13, вылет 19 мм)
    # Z = 19.5 .. 38.5 мм, ось вращения (X_CENTER, Y_CENTER)
    # Диаметр основания 24.0 мм, передний диаметр Ø19.0 мм
    # -------------------------------------------------------------------------
    with BuildPart() as knob_builder:
        # Сечение колокольчика: локальная ось X - радиус от 0 до r, ось Y - Z координата
        with BuildSketch(Plane.XZ) as sk_knob:
            with Locations(Location((X_CENTER, 0))):
                with BuildLine():
                    p_bot = (0, Z_BODY_FRONT)
                    p1 = (12.0, Z_BODY_FRONT)          # R основания = 12.0 мм (Ø24 мм)
                    p2 = (11.5, Z_BODY_FRONT + 1.5)    # Ступенька фланца
                    
                    # Плавные точки вогнутого колокольчика с радиусом кривизны R13
                    curve_pts = [
                        p2,
                        (9.5, Z_BODY_FRONT + 5.0),
                        (7.0, Z_BODY_FRONT + 11.3),    # Шейка R=7.0 мм (Ø14 мм)
                        (7.8, Z_BODY_FRONT + 15.5),
                        (9.5, Z_KNOB_FRONT)            # Передний торец R=9.5 мм (Ø19 мм)
                    ]
                    p_top = (6.4, Z_KNOB_FRONT)        # Полость под личинку

                    Line(p_bot, p1)
                    Line(p1, p2)
                    Spline(curve_pts)
                    Line((9.5, Z_KNOB_FRONT), p_top)
                    Line(p_top, (6.4, Z_BODY_FRONT + 4.0))
                    Line((6.4, Z_BODY_FRONT + 4.0), (0, Z_BODY_FRONT + 4.0))
                    Line((0, Z_BODY_FRONT + 4.0), p_bot)
                make_face()

        # Вращение вокруг оси Z, проходящей через (X_CENTER, Y_CENTER)
        revolve(sk_knob.sketch.move(Location((0, Y_CENTER, 0))),
                axis=Axis((X_CENTER, Y_CENTER, 0), (0, 0, 1)))

    knob = knob_builder.part
    knob.label = "Ruchka_Kolokolchik"
    knob.color = Color(0.75, 0.75, 0.78)  # Полированный хром

    # -------------------------------------------------------------------------
    # 3. Serdechnik_Lichinka (Сердечник с замочной скважиной)
    # Z = 23.5 .. 38.3 мм (утоплен на 0.2 мм относительно торца ручки)
    # -------------------------------------------------------------------------
    with BuildPart() as lichinka_builder:
        with Locations(Location((X_CENTER, Y_CENTER, Z_BODY_FRONT + 4.5))):
            Cylinder(radius=12.5 / 2.0, height=14.3, align=(Align.CENTER, Align.CENTER, Align.MIN))

            # Фаска на лицевом торце
            face_l_top = lichinka_builder.faces().sort_by(Axis.Z)[-1]
            chamfer(face_l_top.outer_wire().edge(), length=0.3)

            # Прорезь замочной скважины
            with Locations(Location((0, 0, 14.3))):
                Box(1.5, 7.5, 10.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
                Cylinder(radius=2.6 / 2.0, height=10.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

    serdechnik = lichinka_builder.part
    serdechnik.label = "Serdechnik_Lichinka"
    serdechnik.color = Color(0.70, 0.72, 0.75)  # Никелированная латунь

    # -------------------------------------------------------------------------
    # 4. Rigel_Zapornyy (Выдвижной запорный ригель 17.8х2.6 мм, вылет 10 мм)
    # По оси Y: вылет от Y=35.0 до 45.0 мм (длина в корпусе до 16.0 мм)
    # Z = 13.1 .. 15.7 мм (толщина 2.6 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as rigel_builder:
        # Общая длина ригеля 29.0 мм (от Y = 16.0 до 45.0 мм)
        with Locations(Location((X_CENTER, 30.5, Z_GLASS_FRONT + 1.3))):
            Box(17.8, 29.0, 2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))

            # Скругление/фаска на рабочем конце ригеля
            face_top = rigel_builder.faces().sort_by(Axis.Y)[-1]
            chamfer(face_top.edges().filter_by(Axis.X), length=0.5)

    rigel = rigel_builder.part
    rigel.label = "Rigel_Zapornyy"
    rigel.color = Color(0.80, 0.80, 0.82)  # Шлифованная нержавеющая сталь

    # -------------------------------------------------------------------------
    # 5. Skoba_Zazhimnaya (L-образная прижимная струбцина для стекла толщиной 1.5 мм)
    # Вертикальная стенка: Z = 2.0 .. 3.5 мм, X = 0.0 .. 32.0 мм, Y = 5.0 .. 35.0 мм
    # Верхняя полка: Y = 33.5 .. 35.0 мм, Z = 3.5 .. 11.5 мм (ширина 8.0 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as skoba_builder:
        # Вертикальная пластина струбцины
        with Locations(Location((16.0, 20.0, (Z_SKOBA_BACK + Z_SKOBA_INNER) / 2.0))):
            Box(32.0, 30.0, 1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Верхняя фиксирующая полка L-профиля (ширина 8 мм)
        with Locations(Location((16.0, Y_HEIGHT - 0.75, (Z_SKOBA_INNER + Z_SKOBA_INNER + 8.0) / 2.0))):
            Box(32.0, 1.5, 8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Резьбовое отверстие под зажимной винт М5 по центру струбцины (X_CENTER, Y_CENTER)
        with Locations(Location((X_CENTER, Y_CENTER, Z_SKOBA_BACK - 0.5))):
            Cylinder(radius=5.0 / 2.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    skoba = skoba_builder.part
    skoba.label = "Skoba_Zazhimnaya"
    skoba.color = Color(0.65, 0.67, 0.70)  # Оцинкованная сталь

    # -------------------------------------------------------------------------
    # 6. Vint_Zazhimnoy (Прижимной винт со шлицем и пятаком под стекло)
    # Ось (X_CENTER, Y_CENTER), от Z = 0.0 до Z = 8.5 мм
    # -------------------------------------------------------------------------
    with BuildPart() as vint_builder:
        # Головка винта накатанная Ø8.5 мм, толщина 2.0 мм (Z = 0.0 .. 2.0 мм)
        with Locations(Location((X_CENTER, Y_CENTER, Z_VINT_HEAD))):
            Cylinder(radius=8.5 / 2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Шлиц под плоскую отвертку
            with Locations(Location((0, 0, 1.0))):
                Box(1.2, 9.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Резьбовой стержень М5 длиной 6.0 мм (Z = 2.0 .. 8.0 мм)
        with Locations(Location((X_CENTER, Y_CENTER, Z_SKOBA_BACK))):
            Cylinder(radius=4.8 / 2.0, height=6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Зажимной латунный пятак Ø7.5 мм, толщина 1.5 мм (Z = 8.0 .. 9.5 мм)
        with Locations(Location((X_CENTER, Y_CENTER, Z_SKOBA_BACK + 6.0))):
            Cylinder(radius=7.5 / 2.0, height=1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

    vint = vint_builder.part
    vint.label = "Vint_Zazhimnoy"
    vint.color = Color(0.72, 0.72, 0.75)  # Стальной винт

    # -------------------------------------------------------------------------
    # 7. Prokladka_Zashchitnaya (Защитная пластиковая прокладка под стекло)
    # Z = 11.8 .. 13.0 мм (толщина 1.2 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as pad_builder:
        with Locations(Location((16.0, 20.0, Z_GLASS_FRONT - 0.6))):
            Box(30.0, 26.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    prokladka = pad_builder.part
    prokladka.label = "Prokladka_Zashchitnaya"
    prokladka.color = Color(0.20, 0.20, 0.20)  # Черный эластичный полимер

    # -------------------------------------------------------------------------
    # 8. Otvetnaya_Planka (Ответная планка 50х15х1.6 мм с пазом 20х4 мм)
    # Расположена в рабочем зацеплении над ригелем: Y = 43.4 .. 45.0 мм
    # Паз 20х4 мм строго отцентрирован по ригелю (X_CENTER)
    # -------------------------------------------------------------------------
    with BuildPart() as strike_builder:
        z_strike_mid = Z_GLASS_FRONT + 1.3
        # Центрируем по X_CENTER и z_strike_mid
        with Locations(Location((X_CENTER, 44.2, z_strike_mid))):
            with BuildSketch(Plane.XZ) as sk_strike:
                RectangleRounded(50.0, 15.0, radius=2.0)
            extrude(sk_strike.sketch, amount=1.6, both=True)

            # Центральный паз под ригель 20.0 х 4.0 мм
            Box(20.0, 3.5, 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

            # Два монтажных отверстия Ø3.0 мм с межцентровым 38.0 мм и зенковкой
            for dx_hole in [-19.0, 19.0]:
                with Locations(Location((dx_hole, 0, 0))):
                    Cylinder(radius=3.0 / 2.0, height=3.5, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
                    # Зенковка Ø5.5 мм
                    with Locations(Location((0, 0.8, 0))):
                        Cone(bottom_radius=5.5 / 2.0, top_radius=3.0 / 2.0, height=1.25,
                             align=(Align.CENTER, Align.MAX, Align.CENTER), mode=Mode.SUBTRACT)

    otvetka = strike_builder.part
    otvetka.label = "Otvetnaya_Planka"
    otvetka.color = Color(0.75, 0.75, 0.78)  # Хромированная сталь

    # =========================================================================
    # ВЫРАВНИВАНИЕ ПО ГАБАРИТНОЙ РАМКЕ БАЗИС-МЕБЕЛЬЩИКА
    # Базис требует:
    #   X: 0 .. Width (или симметрично)
    #   Y: 0 .. Height (основание строго на Y = 0)
    #   Z: 0 .. Depth  (задняя плоскость строго на Z = 0)
    # =========================================================================
    parts_list = [
        korpus,
        knob,
        serdechnik,
        rigel,
        skoba,
        vint,
        prokladka,
        otvetka
    ]

    # Вычисляем общий bounding box до выравнивания
    temp_compound = Compound(children=parts_list)
    raw_bb = temp_compound.bounding_box()

    shift_x = -raw_bb.min.X
    shift_y = -raw_bb.min.Y
    shift_z = -raw_bb.min.Z

    aligned_parts = []
    for p in parts_list:
        p_aligned = p.move(Location((shift_x, shift_y, shift_z)))
        p_aligned.label = p.label
        p_aligned.color = p.color
        aligned_parts.append(p_aligned)

    # -------------------------------------------------------------------------
    # СБОРКА И ЭКСПОРТ В STEP
    # -------------------------------------------------------------------------
    print("Формирование иерархии сборки...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=aligned_parts
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "glass_door_lock_805.step"

    print(f"Экспорт сборки в {step_file}...")
    export_step(assembly, str(step_file))

    bbox = assembly.bounding_box()
    dx = round(bbox.size.X, 2)
    dy = round(bbox.size.Y, 2)
    dz = round(bbox.size.Z, 2)

    min_x, max_x = round(bbox.min.X, 2), round(bbox.max.X, 2)
    min_y, max_y = round(bbox.min.Y, 2), round(bbox.max.Y, 2)
    min_z, max_z = round(bbox.min.Z, 2), round(bbox.max.Z, 2)

    print(f"\n✅ Файл успешно создан: {step_file.resolve()}")
    print(f"Габариты сборки: X={dx} мм, Y={dy} мм, Z={dz} мм")
    print(f"Диапазоны осей: X=[{min_x}..{max_x}], Y=[{min_y}..{max_y}], Z=[{min_z}..{max_z}]")
    print("Состав сборки:")
    for child in assembly.children:
        c = getattr(child, 'color', None)
        rgb_str = f"RGB{tuple(round(v, 2) for v in tuple(c)[:3])}" if c else "None"
        print(f"  - {child.label}: {rgb_str}")

if __name__ == "__main__":
    build_glass_lock_assembly()
