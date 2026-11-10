"""
Скрипт генерации 3D-модели черного ретро-холодильника DEXP (470 x 835 x 435 мм)
для САПР «Базис-Мебельщик».

Строго соблюдает ориентацию по осям Базиса:
  X — Ширина (0.0 .. 470.0 мм)
  Y — Высота (0.0 .. 835.0 мм, ножки стоят строго на плоскости Y = 0.0)
  Z — Глубина (0.0 .. 435.0 мм, задняя стенка на Z = 0.0, фасад двери на Z = 435.0 мм)
"""
import os
import build123d as bd

# Габариты изделия по чертежу пользователя:
WIDTH = 470.0     # Ширина по оси X
HEIGHT = 835.0    # Высота по оси Y
DEPTH = 435.0     # Глубина по оси Z

# Цветовая палитра:
COLOR_BLACK_GLOSS = bd.Color(0.08, 0.08, 0.09)    # Глубокий черный глянец (эмаль корпуса и двери)
COLOR_BLACK_MATTE = bd.Color(0.16, 0.16, 0.16)    # Черный матовый пластик / резина
COLOR_CHROME = bd.Color(0.82, 0.82, 0.85)         # Полированный хром (логотип, элементы ножек)
COLOR_STEEL = bd.Color(0.65, 0.65, 0.68)          # Конструкционная оцинкованная сталь (петли)

def create_refrigerator():
    # -------------------------------------------------------------------------
    # 1. ОСНОВНОЙ КОРПУС ХОЛОДИЛЬНИКА (Korpus)
    # Габариты корпуса:
    #   X in [5.0 .. 465.0] (ширина 460 мм)
    #   Y in [25.0 .. 825.0] (высота 800 мм)
    #   Z in [0.0 .. 370.0] (глубина 370 мм)
    # Сзади снизу - технологическая ниша под компрессор
    # -------------------------------------------------------------------------
    with bd.BuildPart() as kp:
        with bd.BuildSketch(bd.Plane.XY) as s_k:
            bd.RectangleRounded(460.0, 800.0, radius=25.0)
        bd.extrude(amount=370.0)
    
    korpus_solid = kp.part.move(bd.Location((235.0, 425.0, 0.0)))

    # Скругляем верхнюю грань корпуса (при Y=825)
    try:
        top_face = korpus_solid.faces().sort_by(bd.Axis.Y)[-1]
        korpus_solid = bd.fillet(top_face.edges(), radius=15.0)
    except Exception:
        pass

    # Вырезаем нишу под компрессор сзади снизу:
    # X in [30.0 .. 440.0], Y in [25.0 .. 190.0], Z in [-1.0 .. 140.0]
    compressor_niche = bd.Box(
        410.0, 165.0, 142.0,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)
    ).move(bd.Location((235.0, 25.0, -1.0)))

    korpus_solid = korpus_solid - compressor_niche
    korpus_part = bd.Part(korpus_solid.wrapped)
    korpus_part.label = "Korpus"
    korpus_part.color = COLOR_BLACK_GLOSS

    # -------------------------------------------------------------------------
    # 2. РЕТРО-ДВЕРЦА (Dver)
    # Габариты дверцы:
    #   X in [0.0 .. 470.0] (полная ширина 470 мм)
    #   Y in [28.0 .. 830.0] (высота 802 мм)
    #   Z in [375.0 .. 435.0] (толщина 60 мм, выпуклая форма с R=18 мм по периметру)
    # -------------------------------------------------------------------------
    with bd.BuildPart() as dp:
        with bd.BuildSketch() as s_d:
            bd.RectangleRounded(470.0, 802.0, radius=35.0)
        bd.extrude(amount=60.0)
        front_face = dp.faces().filter_by(bd.Axis.Z).sort_by(bd.Axis.Z)[-1]
        bd.fillet(front_face.edges(), radius=18.0)
    
    door_solid = dp.part.move(bd.Location((235.0, 429.0, 375.0)))

    # Выемка под встроенную скрытую ручку на левом торце (X in [-1.0 .. 22.0], Y in [660 .. 760], Z in [395 .. 430])
    handle_pocket = bd.Box(
        25.0, 100.0, 36.0,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)
    ).move(bd.Location((-1.0, 710.0, 412.0)))
    try:
        handle_pocket = bd.fillet(handle_pocket.edges(), radius=5.0)
    except Exception:
        pass

    door_solid = door_solid - handle_pocket
    door_part = bd.Part(door_solid.wrapped)
    door_part.label = "Dver"
    door_part.color = COLOR_BLACK_GLOSS

    # -------------------------------------------------------------------------
    # 3. РУЧКА-ВСТАВКА (Ruchka_Dveri)
    # -------------------------------------------------------------------------
    handle_insert = bd.Box(
        18.0, 96.0, 32.0,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)
    ).move(bd.Location((1.0, 710.0, 412.0)))
    handle_part = bd.Part(handle_insert.wrapped)
    handle_part.label = "Ruchka_Dveri"
    handle_part.color = COLOR_BLACK_MATTE

    # -------------------------------------------------------------------------
    # 4. ЛОГОТИП DEXP (Logotip_Dexp)
    # Хромированный винтажный шильдик на фасаде двери:
    # По центру X = 235 мм, Y = 735 мм, Z = 434.0 .. 435.0 мм
    # -------------------------------------------------------------------------
    logo_base = bd.Box(
        70.0, 22.0, 1.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).move(bd.Location((235.0, 735.0, 435.0)))
    logo_part = bd.Part(logo_base.wrapped)
    logo_part.label = "Logotip_Dexp"
    logo_part.color = COLOR_CHROME

    # -------------------------------------------------------------------------
    # 5. МАГНИТНЫЙ УПЛОТНИТЕЛЬ ДВЕРИ (Uplotnitel_Dveri)
    # Z in [370.0 .. 375.0] (толщина 5 мм)
    # -------------------------------------------------------------------------
    with bd.BuildPart() as up:
        with bd.BuildSketch() as s_u_out:
            bd.RectangleRounded(440.0, 775.0, radius=20.0)
        bd.extrude(amount=5.0)
        with bd.BuildSketch() as s_u_in:
            bd.RectangleRounded(390.0, 725.0, radius=10.0)
        bd.extrude(amount=5.1, mode=bd.Mode.SUBTRACT)

    seal_solid = up.part.move(bd.Location((235.0, 429.0, 370.0)))
    seal_part = bd.Part(seal_solid.wrapped)
    seal_part.label = "Uplotnitel_Dveri"
    seal_part.color = COLOR_BLACK_MATTE

    # -------------------------------------------------------------------------
    # 6. ОПОРЫ / НОЖКИ (Nozhki_Perednie, Nozhki_Zadnie)
    # Высота ножек: от Y = 0.0 до Y = 25.0 мм
    # -------------------------------------------------------------------------
    def make_front_foot(pos_x, pos_z, label):
        base = bd.Cylinder(radius=15.0, height=15.0).rotate(bd.Axis.X, 90).move(bd.Location((pos_x, 7.5, pos_z)))
        stem = bd.Cylinder(radius=5.0, height=10.0).rotate(bd.Axis.X, 90).move(bd.Location((pos_x, 20.0, pos_z)))
        foot = base + stem
        part = bd.Part(foot.wrapped)
        part.label = label
        part.color = COLOR_BLACK_MATTE
        return part

    def make_rear_roller(pos_x, pos_z, label):
        roller = bd.Cylinder(radius=11.0, height=12.0).rotate(bd.Axis.Z, 90).move(bd.Location((pos_x, 11.0, pos_z)))
        bracket = bd.Box(22.0, 14.0, 26.0, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).move(bd.Location((pos_x, 11.0, pos_z)))
        assembly_roller = roller + bracket
        part = bd.Part(assembly_roller.wrapped)
        part.label = label
        part.color = COLOR_STEEL
        return part

    nozhka_p_l = make_front_foot(50.0, 340.0, "Nozhka_Perednyaya_Levaya")
    nozhka_p_r = make_front_foot(420.0, 340.0, "Nozhka_Perednyaya_Pravaya")
    nozhka_z_l = make_rear_roller(50.0, 45.0, "Nozhka_Zadnyaya_Levaya")
    nozhka_z_r = make_rear_roller(420.0, 45.0, "Nozhka_Zadnyaya_Pravaya")

    # -------------------------------------------------------------------------
    # 7. ПЕТЛИ ДВЕРИ (Petlya_Verhnyaya, Petlya_Nizhnyaya)
    # -------------------------------------------------------------------------
    # Верхняя петля с декоративной крышкой: Y in [825.0 .. 835.0] (максимум ровно 835.0 мм!)
    with bd.BuildPart() as v_petlya:
        with bd.BuildSketch(bd.Plane.XZ) as s_vp:
            bd.RectangleRounded(30.0, 35.0, radius=8.0)
        bd.extrude(amount=10.0, dir=(0, 1, 0)) # Y from 0 to 10
    top_hinge_solid = v_petlya.part.move(bd.Location((440.0, 825.0, 365.0)))
    top_hinge_part = bd.Part(top_hinge_solid.wrapped)
    top_hinge_part.label = "Petlya_Verhnyaya"
    top_hinge_part.color = COLOR_BLACK_MATTE

    # Нижний металлический шарнир петли: Y in [19.0 .. 28.0]
    bracket = bd.Box(30.0, 5.0, 30.0, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).move(bd.Location((440.0, 20.0, 370.0)))
    pin = bd.Cylinder(radius=4.0, height=8.0).rotate(bd.Axis.X, 90).move(bd.Location((445.0, 26.0, 375.0)))
    bot_hinge_solid = bracket + pin
    bot_hinge_part = bd.Part(bot_hinge_solid.wrapped)
    bot_hinge_part.label = "Petlya_Nizhnyaya"
    bot_hinge_part.color = COLOR_STEEL

    # -------------------------------------------------------------------------
    # 8. КОМПРЕССОР В ТЕХНИЧЕСКОЙ НИШЕ
    # -------------------------------------------------------------------------
    c_body = bd.Cylinder(radius=45.0, height=110.0).rotate(bd.Axis.Z, 90).move(bd.Location((235.0, 75.0, 65.0)))
    c_base = bd.Box(140.0, 6.0, 50.0, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).move(bd.Location((235.0, 26.0, 65.0)))
    comp_solid = c_body + c_base
    compressor_part = bd.Part(comp_solid.wrapped)
    compressor_part.label = "Kompressor"
    compressor_part.color = COLOR_BLACK_MATTE

    # -------------------------------------------------------------------------
    # КОРНЕВАЯ СБОРКА
    # -------------------------------------------------------------------------
    assembly = bd.Compound(
        label="Furnitura_Assembly",
        children=[
            korpus_part,
            door_part,
            handle_part,
            logo_part,
            seal_part,
            top_hinge_part,
            bot_hinge_part,
            nozhka_p_l,
            nozhka_p_r,
            nozhka_z_l,
            nozhka_z_r,
            compressor_part
        ]
    )

    return assembly

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    asm = create_refrigerator()

    step_path = "output/refrigerator_dexp_black.step"
    bd.export_step(asm, step_path)
    print(f"Exported STEP to {step_path}")

    step_short = "output/refrigerator_black.step"
    bd.export_step(asm, step_short)
    print(f"Exported STEP to {step_short}")

    bb = asm.bounding_box()
    print("Габариты сборки:")
    print(f"  X (Ширина): min={bb.min.X:.2f}, max={bb.max.X:.2f}, размер={bb.size.X:.2f} мм")
    print(f"  Y (Высота): min={bb.min.Y:.2f}, max={bb.max.Y:.2f}, размер={bb.size.Y:.2f} мм")
    print(f"  Z (Глубина): min={bb.min.Z:.2f}, max={bb.max.Z:.2f}, размер={bb.size.Z:.2f} мм")

    print("\nДетали сборки:")
    for c in asm.children:
        b = c.bounding_box()
        print(f"  - {c.label:26s}: X=[{b.min.X:.1f}..{b.max.X:.1f}] Y=[{b.min.Y:.1f}..{b.max.Y:.1f}] Z=[{b.min.Z:.1f}..{b.max.Z:.1f}]")
