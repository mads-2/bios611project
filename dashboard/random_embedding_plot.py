import os
import numpy as np
import plotly.graph_objects as go
from sklearn.manifold import TSNE
import ast

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# OUTPUT HTML FILENAMES
# ============================================================

AESTHETICS = {
    "FA_DORFic":          "r_D_embedding.html",
    "FA_classic":         "r_FA_embedding.html",
    "FA_Frutiger_Metro":  "r_FM_embedding.html",
    "FA_Frutiger_Eco":    "r_FE_embedding.html",
    "FA_Technozen":       "r_T_embedding.html",
    "FA_Dark_Aero":       "r_DA_embedding.html",
}

# ============================================================
# OUTLIERS (REMOVED BEFORE TSNE)
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
    "FA_Technozen": ["Shelving", "Corporate Headquarters"],
}

# ============================================================
# NON-DETERMINISTIC t-SNE
# ============================================================

def run_tsne(vectors):
    print("Running NON-deterministic t-SNE…")

    tsne = TSNE(
        n_components=3,
        perplexity=30,
        learning_rate=300,
        max_iter=1000,
        init="pca",
        method="exact",
        verbose=1,
        random_state=None,   # 🔥 RANDOM every run
    )

    return tsne.fit_transform(vectors)

# ============================================================
# PLOT GENERATION
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
    instances = []
    vectors = []

    # -------------------------------------------------------
    # LOAD VECTORS
    # -------------------------------------------------------
    with open(vector_file, "r") as f:
        for line in f:
            if ":" not in line:
                continue

            try:
                name, score, inst, vec_str = line.strip().split(":", 3)
                labels.append(name)
                instances.append(int(inst))
                vectors.append(ast.literal_eval(vec_str))
            except:
                continue

    # -------------------------------------------------------
    # REMOVE OUTLIERS BEFORE TSNE
    # -------------------------------------------------------
    drop = set(OUTLIERS.get(aesthetic, []))

    filtered_labels = []
    filtered_instances = []
    filtered_vectors = []

    for lbl, inst, vec in zip(labels, instances, vectors):
        if lbl not in drop:
            filtered_labels.append(lbl)
            filtered_instances.append(inst)
            filtered_vectors.append(vec)

    vectors = np.array(filtered_vectors)
    instances = filtered_instances

    print(f"✓ Using {len(vectors)} vectors after outlier removal")

    # -------------------------------------------------------
    # NON-DETERMINISTIC TSNE
    # -------------------------------------------------------
    coords = run_tsne(vectors)

    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]

    sizes = [(inst * 2) + 6 for inst in instances]

    # -------------------------------------------------------
    # SCATTER PLOT (with original hover style)
    # -------------------------------------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers",
        marker=dict(
            size=sizes,
            color=instances,
            colorscale="Viridis",    # 🔥 ORIGINAL COLORSCALE RESTORED
            opacity=0.9
        ),
        text=filtered_labels,
        hovertemplate="<b>%{text}</b><br>Instances=%{marker.size}<extra></extra>",
        name="Points"
    ))

    # -------------------------------------------------------
    # LAYOUT (same style as original)
    # -------------------------------------------------------
    fig.update_layout(
        title=f"Randomized 3D t-SNE — {aesthetic}",
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

    # -------------------------------------------------------
    # DISCLAIMER (same style)
    # -------------------------------------------------------
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
            This version uses <i>non-deterministic</i> t-SNE settings, so layouts vary every run.
        </div>
    """

    # -------------------------------------------------------
    # FULL HTML WRAPPER (same as original)
    # -------------------------------------------------------
    html_out = f"""
<html>
<head>
<meta charset="UTF-8">
<title>{aesthetic} Random t-SNE Embedding</title>

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

    # -------------------------------------------------------
    # SAVE
    # -------------------------------------------------------
    output_path = os.path.join(PROJECT_ROOT, "dashboard", output_filename)
    with open(output_path, "w") as f:
        f.write(html_out)

    print(f"✓ Saved → {output_path}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=== Building RANDOM FA embedding plots ===")

    for aesthetic, html_file in AESTHETICS.items():
        generate_plot(aesthetic, html_file)

    print("\n✔ All randomized t-SNE plots generated!")

