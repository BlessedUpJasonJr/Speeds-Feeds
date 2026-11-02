import streamlit as st

import math

DIAMETERS = [0.125, 0.25, 0.375, 0.5, 0.75, 1.0]

MATERIALS = {
    "Aluminum 2011, 2024, 6061, 7075": {"sfm": 800, "ipt": [0.0013, 0.0022, 0.0038, 0.005, 0.007, 0.009]},
    "Brass 360 half hard": {"sfm": 700, "ipt": [0.0013, 0.0022, 0.0038, 0.005, 0.007, 0.009]},
    "Free machining 12L14, 1215, 11L17": {"sfm": 550, "ipt": [0.0006, 0.0015, 0.0022, 0.004, 0.005, 0.0055]},
    "Low carbon steel 1008, 1018, 1020": {"sfm": 500, "ipt": [0.0006, 0.0014, 0.002, 0.003, 0.004, 0.0045]},
    "Cast iron": {"sfm": 500, "ipt": [0.0005, 0.0014, 0.002, 0.0035, 0.005, 0.0052]},
    "Medium carbon steel 4140, 8620": {"sfm": 400, "ipt": [0.0005, 0.0012, 0.0018, 0.0025, 0.0035, 0.004]},
    "Copper, bronze": {"sfm": 400, "ipt": [0.0006, 0.0015, 0.0022, 0.004, 0.005, 0.0055]},
    "Stainless steel 300 series (303, 304, 316)": {"sfm": 375, "ipt": [0.0005, 0.0014, 0.002, 0.0035, 0.005, 0.0052]},
    "Titanium 6Al-4V": {"sfm": 300, "ipt": [0.0005, 0.001, 0.0016, 0.0022, 0.0035, 0.004]},
    "Tool steel A2, D2, M2, M42": {"sfm": 240, "ipt": [0.0004, 0.001, 0.0016, 0.0022, 0.0032, 0.0035]},
    "Stainless steel 15-5, 17-4": {"sfm": 230, "ipt": [0.0005, 0.0015, 0.002, 0.0035, 0.005, 0.0052]},
    "Stainless steel 400 series": {"sfm": 200, "ipt": [0.0004, 0.0013, 0.0018, 0.0032, 0.0045, 0.0046]},
    "Inconel 625, 718": {"sfm": 60, "ipt": [0.0002, 0.0006, 0.0014, 0.0018, 0.0028, 0.0032]},
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
