# Data Protocol Followed
The data was collected using Visiopharm using the method described in this published protocol with some differences.

**Hinda Najem, Sebastian Pacheco, Joanna Kowal, Dan Winkowski, Jared K. Burks, Amy B. Heimberger,**  
Protocol to quantify immune cell distribution from the vasculature to the glioma microenvironment on sequential immunofluorescence multiplex images,  
*STAR Protocols*, Volume 5, Issue 2, 2024, 103079, ISSN 2666-1667, [https://doi.org/10.1016/j.xpro.2024.103079](https://doi.org/10.1016/j.xpro.2024.103079).  
[Science Direct Article Link](https://www.sciencedirect.com/science/article/pii/S2666166724002442)

**Abstract: Summary**  
Although myeloid-derived immune cells can be dispersed throughout the tumor microenvironment (TME), anti-tumor effector cells are confined to the perivascular space. Here, we present a protocol to quantify immune cell distribution from tumor vasculature to its glioma microenvironment on sequential immunofluorescence multiplex images. We describe steps for sequential immunofluorescence multiplex staining, image generation, and storage. We then detail the procedures for tissue, vessel, and nuclei segmentation; cell phenotyping; data extraction; and training using RStudio and Spyder.

# Data Collection Background

IMAGE

Data is gathered from surgically removed tumors from patients with glioblastoma (GBM) which is a brain tumor originating in glial cells that have the role of protecting nerve cells in the brain. It has a 5-year survival rate of around 10%.  The main question is: Why do some patients with GBM live longer than others? 

An area to explore to find answers to this question is looking at the tumor microenvironment of each patient meaning looking at the types of cells and any signaling molecules that exist in these tumors. For example, suppose there is a lot of molecule A or cell of phenotype A that exists in short-term survivors compared to long-term survivors. In that case, it can explain a patient's survival rate giving them a more accurate prognosis. Or it means we can create treatments for target A to help patients live longer.

These tumors are processed after removal being formalin-fixed and paraffin-embedded (FFPE). They are then sliced 4 microns thick (a cell is typically 10-30 microns in diameter). These FFPE slides are then prepared using antigen retrieval and dewaxing protocols. These slides are then stained by the Lunaphore COMET™ system.

IMAGE

Antibodies are also loaded into COMET™. These antibodies attach to antigens which are proteins on the surface of the tumor slice that are indicators for certain molecules or phenotypes of cells. COMET™ then applies secondary antibodies that have either Cy5 or TRITC fluorophores stuck to them that attach to these antibodies. When 

Then a laser is applied causing Cy5 and TRITC fluorophores to emit light. They have distinguishable emission peaks so the emitted light reveals the location of target antigens as the two targeted antibodies can distinguished from one another. Then this is imaged and the slide is eluted removing the primary antibodies. This is repeated for many pairs of antigens with the images being stacked. With the final stacked image, the user can give the emissions different colors to differentiate between all of them.
Each pixel in the image has the intensity value of every single marker the antibodies targeted. For example, with 20 markers, each pixel stores 20 numerical values. A high-intensity value indicates a high presence of a specified antigen in that area. 



## Tissue Preparation

* **Tumor Processing**  
  - Tumors are formalin-fixed and paraffin-embedded (FFPE) after removal.  
  - They are sliced into 4-micron thick sections (a typical cell diameter is 10-30 microns).  
  - FFPE slides are prepared using antigen retrieval and dewaxing protocols.  
  - These slides are stained using the Lunaphore COMET™ system.

**[Lunaphore COMET™](https://lunaphore.com/products/comet/)**

---

## Staining & Imaging

* **Primary Antibodies** attach to antigens on the tumor slice.  
* **Secondary Antibodies** with Cy5 or TRITC fluorophores attach to the primary antibodies.  
* **Laser Excitation** causes Cy5 and TRITC to emit light, which is imaged.  
* The slide is eluted, removing the primary antibodies. This is repeated for multiple antigen pairs.  
* The final stacked image allows for color differentiation between all targeted antibodies.  
* Each pixel in the image has intensity values for every marker.  
  - Example: With 20 markers, each pixel has 20 numerical values.  
  - High intensity = high presence of the antigen.

---

## Antibodies Used

* **DAPI** (nuclei)  
* **CD31** (vessels)  
* **CD11c** (dendritic cells)  
* **CD163** (M2 macrophages)  
* **CD205** (dendritic cells)  
* **CD206** (M2 macrophages)  
* **CD8** (cytotoxic T cells)  
* **CD4** (helper T cells)  
* **CD103** (tissue-resident memory T cells)  
* **FOXP3** (regulatory T cells (Tregs))  
* **GFAP** (astrocytes)  
* **GRZMB** (granzyme B in cytotoxic lymphocytes)  
* **HLADR** (MHC Class II antigen-presenting cells)  
* **INFγ** (Interferon-gamma)  
* **Ki67** (proliferation marker)  
* **NFAT1** (T cell activation transcription factor)  
* **NFAT2** (T cell activation transcription factor)  
* **P2RY12** (microglia)  
* **PD1** (exhausted T cells)  
* **PDL1** (T cell activity inhibitor)  
* **Perforin** (cytotoxic T cells & NK cells)  
* **SOX2** (stem cell pluripotency marker)  
* **TIM3** (T cell exhaustion marker)  
* **TNFα** (pro-inflammatory cytokine)  
* **cCasp3** (apoptosis marker)  
* **pLCK** (activated LCK kinase)  
* **pSTAT3** (immune cell signaling marker)  
* **CD68** (macrophages)  

---

## Data Extraction

1. **Staining & Imaging**  
   - Follow the "Sequential multiplex immunofluorescence (SeqIF) staining" steps from the protocol.  
   - Transfer image data to Visiopharm.

2. **Tissue Segmentation**  
   - Create an APP in Visiopharm using a deep learning algorithm.  
   - Use areas with high DAPI, GFAP, and CD31 intensity to differentiate tissue from non-tissue.  

3. **Vessel Segmentation**  
   - Identify blood vessels using a thresholding algorithm.  

4. **Nuclei Detection**  
   - Use Visiopharm’s pre-trained deep learning algorithm.  
   - DAPI signal intensity and distribution are used to identify nuclei.  
   - Nuclei are dilated to represent the cell border.

5. **Data Extraction**  
   - Export per-sample data as a TSV file.  
   - Each row = cell; each column = marker.  
   - Extract intensity for 26 markers and normalize using autofluorescence intensity.  

6. **Phenoplex Feature Thresholding**  
   - Use phenoplex to determine intensity thresholds for 26 markers per sample.  
   - If a cell’s intensity is above this threshold, it is positive for the marker.  

---


For more details, see the [Data Collection Documentation](./docs/data_collection.md).


