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

    sfm = material["sfm"]
    ipt = chip_load_for_diameter(diameter, material["ipt"])
    rpm = sfm * 3.82 / diameter
    ipm = rpm * flutes * ipt

    st.divider()
    st.subheader("Calculated results")
    first_left, first_right = st.columns(2)
    with first_left:
        st.metric("SFM", f"{sfm}")
    with first_right:
        st.metric("Chip load (IPT)", f"{ipt:.6f}")

    second_left, second_right = st.columns(2)
    with second_left:
        st.metric("Spindle RPM", f"{rpm:,.0f}")
    with second_right:
        st.metric("Feed (IPM)", f"{ipm:,.1f}")
