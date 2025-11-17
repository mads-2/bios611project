import os
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
# UPDATED CLUSTERS (replacing all previous connections)
# ============================================================

CLUSTERS = {

    "FA_classic": [   # FA
        ["Chess", "Chessboard"],
        ["Meadow", "Grasses"],
        ["Underwater", "Ocellaris_Clownfish", "Aquarium", "Sea", "Fish", "Pomacentridae"],
    ],

    "FA_DORFic": [    # D
        ["Apples", "Citrus"],
        ["Exhibition", "Modern_Art"],
        ["Produce", "Food"],
        ["Operating_System", "Software", "Multimedia_Software"],
    ],

    "FA_Frutiger_Eco": [   # FE
        ["Tropics", "Water", "Ocean"],
        ["Map", "Atlas"],
        ["Garden", "Green"],
        ["Cloud", "Cumulus"],
        ["Technology", "Machine"],
    ],

    "FA_Dark_Aero": [  # DA
        ["Moon", "Moonlight", "Full_Moon"],
        ["Feature_Phone", "Communication_Device"],
        ["Computer", "Technology", "Operating_System"],
        ["Fluid", "Liquid"],
    ],

    "FA_Frutiger_Metro": [  # FM
        ["Chordophone", "Musical_Ensemble", "Disco"],
        ["Graphic_Design", "Packaging_And_Labeling"],
        ["Music", "Jazz"],
    ],

    "FA_Technozen": [   # T
        ["Soft_Tennis", "Sports_Venue", "Tennis_Court", "Racketlon"],
        ["Evergreen", "Bamboo"],
        ["Nintendo_3ds", "Wii", "Portable_Electronic_Game"],
        ["Rapid_Transport", "Mode_Of_Transport", "Train"],
    ],
}

# Distinct, readable line colors
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

# ============================================================
# t-SNE FUNCTION (stabilized)
# ============================================================

def run_tsne(vectors):
    print("Running t-SNE…")

    tsne = TSNE(
        n_components=3,
        perplexity=20,
        learning_rate=200,
        n_jobs=-1,
        verbose=1,
        random_state=242,   # <<< FIXED STABLE LAYOUT
        init="random",      # <<< reproducible but true t-SNE
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

    print(f"→ Loading vectors: {vector_file}")

    labels = []
    scores = []
    instances = []
    vectors = []

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
                print("Skipping malformed:", line)
                continue

    vectors = np.array(vectors)
    print(f"✓ Loaded {len(vectors)} vectors (dim {vectors.shape[1]})")

    # Run stable t-SNE
    coords = run_tsne(vectors)
    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]

    # Marker sizes
    sizes = [(inst * 2) + 6 for inst in instances]

    # Base scatter plot
    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers",
        marker=dict(
            size=sizes,
            color=instances,
            colorscale="Viridis",
            opacity=0.9
        ),
        text=labels,
        hovertemplate="<b>%{text}</b><br>Instances=%{marker.size}<extra></extra>",
        name="Points"
    ))

    # =======================================================
    # ADD COLORED CONNECTION LINES FOR CLUSTERS
    # =======================================================

    if aesthetic in CLUSTERS:
        label_to_idx = {label: i for i, label in enumerate(labels)}
        color_i = 0

        for group in CLUSTERS[aesthetic]:
            group_color = LINE_COLORS[color_i % len(LINE_COLORS)]
            color_i += 1

            # Only include labels actually present in this dataset
            indices = [label_to_idx[l] for l in group if l in label_to_idx]

            # Fully connected edges for all pairs
            for i, j in combinations(indices, 2):
                fig.add_trace(go.Scatter3d(
                    x=[x[i], x[j]],
                    y=[y[i], y[j]],
                    z=[z[i], z[j]],
                    mode="lines",
                    line=dict(color=group_color, width=4),
                    hovertemplate=f"<b>{labels[i]} ↔ {labels[j]}</b><extra></extra>",
                    showlegend=False
                ))

    # Layout
    fig.update_layout(
        title=f"3D t-SNE — {aesthetic} Object Embeddings",
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
    # DISCLAIMER — BOTTOM OF PAGE
    # =======================================================

    disclaimer = """
        <div style='
            color: #ccc;
            font-size: 16px;
            margin-top: 25px;
            margin-bottom: 10px;
            width: 80%;
            text-align: center;
            line-height: 1.4;
        '>
            <b>Important:</b> These points represent semantic embeddings generated using
            Google Vertex AI’s <code>text-embedding-005</code> model (768-dimensional vectors).
            Labels identified by Google Cloud Vision were embedded using this model and then
            reduced to 3D using t-SNE. A fixed random seed (242) is used to ensure stable,
            reproducible spatial layouts each time the visualization is generated.
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

    print(f"✓ Saved HTML plot → {output_path}")


# ============================================================
# MAIN LOOP
# ============================================================

if __name__ == "__main__":
    print("=== Building ALL FA embedding plots ===")

    for aesthetic, html_file in AESTHETICS.items():
        generate_plot(aesthetic, html_file)

    print("\n✔ All t-SNE embedding plots generated!")

