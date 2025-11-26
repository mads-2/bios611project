import os

# ============================================================
# FORCE SINGLE-THREAD BLAS FOR TRUE DETERMINISM
# ============================================================

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import numpy as np
import plotly.graph_objects as go
from sklearn.manifold import TSNE
import ast
from itertools import combinations

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# AESTHETICS CONFIG
# ============================================================

AESTHETICS = {
    "FA_DORFic":          "D_embedding.html",
    "FA_classic":         "FA_embedding.html",
    "FA_Frutiger_Metro":  "FM_embedding.html",
    "FA_Frutiger_Eco":    "FE_embedding.html",
    "FA_Technozen":       "T_embedding.html",
    "FA_Dark_Aero":       "DA_embedding.html",
}

# ============================================================
# NEW UPDATED CLUSTERS (CONNECTIONS)
# ============================================================

CLUSTERS = {

    # --------------------------------------------------------
    "FA_classic": [
        ["Goldfish", "Aquarium", "Underwater"],
        ["Strawberry", "Rangpur", "Orange", "Lemon"],
        ["Ceiling", "Floor"],
        ["Bead", "Marble", "Gemstone"],
        ["Ball", "Spring", "Balance"],
        ["Coral_Reef_Fish", "Sea", "Fin", "Ocellaris_Clownfish"],
        ["Lobby", "Waiting_Room"],
        ["Field", "Park", "Grasses"],
        ["Highway", "Intersection"],
        ["Computer_Program", "Computer_Monitor", "Computer_Hardware", "Computer"],
        ["Wind_Wave", "Wind", "Cumulus", "Sunlight"],
    ],

    # --------------------------------------------------------
    "FA_DORFic": [
        ["Mobile_Phone", "Personal_Computer", "Electronic_Device"],
        ["Technology", "Gadget", "Electronics"],
        ["Floor", "Tile", "Flooring"],
        ["Yellow", "Orange"],
        ["Produce", "Food", "Natural_Foods"],
        ["Clock", "Measuring_Instrument"],
        ["Electrical_Cable", "Wire"],
    ],

    # --------------------------------------------------------
    "FA_Frutiger_Eco": [
        ["Graphic_Design", "Advertising"],
        ["Field", "Garden", "Green"],
        ["Jewelry_Making", "Bracelet", "Gemstone"],
        ["Pasture", "Grasslands", "Prarie"],
        ["Wall", "Ceiling", "Room"],
        ["Pharmaceutical_Drug", "Stimulant", "Medicine", "Pill"],
    ],

    # --------------------------------------------------------
    "FA_Dark_Aero": [
        ["Darkness", "Constellation", "Night"],
        ["Night", "Moonlight", "Full_Moon"],
        ["Game_Controller", "Joystick"],
        ["Celestial_Event", "Astronomical_Object"],
        ["Skyline", "Metropolitan_Area", "Skyscraper"],
        ["Night", "Constellation"],
    ],

    # --------------------------------------------------------
    "FA_Frutiger_Metro": [
        ["Freestyle_Motocross", "Bmx"],
        ["Physical_Fitness", "Zumba"],
        ["Black", "Monochrome", "White"],
        ["Animation", "Animated_Cartoon"],
        ["Glass_Bottle", "Label", "Soft_Drink"],
        ["Fixed-Wing_Aircraft", "Aircraft", "Aerospace_Engineering"],
    ],

    # --------------------------------------------------------
    "FA_Technozen": [
        ["Racketlon", "Soft_Tennis", "Tennis_Court", "Tennis_Equiptment_And_Supplies"],
        ["Bamboo", "Evergreen", "Aloes"],
        ["Steel", "Iron", "Metal", "Aluminum", "Silver"],
        ["Bathroom", "Bathtub", "Tile", "Plumbing"],
        ["Houseplant", "Flower_Pot"],
        ["Car", "Car_Door", "Fender"],
	["Office_Supplies", "Office_Equiptment", "Chair", "Office_Chair"],
    ],
}

# ============================================================
# OUTLIERS (HIDDEN FROM PLOT BUT INCLUDED IN t-SNE)
# ============================================================

OUTLIERS = {
    "FA_classic": ["Blue", "Ocean"],
    "FA_DORFic": ["Graphic_Design", "Plastic", "Interior_Design", "Apples"],
    "FA_Frutiger_Eco": ["Floor"],
    "FA_Dark_Aero": ["Audio_Equiptment", "Loudspeaker", "Operating_System"],
    "FA_Frutiger_Metro": [
        "Black", "Sticker", "Motif", "Mobile_Device",
        "Compact_Disk", "Silhouette", "Wallpaper", "Psychadelic_Art",
    ],
    "FA_Technozen": ["Shelving", "Corporate_Headquarters"],
}

# ============================================================
# FULLY DETERMINISTIC t-SNE
# ============================================================

def run_tsne(vectors):
    print("Running deterministic t-SNE…")

    tsne = TSNE(
        n_components=3,
        perplexity=10,
        learning_rate=200,
        n_jobs=1,
        verbose=1,
        random_state=242,
        init="pca",
        method="exact",
        early_exaggeration=12.0,
        max_iter=1000,
    )

    return tsne.fit_transform(vectors)

# ============================================================
# PLOT GENERATION FUNCTION
# ============================================================

def generate_plot(aesthetic, output_filename):
    print(f"\n============================")
    print(f"Processing {aesthetic}")
    print(f"============================")

    vector_file = os.path.join(PROJECT_ROOT, "images", aesthetic,
                               "vectors_object_instances.txt")

    if not os.path.exists(vector_file):
        print(f"Missing: {vector_file}")
        return

    labels = []
    scores = []
    instances = []
    vectors = []

    # =======================================================
    # LOAD ALL VECTORS — NO OUTLIERS REMOVED FOR t-SNE
    # =======================================================

    with open(vector_file, "r") as f:
        for line in f:
            if ":" not in line:
                continue

            try:
                name, score, inst, vec_str = line.strip().split(":", 3)
                labels.append(name)
                scores.append(float(score))
                instances.append(int(inst))
                vectors.append(ast.literal_eval(vec_str))

            except:
                continue

    vectors = np.array(vectors)
    print(f"✓ Loaded {len(vectors)} vectors (including outliers)")

    # =======================================================
    # RUN t-SNE ON FULL SET (MATCHES d_embedding_plot.py)
    # =======================================================

    coords = run_tsne(vectors)
    x_all, y_all, z_all = coords[:, 0], coords[:, 1], coords[:, 2]

    # =======================================================
    # DROP OUTLIERS *ONLY FOR PLOTTING*
    # =======================================================

    drop = set(OUTLIERS.get(aesthetic, []))

    keep_indices = [i for i, lbl in enumerate(labels) if lbl not in drop]

    filtered_labels = [labels[i] for i in keep_indices]
    filtered_instances = [instances[i] for i in keep_indices]
    x = x_all[keep_indices]
    y = y_all[keep_indices]
    z = z_all[keep_indices]

    print(f"✓ Plotting {len(filtered_labels)} points after hiding outliers")

    sizes = [(inst * 2) + 6 for inst in filtered_instances]

    fig = go.Figure()

    # =======================================================
    # POINT CLOUD
    # =======================================================

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers",
        marker=dict(
            size=sizes,
            color=filtered_instances,
            colorscale="Viridis",
            opacity=0.9
        ),
        text=filtered_labels,
        hovertemplate="<b>%{text}</b><br>Instances=%{marker.size}<extra></extra>",
        name="Points"
    ))

    # =======================================================
    # ADD CLUSTER CONNECTION LINES (ON FILTERED POINTS)
    # =======================================================

    if aesthetic in CLUSTERS:
        label_to_idx = {label: i for i, label in enumerate(filtered_labels)}
        color_i = 0

        LINE_COLORS = [
            "rgba(255,120,120,0.85)",
            "rgba(120,255,120,0.85)",
            "rgba(120,120,255,0.85)",
            "rgba(255,200,120,0.85)",
            "rgba(180,120,255,0.85)",
            "rgba(120,255,255,0.85)",
            "rgba(255,180,220,0.85)",
            "rgba(220,255,180,0.85)",
        ]

        for group in CLUSTERS[aesthetic]:
            indices = [label_to_idx[l] for l in group if l in label_to_idx]
            group_color = LINE_COLORS[color_i % len(LINE_COLORS)]
            color_i += 1

            for i, j in combinations(indices, 2):
                fig.add_trace(go.Scatter3d(
                    x=[x[i], x[j]],
                    y=[y[i], y[j]],
                    z=[z[i], z[j]],
                    mode="lines",
                    line=dict(color=group_color, width=4),
                    hovertemplate=f"<b>{filtered_labels[i]} ↔ {filtered_labels[j]}</b><extra></extra>",
                    showlegend=False
                ))

    # =======================================================
    # PAGE LAYOUT (WITH t-SNE CAVEAT NOTE)
    # =======================================================

    fig.update_layout(
        title=(
            f"3D t-SNE — {aesthetic} Object Embeddings<br>"
            f"<span style='font-size:16px;color:#bbb;'>"
            f"Note: t-SNE preserves some local relationships, but dissimilar words may appear close together "
            f"and similar words may appear far apart due to dimensionality reduction."
            f"</span>"
        ),
        scene=dict(
            xaxis_title="t-SNE 1",
            yaxis_title="t-SNE 2",
            zaxis_title="t-SNE 3",
            bgcolor="#111",
        ),
        paper_bgcolor="#111",
        plot_bgcolor="#111",
        font=dict(color="white"),
        showlegend=False,
        margin=dict(l=0, r=0, t=60, b=0),
    )

    # =======================================================
    # DISCLAIMER
    # =======================================================

    disclaimer = """
        <div style='
            color: #ccc;
            font-size: 16px;
            margin-top: 25px;
            margin-bottom: 20px;
            width: 80%;
            text-align: center;
            line-height: 1.4;
        '>
            <b>Important:</b> These points represent semantic embeddings generated using
            Google Vertex AI’s <code>text-embedding-005</code> model.<br>
            Labels come directly from Google Cloud Vision and are not hand-curated.<br>
            Deterministic t-SNE settings ensure reproducible layouts on every run.<br>
            Words with related meaning that also appear near one another in this 3D space are marked with colored connecting lines.<br>
        </div>
    """

    # =======================================================
    # FINAL HTML OUTPUT
    # =======================================================

    html_out = f"""
<html>
<head>
<meta charset="UTF-8">
<title>{aesthetic} 3D t-SNE Embedding</title>

<style>
    body {{
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        flex-direction: column;
        background-color: #111;
        color: white;
        font-family: Arial, sans-serif;
    }}
    .plot-container {{
        width: 90vw;
        height: 75vh;
        margin-top: 5px;
    }}
</style>

</head>

<body>

    <div class="plot-container">
        {fig.to_html(include_plotlyjs='cdn', full_html=False)}
    </div>

    {disclaimer}

</body>
</html>
"""

    output_path = os.path.join(PROJECT_ROOT, "dashboard", output_filename)

    with open(output_path, "w") as f:
        f.write(html_out)

    print(f"✓ Saved HTML plot →", output_path)

# ============================================================
# MAIN LOOP
# ============================================================

if __name__ == "__main__":
    print("=== Building ALL FA embedding plots ===")

    for aesthetic, html_file in AESTHETICS.items():
        generate_plot(aesthetic, html_file)

    print("\n✔ All t-SNE embedding plots generated!")

