import os
import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build123d import *

def build_folding_shelf_bracket():
    print("Начало построения складного кронштейна для полок (400 × 170 × 42 мм)...")

    # =========================================================================
    # ГАБАРИТНЫЕ РАЗМЕРЫ (мм) строго по чертежу
    # =========================================================================
    # БАЗИС-МЕБЕЛЬЩИК:
    # X — Ширина (42.0 мм, от -21.0 до +21.0 мм по настенной планке)
    # Y — Высота (170.0 мм, от Y = 0.0 внизу до Y = 170.0 мм на плоскости полки)
    # Z — Глубина (400.0 мм, от Z = 0.0 у стены до Z = 400.0 мм у переднего края)
    # =========================================================================
    ARM_LEN = 400.0       # Длина горизонтальной консоли (вылет от стены)
    WALL_H = 170.0        # Высота настенной планки
    BASE_W = 42.0         # Полная ширина настенной крепежной планки с ушками
    ARM_W = 18.0          # Ширина П-образного профиля консоли
    ARM_H = 25.0          # Высота профиля горизонтальной консоли
    WALL_D = 25.0         # Глубина профиля настенного кронштейна от стены
    SHEET_T = 1.8         # Толщина листовой конструкционной стали

    # Цветовая гамма: черный муар / матовая порошковая покраска
    COLOR_BLACK_MATTE = Color(0.14, 0.14, 0.16)
    COLOR_ACCENT = Color(0.18, 0.18, 0.20)
    COLOR_RIVETS = Color(0.30, 0.32, 0.35)

    # =========================================================================
    # 1. Planka_Nastennaya (Вертикальный настенный кронштейн с крепежными ушками)
    # Габариты: X = 42 мм, Y = 170 мм, Z = 25 мм
    # =========================================================================
    with BuildPart() as wall_builder:
        # Задняя пристенная пластина (монтажная база 42 х 170 х 1.8 мм при Z = 0 .. 1.8 мм)
        with Locations(Location((0, WALL_H / 2.0, SHEET_T / 2.0))):
            Box(BASE_W, WALL_H, SHEET_T, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Боковые стенки П-образного канала настенной планки (Z от 1.8 до 25.0 мм)
        # Канал шириной 21.6 мм (для свободного входа консоли 18 мм)
        channel_w = ARM_W + 2.0 * SHEET_T  # 21.6 мм
        wall_flange_d = WALL_D - SHEET_T    # 23.2 мм

        for s in [-1.0, 1.0]:
            x_wall = s * (channel_w / 2.0 - SHEET_T / 2.0)
            with Locations(Location((x_wall, WALL_H / 2.0, SHEET_T + wall_flange_d / 2.0))):
                Box(SHEET_T, WALL_H, wall_flange_d, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Скругления верхних и нижних углов монтажных ушек R4
        # Крепежные отверстия на монтажных ушках под саморезы (4 отверстия Ø 4.5 мм с зенковкой)
        ear_x = BASE_W / 2.0 - 5.5  # 15.5 мм от центра
        for sx in [-ear_x, ear_x]:
            for y_hole in [20.0, 65.0, 115.0, 150.0]:
                with Locations(Location((sx, y_hole, -1.0))):
                    Cylinder(radius=2.25, height=SHEET_T + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Отверстия под оси шарниров:
        # Верхняя ось вращения консоли: Y = 158.0 мм, Z = 14.0 мм
        with Locations(Location((0, 158.0, 14.0)) * Rotation(0, 90, 0)):
            Cylinder(radius=2.6, height=channel_w + 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Нижняя ось диагонального подкоса: Y = 28.0 мм, Z = 14.0 мм
        with Locations(Location((0, 28.0, 14.0)) * Rotation(0, 90, 0)):
            Cylinder(radius=2.6, height=channel_w + 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    wall_bracket = wall_builder.part
    wall_bracket.label = "Planka_Nastennaya_42x170"
    wall_bracket.color = COLOR_BLACK_MATTE

    # =========================================================================
    # 2. Konsol_Polochnaya (Горизонтальная консоль под полку)
    # Габариты: X = 18 мм, Y = 145 .. 170 мм (высота 25 мм), Z = 4 .. 400 мм (длина 400 мм)
    # =========================================================================
    with BuildPart() as arm_builder:
        # Верхняя опорная горизонтальная полка консоли (на Y = 170 мм)
        # Полка шириной 18 мм, толщиной 1.8 мм, от Z = 5.0 до Z = 400.0 мм
        with Locations(Location((0, WALL_H - SHEET_T / 2.0, ARM_LEN / 2.0 + 2.5))):
            Box(ARM_W, SHEET_T, ARM_LEN - 5.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Две боковые стенки П-образного профиля (высота 23.2 мм, от Y = 145.0 до 168.2 мм)
        for s in [-1.0, 1.0]:
            x_arm = s * (ARM_W / 2.0 - SHEET_T / 2.0)
            with Locations(Location((x_arm, WALL_H - ARM_H / 2.0 - SHEET_T / 2.0, ARM_LEN / 2.0 + 2.5))):
                Box(SHEET_T, ARM_H - SHEET_T, ARM_LEN - 5.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Скос переднего края консоли (под 30° срезан передний нижний угол)
        with Locations(Location((0, WALL_H - ARM_H + 5.0, ARM_LEN - 10.0)) * Rotation(35, 0, 0)):
            Box(ARM_W + 4.0, 25.0, 30.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Монтажные отверстия на верхней полке консоли для крепления полки (3 шт. Ø 4.5 мм)
        for z_hole in [80.0, 210.0, 340.0, 385.0]:
            with Locations(Location((0, WALL_H - SHEET_T - 1.0, z_hole))):
                Cylinder(radius=2.25, height=SHEET_T + 2.0, align=(Align.CENTER, Align.MIN, Align.CENTER), mode=Mode.SUBTRACT)

        # Направляющий продольный паз в боковых стенках для фиксации подкоса
        # Паз по бокам от Z = 190.0 до 220.0 мм на высоте Y = 156.0 мм
        with Locations(Location((0, 156.0, 205.0)) * Rotation(0, 90, 0)):
            Cylinder(radius=3.0, height=ARM_W + 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
        with Locations(Location((0, 156.0, 205.0))):
            Box(ARM_W + 4.0, 6.0, 24.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Выемка под палец рычага разблокировки внизу консоли
        with Locations(Location((0, WALL_H - ARM_H + 3.0, 140.0))):
            Box(ARM_W + 2.0, 10.0, 45.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    arm_bracket = arm_builder.part
    arm_bracket.label = "Konsol_Polochnaya_400x25"
    arm_bracket.color = COLOR_BLACK_MATTE

    # =========================================================================
    # 3. Podkos_Diagonalny (Диагональная стальная распорная тяга)
    # Соединяет шарнир (0, 28, 14) с точкой запирания (0, 156, 205)
    # =========================================================================
    p1 = Vector(0, 28.0, 14.0)
    p2 = Vector(0, 156.0, 205.0)
    brace_vec = p2 - p1
    brace_len = brace_vec.length
    brace_center = (p1 + p2) / 2.0
    # Угол наклона к горизонтали:
    brace_angle_deg = math.degrees(math.atan2(brace_vec.Y, brace_vec.Z))

    with BuildPart() as brace_builder:
        # П-образный профиль диагонального подкоса шириной 14 мм
        brace_w = 14.0
        brace_h = 16.0
        
        # Строим тело подкоса вдоль оси Z и ориентируем по вектору
        with Locations(Location(brace_center) * Rotation(-brace_angle_deg, 0, 0)):
            # Верхняя стенка
            Box(brace_w, SHEET_T, brace_len - 10.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            # Две боковые полки
            for s in [-1.0, 1.0]:
                x_b = s * (brace_w / 2.0 - SHEET_T / 2.0)
                with Locations(Location((x_b, -brace_h / 2.0 + SHEET_T / 2.0, 0))):
                    Box(SHEET_T, brace_h, brace_len - 10.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Проушины скруглений на концах под шарниры
        for pt in [p1, p2]:
            with Locations(Location(pt) * Rotation(0, 90, 0)):
                Cylinder(radius=7.0, height=brace_w, align=(Align.CENTER, Align.CENTER, Align.CENTER))
                Cylinder(radius=2.6, height=brace_w + 2.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    brace_part = brace_builder.part
    brace_part.label = "Podkos_Diagonalny_Raskos"
    brace_part.color = COLOR_ACCENT

    # =========================================================================
    # 4. Rychag_Razblokirovki (Эргономичный подпружиненный рычаг-курок)
    # Расположен под консолью около точки Z = 205 .. 255 мм
    # =========================================================================
    with BuildPart() as lever_builder:
        # Рычаг разблокировки с изогнутым хвостовиком для нажатия пальцем снизу
        with Locations(Location((0, 142.0, 230.0)) * Rotation(-12, 0, 0)):
            # Планка рычага 10 х 3.0 х 55 мм
            Box(10.0, 3.0, 55.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            # Загнутый лепесток для удобного упора пальца (хвостик курка)
            with Locations(Location((0, -8.0, 24.0)) * Rotation(35, 0, 0)):
                Box(12.0, 3.0, 18.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    lever_part = lever_builder.part
    lever_part.label = "Rychag_Zamka_Fiksatora"
    lever_part.color = COLOR_BLACK_MATTE

    # =========================================================================
    # 5. Osi_Sharniry (Стальные шарнирные заклепки / пальцы 4 шт.)
    # =========================================================================
    with BuildPart() as pins_builder:
        # 1. Верхняя ось консоли
        with Locations(Location((0, 158.0, 14.0)) * Rotation(0, 90, 0)):
            Cylinder(radius=2.5, height=channel_w + 2.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            for sign in [-1.0, 1.0]:
                with Locations(Location((0, 0, sign * (channel_w / 2.0 + 1.0)))):
                    Cylinder(radius=4.5, height=1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # 2. Нижняя ось диагонального подкоса
        with Locations(Location((0, 28.0, 14.0)) * Rotation(0, 90, 0)):
            Cylinder(radius=2.5, height=channel_w + 2.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            for sign in [-1.0, 1.0]:
                with Locations(Location((0, 0, sign * (channel_w / 2.0 + 1.0)))):
                    Cylinder(radius=4.5, height=1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # 3. Ось подвижного фиксатора диагонали в пазу консоли
        with Locations(Location((0, 156.0, 205.0)) * Rotation(0, 90, 0)):
            Cylinder(radius=2.5, height=ARM_W + 2.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            for sign in [-1.0, 1.0]:
                with Locations(Location((0, 0, sign * (ARM_W / 2.0 + 1.0)))):
                    Cylinder(radius=4.2, height=1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # 4. Ось рычага разблокировки
        with Locations(Location((0, 152.0, 212.0)) * Rotation(0, 90, 0)):
            Cylinder(radius=2.0, height=ARM_W - 1.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    pins_part = pins_builder.part
    pins_part.label = "Osi_Zaklepki_Sharnirov"
    pins_part.color = COLOR_RIVETS

    # =========================================================================
    # СБОРКА КОМПОНЕНТА ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    parts = [
        wall_bracket,
        arm_bracket,
        brace_part,
        lever_part,
        pins_part
    ]

    assembly = Compound(label="Kronshteyn_Skladnoy_400x170x42", children=parts)

    # Проверка габаритных размеров по осям Базиса
    bbox = assembly.bounding_box()
    dx = bbox.max.X - bbox.min.X
    dy = bbox.max.Y - bbox.min.Y
    dz = bbox.max.Z - bbox.min.Z

    print(f"\nГабаритные размеры модели по осям БАЗИС-МЕБЕЛЬЩИК:")
    print(f"X (Ширина): {dx:.1f} мм (по чертежу: 42.0 мм)")
    print(f"Y (Высота): {dy:.1f} мм (по чертежу: 170.0 мм)")
    print(f"Z (Глубина): {dz:.1f} мм (по чертежу: 400.0 мм)")
    print(f"Пристенная плоскость: Z_min = {bbox.min.Z:.1f} мм, вылет консоли: Z_max = {bbox.max.Z:.1f} мм")
    print(f"Основание настенной планки: Y_min = {bbox.min.Y:.1f} мм, верхняя опорная грань: Y_max = {bbox.max.Y:.1f} мм")
    print(f"Количество узлов в сборке: {len(parts)}")

    # Директории вывода
    output_dir = Path("c:/Users/Den/Documents/Ai studio/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    step_file = output_dir / "kronshteyn_skladnoy_400.step"

    print(f"\nЭкспорт в STEP файл: {step_file} ...")
    export_step(assembly, str(step_file))
    print(f"✅ Файл успешно создан! Размер: {step_file.stat().st_size} байт")

    # Экспорт копии в Ai studio-new для веб-платформы
    new_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/private_step")
    new_dir.mkdir(parents=True, exist_ok=True)
    export_step(assembly, str(new_dir / "kronshteyn_skladnoy_400.step"))

    # Экспорт GLB превью для 3D веб-просмотра
    try:
        from build123d import export_gltf
        glb_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/previews")
        glb_dir.mkdir(parents=True, exist_ok=True)
        export_gltf(assembly, str(glb_dir / "kronshteyn_skladnoy_400.glb"), binary=True)
        print("✅ GLB-превью успешно экспортировано!")
    except Exception as e:
        print(f"Экспорт GLB: {e}")

if __name__ == "__main__":
    build_folding_shelf_bracket()
