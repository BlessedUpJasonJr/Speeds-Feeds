import math

DIAMETERS = [0.125, 0.25, 0.375, 0.5, 0.75, 1.0]

MATERIALS = {
    "Aluminum 2011, 2024, 6061, 7075": {"sfm": 640, "ipt": [0.00117, 0.00198, 0.00342, 0.00450, 0.00630, 0.00810]},
    "Brass 360 half hard": {"sfm": 560, "ipt": [0.00117, 0.00198, 0.00342, 0.00450, 0.00630, 0.00810]},
    "Free machining 12L14, 1215, 11L17": {"sfm": 440, "ipt": [0.00054, 0.00135, 0.00198, 0.00360, 0.00450, 0.00495]},
    "Low carbon steel 1008, 1018, 1020": {"sfm": 400, "ipt": [0.00054, 0.00126, 0.00180, 0.00270, 0.00360, 0.00405]},
    "Cast iron": {"sfm": 400, "ipt": [0.00045, 0.00126, 0.00180, 0.00315, 0.00450, 0.00468]},
    "Medium carbon steel 4140, 8620": {"sfm": 320, "ipt": [0.00045, 0.00108, 0.00162, 0.00225, 0.00315, 0.00360]},
    "Copper, bronze": {"sfm": 320, "ipt": [0.00054, 0.00135, 0.00198, 0.00360, 0.00450, 0.00495]},
    "Stainless steel 300 series (303, 304, 316)": {"sfm": 300, "ipt": [0.00045, 0.00126, 0.00180, 0.00315, 0.00450, 0.00468]},
    "Titanium 6Al-4V": {"sfm": 240, "ipt": [0.00045, 0.00090, 0.00144, 0.00198, 0.00315, 0.00360]},
    "Tool steel A2, D2, M2, M42": {"sfm": 192, "ipt": [0.00036, 0.00090, 0.00144, 0.00198, 0.00288, 0.00315]},
    "Stainless steel 15-5, 17-4": {"sfm": 184, "ipt": [0.00045, 0.00135, 0.00180, 0.00315, 0.00450, 0.00468]},
    "Stainless steel 400 series": {"sfm": 160, "ipt": [0.00036, 0.00117, 0.00162, 0.00288, 0.00405, 0.00414]},
    "Inconel 625, 718": {"sfm": 48, "ipt": [0.00018, 0.00054, 0.00126, 0.00162, 0.00252, 0.00288]},
    "Delrin / plastics": {"sfm": None, "ipt": [None, None, None, None, None, None]},
}


def chip_load_for_diameter(diameter, loads):
    for index, chart_diameter in enumerate(DIAMETERS):
        if diameter == chart_diameter:
            return loads[index]

    for index in range(len(DIAMETERS) - 1):
        low = DIAMETERS[index]
        high = DIAMETERS[index + 1]
        if low < diameter < high:
            fraction = (diameter - low) / (high - low)
            return loads[index] + fraction * (loads[index + 1] - loads[index])

    raise ValueError("Diameter is outside the chart range.")


def get_diameter():
    while True:
        try:
            diameter = float(input("Cutter diameter in inches: "))
        except ValueError:
            print("Enter a valid numeric diameter.")
            continue

        if not math.isfinite(diameter) or not DIAMETERS[0] <= diameter <= DIAMETERS[-1]:
            print("Enter a diameter from 0.125 to 1.0 inches (no chart data outside this range).")
            continue
        return diameter


def get_flutes():
    while True:
        entered = input("Number of flutes: ").strip()
        try:
            flutes = int(entered)
        except ValueError:
            print("Enter a positive whole number of flutes.")
            continue
        if flutes <= 0:
            print("Enter a positive whole number of flutes.")
            continue
        return flutes


def main():
    names = list(MATERIALS)
    while True:
        print("\n=== CNC MILLING SPEEDS AND FEEDS ===")
        for number, name in enumerate(names, start=1):
            print(f"{number}. {name}")

        selection = input("Choose a material number (or Q to quit): ").strip()
        if selection.lower() == "q":
            print("Goodbye.")
            return
        try:
            number = int(selection)
        except ValueError:
            print("Enter a valid material number.")
            continue
        if not 1 <= number <= len(names):
            print("Enter a number from the material list.")
            continue

        name = names[number - 1]
        material = MATERIALS[name]
        if material["sfm"] is None:
            print("No shop numbers filled in for Delrin yet")
            continue

        diameter = get_diameter()
        flutes = get_flutes()
        sfm = material["sfm"]
        ipt = chip_load_for_diameter(diameter, material["ipt"])
        rpm = sfm * 3.82 / diameter
        ipm = rpm * flutes * ipt

        print(f"\nMaterial: {name}")
        print(f"SFM used: {sfm}")
        print(f"Chip load used: {ipt:.6f} in/tooth")
        print(f"RPM: {rpm:.0f}")
        print(f"Feed rate: {ipm:.1f} IPM")

        while True:
            again = input("\nRun another? (Y/N): ").strip().lower()
            if again in ("y", "yes"):
                break
            if again in ("n", "no", "q", "quit"):
                print("Goodbye.")
                return
            print("Enter Y or N.")


if __name__ == "__main__":
    main()
