import streamlit as st

DIAMETERS = [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 1.0, 1.25]
ALUMINUM_DIAMETERS = [0.125, 0.25, 0.375, 0.5, 0.75, 1.0]

CHIP_LOAD_PATTERNS = {
    "A": [0.0005, 0.0010, 0.0018, 0.0025, 0.0030, 0.0033, 0.0043, 0.0056],
    "B": [0.0006, 0.0012, 0.0022, 0.0030, 0.0036, 0.0040, 0.0052, 0.0067],
    "C": [0.0008, 0.0016, 0.0029, 0.0040, 0.0048, 0.0053, 0.0069, 0.0090],
    "D": [0.0010, 0.0020, 0.0036, 0.0050, 0.0060, 0.0067, 0.0086, 0.0112],
    "ALLOY1": [0.0005, 0.0008, 0.0009, 0.0013, 0.0015, 0.0017, 0.0022, 0.0028],
    "ALLOY2": [0.0006, 0.0009, 0.0011, 0.0015, 0.0018, 0.0020, 0.0026, 0.0034],
    "ALLOY10": [0.0008, 0.0010, 0.0014, 0.0020, 0.0024, 0.0027, 0.0035, 0.0045],
}

# Original values: no conservative reduction is baked into this data.
MATERIALS = {
    "Carbon Steel 10XX, 11XX, 12XX, 13XX": {
        "sfm": [220, 264, 343, 378], "patterns": ["A", "B", "C", "D"], "axial1": (0.75, 1.0)
    },
    "Alloy Steel 40XX, 41XX, 42XX, 44XX, 48XX, 86XX": {
        "sfm": [180, 225, 270, 297], "patterns": ["ALLOY1", "ALLOY2", "ALLOY10", "D"], "axial1": (0.75, 1.0)
    },
    "Tool Steel A2, A3, D2, H11, H13, M1, O-1, S-7, NAK 55": {
        "sfm": [180, 225, 270, 297], "patterns": ["A", "B", "C", "D"], "axial1": (0.75, 1.0)
    },
    "Cast Iron, Gray GG-10 to GG-40": {
        "sfm": [100, 125, 163, 179], "patterns": ["A", "B", "C", "D"], "axial1": (0.75, 1.0)
    },
    "Cast Iron, Ductile / Malleable GGG-40 to GGG-70": {
        "sfm": [155, 180, 216, 238], "patterns": ["A", "B", "C", "D"], "axial1": (0.75, 0.75)
    },
    "Stainless 300 & 400 (303, 304, 316, 420, 416, 440)": {
        "sfm": [140, 185, 230, 253], "patterns": ["A", "B", "C", "D"], "axial1": (0.75, 0.75)
    },
    "Precipitation SS 15-5, 17-4, 17-5": {
        "sfm": [115, 180, 250, 275], "patterns": ["A", "B", "C", "D"], "axial1": (0.5, 0.5)
    },
    "Titanium 6Al-4V (Grades 5-38)": {
        "sfm": [180, 250, 325, 358], "sfm_row4_7flute": 400,
        "patterns": ["A", "B", "C", "D"], "axial1": (0.5, 1.0)
    },
    "High Temp Alloys (Inconel 625, 718, Hastelloy, Waspaloy, Cobalt Chrome)": {
        "sfm": [70, 80, 125, 138], "patterns": ["A", "B", "C", "D"],
        "labels": ["40% Radial", "20% Radial", "7% Radial", "5% Radial"],
        "radial": [0.4, 0.2, 0.1, 0.05],
        "axial": [0.5, 1.25, 1.5, 2.0],
    },
    "Aluminum 2011, 2024, 6061, 7075 (MariTool)": {
        "sfm": 800, "ipt": [0.0013, 0.0022, 0.0038, 0.005, 0.007, 0.009]
    },
    "Delrin / plastics": None,
}

CHARTS = ["Accupro 5-flute chart", "Accupro 7-flute chart"]


def engagement_options(material_name, chart):
    material = MATERIALS[material_name]
    if "labels" in material:
        return material["labels"]
    if chart == CHARTS[0]:
        return ["Full Slot", "30% Radial", "10% Radial", "5% Radial"]
    return ["50% Radial", "30% Radial", "10% Radial", "5% Radial"]


def row_values(material_name, chart, row, diameter):
    material = MATERIALS[material_name]
    if "ipt" in material:  # Aluminum has its own single-row MariTool chart.
        index = ALUMINUM_DIAMETERS.index(diameter)
        return material["sfm"], material["ipt"][index], None, None

    index = DIAMETERS.index(diameter)
    sfm = material["sfm"][row]
    if row == 3 and chart == CHARTS[1] and "sfm_row4_7flute" in material:
        sfm = material["sfm_row4_7flute"]
    chip_load = CHIP_LOAD_PATTERNS[material["patterns"][row]][index]

    if "radial" in material:  # High-temperature alloys use their own DOC chart.
        radial_ratio = material["radial"][row]
        axial_ratio = material["axial"][row]
    else:
        radial_ratio = ([1.0, 0.3, 0.1, 0.05] if chart == CHARTS[0]
                        else [0.5, 0.3, 0.1, 0.05])[row]
        axial_ratio = (material["axial1"][0 if chart == CHARTS[0] else 1]
                       if row == 0 else [None, 1.25, 1.5, 2.0][row])
    return sfm, chip_load, axial_ratio, radial_ratio


def calculate(base_sfm, base_ipt, diameter, flutes, stickout, conservative):
    sfm = float(base_sfm)
    ipt = float(base_ipt)
    adjustments = []

    if conservative:
        sfm *= 0.8
        ipt *= 0.9
        adjustments.append("Conservative mode: SFM x0.8, chip load x0.9")

    length_ratio = stickout / diameter
    if 3.0 < length_ratio <= 5.0:
        sfm *= 0.85
        ipt *= 0.85
        adjustments.append("Tool length: SFM x0.85, chip load x0.85")
    elif 5.0 < length_ratio <= 8.0:
        sfm *= 0.70
        ipt *= 0.75
        adjustments.append("Tool length: SFM x0.70, chip load x0.75")
    elif length_ratio > 8.0:
        sfm *= 0.55
        ipt *= 0.60
        adjustments.append("Tool length: SFM x0.55, chip load x0.60")

    rpm = round(sfm * 3.82 / diameter)
    ipm = round(ipt * flutes * rpm, 1)
    return sfm, ipt, rpm, ipm, length_ratio, adjustments


st.set_page_config(page_title="Speeds & Feeds Calculator", layout="centered")
st.title("Speeds & Feeds Calculator")

chart = st.selectbox("Chart", CHARTS)
material_name = st.selectbox("Material", list(MATERIALS))

if MATERIALS[material_name] is None:
    st.write("—")
else:
    aluminum = "ipt" in MATERIALS[material_name]
    if aluminum:
        st.caption("Engagement: Standard")
    else:
        options = engagement_options(material_name, chart)
        selected_row = st.selectbox("Engagement", options)

    diameter_options = (ALUMINUM_DIAMETERS if aluminum else
                        DIAMETERS[:-1] if chart == CHARTS[0] else DIAMETERS)
    diameter = st.selectbox("Diameter (inches)", diameter_options,
                            index=diameter_options.index(0.5))
    flutes = st.number_input("Flutes", min_value=1,
                             value=5 if chart == CHARTS[0] else 7,
                             step=1, key="flutes_5" if chart == CHARTS[0] else "flutes_7")
    stickout = st.number_input("Tool length (stickout) in inches", min_value=0.0,
                               value=3.0 * diameter, step=0.001, format="%.3f",
                               key=f"stickout_{diameter:g}")
    conservative = st.toggle("Conservative mode (budget coated tools)", value=False)

    row = 0 if aluminum else options.index(selected_row)
    base_sfm, base_ipt, axial, radial = row_values(material_name, chart, row, diameter)
    sfm, chip_load, rpm, ipm, length_ratio, adjustments = calculate(
        base_sfm, base_ipt, diameter, flutes, stickout, conservative
    )

    st.divider()
    left, right = st.columns(2)
    with left:
        st.metric("SFM", f"{sfm:g}")
        st.metric("Chip load (IPT)", f"{chip_load:.6f}")
    with right:
        st.metric("RPM", f"{rpm:,}")
        st.metric("Feed (IPM)", f"{ipm:.1f}")

    st.caption(f"Tool length = {length_ratio:.2f} x D")
    if axial is not None:
        st.write(f"**Recommended axial DOC:** {axial:g} x D = {axial * diameter:.3f} in")
        st.write(f"**Recommended radial DOC:** {radial:g} x D = {radial * diameter:.3f} in")
    st.write("Adjustments applied: " + (", ".join(adjustments) if adjustments else "none"))
    if conservative:
        st.caption("Conservative mode ON: SFM x0.8, chip load x0.9")
    if length_ratio > 8.0:
        st.warning("Very long tool: high chatter and deflection risk. Consider a shorter tool.")
