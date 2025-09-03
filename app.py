import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import time
import random
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Deteksi Parkir Liar - CCTV Monitoring",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better styling
st.markdown("""
<style>
    /* Main theme */
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #6FA9FF;
        padding-bottom: 8px;
        margin-bottom: 16px;
        border-bottom: 2px solid #e2e8f0;
    }
    .sub-header {
        font-size: 18px;
        font-weight: bold;
        color: #2b6cb0;
        margin-top: 16px;
        margin-bottom: 12px;
        padding-bottom: 4px;
        border-bottom: 1px solid #e2e8f0;
    }
    
    /* Cards and containers */
    .metric-card {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .cctv-container {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
        background-color: #1a202c;
    }
    
    /* Status indicators */
    .status-active {
        color: white;
        background-color: #e53e3e;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .status-clear {
        color: white;
        background-color: #38a169;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* Violations box styling */
    .violation-box {
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    
    /* Notifications */
    .notification-high {
        background-color: rgba(229, 62, 62, 0.1);
        border-left: 4px solid #e53e3e;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 0 4px 4px 0;
    }
    .notification-medium {
        background-color: rgba(237, 137, 54, 0.1);
        border-left: 4px solid #ed8936;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 0 4px 4px 0;
    }
    .notification-low {
        background-color: rgba(49, 130, 206, 0.1);
        border-left: 4px solid #3182ce;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 0 4px 4px 0;
    }
    
    /* Data tables */
    .dataframe-container {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }
    
    /* Custom Streamlit overrides */
    div.stButton > button {
        width: 100%;
    }
    .stProgress .st-eb {
        background-color: #2b6cb0;
    }
    
    /* Status area */
    .status-container {
        background-color: transparent;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .status-label {
        font-weight: 600;
        margin-top: 4px;
    }
    
    /* Alert styling */
    .alert-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 6px;
    }
    .alert-high {
        background-color: #e53e3e;
        color: white;
    }
    .alert-medium {
        background-color: #ed8936;
        color: white;
    }
    .alert-low {
        background-color: #3182ce;
        color: white;
    }
    
    /* Counter badges */
    .counter-badge {
        background-color: #3182ce;
        color: white;
        padding: 0px 6px;
        border-radius: 10px;
        font-size: 12px;
        margin-left: 6px;
    }
    
    /* Additional formatting */
    .timestamp {
        color: #718096;
        font-size: 12px;
    }
    .highlight {
        font-weight: bold;
        color: #e53e3e;
    }
</style>
""", unsafe_allow_html=True)

# Generate realistic dummy data
def generate_dummy_data():
    now = datetime.datetime.now()
    
    # Create common locations with descriptive names
    locations = [
        "Kamera-01: Pintu Masuk Utama", 
        "Kamera-02: Jalur Pejalan Kaki", 
        "Kamera-03: Area Drop-off", 
        "Kamera-04: Pintu Keluar Belakang"
    ]
    
    # Create detection history with realistic patterns
    # More detections during peak hours (morning, lunch time, evening)
    peak_hours = [8, 9, 12, 13, 17, 18]
    
    # Generate timestamps with weighted distribution toward peak hours
    timestamps = []
    # Past history data - last 5 days
    for day in range(5):
        for hour in range(7, 22):  # Active hours 7 AM - 10 PM
            # Determine number of violations in this hour
            if hour in peak_hours:
                num_violations = random.randint(2, 5)  # More during peak hours
            else:
                num_violations = random.randint(0, 2)  # Fewer during other hours
                
            for _ in range(num_violations):
                violation_time = now - datetime.timedelta(
                    days=day,
                    hours=now.hour-hour,
                    minutes=random.randint(0, 59)
                )
                timestamps.append(violation_time)
    
    # Today's data - more recent
    for hour in range(7, now.hour + 1):
        if hour in peak_hours:
            num_violations = random.randint(1, 4)  # Peak hours today
        else:
            num_violations = random.randint(0, 2)  # Non-peak hours today
            
        for _ in range(num_violations):
            if hour == now.hour:
                minute = random.randint(0, now.minute)
            else:
                minute = random.randint(0, 59)
                
            violation_time = now.replace(hour=hour, minute=minute)
            timestamps.append(violation_time)
    
    # Sort timestamps chronologically
    timestamps.sort()
    
    # Create detection records
    records = []
    for ts in timestamps:
        location = random.choice(locations)
        confidence = round(random.uniform(0.75, 0.98), 2)
        
        # Duration is partly based on location and partly random
        if "Drop-off" in location:
            duration = random.randint(2, 12)  # Shorter at drop-off areas
        elif "Pintu" in location:
            duration = random.randint(10, 40)  # Longer at entrances
        else:
            duration = random.randint(5, 30)
        
        # For recent detections, some might still be active
        is_active = False
        if (now - ts).total_seconds() < duration * 60:
            is_active = True
            
        # Create priority level based on duration and location
        if duration > 30 or "Utama" in location:
            priority = "Tinggi"
        elif duration > 15 or "Pejalan" in location:
            priority = "Sedang"
        else:
            priority = "Rendah"
            
        # Notification status
        notif_sent = not is_active or random.random() < 0.8
            
        records.append({
            "waktu": ts,
            "lokasi": location,
            "confidence": confidence,
            "durasi_menit": duration,
            "status": "Aktif" if is_active else "Selesai",
            "prioritas": priority,
            "notifikasi_terkirim": notif_sent
        })
    
    # Create DataFrame
    detections_df = pd.DataFrame(records)
    
    # Create daily summary
    daily_summary = {}
    for day in range(7):
        date = now.date() - datetime.timedelta(days=day)
        
        # Filter detections for this day
        day_detections = [r for r in records if r["waktu"].date() == date]
        
        # Calculate metrics
        total_count = len(day_detections)
        
        # Only include completed durations
        completed_durations = [r["durasi_menit"] for r in day_detections 
                             if r["status"] == "Selesai"]
        
        avg_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0
        
        # Count by location
        loc_counts = {}
        for loc in locations:
            loc_counts[loc] = len([r for r in day_detections if r["lokasi"] == loc])
            
        daily_summary[date] = {
            "tanggal": date,
            "total": total_count,
            "durasi_rata": avg_duration,
            "lokasi_counts": loc_counts
        }
    
    # Create hourly stats
    hourly_stats = []
    for hour in range(24):
        hour_counts = len([r for r in records if r["waktu"].hour == hour])
        hourly_stats.append({"jam": hour, "jumlah": hour_counts})
    
    hourly_df = pd.DataFrame(hourly_stats)
    
    # Location summary
    location_summary = {}
    for loc in locations:
        loc_records = [r for r in records if r["lokasi"] == loc]
        location_summary[loc] = {
            "total": len(loc_records),
            "aktif": len([r for r in loc_records if r["status"] == "Aktif"]),
            "durasi_rata": sum([r["durasi_menit"] for r in loc_records]) / len(loc_records) if loc_records else 0
        }
    
    # System metrics
    fps = random.uniform(21.5, 28.5)
    latency = random.uniform(35, 95)
    gpu_usage = random.uniform(60, 85)
    
    return detections_df, daily_summary, hourly_df, location_summary, fps, latency, gpu_usage

# Create a realistic CCTV frame with detection overlay
def create_cctv_frame(location, has_violation=False):
    width, height = 640, 480
    
    # Create base image (darker for CCTV look)
    img = Image.new('RGB', (width, height), color=(30, 30, 35))
    draw = ImageDraw.Draw(img)
    
    # Draw grid lines for perspective
    for x in range(0, width, 50):
        # Vertical lines with perspective (closer together at the top)
        draw.line([(x, height), (width//2 + (x - width//2)//2, height//3)], fill=(50, 50, 55), width=1)
    
    for y in range(height//3, height, 50):
        # Horizontal lines
        draw.line([(0, y), (width, y)], fill=(50, 50, 55), width=1)
    
    # Draw a sidewalk area
    draw.rectangle([(50, height-100), (width-50, height)], fill=(60, 60, 65))
    
    # Add some background shapes (buildings, signs)
    draw.rectangle([(50, 50), (150, 150)], fill=(70, 70, 80))
    draw.rectangle([(400, 70), (500, 140)], fill=(65, 65, 75))
    
    # Add location and timestamp text
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.rectangle([(10, 10), (350, 30)], fill=(0, 0, 0, 150))
    draw.text((15, 15), f"{location} | {timestamp}", fill=(240, 240, 240))
    
    # Add recording indicator
    draw.ellipse([(width-25, 15), (width-15, 25)], fill=(255, 0, 0))
    draw.text((width-15, 15), "REC", fill=(255, 255, 255))
    
    if has_violation:
        # Draw a person (tukang parkir)
        person_x = random.randint(100, width-150)
        person_y = height - 80
        
        # Body
        draw.rectangle([(person_x-10, person_y-50), (person_x+10, person_y)], fill=(50, 50, 120))
        # Head
        draw.ellipse([(person_x-8, person_y-70), (person_x+8, person_y-54)], fill=(80, 60, 40))
        # Arms
        draw.line([(person_x-10, person_y-40), (person_x-25, person_y-20)], fill=(50, 50, 120), width=5)
        draw.line([(person_x+10, person_y-40), (person_x+25, person_y-20)], fill=(50, 50, 120), width=5)
        # Legs
        draw.line([(person_x-5, person_y), (person_x-10, person_y+30)], fill=(30, 30, 70), width=8)
        draw.line([(person_x+5, person_y), (person_x+10, person_y+30)], fill=(30, 30, 70), width=8)
        
        # Draw bounding box
        draw.rectangle([(person_x-30, person_y-75), (person_x+30, person_y+35)], outline=(255, 50, 50), width=2)
        
        # Add confidence score
        confidence = random.uniform(0.78, 0.96)
        draw.rectangle([(person_x-30, person_y-95), (person_x+80, person_y-75)], fill=(0, 0, 0, 180))
        draw.text((person_x-25, person_y-90), f"Tukang Parkir: {confidence:.2f}", fill=(255, 50, 50))
        
        # Add a parked vehicle nearby
        vehicle_x = person_x + random.randint(-50, 50)
        vehicle_y = person_y + 10
        
        # Simple car shape
        draw.rectangle([(vehicle_x-40, vehicle_y), (vehicle_x+40, vehicle_y+25)], fill=(120, 120, 140))
        draw.rectangle([(vehicle_x-30, vehicle_y-15), (vehicle_x+30, vehicle_y)], fill=(100, 100, 130))
        # Wheels
        draw.ellipse([(vehicle_x-30, vehicle_y+20), (vehicle_x-20, vehicle_y+30)], fill=(30, 30, 30))
        draw.ellipse([(vehicle_x+20, vehicle_y+20), (vehicle_x+30, vehicle_y+30)], fill=(30, 30, 30))
    
    # Add noise to simulate poor camera quality
    pixels = np.array(img)
    noise = np.random.randint(-10, 10, pixels.shape)
    pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
    
    return Image.fromarray(pixels)

# Function to create active violation counter with unified styling
def show_violation_counter(location, count):
    status_html = ""
    if count > 0:
        status_html = f"<div class='status-active'>AKTIF: {count}</div>"
    else:
        status_html = "<div class='status-clear'>AMAN</div>"
        
    st.markdown(f"""
    <div class='status-container'>
        {status_html}
        <div class='status-label'>{location}</div>
    </div>
    """, unsafe_allow_html=True)

# Function to render a CCTV feed with violation detection
def render_cctv_feed(location, has_violation=False):
    img = create_cctv_frame(location, has_violation)
    st.image(img, use_container_width=True)
    
    if has_violation:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.error("⚠️ Terdeteksi Tukang Parkir Liar!")
            
        with col2:
            confidence = random.uniform(0.78, 0.96)
            st.metric("Confidence", f"{confidence:.2f}")
        
        # Detection details
        detection_time = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 15))
        duration = random.randint(1, 15)
        
        st.markdown(f"""
        <div style="font-size: 0.9em">
        ⏱️ <span class="timestamp">Terdeteksi {detection_time.strftime('%H:%M:%S')}</span> | 
        ⌛ <span class="timestamp">Durasi: {duration} menit</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✓ Area aman - tidak ada tukang parkir terdeteksi")

# Function to display notification with priority level
def display_notification(notification):
    priority = notification.get("prioritas", "Rendah")
    priority_class = {
        "Tinggi": "notification-high",
        "Sedang": "notification-medium",
        "Rendah": "notification-low"
    }.get(priority, "notification-low")
    
    badge_class = {
        "Tinggi": "alert-high",
        "Sedang": "alert-medium",
        "Rendah": "alert-low"
    }.get(priority, "alert-low")
    
    notification_time = notification.get("waktu", datetime.datetime.now())
    time_str = notification_time.strftime("%H:%M:%S")
    
    notif_sent = notification.get("notifikasi_terkirim", False)
    notif_status = "✓ Terkirim" if notif_sent else "⏳ Pending"
    
    st.markdown(f"""
    <div class="{priority_class}">
        <div style="display: flex; justify-content: space-between;">
            <div>
                <span class="alert-badge {badge_class}">{priority}</span>
                <b>{time_str}</b> Tukang parkir terdeteksi di <b>{notification.get('lokasi')}</b>
            </div>
            <div>
                {notif_status}
            </div>
        </div>
        <div style="margin-top: 5px; font-size: 0.9em">
            Confidence: <b>{notification.get('confidence', 0.8):.2f}</b> | 
            Durasi: <b>{notification.get('durasi_menit', 5)} menit</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar navigation and controls
with st.sidebar:
    st.title("🚨 Deteksi Parkir Liar")
    st.caption("Sistem Monitoring Pelanggaran Real-time")
    
    st.divider()
    
    # Navigation menu
    selected = st.radio(
        "Menu Navigasi",
        ["📹 Monitoring Real-time", "📊 Statistik Pelanggaran", "📋 Riwayat Deteksi"]
    )
    menu = selected.split(" ", 1)[1]  # Remove the emoji prefix
    
    st.divider()
    
    # Control panel in sidebar
    st.subheader("Panel Kontrol")
    detection_active = st.toggle("Aktifkan Deteksi", value=True)
    
    confidence_threshold = st.slider(
        "Confidence Threshold", 
        min_value=0.5, 
        max_value=1.0, 
        value=0.75, 
        step=0.05,
        help="Nilai minimum untuk mendeteksi tukang parkir"
    )
    
    st.subheader("Kamera Aktif")
    cameras = {
        "cam1": st.checkbox("Kamera-01: Pintu Masuk Utama", value=True),
        "cam2": st.checkbox("Kamera-02: Jalur Pejalan Kaki", value=True),
        "cam3": st.checkbox("Kamera-03: Area Drop-off", value=True),
        "cam4": st.checkbox("Kamera-04: Pintu Keluar Belakang", value=False)
    }
    active_cameras = sum(cameras.values())
    
    # System metrics
    st.divider()
    st.subheader("Status Sistem")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("FPS", "25.3")
    with col2:
        st.metric("Latency", "68ms")

    # Get dummy data
    detections_df, daily_summary, hourly_df, location_summary, fps, latency, gpu_usage = generate_dummy_data()
    
    # Show today's summary
    today = datetime.datetime.now().date()
    
    if today in daily_summary:
        today_data = daily_summary[today]
        st.info(f"""
        **Hari ini:** {today_data['total']} deteksi  
        **Aktif saat ini:** {len(detections_df[detections_df['status'] == 'Aktif'])}
        """)

# Main content area
if menu == "Monitoring Real-time":
    # Header with current time
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %d %B %Y")
    time_str = now.strftime("%H:%M:%S")
    
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <div>{date_str}</div>
        <div>{time_str}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='main-header'>Monitoring Real-time Tukang Parkir Liar</div>", unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        today_detections = len([d for d in detections_df.to_dict('records') 
                              if d['waktu'].date() == datetime.datetime.now().date()])
        yesterday_detections = len([d for d in detections_df.to_dict('records') 
                                  if d['waktu'].date() == (datetime.datetime.now() - datetime.timedelta(days=1)).date()])
        delta = today_detections - yesterday_detections
        delta_str = f"{delta:+d}" if delta else None
        st.metric("Total Deteksi Hari Ini", today_detections, delta=delta_str)
    
    with col2:
        active_count = len(detections_df[detections_df['status'] == 'Aktif'])
        st.metric("Pelanggaran Aktif Saat Ini", active_count)
        
    with col3:
        st.metric("Kamera Aktif", f"{active_cameras}/4")
        
    with col4:
        st.metric("Durasi Rata-rata", f"{detections_df['durasi_menit'].mean():.1f} menit")
    
    # CCTV Feed section
    st.markdown("<div class='sub-header'>Tampilan CCTV</div>", unsafe_allow_html=True)
    
    # Select between grid view and single camera focus
    view_type = st.radio("Tampilan:", ["Grid (Semua Kamera)", "Fokus (Satu Kamera)"], horizontal=True)
    
    if view_type == "Grid (Semua Kamera)":
        # Grid of CCTV feeds
        col1, col2 = st.columns(2)
        with col1:
            # Let's simulate Kamera-01 and Kamera-04 having violations
            render_cctv_feed("Kamera-01: Pintu Masuk Utama", has_violation=True)
        with col2:
            render_cctv_feed("Kamera-02: Jalur Pejalan Kaki", has_violation=False)
            
        col3, col4 = st.columns(2)
        with col3:
            render_cctv_feed("Kamera-03: Area Drop-off", has_violation=False)
        with col4:
            render_cctv_feed("Kamera-04: Pintu Keluar Belakang", has_violation=True)
    else:
        # Single camera view with larger display
        selected_camera = st.selectbox(
            "Pilih Kamera:",
            ["Kamera-01: Pintu Masuk Utama", "Kamera-02: Jalur Pejalan Kaki",
             "Kamera-03: Area Drop-off", "Kamera-04: Pintu Keluar Belakang"]
        )
        
        # Show violations on cameras 1 and 4
        has_violation = "Kamera-01" in selected_camera or "Kamera-04" in selected_camera
        render_cctv_feed(selected_camera, has_violation=has_violation)
        
        # Add additional controls for focused view
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("📸 Ambil Screenshot")
        with col2:
            st.button("👮‍♂️ Panggil Petugas")
        with col3:
            st.button("⏺️ Rekam Bukti")
    
    # Status area section
    st.markdown("<div class='sub-header'>Status Area</div>", unsafe_allow_html=True)
    
    # Status indicators for each camera
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_violation_counter("Kamera-01: Pintu Masuk Utama", 2)
    with col2:
        show_violation_counter("Kamera-02: Jalur Pejalan Kaki", 0)
    with col3:
        show_violation_counter("Kamera-03: Area Drop-off", 0)
    with col4:
        show_violation_counter("Kamera-04: Pintu Keluar Belakang", 1)
    
    # Alert panel
    st.markdown("<div class='sub-header'>Panel Alert Real-time</div>", unsafe_allow_html=True)
    
    # Filter for active detections and sort by priority
    active_detections = detections_df[detections_df['status'] == 'Aktif'].copy()
    
    # If no active detections, show a message
    if len(active_detections) == 0:
        st.success("Tidak ada pelanggaran aktif saat ini.")
    else:
        # Order by priority (High, Medium, Low) then by most recent
        priority_map = {"Tinggi": 0, "Sedang": 1, "Rendah": 2}
        active_detections['priority_value'] = active_detections['prioritas'].map(priority_map)
        active_detections = active_detections.sort_values(by=['priority_value', 'waktu'], ascending=[True, False])
        
        # Display notifications
        for idx, alert in active_detections.iterrows():
            display_notification(alert)
    
    # Recent alerts toggle
    with st.expander("Riwayat Alert (24 Jam Terakhir)"):
        # Get alerts from past 24 hours
        recent_time = datetime.datetime.now() - datetime.timedelta(hours=24)
        recent_alerts = detections_df[detections_df['waktu'] >= recent_time]
        
        if len(recent_alerts) == 0:
            st.info("Tidak ada riwayat alert dalam 24 jam terakhir.")
        else:
            # Order by time, most recent first
            recent_alerts = recent_alerts.sort_values(by='waktu', ascending=False).head(10)
            
            for idx, alert in recent_alerts.iterrows():
                display_notification(alert)

elif menu == "Statistik Pelanggaran":
    st.markdown("<div class='main-header'>Statistik dan Analitik Pelanggaran</div>", unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Dari Tanggal",
            value=datetime.datetime.now().date() - datetime.timedelta(days=6)
        )
    with col2:
        end_date = st.date_input(
            "Sampai Tanggal",
            value=datetime.datetime.now().date()
        )
    
    # Summary metrics
    st.markdown("<div class='sub-header'>Ringkasan Pelanggaran</div>", unsafe_allow_html=True)
    
    # Convert daily summary to DataFrame for the selected date range
    daily_df = pd.DataFrame([
        {
            "tanggal": date,
            "total": data["total"],
            "durasi_rata": data["durasi_rata"]
        }
        for date, data in daily_summary.items()
        if start_date <= date <= end_date
    ])
    
    # Calculate summary metrics
    total_violations = daily_df["total"].sum()
    avg_duration = daily_df["durasi_rata"].mean()
    max_day = daily_df.loc[daily_df["total"].idxmax()]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pelanggaran", f"{total_violations}")
    with col2:
        st.metric("Durasi Rata-rata", f"{avg_duration:.1f} menit")
    with col3:
        st.metric("Hari Terpadat", max_day["tanggal"].strftime("%d/%m/%Y"))
    with col4:
        st.metric("Jumlah di Hari Terpadat", max_day["total"])
    
    # Daily trend chart
    st.markdown("<div class='sub-header'>Tren Pelanggaran Harian</div>", unsafe_allow_html=True)
    
    # Ensure dates are sorted
    daily_df = daily_df.sort_values("tanggal")
    
    # Create a nicer date format for display
    daily_df["tanggal_str"] = daily_df["tanggal"].apply(lambda d: d.strftime("%d/%m"))
    
    fig = px.bar(
        daily_df,
        x="tanggal_str",
        y="total",
        text="total",
        labels={"total": "Jumlah Pelanggaran", "tanggal_str": "Tanggal"},
        title="Jumlah Pelanggaran per Hari",
        color="total",
        color_continuous_scale=px.colors.sequential.Blues
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Hourly pattern and location distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sub-header'>Pola Pelanggaran per Jam</div>", unsafe_allow_html=True)
        
        # Add time period labels
        hourly_df["periode"] = hourly_df["jam"].apply(lambda h: 
            "Pagi (5-10)" if 5 <= h < 10 else
            "Siang (10-14)" if 10 <= h < 14 else
            "Sore (14-18)" if 14 <= h < 18 else
            "Malam (18-22)" if 18 <= h < 22 else
            "Dini Hari (22-5)"
        )
        
        fig = px.line(
            hourly_df,
            x="jam",
            y="jumlah",
            markers=True,
            labels={"jumlah": "Jumlah Pelanggaran", "jam": "Jam"},
            title="Distribusi Pelanggaran Sepanjang Hari",
            color="periode",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Find peak hours
        peak_hour = hourly_df.loc[hourly_df["jumlah"].idxmax()]
        st.info(f"""
        **Jam Puncak:** {peak_hour['jam']}:00 - {(peak_hour['jam']+1) % 24}:00 dengan {peak_hour['jumlah']} pelanggaran
        
        Sebagian besar pelanggaran terjadi pada periode **{hourly_df.groupby('periode')['jumlah'].sum().idxmax()}**
        """)
    
    with col2:
        st.markdown("<div class='sub-header'>Distribusi per Lokasi</div>", unsafe_allow_html=True)
        
        # Convert location summary to a DataFrame for plotting
        location_df = pd.DataFrame([
            {
                "lokasi": loc,
                "total": data["total"],
                "aktif": data["aktif"],
                "durasi_rata": data["durasi_rata"]
            }
            for loc, data in location_summary.items()
        ])
        
        fig = px.pie(
            location_df,
            values="total",
            names="lokasi",
            title="Proporsi Pelanggaran per Lokasi Kamera",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Location details
    st.markdown("<div class='sub-header'>Detail per Lokasi</div>", unsafe_allow_html=True)
    
    # Create a bar chart comparing locations
    fig = px.bar(
        location_df,
        x="lokasi",
        y="total",
        color="durasi_rata",
        text="total",
        labels={"total": "Jumlah Pelanggaran", "lokasi": "Lokasi", "durasi_rata": "Durasi Rata-rata (menit)"},
        title="Perbandingan Jumlah dan Durasi Pelanggaran per Lokasi",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Location comparison table
    st.dataframe(
        location_df[["lokasi", "total", "aktif", "durasi_rata"]].rename(columns={
            "lokasi": "Lokasi", 
            "total": "Total Pelanggaran",
            "aktif": "Pelanggaran Aktif",
            "durasi_rata": "Durasi Rata-rata (menit)"
        }).set_index("Lokasi").style.format({
            "Durasi Rata-rata (menit)": "{:.1f}"
        }),
        use_container_width=True
    )
    
    # Perbaikan untuk distribusi durasi
    st.markdown("<div class='sub-header'>Distribusi Durasi Pelanggaran</div>", unsafe_allow_html=True)

    # Pastikan nilai bin selalu meningkat monoton
    max_duration = max(detections_df["durasi_menit"]) if not detections_df.empty else 61
    if max_duration <= 60:
        max_duration = 61  # Memastikan bin terakhir selalu lebih besar dari 60

    # Create duration bins dengan nilai yang pasti meningkat
    duration_bins = [0, 5, 10, 15, 30, 60, max_duration]
    labels = ["<5", "5-10", "10-15", "15-30", "30-60", ">60"]
    
    detections_df["durasi_kategori"] = pd.cut(
        detections_df["durasi_menit"], 
        bins=duration_bins,
        labels=labels
    )
    
    duration_counts = detections_df["durasi_kategori"].value_counts().sort_index()
    
    fig = px.bar(
        x=duration_counts.index,
        y=duration_counts.values,
        labels={"x": "Durasi (menit)", "y": "Jumlah Pelanggaran"},
        title="Distribusi Durasi Pelanggaran",
        color=duration_counts.values,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Riwayat Deteksi":
    st.markdown("<div class='main-header'>Riwayat Deteksi Tukang Parkir Liar</div>", unsafe_allow_html=True)
    
    # Advanced filters
    with st.expander("Filter Lanjutan"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date filter
            date_filter = st.date_input("Pilih Tanggal", datetime.datetime.now().date())
            
            # Status filter
            status_filter = st.multiselect(
                "Status",
                options=["Aktif", "Selesai"],
                default=["Aktif", "Selesai"]
            )
        
        with col2:
            # Location filter
            locations = detections_df["lokasi"].unique()
            location_filter = st.multiselect(
                "Lokasi",
                options=locations,
                default=locations
            )
            
            # Priority filter
            priority_filter = st.multiselect(
                "Prioritas",
                options=["Tinggi", "Sedang", "Rendah"],
                default=["Tinggi", "Sedang", "Rendah"]
            )
        
        with col3:
            # Confidence threshold
            confidence_filter = st.slider(
                "Confidence Minimum",
                min_value=0.5,
                max_value=1.0,
                value=0.5,
                step=0.05
            )
            
            # Duration filter
            min_duration, max_duration = st.slider(
                "Rentang Durasi (menit)",
                min_value=0,
                max_value=60,
                value=(0, 60)
            )
        
        # Apply button for filters
        filter_button = st.button("Terapkan Filter", use_container_width=True)
    
    # Apply filters to the data
    filtered_df = detections_df.copy()
    
    # Filter by date
    filtered_df = filtered_df[filtered_df["waktu"].dt.date == date_filter]
    
    # Apply other filters
    if status_filter:
        filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
        
    if location_filter:
        filtered_df = filtered_df[filtered_df["lokasi"].isin(location_filter)]
        
    if priority_filter:
        filtered_df = filtered_df[filtered_df["prioritas"].isin(priority_filter)]
        
    filtered_df = filtered_df[filtered_df["confidence"] >= confidence_filter]
    filtered_df = filtered_df[(filtered_df["durasi_menit"] >= min_duration) & 
                             (filtered_df["durasi_menit"] <= max_duration)]
    
    # Display data overview
    st.markdown("<div class='sub-header'>Data Deteksi</div>", unsafe_allow_html=True)
    
    # Display summary count
    st.info(f"Menampilkan {len(filtered_df)} dari {len(detections_df[detections_df['waktu'].dt.date == date_filter])} deteksi pada tanggal {date_filter.strftime('%d/%m/%Y')}")
    
    # Data table with formatting
    if not filtered_df.empty:
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df["waktu"] = display_df["waktu"].dt.strftime("%H:%M:%S")
        display_df = display_df.rename(columns={
            "waktu": "Waktu",
            "lokasi": "Lokasi",
            "confidence": "Confidence",
            "durasi_menit": "Durasi (menit)",
            "status": "Status",
            "prioritas": "Prioritas"
        })
        
        # Keep only the columns we want to display
        display_cols = ["Waktu", "Lokasi", "Confidence", "Durasi (menit)", "Status", "Prioritas"]
        display_df = display_df[display_cols]
        
        # Apply styling based on status
        def style_status(val):
            if val == "Aktif":
                return "background-color: #FEE2E2; color: #991B1B"
            return "background-color: #D1FAE5; color: #065F46"
        
        # Apply styling based on priority
        def style_priority(val):
            colors = {
                "Tinggi": "background-color: #FEE2E2; color: #991B1B",
                "Sedang": "background-color: #FFEDD5; color: #92400E",
                "Rendah": "background-color: #DBEAFE; color: #1E40AF"
            }
            return colors.get(val, "")
        
        # Apply styles
        styled_df = display_df.style.format({
            "Confidence": "{:.2f}"
        }).applymap(style_status, subset=["Status"]).applymap(style_priority, subset=["Prioritas"])
        
        # Show the styled dataframe
        st.dataframe(styled_df, use_container_width=True, height=300)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Export CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name=f"deteksi_parkir_{date_filter}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📊 Export Excel",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name=f"deteksi_parkir_{date_filter}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
    else:
        st.warning("Tidak ada data yang sesuai dengan filter")
    
    # Detail view for selected detection
    st.markdown("<div class='sub-header'>Detail Deteksi</div>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        # Create options for select box with timestamps
        detection_options = [f"{i}: {row['waktu'].strftime('%H:%M:%S')} - {row['lokasi']}" 
                            for i, row in filtered_df.reset_index().iterrows()]
        
        selected_detection = st.selectbox(
            "Pilih deteksi untuk melihat detail:",
            options=detection_options
        )
        
        if selected_detection:
            # Extract index from selection
            selected_idx = int(selected_detection.split(":")[0])
            detection = filtered_df.iloc[selected_idx]
            
            # Display detection details
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Show CCTV frame with detection
                img = create_cctv_frame(detection["lokasi"], True)
                st.image(img, use_container_width=True, caption="Screenshot Deteksi")
            
            with col2:
                # Use Streamlit components for detail card instead of HTML table
                st.subheader(f"Deteksi #{selected_idx}")
                
                # Create a clean card-like container
                with st.container():
                    # Add some padding and styling
                    st.markdown('<div style="padding: 1px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">', unsafe_allow_html=True)
                    
                    # Use columns for label-value pairs
                    detail_items = [
                        ("Waktu", detection["waktu"].strftime("%d/%m/%Y %H:%M:%S")),
                        ("Lokasi", detection["lokasi"]),
                        ("Confidence", f"{detection['confidence']:.2f}"),
                        ("Durasi", f"{detection['durasi_menit']} menit"),
                        ("Status", detection["status"]),
                        ("Prioritas", detection["prioritas"]),
                        ("Notifikasi", "Terkirim" if detection["notifikasi_terkirim"] else "Belum terkirim")
                    ]
                    
                    # Style status and priority differently
                    for label, value in detail_items:
                        col_label, col_value = st.columns([1, 2])
                        
                        with col_label:
                            st.markdown(f"**{label}:**")
                        
                        with col_value:
                            if label == "Status":
                                color = "#ef4444" if value == "Aktif" else "#10b981"
                                st.markdown(f'<span style="color: {color}; font-weight: 500;">{value}</span>', unsafe_allow_html=True)
                            elif label == "Prioritas":
                                colors = {
                                    "Tinggi": "#991B1B",
                                    "Sedang": "#92400E", 
                                    "Rendah": "#1E40AF"
                                }
                                bg_colors = {
                                    "Tinggi": "#FEE2E2",
                                    "Sedang": "#FFEDD5", 
                                    "Rendah": "#DBEAFE"
                                }
                                color = colors.get(value, "#1E40AF")
                                bg_color = bg_colors.get(value, "#DBEAFE")
                                st.markdown(
                                    f'<span style="background-color: {bg_color}; color: {color}; padding: 2px 8px; '
                                    f'border-radius: 12px; font-size: 0.9em; font-weight: 500;">{value}</span>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.write(value)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Action buttons
                st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
                col1, col2 = st.columns(2)
                with col1:
                    if detection["status"] == "Aktif":
                        st.button("✅ Tandai Selesai", key=f"mark_{selected_idx}", use_container_width=True)
                    else:
                        st.button("🔄 Buka Kembali", key=f"reopen_{selected_idx}", use_container_width=True)
                        
                with col2:
                    if not detection["notifikasi_terkirim"]:
                        st.button("📩 Kirim Notifikasi", key=f"notify_{selected_idx}", use_container_width=True)
                    else:
                        st.button("📲 Kirim Ulang Notifikasi", key=f"renotify_{selected_idx}", use_container_width=True)
    else:
        st.warning("Pilih deteksi terlebih dahulu untuk melihat detailnya")

# Footer with app version and copyright
st.markdown("""
<div style="margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; 
            display: flex; justify-content: space-between; color: #64748b; font-size: 0.8em;">
    <div>Sistem Deteksi Parkir Liar v1.0</div>
    <div>© 2025 Keamanan & Penertiban</div>
</div>
""", unsafe_allow_html=True)