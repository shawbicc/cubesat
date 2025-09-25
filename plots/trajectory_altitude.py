import pandas as pd
import matplotlib.pyplot as plt
import os

csv_path = '../20250925_151721.csv'
csv_name = os.path.basename(csv_path)
png_name = f"traj_alt_{csv_name.replace('.csv', '.png')}"

# Load CSV, skipping rows with missing GPS data
df = pd.read_csv(csv_path)
df_gps = df.dropna(subset=['timestamp(gps)', 'latitude', 'longitude', 'altitude'])

# Convert timestamp to numeric
df_gps['timestamp(gps)'] = pd.to_numeric(df_gps['timestamp(gps)'], errors='coerce')
df_gps = df_gps.dropna(subset=['timestamp(gps)'])

# Convert unix time to seconds since first timestamp
t0 = df_gps['timestamp(gps)'].iloc[0]
df_gps['time_sec'] = df_gps['timestamp(gps)'] - t0

# Plotting
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

# Trajectory plot (Latitude vs Longitude)
axs[0].plot(df_gps['longitude'], df_gps['latitude'], marker='o', linestyle='-')
axs[0].set_title('GPS Trajectory')
axs[0].set_xlabel('Longitude')
axs[0].set_ylabel('Latitude')
axs[0].grid(True)

# Altitude vs Time plot (seconds since t=0)
axs[1].plot(df_gps['time_sec'], df_gps['altitude'], marker='o', linestyle='-')
axs[1].set_title('Altitude vs Time (t=0 at first GPS sample)')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Altitude (m)')
axs[1].grid(True)

plt.tight_layout()
plt.savefig(png_name)
plt.show()