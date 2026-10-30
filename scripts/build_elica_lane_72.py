import os
import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build123d import *

def build_elica_lane_hood():
    print("Начало построения встраиваемой вытяжки Elica LANE 72 см...")

    # =========================================================================
    # ОСНОВНЫЕ РАЗМЕРЫ (мм) строго по чертежу каталога Elica LANE 72
    # =========================================================================
    # Габариты нижней рамки (фланца):
    FLANGE_W = 714.0      # Ширина фланца
    FLANGE_D = 282.5      # Глубина фланца
    FLANGE_H = 2.0        # Толщина видимой рамки

    # Габариты встраиваемого короба (под пропил 694+2 х 262+2 мм):
    BODY_W = 693.0        # Ширина короба
    BODY_D = 260.0        # Глубина короба
    BODY_H = 300.6        # Высота короба над фланцем (до отметки 302.6 мм)

    # Смещение короба относительно рамки:
    # Фланец по X центрирован: отступ (714 - 693) / 2 = 10.5 мм
    # Фланец по Y: глубина 282.5, короб 260.
    # Передний свес фланца: 15.0 мм, задний свес: 7.5 мм
    BODY_Y_OFFSET = (15.0 - 7.5) / 2.0  # +3.75 мм смещение центра короба назад

    # Окно забора воздуха в нижней рамке:
    INTAKE_WINDOW_W = 637.4
    INTAKE_WINDOW_D = 216.0
    INTAKE_Y_OFFSET = 3.0   # Смещение окна всасывания относительно центра рамки

    # Центральная декоративная панель периметрального всасывания:
    PANEL_W = 587.4
    PANEL_D = 180.1
    PANEL_H = 8.0

    # Светодиодная планка LED:
    LED_W = 586.0
    LED_D = 14.0
    LED_H = 2.0
    LED_Y = -FLANGE_D / 2.0 + 23.0  # Передняя часть рамки (отступ ~23 мм)

    # Выходной патрубок воздуховода:
    DUCT_DIA = 149.0      # Диаметр Ø 150 мм
    DUCT_H = 19.4         # Высота патрубка (322.0 - 302.6 мм)
    DUCT_Y = BODY_Y_OFFSET # По центру короба

    # =========================================================================
    # 1. Ramka_Nizhnyaya (Нижний видимый фланец с вырезом под панель и LED)
    # =========================================================================
    with BuildPart() as flange_builder:
        # Основная пластина фланца 714 х 282.5 х 2 мм
        Box(FLANGE_W, FLANGE_D, FLANGE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Вырез под нишу периметрального всасывания 637.4 х 216 мм
        with Locations(Location((0, INTAKE_Y_OFFSET, 0))):
            Box(INTAKE_WINDOW_W, INTAKE_WINDOW_D, FLANGE_H + 1.0, 
                align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Вырез под плафон LED освещения 586 х 14 мм
        with Locations(Location((0, LED_Y, 0))):
            Box(LED_W + 1.0, LED_D + 1.0, FLANGE_H + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Скругление внешних 4 углов фланца R3 для аккуратности
        v_edges = flange_builder.edges().filter_by(Axis.Z)
        corner_edges = v_edges.sort_by(Axis.X)
        outer_corners = corner_edges[:2] + corner_edges[-2:]
        fillet(outer_corners, radius=2.5)

    flange = flange_builder.part
    flange.label = "Ramka_Nizhnyaya"
    flange.color = Color(0.76, 0.76, 0.78)  # Шлифованная нержавеющая сталь

    # =========================================================================
    # 2. Korpus_Vstraivaemy (Встраиваемый короб из оцинкованной стали)
    # =========================================================================
    with BuildPart() as body_builder:
        # Внешний объем короба 693 х 260 х 300.6 мм от Z = 2.0 до 302.6 мм
        with Locations(Location((0, BODY_Y_OFFSET, FLANGE_H))):
            Box(BODY_W, BODY_D, BODY_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Внутренняя рабочая полость короба (толщина стенок 1.5 мм)
        with Locations(Location((0, BODY_Y_OFFSET, FLANGE_H - 1.0))):
            Box(BODY_W - 3.0, BODY_D - 3.0, BODY_H - 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Отверстие под воздуховод Ø 150 мм в верхней крышке (Z = 302.6 мм)
        with Locations(Location((0, DUCT_Y, FLANGE_H + BODY_H - 5.0))):
            Cylinder(radius=DUCT_DIA / 2.0, height=10.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Продольные ребра жесткости на передней и задней стенке
        with Locations(Location((0, BODY_Y_OFFSET - BODY_D / 2.0 + 1.0, 160.0))):
            Box(BODY_W - 40.0, 2.0, 8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        with Locations(Location((0, BODY_Y_OFFSET + BODY_D / 2.0 - 1.0, 160.0))):
            Box(BODY_W - 40.0, 2.0, 8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    body = body_builder.part
    body.label = "Korpus_Vstraivaemy"
    body.color = Color(0.63, 0.65, 0.67)  # Оцинкованная листовая сталь

    # =========================================================================
    # 3. Patrubok_Vozduhovoda (Выходной фланец Ø 150 мм с клапаном)
    # =========================================================================
    z_top = FLANGE_H + BODY_H  # Z = 302.6 мм
    with BuildPart() as duct_builder:
        # Внешний цилиндр патрубка Ø 149 мм
        with Locations(Location((0, DUCT_Y, z_top))):
            Cylinder(radius=DUCT_DIA / 2.0, height=DUCT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Внутренний проходной канал (толщина стенки 2.0 мм)
            Cylinder(radius=DUCT_DIA / 2.0 - 2.0, height=DUCT_H + 2.0, 
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Центральная ось обратного клапана
        with Locations(Location((0, DUCT_Y, z_top + DUCT_H / 2.0))):
            Box(DUCT_DIA - 4.0, 3.0, 8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Лепестки антивозвратного клапана
        with Locations(
            Location((-DUCT_DIA / 4.0, DUCT_Y, z_top + DUCT_H / 2.0)),
            Location((DUCT_DIA / 4.0, DUCT_Y, z_top + DUCT_H / 2.0))
        ):
            Box(DUCT_DIA / 2.5, DUCT_DIA / 2.5, 1.2, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    duct = duct_builder.part
    duct.label = "Patrubok_Vozduhovoda"
    duct.color = Color(0.18, 0.18, 0.20)  # Черный термостойкий пластик

    # =========================================================================
    # 4. Panel_Vsasyvaniya_Perimetr (Лицевая панель периметрального всасывания)
    # =========================================================================
    with BuildPart() as panel_builder:
        # Панель 587.4 х 180.1 х 8 мм
        # Размещена внутри ниши забора воздуха (Z = 2.0 .. 10.0 мм)
        with Locations(Location((0, INTAKE_Y_OFFSET, FLANGE_H))):
            Box(PANEL_W, PANEL_D, PANEL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Фаска по периметру нижней грани R1.5 для премиального внешнего вида
        bottom_edges = panel_builder.edges().filter_by(Axis.Z)
        # Скруглим вертикальные углы R4
        fillet(bottom_edges, radius=3.5)

    panel = panel_builder.part
    panel.label = "Panel_Vsasyvaniya_Perimetr"
    panel.color = Color(0.80, 0.80, 0.82)  # Сатинированная нержавеющая сталь Inox

    # =========================================================================
    # 5. Filtr_Zhirovoy (Внутренний многослойный кассетный алюминиевый фильтр)
    # =========================================================================
    with BuildPart() as filter_builder:
        # Кассета фильтра 570 х 165 х 8 мм на высоте Z = 14.0 .. 22.0 мм
        z_filter = FLANGE_H + 12.0
        with Locations(Location((0, INTAKE_Y_OFFSET, z_filter))):
            # Алюминиевая рамка фильтра
            Box(570.0, 165.0, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Углубление для сетки
            Box(550.0, 145.0, 8.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            # Сама мелкоячеистая алюминиевая сетка
            Box(550.0, 145.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Пластиковый замок-защелка кассеты по центру
            with Locations(Location((0, 0, 1.0))):
                Box(45.0, 22.0, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    filter_part = filter_builder.part
    filter_part.label = "Filtr_Zhirovoy_Alyuminiy"
    filter_part.color = Color(0.68, 0.70, 0.72)  # Алюминиевая сетка фильтра

    # =========================================================================
    # 6. Svetodiodnaya_Panel_LED (Светодиодный светильник Strip LED 586 х 14 мм)
    # =========================================================================
    with BuildPart() as led_builder:
        # Устанавливается заподлицо в паз нижней рамки
        with Locations(Location((0, LED_Y, 0.2))):
            # Матовый рассеиватель
            Box(LED_W, LED_D, LED_H - 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

    led_part = led_builder.part
    led_part.label = "Planka_LED_Podsvetki"
    led_part.color = Color(0.96, 0.96, 0.92)  # Рассеиватель молочно-белый теплый

    # =========================================================================
    # 7. Knopki_Upravleniya (Пульт управления - сенсоры/кнопки справа)
    # =========================================================================
    with BuildPart() as buttons_builder:
        # На чертеже 2 кнопки расположены справа от панели (X ~ +325 .. +330 мм)
        btn_x = INTAKE_WINDOW_W / 2.0 + 16.0  # X = +334.7 мм
        # 4 кнопки вертикально с шагом 12 мм
        y_positions = [-18.0, -6.0, 6.0, 18.0]
        for y_pos in y_positions:
            with Locations(Location((btn_x, INTAKE_Y_OFFSET + y_pos, 0.0))):
                Cylinder(radius=3.5, height=1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    buttons_part = buttons_builder.part
    buttons_part.label = "Knopki_Upravleniya"
    buttons_part.color = Color(0.88, 0.88, 0.92)  # Полированная сталь / хром

    # =========================================================================
    # 8. Kronshteyny_Krepleniya (Боковые монтажные пружинные клипсы)
    # =========================================================================
    with BuildPart() as brackets_builder:
        # Расположены на левой и правой боковинах короба
        bracket_h = 45.0
        bracket_w = 26.0
        z_brk = FLANGE_H + 18.0

        for sign in [-1.0, 1.0]:
            x_pos = sign * (BODY_W / 2.0 + 0.5)
            with Locations(Location((x_pos, BODY_Y_OFFSET, z_brk))):
                # Основание клипсы
                Box(1.5, bracket_w, bracket_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Распорный пружинный лепесток под полку 16-40 мм
                with Locations(Location((sign * 4.5, 0, 15.0))):
                    Box(8.0, bracket_w - 4.0, 14.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    brackets_part = brackets_builder.part
    brackets_part.label = "Kronshteyny_Krepleniya"
    brackets_part.color = Color(0.55, 0.58, 0.62)  # Пружинная оцинкованная сталь

    # =========================================================================
    # СБОРКА КОМПОНЕНТА ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    parts = [
        flange,
        body,
        duct,
        panel,
        filter_part,
        led_part,
        buttons_part,
        brackets_part
    ]

    assembly = Compound(label="Elica_Lane_72_Assembly", children=parts)

    # Проверка габаритов
    bbox = assembly.bounding_box()
    dx = bbox.max.X - bbox.min.X
    dy = bbox.max.Y - bbox.min.Y
    dz = bbox.max.Z - bbox.min.Z

    print(f"\nГабаритные размеры модели:")
    print(f"X (Ширина): {dx:.1f} мм (по чертежу 714.0 мм)")
    print(f"Y (Глубина): {dy:.1f} мм (по чертежу 282.5 мм)")
    print(f"Z (Высота): {dz:.1f} мм (по чертежу 322.0 мм)")
    print(f"Количество узлов в сборке: {len(parts)}")

    output_dir = Path("c:/Users/Den/Documents/Ai studio/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    step_file = output_dir / "vytyazhka_vstraivaemaya_elica_lane_72.step"

    print(f"\nЭкспорт в STEP файл: {step_file} ...")
    export_step(assembly, str(step_file))
    print(f"✅ Файл успешно создан! Размер: {step_file.stat().st_size} байт")

    # Экспорт копии в Ai studio-new для веб-генератора
    new_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/private_step")
    new_dir.mkdir(parents=True, exist_ok=True)
    export_step(assembly, str(new_dir / "vytyazhka_vstraivaemaya_elica_lane_72.step"))

    # Экспорт GLB превью для веб-просмотра Three.js / model-viewer
    try:
        from build123d import export_gltf
        glb_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/previews")
        glb_dir.mkdir(parents=True, exist_ok=True)
        export_gltf(assembly, str(glb_dir / "vytyazhka_vstraivaemaya_elica_lane_72.glb"), binary=True)
        print("✅ GLB-превью успешно экспортировано!")
    except Exception as e:
        print(f"Экспорт GLB: {e}")

if __name__ == "__main__":
    build_elica_lane_hood()
