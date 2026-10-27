# RUMBER - Quantum Random Number Generation & Analysis System
> *"True Randomness, Powered by Quantum."*

## Quantum Computing Hackathon — Problem Statement 2

**RUMBER** is an enterprise-grade **Quantum Random Number Generation & Analysis System** built exclusively with **Python, Qiskit, Qiskit Aer, and Streamlit**. 

No HTML, CSS, JavaScript, or external web frameworks are required.

---

## 📁 Repository Structure

```
E:\Qiskit-PROBLEM-STATEMENT-2\
├── QuantumRand.ipynb           # Complete 12-section Hackathon Jupyter Notebook
├── app.py                      # Interactive Streamlit QRNG web application & dashboard
├── QuantumRand_Report.md       # Short project evaluation report
├── Presentation_Outline.md     # 5-7 minute pitch outline for judges
├── requirements.txt            # Python dependencies (Streamlit, Qiskit, Qiskit-Aer, etc.)
├── report.md                   # Formal hackathon technical report & academic citations
├── README.md                   # Setup guide and execution instructions
├── qrng_simulator_bits.csv     # Exported sample of 10,000 quantum bits
└── run_qrng.py                 # Standalone terminal execution script
```

---

## 🚀 Quick Start Guide (Windows PowerShell)

### Step 1: Create and Activate a Virtual Environment (Recommended)

In Windows PowerShell, run:

```powershell
# 1. Navigate to the project root
cd E:\Qiskit-PROBLEM-STATEMENT-2

# 2. Create a virtual environment named .venv
python -m venv .venv

# 3. Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

---

### Step 2: Install Dependencies

With the virtual environment active, install all required packages:

```powershell
pip install -r requirements.txt
```

*(Or directly via `python -m pip install streamlit qiskit qiskit-aer numpy pandas matplotlib scipy`)*.

---

### Step 3: Run the Streamlit Application

Launch the Streamlit web application:

```powershell
streamlit run app.py
```

Your browser will automatically open at:  
👉 **`http://localhost:8501`**

---

## 🔬 Features & Streamlit Dashboard Overview

1. **Quantum Bit Generation (`app.py`):**
   - Single-qubit state initialization in $|0\rangle$.
   - Hadamard ($H$) gate creates equal superposition:
     $$|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$$
   - Computational basis measurement with Qiskit's `AerSimulator` (`memory=True`) preserving chronological sequence.
   - Selectable bit sizes: **100**, **1,000**, **10,000**, or **Custom**.
2. **Interactive Streamlit Dashboard:**
   - 4 Top Metric Cards: Total bits, zero/one proportions, Shannon Entropy ($H(X)$), Wald-Wolfowitz runs count and Z-score, and Pearson Chi-Square ($\chi^2$).
   - Frequency distribution bar chart (0s vs 1s) with theoretical 50% dashed line.
   - Empirical vs theoretical Born's rule probability comparison chart.
   - 2D Spatial Raster Matrix ($20 \times 20$ grid of 400 bits) verifying lack of clustering.
   - Digital waveform pulse trace of the first 50 bits.
   - First 50 bits code viewer.
3. **Statistical Randomness Verification:**
   - Frequency (Monobit) test with Z-score and two-tailed p-value.
   - Shannon binary entropy ($>0.9999$ bits/symbol).
   - Wald-Wolfowitz runs test for sequence independence.
   - Chi-Square goodness-of-fit test.
   - Downloadable statistical report text file.
4. **Classical PRNG Benchmark:**
   - Benchmarks against NumPy's modern `PCG64` BitGenerator (`seed=42`).
   - Side-by-side comparison table showing theoretical vs quantum vs classical results.
   - Explains algorithmic determinism vs quantum measurement model.
5. **Downloadable Results:**
   - One-click download of the active quantum bitstream (`bit_index`, `generated_bit`, `source`).
   - Download of the combined comparison dataset.
   - Download of the statistical summary report.
6. **Optional IBM Quantum Hardware Module:**
   - Secure execution path using modern `qiskit-ibm-runtime` (SamplerV2).
   - Reads tokens from environment variables or sidebar input without hardcoding.
   - Graceful fallback if credentials are unconfigured.

---

## 📜 Citations & References

1. Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
2. Qiskit Development Team (2024). *Qiskit Documentation*. https://qiskit.org/
3. Qiskit Aer Documentation (2024). *Quantum circuit simulator for Qiskit*. https://qiskit.github.io/qiskit-aer/
4. Rukhin, A., et al. (2010). *NIST Special Publication 800-22 Rev. 1a*. National Institute of Standards and Technology.
5. Herrero-Collantes, M., & Garcia-Escartin, J. C. (2017). *Quantum random number generators*. Reviews of Modern Physics.
