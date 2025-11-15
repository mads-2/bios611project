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

# All FA PNG files
PNG_FILES := $(wildcard images/FA_*/*.png)

# Correct rule: foo.png → fooobject.txt
OBJECT_TXT := $(PNG_FILES:.png=object.txt)

# Base color files
COLOR_TXT := $(wildcard images/FA_*/colors.txt)

# Numbered color files
NUMBERED_COLOR_TXT := $(wildcard images/FA_*/*colors.txt)

# Outputs
COLOR_PLOT := dashboard/color_plot_output.html
EMBED_PLOT := dashboard/embedding_plot_output.html

# Any file named vectors_object_instances.txt
VECTOR_OBJECT_FILES := $(shell find . -type f -name "vectors_object_instances.txt")


# ============================================================
# HIGH-LEVEL TARGETS
# ============================================================

.PHONY: all
all: colors objects colors-plot embeddings dashboard
	@echo "✔ Full project build complete (including dashboard)."


.PHONY: dashboard
dashboard: $(EMBED_PLOT)
	cd dashboard && ./run_dashboard.sh


# report = dashboard
.PHONY: report
report: dashboard
	@echo "✔ Dashboard launched (via report)."


# ============================================================
# DOCKER
# ============================================================

.PHONY: build
build:
	docker build -t $(IMAGE) .

.PHONY: run
run:
	docker run --rm \
		-e PASSWORD=$(PASSWORD) \
		-p $(DASHBOARD_PORT):$(DASHBOARD_PORT) \
		-p $(RSTUDIO_PORT):8787 \
		-v "$(PWD)":/home/rstudio/project \
		$(IMAGE)

.PHONY: stop
stop:
	docker ps -q --filter ancestor=$(IMAGE) | xargs -r docker stop


# ============================================================
# COLOR PIPELINE
# ============================================================

.PHONY: colors
colors:
	@echo "Rebuilding all color data..."
	@find images/FA_* -type f -name "colors.txt" -delete
	@find images/FA_* -type f -regex ".*[0-9]+colors\.txt" -delete
	$(R) colors/extract_all_FA.R
	$(R) colors/aggregate_FA_colors.R
	@echo "✔ Color data regenerated."


.PHONY: colors-plot
colors-plot: colors $(COLOR_PLOT)
	@echo "✔ Colors 3D plot updated."


$(COLOR_PLOT): dashboard/color_plot.py $(COLOR_TXT)
	@echo "Generating 3D color plot..."
	python3 dashboard/color_plot.py


# ============================================================
# OBJECT PIPELINE
# ============================================================

$(OBJECT_TXT):
	@echo "❌ Missing object file: $@  (expected from $(@:object.txt=.png))"
	@echo "Every .png must have a matching object.txt"
	@exit 1


.PHONY: objects
objects: $(OBJECT_TXT)
	@echo "Aggregating Vision API object data..."
	$(R) objects/aggregate_FA_objects.R
	@echo "✔ All object data aggregated."


# ============================================================
# VECTOR + EMBEDDING PIPELINE
# ============================================================

# Embedding plot must depend on all vectors_object_instances.txt files
$(EMBED_PLOT): dashboard/embedding_plot.py $(VECTOR_OBJECT_FILES)
	@echo "Generating embedding plot..."
	python3 dashboard/embedding_plot.py


.PHONY: embeddings
embeddings: $(EMBED_PLOT)
	@echo "✔ Embedding plot generated."


# ============================================================
# CLEAN
# ============================================================

.PHONY: clean
clean:
	@echo "Running clean..."
	@if command -v docker >/dev/null 2>&1; then \
		echo "Pruning unused Docker images..."; \
		docker image prune -f; \
	else \
		echo "Docker not available."; \
	fi

	@echo "Removing color files..."
	@find images/FA_* -type f -name "colors.txt" -delete
	@find images/FA_* -type f -regex ".*[0-9]+colors\.txt" -delete

	@echo "Removing color + embedding HTML..."
	@rm -f dashboard/color_plot_output.html
	@find dashboard -type f -name "*_embedding.html" -delete

	@echo "✔ Clean complete."


# ============================================================
# HELP
# ============================================================

.PHONY: help
help:
	@echo ""
	@echo "Available targets:"
	@echo "  all                Full pipeline + dashboard"
	@echo "  dashboard          Launch dashboard"
	@echo "  report             Same as 'dashboard'"
	@echo "  colors             Rebuild color data"
	@echo "  colors-plot        Generate 3D Plotly colors figure"
	@echo "  objects            Aggregate object.txt data"
	@echo "  embeddings         Generate embeddings plot"
	@echo "  clean              Remove intermediates"
	@echo "  build              Build Docker environment"
	@echo "  run                Start RStudio + dashboard"
	@echo "  stop               Stop running containers"
	@echo ""

