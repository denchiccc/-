import sys
from pathlib import Path
from build123d import *

def build_kitchen_sink():
    # =========================================================================
    # РАЗМЕРЫ И КООРДИНАТЫ (С ЦЕНТРОМ В 0,0)
    # =========================================================================
    # Габариты: 1000 x 500 мм, глубина 200 мм
    L = 1000.0
    W = 500.0
    H_main = 200.0
    H_small = 140.0
    flange_t = 1.0  # толщина листа
    
    # Смещение относительно левого края чертежа (X = 0..1000 -> X_c = -500..+500)
    # Чертеж:
    # Главная чаша: X = 251.5 (центр слива и чаши), Y = 250
    # X_c = 251.5 - 500 = -248.5
    main_cx = 251.5 - 500.0
    main_cy = 0.0
    main_w = 340.0
    main_l = 420.0
    main_r = 65.0
    
    # Отверстие под смеситель: X = 423 мм -> X_c = 423 - 500 = -77.0 мм
    tap_x = 423.0 - 500.0
    tap_top_y = (500.0 - 45.5) - 250.0  # +204.5 мм
    tap_bot_y = 45.5 - 250.0            # -204.5 мм
    
    # Малая чаша: ширина 170 мм, расположена сразу за перемычкой смесителя
    # На чертеже правее X = 423:
    small_w = 170.0
    small_l = 300.0
    small_cx = -77.0 + 25.0 + (small_w / 2.0)  # ~ +33.0 мм
    small_cy = 0.0
    small_r = 45.0
    
    # Крыло (сушилка): расположено справа от малой чаши до правого борта
    wing_cx = (small_cx + (small_w / 2.0) + 15.0 + 475.0) / 2.0  # ~ 296 мм
    wing_w = 475.0 - (small_cx + (small_w / 2.0) + 15.0)        # ~ 340 мм
    wing_l = 420.0

    print("Построение корпуса мойки...")
    
    # -------------------------------------------------------------------------
    # 1. Moyka_Karkas (Основной корпус: фланец, чаши, крыло)
    # -------------------------------------------------------------------------
    with BuildPart() as karkas_builder:
        # Верхний базовый фланец с закруглением углов R10
        with BuildSketch(Plane.XY) as sk_flange:
            RectangleRounded(L, W, radius=10.0)
        extrude(sk_flange.sketch, amount=flange_t)  # Z от 0 до 1.0
        
        # Отбортовка вниз по наружному периметру (жесткость и герметик)
        with BuildSketch(Plane.XY) as sk_rim:
            RectangleRounded(L, W, radius=10.0)
            RectangleRounded(L - 4.0, W - 4.0, radius=8.0, mode=Mode.SUBTRACT)
        extrude(sk_rim.sketch, amount=-6.0)  # Z от 0 до -6.0

        # Вырез и построение большой чаши (Main Bowl)
        with Locations(Location((main_cx, main_cy, 0))):
            # Внешний объем чаши
            with BuildSketch(Plane.XY) as sk_mb_outer:
                RectangleRounded(main_w + 2 * flange_t, main_l + 2 * flange_t, radius=main_r)
            mb_outer = extrude(sk_mb_outer.sketch, amount=-H_main)
            
            # Внутренний объем чаши
            with BuildSketch(Plane.XY) as sk_mb_inner:
                RectangleRounded(main_w, main_l, radius=main_r - flange_t)
            mb_inner = extrude(sk_mb_inner.sketch, amount=-(H_main - flange_t))
            
            # Дно с уклоном к сливу и отверстие слива Ø118
            with BuildSketch(Plane.XY.offset(-H_main - 2)) as sk_drain1:
                Circle(radius=118.0 / 2.0)
            extrude(sk_drain1.sketch, amount=10.0, mode=Mode.SUBTRACT)

        # Вырез и построение малой чаши (Small Bowl)
        with Locations(Location((small_cx, small_cy, 0))):
            with BuildSketch(Plane.XY) as sk_sb_outer:
                RectangleRounded(small_w + 2 * flange_t, small_l + 2 * flange_t, radius=small_r)
            sb_outer = extrude(sk_sb_outer.sketch, amount=-H_small)
            
            with BuildSketch(Plane.XY) as sk_sb_inner:
                RectangleRounded(small_w, small_l, radius=small_r - flange_t)
            sb_inner = extrude(sk_sb_inner.sketch, amount=-(H_small - flange_t))
            
            with BuildSketch(Plane.XY.offset(-H_small - 2)) as sk_drain2:
                Circle(radius=118.0 / 2.0)
            extrude(sk_drain2.sketch, amount=10.0, mode=Mode.SUBTRACT)

        # Отверстия под смеситель Ø35 мм (сверху и снизу на перемычке)
        with Locations(Location((tap_x, tap_top_y, 5))):
            Cylinder(radius=35.0 / 2.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        with Locations(Location((tap_x, tap_bot_y, 5))):
            Cylinder(radius=35.0 / 2.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Рельефные ребра на крыле сушилки
        with Locations(Location((wing_cx, 0, flange_t))):
            # Углубление крыла (ванночка сушилки)
            with BuildSketch(Plane.XY) as sk_wing_recess:
                RectangleRounded(wing_w, wing_l, radius=15.0)
            extrude(sk_wing_recess.sketch, amount=-1.2, mode=Mode.SUBTRACT)
            
            # Продольные сточные канавки (5 шт с уклоном в малую чашу)
            for dy in [-140.0, -70.0, 0.0, 70.0, 140.0]:
                with Locations(Location((0, dy, -1.2))):
                    Box(wing_w - 40.0, 12.0, 1.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

    karkas = karkas_builder.part
    karkas.label = "Moyka_Karkas"
    karkas.color = Color(0.75, 0.75, 0.78)  # Полированная нержавейка / хром

    # -------------------------------------------------------------------------
    # 2. Sliv_Bolshoy (Сливная арматура / чашка и решетка большой чаши Ø118)
    # -------------------------------------------------------------------------
    print("Построение слива большой чаши...")
    with BuildPart() as sliv1_builder:
        with Locations(Location((main_cx, main_cy, -H_main + flange_t))):
            # Верхний ободок решетки Ø118, толщина 1.5 мм
            Cylinder(radius=118.0 / 2.0, height=1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Углубленная чаша корзинки Ø82 мм, глубина 22 мм
            Cylinder(radius=82.0 / 2.0, height=22.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
            # Центральный шток корзинки-пробки Ø8 мм
            Cylinder(radius=8.0 / 2.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            # Ручка пробки Ø25 мм
            with Locations(Location((0, 0, 5))):
                Cylinder(radius=25.0 / 2.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    sliv1 = sliv1_builder.part
    sliv1.label = "Sliv_Bolshoy"
    sliv1.color = Color(0.80, 0.80, 0.82)  # Хром

    # -------------------------------------------------------------------------
    # 3. Sliv_Maly (Сливная арматура малой чаши Ø118)
    # -------------------------------------------------------------------------
    print("Построение слива малой чаши...")
    with BuildPart() as sliv2_builder:
        with Locations(Location((small_cx, small_cy, -H_small + flange_t))):
            Cylinder(radius=118.0 / 2.0, height=1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
            Cylinder(radius=82.0 / 2.0, height=22.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
            Cylinder(radius=8.0 / 2.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            with Locations(Location((0, 0, 5))):
                Cylinder(radius=25.0 / 2.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    sliv2 = sliv2_builder.part
    sliv2.label = "Sliv_Maly"
    sliv2.color = Color(0.80, 0.80, 0.82)  # Хром

    # -------------------------------------------------------------------------
    # 4. Sifon_Armatura (Сифон, перелив и соединительные патрубки под мойкой)
    # -------------------------------------------------------------------------
    print("Построение сифона и труб...")
    with BuildPart() as sifon_builder:
        # Стакан слива под большой чашей
        with Locations(Location((main_cx, main_cy, -H_main - 20))):
            Cylinder(radius=88.0 / 2.0, height=35.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            
        # Стакан слива под малой чашей
        with Locations(Location((small_cx, small_cy, -H_small - 20))):
            Cylinder(radius=88.0 / 2.0, height=35.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            
        # Соединительная труба от малой чаши к сифону (Ø40 мм с уклоном)
        # На чертеже труба идет от малой чаши к тройнику под большой чашей
        p_start = Vector(small_cx, small_cy, -H_small - 35)
        p_end = Vector(main_cx + 40, main_cy, -H_main - 40)
        pipe_dir = p_end - p_start
        pipe_len = pipe_dir.length
        mid_pt = (p_start + p_end) / 2.0
        
        # Колба бутылочного сифона под большой чашей
        siphon_center = Vector(main_cx, main_cy, -H_main - 70)
        with Locations(Location(siphon_center)):
            Cylinder(radius=65.0 / 2.0, height=85.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            
        # Отводная труба в канализацию Ø40 мм (назад к стене)
        with Locations(Location((main_cx, main_cy + 40, -H_main - 60)) * Rotation(90, 0, 0)):
            Cylinder(radius=40.0 / 2.0, height=120.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Наклонная труба между сливами
        with Locations(Location(p_start)):
            Cylinder(radius=40.0 / 2.0, height=pipe_len * 0.9, align=(Align.CENTER, Align.CENTER, Align.MIN))

    sifon = sifon_builder.part
    sifon.label = "Sifon_Armatura"
    sifon.color = Color(0.20, 0.20, 0.20)  # Черный сантехнический пластик

    # -------------------------------------------------------------------------
    # 5. Krepleniya (Монтажные зажимы к столешнице по периметру, max 40 мм)
    # -------------------------------------------------------------------------
    print("Построение крепежных зажимов...")
    clips = []
    clip_locs = [
        (-480, -230), (-250, -230), (0, -230), (250, -230), (480, -230),
        (-480, 230), (-250, 230), (0, 230), (250, 230), (480, 230)
    ]
    with BuildPart() as clips_builder:
        for cx, cy in clip_locs:
            with Locations(Location((cx, cy, -10))):
                Box(18.0, 14.0, 20.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
                with Locations(Location((0, 0, -10))):
                    Cylinder(radius=3.0, height=15.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    krepleniya = clips_builder.part
    krepleniya.label = "Krepleniya"
    krepleniya.color = Color(0.60, 0.62, 0.65)  # Оцинкованная сталь

    # -------------------------------------------------------------------------
    # Сборка и экспорт
    # -------------------------------------------------------------------------
    print("Формирование иерархии сборки...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[karkas, sliv1, sliv2, sifon, krepleniya]
    )
    
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "kitchen_sink_chrome.step"
    
    print(f"Экспорт сборки в {step_file}...")
    export_step(assembly, str(step_file))
    
    bbox = assembly.bounding_box()
    dx = round(bbox.size.X, 1)
    dy = round(bbox.size.Y, 1)
    dz = round(bbox.size.Z, 1)
    
    print("Успешно создано!")
    print(f"FILE: {step_file.resolve()}")
    print(f"BBOX: X={dx} mm, Y={dy} mm, Z={dz} mm")
    print("Узлы:")
    for ch in assembly.children:
        c = getattr(ch, 'color', None)
        print(f"  - {ch.label}: Color={tuple(c)[:3] if c else None}")

if __name__ == "__main__":
    build_kitchen_sink()
