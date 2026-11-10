"""
Скрипт генерации 3D-модели алюминиевой рамочной двери (фасада)
из профиля MODUS MZ 02 под стекло 4 мм с габаритами 497 х 895 мм
для САПР «Базис-Мебельщик».

Строго соблюдает правила Базис-Мебельщика:
  X — Ширина (0.0 .. 497.0 мм)
  Y — Высота (0.0 .. 895.0 мм, нижний торец на Y = 0.0)
  Z — Глубина (0.0 .. 20.5 мм, задняя плоскость на Z = 0.0, лицевая на Z = 20.5 мм)
"""
import os
import build123d as bd

# Габариты рамки фасада по ТЗ
FRAME_WIDTH = 497.0
FRAME_HEIGHT = 895.0
FRAME_DEPTH = 20.5

# Цвета для Базис-Мебельщика
COLOR_ALUMINUM = bd.Color(0.60, 0.62, 0.65)   # Матовый анодированный алюминий (серебро)
COLOR_STEEL = bd.Color(0.72, 0.72, 0.75)      # Оцинкованная сталь (стяжные уголки)
COLOR_GLASS = bd.Color(0.80, 0.88, 0.90)      # Стекло 4 мм (прозрачно-голубоватый)
COLOR_RUBBER = bd.Color(0.15, 0.15, 0.15)     # Черный уплотнитель MZ

def create_facade_frame():
    # -------------------------------------------------------------------------
    # 1. 2D-КОНТУР СЕЧЕНИЯ ПРОФИЛЯ MZ 02
    # По чертежу:
    #   Ширина u in [0.0 .. 19.0] мм (u=0 - наружный периметр, u=19 - внутренний край)
    #   Глубина v in [0.0 .. 20.5] мм (v=0 - тыльная грань, v=20.5 - лицевой фланец)
    #   Лицевой фланец: u in [0.0 .. 8.0] при v = 20.5
    #   Паз под стекло: глубина от фланца 5.2 мм (до полочки v = 13.8)
    #   Углубление под уплотнитель: 6.2 мм (полочка v = 12.8 при u in [1.5 .. 6.0])
    # -------------------------------------------------------------------------
    outer_pts = [
        (0.0, 0.0),
        (0.0, 20.5),
        (8.0, 20.5),
        (8.0, 19.0),
        (1.5, 19.0),
        (1.5, 12.8),
        (6.0, 12.8),
        (6.0, 13.8),
        (19.0, 13.8),
        (19.0, 0.0)
    ]

    # Внутренняя полая камера с ребрами под стяжной уголок
    inner_pts = [
        (1.5, 1.5),
        (1.5, 5.5),
        (3.5, 5.5),
        (3.5, 6.7),
        (1.5, 6.7),
        (1.5, 11.3),
        (6.0, 11.3),
        (6.0, 12.3),
        (17.5, 12.3),
        (17.5, 6.7),
        (15.5, 6.7),
        (15.5, 5.5),
        (17.5, 5.5),
        (17.5, 1.5)
    ]

    # Ось вращения по центру фасада для создания симметричных элементов
    center_axis = bd.Axis((FRAME_WIDTH / 2.0, FRAME_HEIGHT / 2.0, 0.0), (0, 0, 1))

    # -------------------------------------------------------------------------
    # 2. ГОРИЗОНТАЛЬНЫЕ ПРОФИЛИ (Нижний и Верхний)
    # Сечение в плоскости YZ: Y = u (0..19), Z = v (0..20.5)
    # Длина W = 497 мм вдоль оси X
    # Запил под 45 градусов на обоих концах
    # -------------------------------------------------------------------------
    face_yz_out = bd.Wire.make_polygon([bd.Vector(0, y, z) for y, z in outer_pts])
    face_yz_in = bd.Wire.make_polygon([bd.Vector(0, y, z) for y, z in inner_pts])
    face_yz = bd.Face(face_yz_out, [face_yz_in])

    def make_horizontal_profile(length):
        # Выдавливаем строго вдоль оси +X
        solid = bd.extrude(face_yz, amount=length, dir=(1, 0, 0))
        # Срезаем левый торец под 45°: плоскость Y = X
        tri_l = bd.Face(bd.Wire.make_polygon([
            bd.Vector(-5, -5, 0), bd.Vector(-5, 30, 0), bd.Vector(30, 30, 0)
        ]))
        cutter_l = bd.extrude(tri_l, amount=30.0).move(bd.Location((0, 0, -5)))

        # Срезаем правый торец под 45°: плоскость Y = (L - X)
        tri_r = bd.Face(bd.Wire.make_polygon([
            bd.Vector(length + 5, -5, 0), bd.Vector(length + 5, 30, 0), bd.Vector(length - 30, 30, 0)
        ]))
        cutter_r = bd.extrude(tri_r, amount=30.0).move(bd.Location((0, 0, -5)))

        return solid - cutter_l - cutter_r

    s_prof_bot = make_horizontal_profile(FRAME_WIDTH)
    prof_bot = bd.Part(s_prof_bot.wrapped)
    prof_bot.label = "Profil_Nizhniy"
    prof_bot.color = COLOR_ALUMINUM

    s_prof_top = s_prof_bot.rotate(center_axis, 180.0)
    prof_top = bd.Part(s_prof_top.wrapped)
    prof_top.label = "Profil_Verhniy"
    prof_top.color = COLOR_ALUMINUM

    # -------------------------------------------------------------------------
    # 3. ВЕРТИКАЛЬНЫЕ ПРОФИЛИ (Левый и Правый)
    # Сечение в плоскости XZ: X = u (0..19), Z = v (0..20.5)
    # Длина H = 895 мм вдоль оси Y
    # Запил под 45 градусов на обоих концах
    # -------------------------------------------------------------------------
    face_xz_out = bd.Wire.make_polygon([bd.Vector(x, 0, z) for x, z in outer_pts])
    face_xz_in = bd.Wire.make_polygon([bd.Vector(x, 0, z) for x, z in inner_pts])
    face_xz = bd.Face(face_xz_out, [face_xz_in])

    def make_vertical_profile(length):
        # Выдавливаем строго вдоль оси +Y
        solid = bd.extrude(face_xz, amount=length, dir=(0, 1, 0))
        # Срезаем нижний торец под 45°: плоскость X = Y
        tri_b = bd.Face(bd.Wire.make_polygon([
            bd.Vector(-5, -5, 0), bd.Vector(30, -5, 0), bd.Vector(30, 30, 0)
        ]))
        cutter_b = bd.extrude(tri_b, amount=30.0).move(bd.Location((0, 0, -5)))

        # Срезаем верхний торец под 45°: плоскость X = (L - Y)
        tri_t = bd.Face(bd.Wire.make_polygon([
            bd.Vector(-5, length + 5, 0), bd.Vector(30, length + 5, 0), bd.Vector(30, length - 30, 0)
        ]))
        cutter_t = bd.extrude(tri_t, amount=30.0).move(bd.Location((0, 0, -5)))

        return solid - cutter_b - cutter_t

    s_prof_left = make_vertical_profile(FRAME_HEIGHT)
    prof_left = bd.Part(s_prof_left.wrapped)
    prof_left.label = "Profil_Levyy"
    prof_left.color = COLOR_ALUMINUM

    s_prof_right = s_prof_left.rotate(center_axis, 180.0)
    prof_right = bd.Part(s_prof_right.wrapped)
    prof_right.label = "Profil_Pravyy"
    prof_right.color = COLOR_ALUMINUM

    # -------------------------------------------------------------------------
    # 4. СТЕКЛО 4 ММ (Steklo_4mm)
    # По каталогу MODUS:
    #   Ширина стекла: W_steklo = W - 5 мм = 492.0 мм (X in [2.5 .. 494.5])
    #   Высота стекла: H_steklo = H - 5 мм = 890.0 мм (Y in [2.5 .. 892.5])
    #   Толщина: 4.0 мм (Z in [14.4 .. 18.4] внутри паза 5.2 мм)
    # -------------------------------------------------------------------------
    glass_box = bd.Box(
        FRAME_WIDTH - 5.0,
        FRAME_HEIGHT - 5.0,
        4.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
    ).move(bd.Location((FRAME_WIDTH / 2.0, FRAME_HEIGHT / 2.0, 16.4)))

    steklo_part = bd.Part(glass_box.wrapped)
    steklo_part.label = "Steklo_4mm"
    steklo_part.color = COLOR_GLASS

    # -------------------------------------------------------------------------
    # 5. СИЛИКОНОВЫЙ УПЛОТНИТЕЛЬ MZ (Uplotnitel_MZ)
    # Эластичный профиль, охватывающий кромку стекла по периметру
    # -------------------------------------------------------------------------
    uplotnitel_outer = bd.Box(
        FRAME_WIDTH - 3.4,
        FRAME_HEIGHT - 3.4,
        5.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
    ).move(bd.Location((FRAME_WIDTH / 2.0, FRAME_HEIGHT / 2.0, 16.4)))

    # Вырезаем внутреннюю часть (открытое световое поле) и паз под стекло
    uplotnitel_inner = bd.Box(
        FRAME_WIDTH - 36.0,
        FRAME_HEIGHT - 36.0,
        6.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
    ).move(bd.Location((FRAME_WIDTH / 2.0, FRAME_HEIGHT / 2.0, 16.4)))

    uplotnitel_solid = (uplotnitel_outer - uplotnitel_inner) - glass_box
    uplotnitel_part = bd.Part(uplotnitel_solid.wrapped)
    uplotnitel_part.label = "Uplotnitel_MZ"
    uplotnitel_part.color = COLOR_RUBBER

    # -------------------------------------------------------------------------
    # 6. СТЯЖНЫЕ УГОЛКИ (Ugolok_Styazhnoy_1 .. 4)
    # Узкие оцинкованные стальные уголки внутри камеры профиля
    # Полочки 40 х 14 мм, толщина 2.5 мм, Z in [2.5 .. 5.0]
    # -------------------------------------------------------------------------
    # Нижний левый уголок
    ugol_w1 = bd.Box(40, 14, 2.5, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).move(bd.Location((15, 9.5, 2.5)))
    ugol_w2 = bd.Box(14, 40, 2.5, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).move(bd.Location((9.5, 15, 2.5)))
    ugol_bl = ugol_w1 + ugol_w2

    ugol1 = bd.Part(ugol_bl.wrapped)
    ugol1.label = "Ugolok_Styazhnoy_1"
    ugol1.color = COLOR_STEEL

    # Нижний правый
    ugol_br = ugol_bl.rotate(bd.Axis((FRAME_WIDTH / 2.0, 9.5, 0.0), (0, 0, 1)), 180.0) # или mirror
    # Для математической точности повернем относительно центра угла
    ugol_br = ugol_bl.rotate(center_axis, 180.0).rotate(bd.Axis((FRAME_WIDTH/2.0, FRAME_HEIGHT/2.0, 0), (1, 0, 0)), 180.0) # mirror across X
    # Проще отразить / сместить явно:
    ugol_br_w1 = bd.Box(40, 14, 2.5, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.MIN)).move(bd.Location((FRAME_WIDTH - 15, 9.5, 2.5)))
    ugol_br_w2 = bd.Box(14, 40, 2.5, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).move(bd.Location((FRAME_WIDTH - 9.5, 15, 2.5)))
    ugol2 = bd.Part((ugol_br_w1 + ugol_br_w2).wrapped)
    ugol2.label = "Ugolok_Styazhnoy_2"
    ugol2.color = COLOR_STEEL

    # Верхний правый (180 град от ugol1)
    ugol3 = bd.Part(ugol_bl.rotate(center_axis, 180.0).wrapped)
    ugol3.label = "Ugolok_Styazhnoy_3"
    ugol3.color = COLOR_STEEL

    # Верхний левый (180 град от ugol2)
    ugol4 = bd.Part(ugol2.rotate(center_axis, 180.0).wrapped)
    ugol4.label = "Ugolok_Styazhnoy_4"
    ugol4.color = COLOR_STEEL

    # -------------------------------------------------------------------------
    # КОРНЕВАЯ СБОРКА
    # -------------------------------------------------------------------------
    assembly = bd.Compound(
        label="Furnitura_Assembly",
        children=[
            prof_bot,
            prof_top,
            prof_left,
            prof_right,
            steklo_part,
            uplotnitel_part,
            ugol1,
            ugol2,
            ugol3,
            ugol4
        ]
    )
    return assembly

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    asm = create_facade_frame()

    step_path = "output/facade_frame_mz02_497x895.step"
    bd.export_step(asm, step_path)
    print(f"Exported STEP to {step_path}")

    # Создаем также стандартное короткое имя
    step_short = "output/facade_frame_mz02.step"
    bd.export_step(asm, step_short)
    print(f"Exported STEP to {step_short}")

    # Проверка габаритов сборки
    bb = asm.bounding_box()
    print("Габариты сборки:")
    print(f"  X (Ширина): min={bb.min.X:.2f}, max={bb.max.X:.2f}, размер={bb.size.X:.2f} мм")
    print(f"  Y (Высота): min={bb.min.Y:.2f}, max={bb.max.Y:.2f}, размер={bb.size.Y:.2f} мм")
    print(f"  Z (Глубина): min={bb.min.Z:.2f}, max={bb.max.Z:.2f}, размер={bb.size.Z:.2f} мм")
    print("\nДетали сборки:")
    for c in asm.children:
        b = c.bounding_box()
        print(f"  - {c.label:20s}: X=[{b.min.X:.1f}..{b.max.X:.1f}] Y=[{b.min.Y:.1f}..{b.max.Y:.1f}] Z=[{b.min.Z:.1f}..{b.max.Z:.1f}]")
