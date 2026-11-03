import streamlit as st

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


st.set_page_config(page_title="CNC Speeds & Feeds", page_icon="⚙️", layout="centered")

st.title("CNC Milling Speeds & Feeds")
st.caption("Conservative cutting values for coated budget tooling")

material_name = st.selectbox("Material", list(MATERIALS))
material = MATERIALS[material_name]

# Delrin is intentionally missing shop data. Show no calculation or inputs.
if material["sfm"] is None:
    st.info("No shop numbers filled in for Delrin yet")
else:
    diameter = st.number_input(
        "Cutter diameter (inches)",
        min_value=DIAMETERS[0],
        max_value=DIAMETERS[-1],
        value=0.5,
        step=0.001,
        format="%.3f",
    )
    flutes = st.number_input(
        "Number of flutes", min_value=1, value=4, step=1, format="%d"
    )

    stepover_percent = st.number_input(
        "Stepover (% of tool diameter)",
        min_value=0.1,
        max_value=100.0,
        value=50.0,
        step=0.1,
        format="%.1f",
    )
    depth_of_cut = st.number_input(
        "Depth of cut (inches)",
        min_value=0.0,
        value=float(diameter),
        step=0.001,
        format="%.3f",
    )
    tool_length = st.number_input(
        "Tool length / stickout (inches)",
        min_value=0.0,
        value=3.0 * float(diameter),
        step=0.001,
        format="%.3f",
    )

    r = stepover_percent / 100.0
    q = depth_of_cut / diameter
    L = tool_length / diameter
    sfm_multiplier = 1.0
    feed_multiplier = 1.0
    adjustments = []

    # Radial chip thinning changes feed only.
    if r < 0.50:
        chip_thinning = min(2.0, 1.0 / math.sqrt(1.0 - (1.0 - 2.0 * r) ** 2))
        feed_multiplier *= chip_thinning
        adjustments.append(f"Chip thinning x{chip_thinning:.2f}")
    elif r == 1.00:
        feed_multiplier *= 0.75
        adjustments.append("Slotting x0.75 feed")

    # Axial depth adjustments.
    if 1.0 < q <= 2.0:
        feed_multiplier *= 0.85
        adjustments.append("Depth x0.85 feed")
    elif q > 2.0:
        feed_multiplier *= 0.70
        sfm_multiplier *= 0.90
        adjustments.append("Depth x0.90 SFM / x0.70 feed")

    # Stickout ratio adjustments.
    if 3.0 < L <= 5.0:
        sfm_multiplier *= 0.85
        feed_multiplier *= 0.85
        adjustments.append("Length x0.85 SFM / x0.85 feed")
    elif 5.0 < L <= 8.0:
        sfm_multiplier *= 0.70
        feed_multiplier *= 0.75
        adjustments.append("Length x0.70 SFM / x0.75 feed")
    elif L > 8.0:
        sfm_multiplier *= 0.55
        feed_multiplier *= 0.60
        adjustments.append("Length x0.55 SFM / x0.60 feed")

    # Start with the existing, already-derated materials table.
    # Do not round the intermediate values used for RPM or IPM.
    sfm = material["sfm"] * sfm_multiplier
    ipt = chip_load_for_diameter(diameter, material["ipt"])
    rpm = sfm * 3.82 / diameter
    ipm = ipt * feed_multiplier * flutes * rpm

    st.divider()
    st.subheader("Calculated results")
    first_left, first_right = st.columns(2)
    with first_left:
        st.metric("SFM", f"{sfm:g}")
    with first_right:
        st.metric("Chip load (IPT)", f"{ipt:.6f}")

    second_left, second_right = st.columns(2)
    with second_left:
        st.metric("Spindle RPM", f"{rpm:,.0f}")
    with second_right:
        st.metric("Feed (IPM)", f"{ipm:,.1f}")

    st.caption(
        f"Depth of cut = {q:.2f} x D  |  Tool length = {L:.2f} x D"
    )
    st.write("Adjustments applied: " + (", ".join(adjustments) if adjustments else "none"))

    if L > 8.0:
        st.warning(
            "Very long tool: high chatter and deflection risk. Consider a shorter tool."
        )
