import os
import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build123d import *

def build_black_kitchen_sink():
    print("Начало построения кухонной мойки в черном цвете (500 × 500 × 200 мм)...")

    # =========================================================================
    # ГАБАРИТНЫЕ РАЗМЕРЫ (мм) строго по чертежу
    # =========================================================================
    # БАЗИС-МЕБЕЛЬЩИК:
    # X — Ширина (500 мм, от 0 до 500 мм)
    # Y — Высота (202 мм, от Y = 0 на дне чаши до Y = 202 мм на верхнем бортике)
    # Z — Глубина (500 мм, от Z = 0 у задней стенки до Z = 500 мм у переднего края)
    # =========================================================================
    SINK_W = 500.0        # Полная ширина по верхнему фланцу
    SINK_D = 500.0        # Полная глубина по верхнему фланцу
    BOWL_H = 200.0        # Глубина чаши (высота)
    RIM_T = 2.0           # Толщина верхнего монтажного бортика

    # Размеры внутренней чаши:
    BOWL_W = 450.0        # Внутренняя ширина чаши
    BOWL_D = 400.0        # Внутренняя глубина чаши
    BOWL_R = 10.0         # Радиус скругления углов чаши R10
    WALL_T = 2.5          # Толщина стенок чаши

    # Отступы бортика:
    # Слева и справа: (500 - 450) / 2 = 25 мм
    # Сзади площадка под смеситель: 70 мм
    # Спереди бортик: 30 мм (70 + 400 + 30 = 500 мм)
    RIM_REAR = 70.0
    RIM_FRONT = 30.0
    RIM_SIDE = 25.0

    # Центр чаши по координатам X и Z:
    BOWL_CENTER_X = SINK_W / 2.0                   # X = 250.0 мм
    BOWL_CENTER_Z = RIM_REAR + BOWL_D / 2.0        # Z = 270.0 мм

    # Сливное отверстие:
    DRAIN_DIA = 90.0      # Диаметр слива Ø 90 мм
    DRAIN_FLANGE_DIA = 114.0 # Наружный фланец выпуска корзинки Ø 114 мм

    # Отверстие под смеситель:
    FAUCET_DIA = 35.0     # Стандартное отверстие Ø 35 мм
    FAUCET_Z = RIM_REAR / 2.0 # Z = 35.0 мм (по центру задней площадки)

    # Цветовая гамма: стильный черный кварцевый композит / черный металлик
    COLOR_SINK = Color(0.12, 0.12, 0.14)      # Матовый черный гранит / композит
    COLOR_DRAIN = Color(0.18, 0.18, 0.20)     # Черный матовый сливной выпуск PVD
    COLOR_CHROME = Color(0.75, 0.76, 0.78)    # Нержавеющая сталь шток/сетка
    COLOR_PAD = Color(0.22, 0.22, 0.25)       # Шумопоглощающий демпфер

    # =========================================================================
    # 1. Chasha_Moyki (Основной корпус мойки: чаша + монтажный фланец)
    # Построение в координатах: Y - высота (0 .. 202 мм), X - ширина, Z - глубина
    # =========================================================================
    with BuildPart(Plane.XZ) as sink_builder:
        # Внешний габаритный объем чаши со стенками (от Y = 0 до Y = 200 мм)
        # Внешний размер чаши: (450 + 2*2.5) х (400 + 2*2.5) = 455 х 405 мм (в вырез 460х460 проходит с запасом!)
        outer_w = BOWL_W + 2.0 * WALL_T
        outer_d = BOWL_D + 2.0 * WALL_T

        # Внешняя коробка чаши
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, 0))):
            Box(outer_w, outer_d, BOWL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Верхний широкий фланец 500 × 500 × 2 мм (на высоте Y = 200 .. 202 мм)
        with Locations(Location((SINK_W / 2.0, SINK_D / 2.0, BOWL_H))):
            Box(SINK_W, SINK_D, RIM_T, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Выемка внутренней полости чаши 450 × 400 мм (глубина от Y = 2.5 до 202 мм)
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, WALL_T))):
            Box(BOWL_W, BOWL_D, BOWL_H + RIM_T + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Скругление 4 вертикальных углов чаши R10 (строго по чертежу)
        inner_z_edges = sink_builder.edges().filter_by(Axis.Y)
        # Отбираем внутренние вертикальные ребра чаши
        bowl_edges = [
            e for e in inner_z_edges 
            if abs(e.center().X - BOWL_CENTER_X) > (BOWL_W / 2.0 - 15.0) 
            and abs(e.center().Z - BOWL_CENTER_Z) > (BOWL_D / 2.0 - 15.0)
            and e.center().Y > 50.0
        ]
        if bowl_edges:
            fillet(bowl_edges, radius=BOWL_R)

        # Сливное отверстие Ø 90 мм на дне чаши
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, -1.0))):
            Cylinder(radius=DRAIN_DIA / 2.0, height=WALL_T + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Посадочная фаска/углубление под фланец корзинки слива Ø 114 мм
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, WALL_T - 0.8))):
            Cylinder(radius=DRAIN_FLANGE_DIA / 2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Отверстие под смеситель Ø 35 мм на задней площадке
        with Locations(Location((BOWL_CENTER_X, FAUCET_Z, BOWL_H - 1.0))):
            Cylinder(radius=FAUCET_DIA / 2.0, height=RIM_T + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Прямоугольное окно перелива на задней стенке чаши (глубина 35 мм от верха)
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z - BOWL_D / 2.0, BOWL_H - 35.0))):
            Box(55.0, WALL_T + 2.0, 14.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    sink_body = sink_builder.part
    sink_body.label = "Chasha_Moyki_Chernaya"
    sink_body.color = COLOR_SINK

    # =========================================================================
    # 2. Slivnoy_Klapana_Vypusk (Сливной корзинчатый выпуск Ø 90 / 114 мм)
    # =========================================================================
    with BuildPart(Plane.XZ) as drain_builder:
        # Верхнее кольцо выпуска Ø 114 мм
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, WALL_T - 0.6))):
            Cylinder(radius=DRAIN_FLANGE_DIA / 2.0, height=1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Углубление чашки слива Ø 90 мм
            with Locations(Location((0, 0, 0.4))):
                Cylinder(radius=DRAIN_DIA / 2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Сетчатая корзинка-фильтр Ø 82 мм
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, WALL_T - 2.0))):
            Cylinder(radius=41.0, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Центральный шток корзинки-пробки
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, WALL_T + 2.0))):
            Cylinder(radius=4.0, height=16.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations(Location((0, 0, 16.0))):
                Cylinder(radius=10.0, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    drain_part = drain_builder.part
    drain_part.label = "Slivnoy_Vypusk_Klapana"
    drain_part.color = COLOR_DRAIN

    # =========================================================================
    # 3. Reshetka_Pereliva (Декоративная решетка перелива на задней стенке)
    # =========================================================================
    with BuildPart(Plane.XZ) as overflow_builder:
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z - BOWL_D / 2.0 + 0.5, BOWL_H - 35.0))):
            # Пластина решетки
            Box(52.0, 1.5, 12.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            # Продольные прорези
            for ox in [-16.0, 0.0, 16.0]:
                with Locations(Location((ox, 0, 0))):
                    Box(8.0, 3.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    overflow_part = overflow_builder.part
    overflow_part.label = "Reshetka_Pereliva"
    overflow_part.color = COLOR_DRAIN

    # =========================================================================
    # 4. Shumopogloshchayushchie_Nakladki (Антивибрационные накладки снизу)
    # =========================================================================
    with BuildPart(Plane.XZ) as pad_builder:
        # Демпферная пластина на дне чаши (снизу от Y = -2.0 до 0.0 мм)
        with Locations(Location((BOWL_CENTER_X, BOWL_CENTER_Z, -2.0))):
            Box(320.0, 260.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Отверстие под слив
            with Locations(Location((0, 0, -0.5))):
                Cylinder(radius=DRAIN_FLANGE_DIA / 2.0 + 5.0, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    pad_part = pad_builder.part
    pad_part.label = "Shumoizolyatsiya_Dna"
    pad_part.color = COLOR_PAD

    # =========================================================================
    # СБОРКА КОМПОНЕНТА ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    parts = [
        sink_body,
        drain_part,
        overflow_part,
        pad_part
    ]

    assembly = Compound(label="Kukhonnaya_Moyka_Chernaya_500x500", children=parts)

    # Проверка габаритных размеров по осям Базиса
    bbox = assembly.bounding_box()
    dx = bbox.max.X - bbox.min.X
    dy = bbox.max.Y - bbox.min.Y
    dz = bbox.max.Z - bbox.min.Z

    # Нормализуем основание строго на Y = 0.0 (если шумоизоляция была в минусе)
    if bbox.min.Y != 0.0:
        y_shift = -bbox.min.Y
        assembly = assembly.moved(Location((0, y_shift, 0)))
        bbox = assembly.bounding_box()
        dx = bbox.max.X - bbox.min.X
        dy = bbox.max.Y - bbox.min.Y
        dz = bbox.max.Z - bbox.min.Z

    print(f"\nГабаритные размеры модели по осям БАЗИС-МЕБЕЛЬЩИК:")
    print(f"X (Ширина): {dx:.1f} мм (по чертежу: 500.0 мм)")
    print(f"Y (Высота): {dy:.1f} мм (глубина чаши с бортиком: 202.0 мм)")
    print(f"Z (Глубина): {dz:.1f} мм (по чертежу: 500.0 мм)")
    print(f"Базовое основание дна: Y_min = {bbox.min.Y:.1f} мм, верхний бортик: Y_max = {bbox.max.Y:.1f} мм")
    print(f"Внутренний проем чаши: {BOWL_W:.1f} х {BOWL_D:.1f} мм (R10)")
    print(f"Монтажный вырез в столешнице: 460.0 х 460.0 мм")
    print(f"Количество узлов в сборке: {len(parts)}")

    # Директории вывода
    output_dir = Path("c:/Users/Den/Documents/Ai studio/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    step_file = output_dir / "kukhonnaya_moyka_chernaya_500x500.step"

    print(f"\nЭкспорт в STEP файл: {step_file} ...")
    export_step(assembly, str(step_file))
    print(f"✅ Файл успешно создан! Размер: {step_file.stat().st_size} байт")

    # Экспорт копии в Ai studio-new для веб-платформы
    new_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/private_step")
    new_dir.mkdir(parents=True, exist_ok=True)
    export_step(assembly, str(new_dir / "kukhonnaya_moyka_chernaya_500x500.step"))

    # Экспорт GLB превью для 3D веб-просмотра
    try:
        from build123d import export_gltf
        glb_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/previews")
        glb_dir.mkdir(parents=True, exist_ok=True)
        export_gltf(assembly, str(glb_dir / "kukhonnaya_moyka_chernaya_500x500.glb"), binary=True)
        print("✅ GLB-превью успешно экспортировано!")
    except Exception as e:
        print(f"Экспорт GLB: {e}")

if __name__ == "__main__":
    build_black_kitchen_sink()
