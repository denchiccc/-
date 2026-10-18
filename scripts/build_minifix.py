import math
from pathlib import Path
from build123d import *

def build_minifix_assembly():
    print("Построение мебельной стяжки Minifix 15...")

    # =========================================================================
    # РАЗМЕРЫ С ЧЕРТЕЖА HAFELE MINIFIX 15 (мм)
    # =========================================================================
    # Эксцентрик: Ø15 мм, высота 12 мм, ось штока на глубине 7.5 мм от пласти
    # Шток: общая длина 44 мм, сверление до центра 34 мм, резьба 11 мм (Ø6.1 мм)
    # Буртик штока: Ø7.8 мм на стыке деталей (X = 34.0)
    # Пластиковая направляющая муфта: Ø7.5 мм, длина 20 мм (красная)
    # Заглушка: Ø17 мм, толщина 1.2 мм
    # =========================================================================

    # -------------------------------------------------------------------------
    # 1. Minifiks_Ekstsentrik (Корпус эксцентрика Ø15х12 мм, цинковый сплав)
    # -------------------------------------------------------------------------
    with BuildPart() as ek_builder:
        # Базовый цилиндр Ø15 мм, Z от 0 до -12 мм
        Cylinder(radius=15.0 / 2.0, height=12.0, align=(Align.CENTER, Align.CENTER, Align.MAX))

        # Верхний крестообразный шлиц PZ2 со стрелкой-указателем (Z = 0 .. -3.2 мм)
        with Locations(Location((0, 0, 0))):
            Box(9.5, 1.8, 3.2, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
            Box(1.8, 9.5, 3.2, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
            Cylinder(radius=2.2, height=3.5, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
            
            # Треугольная стрелка-указатель направления затяжки на лицевой грани
            with Locations(Location((0, -5.5, 0))):
                with BuildSketch(Plane.XY) as sk_arrow:
                    Triangle(a=2.5, b=2.5, C=60)
                extrude(sk_arrow.sketch, amount=-0.8, mode=Mode.SUBTRACT)

        # Боковое приемное окно и спиральная камера под головку штока
        # Ось штока лежит на Z = -7.5 мм вдоль оси X
        loc_dowel_axis = Location((0, 0, -7.5)) * Rotation(0, 90, 0)
        
        # Входной боковой канал под шток (Ø7.6 мм) с лицевой стороны X > 0
        with Locations(Location((4.0, 0, -7.5)) * Rotation(0, 90, 0)):
            Cylinder(radius=7.6 / 2.0, height=8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Внутренняя полость под захват головки штока Ø7 мм
        with Locations(Location((0.5, 0, -7.5))):
            Cylinder(radius=8.5 / 2.0, height=7.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Боковой спиральный сектор (клиновой скос затяжки эксцентрика)
        with Locations(Location((0, 0, -7.5))):
            with BuildSketch(Plane.XY) as sk_ramp:
                Circle(radius=8.0)
                Rectangle(16.0, 16.0, align=(Align.MIN, Align.CENTER), mode=Mode.INTERSECT)
            extrude(sk_ramp.sketch, amount=3.2, mode=Mode.SUBTRACT)

    ekscentrik = ek_builder.part
    ekscentrik.label = "Minifiks_Ekstsentrik"
    ekscentrik.color = Color(0.60, 0.62, 0.65)  # Цинковый сплав Zamak

    # -------------------------------------------------------------------------
    # 2. Minifiks_Shtok_Stal (Стальной силовой шток дюбеля, L = 44 мм)
    # -------------------------------------------------------------------------
    # Ось штока направлена вдоль оси +X, Z = -7.5 мм
    # Стык плит находится на X = 34.0 мм
    with BuildPart() as shtok_builder:
        # Головка штока Ø7.0 мм (X = 1.0 .. 4.5 мм)
        with Locations(Location((1.0, 0, -7.5)) * Rotation(0, 90, 0)):
            Cylinder(radius=7.0 / 2.0, height=3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Шейка зацепления эксцентрика Ø4.8 мм (X = 4.5 .. 13.0 мм)
        with Locations(Location((4.5, 0, -7.5)) * Rotation(0, 90, 0)):
            Cylinder(radius=4.8 / 2.0, height=8.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Сердечник под пластиковую муфту Ø5.0 мм (X = 13.0 .. 33.0 мм)
        with Locations(Location((13.0, 0, -7.5)) * Rotation(0, 90, 0)):
            Cylinder(radius=5.0 / 2.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Опорный буртик Ø7.8 мм, толщина 1.0 мм на линии стыка (X = 33.0 .. 34.0 мм)
        with Locations(Location((33.0, 0, -7.5)) * Rotation(0, 90, 0)):
            Cylinder(radius=7.8 / 2.0, height=1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Резьбовая евро-часть под отверстие Ø5 мм (X = 34.0 .. 45.0 мм, длина 11.0 мм)
        with Locations(Location((34.0, 0, -7.5)) * Rotation(0, 90, 0)):
            # Тело сердечника резьбы Ø4.6 мм
            Cylinder(radius=4.6 / 2.0, height=11.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
            # Витки самонарезающей резьбы наружным диаметром Ø6.1 мм (5 витков)
            for pitch_x in [1.2, 3.4, 5.6, 7.8, 9.8]:
                with Locations(Location((0, 0, pitch_x))):
                    Cylinder(radius=6.1 / 2.0, height=0.9, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    shtok = shtok_builder.part
    shtok.label = "Minifiks_Shtok_Stal"
    shtok.color = Color(0.75, 0.75, 0.78)  # Оцинкованная сталь

    # -------------------------------------------------------------------------
    # 3. Shtok_Plastik_Vtulka (Красная рифленая центрующая муфта Hafele)
    # -------------------------------------------------------------------------
    with BuildPart() as vtulka_builder:
        # Цилиндрическое тело муфты Ø7.5 мм, длина 20 мм (X = 13.0 .. 33.0 мм)
        with Locations(Location((13.0, 0, -7.5)) * Rotation(0, 90, 0)):
            Cylinder(radius=7.2 / 2.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
            # Продольные центрующие ребра (шлицы) наружным диаметром Ø7.6 мм
            for deg in range(0, 360, 45):
                with Locations(Rotation(0, 0, deg)):
                    with Locations(Location((0, 3.6, 10.0))):
                        Box(1.0, 0.8, 19.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    vtulka = vtulka_builder.part
    vtulka.label = "Shtok_Plastik_Vtulka"
    vtulka.color = Color(0.85, 0.15, 0.10)  # Фирменный ярко-красный пластик Hafele

    # -------------------------------------------------------------------------
    # 4. Zaglushka_Plastik (Декоративная крышка Ø17 мм, толщина 1.2 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as cap_builder:
        # Верхняя шляпка заглушки Ø17.0 мм (Z = 0 .. +1.2 мм)
        with Locations(Location((0, 0, 0))):
            Cylinder(radius=17.0 / 2.0, height=1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Скругление верхней кромки шляпки
        top_cap_edge = cap_builder.edges().filter_by(Axis.Z).sort_by(SortBy.LENGTH)[-1]

        # Фиксирующий крестообразный выступ на нижней плоскости (Z = 0 .. -2.2 мм)
        with Locations(Location((0, 0, 0))):
            Box(8.0, 1.5, 2.2, align=(Align.CENTER, Align.CENTER, Align.MAX))
            Box(1.5, 8.0, 2.2, align=(Align.CENTER, Align.CENTER, Align.MAX))

    zaglushka = cap_builder.part
    zaglushka.label = "Zaglushka_Plastik"
    zaglushka.color = Color(0.15, 0.15, 0.15)  # Черный матовый пластик

    # -------------------------------------------------------------------------
    # Сборка и экспорт в STEP
    # -------------------------------------------------------------------------
    print("Формирование иерархии деталей...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[ekscentrik, shtok, vtulka, zaglushka]
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "minifix_15_assembly.step"

    print(f"Экспорт сборки в {step_file}...")
    export_step(assembly, str(step_file))

    bbox = assembly.bounding_box()
    dx = round(bbox.size.X, 1)
    dy = round(bbox.size.Y, 1)
    dz = round(bbox.size.Z, 1)

    print(f"Файл успешно создан: {step_file.resolve()}")
    print(f"Габариты сборки: X={dx} mm, Y={dy} mm, Z={dz} mm")
    print("Состав сборки:")
    for child in assembly.children:
        c = getattr(child, 'color', None)
        print(f"  - {child.label}: {tuple(c)[:3] if c else None}")

if __name__ == "__main__":
    build_minifix_assembly()
