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


def validate_city_country(city: str, country: str) -> dict:
    # Stub: integrate OSM Nominatim later
    return {"valid": True, "ambiguous": False}


def call_perplexity_api(data: dict) -> dict:
    # Stub: integrate real API
    return {
        "sections": [
            {"title": "Traveler Summary", "content": "(Summary...)"},
            {"title": "Disease Risks", "content": "(Risks...)"},
            {"title": "Vaccine Recommendations", "content": "(Vaccines...)"},
            {"title": "Medications", "content": "(Meds...)"},
            {"title": "Local Regulations", "content": "(Rules...)"},
            {"title": "Hygiene & Behavior Tips", "content": "(Tips...)"}
        ]
    }


def get_nearby_clinics(postal_code: str) -> list:
    # Stub: integrate clinic DB/API
    return []

# --- Navigation ---
def go_to_step(step: int):
    st.session_state.step = step

# --- Destination management callbacks ---
def add_destination():
    if "destinations" not in st.session_state:
        st.session_state.destinations = [0]
    new_idx = max(st.session_state.destinations) + 1
    st.session_state.destinations.append(new_idx)


def remove_destination(idx):
    st.session_state.destinations.remove(idx)

# --- Step 1: Traveler Profile ---
def traveler_info():
    st.header("1. Traveler Profile")
    cols = st.columns(2)
    cols[0].number_input("Age", min_value=0, max_value=120, value=30, key="age")
    cols[1].selectbox("Sex at birth", ["Female", "Male", "Other"], key="sex_at_birth")

    if st.session_state.get("sex_at_birth") == "Female":
        st.radio(
            "Pregnancy/Breastfeeding status",
            ["Not pregnant/not breastfeeding", "Pregnant", "Breastfeeding"],
            key="preg_status"
        )

    st.radio("Received all childhood vaccinations?", ["Yes", "No", "Not sure"], key="childhood_vax")
    if st.session_state.get("childhood_vax") == "No":
        st.multiselect("Which vaccines were not taken?",
                       ["MMR", "DTP", "Polio", "Varicella", "Other"],
                       key="missing_vax")

    st.text_area("Known medical conditions (optional)", key="med_conditions", height=100)
    st.text_area("Current medications (optional)", key="medications", height=100)
    st.text_area("Known allergies (optional)", key="allergies", height=100)

    cols = st.columns(2)
    cols[0].radio("Family history of blood clots/DVT?", ["Yes", "No"], index=1, key="family_dvt")
    cols[1].radio("Family history of pulmonary embolism?", ["Yes", "No"], index=1, key="family_pe")

    # Continue button for mobile navigation
    st.button("Continue to Destination ▶", on_click=go_to_step, args=(1,))

# --- Step 2: Destination Info ---
def destination_info():
    st.header("2. Destination Information")
    if "destinations" not in st.session_state:
        st.session_state.destinations = [0]

    countries = ["-- Select Destination Country --"] + load_countries()
    for idx in st.session_state.destinations:
        with st.expander(f"Destination #{idx+1}", expanded=True):
            st.selectbox("Destination Country", countries, key=f"country_{idx}")
            st.text_input("City (e.g., Toronto)", key=f"city_{idx}")

            cols = st.columns(2)
            cols[0].date_input("Arrival date", min_value=date.today(), key=f"arrival_{idx}")
            cols[1].number_input("Duration (days)", min_value=1, key=f"days_{idx}")

            st.selectbox("Accommodation type", ACCOMMODATION_TYPES, key=f"accom_{idx}")
            st.markdown("**Planned Activities**")
            act_cols = st.columns(2)
            for i, act in enumerate(ACTIVITIES):
                act_cols[i % 2].checkbox(act, key=f"activities_{idx}_{i}")

            if idx > 0:
                st.button("Remove this destination", on_click=remove_destination, args=(idx,), key=f"remove_{idx}")

    st.button("Add another destination", on_click=add_destination)
    st.button("Continue to Review ▶", on_click=go_to_step, args=(2,))

# --- Step 3: Review & Submit ---
def validate_inputs():
    st.header("3. Review & Submit")
    errors = []
    if st.session_state.get("age") is None:
        errors.append("Please enter your age.")
    if not st.session_state.get("sex_at_birth"):
        errors.append("Please select sex at birth.")
    if not st.session_state.get("childhood_vax"):
        errors.append("Please indicate childhood vaccination status.")

    if not st.session_state.destinations:
        errors.append("At least one destination is required.")
    else:
        for idx in st.session_state.destinations:
            city = st.session_state.get(f"city_{idx}")
            country = st.session_state.get(f"country_{idx}")
            if not city:
                errors.append(f"City is required for destination #{idx+1}.")
            elif country == "-- Select Destination Country --":
                errors.append(f"Please select a country for destination #{idx+1}.")
            else:
                check = validate_city_country(city, country)
                if not check['valid']:
                    errors.append(f"City '{city}' not found in {country}.")
                elif check['ambiguous']:
                    errors.append(f"City '{city}' is ambiguous; please specify province/state.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        st.button("Generate Advisory Report", on_click=go_to_step, args=(3,))

# --- Step 4: Report Generation ---
def generate_report():
    st.header("4. Travel Health Advisory Report")
    st.info("Building your personalized report—please wait...")

    data = {"traveler": {}, "destinations": []}
    for key in ["age","sex_at_birth","preg_status","childhood_vax","missing_vax",
                "med_conditions","medications","allergies","family_dvt","family_pe"]:
        data["traveler"][key] = st.session_state.get(key)

    for idx in st.session_state.destinations:
        activities = [ACTIVITIES[i] for i in range(len(ACTIVITIES)) if st.session_state.get(f"activities_{idx}_{i}")]
        data["destinations"].append({
            "country": st.session_state.get(f"country_{idx}"),
            "city": st.session_state.get(f"city_{idx}"),
            "arrival": str(st.session_state.get(f"arrival_{idx}")),
            "duration": st.session_state.get(f"days_{idx}"),
            "accommodation": st.session_state.get(f"accom_{idx}"),
            "activities": activities
        })

    response = call_perplexity_api(data)
    for section in response.get("sections", []):
        st.subheader(section["title"])
        st.write(section["content"])

    st.button("Find Nearby Clinics ▶", on_click=go_to_step, args=(4,))

# --- Step 5: Clinic Locator ---
def clinic_map():
    st.header("5. Find Nearby Travel Clinics")
    postal_code = st.text_input("Enter your Canadian postal code:")
    st.button("Search Clinics")
    if postal_code:
        st.info("Looking up clinics—feature under development...")
        clinics = get_nearby_clinics(postal_code)
        if clinics:
            import pandas as pd
            df = pd.DataFrame(clinics)
            st.map(df)
        else:
            st.info("No clinics found or service not yet available.")

# --- Main Application ---
def main():
    st.set_page_config(page_title="Travel Vaccination Assistant", layout="wide")
    st.title("Travel Vaccination Assistant (Prototype)")

    steps = [
        "Traveler Profile",
        "Destination Information",
        "Review & Submit",
        "Generate Report",
        "Travel Clinics"
    ]
    if "step" not in st.session_state:
        st.session_state.step = 0
    choice = st.sidebar.radio("Go to step:", steps, index=st.session_state.step)
    st.session_state.step = steps.index(choice)

    if st.session_state.step == 0:
        traveler_info()
    elif st.session_state.step == 1:
        destination_info()
    elif st.session_state.step == 2:
        validate_inputs()
    elif st.session_state.step == 3:
        generate_report()
    elif st.session_state.step == 4:
        clinic_map()

if __name__ == "__main__":
    main()
