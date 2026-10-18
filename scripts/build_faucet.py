import math
from pathlib import Path
from build123d import *

def build_modern_faucet():
    # =========================================================================
    # РАЗМЕРЫ С ЧЕРТЕЖА (мм)
    # =========================================================================
    # Полная высота: 176 мм
    # Высота излива (до аэратора): 117 мм
    # Вылет излива (межосевое до аэратора): 118 мм
    # Диаметр основания: 50 мм
    # Монтажное отверстие: 35 мм
    # Макс. толщина столешницы: 35 мм
    
    print("Создание элементов смесителя...")

    # -------------------------------------------------------------------------
    # 1. Kolco_Osnovaniya (Базовое кольцо Ø50 мм, t=4.5 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as base_builder:
        # Внешний цилиндр Ø50
        Cylinder(radius=50.0 / 2, height=4.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Сквозное отверстие под резьбовую втулку Ø34
        Cylinder(radius=34.0 / 2, height=10.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        # Фаска по верхнему ребру
        top_edge = base_builder.edges().filter_by(Axis.Z).sort_by(SortBy.LENGTH)[-1]
        
    kolco = base_builder.part
    kolco.label = "Kolco_Osnovaniya"
    kolco.color = Color(0.75, 0.75, 0.78)  # Хром / полированная нержавеющая сталь

    # -------------------------------------------------------------------------
    # 2. Smesitel_Korpus (Вертикальный корпус 36x36 мм и горизонтальный излив)
    # -------------------------------------------------------------------------
    # Корпус прямоугольного сечения в стиле модерн с плавными радиусными фасками
    body_w = 36.0
    spout_h = 16.0
    spout_bottom_z = 126.5  # чтобы аэратор высотой 9.5 мм заканчивался ровно на Z = 117
    spout_top_z = spout_bottom_z + spout_h  # 142.5 мм
    body_top_z = 145.0

    with BuildPart() as korpus_builder:
        # Вертикальная стойка корпуса от Z = 4.0 до Z = 145.0
        with Locations(Location((0, 0, 4.0))):
            Box(body_w, body_w, body_top_z - 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Горизонтальный излив от оси X = 0 до носовой части X = 135
        spout_len = 135.0
        with Locations(Location((spout_len / 2.0, 0, spout_bottom_z))):
            Box(spout_len, body_w, spout_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Сглаживание передних вертикальных углов излива R6
        front_edges = korpus_builder.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
        fillet(front_edges, radius=6.0)

        # Верхняя цилиндрическая шейка под картридж Ø34 мм (Z = 145 .. 148)
        with Locations(Location((0, 0, body_top_z))):
            Cylinder(radius=34.0 / 2, height=3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Посадочное гнездо под аэратор снизу излива на X = 118 мм
        with Locations(Location((118.0, 0, spout_bottom_z))):
            Cylinder(radius=24.0 / 2, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    korpus = korpus_builder.part
    korpus.label = "Smesitel_Korpus"
    korpus.color = Color(0.75, 0.75, 0.78)  # Брашированная сталь / сатин-хром

    # -------------------------------------------------------------------------
    # 3. Smesitel_Rychag (Поворотный рычаг управления с тонкой рукоятью)
    # -------------------------------------------------------------------------
    with BuildPart() as rychag_builder:
        # Нижнее кольцо картриджа Ø32 мм (Z = 148.5 .. 152.0)
        with Locations(Location((0, 0, 148.5))):
            Cylinder(radius=32.0 / 2, height=3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Головка рычага (куб 34x34 со скосом) Z = 152.0 .. 172.0
        with Locations(Location((0, 0, 152.0))):
            Box(34.0, 34.0, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Тонкая пластина рукояти (Z = 172.0 .. 176.0 -> верх ровно 176 мм!)
        lever_len = 110.0
        with Locations(Location((lever_len / 2.0 - 15.0, 0, 172.0))):
            Box(lever_len, 34.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Сглаживание передних ребер пластины рычага
        lever_front = rychag_builder.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
        fillet(lever_front, radius=4.0)

    rychag = rychag_builder.part
    rychag.label = "Smesitel_Rychag"
    rychag.color = Color(0.78, 0.78, 0.80)  # Хром / полированный металл

    # -------------------------------------------------------------------------
    # 4. Aerator (Аэратор на носике излива: низ на Z = 117 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as aerator_builder:
        # Корпус аэратора Ø24 мм, высота 8.5 мм (Z = 118.0 .. 126.5)
        with Locations(Location((118.0, 0, 118.0))):
            Cylinder(radius=24.0 / 2, height=8.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Нижний бортик рассекателя Ø22 мм (Z = 117.0 .. 118.0 -> ровно 117 мм снизу!)
        with Locations(Location((118.0, 0, 117.0))):
            Cylinder(radius=22.0 / 2, height=1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Внутренняя сеточка рассекателя
        with Locations(Location((118.0, 0, 117.0))):
            Cylinder(radius=18.0 / 2, height=0.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    aerator = aerator_builder.part
    aerator.label = "Aerator"
    aerator.color = Color(0.82, 0.82, 0.85)  # Хромированное кольцо аэратора

    # -------------------------------------------------------------------------
    # 5. Kreplenie_Geyka (Монтажная резьбовая втулка и цанговая гайка max 35)
    # -------------------------------------------------------------------------
    with BuildPart() as mount_builder:
        # Резьбовой шток Ø32 мм вниз до Z = -55 мм
        with Locations(Location((0, 0, 0))):
            Cylinder(radius=32.0 / 2, height=55.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
            # Внутреннее отверстие под шланги Ø24 мм
            Cylinder(radius=24.0 / 2, height=60.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # Быстрозажимная монтажная гильза/гайка с ребрами захвата (Z = -12 .. -48 мм)
        with Locations(Location((0, 0, -12.0))):
            Cylinder(radius=42.0 / 2, height=36.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
            
        # 6 продольных ребер для ручной затяжки
        for angle in range(0, 360, 60):
            with Locations(Location((0, 0, -30.0)) * Rotation(0, 0, angle)):
                with Locations(Location((22.0, 0, 0))):
                    Box(4.0, 5.0, 32.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Уплотнительная шайба под столешницу Z = 0 .. -3 мм
        with Locations(Location((0, 0, 0))):
            Cylinder(radius=48.0 / 2, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MAX))

    kreplenie = mount_builder.part
    kreplenie.label = "Kreplenie_Geyka"
    kreplenie.color = Color(0.60, 0.62, 0.65)  # Цинковый сплав / сталь

    # -------------------------------------------------------------------------
    # 6. Podvodka_Shlangi (Гибкие шланги 1/2" в металлической оплетке)
    # -------------------------------------------------------------------------
    with BuildPart() as shlangi_builder:
        # Два гибких шланга Ø10 мм вниз до Z = -160 мм
        for dx in [-5.0, 5.0]:
            with Locations(Location((dx, 0, -10.0))):
                Cylinder(radius=10.0 / 2, height=150.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
                # Латунные накидные шестигранные гайки на конце (Z = -160 .. -175)
                with Locations(Location((0, 0, -150.0))):
                    Cylinder(radius=18.0 / 2, height=15.0, align=(Align.CENTER, Align.CENTER, Align.MAX))

    shlangi = shlangi_builder.part
    shlangi.label = "Podvodka_Shlangi"
    shlangi.color = Color(0.70, 0.70, 0.72)  # Стальная оплетка

    # -------------------------------------------------------------------------
    # Сборка узлов и экспорт
    # -------------------------------------------------------------------------
    print("Формирование иерархии деталей...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[kolco, korpus, rychag, aerator, kreplenie, shlangi]
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "smesitel_kuhnya_chrome.step"

    print(f"Экспорт модели в {step_file}...")
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
    build_modern_faucet()
