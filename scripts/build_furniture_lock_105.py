import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
sys.stdout.reconfigure(encoding='utf-8')

from build123d import *

def build_lock_assembly():
    print("Построение мебельного кнопочного замка (GTV №105 / push lock)...")

    # =========================================================================
    # ГАБАРИТЫ И ПРИВЯЗКА К ОСЯМ БАЗИС-МЕБЕЛЬЩИКА:
    # X — Ширина:  19.0 мм (симметрично: от -9.5 до +9.5 мм)
    # Y — Высота:  49.5 мм (от Y = 0.0 на нижнем крае до Y = 49.5 мм на верхнем)
    # Z — Глубина: 38.0 мм (от Z = 0.0 на торце штока до Z = 38.0 мм на лице цилиндра)
    #
    # Центр цилиндра и штока:
    # X = 0.0 мм
    # Y = 49.5 / 2 = 24.75 мм
    # =========================================================================

    Y_MID = 24.75
    HOLE_DIST = 34.0
    Y_HOLE_TOP = Y_MID + HOLE_DIST / 2.0   # 41.75 мм
    Y_HOLE_BOT = Y_MID - HOLE_DIST / 2.0   # 7.75 мм

    # -------------------------------------------------------------------------
    # 1. Planka_Montazhnaya (Монтажная планка / фланец 19х49.5х2 мм)
    # Z = 12.0 .. 14.0 мм
    # На Z = 12.0 мм находятся зенкованные отверстия Ø8.5/Ø4.5 мм под шурупы
    # -------------------------------------------------------------------------
    with BuildPart() as planka_builder:
        # Базовый контур овальной планки (скругление R=9.5 на концах)
        with Locations(Location((0, Y_MID, 12.0))):
            with BuildSketch(Plane.XY) as sk_planka:
                # Центральный прямоугольник
                Rectangle(19.0, 49.5 - 19.0)
                # Верхний и нижний полукруги
                with Locations((0, (49.5 - 19.0) / 2.0)):
                    Circle(radius=9.5)
                with Locations((0, -(49.5 - 19.0) / 2.0)):
                    Circle(radius=9.5)
            extrude(sk_planka.sketch, amount=2.0)

        # Верхнее и нижнее крепежные отверстия (зенковка со стороны Z = 12.0)
        for y_pos in [Y_HOLE_BOT, Y_HOLE_TOP]:
            # Сквозное отверстие Ø4.5 мм
            with Locations(Location((0, y_pos, 11.5))):
                Cylinder(radius=4.5 / 2.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            # Коническая зенковка Ø8.5 мм под 90 градусов (глубина 2.0 мм: от Ø8.5 на Z=12.0 до Ø4.5 на Z=14.0)
            with Locations(Location((0, y_pos, 12.0))):
                Cone(bottom_radius=8.5 / 2.0, top_radius=4.5 / 2.0, height=2.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Центральное технологическое отверстие под цилиндр и шток (Ø18.5 мм)
        with Locations(Location((0, Y_MID, 11.5))):
            Cylinder(radius=18.5 / 2.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    planka = planka_builder.part
    planka.label = "Planka_Montazhnaya"
    planka.color = Color(0.75, 0.75, 0.78)  # Хромированная сталь

    # -------------------------------------------------------------------------
    # 2. Korpus_Tsilindra (Врезной цилиндр замка Ø19х24 мм)
    # Z = 14.0 .. 38.0 мм, ось (0, Y_MID)
    # -------------------------------------------------------------------------
    with BuildPart() as cyl_builder:
        # Основной цилиндр Ø19.0 мм, длина 24.0 мм
        with Locations(Location((0, Y_MID, 14.0))):
            Cylinder(radius=19.0 / 2.0, height=24.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

            # Внутренняя полость под сердечник (Ø13.0 мм, глубина 20 мм от лицевой поверхности Z=38.0)
            with Locations(Location((0, 0, 4.0))):
                Cylinder(radius=13.0 / 2.0, height=20.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

            # Внутреннее отверстие под проход штока (Ø7.5 мм, Z=0..6 мм)
            Cylinder(radius=7.5 / 2.0, height=6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Небольшая фаска на лицевой внешней кромке цилиндра (на Z=38.0)
        face_front = cyl_builder.faces().sort_by(Axis.Z)[-1]
        edge_front = face_front.outer_wire().edge()
        chamfer(edge_front, length=0.4)

    korpus_tsilindra = cyl_builder.part
    korpus_tsilindra.label = "Korpus_Tsilindra"
    korpus_tsilindra.color = Color(0.75, 0.75, 0.78)  # Полированный хром

    # -------------------------------------------------------------------------
    # 3. Serdechnik_Lichinka (Сердечник замка с замочной скважиной)
    # Расположен внутри цилиндра, торец на Z = 37.8 мм
    # -------------------------------------------------------------------------
    with BuildPart() as lichinka_builder:
        # Тело сердечника Ø12.8 мм, длина 18.0 мм (Z = 19.8 .. 37.8 мм)
        with Locations(Location((0, Y_MID, 19.8))):
            Cylinder(radius=12.8 / 2.0, height=18.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

            # Лицевая фаска сердечника
            face_l_front = lichinka_builder.faces().sort_by(Axis.Z)[-1]
            edge_l_front = face_l_front.outer_wire().edge()
            chamfer(edge_l_front, length=0.3)

            # Прорезь замочной скважины на лицевом торце (Z = 37.8 мм)
            # Вертикальная щель 1.6 x 8.0 мм, глубина 12.0 мм
            with Locations(Location((0, 0, 18.0))):
                Box(1.6, 8.0, 12.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
                # Круглое центровочное отверстие скважины Ø3.0 мм
                Cylinder(radius=3.0 / 2.0, height=12.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

    serdechnik = lichinka_builder.part
    serdechnik.label = "Serdechnik_Lichinka"
    serdechnik.color = Color(0.70, 0.72, 0.75)  # Никелированная латунь / ЦАМ

    # -------------------------------------------------------------------------
    # 4. Zapornyy_Shtok (Выдвижной запорный штифт/ригель Ø7 мм, вылет 12 мм)
    # Z = 0.0 .. 12.0 мм (снаружи) + проходит внутрь до Z = 22.0 мм
    # -------------------------------------------------------------------------
    with BuildPart() as shtok_builder:
        # Шток Ø7.0 мм, общая длина 22.0 мм (от Z = 0.0 до Z = 22.0 мм)
        with Locations(Location((0, Y_MID, 0.0))):
            Cylinder(radius=7.0 / 2.0, height=22.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

            # Фаска на рабочем торце штока (Z = 0.0)
            face_tip = shtok_builder.faces().sort_by(Axis.Z)[0]
            edge_tip = face_tip.outer_wire().edge()
            chamfer(edge_tip, length=0.5)

    shtok = shtok_builder.part
    shtok.label = "Zapornyy_Shtok"
    shtok.color = Color(0.80, 0.80, 0.82)  # Полированная нержавеющая сталь

    # -------------------------------------------------------------------------
    # 5. Korpus_Mekhanizma (Задняя штампованная крышка механизма с ушками)
    # Расположена на задней стороне планки: Z = 10.5 .. 12.5 мм
    # Квадратный профиль со скругленными углами 17.5 x 17.5 мм
    # -------------------------------------------------------------------------
    with BuildPart() as mekh_builder:
        with Locations(Location((0, Y_MID, 10.5))):
            # Основание механизма 17.5 x 17.5 мм со скруглением углов
            with BuildSketch(Plane.XY) as sk_mekh:
                RectangleRounded(17.5, 17.5, radius=2.5)
            extrude(sk_mekh.sketch, amount=1.8)

            # Отверстие под выход штока Ø8.5 мм
            Cylinder(radius=8.5 / 2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

            # 4 угловых гнезда под заклепки Ø1.8 мм
            for rx in [-6.5, 6.5]:
                for ry in [-6.5, 6.5]:
                    with Locations(Location((rx, ry, 0))):
                        Cylinder(radius=1.8 / 2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    mekhanizm = mekh_builder.part
    mekhanizm.label = "Korpus_Mekhanizma"
    mekhanizm.color = Color(0.60, 0.62, 0.65)  # Цинковый сплав

    # -------------------------------------------------------------------------
    # 6. Zaklepki_Mekhanizma (4 стальные заклепки крепления механизма)
    # -------------------------------------------------------------------------
    with BuildPart() as rivets_builder:
        for rx in [-6.5, 6.5]:
            for ry in [-6.5, 6.5]:
                with Locations(Location((rx, Y_MID + ry, 10.4))):
                    # Тело заклепки
                    Cylinder(radius=1.6 / 2.0, height=2.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
                    # Полукруглая шляпка заклепки
                    with Locations(Location((0, 0, 0))):
                        Sphere(radius=1.2)

    rivets = rivets_builder.part
    rivets.label = "Zaklepki_Mekhanizma"
    rivets.color = Color(0.72, 0.72, 0.75)  # Стальные заклепки

    # =========================================================================
    # СБОРКА И ЭКСПОРТ В STEP ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    print("Формирование иерархии сборки...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[
            planka,
            korpus_tsilindra,
            serdechnik,
            shtok,
            mekhanizm,
            rivets
        ]
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "furniture_lock_gtv_105.step"

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
    build_lock_assembly()
