<div align="center">

<br/>

```
 █████╗ ███████╗██╗
██╔══██╗██╔════╝██║
███████║███████╗██║
██╔══██║╚════██║██║
██║  ██║███████║██║
╚═╝  ╚═╝╚══════╝╚═╝
```

# Atlas de Suscetibilidade a Inundações
### **SIGWeb — Geographic Information System for Flood Susceptibility Analysis**

<br/>

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-0.16%2B-77B829?style=for-the-badge&logo=leaflet&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Stable%20v3.0-success?style=for-the-badge)
![Brazil](https://img.shields.io/badge/Made%20in-Brazil-009C3B?style=for-the-badge)

<br/>

> *"Translating terrain morphology into actionable flood risk intelligence."*

<br/>

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Objectives](#-objectives)
- [How It Works — The TWI Model](#-how-it-works--the-twi-model)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Data Sourcing & Provenance](#-data-sourcing--provenance)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Legal & Licensing](#-legal--licensing)
- [Academic Credits & Acknowledgements](#-academic-credits--acknowledgements)

---

##  Overview

**ASI** (Atlas de Suscetibilidade a Inundações) is a **geospatial data engineering pipeline** wrapped in an interactive web-based Geographic Information System (SIGWeb). It was developed to model, classify and visualize flood susceptibility across the municipality of **Cabo de Santo Agostinho, Pernambuco, Brazil**, using physical-mathematical descriptors of terrain morphology.

At its core, the system translates raw topographic data — Digital Elevation Models (DEMs), slope measurements, and upstream contributing areas — into a structured susceptibility index, rendered through a fully interactive cartographic interface accessible directly from the browser.

ASI is an **educational and scientific instrument**. It was not designed as a commercial product, nor as a real-time emergency system. Its purpose is to support academic research, territorial planning studies, and the development of spatial literacy among students and researchers in geography, environmental engineering, and data science.

The platform operates on a **modular Python architecture** centered around the Streamlit framework, with spatial rendering powered by Folium/Leaflet.js and geospatial data processing handled by PyProj and Pandas. The entire ETL pipeline — from raw coordinate reprojection to risk classification and dashboard rendering — runs automatically on first launch.

---

##  Objectives

The ASI project was conceived around five primary scientific and technical objectives:

**1. Spatial Modeling of Flood Susceptibility**
Apply the Topographic Wetness Index (TWI) as the primary physical descriptor to quantify the natural predisposition of terrain to hydrological accumulation, identifying areas of critical saturability within the study area.

**2. Geospatial ETL Pipeline Design**
Build a robust, reproducible data engineering pipeline capable of ingesting raw geospatial attribute tables, reprojecting coordinate systems from UTM SIRGAS 2000 (EPSG:31985) to WGS84 (EPSG:4326), applying conditional risk classification, and loading the processed dataset into an interactive visualization engine.

**3. Accessible Interactive Cartographic Interface**
Deliver a fully browser-based GIS application that allows users to explore susceptibility patterns without requiring desktop GIS software (ArcGIS, QGIS, etc.), democratizing access to spatial analysis tools.

**4. Multi-layered Spatial Diagnostics**
Enable point-level diagnostics, buffer-based proximity analysis (500m radius), and neighborhood risk clustering detection — providing granular hydrological intelligence beyond simple map visualization.

**5. Academic Contribution to Territorial Planning**
Provide an empirical, reproducible basis for discussions on urban flood risk, land use planning, and infrastructure policy in coastal and semi-urban municipalities of Pernambuco.

---

##  How It Works — The TWI Model

The susceptibility model is grounded in the **Topographic Wetness Index (TWI)**, a geomorphometric descriptor developed from the seminal work of Beven & Kirkby (1979) in the TOPMODEL framework.

### The Core Equation

$$TWI = \ln\left(\frac{a}{\tan \beta}\right)$$

| Variable | Description |
|----------|-------------|
| **a** | Specific contributing area (m²/m) — the upslope area draining to a given point, divided by contour width. Represents the volume of water flux arriving at a location. |
| **tan β** | Local slope tangent — the gradient of the terrain surface. Represents the gravitational drainage potential. |

### Physical Interpretation

The relationship between these variables is inversely proportional to slope: **flat areas with large upstream catchments produce high TWI values**, indicating zones of natural water accumulation. Steep terrain with small contributing areas produces low TWI values, indicating zones of rapid drainage and low retention.

### Risk Classification Thresholds

| Class Code | TWI Range | Label | Hydrological Meaning |
|------------|-----------|-------|----------------------|
| `MUITO_BAIXO` | TWI < 4.0 | Very Low (Divide) | Ridgelines or high-gradient slopes. Flow accelerates without retention. |
| `BAIXO` | 4.0 – 8.0 | Low (Drainage) | Dissipation zones. Runoff without significant retention under normal conditions. |
| `MODERADO` | 8.0 – 12.0 | Moderate (Attention) | Hydrological transition. Ponding and localized flooding may occur during intense precipitation. |
| `ALTO` | 12.0 – 16.0 | High (Flooding Potential) | Strong hydraulic accumulation. Infiltration capacity is rapidly exceeded. |
| `CRITICO` | TWI ≥ 16.0 | Critical (Immediate Saturation) | Zones of extreme flow convergence. Near-certain saturation during any pluviometric event. |

---

##  System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     ASI SIGWeb                          │
│              Geospatial Pipeline Architecture           │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────────────────┐
│   DATA LAYER    │────▶│         ETL PIPELINE          │
│                 │     │  src/processing/data_loader   │
│  data/curated/  │     │                               │
│  attribute_     │     │  1. CSV Ingestion (UTF-8)     │
│  tables/        │     │  2. UTM→WGS84 Reprojection    │
│  data_table.txt │     │     (PyProj / EPSG:31985→4326)│
│                 │     │  3. MapBiomas Land Use Decode │
│  data/raw/      │     │  4. IBGE Situacao Decode      │
│  arcmap_exports/│     │  5. TWI Risk Classification   │
│  *.json / *.txt │     │     (pd.cut with thresholds)  │
└─────────────────┘     └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │       APPLICATION LAYER      │
                        │         src/sigweb/          │
                        │                             │
                        │  config.py    → Constants    │
                        │  components.py → UI Widgets  │
                        │  map_engine.py → Folium Maps │
                        │  report_gen.py → Diagnostics │
                        │  analytics.py  → Statistics  │
                        │  documentation.py → Docs     │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │      PRESENTATION LAYER      │
                        │          app.py              │
                        │                             │
                        │  Streamlit + Folium/Leaflet  │
                        │  Plotly Charts               │
                        │  Interactive Map (Canvas)    │
                        │  Point Diagnostics           │
                        │  Buffer Analysis (500m)      │
                        │  Statistical Dashboard       │
                        └─────────────────────────────┘
```

---

##  Features

###  Interactive Cartographic Rendering
- Three selectable basemap styles: **Standard (OpenStreetMap)**, **High Contrast Light (CartoDB Positron)** and **Dark Mode (CartoDB Dark Matter)**
- **Municipal boundary overlay** — all 185 PE municipalities (`pe_municipios_2024.json`) as transparent delimiters with hover tooltips
- **TWI point sample layer** with risk-coded color markers; **MarkerCluster mode** for performance optimization
- **Kernel Density Heatmap** for high-risk cluster visualization (Critical + High classes)
- **Hydrographic network layer** — rivers and streams from APAC/ANA (`Hidrografia_Pernambuco.geojson`) ← *v3.0*
- **Historical flood events layer** — SEPDEC occurrences by severity (LEVE / MODERADA / GRAVE) with popup and year range filter ← *v3.0*
- Native map scale bar and fullscreen control

###  Spatial Filters
- **Spatial unit filtering** (Recorte Espacial) by neighborhood/administrative boundary
- **TWI minimum threshold slider** (Limiar TWI Mínimo) for dynamic severity filtering
- **Year range filter** for historical flood events (Janela Temporal) ← *v3.0*
- Active filter display with sample count feedback

###  Point-Level Diagnostics
- Click-to-inspect vector sample; diagnostic card header **dynamically colored** by the TWI class of the selected point ← *v3.0*
- Displays: TWI value, slope (°), altitude (m), land use (MapBiomas), IBGE urban classification, technical recommendation
- Optional **geomorphometric notation** (academic mode)
- **Nearby historical flood events** listed within buffer proximity ← *v3.0*

###  Buffer Proximity Analysis (500m Radius)
- Geodesic distance calculation (via GeoPy) for all neighboring points
- Critical/High risk point count within radius; dynamic alert escalation
- Donut chart of risk composition within buffer

###  Statistical Dashboards ← *v3.0*
- **Análise Geoestatística** — proportional composition, TWI frequency distribution, spatial dispersion scatter, land use × susceptibility matrix
- **Série Histórica de Precipitação (INMET/APAC)** — time series by meteorological station with max, mean, median
- **Painel Defesa Civil PE 2024–2026** — human damages (deaths, displaced, homeless, injured) and material damages across 78 municipalities (SEPDEC/`defesacivil_pe_consolidado.csv`)
- **Ranking IRA por Bairro** — Aggregated Risk Index with weighted TWI class scores (CRÍTICO=5 → MUITO_BAIXO=1) per neighborhood

###  Data Export
- Export the currently filtered TWI dataset as a semicolon-separated UTF-8 CSV (Export · CSV Filtrado)

###  Professional GIS UI/UX ← *v3.0*
- Full CSS redesign: **IBM Plex Mono** (labels, values, tabs) + **IBM Plex Sans** (body)
- Dark theme: `#080C10` background, steel blue `#2E86C1`, cyan `#00B4D8`
- Nested submenus within each control panel (`// CARTOGRAFIA`, `// FILTRAGEM VETORIAL`, `// MÓDULOS ANALÍTICOS`)
- Hover micro-interactions, smooth transitions, pulse animation on critical alerts

###  Technical Documentation Module (DTM)
- In-app **TWI mathematical formulation** with LaTeX rendering
- **ETL pipeline documentation** (Extract → Reproject → Classify → Load)
- **Official data sources** reference panel
- **Methodological disclaimer** and limitation notice
- Embeddable **Markdown academic documentation** (`DTM_doc.md`)

---

##  Technology Stack

| Layer | Technology | Version | Role |
|-------|-----------|---------|------|
| **Web Framework** | Streamlit | ≥ 1.35.0 | Application server, UI components, session state |
| **Cartographic Engine** | Folium + Leaflet.js | ≥ 0.16.0 | Interactive map rendering with Canvas optimization |
| **Streamlit-Folium Bridge** | streamlit-folium | ≥ 0.20.0 | Bidirectional communication between map and app |
| **Coordinate Reprojection** | PyProj | ≥ 3.6.0 | CRS transformation (EPSG:31985 → EPSG:4326) |
| **Geodesic Computation** | GeoPy | ≥ 2.4.0 | Accurate ellipsoidal distance calculation (500m buffer) |
| **Data Processing** | Pandas | ≥ 2.2.0 | ETL pipeline, classification, filtering |
| **Statistical Visualization** | Plotly | ≥ 5.22.0 | Interactive charts (pie, histogram, scatter, bar) |
| **Language** | Python | ≥ 3.12 | Core runtime |

---

##  Data Sourcing & Provenance

The spatial and attribute datasets used in ASI were compiled from official Brazilian and international data infrastructure providers. All data has been processed and redistributed in accordance with the terms of use of each respective source.

---

###  Brazilian Government & Institutional Sources

**Instituto Brasileiro de Geografia e Estatística (IBGE)**
Digital Elevation Models (DEM/MDS) derived from SRTM missions, census data, and administrative boundary shapefiles for Pernambuco state municipalities. The DEM data served as the primary input for TWI computation, providing terrain altitude and slope matrices.

**Prefeitura Municipal do Cabo de Santo Agostinho**
Primary cartographic base, official neighborhood boundary shapefiles (`bairros_cabo_oficial.json`), urban zoning classifications, and local territorial reference data. This dataset defines the core spatial extent and administrative granularity of the system.

**SEINFRA-PE — Secretaria de Infraestrutura do Estado de Pernambuco**
State-level infrastructure guidelines, road network data, and macro-zoning territorial directives used to contextualize land use classification within the susceptibility model.

**APAC — Agência Pernambucana de Águas e Clima**
Watershed parameters, hydrographic basin boundaries, and historical precipitation modeling data for the Pernambuco coastal region. APAC data informed the hydrological thresholds used in TWI classification.

**CONDEPE-FIDEM — Agência Estadual de Planejamento e Pesquisas de Pernambuco**
Regional planning studies and spatial macrozoning reports from the Pernambuco State Environmental and Planning Agencies, providing contextual territorial intelligence for the study area.

---

###  Scientific & Remote Sensing Sources

**MapBiomas Project** — [mapbiomas.org](https://mapbiomas.org)
Land use and land cover (LULC) classification data for Brazil, derived from Landsat satellite imagery time series and machine learning classification algorithms. MapBiomas codes were used to generate the `Uso_Solo_Desc` attribute column, enabling land use correlation with susceptibility classes. Specific classes used include: Forest Formation (3), Pasture (15), Urban Infrastructure (24), Non-Vegetated Area (25), Water Bodies (33), Silviculture (9), and Agriculture/Pasture Mosaic (21).

**SRTM — Shuttle Radar Topography Mission (NASA/USGS)**
Global DEM data at 30m resolution, used as the base elevation model for slope and contributing area computation. Accessed via IBGE distribution channels.

---

###  Academic Institution

**FACEP — Faculdade de Ciências Educacionais de Pernambuco**
Institutional context and academic framework within which this project was developed. The ASI system was produced as part of applied research in geospatial analysis and data science education.

---

##  Installation

> **Before proceeding**, read the full Terms of Use available in:
> - `ASI_Termos_de_Uso_PT.docx` (Portuguese)
> - `ASI_Terms_of_Use_EN.docx` (English)
>
> For detailed step-by-step installation instructions, refer to **`INSTRUCTIONS.md`**.

### Quick Start

**1. Clone the repository**
```bash
git clone https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes.git
cd ASI---Atlas-de-Suscetibilidade-a-Inundacoes
```

**2. Download the geospatial dataset**

The `data_V3.0` folder is not included in the repository due to file size constraints.
Download it from the official Google Drive link:

```
https://drive.google.com/file/d/1bmu7YR-gXdqL6Qstw1yMd0HpoqAZ_ik3/view?usp=sharing
```

Move the extracted `data_V3.0` folder to the project root (same level as `app.py`).

**3. Run the launcher**

```
Double-click: launch.bat
```

The launcher will automatically:
- Validate Python version (≥ 3.12 required)
- Verify and rename `data_V3.0` → `data`
- Validate the full project structure
- Install all dependencies from `requirements.txt`
- Launch the SIGWeb at `http://localhost:8501`

### System Requirements

| Requirement | Minimum |
|-------------|---------|
| OS | Windows 10 (64-bit) or higher |
| Python | 3.12+ (3.14 recommended) |
| RAM | 4 GB (8 GB recommended) |
| Disk Space | 500 MB free |
| Internet | Required on first run (dependency installation) |
| Browser | Chrome, Firefox or Edge (recent versions) |

---

##  Usage

Once the SIGWeb is running in your browser:

1. **Select a basemap style** — open `// CARTOGRAFIA` → `TILESET BASE` (OSM · Topográfico / CartoDB · Positron / CartoDB · Dark Matter)
2. **Toggle map layers** — open `OVERLAY DE CAMADAS`: municipal mesh, TWI points, hydrographic network, historical flood events, heatmap
3. **Apply spatial filters** — open `// FILTRAGEM VETORIAL`: filter by neighborhood (`Recorte Espacial`) or minimum TWI (`Limiar TWI Mínimo`)
4. **Enable diagnostics** — activate `Inspeção · Ponto` and click any point on the map; the diagnostic card header color reflects the TWI class of the selected point
5. **Explore the buffer analysis** — view 500m risk distribution and nearby historical flood events around the selected point
6. **Open the statistical dashboards** — activate `Dashboard Geoestatístico` for TWI analysis, precipitation history (INMET/APAC), and Defesa Civil PE panel; activate `Ranking IRA · Por Bairro` for neighborhood risk ranking
7. **Export data** — use `Export · CSV Filtrado` to download the active filtered dataset
8. **Read the methodology** — scroll to the *Documentação Técnica e Metodológica (DTM)* section at the bottom

---

##  Project Structure

```
ASI/
│   .gitignore
│   app.py                              # Main Streamlit application entry point
│   ASI_Termos_de_Uso_PT.docx           # Terms of Use (Portuguese)
│   ASI_Terms_of_Use_EN.docx            # Terms of Use (English)
│   Credits.txt
│   INSTRUCTIONS.md                     # Installation and usage guide
│   launch.bat                          # Windows unified launcher
│   LICENSE
│   README.md
│   requirements.txt                    # Python dependencies
│
├───data/                               # Geospatial dataset (renamed from data_V3.0)
│   ├───curated/
│   │   └───attribute_tables/           # Processed TWI attribute tables
│   │           data_table.txt          # Main dataset (semicolon-separated, UTM coords)
│   │           data_table.txt.xml
│   │           Data_Table.xls
│   │           schema.ini
│   │           └───info/
│   │                   arc.dir
│   │
│   └───raw/
│       ├───apac_exports/               # Precipitation data — v3.0
│       │       precipitacao_nordeste.csv
│       │       precipitacao_pernambuco.csv
│       │
│       ├───arcmap_exports/             # GeoJSON boundary files
│       │       bairros_cabo_oficial.json       # Cabo neighborhoods (WGS84)
│       │       br_uf_2024.json                 # Brazil state boundaries
│       │       Data_Table.xls
│       │       mdt_points_tables.txt
│       │       pe_municipios_2024.json         # 185 PE municipalities (active layer)
│       │
│       ├───events/                     # Historical event data — v3.0
│       │       defesacivil_pe_consolidado.csv  # SEPDEC 2024–2026 (78 municipalities)
│       │       historico_inundacoes.csv        # Flood event registry
│       │
│       └───qgis_exports/              # Hydrographic network — v3.0
│               Hidrografia_Pernambuco.geojson
│
├───docs/                               # Academic and methodological documentation
│   ├───academic_context/
│   │       credits.md
│   │       DTM_doc.md
│   │       institutions.md
│   │       project_origin.md
│   │       timeline.md
│   ├───ethics_and_use/
│   ├───methodology/
│   ├───project_overview/
│   └───roadmap/
│
├───outputs/                            # Generated outputs
│   ├───charts/
│   ├───dashboards/
│   ├───maps/
│   └───reports/
│
├───references/
│       articles.md
│       links.md
│       technical_docs.md
│
├───System Version/
│       ASI_CHANGELOG_v3.0.docx         # Full version changelog
│
└───src/                                # Application source code
    ├───analysis/
    │       analytics.py                # Statistical dashboards (TWI, precipitation, Defesa Civil, IRA)
    ├───dashboard/
    ├───processing/
    │       data_loader.py              # ETL pipeline + all v3.0 dataset loaders
    ├───scripts/
    │       utilits.py                  # Shared utility functions
    └───sigweb/
            components.py               # UI components, navigation, GIS theme CSS
            config.py                   # Global constants, paths, color palette
            documentation.py            # In-app DTM documentation renderer
            map_engine.py               # Folium map builder (all layers)
            report_generator.py         # Point-level diagnostic report generator
```

---

##  Legal & Licensing

This software is distributed under the **Apache License 2.0**, supplemented by additional contractual restrictions detailed in the official Terms of Use documents.

```
Copyright © ASI — Atlas de Suscetibilidade a Inundações
Licensed under the Apache License, Version 2.0

This software was developed entirely in Brazil and is governed
exclusively by the laws of the Federative Republic of Brazil,
regardless of the geographic location of the user or device.
```

**Key points:**
- ✅ Free to use for educational and research purposes
- ✅ Permitted to cite in academic work with proper attribution
- ❌ Prohibited to sell, sublicense or commercialize
- ❌ Prohibited to distribute modified versions without prior written authorization
- ❌ Prohibited to remove credits, copyright notices or authorship information

Full terms: [`ASI_Termos_de_Uso_PT.docx`](./ASI_Termos_de_Uso_PT.docx) · [`ASI_Terms_of_Use_EN.docx`](./ASI_Terms_of_Use_EN.docx)

---

## 🎓 Academic Credits & Acknowledgements

This project would not exist without the intellectual guidance, institutional support and scientific rigor provided by the following individuals and organizations.

---

###  Development

**Lúcio Lima**
*Developer & Project Author*
Concept, architecture, data engineering pipeline, geospatial modeling, and full-stack implementation of the ASI SIGWeb system.
🔗 [github.com/LuciolLima](https://github.com/LuciolLima)

---

###  Academic Advisor & Scientific Supervisor

**Dr. Renilson Ramos**
*Researcher · Master in Geography and Geographic Analysis*
Scientific advisor and primary intellectual mentor throughout the development of this project. His expertise in geographic analysis, geomorphometry and spatial research methodology was instrumental in defining the theoretical framework, the selection of the TWI model, and the scientific validity of the susceptibility classification approach adopted by the ASI system. This project is a direct reflection of his guidance and commitment to applied geographic research.

---

###  Instructors & Educators

The following educators contributed to the academic formation that made this project possible:

| Instructor | Discipline | Contribution |
|-----------|-----------|--------------|
| **Prof.ª Bruna Kelly** | Biology | Ecological systems thinking and environmental contextualization of hydrological risk |
| **Prof.ª Gabrielly Simões** | Chemistry | Quantitative analysis methodology and scientific rigor in data interpretation |
| **Prof. Renilson Ramos** | Geography | Core geographic concepts, spatial analysis theory, territorial planning and flood dynamics |

---

###  Institutional Support

**FACEPE —  Fundação de Amparo à Ciência e Tecnologia de Pernambuco**
**CNpq - Conselho Nacional de Desenvolvimento Científico e Tecnológico**
Academic institution providing the educational and institutional framework within which the ASI project was developed and presented.

---

###  Data Providers

| Organization | Country | Contribution |
|-------------|---------|--------------|
| IBGE | 🇧🇷 Brazil | DEM, census data, administrative shapefiles |
| Prefeitura Municipal do Cabo de Santo Agostinho | 🇧🇷 Brazil | Primary cartographic base, neighborhood boundaries |
| SEINFRA-PE | 🇧🇷 Brazil | State infrastructure and territorial directives |
| APAC | 🇧🇷 Brazil | Watershed parameters and precipitation modeling |
| CONDEPE-FIDEM | 🇧🇷 Brazil | Regional planning and macrozoning studies |
| MapBiomas Project | 🌍 International | Land use and land cover classification |
| NASA/USGS (SRTM) | 🌍 International | Global Digital Elevation Model |

---

<div align="center">

<br/>

---

*ASI — Atlas de Suscetibilidade a Inundações*
*SIGWeb v3.0 · Stable Release*

*Developed in Brazil · Governed by Brazilian Law · Apache License 2.0*

[![Repository](https://img.shields.io/badge/Repository-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes)

<br/>

</div>
