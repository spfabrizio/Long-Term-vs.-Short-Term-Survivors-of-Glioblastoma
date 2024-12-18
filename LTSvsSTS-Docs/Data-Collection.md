
---
# Data Protocol Followed
The data was collected using Visiopharm using the method described in this published protocol with some differences.

**Hinda Najem, Sebastian Pacheco, Joanna Kowal, Dan Winkowski, Jared K. Burks, Amy B. Heimberger,**  
Protocol to quantify immune cell distribution from the vasculature to the glioma microenvironment on sequential immunofluorescence multiplex images,  
*STAR Protocols*, Volume 5, Issue 2, 2024, 103079, ISSN 2666-1667, [https://doi.org/10.1016/j.xpro.2024.103079](https://doi.org/10.1016/j.xpro.2024.103079).  
[Science Direct Article Link](https://www.sciencedirect.com/science/article/pii/S2666166724002442)

**Abstract: Summary**  
Although myeloid-derived immune cells can be dispersed throughout the tumor microenvironment (TME), anti-tumor effector cells are confined to the perivascular space. Here, we present a protocol to quantify immune cell distribution from tumor vasculature to its glioma microenvironment on sequential immunofluorescence multiplex images. We describe steps for sequential immunofluorescence multiplex staining, image generation, and storage. We then detail the procedures for tissue, vessel, and nuclei segmentation; cell phenotyping; data extraction; and training using RStudio and Spyder.

<br>
<div align="center">
  <img src="/LTSvsSTS-Docs/images/LTSvsSTS-Abstract.png" alt="Description of image" width="550"/>
</div>
<br>

---

# Data Collection Background
Data is gathered from surgically removed tumors from patients with glioblastoma (GBM) which is a brain tumor originating in glial cells that have the role of protecting nerve cells in the brain. It has a 5-year survival rate of around 10%.  The main question is: Why do some patients with GBM live longer than others? 

An area to explore to find answers to this question is looking at the tumor microenvironment of each patient meaning looking at the types of cells and any signaling molecules that exist in these tumors. For example, suppose there is a lot of molecule A or cell of phenotype A that exists in short-term survivors compared to long-term survivors. In that case, it can explain a patient's survival rate giving them a more accurate prognosis. Or it means we can create treatments for target A to help patients live longer.

These tumors are processed after removal being formalin-fixed and paraffin-embedded (FFPE). They are then sliced 4 microns thick (a cell is typically 10-30 microns in diameter). These FFPE slides are then prepared using antigen retrieval and dewaxing protocols. These slides are then stained by the Lunaphore COMET™ system.

<br>
<div align="center">
  <img src="/LTSvsSTS-Docs/images/LTSvsSTS-FFPE.png" alt="Description of image" width="650"/>
</div>
<br>

Antibodies are also loaded into COMET™. These antibodies attach to antigens which are proteins on the surface of the tumor slice that are indicators for certain molecules or phenotypes of cells. COMET™ then applies secondary antibodies that have either Cy5 or TRITC fluorophores stuck to them that attach to these antibodies.

<br>
<div align="center">
  <img src="/LTSvsSTS-Docs/images/LTSvsSTS-Lunaphore.png" alt="Description of image" width="850"/>
</div>
<br>

Then a laser is applied causing Cy5 and TRITC fluorophores to emit light. They have distinguishable emission peaks so the emitted light reveals the location of target antigens as the two targeted antibodies can distinguished from one another. Then this is imaged and the slide is eluted removing the primary antibodies. This is repeated for many pairs of antigens with the images being stacked. With the final stacked image, the user can give the emissions different colors to differentiate between all of them.
Each pixel in the image has the intensity value of every single marker the antibodies targeted. For example, with 20 markers, each pixel stores 20 numerical values. A high-intensity value indicates a high presence of a specified antigen in that area.

<br>
<div align="center">
  <img src="/LTSvsSTS-Docs/images/LTSvsSTS-Antibodies.png" alt="Description of image" width="650"/>
</div>
<br>

All antibodies used for staining include:
<div align="center">

| **Antibody** | **Target** |
|--------------|------------|
| **DAPI**     | Nuclei      |
| **CD31**     | Vessels     |
| **CD11c**    | Dendritic cells |
| **CD163**    | M2 macrophages |
| **CD205**    | Dendritic cells |
| **CD206**    | M2 macrophages |
| **CD8**      | Cytotoxic T cells |
| **CD4**      | Helper T cells |
| **CD103**    | Tissue-resident memory T cells |
| **FOXP3**    | Regulatory T cells (Tregs) |
| **GFAP**     | Astrocytes  |
| **GRZMB**    | Granzyme B in cytotoxic lymphocytes |
| **HLADR**    | MHC Class II antigen-presenting cells |
| **INFγ**     | Interferon-gamma produced by Th1 cells and NK cells |
| **Ki67**     | Proliferation marker |
| **NFAT1**    | Transcription factor in T cell activation |
| **NFAT2**    | Transcription factor in T cell activation |
| **P2RY12**   | Microglia   |
| **PD1**      | Exhausted T cells |
| **PDL1**     | Inhibits T cell activity |
| **Perforin** | Found in cytotoxic T cells and NK cells |
| **SOX2**     | Stem cell pluripotency marker |
| **TIM3**     | Exhaustion marker on T cells |
| **TNFa**     | Pro-inflammatory cytokine |
| **cCasp3**   | Marker of apoptosis |
| **pLCK**     | Activated LCK kinase in T cells |
| **pSTAT3**   | Signaling marker in immune cells |
| **CD68**     | Macrophages |
</div>

---

# Data Extraction

Navigate to the protocol referenced above.

Follow the steps in “Sequential multiplex immunofluorescence (SeqIF) staining on the COMET platform” and “Data transfer to Visiopharm software”.

Follow the steps in “Part 1: Tissue segmentation” to create an APP in Visiopharm that uses a deep learning algorithm using areas of high DAPI, GFAP, and CD31 intensity to differentiate between tissue and non-tissue. 

Follow the steps in “Part 2: Vessel identification and segmentation” creating an APP using a thresholding algorithm to identify blood vessels. The application using AWS does not support computations using blood vessel distance yet but the Jupyter file shows how it would be implemented. 

Follow the steps in “Part 3: Nuclei detection” using Visiopharm’s pre-trained deep learning algorithm with a few edits for the algorithm and post-processing indicated in the protocol. This algorithm looks at DAPI signal intensity and distribution to identify if areas of high DAPI signal represent a cell nucleus based on previous training. It will then label the nucleus as an object and dilate a few pixels to represent the cell membrane border. 

<br>
<div align="center">
  <img src="/LTSvsSTS-Docs/images/LTSvsSTS-Nuclei.png" alt="Description of image" width="650"/>
</div>
<br>

Follow most of the steps in “Part 4: Data extraction.”  However, instead of exporting raw intensity, perform post-processing calculations to calculate relative intensity. For each marker, manually extract its intensity (don’t use multiplexing) and use the top 50% of pixels with the highest intensity values for that marker to calculate the average marker intensity within a cell’s border. Then divide this value by the average autofluorescence intensity of either Cy5 or TRITC depending on which secondary antibody the marker was used with (this is in the protocol). Name this calculation {Marker}_R. You should have these columns to export per sample: CD11c_R, CD163_R, CD205_R, CD206_R, CD8_R, CD4_R, CD103_R, FOXP3_R, GFAP_R, GRZMB_R, HLADR_R, INFgamma_R, NFAT1_R, NFAT2_R, P2RY12_R, PD1_R, PDL1_R, Perforin_R, SOX2_R, TIM3_R, TNFa_R, cCasp3_R, pLCK_R, pSTAT3_R, and CD68_R. So each sample (20 of them) should only have these columns.

The data per sample is exported as a TSV file. Each row of the file represents a cell. Each column represents a marker. Remember each pixel within a cell’s border contains all 26 intensity values. So there are 26 averages controlled for noise calculated per cell. A sample has 100k+ cells each having these 26 averages. Most averages are near 0 for a cell because they had little to no staining present within its border for most markers. 

Stop following the protocol and skip to “Part 8: Visiopharm phenoplex feature”. Use phenoplex to threshold each marker per sample. This means finding the most accurate average intensity value for a marker such that if a cell has a higher value than that average you would consider it positive for that marker and negative if it is lower. There will be 26 threshold values per sample.


