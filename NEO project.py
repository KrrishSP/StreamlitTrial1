import requests
import numpy as np
import plotly.graph_objects as go

# ---------------- API CALL ----------------
API_KEY = "Qzrl1s2oyyqFmKPghoS54vTvWxZAagovj707VWtk"
API_URL = f"https://api.nasa.gov/neo/rest/v1/feed?api_key={API_KEY}"

response = requests.get(API_URL)
data = response.json()

names = []
distances = []
sizes = []
numbers = []
hazardous_list = []

counter = 1

# ---------------- FETCH DATA ----------------
for date in data["near_earth_objects"]:
    for neo in data["near_earth_objects"][date]:
        name = neo["name"]
        size = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
        dist = float(neo["close_approach_data"][0]["miss_distance"]["kilometers"])
        is_hazardous = neo["is_potentially_hazardous_asteroid"]

        # Scale distance for visualization
        scaled_dist = dist / 1_000_000

        names.append(name)
        distances.append(scaled_dist)
        sizes.append(size)
        numbers.append(counter)
        hazardous_list.append(is_hazardous)

        counter += 1

# ---------------- 3D POSITIONS ----------------
theta = np.linspace(0, 2*np.pi, len(distances))
phi = np.linspace(0, np.pi, len(distances))

x = np.array(distances) * np.cos(theta)
y = np.array(distances) * np.sin(theta)
z = np.array(distances) * np.cos(phi)

# ---------------- EARTH PYRAMID ----------------
pyramid_vertices = np.array([
    [0, 0, 0.4],     # top
    [-0.3, -0.3, 0],
    [0.3, -0.3, 0],
    [0.3, 0.3, 0],
    [-0.3, 0.3, 0]
])

faces = [
    [0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1],   # sides
    [1, 2, 3, 4]                                  # base
]

# ---------------- CREATE FIGURE ----------------
fig = go.Figure()

# ---- Add NEO points colored by hazard ----
hazard_values = [1 if h else 0 for h in hazardous_list]

fig.add_trace(go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode="markers+text",
    marker=dict(
        size=np.array(sizes)/50,
        color=hazard_values,
        colorscale=[[0, "green"], [1, "red"]],
        showscale=True,
        colorbar=dict(
            title=dict(text="Hazard Level"),  # fixed
            tickvals=[0, 1],
            ticktext=["Safe", "Hazardous"],
            thickness=15,
            len=0.75,
            x=1.05
        )
    ),
    text=[str(n) for n in numbers],
    textposition="top center",
    hovertext=[f"{numbers[i]}. {names[i]}<br>Hazard: {'YES' if hazardous_list[i] else 'No'}"
               for i in range(len(names))],
    hoverinfo="text"
))


# ---- Add Earth Pyramid ----
for face in faces:
    face_vertices = pyramid_vertices[face]
    fig.add_trace(go.Mesh3d(
        x=face_vertices[:, 0],
        y=face_vertices[:, 1],
        z=face_vertices[:, 2],
        color="red",
        opacity=1.0,
        name="Earth"
    ))

# ---------------- LAYOUT ----------------
fig.update_layout(
    title="Interactive 3D Near-Earth Object Map",
    scene=dict(
        xaxis_title="X (scaled)",
        yaxis_title="Y (scaled)",
        zaxis_title="Z (scaled)",
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
    ),
    legend=dict(x=0.02, y=0.02)
)

fig.show()
