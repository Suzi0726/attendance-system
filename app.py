import streamlit as st
import streamlit.components.v1 as components
import math
import pandas as pd
from datetime import datetime
import os

# -------------------------------
# CONFIGURATION
# -------------------------------
office_lat = 23.01046725209043
office_lon = 72.62060184026596
allowed_distance = 100  # meters

st.set_page_config(page_title="📍 Staff Attendance", layout="centered")
st.title("📍 Staff Attendance")

# -------------------------------
# Get Staff ID from URL
# -------------------------------
query_params = st.query_params
staff_id = query_params.get("staff", "Unknown")

st.markdown(f"👤 **Welcome, `{staff_id}`**")

# -------------------------------
# Hidden input field + JS GPS Injection
# -------------------------------
gps = st.text_input("GPS", key="gps-data")

components.html("""
<script>
navigator.geolocation.getCurrentPosition(function(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const coords = lat + "," + lon;
    const input = window.parent.document.querySelector('input[id="gps-data"]');
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
    nativeInputValueSetter.call(input, coords);
    input.dispatchEvent(new Event('input', { bubbles: true }));
});
</script>
""", height=0)

if gps:
    try:
        user_lat, user_lon = map(float, gps.split(","))
        st.success(f"📍 Your Location: {user_lat}, {user_lon}")
    except:
        st.error("Failed to parse GPS coordinates.")
        st.stop()
else:
    st.warning("Waiting for GPS location... please allow browser access.")
    st.stop()

# -------------------------------
# Haversine Formula
# -------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

distance = haversine(user_lat, user_lon, office_lat, office_lon)
st.info(f"📏 Distance from office: `{int(distance)} meters`")

# -------------------------------
# Attendance Form
# -------------------------------
if distance <= allowed_distance:
    with st.form("attendance_form", clear_on_submit=False):
        st.success("✅ You are inside the allowed area.")
        option = st.radio("Select action:", ["Punch In", "Punch Out"])
        photo = st.camera_input("📸 Take a selfie")
        submitted = st.form_submit_button("Submit Attendance")

        if submitted:
            if not photo:
                st.error("Photo is required for attendance!")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {
                    "Staff ID": staff_id,
                    "Action": option,
                    "Time": timestamp,
                    "Latitude": user_lat,
                    "Longitude": user_lon
                }
                df = pd.DataFrame([data])

                if os.path.exists("attendance_log.csv"):
                    df.to_csv("attendance_log.csv", mode="a", header=False, index=False)
                else:
                    df.to_csv("attendance_log.csv", index=False)

                st.success(f"✅ {option} recorded at {timestamp}")
else:
    st.error("❌ You are outside the allowed 100 meter radius from office.")
