"""
Скрипт генерации 3D-моделей металлической фурнитуры для стеклянных дверей
по чертежу SISO (40х14 мм с поворотным штифтом и 40х22 мм зажимная планка)
для САПР «Базис-Мебельщик».

Строго соблюдает правила Базис-Мебельщика:
  X — Ширина (0.0 .. 40.0 мм)
  Y — Высота (0.0 .. Высота мм, основание лежит на плоскости Y = 0.0)
  Z — Глубина (0.0 .. Глубина мм)
"""
import os
import build123d as bd

# Цветовая палитра по правилам Базис-Мебельщика
COLOR_CHROME = bd.Color(0.75, 0.75, 0.78)   # Хром / полированная сталь
COLOR_STEEL = bd.Color(0.70, 0.70, 0.73)    # Сталь / никель
COLOR_BLACK_PLASTIC = bd.Color(0.15, 0.15, 0.15)  # Черный пластик / резина

def build_hinge_40x14():
    """
    Поворотно-осевая петля для стекла 40х14 мм с 2 прижимными винтами и штифтом.
    Габариты:
      X: [0.0 .. 40.0] (длина 40 мм)
      Y: [0.0 .. 24.0] (высота 24 мм: штифт 10 мм, корпус 14 мм)
      Z: [0.0 .. 12.0] (глубина 12 мм: винты 4 мм, корпус 8 мм)
    """
    # 1. Корпус петли (U-образный профиль 40 x 14 x 8 мм)
    with bd.BuildPart() as kp:
        with bd.BuildSketch(bd.Plane.XY) as sk:
            with bd.BuildLine() as bl:
                bd.Line((0, 10), (40, 10))
                bd.Line((40, 10), (40, 21.5))
                bd.RadiusArc((40, 21.5), (37.5, 24), radius=2.5)
                bd.Line((37.5, 24), (2.5, 24))
                bd.RadiusArc((2.5, 24), (0, 21.5), radius=2.5)
                bd.Line((0, 21.5), (0, 10))
            bd.make_face()
        bd.extrude(amount=8.0)

    korpus = kp.part.move(bd.Location((0, 0, 4)))

    # Паз под стекло: ширина 5 мм (Z in [5.5 .. 10.5]), глубина 12 мм (Y in [12.0 .. 25.0])
    slot = bd.Box(42, 13, 5).move(bd.Location((20, 18.5, 8.0)))

    # Отверстия под винты в задней стенке корпуса (Z in [4.0 .. 5.5])
    h1 = bd.Cylinder(radius=2.1, height=2.0).move(bd.Location((8.5, 17.0, 4.8)))
    h2 = bd.Cylinder(radius=2.1, height=2.0).move(bd.Location((30.0, 17.0, 4.8)))

    korpus = korpus - slot - h1 - h2
    korpus_part = bd.Part(korpus.wrapped)
    korpus_part.label = "Korpus"
    korpus_part.color = COLOR_CHROME

    # 2. Поворотный штифт (цапфа) D = 5 мм, Y in [0.0 .. 11.5]
    # На кончике штифта формируем заходную фаску 0.5 x 45°
    main_cyl = bd.Cylinder(radius=2.5, height=11.0).rotate(bd.Axis.X, 90).move(bd.Location((32.5, 6.0, 8.0)))
    tip_cone = bd.Cone(bottom_radius=2.5, top_radius=2.0, height=0.5).rotate(bd.Axis.X, 90).move(bd.Location((32.5, 0.25, 8.0)))
    shtok = main_cyl + tip_cone
    shtok_part = bd.Part(shtok.wrapped)
    shtok_part.label = "Shtok_Povorotny"
    shtok_part.color = COLOR_CHROME

    # 3. Прижимные винты со шлицем (Z in [0.0 .. 6.0])
    def make_vint(px, py, label):
        head = bd.Cylinder(radius=3.5, height=4.0).move(bd.Location((px, py, 2.0)))
        slot_tool = bd.Box(1.0, 7.2, 1.2).rotate(bd.Axis.Z, 45).move(bd.Location((px, py, 0.6)))
        shank = bd.Cylinder(radius=2.0, height=2.0).move(bd.Location((px, py, 5.0)))
        v = (head - slot_tool) + shank
        vp = bd.Part(v.wrapped)
        vp.label = label
        vp.color = COLOR_STEEL
        return vp

    vint1 = make_vint(8.5, 17.0, "Vint_Zazhimnoy_1")
    vint2 = make_vint(30.0, 17.0, "Vint_Zazhimnoy_2")

    # 4. Защитные прокладки под стекло (мягкий пластик)
    p_back = bd.Box(38.0, 11.0, 0.8).move(bd.Location((20.0, 18.0, 5.9)))
    p_front = bd.Box(38.0, 11.0, 0.8).move(bd.Location((20.0, 18.0, 10.1)))
    prok = p_back + p_front
    prok_part = bd.Part(prok.wrapped)
    prok_part.label = "Prokladka_Zashchitnaya"
    prok_part.color = COLOR_BLACK_PLASTIC

    assembly = bd.Compound(
        label="Furnitura_Assembly",
        children=[
            korpus_part,
            shtok_part,
            vint1,
            vint2,
            prok_part
        ]
    )
    return assembly

def build_clamp_40x22():
    """
    Верхняя накладка / зажим для стекла 40х22х8 мм (верхний чертеж).
    Габариты:
      X: [0.0 .. 40.0]
      Y: [0.0 .. 22.0]
      Z: [0.0 .. 8.0]
    """
    with bd.BuildPart() as cp:
        with bd.BuildSketch(bd.Plane.XY) as sk:
            with bd.BuildLine() as bl:
                bd.Line((0, 0), (40, 0))
                bd.Line((40, 0), (40, 19.5))
                bd.RadiusArc((40, 19.5), (37.5, 22), radius=2.5)
                bd.Line((37.5, 22), (2.5, 22))
                bd.RadiusArc((2.5, 22), (0, 19.5), radius=2.5)
                bd.Line((0, 19.5), (0, 0))
            bd.make_face()
        bd.extrude(amount=8.0)

    korpus = cp.part
    # Паз под стекло: ширина 5 мм (Z in [1.5 .. 6.5]), глубина 20 мм (Y in [2.0 .. 23.0])
    slot = bd.Box(42, 21, 5).move(bd.Location((20, 12.5, 4.0)))
    korpus = korpus - slot
    korpus_part = bd.Part(korpus.wrapped)
    korpus_part.label = "Korpus_Nakladka"
    korpus_part.color = COLOR_CHROME

    # Прокладки
    p1 = bd.Box(38.0, 19.0, 0.8).move(bd.Location((20.0, 12.0, 1.9)))
    p2 = bd.Box(38.0, 19.0, 0.8).move(bd.Location((20.0, 12.0, 6.1)))
    prok = p1 + p2
    prok_part = bd.Part(prok.wrapped)
    prok_part.label = "Prokladka_Nakladki"
    prok_part.color = COLOR_BLACK_PLASTIC

    clamp_asm = bd.Compound(
        label="Furnitura_Assembly",
        children=[
            korpus_part,
            prok_part
        ]
    )
    return clamp_asm

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)

    # 1. Основная петля для стекла
    hinge_asm = build_hinge_40x14()
    step_hinge = "output/glass_hinge_40x14.step"
    bd.export_step(hinge_asm, step_hinge)
    print(f"Exported Hinge to {step_hinge}")

    h_bb = hinge_asm.bounding_box()
    print("Габариты петли (glass_hinge_40x14.step):")
    print(f"  X (Ширина): min={h_bb.min.X:.2f}, max={h_bb.max.X:.2f}, размер={h_bb.size.X:.2f} мм")
    print(f"  Y (Высота): min={h_bb.min.Y:.2f}, max={h_bb.max.Y:.2f}, размер={h_bb.size.Y:.2f} мм")
    print(f"  Z (Глубина): min={h_bb.min.Z:.2f}, max={h_bb.max.Z:.2f}, размер={h_bb.size.Z:.2f} мм")

    # 2. Верхняя накладка/зажим 40х22
    clamp_asm = build_clamp_40x22()
    step_clamp = "output/glass_clamp_40x22.step"
    bd.export_step(clamp_asm, step_clamp)
    print(f"Exported Clamp to {step_clamp}")

    c_bb = clamp_asm.bounding_box()
    print("Габариты накладки (glass_clamp_40x22.step):")
    print(f"  X (Ширина): min={c_bb.min.X:.2f}, max={c_bb.max.X:.2f}, размер={c_bb.size.X:.2f} мм")
    print(f"  Y (Высота): min={c_bb.min.Y:.2f}, max={c_bb.max.Y:.2f}, размер={c_bb.size.Y:.2f} мм")
    print(f"  Z (Глубина): min={c_bb.min.Z:.2f}, max={c_bb.max.Z:.2f}, размер={c_bb.size.Z:.2f} мм")
