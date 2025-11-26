# ============================================================
# Frutiger Aero — Analysis + Dashboard Environment
# ============================================================

IMAGE = aero
RSTUDIO_PORT = 8787
DASHBOARD_PORT = 8181
PASSWORD = mysecret
R = Rscript

# ============================================================
# FILE DISCOVERY
# ============================================================

PNG_FILES := $(wildcard images/FA_*/*.png)

ifeq ($(PNG_FILES),)
  $(error No PNG files found in images/FA_*/)
endif

# PNG → <image>object.txt
OBJECT_TXT := $(PNG_FILES:.png=object.txt)

# Per-image extracted color files (e.g., 91color.txt)
NUMBERED_COLOR_TXT := $(wildcard images/FA_*/*color.txt)

# Per-folder aggregated colors
COLOR_TXT := $(wildcard images/FA_*/colors.txt)

# Per-folder object_instances.txt
OBJECT_INSTANCES := $(patsubst images/FA_%/,images/FA_%/object_instances.txt,$(dir $(OBJECT_TXT)))

# Any vectors file for embeddings
VECTOR_OBJECT_FILES := $(shell find images/FA_* -type f -name "vectors_object_instances.txt")

# Outputs
COLOR_PLOT := dashboard/color_plot_output.html
EMBED_PLOT := dashboard/embedding_plot_output.html
RANDOM_EMBED_PLOT := dashboard/random_embedding_plot_output.html


# ============================================================
# HIGH-LEVEL TARGETS
# ============================================================

.PHONY: all report dashboard build-dashboard build run stop clean help

all: build-dashboard
report: build-dashboard
dashboard: build-dashboard

build-dashboard: $(COLOR_PLOT) $(EMBED_PLOT) $(RANDOM_EMBED_PLOT)
	cd dashboard && ./run_dashboard.sh
	@echo "✔ Dashboard launched."


# ============================================================
# DOCKER
# ============================================================

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm \
		-e PASSWORD=$(PASSWORD) \
		-p $(DASHBOARD_PORT):$(DASHBOARD_PORT) \
		-p $(RSTUDIO_PORT):8787 \
		-v "$(PWD)":/home/rstudio/project \
		$(IMAGE)

stop:
	docker ps -q --filter ancestor=$(IMAGE) | xargs -r docker stop


# ============================================================
# REAL TARGET: COLORS
# ============================================================

FA_DIRS := $(wildcard images/FA_*)
COLOR_TXT := $(addsuffix /colors.txt,$(FA_DIRS))

$(COLOR_TXT): $(PNG_FILES) colors/extract_all_FA.R colors/aggregate_FA_colors.R
	@echo "Rebuilding all color data..."

	@find images/FA_* -type f -name "*color.txt" -delete
	@find images/FA_* -type f -name "colors.txt" -delete

	$(R) colors/extract_all_FA.R
	$(R) colors/aggregate_FA_colors.R

	@echo "✔ Color data regenerated."

colors: $(COLOR_TXT)

# ============================================================
# COLORS PLOT (REAL TARGET)
# ============================================================

$(COLOR_PLOT): dashboard/color_plot.py $(COLOR_TXT)
	@echo "Generating 3D color plot..."
	python3 dashboard/color_plot.py
	@echo "✔ Colors plot updated."

colors-plot: $(COLOR_PLOT)


# ============================================================
# OBJECTS PIPELINE (REAL TARGET)
# ============================================================

%.object.txt: %.png
	@echo "ERROR: Missing object file: $@"
	@echo "→ Run: python3 objects/FA_google_vision.py"
	@exit 1

images/FA_%/object_instances.txt: $(filter images/FA_%/%.object.txt,$(OBJECT_TXT)) objects/aggregate_FA_objects.R
	@echo "Aggregating object data for folder $* ..."
	$(R) objects/aggregate_FA_objects.R
	@echo "✔ Wrote aggregated object_instances.txt for $*"

objects: $(OBJECT_INSTANCES)
	@echo "✔ All object aggregation complete."


# ============================================================
# RANDOM EMBEDDINGS (REAL TARGET)
# ============================================================

$(RANDOM_EMBED_PLOT): dashboard/random_embedding_plot.py $(VECTOR_OBJECT_FILES)
	@echo "Generating random embeddings plot..."
	python3 dashboard/random_embedding_plot.py
	@echo "✔ Random embeddings plot generated."

random-embeddings: $(RANDOM_EMBED_PLOT)


# ============================================================
# EMBEDDINGS (REAL TARGET)
# ============================================================

$(EMBED_PLOT): dashboard/embedding_plot.py $(VECTOR_OBJECT_FILES)
	@echo "Generating embedding plot..."
	python3 dashboard/embedding_plot.py
	@echo "✔ Embedding plot generated."

embeddings: $(EMBED_PLOT)


# ============================================================
# CLEAN (SAFE)
# ============================================================

clean:
	@echo "Running clean..."

	@if command -v docker >/dev/null 2>&1; then \
		echo "Pruning unused Docker images..."; \
		docker image prune -f; \
	else \
		echo "Docker not available."; \
	fi

	@echo "Removing generated COLOR files..."
	@find images/FA_* -type f -name "*color.txt" -delete
	@find images/FA_* -type f -name "colors.txt" -delete

	@echo "Preserving object_instances.txt and vectors_object_instances.txt."

	@echo "Removing dashboard HTML outputs..."
	@rm -f dashboard/color_plot_output.html
	@rm -f dashboard/random_embedding_plot_output.html
	@rm -f dashboard/embedding_plot_output.html
	@find dashboard -type f -name "*_embedding.html" -delete
	@find dashboard -type f -name "r_*_embedding.html" -delete

	@echo "✔ Clean complete."


# ============================================================
# HELP
# ============================================================

help:
	@echo ""
	@echo "Available targets:"
	@echo "  all                Full pipeline + dashboard"
	@echo "  dashboard          Launch dashboard"
	@echo "  colors             Generate color data"
	@echo "  colors-plot        Generate 3D color plot"
	@echo "  objects            Aggregate object labels"
	@echo "  embeddings         Generate embedding plot"
	@echo "  random-embeddings  Generate random embedding plot"
	@echo "  clean              Remove pipeline-generated artifacts"
	@echo "  build              Build Docker environment"
	@echo "  run                Start RStudio + dashboard"
	@echo "  stop               Stop running containers"
	@echo ""

