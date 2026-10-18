import math
from pathlib import Path
from build123d import *

def build_atlas_design_double_socket():
    # =========================================================================
    # ГАБАРИТНЫЕ РАЗМЕРЫ С ЧЕРТЕЖА (Systeme Electric AtlasDesign)
    # =========================================================================
    # Длина рамки: 154 мм
    # Высота рамки: 83 мм
    # Полная глубина: 42 мм (10.5 мм выступ рамки + 31.5 мм глубина в подрозетник)
    # Межосевое расстояние (стандарт 2 поста): 71 мм
    # Центры постов: X = -35.5 мм и X = +35.5 мм
    # =========================================================================

    L_frame = 154.0
    H_frame = 83.0
    T_frame = 10.5
    gang_dist = 71.0
    x_left = -gang_dist / 2.0   # -35.5 мм
    x_right = gang_dist / 2.0   # +35.5 мм

    print("Построение 2-постовой розетки AtlasDesign...")

    # -------------------------------------------------------------------------
    # 1. Ramka_2Posta (Декоративная двухпостовая рамка 154х83 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as ramka_builder:
        # Базовый параллелепипед рамки Z = 0 .. 10.5 мм
        with BuildSketch(Plane.XY) as sk_frame:
            RectangleRounded(L_frame, H_frame, radius=2.0)
        extrude(sk_frame.sketch, amount=T_frame)

        # Фаска по внешнему лицевому контуру
        front_face = ramka_builder.faces().sort_by(Axis.Z)[-1]
        
        # Квадратные окна 55.5 x 55.5 мм под накладки механизмов
        for x_c in [x_left, x_right]:
            with Locations(Location((x_c, 0, 0))):
                with BuildSketch(Plane.XY) as sk_cut:
                    RectangleRounded(55.5, 55.5, radius=1.5)
                extrude(sk_cut.sketch, amount=T_frame + 2.0, mode=Mode.SUBTRACT)

    ramka = ramka_builder.part
    ramka.label = "Ramka_2Posta"
    ramka.color = Color(0.15, 0.15, 0.15)  # Матовый черный пластик / софт-тач

    # -------------------------------------------------------------------------
    # Функция построения лицевой накладки розетки Schuko 55x55 мм
    # -------------------------------------------------------------------------
    def make_socket_cover(cx: float, label_name: str) -> Part:
        with BuildPart() as cover_builder:
            # Лицевая квадратная панель 55х55 мм (Z = 0 .. 9.8 мм)
            with Locations(Location((cx, 0, 0))):
                with BuildSketch(Plane.XY) as sk_cov:
                    RectangleRounded(55.0, 55.0, radius=1.2)
                extrude(sk_cov.sketch, amount=9.8)

                # Углубленный круглый колодец под вилку Schuko Ø41.5 мм, глубина 16 мм (до Z = -6.2 мм)
                with Locations(Location((0, 0, 10.0))):
                    Cylinder(radius=41.5 / 2.0, height=16.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

                # Отверстия под штыри вилки Ø5.0 мм (межосевое 19 мм: X = ±9.5 мм)
                for dx in [-9.5, 9.5]:
                    with Locations(Location((dx, 0, -6.0))):
                        Cylinder(radius=5.0 / 2.0, height=8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

                # Пазы под заземляющие скобы сверху и снизу (Y = ±18.0 мм)
                for dy in [-18.5, 18.5]:
                    with Locations(Location((0, dy, -3.0))):
                        Box(5.0, 4.0, 10.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

                # Центральное углубление под крепежный винт лицевой панели
                with Locations(Location((0, 0, -5.5))):
                    Cylinder(radius=6.0 / 2.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        part = cover_builder.part
        part.label = label_name
        part.color = Color(0.15, 0.15, 0.15)
        return part

    # 2. Накладки левой и правой розетки
    nakladka_left = make_socket_cover(x_left, "Nakladka_Rozetka_1")
    nakladka_right = make_socket_cover(x_right, "Nakladka_Rozetka_2")

    # -------------------------------------------------------------------------
    # 4. Kontakty_Zazemleniya (Латунные пружинные контакты заземления Schuko + винты)
    # -------------------------------------------------------------------------
    with BuildPart() as contacts_builder:
        for x_c in [x_left, x_right]:
            # Верхний и нижний контакт заземления
            for dy in [-18.0, 18.0]:
                with Locations(Location((x_c, dy, -2.0))):
                    # Пружинная скоба из латуни
                    Box(4.0, 1.2, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
                    # Загнутый фиксирующий лепесток
                    tip_y = -0.8 if dy > 0 else 0.8
                    with Locations(Location((0, tip_y, 8.0))):
                        Box(4.0, 1.5, 1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))

            # Центральный винт крепления накладки (хромированная головка с шлицем)
            with Locations(Location((x_c, 0, -6.0))):
                Cylinder(radius=5.5 / 2.0, height=1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

    kontakty = contacts_builder.part
    kontakty.label = "Kontakty_Zazemleniya"
    kontakty.color = Color(0.85, 0.65, 0.20)  # Латунь / позолоченные контакты

    # -------------------------------------------------------------------------
    # 5. Support_Metallicheskiy (Сдвоенный стальной монтажный суппорт)
    # -------------------------------------------------------------------------
    with BuildPart() as support_builder:
        # Стальная монтажная пластина 142х71х1.2 мм (Z = -1.2 .. 0.0 мм)
        with Locations(Location((0, 0, -1.2))):
            with BuildSketch(Plane.XY) as sk_sup:
                RectangleRounded(142.0, 71.0, radius=3.0)
            extrude(sk_sup.sketch, amount=1.2)

        # Вырезы под колодцы механизмов Ø52 мм
        for x_c in [x_left, x_right]:
            with Locations(Location((x_c, 0, -2.0))):
                Cylinder(radius=52.0 / 2.0, height=5.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

            # Монтажные прорези под винты подрозетника (шаг 60 мм по вертикали и горизонтали)
            for dy in [-30.0, 30.0]:
                with Locations(Location((x_c, dy, -2.0))):
                    Box(10.0, 3.5, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            for dx in [-30.0, 30.0]:
                with Locations(Location((x_c + dx, 0, -2.0))):
                    Box(3.5, 10.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    support = support_builder.part
    support.label = "Support_Metallicheskiy"
    support.color = Color(0.60, 0.62, 0.65)  # Оцинкованная сталь

    # -------------------------------------------------------------------------
    # 6. Mekhanizm_Korpusa (2 механизма в подрозетники: Z = -1.2 .. -31.5 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as mekhanizm_builder:
        for x_c in [x_left, x_right]:
            # Цилиндрический корпус механизма Ø52 мм, глубина 24 мм (до Z = -25 мм)
            with Locations(Location((x_c, 0, -1.2))):
                Cylinder(radius=50.0 / 2.0, height=24.0, align=(Align.CENTER, Align.CENTER, Align.MAX))

            # Задняя клеммная колодка (Z = -25.0 .. -31.5 мм -> полная глубина 42 мм!)
            with Locations(Location((x_c, 0, -25.0))):
                Box(44.0, 34.0, 6.5, align=(Align.CENTER, Align.CENTER, Align.MAX))

            # Боковые металлические распорные лапки
            for sign in [-1, 1]:
                with Locations(Location((x_c + sign * 25.5, 0, -14.0))):
                    Box(2.5, 14.0, 16.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    mekhanizm = mekhanizm_builder.part
    mekhanizm.label = "Mekhanizm_Korpusa"
    mekhanizm.color = Color(0.90, 0.90, 0.90)  # Белый электротехнический пластик

    # -------------------------------------------------------------------------
    # Сборка и экспорт
    # -------------------------------------------------------------------------
    print("Формирование иерархии сборки...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[ramka, nakladka_left, nakladka_right, kontakty, support, mekhanizm]
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "rozetka_dvoynaya_atlas.step"

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
    build_atlas_design_double_socket()
