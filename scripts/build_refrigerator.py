import math
from pathlib import Path
from build123d import *

def build_builtin_refrigerator():
    print("Построение встраиваемого двухкамерного холодильника...")

    # =========================================================================
    # ГАБАРИТНЫЕ РАЗМЕРЫ (мм) - стандарт под нишу 1773-1780 х 564 х 560 мм
    # =========================================================================
    # Ширина корпуса: 540 мм (в нишу 564 мм с зазорами 12 мм)
    # Глубина корпуса с дверями: 545 мм (корпус 510 мм + двери 35 мм)
    # Полная высота: 1770 мм (в нишу 1773 мм)
    # Высота нижней двери (морозилка): 640 мм (под фасад 696+A мм)
    # Высота верхней двери (холодилка): 1025 мм
    # Межфасадный технологический зазор: 50 мм (Z = 675 .. 725 мм)
    # Регулируемые ножки: 30 мм (Z = 0 .. 30 мм)
    # =========================================================================

    W = 540.0
    D_body = 510.0
    D_door = 35.0
    H_total = 1770.0
    H_feet = 30.0

    # -------------------------------------------------------------------------
    # 1. Korpus_Kholodilnika (Основной теплоизолированный корпус)
    # -------------------------------------------------------------------------
    with BuildPart() as korpus_builder:
        # Основной шкаф холодильника от Z = 30 до 1770 мм
        with Locations(Location((0, D_body / 2.0, H_feet))):
            Box(W, D_body, H_total - H_feet, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Сглаживание вертикальных углов корпуса R8
        # Выбираем углы, параллельные оси Z
        vert_edges = korpus_builder.edges().filter_by(Axis.Z)
        # Скругляем передние углы
        front_vert_edges = vert_edges.sort_by(Axis.Y)[-2:]
        fillet(front_vert_edges, radius=8.0)

        # Задняя ниша под компрессор и вентиляционный канал (Z = 30 .. 240 мм, глубина 170 мм)
        with Locations(Location((0, 85.0, H_feet))):
            Box(W - 40.0, 170.0, 210.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Верхняя вентиляционная планка и декоративный козырек (Z = 1755 .. 1770)
        with Locations(Location((0, D_body - 15.0, 1755.0))):
            Box(W - 20.0, 20.0, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    korpus = korpus_builder.part
    korpus.label = "Korpus_Kholodilnika"
    korpus.color = Color(0.95, 0.95, 0.95)  # Белая глянцевая эмаль

    # -------------------------------------------------------------------------
    # 2. Dver_Morozilnaya (Нижняя дверь морозильной камеры)
    # -------------------------------------------------------------------------
    z_freezer_min = H_feet + 5.0    # Z = 35.0 мм
    h_freezer_door = 640.0          # Z = 35.0 .. 675.0 мм
    w_door = W - 6.0                # 534 мм

    with BuildPart() as freezer_builder:
        # Полотно двери толщиной 35 мм (Y = 510 .. 545 мм)
        with Locations(Location((0, D_body + D_door / 2.0, z_freezer_min))):
            Box(w_door, D_door, h_freezer_door, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Скругление лицевых кромок двери R5 мм
        front_face_freezer = freezer_builder.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
        fillet(front_face_freezer, radius=5.0)

        # Магнитный силиконовый уплотнитель по периметру двери (Y = 502 .. 510 мм)
        with Locations(Location((0, D_body - 4.0, z_freezer_min + 6.0))):
            Box(w_door - 12.0, 8.0, h_freezer_door - 12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    dver_moroz = freezer_builder.part
    dver_moroz.label = "Dver_Morozilnaya"
    dver_moroz.color = Color(0.96, 0.96, 0.96)  # Белый пластик

    # -------------------------------------------------------------------------
    # 3. Dver_Kholodilnaya (Верхняя дверь холодильного отделения)
    # -------------------------------------------------------------------------
    z_fridge_min = 725.0            # Z = 725.0 мм (зазор 50 мм над нижней дверью)
    h_fridge_door = 1025.0          # Z = 725.0 .. 1750.0 мм

    with BuildPart() as fridge_builder:
        with Locations(Location((0, D_body + D_door / 2.0, z_fridge_min))):
            Box(w_door, D_door, h_fridge_door, align=(Align.CENTER, Align.CENTER, Align.MIN))

        front_face_fridge = fridge_builder.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
        fillet(front_face_fridge, radius=5.0)

        # Магнитный уплотнитель по периметру
        with Locations(Location((0, D_body - 4.0, z_fridge_min + 6.0))):
            Box(w_door - 12.0, 8.0, h_fridge_door - 12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    dver_kholod = fridge_builder.part
    dver_kholod.label = "Dver_Kholodilnaya"
    dver_kholod.color = Color(0.96, 0.96, 0.96)  # Белый пластик

    # -------------------------------------------------------------------------
    # 4. Petli_Naveski (Комплект стальных петель: верхняя, средняя, нижняя)
    # -------------------------------------------------------------------------
    # Петли расположены на правом ребре (X = +265 мм)
    with BuildPart() as petli_builder:
        # Верхняя петля (Z = 1750 .. 1765 мм)
        with Locations(Location((W / 2.0 - 15.0, D_body + 10.0, 1750.0))):
            Box(25.0, 50.0, 12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations(Location((8.0, 15.0, 6.0))):
                Cylinder(radius=4.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Средняя петля (Z = 675 .. 725 мм)
        with Locations(Location((W / 2.0 - 15.0, D_body + 10.0, 690.0))):
            Box(25.0, 50.0, 16.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations(Location((8.0, 15.0, 8.0))):
                Cylinder(radius=4.0, height=35.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Нижняя петля (Z = 20 .. 35 мм)
        with Locations(Location((W / 2.0 - 15.0, D_body + 10.0, 20.0))):
            Box(25.0, 50.0, 14.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations(Location((8.0, 15.0, 7.0))):
                Cylinder(radius=4.0, height=22.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    petli = petli_builder.part
    petli.label = "Petli_Naveski"
    petli.color = Color(0.75, 0.75, 0.78)  # Оцинкованная сталь / хром

    # -------------------------------------------------------------------------
    # 5. Slaydery_Krepleniya (4 направляющих скользящих слайдера для фасадов)
    # -------------------------------------------------------------------------
    # Расположены на левой стороне дверей для жесткой связки с мебельным фасадом
    slider_z_locs = [
        z_freezer_min + 100.0,      # Нижняя дверь (низ)
        z_freezer_min + 540.0,      # Нижняя дверь (верх)
        z_fridge_min + 120.0,       # Верхняя дверь (низ)
        z_fridge_min + 900.0        # Верхняя дверь (верх)
    ]
    with BuildPart() as sliders_builder:
        for sz in slider_z_locs:
            # Основание слайдера на двери холодильника (X = -245 мм)
            with Locations(Location((-W / 2.0 + 25.0, D_body + D_door + 2.0, sz))):
                Box(45.0, 4.0, 20.0, align=(Align.CENTER, Align.MIN, Align.CENTER))
                # Скользящая пластина-тяга для мебельного фасада
                with Locations(Location((10.0, 4.0, 0))):
                    Box(65.0, 3.0, 14.0, align=(Align.CENTER, Align.MIN, Align.CENTER))

    slaydery = sliders_builder.part
    slaydery.label = "Slaydery_Krepleniya"
    slaydery.color = Color(0.90, 0.90, 0.90)  # Белый прочный конструкционный пластик

    # -------------------------------------------------------------------------
    # 6. Nozhki_Opornye (Регулируемые передние опоры и задние ролики)
    # -------------------------------------------------------------------------
    with BuildPart() as feet_builder:
        # Передние винтовые регулируемые опоры Ø36 мм (X = ±220 мм, Y = 460 мм)
        for fx in [-220.0, 220.0]:
            with Locations(Location((fx, 460.0, 0))):
                Cylinder(radius=36.0 / 2.0, height=18.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations(Location((0, 0, 18.0))):
                    Cylinder(radius=16.0 / 2.0, height=12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Задние транспортировочные ролики/опоры (X = ±220 мм, Y = 60 мм)
        for rx in [-220.0, 220.0]:
            with Locations(Location((rx, 60.0, 0))):
                Box(40.0, 50.0, 30.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    nozhki = feet_builder.part
    nozhki.label = "Nozhki_Opornye"
    nozhki.color = Color(0.60, 0.62, 0.65)  # Металл / оцинковка

    # -------------------------------------------------------------------------
    # Сборка и экспорт в STEP
    # -------------------------------------------------------------------------
    print("Формирование иерархии сборки...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[korpus, dver_moroz, dver_kholod, petli, slaydery, nozhki]
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "kholodilnik_vstraivaemy_177.step"

    print(f"Экспорт модели в {step_file}...")
    export_step(assembly, str(step_file))

    bbox = assembly.bounding_box()
    dx = round(bbox.size.X, 1)
    dy = round(bbox.size.Y, 1)
    dz = round(bbox.size.Z, 1)

    print(f"Файл успешно создан: {step_file.resolve()}")
    print(f"Габариты холодильника: X={dx} mm, Y={dy} mm, Z={dz} mm")
    print("Состав узлов:")
    for child in assembly.children:
        c = getattr(child, 'color', None)
        print(f"  - {child.label}: {tuple(c)[:3] if c else None}")

if __name__ == "__main__":
    build_builtin_refrigerator()
