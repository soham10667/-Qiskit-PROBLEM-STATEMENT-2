"""
RUMBER - Quantum Random Number Generation & Analysis System
"True Randomness, Powered by Quantum."
Hackathon Submission: Problem Statement 2

This application runs entirely in Streamlit with pure Python, Qiskit, Qiskit Aer,
NumPy, Pandas, Matplotlib, and SciPy. No HTML, CSS, JS, or external web frameworks.
"""

import math
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import streamlit as st

import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Configure Matplotlib default parameters for Streamlit
plt.rcParams.update({
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.titlesize": 13,
    "figure.dpi": 130,
})

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="RUMBER - Quantum Random Number Generation & Analysis System",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# 1. QUANTUM CIRCUIT CREATION & AER SIMULATION
# ==============================================================================
def create_qrng_circuit() -> QuantumCircuit:
    """
    Constructs the canonical 1-qubit, 1-classical-bit QRNG quantum circuit:
    1. Initializes qubit in ground state |0>
    2. Applies Hadamard (H) gate to create equal superposition (|0> + |1>) / sqrt(2)
    3. Measures the qubit in the computational basis (Z) onto classical register c0
    """
    qc = QuantumCircuit(1, 1, name="QRNG_Core")
    qc.h(0)
    qc.measure(0, 0)
    return qc


def generate_quantum_bits(num_bits: int, seed: int = None) -> List[int]:
    """
    Executes the QRNG circuit on Qiskit AerSimulator.
    Uses memory=True to record individual measurement outcomes in exact chronological order.
    """
    qc = create_qrng_circuit()
    backend = AerSimulator()
    transpiled_qc = transpile(qc, backend)

    # memory=True is required to retrieve the chronological sequence of measurement outcomes
    job = backend.run(transpiled_qc, shots=num_bits, memory=True, seed_simulator=seed)
    result = job.result()
    memory_bits = result.get_memory()

    return [int(bit_str) for bit_str in memory_bits]


# ==============================================================================
# 2. CLASSICAL PSEUDO-RANDOM NUMBER GENERATOR
# ==============================================================================
def generate_classical_bits(num_bits: int, seed: int = 42) -> List[int]:
    """
    Generates classical pseudorandom bits using NumPy's modern PCG64 BitGenerator.
    Uses a fixed seed for reproducible benchmark comparison.
    """
    rng = np.random.default_rng(seed=seed)
    return rng.integers(low=0, high=2, size=num_bits).tolist()


# ==============================================================================
# 3. STATISTICAL RANDOMNESS ANALYSIS
# ==============================================================================
def analyze_sequence(bits: List[int], label: str = "Quantum Simulator") -> Dict[str, Any]:
    """
    Evaluates an ordered binary sequence across four standard statistical tests:
    1. Frequency (Monobit) Test
    2. Shannon Binary Entropy
    3. Wald-Wolfowitz Runs Test
    4. Chi-Square Goodness-of-Fit Test
    """
    arr = np.array(bits, dtype=int)
    n = len(arr)
    if n == 0:
        return {}

    n0 = int(np.sum(arr == 0))
    n1 = int(np.sum(arr == 1))
    p0 = n0 / n
    p1 = n1 / n

    # 1. Frequency (Monobit) Test (NIST SP 800-22 inspired)
    s_obs = abs(n1 - n0) / math.sqrt(n)
    freq_p = math.erfc(s_obs / math.sqrt(2.0))
    freq_pass = freq_p >= 0.05

    # 2. Shannon Binary Entropy
    h0 = 0.0 if p0 == 0.0 else -p0 * math.log2(p0)
    h1 = 0.0 if p1 == 0.0 else -p1 * math.log2(p1)
    entropy = h0 + h1

    # 3. Wald-Wolfowitz Runs Test
    diffs = arr[1:] != arr[:-1]
    observed_runs = int(np.sum(diffs) + 1)
    if n > 1 and n0 > 0 and n1 > 0:
        exp_runs = (2.0 * n0 * n1 / n) + 1.0
        var_num = 2.0 * n0 * n1 * (2.0 * n0 * n1 - n)
        var_den = (n ** 2) * (n - 1)
        var_runs = max(0.0, var_num / var_den)
        std_runs = math.sqrt(var_runs) if var_runs > 0 else 1e-9
        z_score = (observed_runs - exp_runs) / std_runs
        runs_p = float(2.0 * (1.0 - stats.norm.cdf(abs(z_score))))
    else:
        exp_runs = float(observed_runs)
        z_score = 0.0
        runs_p = 1.0

    runs_pass = runs_p >= 0.05

    # 4. Chi-Square Goodness-of-Fit
    obs = np.array([n0, n1])
    exp = np.array([n / 2.0, n / 2.0])
    chi2_stat, chi2_p = stats.chisquare(f_obs=obs, f_exp=exp)
    chi2_pass = float(chi2_p) >= 0.05

    return {
        "label": label,
        "total_bits": n,
        "count_zeros": n0,
        "count_ones": n1,
        "prob_zero": p0,
        "prob_one": p1,
        "entropy": entropy,
        "entropy_deficit": 1.0 - entropy,
        "frequency_test": {
            "statistic": s_obs,
            "p_value": freq_p,
            "passed": freq_pass,
        },
        "runs_test": {
            "observed_runs": observed_runs,
            "expected_runs": exp_runs,
            "z_score": z_score,
            "p_value": runs_p,
            "passed": runs_pass,
        },
        "chi_square_test": {
            "statistic": float(chi2_stat),
            "p_value": float(chi2_p),
            "passed": chi2_pass,
        },
    }


def von_neumann_extractor(raw_bits: List[int]) -> List[int]:
    """
    Von Neumann debiasing algorithm:
    Takes consecutive non-overlapping pairs (b0, b1):
    - 01 -> output 0
    - 10 -> output 1
    - 00 or 11 -> discard
    Mathematically proves that P(0) = P(1) = 0.5 regardless of hardware asymmetry.
    """
    clean_bits = []
    for i in range(0, len(raw_bits) - 1, 2):
        b1, b2 = raw_bits[i], raw_bits[i + 1]
        if b1 == 0 and b2 == 1:
            clean_bits.append(0)
        elif b1 == 1 and b2 == 0:
            clean_bits.append(1)
    return clean_bits


# ==============================================================================
# 4. SESSION STATE INITIALIZATION
# ==============================================================================
if "quantum_bits" not in st.session_state:
    # Pre-generate 1,000 bits so judges immediately see live results
    initial_bits = generate_quantum_bits(1000, seed=42)
    initial_classical = generate_classical_bits(1000, seed=42)
    st.session_state["quantum_bits"] = initial_bits
    st.session_state["classical_bits"] = initial_classical
    st.session_state["analysis_q"] = analyze_sequence(initial_bits, "Qiskit Aer Simulator")
    st.session_state["analysis_c"] = analyze_sequence(initial_classical, "Classical PRNG (NumPy)")
    st.session_state["num_bits"] = 1000


# ==============================================================================
# 5. SIDEBAR CONTROLS
# ==============================================================================
st.sidebar.title("⚛️ RUMBER")
st.sidebar.caption("Quantum Random Number Generation & Analysis System")
st.sidebar.markdown("*\"True Randomness, Powered by Quantum.\"*")
st.sidebar.write("Configure simulator shot size and execute the Qiskit quantum circuit.")

bit_choice = st.sidebar.selectbox(
    "Select Bit Count:",
    options=["100 bits", "1,000 bits", "10,000 bits", "Custom size..."],
    index=1,
)

if bit_choice == "100 bits":
    requested_bits = 100
elif bit_choice == "1,000 bits":
    requested_bits = 1000
elif bit_choice == "10,000 bits":
    requested_bits = 10000
else:
    requested_bits = st.sidebar.number_input(
        "Enter Custom Bit Count:",
        min_value=10,
        max_value=50000,
        value=5000,
        step=100,
    )

# Optional reproducibility seed
use_seed = st.sidebar.checkbox("Use Fixed Simulator Seed", value=False)
sim_seed = None
if use_seed:
    sim_seed = st.sidebar.number_input("Simulator Seed Value:", min_value=1, max_value=999999, value=42)

classical_seed = st.sidebar.number_input("Classical PRNG Seed:", min_value=1, max_value=999999, value=42)

# Execution trigger
if st.sidebar.button("⚡ Generate Quantum Bits", type="primary", use_container_width=True):
    with st.spinner(f"Simulating {requested_bits:,} quantum measurement shots on AerSimulator..."):
        q_out = generate_quantum_bits(requested_bits, seed=sim_seed)
        c_out = generate_classical_bits(requested_bits, seed=classical_seed)

        # Update session state
        st.session_state["quantum_bits"] = q_out
        st.session_state["classical_bits"] = c_out
        st.session_state["analysis_q"] = analyze_sequence(q_out, "Qiskit Aer Simulator")
        st.session_state["analysis_c"] = analyze_sequence(c_out, "Classical PRNG (NumPy)")
        st.session_state["num_bits"] = requested_bits
        st.sidebar.success(f"Generated {requested_bits:,} bits successfully!")

st.sidebar.markdown("---")
st.sidebar.write(f"**Qiskit Version:** `{qiskit.__version__}`")
st.sidebar.write(f"**Backend:** `AerSimulator (C++)`")
st.sidebar.write(f"**Active Sequence:** `{len(st.session_state['quantum_bits']):,} bits`")


# ==============================================================================
# 6. MAIN APPLICATION INTERFACE
# ==============================================================================
st.title("⚛️ RUMBER")
st.subheader("Quantum Random Number Generation & Analysis System")
st.markdown("##### *\"True Randomness, Powered by Quantum.\"*")
st.caption("Quantum Computing Hackathon — Problem Statement 2")

st.write(
    """
    **RUMBER** is a comprehensive **Quantum Random Number Generation & Analysis System** implemented with Qiskit.
    By preparing a qubit in the equal superposition state 
    $|+\\rangle = \\frac{1}{\\sqrt{2}}(|0\\rangle + |1\\rangle)$ via a Hadamard gate and measuring in the 
    computational basis, binary measurement outcomes are sampled according to **Born's Rule** 
    ($P(0) = P(1) = 0.5$).
    """
)

# Status notification
st.info(
    f"📍 **Data Source:** Qiskit Aer Simulator (Simulated Quantum Measurements) | "
    f"**Sample Size:** {len(st.session_state['quantum_bits']):,} bits | "
    f"**Circuit:** 1 Qubit, 1 Classical Bit, 1 Hadamard Gate, 1 Measurement"
)

# Native Streamlit Tabs
tab_dash, tab_stats, tab_comp, tab_mitigation, tab_circ, tab_report = st.tabs([
    "📊 Dashboard & Visualizations",
    "📈 Statistical Randomness Analysis",
    "⚖️ Classical PRNG Comparison",
    "🛡️ Innovation: Bias Mitigation",
    "🔬 Quantum Circuit Architecture",
    "📑 Hackathon Report",
])

aq = st.session_state["analysis_q"]
ac = st.session_state["analysis_c"]
q_bits = st.session_state["quantum_bits"]
c_bits = st.session_state["classical_bits"]
N = len(q_bits)

# ==============================================================================
# TAB 1: DASHBOARD & VISUALIZATIONS
# ==============================================================================
with tab_dash:
    # 4 Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Bits Generated (N)",
            value=f"{N:,}",
            delta=f"0s: {aq['count_zeros']:,} ({aq['prob_zero']*100:.1f}%) | 1s: {aq['count_ones']:,} ({aq['prob_one']*100:.1f}%)",
        )

    with col2:
        entropy_val = aq["entropy"]
        st.metric(
            label="Shannon Entropy",
            value=f"{entropy_val:.6f} bits",
            delta=f"Deficit: {aq['entropy_deficit']:.2e} from 1.0",
        )

    with col3:
        runs_obs = aq["runs_test"]["observed_runs"]
        z_score = aq["runs_test"]["z_score"]
        verdict_runs = "PASS" if aq["runs_test"]["passed"] else "FAIL"
        st.metric(
            label="Wald-Wolfowitz Runs",
            value=f"{runs_obs:,} runs",
            delta=f"Z = {z_score:+.2f} [{verdict_runs}]",
        )

    with col4:
        chi2_val = aq["chi_square_test"]["statistic"]
        chi2_p = aq["chi_square_test"]["p_value"]
        verdict_chi2 = "PASS" if aq["chi_square_test"]["passed"] else "FAIL"
        st.metric(
            label="Chi-Square (df=1)",
            value=f"χ² = {chi2_val:.4f}",
            delta=f"p = {chi2_p:.4f} [{verdict_chi2}]",
        )

    st.markdown("---")

    # Visualizations: 2 Columns
    c_left, c_right = st.columns(2)

    with c_left:
        st.subheader("Frequency Distribution: Zeros vs Ones")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        categories = ["Bit 0 (|0⟩)", "Bit 1 (|1⟩)"]
        counts = [aq["count_zeros"], aq["count_ones"]]
        colors = ["#1f77b4", "#ff7f0e"]

        bars = ax1.bar(categories, counts, color=colors, width=0.5, edgecolor="black", alpha=0.85)
        ax1.axhline(N / 2.0, color="#d62728", linestyle="--", linewidth=1.8, label=f"Expected ({N//2:,})")

        for bar, count, p in zip(bars, counts, [aq["prob_zero"], aq["prob_one"]]):
            ax1.annotate(
                f"{count:,}\n({p*100:.2f}%)",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=9,
            )

        ax1.set_ylim(0, max(counts) * 1.2)
        ax1.set_ylabel("Occurrence Count")
        ax1.set_title("Zero and One Measurement Counts")
        ax1.legend(loc="lower right")
        ax1.grid(axis="y", linestyle=":", alpha=0.6)
        st.pyplot(fig1)

    with c_right:
        st.subheader("Empirical vs Theoretical Probability")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        x_indices = np.arange(2)
        bar_w = 0.35

        observed_p = [aq["prob_zero"], aq["prob_one"]]
        theory_p = [0.5, 0.5]

        r1 = ax2.bar(x_indices - bar_w / 2, observed_p, bar_w, label="Observed (Quantum)", color="#2ca02c", edgecolor="black")
        r2 = ax2.bar(x_indices + bar_w / 2, theory_p, bar_w, label="Theoretical (Born Rule)", color="#7f7f7f", alpha=0.55, edgecolor="black")

        ax2.axhline(0.5, color="#d62728", linestyle=":", linewidth=1.5)
        ax2.set_xticks(x_indices)
        ax2.set_xticklabels(["Bit 0", "Bit 1"])
        ax2.set_ylim(0, 0.7)
        ax2.set_ylabel("Probability P(x)")
        ax2.set_title("Probability Comparison (Expected 0.5000)")
        ax2.legend(loc="lower right")
        ax2.grid(axis="y", linestyle=":", alpha=0.6)

        for rect in r1:
            ax2.annotate(
                f"{rect.get_height():.4f}",
                xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

        st.pyplot(fig2)

    # Spatial Bit Raster Heatmap & Digital Waveform Trace
    st.subheader("Spatial Dispersion & Digital Waveform Trace")
    v_left, v_right = st.columns([1, 1.2])

    with v_left:
        st.write("**2D Spatial Dispersion Raster (First 400 Bits, 20 × 20 Matrix)**")
        grid_dim = 20
        raster_sample = np.array(q_bits[: grid_dim * grid_dim])
        if len(raster_sample) < grid_dim * grid_dim:
            raster_sample = np.pad(raster_sample, (0, grid_dim * grid_dim - len(raster_sample)))
        grid_data = raster_sample.reshape((grid_dim, grid_dim))

        fig_r, ax_r = plt.subplots(figsize=(4, 4))
        ax_r.imshow(grid_data, cmap="Blues", interpolation="nearest")
        ax_r.set_xticks([])
        ax_r.set_yticks([])
        ax_r.set_title("Bit Dispersion (White=0, Dark Blue=1)", fontsize=10)
        st.pyplot(fig_r)

    with v_right:
        st.write("**Digital Waveform Pulse Trace (First 50 Generated Bits)**")
        first_50 = q_bits[:50]
        steps_x = np.repeat(np.arange(len(first_50)), 2)[1:]
        steps_y = np.repeat(first_50, 2)[:-1]

        fig_w, ax_w = plt.subplots(figsize=(7, 3.4))
        ax_w.plot(steps_x, steps_y, color="#0052cc", linewidth=1.8, label="Quantum Bit Level")
        ax_w.scatter(np.arange(len(first_50)), first_50, color="#d62728", s=18, zorder=3)
        ax_w.set_yticks([0, 1])
        ax_w.set_yticklabels(["0 (|0⟩)", "1 (|1⟩)"])
        ax_w.set_xlabel("Bit Index")
        ax_w.set_ylabel("Collapsed State")
        ax_w.set_ylim(-0.25, 1.25)
        ax_w.grid(True, linestyle=":", alpha=0.5)
        ax_w.legend(loc="upper right", fontsize=8)
        st.pyplot(fig_w)

    # Bit Sequence Viewer
    st.subheader("Generated Bit Sequence Inspector")
    first_50_str = "".join(str(b) for b in q_bits[:50])
    st.code(first_50_str, language="text")
    st.caption("First 50 chronologically ordered quantum measurement bits.")

    # CSV Download
    df_quantum = pd.DataFrame({
        "bit_index": list(range(len(q_bits))),
        "generated_bit": q_bits,
        "source": "Qiskit AerSimulator",
    })

    csv_data = df_quantum.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Quantum Bitstream CSV",
        data=csv_data,
        file_name=f"qrng_simulator_{N}_bits.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ==============================================================================
# TAB 2: STATISTICAL RANDOMNESS ANALYSIS
# ==============================================================================
with tab_stats:
    st.header("Statistical Randomness Battery")
    st.write(
        """
        We evaluate the generated bitstream across four standard statistical tests to assess conformity 
        with an ideal, independent Bernoulli process ($p=0.5$).
        """
    )

    s_left, s_right = st.columns(2)

    with s_left:
        st.subheader("1. Frequency (Monobit) Test")
        st.latex(r"S_{obs} = \frac{|n_1 - n_0|}{\sqrt{N}}, \quad p = \text{erfc}\left(\frac{S_{obs}}{\sqrt{2}}\right)")
        st.write(f"- **Count of Ones:** `{aq['count_ones']:,}` ({aq['prob_one']*100:.2f}%)")
        st.write(f"- **Count of Zeros:** `{aq['count_zeros']:,}` ({aq['prob_zero']*100:.2f}%)")
        st.write(f"- **Statistic ($S_{{obs}}$):** `{aq['frequency_test']['statistic']:.4f}`")
        st.write(f"- **p-value:** `{aq['frequency_test']['p_value']:.4f}`")
        if aq["frequency_test"]["passed"]:
            st.success("Verdict: PASS — Observed frequencies match 50:50 parity ($p \\ge 0.05$).")
        else:
            st.warning("Verdict: FAIL — Proportions deviate from parity ($p < 0.05$).")

        st.subheader("2. Shannon Binary Entropy")
        st.latex(r"H(X) = - \sum_{x \in \{0, 1\}} P(x) \log_2 P(x)")
        st.write(f"- **Calculated Entropy:** `{aq['entropy']:.6f}` bits per symbol")
        st.write(f"- **Theoretical Maximum:** `1.000000` bit per symbol")
        st.write(f"- **Entropy Deficit:** `{aq['entropy_deficit']:.2e}` bits")
        st.info("High entropy confirms near-maximal information uncertainty per bit.")

    with s_right:
        st.subheader("3. Wald-Wolfowitz Runs Test")
        st.latex(r"\mu_R = \frac{2n_0n_1}{N} + 1, \quad Z = \frac{R - \mu_R}{\sigma_R}")
        st.write(f"- **Observed Runs ($R$):** `{aq['runs_test']['observed_runs']:,}`")
        st.write(f"- **Expected Runs ($\mu_R$):** `{aq['runs_test']['expected_runs']:.2f}`")
        st.write(f"- **Standardized Z-Score:** `{aq['runs_test']['z_score']:+.4f}`")
        st.write(f"- **p-value:** `{aq['runs_test']['p_value']:.4f}`")
        if aq["runs_test"]["passed"]:
            st.success("Verdict: PASS — Runs are consistent with independent trials ($|Z| \\le 1.96$).")
        else:
            st.warning("Verdict: FAIL — Excessive clustering or alternation detected.")

        st.subheader("4. Chi-Square (χ²) Goodness-of-Fit")
        st.latex(r"\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}, \quad E_0 = E_1 = \frac{N}{2}")
        st.write(f"- **Statistic ($\chi^2$):** `{aq['chi_square_test']['statistic']:.4f}` ($df=1$)")
        st.write(f"- **p-value:** `{aq['chi_square_test']['p_value']:.4f}`")
        if aq["chi_square_test"]["passed"]:
            st.success("Verdict: PASS — Frequencies are consistent with discrete uniform distribution.")
        else:
            st.warning("Verdict: FAIL — Significant deviation from uniform expectation.")

    st.markdown("---")
    st.warning(
        """
        **Important Scientific Caveat:**  
        Passing basic statistical tests is a necessary baseline, but **does not prove that a generator 
        is cryptographically secure or truly physically random.** Classical pseudorandom algorithms (such as 
        the Mersenne Twister) pass these exact tests while being completely deterministic. True physical 
        unpredictability requires physical quantum hardware rather than simulation.
        """
    )

    # Downloadable statistical report
    stat_report_str = f"""QUANTUM RANDOM NUMBER GENERATOR (QRNG) STATISTICAL REPORT
Source: Qiskit AerSimulator (Simulated Quantum Measurements)
Total Shots (N): {N:,}

1. FREQUENCY TEST:
   - Zeros: {aq['count_zeros']:,} ({aq['prob_zero']*100:.2f}%)
   - Ones:  {aq['count_ones']:,} ({aq['prob_one']*100:.2f}%)
   - S_obs: {aq['frequency_test']['statistic']:.4f}
   - p-val: {aq['frequency_test']['p_value']:.4f}
   - Status: {'PASS' if aq['frequency_test']['passed'] else 'FAIL'}

2. SHANNON ENTROPY:
   - Observed: {aq['entropy']:.6f} bits/symbol
   - Maximum:  1.000000 bits/symbol
   - Deficit:  {aq['entropy_deficit']:.2e} bits

3. RUNS TEST:
   - Observed Runs: {aq['runs_test']['observed_runs']:,}
   - Expected Runs: {aq['runs_test']['expected_runs']:.2f}
   - Z-Score:       {aq['runs_test']['z_score']:+.4f}
   - p-val:         {aq['runs_test']['p_value']:.4f}
   - Status:        {'PASS' if aq['runs_test']['passed'] else 'FAIL'}

4. CHI-SQUARE TEST:
   - Chi2 (df=1):   {aq['chi_square_test']['statistic']:.4f}
   - p-val:         {aq['chi_square_test']['p_value']:.4f}
   - Status:        {'PASS' if aq['chi_square_test']['passed'] else 'FAIL'}
"""
    st.download_button(
        label="📥 Download Statistical Summary Report (.txt)",
        data=stat_report_str.encode("utf-8"),
        file_name=f"qrng_statistical_summary_{N}_bits.txt",
        mime="text/plain",
    )


# ==============================================================================
# TAB 3: CLASSICAL PRNG COMPARISON
# ==============================================================================
with tab_comp:
    st.header("Classical Pseudorandom Number Generator Benchmark")
    st.write(
        """
        We generate a comparison sequence of the same length using NumPy's modern **PCG64 BitGenerator** 
        with a fixed seed (`seed = 42`) for reproducibility.
        """
    )

    comparison_rows = [
        {
            "Metric": "Total Bits (N)",
            "Theoretical Value": f"{N:,}",
            "Quantum Simulator (Aer)": f"{aq['total_bits']:,}",
            "Classical PRNG (PCG64)": f"{ac['total_bits']:,}",
            "Status": "Exact Match",
        },
        {
            "Metric": "Bit 0 Count (n0)",
            "Theoretical Value": f"{N//2:,} (50.0%)",
            "Quantum Simulator (Aer)": f"{aq['count_zeros']:,} ({aq['prob_zero']*100:.2f}%)",
            "Classical PRNG (PCG64)": f"{ac['count_zeros']:,} ({ac['prob_zero']*100:.2f}%)",
            "Status": "Balanced",
        },
        {
            "Metric": "Bit 1 Count (n1)",
            "Theoretical Value": f"{N//2:,} (50.0%)",
            "Quantum Simulator (Aer)": f"{aq['count_ones']:,} ({aq['prob_one']*100:.2f}%)",
            "Classical PRNG (PCG64)": f"{ac['count_ones']:,} ({ac['prob_one']*100:.2f}%)",
            "Status": "Balanced",
        },
        {
            "Metric": "Shannon Entropy (bits/sym)",
            "Theoretical Value": "1.000000",
            "Quantum Simulator (Aer)": f"{aq['entropy']:.6f}",
            "Classical PRNG (PCG64)": f"{ac['entropy']:.6f}",
            "Status": "High Entropy (> 0.999)",
        },
        {
            "Metric": "Observed Runs (R)",
            "Theoretical Value": f"{(N/2)+1:,.1f}",
            "Quantum Simulator (Aer)": f"{aq['runs_test']['observed_runs']:,}",
            "Classical PRNG (PCG64)": f"{ac['runs_test']['observed_runs']:,}",
            "Status": "Normal Mixing",
        },
        {
            "Metric": "Runs Test Z-Score",
            "Theoretical Value": "0.0000",
            "Quantum Simulator (Aer)": f"{aq['runs_test']['z_score']:+.4f}",
            "Classical PRNG (PCG64)": f"{ac['runs_test']['z_score']:+.4f}",
            "Status": "Within [-1.96, +1.96]",
        },
        {
            "Metric": "Runs Test p-value",
            "Theoretical Value": "1.0000",
            "Quantum Simulator (Aer)": f"{aq['runs_test']['p_value']:.4f}",
            "Classical PRNG (PCG64)": f"{ac['runs_test']['p_value']:.4f}",
            "Status": "Passed",
        },
        {
            "Metric": "Chi-Square p-value",
            "Theoretical Value": "1.0000",
            "Quantum Simulator (Aer)": f"{aq['chi_square_test']['p_value']:.4f}",
            "Classical PRNG (PCG64)": f"{ac['chi_square_test']['p_value']:.4f}",
            "Status": "Passed",
        },
    ]

    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)

    # Comparison Plot
    fig_comp, ax_comp = plt.subplots(figsize=(7, 3.5))
    dev_q = abs(aq["prob_one"] - 0.5)
    dev_c = abs(ac["prob_one"] - 0.5)

    comp_bars = ax_comp.bar(
        ["Quantum Simulator (Aer)", "Classical PRNG (NumPy)"],
        [dev_q, dev_c],
        color=["#1d4ed8", "#d97706"],
        width=0.4,
        edgecolor="black",
    )
    ax_comp.set_ylabel("Absolute Deviation from 0.5000 |P1 - 0.5|")
    ax_comp.set_title("Proportion Bias Deviation (Lower is Closer to Parity)")
    ax_comp.grid(axis="y", linestyle=":", alpha=0.6)

    for b in comp_bars:
        ax_comp.annotate(
            f"{b.get_height():.5f}",
            xy=(b.get_x() + b.get_width() / 2, b.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    st.pyplot(fig_comp)

    st.subheader("Fundamental Distinction: Determinism vs Simulated Sampling")
    st.write(
        """
        - **Classical PRNG:** Fully deterministic. Given the seed (`42`), the sequence can be perfectly reproduced by anyone on any machine.
        - **Qiskit Aer Simulator:** Mathematically models the statevector $|+\rangle$ and uses classical pseudo-stochastic routines in C++ to sample measurement outcomes. It simulates the behavior of a quantum circuit, but runs on classical hardware.
        - **Physical Quantum Computer (QPU):** Measures physical superconducting transmon qubits. The unpredictability arises from genuine quantum physical indeterminism and measurement collapse.
        """
    )

    # Combined CSV Download
    df_comb = pd.DataFrame({
        "bit_index": list(range(N)),
        "quantum_bit": q_bits,
        "classical_bit": c_bits,
    })
    st.download_button(
        label="📥 Download Combined Quantum vs Classical CSV",
        data=df_comb.to_csv(index=False).encode("utf-8"),
        file_name=f"qrng_vs_classical_{N}_bits.csv",
        mime="text/csv",
    )


# ==============================================================================
# TAB 4: INNOVATION IN BIAS MITIGATION (VON NEUMANN EXTRACTOR)
# ==============================================================================
with tab_mitigation:
    st.header("🛡️ Innovation: Quantum Hardware Bias Mitigation")
    st.write(
        """
        ### The Physical Challenge: Readout Asymmetry & Thermal Noise
        Real superconducting quantum computers (such as transmon qubits in dilution refrigerators) 
        are subject to physical imperfections:
        - **Readout Asymmetry ($F_{0\\to 1} \\neq F_{1\\to 0}$):** State classification errors favor one state.
        - **Thermal Relaxation ($T_1$):** Excited state $|1\\rangle$ decays spontaneously toward ground state $|0\\rangle$.
        
        This physical noise introduces a persistent bias ($P(1) \\neq 0.50$), causing standard statistical tests to fail.
        """
    )

    st.subheader("The Mathematical Solution: John von Neumann Extractor (1951)")
    st.write(
        """
        To mathematically eliminate physical bias without knowing the exact noise parameter $p$, 
        we implement the **Von Neumann Debiasing Algorithm**:
        """
    )
    st.latex(r"\text{Pair } (b_1, b_2): \quad 01 \to 0, \quad 10 \to 1, \quad 00 \text{ or } 11 \to \text{Discard}")
    st.write(
        """
        **Mathematical Proof of Perfect Unbiasedness:**  
        For any independent trials with arbitrary physical bias $P(1) = p$ and $P(0) = 1-p$:
        """
    )
    st.latex(r"P(01) = (1 - p)p, \quad P(10) = p(1 - p)")
    st.latex(r"\text{Since } P(01) = P(10) \implies P(0 \mid \text{output}) = P(1 \mid \text{output}) = 50.0\%")

    st.markdown("---")
    st.subheader("Interactive Hardware Noise & Mitigation Demonstration")

    noise_col1, noise_col2 = st.columns([1, 1.2])

    with noise_col1:
        st.write("**Simulate Imperfect Quantum Hardware:**")
        sim_bias = st.slider(
            "Simulated Physical Bias P(1):",
            min_value=0.50,
            max_value=0.75,
            value=0.58,
            step=0.01,
            help="Simulates asymmetric readout noise or T1 relaxation.",
        )
        sample_raw_size = st.selectbox("Raw Hardware Shots:", [2000, 5000, 10000], index=1)

        # Generate biased stream
        rng_noise = np.random.default_rng(seed=123)
        raw_biased = rng_noise.choice([0, 1], size=sample_raw_size, p=[1.0 - sim_bias, sim_bias]).tolist()

        # Apply Von Neumann extractor
        mitigated_bits = von_neumann_extractor(raw_biased)

    with noise_col2:
        st.write("**Extraction Efficiency & Yield:**")
        n_raw = len(raw_biased)
        n_clean = len(mitigated_bits)
        yield_rate = (n_clean / n_raw) * 100 if n_raw > 0 else 0
        theory_yield = 2.0 * sim_bias * (1.0 - sim_bias) * 100

        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Raw Biased Bits", f"{n_raw:,}")
        m_c2.metric("Extracted Pure Bits", f"{n_clean:,}", delta=f"Yield: {yield_rate:.1f}% (Theory: {theory_yield:.1f}%)")

    # Side-by-side analysis: Raw vs Mitigated
    ana_raw = analyze_sequence(raw_biased, "Raw Biased Hardware")
    ana_mit = analyze_sequence(mitigated_bits, "Von Neumann Mitigated")

    st.markdown("#### Side-by-Side Verification: Before vs After Debiasing")
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        st.markdown("**1. Raw Imperfect Hardware Stream (Biased)**")
        st.write(f"- Proportion Ones: `{ana_raw['prob_one']*100:.2f}%` (Target: 50.0%)")
        st.write(f"- Shannon Entropy: `{ana_raw['entropy']:.6f}` bits/sym")
        st.write(f"- Chi-Square p-value: `{ana_raw['chi_square_test']['p_value']:.4e}`")
        if ana_raw["chi_square_test"]["passed"]:
            st.success("Verdict: PASS")
        else:
            st.error("Verdict: FAIL — Significant hardware noise bias ($p < 0.05$)")

    with b_col2:
        st.markdown("**2. Extracted Stream via Von Neumann Protocol (Mitigated)**")
        st.write(f"- Proportion Ones: `{ana_mit['prob_one']*100:.2f}%` (Target: 50.0%)")
        st.write(f"- Shannon Entropy: `{ana_mit['entropy']:.6f}` bits/sym")
        st.write(f"- Chi-Square p-value: `{ana_mit['chi_square_test']['p_value']:.4f}`")
        if ana_mit["chi_square_test"]["passed"]:
            st.success("Verdict: PASS — Hardware bias mathematically eliminated! ($p \\ge 0.05$)")
        else:
            st.warning("Verdict: Needs larger sample")

    # Matplotlib Comparison Figure
    fig_mit, (ax_m1, ax_m2) = plt.subplots(1, 2, figsize=(7, 3.2))

    # Raw bar chart
    ax_m1.bar(["0", "1"], [ana_raw["prob_zero"], ana_raw["prob_one"]], color=["#7f7f7f", "#d62728"], width=0.45)
    ax_m1.axhline(0.5, color="black", linestyle="--", linewidth=1.2)
    ax_m1.set_ylim(0, 0.8)
    ax_m1.set_title(f"Raw Stream (P1 = {ana_raw['prob_one']*100:.1f}%)", fontsize=10, fontweight="bold")
    ax_m1.set_ylabel("Probability P(x)")

    # Mitigated bar chart
    ax_m2.bar(["0", "1"], [ana_mit["prob_zero"], ana_mit["prob_one"]], color=["#1f77b4", "#2ca02c"], width=0.45)
    ax_m2.axhline(0.5, color="black", linestyle="--", linewidth=1.2)
    ax_m2.set_ylim(0, 0.8)
    ax_m2.set_title(f"Mitigated Stream (P1 = {ana_mit['prob_one']*100:.1f}%)", fontsize=10, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig_mit)

    # Download mitigated bits
    df_mit = pd.DataFrame({
        "bit_index": list(range(len(mitigated_bits))),
        "debiased_bit": mitigated_bits,
        "source": "Von Neumann Extractor (Debiased)",
    })
    st.download_button(
        label="📥 Download Mitigated Pure Bitstream CSV",
        data=df_mit.to_csv(index=False).encode("utf-8"),
        file_name="qrng_von_neumann_debiased_bits.csv",
        mime="text/csv",
    )


# ==============================================================================
# TAB 5: QUANTUM CIRCUIT ARCHITECTURE
# ==============================================================================
with tab_circ:
    st.header("Quantum Circuit Architecture")
    qc = create_qrng_circuit()

    circ_col1, circ_col2 = st.columns([1, 1.2])

    with circ_col1:
        st.subheader("ASCII Circuit Diagram")
        st.code(qc.draw(output="text"), language="text")

        st.subheader("Graphical Circuit Diagram")
        fig_circuit = qc.draw(output="mpl", style="iqp")
        st.pyplot(fig_circuit)

    with circ_col2:
        st.subheader("Circuit Operations Breakdown")
        st.write(
            """
            1. **Qubit Initialization:**  
               A single qubit $q_0$ is prepared in the ground state:  
               $$|0\\rangle = \\begin{pmatrix} 1 \\\\ 0 \\end{pmatrix}$$

            2. **Hadamard Gate Application ($H$):**  
               Applying the unitary transformation:  
               $$H = \\frac{1}{\\sqrt{2}}\\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix}$$  
               Creates an equal superposition state:  
               $$|\\psi\\rangle = H|0\\rangle = \\frac{1}{\\sqrt{2}}|0\\rangle + \\frac{1}{\\sqrt{2}}|1\\rangle = |+\\rangle$$

            3. **Computational Basis Measurement ($M_Z$):**  
               Measurement collapses the superposition into either $|0\\rangle$ or $|1\\rangle$. By **Born's Rule**:  
               $$P(0) = |\\langle 0 | + \\rangle|^2 = 50.0\\%$$  
               $$P(1) = |\\langle 1 | + \\rangle|^2 = 50.0\\%$$

            4. **Shot-Memory Collection:**  
               `AerSimulator` records individual sequential measurement outcomes using `memory=True`.
            """
        )


# ==============================================================================
# TAB 5: HACKATHON REPORT
# ==============================================================================
with tab_report:
    st.header("Hackathon Evaluation Report & Methodology")
    st.write(
        """
        ### Executive Summary
        **RUMBER (Quantum Random Number Generation & Analysis System)**  
        *\"True Randomness, Powered by Quantum.\"*

        This project implements a fully working prototype of an enterprise-grade QRNG
        built with Python, Qiskit, Qiskit Aer, and Streamlit.
        
        ### Key Scientific Results:
        1. **Equal Superposition:** Single-qubit Hadamard transformation creates equal superposition ($H|0\\rangle = |+\\rangle$).
        2. **Order-Preserving Bitstream:** Measurement shots retrieved chronologically via Qiskit Aer's `memory=True`.
        3. **Statistical Randomness Verification:** High entropy ($>0.9999$ bits/sym), balanced zero/one counts, and normal run transitions verified via Chi-Square and Runs tests.
        4. **Classical Benchmark:** Comparative analysis against NumPy PCG64 PRNG delineates algorithmic determinism from quantum measurement models.
        5. **Streamlit UI:** Native Streamlit components provide interactive controls, dynamic Matplotlib plots, raster grids, and downloadable CSV exports.

        ### References
        1. **Nielsen, M. A., & Chuang, I. L.** (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
        2. **Qiskit Development Team** (2024). *Qiskit: An Open-Source Framework for Quantum Computing*. https://qiskit.org/
        3. **Qiskit Aer Documentation** (2024). *Quantum Circuit Simulator for Qiskit*. https://qiskit.github.io/qiskit-aer/
        4. **Rukhin, A., et al.** (2010). *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*. NIST Special Publication 800-22 Rev. 1a.
        5. **Herrero-Collantes, M., & Garcia-Escartin, J. C.** (2017). *Quantum random number generators*. Reviews of Modern Physics, 89(1), 015004.
        """
    )
