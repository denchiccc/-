import sys
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
sys.stdout.reconfigure(encoding='utf-8')

from build123d import *

def build_plinth_assembly(length: float = 300.0):
    print(f"Построение кухонного цоколя ПВХ H=100 (Makmart MPP.01.100.4000.38)... Длина: {length} мм")

    # =========================================================================
    # ГАБАРИТЫ И ОРИЕНТАЦИЯ В САПР БАЗИС-МЕБЕЛЬЩИК:
    # X — Длина цоколя (Ширина кухни слева направо): 0 .. length (базовая 300 мм)
    #     Профиль постоянного сечения вдоль оси X позволяет накладывать
    #     плоскость эластичности по X в Базисе от 300 мм до любой длины (до 4000 мм)!
    # Y — Высота цоколя: от Y = 0.0 (пол / нижняя кромка уплотнителя) до Y = 104.0 мм (верх цоколя)
    # Z — Глубина / Толщина: от Z = 0.0 (задняя плоскость с пазом под клипсу) до Z = 13.0 мм (лицевая панель)
    # =========================================================================

    Y_BASE = 4.0      # Нижняя плоскость жесткого профиля (Y=0..4 мм занимает уплотнитель)
    Y_TOP = 104.0     # Верхняя грань профиля (высота самого профиля ровно 100.0 мм)
    Z_THICK = 13.0    # Толщина профиля цоколя 13.0 мм
    WALL_T = 1.2      # Толщина внешних стенок
    RIB_T = 0.9       # Толщина внутренних перегородок

    # -------------------------------------------------------------------------
    # 1. Tsokol_Profil_PVKh (Основной несущий профиль цоколя H=100 мм)
    # -------------------------------------------------------------------------
    # Строим 2D-сечение профиля в плоскости YZ на X = 0, затем выдавливаем вдоль оси X на `length`
    with BuildPart() as plinth_builder:
        with BuildSketch(Plane.YZ) as sk_plinth:
            # Наружный габарит профиля: Y от Y_BASE до Y_TOP, Z от 0 до Z_THICK
            with BuildLine():
                # Наружный прямоугольник профиля с небольшим скосом/фаской 0.5 мм на верхнем лицевом ребре
                l_bot = Line((Y_BASE, 0), (Y_BASE, Z_THICK))
                l_front = Line((Y_BASE, Z_THICK), (Y_TOP - 0.5, Z_THICK))
                c_bevel = Line((Y_TOP - 0.5, Z_THICK), (Y_TOP, Z_THICK - 0.5))
                l_top = Line((Y_TOP, Z_THICK - 0.5), (Y_TOP, 0))
                l_back_top = Line((Y_TOP, 0), (60.0, 0))
                
                # Паз под клипсу опоры на тыльной стороне (Z = 0)
                # Верхняя губка паза (Y = 56.5 .. 60.0, глубина 1.4 мм)
                p_clip1 = Line((60.0, 0), (60.0, 4.0))
                p_clip2 = Line((60.0, 4.0), (48.0, 4.0))
                p_clip3 = Line((48.0, 4.0), (48.0, 0))
                
                # Нижняя часть тыльной стенки
                l_back_bot = Line((48.0, 0), (Y_BASE, 0))
            make_face()

            # Внутренний паз под фиксацию защелки клипсы:
            # Вырез отверстия прорези клипсы (окно высотой 5.0 мм от Y=51.5 до Y=56.5)
            # В наружном контуре уже сделана ниша 48..60 глубиной 4 мм.
            # Теперь добавим удерживающие выступы (зубья защелки):
            with Locations(Location((58.25, 0.7))):
                Rectangle(3.5, 1.4, align=(Align.CENTER, Align.CENTER))
            with Locations(Location((49.75, 0.7))):
                Rectangle(3.5, 1.4, align=(Align.CENTER, Align.CENTER))

            # Вычитаем внутренние полые камеры (ячеистая сотовая структура ПВХ)
            # Камеры разделены перегородками RIB_T = 0.9 мм
            chambers_y = [
                (98.5, 102.8),  # Верхняя малая камера
                (89.5, 97.6),   # Камера 2
                (73.5, 88.6),   # Камера 3
                (61.5, 72.6),   # Камера над пазом клипсы
                (31.5, 46.5),   # Камера под пазом клипсы
                (14.5, 30.6),   # Камера 6
                (8.5, 13.6),    # Камера над пазом уплотнителя
            ]
            
            for y_min, y_max in chambers_y:
                h_ch = y_max - y_min
                y_c = (y_min + y_max) / 2.0
                with Locations(Location((y_c, Z_THICK / 2.0))):
                    Rectangle(h_ch, Z_THICK - 2 * WALL_T, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

            # Камера перед пазом клипсы (Y = 48.0 .. 60.0, Z = 5.0 .. 11.8)
            with Locations(Location((54.0, (4.9 + Z_THICK - WALL_T) / 2.0))):
                Rectangle(12.0 - 2 * RIB_T, (Z_THICK - WALL_T) - 4.9, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

            # Паз под уплотнитель в нижнем торце (Y = Y_BASE = 4.0)
            # Гарпунный паз: ширина зева 2.8 мм, внутренняя Т-полость 4.2 мм, глубина 3.5 мм (Y = 4.0 .. 7.5)
            with Locations(Location((Y_BASE + 1.2, 5.0))):
                Rectangle(2.4, 2.8, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
            with Locations(Location((Y_BASE + 2.8, 5.0))):
                Rectangle(1.6, 4.2, align=(Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Выдавливаем профиль цоколя вдоль оси X от X = 0 до X = length
        extrude(sk_plinth.sketch, amount=length)

    plinth = plinth_builder.part
    plinth.label = "Tsokol_Profil_PVKh"
    # Декоративная пленка Золото шлифованное (38 Makmart) / брашированная латунь
    plinth.color = Color(0.82, 0.68, 0.32)

    # -------------------------------------------------------------------------
    # 2. Uplotnitel_Vodootboynik (Эластичный силиконовый уплотнитель)
    # Защищает от попадания влаги и крошек под кухню, плотно прилегает к полу на Y=0
    # -------------------------------------------------------------------------
    with BuildPart() as seal_builder:
        with BuildSketch(Plane.YZ) as sk_seal:
            # Т-образный гарпунный хвостовик, подошва и наклонный водоотбойный лепесток
            Polygon([
                (Y_BASE, 3.8),
                (Y_BASE + 2.4, 3.8),
                (Y_BASE + 2.4, 3.2),
                (Y_BASE + 3.4, 4.8),
                (Y_BASE + 3.4, 5.2),
                (Y_BASE + 2.4, 6.8),
                (Y_BASE + 2.4, 6.2),
                (Y_BASE, 6.2),
                (Y_BASE, 0.5),
                (3.2, 0.5),
                (3.2, 12.8),
                (0.0, 15.0),   # Лепесток касается пола на Y = 0.0 мм
                (0.6, 14.8),
                (Y_BASE, 13.0)
            ])

        # Выдавливаем уплотнитель вдоль оси X на всю длину цоколя
        extrude(sk_seal.sketch, amount=length)

    seal = seal_builder.part
    seal.label = "Uplotnitel_Vodootboynik"
    # Полупрозрачный / светло-серый мягкий силикон
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
    step_filename = f"plinth_pvc_100_L{int(length) if length.is_integer() else length}.step"
    step_file = out_dir / step_filename

    print(f"Экспорт сборки в {step_file}...")
    export_step(assembly, str(step_file))

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
    # Построение цоколей длиной 1200 мм и 534 мм для Базиса
    build_plinth_assembly(length=1200.0)
    print("\n" + "="*60 + "\n")
    build_plinth_assembly(length=534.0)
