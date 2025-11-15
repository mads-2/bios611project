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
# AESTHETICS CONFIG
# ============================================================

AESTHETICS = {
    "FA_DORFic":       "D_embedding.html",
    "FA_classic":      "FA_embedding.html",
    "FA_Frutiger_Metro": "FM_embedding.html",
    "FA_Frutiger_Eco": "FE_embedding.html",
    "FA_Technozen":    "T_embedding.html",
    "FA_Dark_Aero":    "DA_embedding.html",
}

# ============================================================
# t-SNE FUNCTION
# ============================================================

def run_tsne(vectors):
    print("Running t-SNE…")
    tsne = TSNE(
        n_components=3,
        perplexity=20,
        learning_rate=200,
        n_jobs=-1,
        verbose=1,
    )
    return tsne.fit_transform(vectors)


# ============================================================
# PLOT GENERATION FUNCTION
# ============================================================

def generate_plot(aesthetic, output_filename):
    print(f"\n============================")
    print(f"Processing {aesthetic}")
    print(f"============================")

    vector_file = os.path.join(PROJECT_ROOT, "images", aesthetic, "vectors_object_instances.txt")

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
            line = line.strip()
            if not line or ":" not in line:
                continue
            try:
                name, score, inst, vec_str = line.split(":", 3)
                labels.append(name)
                scores.append(float(score))
                instances.append(int(inst))
                vectors.append(ast.literal_eval(vec_str))
            except:
                print("Skipping malformed:", line)
                continue

    vectors = np.array(vectors)
    print(f"✓ Loaded {len(vectors)} vectors (dim {vectors.shape[1]})")

    # Run t-SNE
    coords = run_tsne(vectors)
    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]

    # Point sizes
    sizes = [(inst * 2) + 6 for inst in instances]

    # Build Plotly figure
    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="markers",
        marker=dict(
            size=sizes,
            color=instances,
            colorscale="Viridis",
            opacity=0.9
        ),
        text=labels,
        hovertemplate="<b>%{text}</b><br>Instances=%{marker.size}<extra></extra>",
    ))

    fig.update_layout(
        title=f"3D t-SNE — {aesthetic} Object Embeddings",
        scene=dict(
            xaxis_title="t-SNE 1",
            yaxis_title="t-SNE 2",
            zaxis_title="t-SNE 3",
            bgcolor="#111"
        ),
        paper_bgcolor="#111",
        plot_bgcolor="#111",
        font=dict(color="white"),
        showlegend=False,
        margin=dict(l=0, r=0, t=60, b=0),
    )

    # Centered HTML wrapper
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
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #111;
    }}
    .plot-container {{
        width: 80vw;
        height: 80vh;
    }}
</style>
</head>
<body>
    <div class="plot-container">
        {fig.to_html(include_plotlyjs='cdn', full_html=False)}
    </div>
</body>
</html>
"""

    output_path = os.path.join(PROJECT_ROOT, "dashboard", output_filename)

    with open(output_path, "w") as f:
        f.write(html_out)

    print(f"✓ Saved HTML plot → {output_path}")


# ============================================================
# MAIN LOOP — build ALL aesthetic plots
# ============================================================

if __name__ == "__main__":
    print("=== Building ALL FA embedding plots ===")

    for aesthetic, html_file in AESTHETICS.items():
        generate_plot(aesthetic, html_file)

    print("\n✔ All t-SNE embedding plots generated!")

