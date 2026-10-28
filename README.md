# RUMBER — Quantum Random Number Generator (QRNG)
> *"True Randomness, Powered by Quantum Mechanics."*

### Qiskit Fall Fest 2026 | Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
**Hackathon Track:** Problem Statement 2: Quantum Random Number Generator (QRNG) — Harnessing Quantum Mechanics for True Randomness  
**Core Stack:** Python 3.10+, Qiskit 2.x / 1.x, Qiskit Aer, Qiskit IBM Runtime, Streamlit, NumPy, Pandas, Matplotlib, SciPy.

---

## 📖 Executive Summary & Core Objective

Randomness is a cornerstone of modern digital infrastructure—essential for cryptographic key generation (RSA, ECC, AES), zero-knowledge proofs, Monte Carlo stochastic simulations, and statistical modeling. However, classical computers are deterministic state machines that cannot produce true physical randomness. They rely on **Pseudorandom Number Generators (PRNGs)** governed by deterministic mathematical recurrence relations $s_{n+1} = f(s_n)$, meaning any agent with knowledge of the internal state or seed can anticipate all past and future outputs.

**RUMBER** is an enterprise-grade **Quantum Random Number Generator (QRNG)** built using **Qiskit** and presented through an interactive, responsive **Streamlit** dashboard. By preparing a single superconducting qubit in an equal superposition state:

$$|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$$

via a Hadamard ($H$) gate and measuring in the Pauli-$Z$ computational basis, RUMBER harnesses the irreducible indeterminism of quantum measurement (**Born's Rule**, $P(0) = P(1) = 0.5$) to generate unbiased, unpredictable binary sequences.

RUMBER preserves **individual chronological measurement outcomes** (via Qiskit Aer's `memory=True` and Qiskit IBM Runtime's `Sampler`), rigorously analyzes sequences across a **5-test statistical randomness battery**, benchmarks against classical PRNGs, provides **John von Neumann hardware bias mitigation**, and supports execution on **real IBM Quantum hardware**.

---

## 🌟 Key Features & Capabilities

1. **Genuine Qiskit Circuit Architecture:**
   - 1-qubit, 1-classical-register circuit (`QuantumCircuit(1, 1)`).
   - Equal superposition state preparation via Hadamard ($H$) gate.
   - Computational basis measurement projection ($M_Z$).
   - Both ASCII text diagram and graphical Matplotlib circuit rendering.

2. **Order-Preserving Bit Extraction:**
   - Extracts individual measurement outcomes in exact chronological order (no aggregate binning).
   - Scalable generation supporting **1,000**, **10,000**, and **100,000 bits** using efficient batching.

3. **Dual Execution Modes:**
   - **Mode A — Local Quantum Simulator (AerSimulator):** Runs instantly out of the box with zero IBM credentials required.
   - **Mode B — Real IBM Quantum Hardware (QPU):** Optional cloud execution on real superconducting quantum processors (`ibm_sherbrooke`, `ibm_kyiv`, `ibm_brisbane`, etc.) via `qiskit-ibm-runtime` and `Sampler`. Non-blocking, secure credential handling, queue status tracking, and graceful fallback.

4. **Rigorous 5-Test Statistical Randomness Suite:**
   - **Chi-Square ($\chi^2$) Goodness-of-Fit Test ($df=1$):** Tests uniform 50:50 parity.
   - **Wald-Wolfowitz Runs Test:** Tests sequence independence and absence of clustering.
   - **Frequency (Monobit) Test (NIST SP 800-22):** Complementary error function ($S_{obs}$) test.
   - **Shannon Binary Entropy:** Measures information uncertainty per symbol (ideal: $1.000000$ bit/symbol).
   - **Serial Lag-1 Autocorrelation ($r_1$):** Verifies absence of adjacent bit memory.
   - Honest scientific interpretation: explicitly notes that passing statistical tests does not alone prove true physical randomness or cryptographic security on a classical simulator.

5. **Classical PRNG Benchmark:**
   - Direct empirical comparison against NumPy's modern `PCG64` BitGenerator.
   - Comparative metrics table and side-by-side deviation plots.
   - Architectural delineation: Algorithmic PRNG vs Quantum Simulation vs Physical QPU.

6. **Hardware Bias Mitigation (Von Neumann Extractor):**
   - Addresses real superconducting hardware noise (readout asymmetry and $T_1$ relaxation).
   - Mathematical implementation of John von Neumann debiasing ($01 \to 0, 10 \to 1$, discards $00/11$).
   - Interactive noise simulator slider ($P(1) \in [0.50, 0.80]$) with live before/after statistical comparison and yield analysis.

7. **Streamlit Application & Exports:**
   - Single-file Streamlit interface with a clean, readable white-and-blue theme (`#0052cc`).
   - 2D spatial raster dispersion matrix ($20 \times 20$ grid) and digital waveform pulse trace.
   - One-click downloads: **Raw bitstream (.txt)**, **Structured CSV (.csv)**, and **Statistical Report (.txt)**.

---

## 📁 Repository Structure

```
e:\Qiskit-PROBLEM-STATEMENT-2\
├── app.py                      # Complete interactive Streamlit web dashboard
├── run_qrng.py                 # Standalone terminal CLI execution script
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation and setup guide
├── QRNG_Qiskit_Prototype.ipynb # 12-section Jupyter Notebook prototype
├── QRNG_Hackathon_Report.md    # Formal hackathon evaluation report
├── report.md                   # Concise technical summary
├── qrng_simulator_bits.csv     # Sample generated bitstream (CSV format)
└── qrng_simulator_bits.txt     # Sample generated bitstream (Raw TXT format)
```

---

## 🚀 Installation & Quick Start Guide (Windows PowerShell)

Follow these exact steps in Windows PowerShell to set up and launch the application.

### Step 1: Open Windows PowerShell and Navigate to the Project

```powershell
cd e:\Qiskit-PROBLEM-STATEMENT-2
```

### Step 2: Create and Activate a Python Virtual Environment

```powershell
# Create a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

> *Note: If PowerShell displays an execution policy error, enable local script execution for this session by running: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`.*

### Step 3: Install Required Dependencies

```powershell
pip install -r requirements.txt
```

Verified compatible dependencies:
- `streamlit>=1.32.0`
- `qiskit>=1.0.0`
- `qiskit-aer>=0.14.0`
- `qiskit-ibm-runtime>=0.20.0`
- `numpy>=1.24.0`
- `pandas>=2.0.0`
- `matplotlib>=3.7.0`
- `scipy>=1.10.0`

---

## 🔐 IBM Quantum Credentials Setup (Optional for Hardware Mode)

To run the QRNG on **real IBM Quantum hardware** (Mode B), configure your API key securely without committing it to git:

1. Create a directory named `.streamlit` (if it does not already exist) and a file named `secrets.toml`:
   ```powershell
   New-Item -ItemType Directory -Force -Path ".streamlit"
   New-Item -ItemType File -Force -Path ".streamlit\secrets.toml"
   ```
2. Open `.streamlit\secrets.toml` and add your 44-character API key:
   ```toml
   IBM_QUANTUM_API_KEY = "YOUR_44_CHARACTER_API_KEY_HERE"
   
   # Optional: If your account uses a specific instance or CRN (e.g. from an invited hub)
   # IBM_QUANTUM_INSTANCE = "crn:v1:bluemix:public:quantum-computing:us-east:a/...::"
   ```
3. `.streamlit/secrets.toml` is pre-configured in `.gitignore` to ensure your credentials are never committed.
4. *Security guarantee:* Your token is never logged, printed, or exposed in the UI. Only masked tokens (e.g. `••••4a1b`) are displayed.

---

## 🖥️ Launching the Streamlit Web Application

Launch the full interactive QRNG dashboard:

```powershell
streamlit run app.py
```

Streamlit will launch locally and automatically open your default web browser at:
👉 **`http://localhost:8501`**

### Using the Application:
1. **Mode A (Simulator):**
   - Choose a bit preset (**1,000**, **10,000**, or **100,000 bits**) or enter a custom size.
   - Click **⚡ Generate Random Bits (Simulator)**.
   - Inspect the live metric cards, frequency charts, probability comparison, 2D raster matrix, and waveform trace in Tab 1.
   - Review detailed $p$-values and hypothesis tests in Tab 2.
   - Benchmark against classical PRNG in Tab 3.
   - Experiment with the hardware noise slider and Von Neumann extractor in Tab 4.
   - View the circuit diagram and mathematical derivation in Tab 5.
   - Download the generated bits in both **TXT** and **CSV** formats.
2. **Mode B (Real IBM Quantum Hardware):**
   - Switch to **Mode B: Real IBM Quantum Hardware** in the sidebar.
   - The app automatically detects credentials from `.streamlit/secrets.toml`.
   - Click **🔄 Query / Refresh Backends** to query live operational real quantum processors (`ibm_sherbrooke`, `ibm_kyiv`, `ibm_brisbane`, etc., strictly excluding simulators).
   - Select your target backend or `Least Busy Real QPU (Auto-select)`.
   - Select your shot count and click **🚀 Run on Real Quantum Hardware**.
   - If execution fails or the cloud queue times out, the error is displayed with diagnostic instructions without silently falling back to a simulator.

---

## 💻 Running the Standalone CLI Script

You can also run the terminal-based QRNG generator and statistical test battery without the web interface:

```powershell
# Default: 10,000 bits
python run_qrng.py

# Custom bit size (e.g. 100,000 bits):
python run_qrng.py --bits 100000
```

---

## 📓 Running the Jupyter Notebook

To inspect and run the interactive 12-section notebook in VS Code or JupyterLab:

```powershell
jupyter notebook QRNG_Qiskit_Prototype.ipynb
```

The notebook covers circuit synthesis, Bloch sphere representation, shot collection, statistical testing, classical PRNG benchmarking, and Von Neumann debiasing.

---

## 🔬 Statistical Analysis Battery Details

| Statistical Test | Null Hypothesis ($H_0$) | Test Statistic / Equation | Decision Rule ($\alpha = 0.05$) |
| :--- | :--- | :--- | :--- |
| **Chi-Square ($\chi^2$) Goodness-of-Fit** | Frequencies conform to discrete uniform distribution ($P(0)=P(1)=0.5$). | $\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$ with $df=1$ | Fail to Reject $H_0$ if $p \ge 0.05$ |
| **Wald-Wolfowitz Runs Test** | Sequence transitions are independent Bernoulli trials. | $Z = \frac{R - \mu_R}{\sigma_R}$ | Fail to Reject $H_0$ if $|Z| \le 1.96$ ($p \ge 0.05$) |
| **Frequency (Monobit) Test** | Equal proportion of 0s and 1s (NIST SP 800-22). | $S_{obs} = \frac{\|n_1 - n_0\|}{\sqrt{N}}, \quad p = \text{erfc}(S_{obs}/\sqrt{2})$ | Fail to Reject $H_0$ if $p \ge 0.05$ |
| **Shannon Binary Entropy** | Maximal information entropy (1.0 bit/symbol). | $H(X) = -p_0\log_2(p_0) - p_1\log_2(p_1)$ | Target: $H(X) \ge 0.999$ bits/symbol |
| **Serial Lag-1 Autocorrelation** | Successive bits are uncorrelated (memoryless). | $r_1 = \frac{\sum (x_i - \bar{x})(x_{i+1} - \bar{x})}{\sum (x_i - \bar{x})^2}$ | Target: $\|r_1\| \approx 0.000$ |

---

## 🛡️ Innovation: John von Neumann Hardware Debiasing

Real superconducting quantum computers (transmons) suffer from physical state preparation and measurement (SPAM) asymmetry and $T_1$ relaxation, causing raw hardware outputs to exhibit a slight bias ($P(1) \neq 0.50$).

The **Von Neumann Debiasing Extractor (1951)** processes non-overlapping consecutive pairs $(b_1, b_2)$:
- **`01`** $\to$ Output **`0`**
- **`10`** $\to$ Output **`1`**
- **`00`** or **`11`** $\to$ **Discard**

### Proof of Unbiasedness:
For any independent trials with physical bias $P(1) = p$ and $P(0) = 1 - p$:
$$P(01) = (1 - p)p = p(1 - p) = P(10)$$
$$\implies P(0 \mid \text{output}) = P(1 \mid \text{output}) = 50.0\%$$

The expected extraction yield is:
$$\text{Yield} = 2p(1 - p)$$
For $p = 0.50$, theoretical yield is $50.0\%$. At $p = 0.60$, yield is $48.0\%$. This provably converts a physically noisy quantum bitstream into a mathematically unbiased sequence.

---

## ⚖️ Quantum vs Classical PRNG Comparison

| Metric | Quantum Simulator (Aer) | Classical PRNG (NumPy PCG64) | Physical Quantum QPU |
| :--- | :--- | :--- | :--- |
| **Generation Mechanism** | Unitary gate simulation + sampling | Permuted Congruential Generator algorithm | Superconducting transmon state collapse |
| **Underlying Source** | Simulated quantum statevector | Classical algorithmic recurrence $s_{n+1}=f(s_n)$ | Genuine quantum indeterminism (Born's rule) |
| **Reproducibility** | Repeatable if seed is provided | Fully deterministic with fixed seed | **Fundamentally non-deterministic** |
| **Cryptographic Utility** | Educational / testing model | Non-cryptographic (predictable if state leaks) | True physical entropy source |
| **Hardware Required** | Standard CPU/Laptop | Standard CPU/Laptop | Dilution refrigerator at ~15 mK |

---

## 🏆 Hackathon Judging Criteria Alignment

- **Correct Qiskit QRNG Circuit:** 1-qubit Hadamard superposition circuit verified with text and graphical diagrams.
- **Reliable Scalable Bit Generation:** Supports 1,000, 10,000, and 100,000 bits using batching and individual chronological measurement outcomes via `memory=True`.
- **Appropriate Statistical Tests:** 5-test battery with null hypotheses, test statistics, $p$-values, and honest scientific interpretation.
- **Meaningful Quantum vs Classical Benchmark:** Direct side-by-side comparison with NumPy PCG64, highlighting determinism vs quantum measurement.
- **Clear Visualizations:** Frequency bar chart, probability comparison, 2D raster dispersion matrix, and digital waveform trace in a clean white-and-blue theme.
- **Real IBM Quantum Hardware Mode:** Fully integrated `qiskit-ibm-runtime` execution pathway with secure token handling and graceful error handling.
- **Originality & Bias Analysis:** Implemented John von Neumann hardware debiasing with interactive noise demonstration.
- **Code Quality:** Pure Python and Streamlit, modular functions, robust exception handling, and beginner-friendly documentation.

---

## 📜 References & Citations

1. **Nielsen, M. A., & Chuang, I. L.** (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
2. **Qiskit Development Team** (2024). *Qiskit: An Open-Source Framework for Quantum Computing*. https://qiskit.org/
3. **Qiskit Aer Documentation** (2024). *Quantum Circuit Simulator for Qiskit*. https://qiskit.github.io/qiskit-aer/
4. **Qiskit IBM Runtime Documentation** (2024). *IBM Quantum Runtime Services*. https://docs.quantum.ibm.com/
5. **Rukhin, A., et al.** (2010). *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*. NIST Special Publication 800-22 Rev. 1a.
6. **von Neumann, J.** (1951). *Various techniques used in connection with random digits*. National Bureau of Standards Applied Mathematics Series, 12, 36-38.
7. **Herrero-Collantes, M., & Garcia-Escartin, J. C.** (2017). *Quantum random number generators*. Reviews of Modern Physics, 89(1), 015004.
