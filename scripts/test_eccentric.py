from build123d import *
from pathlib import Path

def create_eccentric_assembly():
    # ---------------------------------------------------------
    # 1. Eksentrik_Korpus (Эксцентрик 15x12.5 мм)
    # ---------------------------------------------------------
    # Базовый цилиндр корпуса Ø15, высота 12.5
    with BuildPart() as korpus_builder:
        Cylinder(radius=15.0 / 2, height=12.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # Паз под крестовую отвертку сверху (Z = 12.5)
        with Locations(Location((0, 0, 12.5))):
            Box(7.0, 1.6, 3.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
            Box(1.6, 7.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
            
        # Боковое отверстие/окно под головку штока на высоте Z = 6.25
        with Locations(Location((0, 0, 6.25)) * Rotation(0, 90, 0)):
            Cylinder(radius=7.2 / 2, height=16.0, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)

    korpus = korpus_builder.part
    korpus.label = "Eksentrik_Korpus"
    korpus.color = Color(0.60, 0.62, 0.65)  # Цинк

    # ---------------------------------------------------------
    # 2. Eksentrik_Shtok (Дюбель/шток L=34 мм)
    # ---------------------------------------------------------
    # Строим шток вдоль оси X с центром на высоте Z = 6.25
    with BuildPart() as shtok_builder:
        # Головка штока (Ø7 мм, L=6 мм), заходящая в эксцентрик
        with Locations(Location((-2.0, 0, 6.25)) * Rotation(0, 90, 0)):
            Cylinder(radius=7.0 / 2, height=6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Шейка штока (Ø4.5 мм, L=4 мм)
        with Locations(Location((4.0, 0, 6.25)) * Rotation(0, 90, 0)):
            Cylinder(radius=4.5 / 2, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Упорный буртик (Ø8.0 мм, L=2 мм)
        with Locations(Location((8.0, 0, 6.25)) * Rotation(0, 90, 0)):
            Cylinder(radius=8.0 / 2, height=2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Резьбовая часть дюбеля (Ø6 мм, L=22 мм)
        with Locations(Location((10.0, 0, 6.25)) * Rotation(0, 90, 0)):
            Cylinder(radius=6.0 / 2, height=22.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    shtok = shtok_builder.part
    shtok.label = "Eksentrik_Shtok"
    shtok.color = Color(0.75, 0.75, 0.78)  # Сталь

    # ---------------------------------------------------------
    # 3. Zaglushka_Plastik (Заглушка Ø18 мм, толщина 1.5 мм)
    # ---------------------------------------------------------
    with BuildPart() as zaglushka_builder:
        with Locations(Location((0, 0, 12.5))):
            Cylinder(radius=18.0 / 2, height=1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Внутренний фиксирующий выступ в шлиц (Ø6 мм, высота 1.2 мм вниз)
        with Locations(Location((0, 0, 12.5))):
            Cylinder(radius=5.5 / 2, height=1.2, align=(Align.CENTER, Align.CENTER, Align.MAX))

    zaglushka = zaglushka_builder.part
    zaglushka.label = "Zaglushka_Plastik"
    zaglushka.color = Color(0.15, 0.15, 0.15)  # Черный пластик

    # ---------------------------------------------------------
    # Сборка и экспорт в STEP
    # ---------------------------------------------------------
    assembly = Compound(
        label="Furnitura_Assembly",
        children=[korpus, shtok, zaglushka]
    )
    
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    step_path = output_dir / "test_eccentric.step"
    
    export_step(assembly, str(step_path))
    
    # Расчет габаритов
    bbox = assembly.bounding_box()
    dx = round(bbox.size.X, 2)
    dy = round(bbox.size.Y, 2)
    dz = round(bbox.size.Z, 2)
    
    print(f"STEP created: {step_path.resolve()}")
    print(f"File size: {step_path.stat().st_size} bytes")
    print(f"BBox: X={dx} mm, Y={dy} mm, Z={dz} mm")
    print("Parts:")
    for child in assembly.children:
        c = getattr(child, 'color', None)
        color_str = f"({tuple(c)[:3]})" if c else "None"
        print(f"  - {child.label}: Color={color_str}")

if __name__ == "__main__":
    create_eccentric_assembly()
