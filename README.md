# Frutiger Aero — Analysis + Dashboard (bios611project)

## For Creatives (People Using the Dashboard for Inspiration)

This project provides an interactive exploration of the Frutiger Aero aesthetic through 3D color maps, semantic embeddings, and a visual dashboard. No technical background is required.

Repository URL:  
https://github.com/mads-2/bios611project

---

### 1. Clone the Repository and Enter this Local Directory

---

### 2. Build the Dashboard Environment

```bash
docker build . -t aero
```

---

### 3. Run the Environment (RStudio Only)

```bash
docker run --rm     -e PASSWORD=mysecret     -p 8181:8181     -p 8787:8787     -v "$(pwd)":/home/rstudio/project     aero
```

- RStudio: http://localhost:8787  
  username: `rstudio`, password: `mysecret`

---

### 4. Build Everything (Required Before Dashboard Works)

Inside the RStudio terminal:

```bash
make all
```

This will:

- Regenerate all color files  
- Aggregate object metadata  
- Build 3D color plots  
- Build t-SNE embeddings  
- Build random embedding plots  
- And **finally run**:

```
./dashboard/run_dashboard.sh
```

### **The dashboard cannot be viewed until `make all` finishes.**

After the pipeline completes, open:

```
http://localhost:8181/dashboard/prototype/prototype.html
```

---

# For Developers  
## (Adding New Data, Using Vision/Vertex AI Tools, Extending the Pipeline)

# IDEAS FOR IMPROVEMENT OF THIS PROJECT:

- Create classifier that can detect which subtype of Frutiger Aero and image most closely aligns with
- Create a binary classifier that can tell you if an image is Frutiger Aero (including subtypes) or not
---
This section provides detailed instructions for adding images, generating objects, embeddings, and understanding the project workflow.

---

## Required Directory Structure

```
images/
    FA_<style>/
        001.png
        001colors.txt
        001object.txt
        object_instances.txt
        vectors_object_instances.txt
```

---

## Image Naming Rules

Each image must follow:

```
<NUMBER>.png
```

Example:

```
001.png
002.png
003.png
```

Generated files must use matching numbers:

```
001colors.txt
001object.txt
```

If the numbering is not correct, the Makefile will stop with an error.

---

## How Colors Are Generated

Color files are **fully automatic**.

Running:

```bash
make colors
```

will:

- Delete old color files  
- Extract dominant colors for every image (`<NUMBER>colors.txt`)  
- Generate combined `colors.txt` summary  

No manual editing is needed.

---

## How Objects Are Generated (Google Vision API)

Each PNG requires a corresponding:

```
<NUMBER>object.txt
```

These files are created using your existing script:

```
objects/FA_google_vision.py
```

This uses:

- Your environment variable: `GOOGLE_VISION_API_KEY`  
- Google Cloud Vision API: LABEL_DETECTION  

Outputs look like:

```
Aquarium    0.912
Fish        0.801
...
```

Feel free to also create these <NUMBER>object.txt files manually as well

(follow the formatting of the existing <NUMBER>object.txt files)

---

## Combining Object Files

Run:

```bash
Rscript objects/aggregate_FA_objects.R
```

This creates:

```
object_instances.txt
```

This aggregated file is required before embeddings can be generated.

---

## Generating Embeddings (Google Vertex AI)

Two scripts already exist:

```
objects/test_DORFic_vectors.py
objects/all_non_DORFic_vectors.py
```

These scripts:

- Read `object_instances.txt`
- Call Vertex AI **text-embedding-005**
- Produce:

```
vectors_object_instances.txt
```

Authentication uses:

```
gcloud auth print-access-token
```

---

## Adding New Images (Full Workflow)

1. Place new images into:

```
images/FA_<style>/
```

Number them:

```
<NUMBER>.png
```

2. Run object detection:

```bash
python objects/FA_google_vision.py
```

3. Aggregate objects:

```bash
Rscript objects/aggregate_FA_objects.R
```

4. Generate embeddings:

```bash
python objects/all_non_DORFic_vectors.py
```

(or the DORFic version if applicable)

5. Build dashboard + plots:

```bash
make all
```

---

## Makefile Targets

```
make all               # Full pipeline + dashboard
make dashboard         # Same as all
make colors            # Rebuild all color files
make objects           # Aggregate object metadata
make embeddings        # Build t-SNE embeddings
make random-embeddings # Random embedding plot
make colors-plot       # 3D color plot
make clean             # Remove generated files
make build             # Build Docker image
make run               # Run environment
make stop              # Stop running containers
```

---

This README provides a complete guide for both creatives and developers who want to explore or extend the bios611project.
