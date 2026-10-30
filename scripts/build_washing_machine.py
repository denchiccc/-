import os
import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build123d import *

def build_samsung_addwash_washing_machine():
    print("Начало построения стиральной машины Samsung AddWash (600 × 850 × 600 мм)...")

    # =========================================================================
    # ГАБАРИТНЫЕ РАЗМЕРЫ (мм)
    # =========================================================================
    TOTAL_W = 600.0     # Полная ширина
    TOTAL_H = 850.0     # Полная высота
    TOTAL_D = 600.0     # Полная глубина (с учетом выпуклости люка AddWash)

    FEET_H = 15.0       # Высота регулируемых опор (Z = 0 .. 15 мм)
    BODY_W = 596.0      # Ширина металлического корпуса
    BODY_H = 805.0      # Высота металлического корпуса (Z = 15 .. 820 мм)
    BODY_D = 540.0      # Глубина металлического корпуса
    
    # Центрирование корпуса по Y:
    # Задняя стенка на Y = -270.0 мм, крышка выступает назад до -300.0 мм
    # Передняя стенка на Y = +270.0 мм, люк выступает вперед до +300.0 мм (общая глубина строго 600.0 мм)
    BODY_Y_CENTER = 0.0
    FRONT_Y = BODY_Y_CENTER + BODY_D / 2.0  # +270.0 мм
    BACK_Y = BODY_Y_CENTER - BODY_D / 2.0   # -270.0 мм

    # Центр загрузочного люка:
    DOOR_CENTER_Z = 430.0   # Центр оси барабана
    DOOR_OUTER_DIA = 480.0  # Внешний диаметр люка

    # =========================================================================
    # 1. Nozhki_Reguliruemye (4 регулируемые виброопоры)
    # =========================================================================
    with BuildPart() as feet_builder:
        feet_locs = [
            (-TOTAL_W / 2.0 + 45.0, -BODY_D / 2.0 + 45.0),
            (TOTAL_W / 2.0 - 45.0, -BODY_D / 2.0 + 45.0),
            (-TOTAL_W / 2.0 + 45.0, BODY_D / 2.0 - 45.0),
            (TOTAL_W / 2.0 - 45.0, BODY_D / 2.0 - 45.0),
        ]
        for lx, ly in feet_locs:
            with Locations(Location((lx, ly, 0))):
                # Резиновая подошва
                Cylinder(radius=18.0, height=FEET_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Металлическая юбка ножки
                with Locations(Location((0, 0, FEET_H - 4.0))):
                    Cylinder(radius=21.0, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    feet = feet_builder.part
    feet.label = "Nozhki_Reguliruemye"
    feet.color = Color(0.15, 0.15, 0.15)  # Черная техническая резина

    # =========================================================================
    # 2. Korpus_Osnovnoy (Металлический эмалированный корпус со штамповкой)
    # =========================================================================
    with BuildPart() as body_builder:
        # Основной короб корпуса от Z = 15 до 820 мм
        with Locations(Location((0, BODY_Y_CENTER, FEET_H))):
            Box(BODY_W, BODY_D, BODY_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Скругление вертикальных ребер корпуса R8
        v_edges = body_builder.edges().filter_by(Axis.Z)
        fillet(v_edges, radius=8.0)

        # Вырез ниши под барабан в передней панели Ø 440 мм
        with Locations(Location((0, FRONT_Y - 15.0, DOOR_CENTER_Z)) * Rotation(90, 0, 0)):
            Cylinder(radius=220.0, height=40.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Боковые антивибрационные ребра жесткости (типичная форма боковин стиральных машин)
        for side_sign in [-1.0, 1.0]:
            x_side = side_sign * (BODY_W / 2.0 - 0.5)
            # 3 продолговатых рельефных полосы жесткости
            for z_rib in [240.0, 420.0, 600.0]:
                with Locations(Location((x_side, BODY_Y_CENTER, z_rib))):
                    Box(2.0, 360.0, 120.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
                with Locations(Location((x_side, BODY_Y_CENTER, z_rib))):
                    Box(1.0, 350.0, 110.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Цокольный скос / выемка снизу
        with Locations(Location((0, FRONT_Y - 10.0, FEET_H))):
            Box(BODY_W - 20.0, 20.0, 10.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    body = body_builder.part
    body.label = "Korpus_Osnovnoy"
    body.color = Color(0.95, 0.95, 0.96)  # Белая эмаль

    # =========================================================================
    # 3. Kryshka_Verhnyaya (Верхняя панель / столешница машины)
    # =========================================================================
    with BuildPart() as top_builder:
        top_h = TOTAL_H - (FEET_H + BODY_H)  # 850 - 820 = 30 мм
        top_d = 570.0                        # 570 мм (от Y = -300.0 до +270.0 мм)
        top_y_center = -15.0                 # Задний свес для труб/примыкания к стене

        with Locations(Location((0, top_y_center, FEET_H + BODY_H))):
            Box(TOTAL_W, top_d, top_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Скругление верхних передних и боковых ребер столешницы R4
        top_edges = top_builder.edges().filter_by(Axis.Z)
        fillet(top_edges, radius=6.0)

    top_cover = top_builder.part
    top_cover.label = "Kryshka_Verhnyaya"
    top_cover.color = Color(0.94, 0.94, 0.95)  # Матовый белый пластик

    # =========================================================================
    # 4. Panel_Upravleniya (Фронтальная панель с лотком, дисплеем и кнопками)
    # =========================================================================
    PANEL_H = 130.0
    panel_z_min = FEET_H + BODY_H - PANEL_H  # 690 .. 820 мм

    with BuildPart() as panel_builder:
        # Основа панели управления, слегка выступающая вперед (на 4 мм)
        with Locations(Location((0, FRONT_Y + 2.0, panel_z_min + PANEL_H / 2.0))):
            Box(BODY_W - 4.0, 5.0, PANEL_H - 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    panel_base = panel_builder.part
    panel_base.label = "Panel_Upravleniya"
    panel_base.color = Color(0.93, 0.93, 0.95)  # Белый глянцевый пластик

    # =========================================================================
    # 5. Lotok_Poroshka (Выдвижной диспенсер для порошка и кондиционера)
    # =========================================================================
    with BuildPart() as tray_builder:
        tray_w = 175.0
        tray_h = 105.0
        tray_x = -BODY_W / 2.0 + 105.0
        tray_z = panel_z_min + PANEL_H / 2.0
        
        with Locations(Location((tray_x, FRONT_Y + 4.5, tray_z))):
            # Лицевая планка лотка
            Box(tray_w, 4.0, tray_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            # Эргономичная выемка ручки
            with Locations(Location((0, 1.5, -20.0))):
                Box(tray_w - 40.0, 3.0, 18.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    tray = tray_builder.part
    tray.label = "Lotok_Dozator_Poroshka"
    tray.color = Color(0.96, 0.96, 0.97)  # Белый пластик

    # =========================================================================
    # 6. Pereklyuchatel_JogDial (Круглый поворотный программатор режимов)
    # =========================================================================
    with BuildPart() as dial_builder:
        dial_dia = 52.0
        dial_x = 10.0
        dial_z = panel_z_min + PANEL_H / 2.0

        with Locations(Location((dial_x, FRONT_Y + 4.0, dial_z)) * Rotation(90, 0, 0)):
            # Кольцо-основание
            Cylinder(radius=dial_dia / 2.0 + 4.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Сама круглая ручка Jog Dial с рельефом
            with Locations(Location((0, 0, 3.0))):
                Cylinder(radius=dial_dia / 2.0, height=12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Центральный световой индикатор/углубление
            with Locations(Location((0, 0, 13.0))):
                Cylinder(radius=dial_dia / 2.0 - 5.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    dial = dial_builder.part
    dial.label = "Pereklyuchatel_JogDial"
    dial.color = Color(0.78, 0.80, 0.83)  # Сатинированный металл / хром

    # =========================================================================
    # 7. Displey_Elektronny (Черный сенсорный LED-экран управления)
    # =========================================================================
    with BuildPart() as display_builder:
        disp_w = 210.0
        disp_h = 75.0
        disp_x = BODY_W / 2.0 - 125.0
        disp_z = panel_z_min + PANEL_H / 2.0

        with Locations(Location((disp_x, FRONT_Y + 4.5, disp_z))):
            Box(disp_w, 2.5, disp_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Скругление углов дисплея R6
        d_edges = display_builder.edges().filter_by(Axis.Y)
        fillet(d_edges, radius=5.0)

    display = display_builder.part
    display.label = "Displey_Elektronny"
    display.color = Color(0.08, 0.08, 0.10)  # Черный тонированный акрил

    # =========================================================================
    # 8. Manzheta_Lyuka (Резиновый гофрированный уплотнитель)
    # =========================================================================
    with BuildPart() as cuff_builder:
        with Locations(Location((0, FRONT_Y - 25.0, DOOR_CENTER_Z)) * Rotation(90, 0, 0)):
            # Внешняя часть манжеты
            Cylinder(radius=210.0, height=35.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Внутренний просвет
            Cylinder(radius=180.0, height=36.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    cuff = cuff_builder.part
    cuff.label = "Manzheta_Rezina"
    cuff.color = Color(0.24, 0.25, 0.27)  # Матовая темно-серая резина

    # =========================================================================
    # 9. Baraban_Nerzhaveyushchiy (Внутренний перфорированный барабан)
    # =========================================================================
    with BuildPart() as drum_builder:
        with Locations(Location((0, FRONT_Y - 140.0, DOOR_CENTER_Z)) * Rotation(90, 0, 0)):
            # Корпус барабана
            Cylinder(radius=185.0, height=115.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            Cylinder(radius=180.0, height=116.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            # Задняя торцевая стенка барабана
            with Locations(Location((0, 0, 1.0))):
                Cylinder(radius=180.0, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    drum = drum_builder.part
    drum.label = "Baraban_Nerzhaveyka"
    drum.color = Color(0.72, 0.74, 0.76)  # Нержавеющая сталь

    # =========================================================================
    # 10. Dver_Osnovnaya_Lyuk (Большая дверь люка с черным ободом Crystal Gloss)
    # =========================================================================
    with BuildPart() as door_builder:
        # Внешний декоративный люк Ø 480 мм
        with Locations(Location((0, FRONT_Y, DOOR_CENTER_Z)) * Rotation(90, 0, 0)):
            # Обод люка
            Cylinder(radius=DOOR_OUTER_DIA / 2.0, height=26.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Конусная центральная выемка под стекло
            with Locations(Location((0, 0, 8.0))):
                Cylinder(radius=DOOR_OUTER_DIA / 2.0 - 55.0, height=20.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            # Выпуклое смотровое стекло (сферический сегмент)
            with Locations(Location((0, 0, 12.0))):
                Cylinder(radius=DOOR_OUTER_DIA / 2.0 - 58.0, height=10.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Хромированная ручка люка справа (X = +210 мм)
        with Locations(Location((DOOR_OUTER_DIA / 2.0 - 25.0, FRONT_Y + 18.0, DOOR_CENTER_Z))):
            Box(14.0, 12.0, 90.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    door = door_builder.part
    door.label = "Dver_Lyuka_Osnovnaya"
    door.color = Color(0.12, 0.12, 0.14)  # Глянцевый черный пластик / тонированное стекло

    # =========================================================================
    # 11. Dverca_AddWash (Оригинальный мини-люк дозагрузки белья Samsung AddWash)
    # =========================================================================
    with BuildPart() as addwash_builder:
        # Мини-люк расположен в верхней части большой двери
        addwash_z = DOOR_CENTER_Z + 75.0
        addwash_w = 210.0
        addwash_h = 135.0
        
        with Locations(Location((0, FRONT_Y + 22.0, addwash_z))):
            # Корпус мини-люка AddWash
            Box(addwash_w, 14.0, addwash_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Скругление углов дверцы AddWash R24
        aw_edges = addwash_builder.edges().filter_by(Axis.Y)
        fillet(aw_edges, radius=22.0)

        # Клавиша замка AddWash сверху
        with Locations(Location((0, FRONT_Y + 28.0, addwash_z + addwash_h / 2.0 - 10.0))):
            Box(65.0, 4.0, 14.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    addwash_door = addwash_builder.part
    addwash_door.label = "Dverca_AddWash"
    addwash_door.color = Color(0.10, 0.10, 0.12)  # Тонированный черный глянец

    # =========================================================================
    # 12. Lyuchok_Filtra_Nasosa (Нижняя сервисная дверца сливного фильтра)
    # =========================================================================
    with BuildPart() as hatch_builder:
        hatch_w = 110.0
        hatch_h = 85.0
        hatch_x = BODY_W / 2.0 - 85.0
        hatch_z = FEET_H + 50.0

        with Locations(Location((hatch_x, FRONT_Y + 1.0, hatch_z))):
            Box(hatch_w, 2.5, hatch_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Скругление кромок лючка R6
        h_edges = hatch_builder.edges().filter_by(Axis.Y)
        fillet(h_edges, radius=6.0)

    hatch = hatch_builder.part
    hatch.label = "Lyuchok_Slivnogo_Filtra"
    hatch.color = Color(0.92, 0.92, 0.94)  # Белый пластик

    # =========================================================================
    # СБОРКА КОМПОНЕНТА ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    parts = [
        feet,
        body,
        top_cover,
        panel_base,
        tray,
        dial,
        display,
        cuff,
        drum,
        door,
        addwash_door,
        hatch
    ]

    assembly = Compound(label="Stiralnaya_Mashina_Samsung_AddWash_60x85x60", children=parts)

    # Проверка габаритных размеров
    bbox = assembly.bounding_box()
    dx = bbox.max.X - bbox.min.X
    dy = bbox.max.Y - bbox.min.Y
    dz = bbox.max.Z - bbox.min.Z

    print(f"\nГабаритные размеры модели:")
    print(f"X (Ширина): {dx:.1f} мм (по ТЗ: 600.0 мм)")
    print(f"Y (Глубина): {dy:.1f} мм (по ТЗ: 600.0 мм)")
    print(f"Z (Высота): {dz:.1f} мм (по ТЗ: 850.0 мм)")
    print(f"Количество узлов в сборке: {len(parts)}")

    # Директории вывода
    output_dir = Path("c:/Users/Den/Documents/Ai studio/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    step_file = output_dir / "stiralnaya_mashina_samsung_600x850x600.step"

    print(f"\nЭкспорт в STEP файл: {step_file} ...")
    export_step(assembly, str(step_file))
    print(f"✅ Файл успешно создан! Размер: {step_file.stat().st_size} байт")

    # Экспорт копии в Ai studio-new для веб-платформы
    new_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/private_step")
    new_dir.mkdir(parents=True, exist_ok=True)
    export_step(assembly, str(new_dir / "stiralnaya_mashina_samsung_600x850x600.step"))

    # Экспорт GLB превью для 3D веб-просмотра
    try:
        from build123d import export_gltf
        glb_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/previews")
        glb_dir.mkdir(parents=True, exist_ok=True)
        export_gltf(assembly, str(glb_dir / "stiralnaya_mashina_samsung_600x850x600.glb"), binary=True)
        print("✅ GLB-превью успешно экспортировано!")
    except Exception as e:
        print(f"Экспорт GLB: {e}")

if __name__ == "__main__":
    build_samsung_addwash_washing_machine()
