# ============================================================
# Frutiger Aero — Text, Image, and Trend Analysis Environment
# ============================================================

FROM rocker/rstudio:latest

# ------------------------------------------------------------
# System dependencies for R packages (text + image analysis)
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libblas-dev \
    liblapack-dev \
    libgmp-dev \
    libglpk-dev \
    # Rendering and font dependencies for tidyverse/colorfindr
    libfontconfig1-dev \
    libfreetype6-dev \
    librsvg2-dev \
    pkg-config \
    # Python for Ultralytics
    python3 \
    python3-pip \
    # Optional but helpful tools
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Python dependencies for 3D color plotting
# ------------------------------------------------------------
RUN pip3 install --break-system-packages numpy scipy plotly scikit-learn

# ------------------------------------------------------------
# R packages for text mining, visualization, and trends
# ------------------------------------------------------------
RUN set -eux; \
    R -e "install.packages(c( \
      'tidytext', 'udpipe', 'textstem', 'colorfindr', \
      'patchwork', 'ggplot2', 'readr', 'dplyr', 'stringr', 'lubridate', \
      'httr', 'jsonlite' \
    ), repos='https://cloud.r-project.org/')"

# ------------------------------------------------------------
# Install tidyverse wrapper separately to ensure correct registration
# ------------------------------------------------------------
RUN set -eux; \
    R -e "install.packages('tidyverse', repos='https://cloud.r-project.org')"


# ------------------------------------------------------------
# Default working directory and RStudio startup path
# ------------------------------------------------------------
ENV HOME=/home/rstudio
WORKDIR /home/rstudio/project

RUN echo '\nif (interactive()) { p <- "/home/rstudio/project"; if (dir.exists(p)) setwd(p) }\n' >> /home/rstudio/.Rprofile \
 && chown rstudio:rstudio /home/rstudio/.Rprofile

RUN echo 'cd /home/rstudio/project' >> /home/rstudio/.bashrc \
 && chown rstudio:rstudio /home/rstudio/.bashrc

