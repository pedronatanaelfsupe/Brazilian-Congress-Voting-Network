# Community Detection in Brazilian Congress Voting Network

This repository contains the source code and data for the research paper **"Community Detection and Analysis of Political Alliances in the Brazilian Congress Voting Network"**. The project explores advanced network analysis techniques, including the **Leiden algorithm** and **edge pruning**, to analyze political alliances and voting behaviors in the Brazilian Congress.

## Project Overview

This study aims to uncover ideological divides and temporal shifts in political alliances within the Brazilian Congress by:
1. Applying network science techniques to analyze voting data.
2. Utilizing polarized proposition filtering and edge pruning for improved modularity.
3. Detecting and tracking communities across multiple legislative years.

The repository is structured to facilitate reproducibility and further research in community detection and political network analysis.

---

## Repository Structure

```
├── data/
│   ├── csv/                    # Processed CSV data files
│   │   ├── detailed_results.csv
│   │   ├── party_community_table_adjusted.csv
│   │   ├── party_community_table.csv
│   │   ├── results_backbone.csv
│   │   └── results_summary.csv
│   └── graphs/                 # Graphs generated from the analysis
├── depcom/                     # Main Python package
│   └── src/
│       └── __init__.py
├── notebooks/                  # Jupyter Notebooks for data analysis
│   ├── dataset_analysis.ipynb
│   ├── method_evaluation.ipynb
│   └── results_evaluation.ipynb
├── .gitignore
├── Dockerfile                  # Docker configuration for the project
├── output.png                  # Sample output visualization
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

---

## Installation

### Using Docker
To set up the environment with Docker:
1. Ensure you have Docker installed.
2. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
3. Build the Docker image:
   ```bash
   docker build -t community-detection .
   ```
4. Run the container:
   ```bash
   docker run -v $(pwd)/data:/app/data community-detection
   ```

### Manual Setup
1. Install Python 3.9 or higher.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Data Preparation
Ensure the required data files are placed in the `data/csv` directory. The data includes voting records and other metadata from the Brazilian Congress.

### Running the Code
To execute the main script:
```bash
python depcom/src/main.py
```

### Notebooks
Use the Jupyter Notebooks in the `notebooks/` folder for:
- **`dataset_analysis.ipynb`**: Analyzing raw and processed datasets.
- **`method_evaluation.ipynb`**: Comparing different community detection methods.
- **`results_evaluation.ipynb`**: Visualizing and interpreting results.

---

## Methodology

1. **Data Preprocessing**: Standardizing and filtering voting data.
2. **Polarized Proposition Filtering**: Selecting propositions based on vote polarization thresholds.
3. **Network Construction**: Building voting similarity networks.
4. **Edge Pruning**: Optimizing network modularity by removing weaker connections.
5. **Community Detection**: Using the Leiden algorithm to identify cohesive communities.
6. **Temporal Analysis**: Tracking changes in community structures over time.

For more details, refer to the accompanying research paper in the repository.

---

## Results

The proposed methodology achieved:
- **10.95% improvement in modularity** compared to previous methods.
- Identification of distinct political communities and temporal shifts.
- Enhanced understanding of ideological divides in the Brazilian Congress.

---

## Dependencies

The project uses the following libraries:
- `pandas`
- `matplotlib`
- `seaborn`
- `numpy`
- `networkx`
- `leidenalg`

Full dependencies are listed in `requirements.txt`.

---
