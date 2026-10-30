import os
import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build123d import *

def build_revolving_shoe_rack():
    print("Начало построения поворотной выдвижной обувницы (колонна 12 уровней, без обуви, серый цвет)...")

    # =========================================================================
    # ГАБАРИТНЫЕ РАЗМЕРЫ (мм) строго по чертежу (12 Layers, 1920-2210, Min 800 x 400)
    # =========================================================================
    TOTAL_W = 700.0       # Ширина поворотной рамы (в нишу Min 800 мм)
    TOTAL_D = 360.0       # Глубина системы с полками (в нишу Min 400 мм)
    TOTAL_H = 1960.0      # Высота колонны (диапазон 1920 - 2210 мм)

    # Размеры нижнего выдвижного основания:
    BASE_W = 120.0
    BASE_D = 350.0
    BASE_H = 45.0

    # Размеры верхнего телескопического крепления:
    TOP_MOUNT_W = 120.0
    TOP_MOUNT_D = 350.0
    TOP_MOUNT_H = 40.0

    # Высота поворотной рамы:
    FRAME_H = 1720.0
    FRAME_Z_MIN = BASE_H + 30.0  # Z = 75 мм

    # Профиль труб рамы:
    TUBE_SIZE = 22.0

    # Параметры обувных полок (12 уровней х 2 стороны = 24 лотка):
    NUM_LEVELS = 12
    LEVEL_PITCH = (FRAME_H - 100.0) / (NUM_LEVELS - 1)  # Шаг ~147 мм
    SHELF_W = 660.0
    SHELF_L = 165.0       # Длина наклонного полотна
    SHELF_ANGLE = 22.0    # Угол наклона полок (градусы)
    LIP_H = 32.0          # Высота переднего ограничительного бортика

    # Цветовая палитра: премиальный серый антрацит / графит
    COLOR_FRAME = Color(0.36, 0.38, 0.40)      # Темно-серый матовый металл рамы
    COLOR_SHELVES = Color(0.44, 0.46, 0.48)    # Серый графит полок
    COLOR_MECHANISM = Color(0.28, 0.29, 0.31)  # Антрацит направляющих баз
    COLOR_CHROME = Color(0.75, 0.76, 0.78)     # Сталь / хром осей и телескопа
    COLOR_PLASTIC = Color(0.18, 0.18, 0.20)    # Черно-серый конструкционный пластик
    COLOR_HANDLE = Color(0.55, 0.57, 0.60)     # Матовый серый алюминий ручки

    # =========================================================================
    # 1. Baza_Nizhnyaya_Mekhanizm (Нижняя направляющая с поворотной осью)
    # =========================================================================
    with BuildPart() as base_builder:
        # Корпус направляющей полного выдвижения на дно шкафа
        Box(BASE_W, BASE_D, BASE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Продольные пазы шариковых телескопических рельсов
        for s in [-1.0, 1.0]:
            with Locations(Location((s * (BASE_W / 2.0 - 5.0), 0, BASE_H / 2.0))):
                Box(10.0, BASE_D - 20.0, 12.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Нижний поворотный опорный узел (шариковый подшипник вращения)
        with Locations(Location((0, 0, BASE_H))):
            Cylinder(radius=35.0, height=18.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Центральный стальной шпиндель оси вращения
            with Locations(Location((0, 0, 18.0))):
                Cylinder(radius=16.0, height=12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    base_part = base_builder.part
    base_part.label = "Baza_Nizhnyaya_Mekhanizm"
    base_part.color = COLOR_MECHANISM

    # =========================================================================
    # 2. Kreplenie_Verkhnee_Teleskop (Верхняя телескопическая направляющая с осью)
    # =========================================================================
    top_z = TOTAL_H - TOP_MOUNT_H
    with BuildPart() as top_builder:
        # Верхняя потолочная направляющая
        with Locations(Location((0, 0, top_z))):
            Box(TOP_MOUNT_W, TOP_MOUNT_D, TOP_MOUNT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Верхний поворотный фланец
            with Locations(Location((0, 0, -18.0))):
                Cylinder(radius=35.0, height=18.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Телескопическая вертикальная стойка компенсации высоты (труба в трубе)
        telescope_z_min = FRAME_Z_MIN + FRAME_H
        telescope_h = top_z - 18.0 - telescope_z_min
        with Locations(Location((0, 0, telescope_z_min))):
            # Внешняя труба регулировки Ø 38 мм
            Cylinder(radius=19.0, height=telescope_h / 2.0 + 10.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Внутренняя выдвижная труба Ø 32 мм
            with Locations(Location((0, 0, telescope_h / 2.0))):
                Cylinder(radius=16.0, height=telescope_h / 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Зажимное кольцо-фиксатор высоты с винтом
            with Locations(Location((0, 0, telescope_h / 2.0 - 5.0))):
                Cylinder(radius=24.0, height=14.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    top_part = top_builder.part
    top_part.label = "Kreplenie_Verkhnee_Teleskop"
    top_part.color = COLOR_MECHANISM

    # =========================================================================
    # 3. Rama_Povorotnaya_Karkas (Несущая поворотная рама 700 х 1720 мм)
    # =========================================================================
    frame_z_center = FRAME_Z_MIN + FRAME_H / 2.0
    with BuildPart() as frame_builder:
        # 1. Левая и правая вертикальные стойки рамы из профильной трубы 22х22 мм
        for s in [-1.0, 1.0]:
            x_col = s * (TOTAL_W / 2.0 - TUBE_SIZE / 2.0)
            with Locations(Location((x_col, 0, frame_z_center))):
                Box(TUBE_SIZE, TUBE_SIZE, FRAME_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # 2. Нижняя и верхняя поперечины рамы
        with Locations(Location((0, 0, FRAME_Z_MIN + TUBE_SIZE / 2.0))):
            Box(TOTAL_W, TUBE_SIZE, TUBE_SIZE, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        with Locations(Location((0, 0, FRAME_Z_MIN + FRAME_H - TUBE_SIZE / 2.0))):
            Box(TOTAL_W, TUBE_SIZE, TUBE_SIZE, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # 3. Центральная несущая вертикальная стойка-хребет (30 х 40 мм)
        with Locations(Location((0, 0, frame_z_center))):
            Box(32.0, 40.0, FRAME_H - 2.0 * TUBE_SIZE, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # 4. Центральные поворотные цапфы (вверху и внизу)
        with Locations(Location((0, 0, FRAME_Z_MIN - 15.0))):
            Cylinder(radius=18.0, height=16.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations(Location((0, 0, FRAME_Z_MIN + FRAME_H))):
            Cylinder(radius=18.0, height=16.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    frame_part = frame_builder.part
    frame_part.label = "Rama_Povorotnaya_Karkas"
    frame_part.color = COLOR_FRAME

    # =========================================================================
    # 4. Ruchka_Povorota (Боковая ручка для вращения и выдвижения)
    # =========================================================================
    with BuildPart() as handle_builder:
        # Установлена на правой боковой стойке рамы (X = +340 мм, Z = 960 мм)
        handle_x = TOTAL_W / 2.0 + 6.0
        handle_z = FRAME_Z_MIN + FRAME_H / 2.0 - 50.0

        with Locations(Location((handle_x, 0, handle_z))):
            # Эргономичная рукоять 14 х 26 х 180 мм
            Box(14.0, 26.0, 180.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            # Ножки крепления к стойке рамы
            with Locations(Location((-10.0, 0, 70.0)), Location((-10.0, 0, -70.0))):
                Box(12.0, 16.0, 20.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    handle_part = handle_builder.part
    handle_part.label = "Ruchka_Fasada"
    handle_part.color = COLOR_HANDLE

    # =========================================================================
    # 5. Polki_Perednie (12 наклонных металлических полок-лотков спереди)
    # =========================================================================
    # Полка строится как наклонная панель с передним бортиком-ограничителем
    cos_a = math.cos(math.radians(SHELF_ANGLE))
    sin_a = math.sin(math.radians(SHELF_ANGLE))

    with BuildPart() as front_shelves_builder:
        for i in range(NUM_LEVELS):
            z_lvl = FRAME_Z_MIN + 50.0 + i * LEVEL_PITCH

            # Лицевая полка (наклон вперед: Y > 0)
            # Базовое положение центра лотка
            y_shelf = 20.0 + (SHELF_L / 2.0) * cos_a
            z_shelf = z_lvl - (SHELF_L / 2.0) * sin_a

            # Наклонное полотно полки
            with Locations(Location((0, y_shelf, z_shelf)) * Rotation(-SHELF_ANGLE, 0, 0)):
                # Основной лист лотка 660 х 165 х 2.5 мм
                Box(SHELF_W, SHELF_L, 2.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))

            # Передний ограничительный бортик (предотвращает соскальзывание обуви)
            y_lip = 20.0 + SHELF_L * cos_a
            z_lip = z_lvl - SHELF_L * sin_a + LIP_H / 2.0
            with Locations(Location((0, y_lip, z_lip))):
                # Вертикальный бортик с вырезом
                Box(SHELF_W, 3.0, LIP_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))
                # Верхняя скругленная отбортовка
                with Locations(Location((0, -1.0, LIP_H / 2.0))):
                    Box(SHELF_W, 5.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    front_shelves = front_shelves_builder.part
    front_shelves.label = "Polki_Perednie_12_Yarusov"
    front_shelves.color = COLOR_SHELVES

    # =========================================================================
    # 6. Polki_Zadnie (12 наклонных металлических полок-лотков сзади)
    # =========================================================================
    with BuildPart() as rear_shelves_builder:
        for i in range(NUM_LEVELS):
            z_lvl = FRAME_Z_MIN + 50.0 + i * LEVEL_PITCH

            # Задняя полка (наклон назад: Y < 0)
            y_shelf = -20.0 - (SHELF_L / 2.0) * cos_a
            z_shelf = z_lvl - (SHELF_L / 2.0) * sin_a

            # Наклонное полотно задней полки
            with Locations(Location((0, y_shelf, z_shelf)) * Rotation(SHELF_ANGLE, 0, 0)):
                Box(SHELF_W, SHELF_L, 2.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))

            # Задний ограничительный бортик
            y_lip = -20.0 - SHELF_L * cos_a
            z_lip = z_lvl - SHELF_L * sin_a + LIP_H / 2.0
            with Locations(Location((0, y_lip, z_lip))):
                Box(SHELF_W, 3.0, LIP_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))
                with Locations(Location((0, 1.0, LIP_H / 2.0))):
                    Box(SHELF_W, 5.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    rear_shelves = rear_shelves_builder.part
    rear_shelves.label = "Polki_Zadnie_12_Yarusov"
    rear_shelves.color = COLOR_SHELVES

    # =========================================================================
    # 7. Kronshteyny_Krepleniya_Polok (Боковые держатели полок к центральной стойке)
    # =========================================================================
    with BuildPart() as brackets_builder:
        for i in range(NUM_LEVELS):
            z_lvl = FRAME_Z_MIN + 50.0 + i * LEVEL_PITCH
            # Кронштейны-планки соединяющие полки со стойкой и боковинами
            for s in [-1.0, 1.0]:
                x_b = s * (SHELF_W / 2.0 - 5.0)
                with Locations(Location((x_b, 0, z_lvl - 10.0))):
                    Box(3.0, 60.0, 24.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    brackets = brackets_builder.part
    brackets.label = "Kronshteyny_Polok"
    brackets.color = COLOR_PLASTIC

    # =========================================================================
    # 8. Rychag_Kinematiki (Поворотные кинематические тяги-рычаги)
    # =========================================================================
    with BuildPart() as arm_builder:
        # Верхняя и нижняя диагональные тяги ограничения поворота 180°
        # Нижний поворотный рычаг (Z = 55 мм)
        with Locations(Location((40.0, 60.0, BASE_H + 8.0)) * Rotation(0, 0, 35)):
            Box(16.0, 180.0, 6.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            Cylinder(radius=10.0, height=8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            with Locations(Location((0, 80.0, 0))):
                Cylinder(radius=8.0, height=8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Верхний поворотный рычаг (под потолочной направляющей)
        with Locations(Location((40.0, 60.0, top_z - 10.0)) * Rotation(0, 0, 35)):
            Box(16.0, 180.0, 6.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            Cylinder(radius=10.0, height=8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    arm = arm_builder.part
    arm.label = "Rychagi_Kinematiki_Povorota"
    arm.color = COLOR_CHROME

    # =========================================================================
    # СБОРКА КОМПОНЕНТА ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    raw_parts = [
        base_part,
        top_part,
        frame_part,
        handle_part,
        front_shelves,
        rear_shelves,
        brackets,
        arm
    ]

    # ТРАНСФОРМАЦИЯ В СИСТЕМУ КООРДИНАТ И ГАБАРИТНУЮ РАМКУ «БАЗИС-МЕБЕЛЬЩИК»:
    # X — Ширина (по горизонтали, -350 .. +350 мм)
    # Y — Высота (по вертикали, основание на Y = 0.0, верх на Y = 1960.0 мм)
    # Z — Глубина (по глубине шкафа, от задней плоскости Z = 0.0 до фасада Z = 350.0 мм)
    basis_transform = Location((0, 0, TOTAL_D / 2.0)) * Rotation(-90, 0, 0)
    
    parts = []
    for p in raw_parts:
        p_basis = p.moved(basis_transform)
        p_basis.label = p.label
        p_basis.color = p.color
        parts.append(p_basis)

    assembly = Compound(label="Obuvnitsa_Povorotnaya_Kolonna_12_Yarusov", children=parts)

    # Проверка габаритных размеров по осям Базиса
    bbox = assembly.bounding_box()
    dx = bbox.max.X - bbox.min.X
    dy = bbox.max.Y - bbox.min.Y
    dz = bbox.max.Z - bbox.min.Z

    print(f"\nГабаритные размеры модели по осям БАЗИС-МЕБЕЛЬЩИК:")
    print(f"X (Ширина): {dx:.1f} мм (в нишу: Min 800.0 мм)")
    print(f"Y (Высота): {dy:.1f} мм (диапазон по чертежу: 1920 - 2210 мм)")
    print(f"Z (Глубина): {dz:.1f} мм (в нишу: Min 400.0 мм)")
    print(f"Базовая плоскость пола: Y_min = {bbox.min.Y:.1f} мм, Y_max = {bbox.max.Y:.1f} мм")
    print(f"Количество уровней: {NUM_LEVELS} (всего 24 полки-лотка: 12 спереди + 12 сзади)")
    print(f"Количество узлов в сборке: {len(parts)}")

    # Директории вывода
    output_dir = Path("c:/Users/Den/Documents/Ai studio/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    step_file = output_dir / "obuvnitsa_povorotnaya_vydvizhnaya.step"

    print(f"\nЭкспорт в STEP файл: {step_file} ...")
    export_step(assembly, str(step_file))
    print(f"✅ Файл успешно создан! Размер: {step_file.stat().st_size} байт")

    # Экспорт копии в Ai studio-new для веб-платформы
    new_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/private_step")
    new_dir.mkdir(parents=True, exist_ok=True)
    export_step(assembly, str(new_dir / "obuvnitsa_povorotnaya_vydvizhnaya.step"))

    # Экспорт GLB превью для 3D веб-просмотра
    try:
        from build123d import export_gltf
        glb_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/previews")
        glb_dir.mkdir(parents=True, exist_ok=True)
        export_gltf(assembly, str(glb_dir / "obuvnitsa_povorotnaya_vydvizhnaya.glb"), binary=True)
        print("✅ GLB-превью успешно экспортировано!")
    except Exception as e:
        print(f"Экспорт GLB: {e}")

if __name__ == "__main__":
    build_revolving_shoe_rack()
