# Running the Jupyter Notebook for LTS vs SSTS Analysis

## Prerequisites

To run the Jupyter Notebook, ensure that all the libraries listed in `minicondalibraries.txt` are installed. Creating a Miniconda environment is not required; you may choose your preferred method to run the notebook.

## Directory Structure

- **LTSvsSTS-Jupyter-Notebook/**
  - **LTSvsSTS-Data/**: Contains all 20 CSV files of the data extracted from all samples. Each CSV file includes signal-intensity data for all 26 markers analyzed for each cell. These CSVs were created using the protocol described [here](#). Note that the original protocol outputs TSV files, which have been converted to CSV format for easier visualization.
  - **LTSvsSTS-Results/**: Contains sample result outputs from the `LTSvsSTS_Analysis.ipynb` using default values.

## Threshold Dictionary (`thresholddict`)

The `thresholddict` dictionary contains threshold values for each marker per sample. Each entry in the dictionary corresponds to a CSV file and includes 26 keys, each representing a marker. The values indicate the signal intensity required to label a cell as positive for that marker.

### Example Entry

```python
thresholddict = {
    "LTSvsSTS-Data/NU00295.csv": {
        "CD11c_R": 1.59, "CD163_R": 1.30, "CD205_R": 1.40, "CD206_R": 1.40, "CD8_R": 1.85,
        "CD4_R": 1.32, "CD103_R": 1.50, "FOXP3_R": 1.46, "GFAP_R": 3.21, "GRZMB_R": 1.89,
        "HLADR_R": 1.74, "INFgamma_R": 1.92, "Ki67_R": 1.66, "NFAT1_R": 1.89, "NFAT2_R": 2.50,
        "P2RY12_R": 1.31, "PD1_R": 1.38, "PDL1_R": 1.48, "Perforin_R": 1.63, "SOX2_R": 2.20,
        "TIM3_R": 1.31, "TNFa_R": 1.84, "cCasp3_R": 1.27, "pLCK_R": 2.20, "pSTAT3_R": 1.26,
        "CD68_R": 1.43
    },
    # ... include all 20 entries
}
```

**Note:** Ensure that each entry in `thresholddict` has all 26 keys corresponding to the columns in the CSV files. If you remove any entries from `thresholddict`, update the `filelist` accordingly.

## File List (`filelist`)

The `filelist` variable contains the paths to all 20 CSV data files.

```python
filelist = [
    "LTSvsSTS-Data/NU00295.csv", "LTSvsSTS-Data/NU00429.csv", "LTSvsSTS-Data/NU00431.csv",
    "LTSvsSTS-Data/NU00468.csv", "LTSvsSTS-Data/NU00759.csv", "LTSvsSTS-Data/NU00826.csv",
    "LTSvsSTS-Data/NU00866.csv", "LTSvsSTS-Data/NU00908.csv", "LTSvsSTS-Data/NU01094.csv",
    "LTSvsSTS-Data/NU01115.csv", "LTSvsSTS-Data/NU01405.csv", "LTSvsSTS-Data/NU01420.csv",
    "LTSvsSTS-Data/NU01482.csv", "LTSvsSTS-Data/NU01713.csv", "LTSvsSTS-Data/NU01798.csv",
    "LTSvsSTS-Data/NU01929.csv", "LTSvsSTS-Data/NU02064.csv", "LTSvsSTS-Data/NU02359.csv",
    "LTSvsSTS-Data/NU02514.csv", "LTSvsSTS-Data/NU02738.csv"
]
```

**Important:** If you remove any entries from `thresholddict`, ensure that the corresponding files are also removed from `filelist`.

## Phenotype Dictionary (`phenotypedict`)

The `phenotypedict` dictionary defines phenotypes based on combinations of markers. Each key is the name of the phenotype, and the value is a list of marker columns that define that phenotype. A cell is considered positive for a phenotype if all markers in the list exceed their respective thresholds.

### Example

```python
phenotypedict = {
    # Single marker phenotypes
    "CD11c+": ["CD11c_R"],
    "CD163+": ["CD163_R"],
    "CD4+Ki67+": ["CD4_R", "Ki67_R"],
    "CD4+pSTAT3+": ["CD4_R", "pSTAT3_R"],
    "CD68+CD163+CD11c+pSTAT3+": ["CD68_R", "CD163_R", "CD11c_R", "pSTAT3_R"],
}
```

**Note:** The list can contain any combination of marker names corresponding to the CSV columns. Customize the phenotype names and marker combinations as needed.

## Distance Dictionary (`distancedict`)

The `distancedict` dictionary is used to perform computations on specific ranges of distance measurements within the dataset. Each key represents a distance category, and the value is a list defining the range.

### Example

```python
distancedict = {
    "cCasp3+GFAP+ Distance": {
        "0-100": [0, 100],
        "100-250": [100, 250],
        "250-500": [250, 500]
    }
}
```

**Usage:** This allows for analysis of cells within specific distance ranges, such as the distance from the center of a cell to a particular structure. Refer to the referenced protocol paper for detailed instructions on collecting and using distance data.

## Running the Analysis

1. **Install Required Libraries:**
   Ensure all libraries listed in `minicondalibraries.txt` are installed. You can install them using:

   ```bash
   pip install -r minicondalibraries.txt
   ```

2. **Prepare Data:**
   - Place all CSV files in the `LTSvsSTS-Data/` directory.
   - Ensure that `thresholddict`, `phenotypedict`, and `distancedict` are correctly defined in the `LTSvsSTS_Analysis.ipynb` notebook.

3. **Run the Jupyter Notebook:**
   - Open Jupyter Notebook and navigate to `LTSvsSTS-Jupyter-Notebook/LTSvsSTS_Analysis.ipynb`.
   - Execute the notebook cells to perform data analysis using the defined dictionaries and file list.

4. **Review Results:**
   - Results will be saved in the `LTSvsSTS-Results/` directory.
   - Sample outputs using default values are already provided for reference.

## Important Considerations

- **Threshold Consistency:** Ensure that the thresholds in `thresholddict` align with the corresponding markers in your CSV files. A mismatch can lead to incorrect phenotype classification.
  
- **File and Dictionary Alignment:** If you modify `thresholddict` by adding or removing entries, make sure to update `filelist` accordingly to maintain consistency.

- **Phenotype Definitions:** Customize `phenotypedict` to reflect the specific combinations of markers relevant to your analysis objectives.

- **Distance Analysis:** Utilize `distancedict` to segment your data based on distance measurements, enabling more granular analysis of spatial relationships within the tumor microenvironment.

For further details on the functions and their implementations, refer to the `LTSvsSTS_Analysis.ipynb` notebook.

