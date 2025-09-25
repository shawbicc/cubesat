import pandas as pd
import matplotlib.pyplot as plt

def plot_gps_trajectory(csv_file):
    # Read CSV
    df = pd.read_csv(csv_file)

    # Extract latitude (2nd col) and longitude (3rd col)
    latitudes = df.iloc[:, 1]
    longitudes = df.iloc[:, 2]

    # Plot trajectory
    plt.figure(figsize=(8, 6))
    plt.plot(longitudes, latitudes, marker='o', linestyle='-', color='blue')

    # Mark start and end
    plt.plot(longitudes.iloc[0], latitudes.iloc[0], marker='o', color='green', markersize=10, label="Start")
    plt.plot(longitudes.iloc[-1], latitudes.iloc[-1], marker='o', color='red', markersize=10, label="End")

    # Labels
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("2D GPS Trajectory")
    plt.legend()
    plt.grid(True)
    plt.axis("equal")  # Keep aspect ratio correct

    plt.show()
    plt.savefig("gps_trajectory.png")


if __name__ == "__main__":
    # Replace 'gps_data.csv' with your CSV filename
    plot_gps_trajectory("gps_air_data.csv")
