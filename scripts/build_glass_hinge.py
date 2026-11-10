import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
sys.stdout.reconfigure(encoding='utf-8')

from build123d import *

def build_glass_hinge_assembly():
    print("Построение металлической накладной петли для стекла без сверления...")

    # =========================================================================
    # РАЗМЕРЫ С ЧЕРТЕЖА (мм):
    # Корпус: Длина 40.0 мм, Высота 18.0 мм, Ширина 11.0 мм
    # Паз под стекло: глубина 16.5 мм, ширина 6.0 мм (толщина дна 1.5 мм, стенок 2.5 мм)
    # Опорный штифт: диаметр Ø8.5 мм, длина 9.5 мм (включая буртик 1.0 мм)
    # Зажимные винты: 2 х М4, расстояние между осями 25.0 мм
    # =========================================================================

    L_BODY = 40.0
    H_BODY = 18.0
    W_BODY = 11.0
    W_SLOT = 6.0
    D_SLOT = 16.5
    WALL_T = 2.5                      # (11 - 6) / 2 = 2.5 мм
    BOT_T = H_BODY - D_SLOT           # 18 - 16.5 = 1.5 мм

    H_PIN_TOTAL = 9.5
    H_COLLAR = 1.0
    H_PIN = H_PIN_TOTAL - H_COLLAR    # 8.5 мм
    D_PIN = 8.5
    D_COLLAR = 10.5

    # Ось штифта: 6.0 мм от правого торца корпуса (X = 34.0 мм), по центру ширины (Z = 5.5 мм)
    X_PIN = L_BODY - 6.0  # 34.0 мм
    Z_CENTER = W_BODY / 2.0  # 5.5 мм

    # Позиционирование по Y:
    # Y = 0.0 .. 8.5 мм — опорный штифт Ø8.5 мм
    # Y = 8.5 .. 9.5 мм — упорный буртик 1.0 мм
    # Y = 9.5 .. 27.5 мм — П-образный корпус петли (H=18.0 мм)
    # Y = 11.0 .. 27.5 мм — паз под стекло (глубина 16.5 мм)
    Y_PIN_BASE = 0.0
    Y_COLLAR_BASE = H_PIN             # 8.5 мм
    Y_BODY_BASE = H_PIN_TOTAL         # 9.5 мм
    Y_BODY_TOP = Y_BODY_BASE + H_BODY # 27.5 мм
    Y_SLOT_BASE = Y_BODY_TOP - D_SLOT # 11.0 мм

    # Оси винтов М4:
    # Межосевое 25.0 мм, симметрично: X = 7.5 мм и X = 32.5 мм
    X_SCREW1 = (L_BODY - 25.0) / 2.0  # 7.5 мм
    X_SCREW2 = X_SCREW1 + 25.0        # 32.5 мм
    Y_SCREWS = Y_SLOT_BASE + D_SLOT / 2.0  # 19.25 мм

    # -------------------------------------------------------------------------
    # 1. Korpus_Petli (П-образный корпус петли 40х18х11 мм)
    # -------------------------------------------------------------------------
    with BuildPart() as body_builder:
        # Строим 2D-сечение П-образного корпуса в плоскости YZ и выдавливаем вдоль X
        with BuildSketch(Plane.YZ) as sk_body:
            with BuildLine():
                # Наружный контур U-профиля со скруглениями верхних ребер R=1 мм
                l_bot = Line((Y_BODY_BASE, 0), (Y_BODY_BASE, W_BODY))
                l_front = Line((Y_BODY_BASE, W_BODY), (Y_BODY_TOP - 1.0, W_BODY))
                arc_top_front = RadiusArc((Y_BODY_TOP - 1.0, W_BODY), (Y_BODY_TOP, W_BODY - 1.0), 1.0)
                l_top_front = Line((Y_BODY_TOP, W_BODY - 1.0), (Y_BODY_TOP, W_BODY - WALL_T))
                
                # Внутренний паз под стекло (ширина 6 мм, глубина 16.5 мм)
                l_slot_down = Line((Y_BODY_TOP, W_BODY - WALL_T), (Y_SLOT_BASE, W_BODY - WALL_T))
                l_slot_bot = Line((Y_SLOT_BASE, W_BODY - WALL_T), (Y_SLOT_BASE, WALL_T))
                l_slot_up = Line((Y_SLOT_BASE, WALL_T), (Y_BODY_TOP, WALL_T))
                
                # Верхнее ребро тыльной стенки и скругление R=1 мм
                l_top_back = Line((Y_BODY_TOP, WALL_T), (Y_BODY_TOP, 1.0))
                arc_top_back = RadiusArc((Y_BODY_TOP, 1.0), (Y_BODY_TOP - 1.0, 0), 1.0)
                l_back = Line((Y_BODY_TOP - 1.0, 0), (Y_BODY_BASE, 0))
            make_face()

        # Выдавливаем корпус вдоль оси X от 0 до 40 мм
        extrude(sk_body.sketch, amount=L_BODY)

        # Буртик штифта толщиной 1.0 мм (Y = 8.5 .. 9.5 мм)
        with Locations(Location((X_PIN, Y_COLLAR_BASE, Z_CENTER))):
            Cylinder(radius=D_COLLAR / 2.0, height=H_COLLAR, align=(Align.CENTER, Align.MIN, Align.CENTER))

        # Резьбовые отверстия М4 под винты на тыльной стенке (Z = 0.0 .. 2.5 мм)
        for x_sc in [X_SCREW1, X_SCREW2]:
            with Locations(Location((x_sc, Y_SCREWS, -0.5))):
                Cylinder(radius=4.0 / 2.0, height=WALL_T + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    korpus = body_builder.part
    korpus.label = "Korpus_Petli"
    korpus.color = Color(0.75, 0.75, 0.78)  # Полированный хром / никель

    # -------------------------------------------------------------------------
    # 2. Opornyy_Shtift (Опорный штифт/цапфа оси вращения Ø8.5 мм)
    # Y = 0.0 .. 8.5 мм, ось (X_PIN, Z_CENTER)
    # -------------------------------------------------------------------------
    with BuildPart() as pin_builder:
        with Locations(Location((X_PIN, Y_PIN_BASE, Z_CENTER))):
            # Цилиндрическое тело штифта
            Cylinder(radius=D_PIN / 2.0, height=H_PIN, align=(Align.CENTER, Align.MIN, Align.CENTER))

            # Фаска на нижнем конце штифта
            face_bot = pin_builder.faces().sort_by(Axis.Y)[0]
            chamfer(face_bot.outer_wire().edge(), length=0.6)

    pin = pin_builder.part
    pin.label = "Opornyy_Shtift"
    pin.color = Color(0.80, 0.80, 0.82)  # Шлифованная нержавеющая сталь

    # -------------------------------------------------------------------------
    # 3. Vint_Zazhimnoy_1 и Vint_Zazhimnoy_2 (Прижимные винты М4 с пятаками)
    # Ось винтов направлена строго вдоль оси Z
    # Головка: Z = -2.0 .. 0.0 мм, резьба: Z = 0.0 .. 2.5 мм, пятак: Z = 2.5 .. 3.5 мм
    # -------------------------------------------------------------------------
    def make_screw(x_pos: float, label: str):
        with BuildPart() as screw_builder:
            # Полукруглая накатанная шляпка винта М4 (диаметр 7.0 мм, толщина 2.0 мм)
            with Locations(Location((x_pos, Y_SCREWS, -2.0))):
                Cylinder(radius=7.0 / 2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Шлиц под отвертку (глубина 1.0 мм)
                Box(1.0, 7.0, 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

            # Резьбовой стержень М4 (длина 2.5 мм сквозь стенку корпуса)
            with Locations(Location((x_pos, Y_SCREWS, 0.0))):
                Cylinder(radius=3.9 / 2.0, height=WALL_T, align=(Align.CENTER, Align.CENTER, Align.MIN))

            # Прижимной пятак Ø5.5 мм, толщина 1.0 мм внутри паза для мягкого зажима стекла
            with Locations(Location((x_pos, Y_SCREWS, WALL_T))):
                Cylinder(radius=5.5 / 2.0, height=1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        part = screw_builder.part
        part.label = label
        part.color = Color(0.72, 0.72, 0.75)  # Никелированная сталь
        return part

    screw1 = make_screw(X_SCREW1, "Vint_Zazhimnoy_1")
    screw2 = make_screw(X_SCREW2, "Vint_Zazhimnoy_2")

    # -------------------------------------------------------------------------
    # 4. Prokladka_Zashchitnaya (Защитная полимерная прокладка под стекло)
    # -------------------------------------------------------------------------
    with BuildPart() as pad_builder:
        with Locations(Location((L_BODY / 2.0, (Y_SLOT_BASE + Y_BODY_TOP) / 2.0, (W_BODY - WALL_T) - 0.5))):
            Box(L_BODY - 1.0, D_SLOT - 1.0, 1.0)

    prokladka = pad_builder.part
    prokladka.label = "Prokladka_Zashchitnaya"
    prokladka.color = Color(0.15, 0.15, 0.15)  # Черный эластичный пластик

    # =========================================================================
    # ВЫРАВНИВАНИЕ ПО ОСЯМ И ГАБАРИТНОЙ РАМКЕ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    # В сборку входят детали строго с чертежа:
    # Корпус, опорный штифт, 2 зажимных винта и защитная прокладка
    parts_list = [korpus, pin, screw1, screw2, prokladka]

    temp_compound = Compound(children=parts_list)
    raw_bb = temp_compound.bounding_box()

    shift_x = -raw_bb.min.X
    shift_y = -raw_bb.min.Y
    shift_z = -raw_bb.min.Z

    aligned_parts = []
    for p in parts_list:
        p_aligned = p.move(Location((shift_x, shift_y, shift_z)))
        p_aligned.label = p.label
        p_aligned.color = p.color
        aligned_parts.append(p_aligned)

    # -------------------------------------------------------------------------
    # СБОРКА И ЭКСПОРТ В STEP
    # -------------------------------------------------------------------------
    print("Формирование иерархии сборки...")
    assembly = Compound(
        label="Furnitura_Assembly",
        children=aligned_parts
    )

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    step_file = out_dir / "glass_pivot_hinge_40.step"

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
    build_glass_hinge_assembly()
