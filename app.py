# app.py

import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from datetime import datetime
from geopy.distance import geodesic
import pandas as pd
import os

# === CONFIG ===
OFFICE_COORDS = (26.8497, 80.9462)
PHOTO_FOLDER = "photos"
os.makedirs(PHOTO_FOLDER, exist_ok=True)
st.set_page_config(page_title="Attendance", layout="centered")

# === GET STAFF ID ===
query_params = st.experimental_get_query_params()
staff_id = query_params.get("staff", ["Unknown"])[0]

st.title("📍 Staff Attendance")
st.subheader(f"👤 Welcome, {staff_id}")
st.markdown("### 📡 Detecting your GPS location...")

# === GET LOCATION VIA BROWSER (AUTO)
location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition((pos) => {return [pos.coords.latitude, pos.coords.longitude]})", key="get_location", timeout=30)

if not location:
    st.warning("Waiting for GPS location… please allow location access in your browser.")
    st.stop()

try:
    lat, lon = float(location[0]), float(location[1])
    user_coords = (lat, lon)
    distance = geodesic(OFFICE_COORDS, user_coords).meters

    if distance > 100:
        st.error(f"⛔ You are too far from the office: {int(distance)} meters")
        st.stop()
    else:
        st.success(f"✅ Location Verified: {int(distance)} meters from office")

        # === MANDATORY PHOTO ===
        photo = st.camera_input("📸 Please take a live photo (required)")

        if not photo:
            st.warning("⚠️ You must click a live photo to proceed.")
            st.stop()

        # === BUTTONS ===
        col1, col2 = st.columns(2)
        punch_type = None

        if col1.button("📥 Punch In"):
            punch_type = "Punch In"
        elif col2.button("📤 Punch Out"):
            punch_type = "Punch Out"

        if punch_type:
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            photo_filename = f"{PHOTO_FOLDER}/{staff_id}_{timestamp}_{punch_type.replace(' ', '')}.jpg"
            with open(photo_filename, "wb") as f:
                f.write(photo.getbuffer())

            record = {
                "Staff ID": staff_id,
                "Date": now.strftime("%Y-%m-%d"),
                "Time": now.strftime("%H:%M:%S"),
                "Type": punch_type,
                "Latitude": lat,
                "Longitude": lon,
                "Photo": photo_filename
            }

            file_exists = os.path.exists("attendance.xlsx")
            df = pd.DataFrame([record])
            df.to_excel("attendance.xlsx", index=False, header=not file_exists, mode='a' if file_exists else 'w')

            st.success(f"✅ {punch_type} recorded successfully!")
except:
    st.error("❌ GPS data error. Please reload the page and allow location access.")
