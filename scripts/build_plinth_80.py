import sys
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
sys.stdout.reconfigure(encoding='utf-8')

from build123d import *

def build_plinth_assembly(length: float = 1180.0, height: float = 80.0, depth: float = 12.0):
    print(f"Построение кухонного цоколя ПВХ H={height} мм, L={length} мм, D={depth} мм...")

    # =========================================================================
    # ГАБАРИТЫ И ОРИЕНТАЦИЯ В САПР БАЗИС-МЕБЕЛЬЩИК:
    # X — Ширина / Длина цоколя: 0.0 .. length (1180.0 мм)
    # Y — Высота: от Y = 0.0 (пол / водоотбойник) до Y = 80.0 мм (верхняя кромка)
    # Z — Глубина / Толщина: от Z = 0.0 (тыл с пазом под клипсу) до Z = 12.0 мм (лицевая панель)
    # =========================================================================

    Y_FLOOR = 0.0
    Y_BASE = 3.5      # Нижний срез жесткого ПВХ профиля (Y=0..3.5 мм занимает водоотбойник)
    Y_TOP = height    # Верхняя грань цоколя (80.0 мм)
    Z_THICK = depth   # Толщина профиля (12.0 мм)
    WALL_T = 1.1      # Толщина внешних стенок
    RIB_T = 0.8       # Толщина внутренних перегородок

    # -------------------------------------------------------------------------
    # 1. Tsokol_Profil_PVKh (Основной несущий профиль цоколя H=80 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as plinth_builder:
        with BuildSketch(Plane.YZ) as sk_plinth:
            with BuildLine():
                # Контур наружного габарита профиля с фаской 0.5 мм на верхнем лицевом ребре
                Line((Y_BASE, 0), (Y_BASE, Z_THICK))
                Line((Y_BASE, Z_THICK), (Y_TOP - 0.5, Z_THICK))
                Line((Y_TOP - 0.5, Z_THICK), (Y_TOP, Z_THICK - 0.5))
                Line((Y_TOP, Z_THICK - 0.5), (Y_TOP, 0))
                Line((Y_TOP, 0), (48.0, 0))
                
                # Паз под клипсу опоры на тыльной стороне (Z = 0)
                # Диапазон Y = 36.0 .. 48.0, глубина 3.5 мм
                Line((48.0, 0), (48.0, 3.5))
                Line((48.0, 3.5), (36.0, 3.5))
                Line((36.0, 3.5), (36.0, 0))
                Line((36.0, 0), (Y_BASE, 0))
            make_face()

            # Зубья защелки клипсы опоры
            with Locations(Location((46.5, 0.6))):
                Rectangle(3.0, 1.2, align=(Align.CENTER, Align.CENTER))
            with Locations(Location((37.5, 0.6))):
                Rectangle(3.0, 1.2, align=(Align.CENTER, Align.CENTER))

            # Внутренние полые камеры жесткости (ячеистая сотовая структура ПВХ)
            chambers_y = [
                (73.5, 78.5),
                (61.5, 72.5),
                (49.0, 60.5),
                (24.0, 35.0),
                (12.0, 23.0),
                (7.0, 11.0)
            ]
            for y_min, y_max in chambers_y:
                h_ch = y_max - y_min
                yc = (y_min + y_max) / 2.0
                with Locations(Location((yc, Z_THICK / 2.0))):
                    Rectangle(h_ch, Z_THICK - 2 * WALL_T, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

            # Камера перед пазом клипсы
            with Locations(Location((42.0, (4.0 + Z_THICK - WALL_T) / 2.0))):
                Rectangle(12.0 - 2 * RIB_T, (Z_THICK - WALL_T) - 4.0, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

            # Нижний гарпунный паз под силиконовый уплотнитель (по центру Z = 6.0)
            # Входной зев (Y = 3.5 .. 4.8)
            with Locations(Location((Y_BASE + 0.65, 6.0))):
                Rectangle(1.3, 2.4, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
            # Внутренняя расширенная полость фиксатора (Y = 4.8 .. 6.2)
            with Locations(Location((Y_BASE + 2.0, 6.0))):
                Rectangle(1.4, 4.2, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Выдавливаем профиль цоколя вдоль оси X от 0 до length
        extrude(sk_plinth.sketch, amount=length)

    plinth = plinth_builder.part
    plinth.label = "Tsokol_Profil_PVKh"
    # Декоративное покрытие: матовый алюминий / шампань
    plinth.color = Color(0.60, 0.62, 0.65)

    # -------------------------------------------------------------------------
    # 2. Uplotnitel_Vodootboynik (Мягкий силиконовый водоотталкивающий уплотнитель)
    # -------------------------------------------------------------------------
    with BuildPart() as seal_builder:
        with BuildSketch(Plane.YZ) as sk_seal:
            # Т-образный гарпунный хвостовик, основание и водоотбойный лепесток к полу
            Polygon([
                (Y_BASE - 0.1, 4.9),
                (Y_BASE + 1.8, 4.9),
                (Y_BASE + 1.3, 4.0),
                (Y_BASE + 2.6, 5.8),
                (Y_BASE + 2.6, 6.2),
                (Y_BASE + 1.3, 8.0),
                (Y_BASE + 1.8, 7.1),
                (Y_BASE - 0.1, 7.1),
                (Y_BASE - 0.1, 11.5),
                (Y_FLOOR, 12.0),       # Лепесток плотно прилегает к полу на Y = 0.0 мм
                (Y_FLOOR + 0.6, 11.5),
                (Y_FLOOR + 0.8, 2.5),
                (Y_FLOOR, 0.5),        # Опорная пяточка уплотнителя на полу
                (Y_BASE - 0.1, 0.5),
            ])
        # Выдавливаем уплотнитель вдоль оси X на всю длину цоколя
        extrude(sk_seal.sketch, amount=length)

    seal = seal_builder.part
    seal.label = "Uplotnitel_Vodootboynik"
    # Полупрозрачный силикон
    seal.color = Color(0.85, 0.85, 0.88)

    # =========================================================================
    # СБОРКА И ЭКСПОРТ В STEP ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    print("Формирование иерархии сборки...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[plinth, seal]
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    len_str = f"{int(length)}" if length.is_integer() else f"{length}"
    h_str = f"{int(height)}" if height.is_integer() else f"{height}"
    d_str = f"{int(depth)}" if depth.is_integer() else f"{depth}"
    step_filename = f"plinth_{len_str}x{h_str}x{d_str}.step"
    step_file = out_dir / step_filename

    print(f"Экспорт сборки в {step_file}...")
    export_step(assembly, str(step_file))

    # Также сохраняем альтернативное имя с указанием длины
    export_step(assembly, str(out_dir / f"plinth_{h_str}_L{len_str}.step"))

    bbox = assembly.bounding_box()
    dx = round(bbox.size.X, 2)
    dy = round(bbox.size.Y, 2)
    dz = round(bbox.size.Z, 2)

    min_x, max_x = round(bbox.min.X, 2), round(bbox.max.X, 2)
    min_y, max_y = round(bbox.min.Y, 2), round(bbox.max.Y, 2)
    min_z, max_z = round(bbox.min.Z, 2), round(bbox.max.Z, 2)

    print(f"\n✅ Файл успешно создан: {step_file.resolve()}")
    print(f"Габариты сборки: X={dx} мм, Y={dy} мм, Z={dz} мм")
    print(f"Диапазоны осей: X=[{min_x}..{max_x}], Y=[{min_y}..{max_y}], Z=[{min_z}..{max_z}]")
    print("Состав сборки:")
    for child in assembly.children:
        c = getattr(child, 'color', None)
        rgb_str = f"RGB{tuple(round(v, 2) for v in tuple(c)[:3])}" if c else "None"
        print(f"  - {child.label}: {rgb_str}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Построение цоколя для Базис-Мебельщик")
    parser.add_argument("--length", type=float, default=1083.0, help="Длина / ширина цоколя (мм)")
    parser.add_argument("--height", type=float, default=80.0, help="Высота цоколя (мм)")
    parser.add_argument("--depth", type=float, default=12.0, help="Глубина / толщина цоколя (мм)")
    args = parser.parse_args()

    build_plinth_assembly(length=args.length, height=args.height, depth=args.depth)
