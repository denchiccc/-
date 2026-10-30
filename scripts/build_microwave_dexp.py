import os
import sys
import math
from pathlib import Path

# Принудительно устанавливаем UTF-8 для вывода в консоль Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build123d import *

def build_builtin_microwave():
    print("Начало построения встраиваемой микроволновой печи DEXP (595 × 388 × 420 мм)...")

    # =========================================================================
    # ГАБАРИТНЫЕ РАЗМЕРЫ (мм) строго по чертежу из каталога (чертеж 3)
    # =========================================================================
    # Фасадная стеклянная панель:
    FASAD_W = 595.0       # Полная ширина фасада
    FASAD_H = 388.0       # Полная высота фасада
    FASAD_T = 20.0        # Толщина фасадной рамки со стеклом (Y = 0 .. +20.0 мм)

    # Встраиваемый металлический короб (под нишу 560 х 380 х 500 мм):
    BODY_W = 513.0        # Ширина короба
    BODY_H = 378.0        # Высота короба
    BODY_D = 400.0        # Глубина короба в нишу (Y = -400.0 .. 0.0 мм)

    # Положение короба по высоте:
    # Разница по высоте фасада и короба: 388 - 378 = 10 мм.
    # Равномерный нахлест фасада: 5 мм снизу и 5 мм сверху (Z_BODY_MIN = 5.0 мм)
    Z_BODY_MIN = 5.0

    # Размеры дверцы микроволновки:
    DOOR_W = 390.0
    DOOR_H = 285.0
    DOOR_X = -FASAD_W / 2.0 + 35.0 + DOOR_W / 2.0  # Слева на фасаде
    DOOR_Z = FASAD_H / 2.0

    # =========================================================================
    # 1. Fasad_Ramka_Steklo (Внешняя фасадная рама из черного глянцевого стекла)
    # =========================================================================
    with BuildPart() as fasad_builder:
        # Основная стеклянная панель 595 х 20 х 388 мм
        with Locations(Location((0, FASAD_T / 2.0, FASAD_H / 2.0))):
            Box(FASAD_W, FASAD_T, FASAD_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Выемка под дверцу микроволновки на лицевой стороне (глубина 8 мм)
        with Locations(Location((DOOR_X, FASAD_T - 4.0, DOOR_Z))):
            Box(DOOR_W + 3.0, 9.0, DOOR_H + 3.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Выемка под сенсорную зону панели управления справа
        ctrl_w = FASAD_W - DOOR_W - 75.0  # ~130 мм
        ctrl_x = FASAD_W / 2.0 - ctrl_w / 2.0 - 25.0
        with Locations(Location((ctrl_x, FASAD_T - 2.0, DOOR_Z))):
            Box(ctrl_w, 5.0, DOOR_H, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Скругление наружных 4 вертикальных кромок стекла R2 (еврокромка)
        v_edges = fasad_builder.edges().filter_by(Axis.Z)
        corner_edges = v_edges.sort_by(Axis.X)
        outer_corners = corner_edges[:2] + corner_edges[-2:]
        fillet(outer_corners, radius=1.5)

    fasad = fasad_builder.part
    fasad.label = "Fasad_Ramka_Chernoe_Steklo"
    fasad.color = Color(0.08, 0.08, 0.10)  # Глянцевое черное стекло

    # =========================================================================
    # 2. Dver_Mikrovolnovki (Дверца с остеклением и защитной сеткой)
    # =========================================================================
    with BuildPart() as door_builder:
        # Корпус дверцы
        with Locations(Location((DOOR_X, FASAD_T - 6.0, DOOR_Z))):
            Box(DOOR_W, 10.0, DOOR_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Смотровое окно дверцы
        win_w = 265.0
        win_h = 175.0
        with Locations(Location((DOOR_X - 10.0, FASAD_T - 1.0, DOOR_Z))):
            # Внутреннее углубление окна
            Box(win_w, 4.0, win_h, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Скругление углов дверцы R3
        d_edges = door_builder.edges().filter_by(Axis.Y)
        fillet(d_edges, radius=3.0)

    door = door_builder.part
    door.label = "Dver_Mikrovolnovki"
    door.color = Color(0.12, 0.12, 0.14)  # Черная рамка дверцы

    # Смотровое стекло с защитной металлической сеткой
    with BuildPart() as window_builder:
        with Locations(Location((DOOR_X - 10.0, FASAD_T - 2.0, DOOR_Z))):
            Box(win_w - 2.0, 3.0, win_h - 2.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    window = window_builder.part
    window.label = "Smotrovoe_Steklo_Setka"
    window.color = Color(0.20, 0.22, 0.25)  # Тонированное стекло с сеткой

    # =========================================================================
    # 3. Korpus_Vstraivaemy (Встраиваемый металлический короб 513 × 378 × 400 мм)
    # =========================================================================
    with BuildPart() as body_builder:
        # Основной металлический корпус (Y от -400.0 до 0.0 мм)
        with Locations(Location((0, -BODY_D / 2.0, Z_BODY_MIN + BODY_H / 2.0))):
            Box(BODY_W, BODY_D, BODY_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        # Верхний вентиляционный скос/канал (отступ на верхней стенке)
        with Locations(Location((0, -BODY_D + 80.0, Z_BODY_MIN + BODY_H - 10.0))):
            Box(BODY_W - 40.0, 140.0, 22.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

        # Боковые вентиляционные просечки (жалюзи) справа и слева
        for sign in [-1.0, 1.0]:
            x_side = sign * (BODY_W / 2.0 - 0.5)
            for z_louver in range(260, 350, 10):
                with Locations(Location((x_side, -BODY_D + 60.0, z_louver))):
                    Box(2.0, 60.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

            # Продольные ребра жесткости штамповки внизу
            for z_rib in [60.0, 75.0, 90.0, 105.0]:
                with Locations(Location((x_side, -BODY_D / 2.0, z_rib))):
                    Box(2.0, 260.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    body = body_builder.part
    body.label = "Korpus_Vstraivaemy"
    body.color = Color(0.70, 0.72, 0.74)  # Оцинкованная сталь

    # =========================================================================
    # 4. Panel_Upravleniya_Displey (LED-экран, программатор и сенсоры)
    # =========================================================================
    with BuildPart() as display_builder:
        # Цифровой экран часов и режимов в верхней правой части
        disp_w = 68.0
        disp_h = 36.0
        disp_x = ctrl_x
        disp_z = FASAD_H - 105.0

        with Locations(Location((disp_x, FASAD_T - 1.0, disp_z))):
            Box(disp_w, 2.0, disp_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    display = display_builder.part
    display.label = "Displey_Elektronny_LED"
    display.color = Color(0.05, 0.15, 0.12)  # Темный экран с зеленоватой индикацией

    # Поворотный круглый регулятор Jog Dial (утапливаемый, вровень со стеклом)
    with BuildPart() as dial_builder:
        dial_dia = 44.0
        dial_z = FASAD_H / 2.0 + 8.0

        with Locations(Location((ctrl_x, FASAD_T - 6.0, dial_z)) * Rotation(-90, 0, 0)):
            # Хромированный наружный ободок
            Cylinder(radius=dial_dia / 2.0, height=6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Черная торцевая вставка
            with Locations(Location((0, 0, 2.0))):
                Cylinder(radius=dial_dia / 2.0 - 5.0, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    dial = dial_builder.part
    dial.label = "Pereklyuchatel_JogDial"
    dial.color = Color(0.78, 0.78, 0.82)  # Хром / полированный металл

    # Кнопки управления (Микро/Гриль, Разморозка, Таймер, Стоп/Отмена, Старт/+30с)
    with BuildPart() as buttons_builder:
        btn_w = 34.0
        btn_h = 9.0
        # Верхний ряд кнопок под экраном
        with Locations(
            Location((ctrl_x - 20.0, FASAD_T - 1.0, disp_z - 30.0)),
            Location((ctrl_x + 20.0, FASAD_T - 1.0, disp_z - 30.0)),
            # Нижний ряд кнопок под Jog Dial
            Location((ctrl_x - 20.0, FASAD_T - 1.0, dial_z - 45.0)),
            Location((ctrl_x + 20.0, FASAD_T - 1.0, dial_z - 45.0)),
            # Широкая клавиша Старт / +30с
            Location((ctrl_x, FASAD_T - 1.0, dial_z - 65.0))
        ):
            Box(btn_w, 2.0, btn_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    buttons = buttons_builder.part
    buttons.label = "Knopki_Upravleniya"
    buttons.color = Color(0.18, 0.18, 0.22)  # Черный матовый пластик кнопок

    # Клавиша открывания дверцы в правом нижнем углу
    with BuildPart() as open_btn_builder:
        open_w = 75.0
        open_h = 32.0
        open_z = FASAD_H / 2.0 - 110.0
        with Locations(Location((ctrl_x, FASAD_T - 1.5, open_z))):
            Box(open_w, 3.0, open_h, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    open_btn = open_btn_builder.part
    open_btn.label = "Klavisha_Otkryvaniya_Dveri"
    open_btn.color = Color(0.12, 0.12, 0.15)  # Черная клавиша открывания

    # =========================================================================
    # 5. Kronshteyny_Krepleniya (Боковые монтажные пластины)
    # =========================================================================
    with BuildPart() as brackets_builder:
        # Черные боковые уголки крепления фасада к корпусу (по фото 2)
        for sign in [-1.0, 1.0]:
            x_b = sign * (BODY_W / 2.0 + 8.0)
            with Locations(Location((x_b, -15.0, FASAD_H / 2.0))):
                Box(16.0, 30.0, BODY_H - 40.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    brackets = brackets_builder.part
    brackets.label = "Kronshteyny_Krepleniya"
    brackets.color = Color(0.15, 0.15, 0.15)  # Черный конструкционный пластик

    # =========================================================================
    # 6. Nozhki_Opornye (4 опорные ножки днища короба)
    # =========================================================================
    with BuildPart() as feet_builder:
        for fx in [-BODY_W / 2.0 + 40.0, BODY_W / 2.0 - 40.0]:
            for fy in [-BODY_D + 50.0, -50.0]:
                with Locations(Location((fx, fy, 0))):
                    Cylinder(radius=14.0, height=Z_BODY_MIN, align=(Align.CENTER, Align.CENTER, Align.MIN))

    feet = feet_builder.part
    feet.label = "Nozhki_Opornye"
    feet.color = Color(0.12, 0.12, 0.12)  # Черная резина / пластик

    # =========================================================================
    # СБОРКА КОМПОНЕНТА ДЛЯ БАЗИС-МЕБЕЛЬЩИКА
    # =========================================================================
    parts = [
        fasad,
        door,
        window,
        body,
        display,
        dial,
        buttons,
        open_btn,
        brackets,
        feet
    ]

    assembly = Compound(label="Vstraivaemaya_Mikrovolnovka_DEXP_595x388x420", children=parts)

    # Проверка габаритных размеров
    bbox = assembly.bounding_box()
    dx = bbox.max.X - bbox.min.X
    dy = bbox.max.Y - bbox.min.Y
    dz = bbox.max.Z - bbox.min.Z

    print(f"\nГабаритные размеры модели:")
    print(f"X (Ширина): {dx:.1f} мм (по чертежу фасада: 595.0 мм)")
    print(f"Y (Глубина): {dy:.1f} мм (короб 400 мм + фасад 20 мм = 420.0 мм)")
    print(f"Z (Высота): {dz:.1f} мм (по чертежу фасада: 388.0 мм)")
    print(f"Встраиваемый короб: {BODY_W:.1f} х {BODY_D:.1f} х {BODY_H:.1f} мм (под нишу 560 х 380 мм)")
    print(f"Количество узлов в сборке: {len(parts)}")

    # Директории вывода
    output_dir = Path("c:/Users/Den/Documents/Ai studio/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    step_file = output_dir / "vstraivaemaya_mikrovolnovka_dexp.step"

    print(f"\nЭкспорт в STEP файл: {step_file} ...")
    export_step(assembly, str(step_file))
    print(f"✅ Файл успешно создан! Размер: {step_file.stat().st_size} байт")

    # Экспорт копии в Ai studio-new для веб-генератора
    new_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/private_step")
    new_dir.mkdir(parents=True, exist_ok=True)
    export_step(assembly, str(new_dir / "vstraivaemaya_mikrovolnovka_dexp.step"))

    # Экспорт GLB превью для 3D веб-просмотра
    try:
        from build123d import export_gltf
        glb_dir = Path("c:/Users/Den/Documents/Ai studio-new/storage/previews")
        glb_dir.mkdir(parents=True, exist_ok=True)
        export_gltf(assembly, str(glb_dir / "vstraivaemaya_mikrovolnovka_dexp.glb"), binary=True)
        print("✅ GLB-превью успешно экспортировано!")
    except Exception as e:
        print(f"Экспорт GLB: {e}")

if __name__ == "__main__":
    build_builtin_microwave()
