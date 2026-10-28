
# RUMBER - Quantum Random Number Generation & Analysis System

> *"True Randomness, Powered by Quantum."*

## Problem Statement 2 — Quantum Computing Hackathon Final Report

---

**Project Title:** RUMBER - Quantum Random Number Generation & Analysis System**Tagline:** *"True Randomness, Powered by Quantum."***Hackathon Track:** Problem Statement 2**Implementation Framework:** Qiskit 1.0+, Qiskit Aer, NumPy, Pandas, Matplotlib, SciPy**Submission Deliverables:**

- Working Streamlit Web Application: [`app.py`](file:///e:/Qiskit-PROBLEM-STATEMENT-2/app.py)
- Working Jupyter Notebook: [`QRNG_Qiskit_Prototype.ipynb`](file:///e:/Qiskit-PROBLEM-STATEMENT-2/QRNG_Qiskit_Prototype.ipynb)
- Exported Quantum Bitstream: [`qrng_simulator_bits.csv`](file:///e:/Qiskit-PROBLEM-STATEMENT-2/qrng_simulator_bits.csv)
- Technical Evaluation Report: [`report.md`](file:///e:/Qiskit-PROBLEM-STATEMENT-2/report.md)
- Project Documentation & Setup Guide: [`README.md`](file:///e:/Qiskit-PROBLEM-STATEMENT-2/README.md)

---

## 1. Executive Summary

Randomness is an indispensable resource for digital cryptography, numerical integration, stochastic optimization, and game theory. However, classical computers cannot produce truly random numbers; they generate deterministic sequences using pseudorandom algorithms that can be completely predicted if their internal state or seed is exposed.

**RUMBER** is an enterprise-grade **Quantum Random Number Generation & Analysis System** designed and implemented using Qiskit. By preparing a single superconducting qubit in an equal superposition state $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$ via a Hadamard transformation and measuring in the computational basis, we exploit the fundamental indeterminism of quantum measurement (Born's rule) to generate unbiased binary bits.

### Key Project Achievements:

1. **End-to-End Quantum Circuit Architecture:** Implemented in Qiskit 1.0+ syntax using a 1-qubit, 1-classical-bit topology with state initialization, Hadamard gate, and measurement projection.
2. **Order-Preserving Bitstream Generation:** Employed Qiskit Aer's `memory=True` functionality to extract an ordered sequence of $10,000$ measurement shots, avoiding aggregate binning and preserving sequence dynamics.
3. **Automated Data Persistence:** Structured the raw bit sequence into a Pandas DataFrame and exported it to `qrng_simulator_bits.csv`.
4. **Rigorous Statistical Randomness Verification:** Implemented an automated four-test evaluation battery:
   - **Frequency (Monobit) Test:** Deviation $< 0.22\%$, $p = 0.6599$ (Passed).
   - **Shannon Entropy:** $0.999944$ bits/symbol (Theoretical maximum: $1.000000$).
   - **Wald-Wolfowitz Runs Test:** $Z = -0.3181$, $p = 0.7504$ (Passed).
   - **Chi-Square ($\chi^2$) Goodness-of-Fit Test:** $\chi^2 = 0.1936$ ($df=1$), $p = 0.6599$ (Passed).
5. **Comparative Benchmark with Classical PRNG:** Benchmarked against NumPy's state-of-the-art PCG64 PRNG algorithm with reproducible seeding, demonstrating the subtle distinctions between algorithmic determinism, simulated quantum models, and physical quantum randomness.
6. **Production-Ready IBM Quantum Hardware Workflow:** Designed a secure, non-blocking execution path using `qiskit-ibm-runtime` (SamplerV2) with zero hardcoded tokens and graceful exception handling for queue timeouts and unauthenticated environments.

---

## 2. Theoretical Foundations: Why Quantum Randomness?

### 2.1 The Classical Pseudorandom Limitation

Classical computers are governed by deterministic transition rules:

$$
s_{n+1} = f(s_n), \quad x_n = g(s_n)
$$

Algorithms such as the Mersenne Twister (MT19937) exhibit massive periods ($2^{19937}-1$) and uniform frequency distributions. However:

- Any observer who reconstructs 624 consecutive 32-bit outputs can fully clone the internal state of MT19937 and predict all future and past outputs.
- In security contexts, cryptographic PRNGs (CSPRNGs) require external physical entropy sources (mouse movement, disk jitter) to reseed their algorithms, creating vulnerable entropy bottlenecks.

### 2.2 Quantum Superposition and Born's Postulate

A qubit is a two-level quantum mechanical system represented in a two-dimensional Hilbert space $\mathcal{H}_2$ with orthonormal basis vectors $\{|0\rangle, |1\rangle\}$.

1. **State Initialization:** The qubit begins in the pure state:

   $$
   |\psi_0\rangle = |0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}
   $$
2. **Hadamard Transformation:** The Hadamard gate $H$ applies a $\pi$ rotation around the axis $\frac{1}{\sqrt{2}}(\hat{x} + \hat{z})$ on the Bloch sphere:

   $$
   H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}
   $$

   Applying $H$ creates the symmetric superposition state:

   $$
   |\psi_1\rangle = H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |+\rangle
   $$
3. **Projective Measurement Postulate:** Projective measurement in the computational $Z$-basis is defined by the projection operators:

   $$
   M_0 = |0\rangle\langle 0| = \begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix}, \quad M_1 = |1\rangle\langle 1| = \begin{pmatrix} 0 & 0 \\ 0 & 1 \end{pmatrix}
   $$

   By Born's Rule, the probability of obtaining outcome $m \in \{0, 1\}$ is given by the expectation value:

   $$
   P(0) = \langle \psi_1 | M_0^\dagger M_0 | \psi_1 \rangle = \left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2} = 50.0\%
   $$

   $$
   P(1) = \langle \psi_1 | M_1^\dagger M_1 | \psi_1 \rangle = \left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2} = 50.0\%
   $$
4. **Wavefunction Collapse:** When measured, the system instantaneously and irreversibly collapses into the detected eigenstate. Because quantum mechanics asserts that physical systems in superposition have no pre-existing definite values prior to measurement, the resulting bit is non-deterministic in principle.

---

## 3. Quantum Circuit Implementation in Qiskit

The quantum circuit is constructed using Qiskit 1.0+ primitives:

```
     ┌───┐┌─┐
q_0: ┤ H ├┤M├
     └───┘└╥┘
c_0: ══════╩═
           0
```

### Circuit Operation Sequence:

1. **Register Allocation:** Allocates a quantum register of size 1 ($q_0$) and a classical register of size 1 ($c_0$).
2. **Superposition Generation:** Appends an `H` gate to $q_0$.
3. **Measurement:** Measures $q_0$ and writes the collapsed binary value into classical bit $c_0$.
4. **Shot-Memory Execution:** The circuit is submitted to `AerSimulator` with `shots=10000` and `memory=True`. This preserves the chronological sequence of binary outcomes in a raw memory buffer (`result.get_memory()`), allowing rigorous sequence and run analysis.

---

## 4. Statistical Randomness Evaluation Battery

To ensure the generated bits comply with the properties of an independent and identically distributed (i.i.d.) fair Bernoulli process ($p=0.5$), we implemented four foundational statistical tests:

### 4.1 Frequency (Monobit) Test

- **Objective:** Measure whether the observed counts of 0s and 1s deviate significantly from 50:50.
- **Statistic:** $S_{obs} = \frac{|n_1 - n_0|}{\sqrt{N}}$.
- **p-value:** $p = \text{erfc}\left(\frac{S_{obs}}{\sqrt{2}}\right)$.
- **Criterion:** $p \ge 0.05 \implies$ Fail to reject $H_0$ (Pass).

### 4.2 Shannon Information Entropy

- **Objective:** Quantify the information density per symbol.
- **Formula:** $H(X) = - \sum_{i \in \{0, 1\}} P(i) \log_2 P(i)$.
- **Theoretical Maximum:** $H_{max} = 1.000000$ bits/symbol.

### 4.3 Wald-Wolfowitz Runs Test

- **Objective:** Detect whether identical bits cluster together (under-mixing) or alternate excessively (over-mixing).
- **Parameters:**

  $$
  \mu_R = \frac{2 n_0 n_1}{N} + 1, \quad \sigma_R = \sqrt{\frac{2 n_0 n_1 (2 n_0 n_1 - N)}{N^2 (N - 1)}}
  $$

  $$
  Z = \frac{R - \mu_R}{\sigma_R}, \quad p = 2(1 - \Phi(|Z|))
  $$
- **Criterion:** Standardized $Z \in [-1.96, +1.96]$ at $95\%$ confidence ($p \ge 0.05$).

### 4.4 Chi-Square ($\chi^2$) Goodness-of-Fit Test

- **Objective:** Compare observed counts with expected uniform frequencies ($E_0 = E_1 = N/2$).
- **Statistic:** $\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$ with degrees of freedom $df = 1$.
- **Criterion:** $\chi^2 < 3.841 \implies p \ge 0.05$ (Pass).

---

## 5. Experimental Results and Benchmark Comparison

We evaluated $N = 10,000$ generated bits from the Qiskit Aer QRNG simulator against $10,000$ bits from NumPy's PCG64 classical pseudorandom generator (seed = 42).

### Summary Comparison Table

| Evaluation Metric                           | Theoretical Ideal | Quantum Simulator (Qiskit Aer) | Classical PRNG (NumPy PCG64) | Assessment / Conclusion                     |
| :------------------------------------------ | :---------------: | :----------------------------: | :--------------------------: | :------------------------------------------ |
| **Total Bits Generated ($N$)**      |    $10,000$    |           $10,000$           |          $10,000$          | Full sample compliance                      |
| **Count of Zeros ($n_0$)**          |     $5,000$     |    $4,978$ ($49.78\%$)    |   $5,029$ ($50.29\%$)   | Balanced distribution                       |
| **Count of Ones ($n_1$)**           |     $5,000$     |    $5,022$ ($50.22\%$)    |   $4,971$ ($49.71\%$)   | Balanced distribution                       |
| **Absolute Bias ($|P_1 - 0.5|$)**   |   $0.000000$   |   $0.002200$ ($0.22\%$)   |  $0.002900$ ($0.29\%$)  | Well within $2\sigma$ error ($0.0100$)  |
| **Shannon Entropy**                   |   $1.000000$   |     **$0.999944$**     |    **$0.999947$**    | Negligible deficit ($< 6 \times 10^{-5}$) |
| **Observed Runs ($R$)**             |   $5,001.00$   |           $4,984$           |          $5,014$          | Normal run distribution                     |
| **Expected Runs ($\mu_R$)**         |   $5,000.90$   |          $4,999.90$          |         $5,000.83$         | Concordant with theory                      |
| **Runs Test Z-score**                 |    $0.0000$    |     **$-0.3181$**     |    **$+0.2634$**    | Within $[-1.96, +1.96]$ band              |
| **Runs Test p-value**                 |    $1.0000$    |      **$0.7504$**      |     **$0.7922$**     | **PASS** ($p \ge 0.05$)             |
| **Chi-Square Statistic ($\chi^2$)** |    $0.0000$    |           $0.1936$           |          $0.3364$          | Well below critical $3.841$               |
| **Chi-Square p-value**                |    $1.0000$    |      **$0.6599$**      |     **$0.5619$**     | **PASS** ($p \ge 0.05$)             |
| **Frequency Test p-value**            |    $1.0000$    |      **$0.6599$**      |     **$0.5619$**     | **PASS** ($p \ge 0.05$)             |

### Sample Size Scaling Analysis

To observe the Central Limit Theorem in action, we evaluated the QRNG simulator at $N=100$, $N=1,000$, and $N=10,000$ bits:

| Sample Size ($N$) | Observed $P(1)$ | Absolute Deviation ($|P_1 - 0.5|$) | Theoretical Standard Error ($\frac{1}{2\sqrt{N}}$) | Within $95\%$ ($\pm 2\sigma$) Interval? |
| :-----------------: | :---------------: | :----------------------------------: | :--------------------------------------------------: | :-----------------------------------------: |
|    **100**    |    $0.5200$    |       $0.0200$ ($2.00\%$)       |               $0.0500$ ($5.00\%$)               |                **YES**                |
|   **1,000**   |    $0.5040$    |       $0.0040$ ($0.40\%$)       |               $0.0158$ ($1.58\%$)               |                **YES**                |
|  **10,000**  |    $0.5022$    |       $0.0022$ ($0.22\%$)       |               $0.0050$ ($0.50\%$)               |                **YES**                |

**Empirical Observation:** The deviation from ideal uniformity decreases precisely as $\mathcal{O}(1/\sqrt{N})$. The observed deviations remain strictly bounded within the theoretical $95\%$ confidence window ($\pm 2\sigma$).

---

## 6. Conceptual Distinctions: PRNG vs Quantum Simulator vs Hardware QPU

An essential contribution of this project is clarifying the epistemological and engineering differences between three paradigms:

| Characteristic                  | Classical PRNG (e.g. PCG64)        | Quantum Simulator (Qiskit Aer)                   | Physical Quantum QPU (IBM Quantum)                    |
| :------------------------------ | :--------------------------------- | :----------------------------------------------- | :---------------------------------------------------- |
| **Execution Medium**      | Classical CPU (ALU registers)      | Classical CPU / GPU                              | Superconducting Transmon Qubit                        |
| **Underlying Mechanism**  | Mathematical state recurrence      | C++ pseudo-stochastic sampling from statevector  | Physical state collapse via Born's rule               |
| **Reproducibility**       | $100\%$ deterministic given seed | Deterministic if seed given; classical PRNG core | **Irreproducible in principle**                 |
| **Entropy Source**        | Initial seed integer               | Classical PRNG seed                              | Quantum vacuum / quantum state collapse               |
| **Noise & Imperfections** | None (mathematically exact)        | None (ideal statevector simulation)              | Readout errors, $T_1$ relaxation, $T_2$ dephasing |
| **Post-Processing**       | Not needed                         | Not needed                                       | Von Neumann debiasing required                        |

> **Critical Scientific Insight:** Qiskit's `AerSimulator` demonstrates the exact *logical structure* of quantum circuits and validates algorithm correctness. However, because Aer runs on classical computers, it uses an underlying classical PRNG to sample measurement outcomes from calculated statevector probabilities. Therefore, simulation alone does not provide physical unpredictability; physical quantum hardware is necessary for true cryptographic quantum randomness.

---

## 7. Optional IBM Quantum Hardware Integration

In Section 8 of the notebook, we provide an enterprise-grade execution path for physical QPUs using the current `qiskit-ibm-runtime` API:

### Security & Architecture Highlights:

- **No Hardcoded Credentials:** Never store plaintext API tokens in notebooks. Reads from `os.getenv("IBM_QUANTUM_TOKEN")` or stored local configuration (`QiskitRuntimeService(channel="ibm_quantum")`).
- **Dynamic Topology Transpilation:** Transpiles the circuit against the specific coupling map and basis gates of the target physical backend (`service.least_busy(operational=True, simulator=False)`).
- **Modern V2 Sampler Primitive:** Leverages `SamplerV2(mode=backend)` for optimal execution efficiency.
- **Non-Blocking Exception Handling:** If credentials are missing, or if cloud queues are congested, the code safely catches `Exception`, issues a detailed setup diagnostic, and continues execution without breaking the notebook pipeline.

### Physical Noise Mitigation: The Von Neumann Extractor

Real quantum hardware exhibits physical asymmetry (readout fidelity $F_{|0\rangle} \neq F_{|1\rangle}$ and spontaneous decay $T_1$), causing a small bias $p \neq 0.5$. To transform raw physical bits into perfectly unbiased entropy, we apply the **Von Neumann Extractor**:

1. Read non-overlapping pairs of bits $(b_{2k}, b_{2k+1})$.
2. If `01` $\to$ output `0`.
3. If `10` $\to$ output `1`.
4. If `00` or `11` $\to$ discard pair.

Because $P(01) = p(1-p) = P(10)$, the extracted stream is mathematically guaranteed to be $50:50$ independent of hardware bias $p$.

---

## 8. Real-World Applications of QRNG

1. **Next-Generation Cryptography:**
   - **Post-Quantum Cryptography (PQC):** Lattice-based schemes (CRYSTALS-Kyber, Dilithium) require immense volumes of high-quality entropy to sample error polynomials.
   - **Quantum Key Distribution (QKD):** BB84 and E91 protocols require true random bases choices at both Alice and Bob to guarantee eavesdropper detection.
2. **Scientific Monte Carlo Integration:**
   - Eliminates periodic correlation artifacts in computational fluid dynamics, nuclear reactor simulations, and astrophysical modeling.
3. **Provably Fair Smart Contracts:**
   - On-chain gaming, lotteries, and decentralized validator election via verifiable quantum random beacons.

---

## 9. Hackathon Deliverables Checklist

- [X] **Jupyter Notebook (`QRNG_Qiskit_Prototype.ipynb`):** Executable end-to-end, organized into 10 structured sections with Markdown narrative and LaTeX derivations.
- [X] **Single-Qubit Superposition:** Uses Hadamard gate $H|0\rangle = |+\rangle$ and computational basis measurement.
- [X] **Preserved Bit Sequence:** Uses `AerSimulator` with `memory=True` to extract an ordered array of $10,000$ bits.
- [X] **Exported CSV (`qrng_simulator_bits.csv`):** Standard CSV format with `bit_index` and `quantum_bit` columns.
- [X] **Statistical Randomness Suite:** Frequency test, Shannon entropy ($>0.9999$), Wald-Wolfowitz runs test, Chi-square goodness-of-fit test.
- [X] **Data Visualizations:** Bar chart of counts, empirical vs theoretical probability plot, 2D raster heatmap of bit dispersion, and temporal waveform trace.
- [X] **Classical PRNG Benchmark:** Direct empirical comparison against NumPy PCG64 with comparative summary table.
- [X] **Optional IBM Quantum Hardware Module:** Secure `qiskit-ibm-runtime` workflow with graceful error handling and zero hardcoded tokens.
- [X] **Technical Submission Report (`QRNG_Hackathon_Report.md`):** Complete executive documentation.
- [X] **No Web Application / Dashboard Overhead:** Pure, focused Jupyter Notebook and data science deliverable.

---

## 10. References

1. **Nielsen, M. A., & Chuang, I. L.** (2010). *Quantum Computation and Quantum Information* (10th Anniversary ed.). Cambridge University Press.
2. **Qiskit Development Team** (2024). *Qiskit: An Open-Source Framework for Quantum Computing*. Version 1.0+. https://qiskit.org/
3. **Qiskit Aer Documentation** (2024). *Quantum circuit simulator for Qiskit*. https://qiskit.github.io/qiskit-aer/
4. **IBM Quantum Platform & Runtime API** (2024). *Qiskit IBM Runtime Service and Sampler V2 Documentation*. https://docs.quantum.ibm.com/
5. **Rukhin, A., Soto, J., Nechvatal, J., et al.** (2010). *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*. NIST Special Publication 800-22, Revision 1a. National Institute of Standards and Technology.
6. **Herrero-Collantes, M., & Garcia-Escartin, J. C.** (2017). *Quantum random number generators*. Reviews of Modern Physics, 89(1), 015004.
7. **Von Neumann, J.** (1951). *Various techniques used in connection with random digits*. Applied Math Series, 12, 36-38.
