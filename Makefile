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

# Per-folder object_instances.txt
OBJECT_INSTANCES := $(patsubst images/FA_%/,images/FA_%/object_instances.txt,$(dir $(OBJECT_TXT)))

# Vectors used for embeddings
VECTOR_OBJECT_FILES := $(shell find images/FA_* -type f -name "vectors_object_instances.txt")

# Color plot output
COLOR_PLOT := dashboard/color_plot_output.html

# Deterministic embedding outputs
EMBED_PLOTS := \
	dashboard/D_embedding.html \
	dashboard/FA_embedding.html \
	dashboard/FM_embedding.html \
	dashboard/FE_embedding.html \
	dashboard/T_embedding.html \
	dashboard/DA_embedding.html

# Random embedding outputs
RANDOM_EMBED_PLOTS := \
	dashboard/r_D_embedding.html \
	dashboard/r_FA_embedding.html \
	dashboard/r_FM_embedding.html \
	dashboard/r_FE_embedding.html \
	dashboard/r_T_embedding.html \
	dashboard/r_DA_embedding.html


# ============================================================
# HIGH-LEVEL TARGETS
# ============================================================

.PHONY: all report dashboard build run stop clean help

all: build-dashboard
report: build-dashboard
dashboard: build-dashboard

# Must NOT be PHONY → depends on REAL outputs
build-dashboard: $(COLOR_PLOT) $(EMBED_PLOTS) $(RANDOM_EMBED_PLOTS)
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
# EMBEDDINGS (DETERMINISTIC)
# ============================================================

$(EMBED_PLOTS): dashboard/embedding_plot.py $(VECTOR_OBJECT_FILES)
	@echo "Generating deterministic embedding plots..."
	python3 dashboard/embedding_plot.py
	@echo "✔ All deterministic embedding plots generated."

embeddings: $(EMBED_PLOTS)


# ============================================================
# RANDOM EMBEDDINGS
# ============================================================

$(RANDOM_EMBED_PLOTS): dashboard/random_embedding_plot.py $(VECTOR_OBJECT_FILES)
	@echo "Generating random embedding plots..."
	python3 dashboard/random_embedding_plot.py
	@echo "✔ All randomized embedding plots generated."

random-embeddings: $(RANDOM_EMBED_PLOTS)


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
	@rm -f dashboard/*.html
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
	@echo "  embeddings         Generate deterministic embedding plots"
	@echo "  random-embeddings  Generate randomized embedding plots"
	@echo "  clean              Remove pipeline-generated artifacts"
	@echo "  build              Build Docker environment"
	@echo "  run                Start RStudio + dashboard"
	@echo "  stop               Stop running containers"
	@echo ""

