import streamlit as st
from datetime import date

# --- Constants & Configuration ---
COUNTRIES_FILE = "countries.txt"
ACCOMMODATION_TYPES = [
    "hotel", "budget hostel", "camping", "rural area lodging", "private home", "other"
]
ACTIVITIES = [
    "walking, hiking, trekking, backpacking",
    "cycling, mountain biking, horseback riding",
    "caving, spelunking, rock climbing, mountaineering",
    "bird-watching, wildlife watching",
    "safari, game drive, hunting",
    "swimming, scuba diving, snorkeling",
    "surfing, windsurfing, kitesurfing, canoeing, kayaking, rafting, boating, sailing",
    "fishing",
    "day trips to rural areas",
    "fieldwork in rural or remote areas",
    "fieldwork with animals",
    "ecotourism in remote areas",
    "going to beaches (sunbathing, relaxing, beach sports)",
    "attending large events (festivals, concerts, sports)",
    "dining out, nightlife (restaurants, clubs, bars)"
]

# --- Utility Functions ---

def load_countries():
    try:
        with open(COUNTRIES_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        st.error(f"{COUNTRIES_FILE} not found.")
        return []

# --- State Initialization ---
def init_state():
    # Navigation
    st.session_state.setdefault("step", 0)
    # Step 0: Traveler Profile defaults
    st.session_state.setdefault("age", 30)
    st.session_state.setdefault("sex_at_birth", None)
    st.session_state.setdefault("preg_status", None)
    st.session_state.setdefault("childhood_vax", None)
    st.session_state.setdefault("missing_vax", [])
    st.session_state.setdefault("med_conditions", "")
    st.session_state.setdefault("medications", "")
    st.session_state.setdefault("allergies", "")
    st.session_state.setdefault("family_dvt", None)
    st.session_state.setdefault("family_pe", None)
    # Step 1: Destination indices
    st.session_state.setdefault("destinations", [0])

# --- Navigation Callback ---
def go_to_step(step: int):
    st.session_state.step = step

# --- Destination management callbacks ---
def add_destination():
    new_idx = max(st.session_state.destinations) + 1
    st.session_state.destinations.append(new_idx)


def remove_destination(idx):
    st.session_state.destinations.remove(idx)

# --- Step 0: Traveler Profile ---
def traveler_info():
    st.header("1. Tell us about yourself")
    cols = st.columns(2)
    cols[0].number_input("Age", min_value=0, max_value=120,
                        value=st.session_state.age, key="age")
    cols[1].selectbox("Sex at birth", ["Female", "Male", "Other"],
                     index=(0 if st.session_state.sex_at_birth is None else ["Female", "Male", "Other"].index(st.session_state.sex_at_birth)),
                     key="sex_at_birth")

    if st.session_state.sex_at_birth == "Female":
        st.radio(
            "Pregnancy/Breastfeeding status",
            ["Not pregnant/not breastfeeding", "Pregnant", "Breastfeeding"],
            key="preg_status",
            index=(0 if st.session_state.preg_status is None else ["Not pregnant/not breastfeeding", "Pregnant", "Breastfeeding"].index(st.session_state.preg_status))
        )

    st.radio(
        "Received all childhood vaccinations?",
        ["Yes", "No", "Not sure"],
        key="childhood_vax",
        index=(0 if st.session_state.childhood_vax is None else ["Yes", "No", "Not sure"].index(st.session_state.childhood_vax))
    )
    if st.session_state.childhood_vax == "No":
        st.multiselect(
            "Which vaccines were not taken?",
            ["MMR", "DTP", "Polio", "Varicella", "Other"],
            default=st.session_state.missing_vax,
            key="missing_vax"
        )

    st.text_area("Known medical conditions (optional)",
                value=st.session_state.med_conditions,
                key="med_conditions", height=100)
    st.text_area("Current medications (optional)",
                value=st.session_state.medications,
                key="medications", height=100)
    st.text_area("Known allergies (optional)",
                value=st.session_state.allergies,
                key="allergies", height=100)

    cols = st.columns(2)
    cols[0].radio("Family history of blood clots/DVT?", ["Yes", "No"],
                 index=(0 if st.session_state.family_dvt == "Yes" else 1),
                 key="family_dvt")
    cols[1].radio("Family history of pulmonary embolism?", ["Yes", "No"],
                 index=(0 if st.session_state.family_pe == "Yes" else 1),
                 key="family_pe")

    st.button("Continue to Destination ▶", on_click=go_to_step, args=(1,))

# --- Step 1: Destination Information ---
def destination_info():
    st.header("2. Where are you going?")
    countries = ["-- Select Destination Country --"] + load_countries()

    for idx in st.session_state.destinations:
        with st.expander(f"Destination #{idx+1}", expanded=True):
            st.selectbox("Destination Country", countries,
                         key=f"country_{idx}")
            st.text_input("City (e.g., Toronto)",
                          key=f"city_{idx}")

            cols = st.columns(2)
            cols[0].date_input("Arrival date",
                              min_value=date.today(),
                              key=f"arrival_{idx}")
            cols[1].number_input("Duration (days)", min_value=1,
                                 key=f"days_{idx}")

            st.selectbox("Accommodation type", ACCOMMODATION_TYPES,
                         key=f"accom_{idx}")

            st.markdown("**Planned Activities**")
            act_cols = st.columns(2)
            for i, act in enumerate(ACTIVITIES):
                act_cols[i % 2].checkbox(
                    act,
                    key=f"activities_{idx}_{i}"
                )

            if idx > 0:
                st.button(
                    "Remove this destination",
                    on_click=remove_destination,
                    args=(idx,),
                    key=f"remove_{idx}"
                )

    st.button("Add another destination", on_click=add_destination)
    # st.button("Continue ▶", on_click=go_to_step, args=(2,))

# --- Main Application ---
def main():
    init_state()
    st.set_page_config(page_title="Travel Vaccination Assistant", layout="wide")
    st.title("Travel Vaccination Advisory")

    steps = [
        "Traveler Profile",
        "Destination Information"
    ]

    # Sidebar navigation & debug
    with st.sidebar.expander("Debug Info"):
        st.write("Current step:", st.session_state.step)
        st.write("Session state keys:", list(st.session_state.keys()))
        if st.button("Clear session state"):
            st.session_state.clear()
            st.experimental_rerun()

    choice = st.sidebar.radio("Go to step:", steps, index=st.session_state.step)
    if steps.index(choice) != st.session_state.step:
        st.session_state.step = steps.index(choice)

    # Route to steps
    if st.session_state.step == 0:
        traveler_info()
    elif st.session_state.step == 1:
        destination_info()

if __name__ == "__main__":
    main()
