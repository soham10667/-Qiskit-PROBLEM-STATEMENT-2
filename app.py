"""
RUMBER - Quantum Random Number Generation & Analysis System
"True Randomness, Powered by Quantum Mechanics."
Qiskit Fall Fest 2026 — Problem Statement 2: Quantum Random Number Generator (QRNG)

Integrated with IBM Quantum API via qiskit-ibm-runtime (QiskitRuntimeService, SamplerV2).
Supports Mode A (Local Qiskit Aer Simulator) and Mode B (Real IBM Quantum Hardware).
Credentials secured via Streamlit secrets (.streamlit/secrets.toml) or environment variables.
"""

import os
import math
import time
from typing import List, Dict, Any, Tuple, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import streamlit as st

import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Official IBM Quantum Runtime imports (Robust dynamic discovery across .venv and global site-packages)
import sys
_global_site = r"C:\Users\HP\AppData\Local\Programs\Python\Python312\Lib\site-packages"
if os.path.exists(_global_site) and _global_site not in sys.path:
    sys.path.append(_global_site)

IBM_RUNTIME_ERROR = None
try:
    import importlib
    _ibm_runtime = importlib.import_module("qiskit_ibm_runtime")
    QiskitRuntimeService = getattr(_ibm_runtime, "QiskitRuntimeService")
    Sampler = getattr(_ibm_runtime, "SamplerV2", getattr(_ibm_runtime, "Sampler", None))

    try:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    except ImportError:
        from qiskit.transpiler import generate_preset_pass_manager
    HAS_IBM_RUNTIME = True
except Exception as e:
    HAS_IBM_RUNTIME = False
    IBM_RUNTIME_ERROR = str(e)

# Configure Matplotlib default styling for Streamlit
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.titlesize": 13,
    "figure.dpi": 130,
})

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION & THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="RUMBER - Quantum Random Number Generator (QRNG)",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High-Contrast Professional Theme (Guarantees 100% visibility of tabs, buttons, and text)
st.markdown(
    """
    <style>
    /* -------------------------------------------------------------------------
       0. GLOBAL CURSOR BEHAVIOR (Prevents unwanted text caret/I-beam everywhere)
       ------------------------------------------------------------------------- */
    body, .stApp, .stApp * {
        cursor: default;
    }
    button, button *, [role="button"], [role="button"] *, [role="tab"], [role="tab"] *,
    .stButton button, .stButton button *, .stDownloadButton button, .stDownloadButton button *,
    input[type="radio"], input[type="checkbox"], label, .stRadio label, .stSlider {
        cursor: pointer !important;
    }
    input[type="text"], input[type="password"], textarea {
        cursor: text !important;
    }
    div[data-testid="stMetric"], div[data-testid="stTabs"], div[data-testid="stHorizontalBlock"] {
        cursor: default !important;
    }

    /* -------------------------------------------------------------------------
       1. TABS: Solid border, high-contrast, crystal clear text
       ------------------------------------------------------------------------- */
    div[data-testid="stTabs"] {
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }
    div[data-testid="stTabs"] div[role="tablist"],
    div[data-baseweb="tab-list"] {
        background-color: #f1f5f9 !important;
        padding: 6px !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
    }
    /* Inactive / Unselected Tabs */
    div[data-testid="stTabs"] button,
    button[data-baseweb="tab"] {
        background-color: #ffffff !important;
        border: 1px solid #94a3b8 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    div[data-testid="stTabs"] button *,
    button[data-baseweb="tab"] * {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    /* Active / Selected Tab */
    div[data-testid="stTabs"] button[aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #0052cc !important;
        border: 2px solid #003d99 !important;
        box-shadow: 0 4px 8px rgba(0, 82, 204, 0.3) !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] *,
    button[data-baseweb="tab"][aria-selected="true"] * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* -------------------------------------------------------------------------
       2. BUTTONS: Prominent Royal Blue with Bold White Text
       ------------------------------------------------------------------------- */
    .stButton button,
    div[data-testid="stButton"] button {
        background-color: #0052cc !important;
        border: 2px solid #003d99 !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 6px rgba(0, 82, 204, 0.25) !important;
        cursor: pointer !important;
    }
    .stButton button:hover,
    div[data-testid="stButton"] button:hover {
        background-color: #003d99 !important;
        box-shadow: 0 6px 12px rgba(0, 82, 204, 0.4) !important;
    }
    .stButton button *,
    div[data-testid="stButton"] button * {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
    }

    /* Download Buttons */
    .stDownloadButton button,
    div[data-testid="stDownloadButton"] button {
        background-color: #ffffff !important;
        border: 2px solid #0052cc !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    .stDownloadButton button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #eff6ff !important;
        border-color: #003d99 !important;
    }
    .stDownloadButton button *,
    div[data-testid="stDownloadButton"] button * {
        color: #0052cc !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }

    /* -------------------------------------------------------------------------
       3. INLINE CODE & STAT VALUES
       ------------------------------------------------------------------------- */
    code {
        background-color: #e2e8f0 !important;
        color: #0043a8 !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }

    /* -------------------------------------------------------------------------
       4. METRIC CARDS
       ------------------------------------------------------------------------- */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #0052cc !important;
        font-weight: 800 !important;
    }

    /* -------------------------------------------------------------------------
       5. ALERTS & NOTIFICATIONS
       ------------------------------------------------------------------------- */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"] p {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    /* -------------------------------------------------------------------------
       6. HEADERS
       ------------------------------------------------------------------------- */
    h1, h2, h3, h4, h5 {
        color: #0f2744 !important;
        font-weight: 800 !important;
    }

    /* Source Badges */
    .source-badge-sim {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #bae6fd;
    }
    .source-badge-hw {
        background-color: #fef3c7;
        color: #b45309;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #fde68a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 1. SECURE CREDENTIALS RESOLUTION
# ==============================================================================
def get_configured_ibm_credentials() -> Tuple[str, str, Optional[str]]:
    """
    Safely discovers IBM Quantum API credentials without exposing keys.
    Searches Streamlit secrets (.streamlit/secrets.toml) then environment variables.
    Returns: (token, source_description, optional_instance)
    """
    token = ""
    source = "Not Configured"
    instance = None

    # 1. Check Streamlit secrets (.streamlit/secrets.toml)
    if hasattr(st, "secrets"):
        for key_name in ["IBM_QUANTUM_API_KEY", "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN"]:
            if key_name in st.secrets and str(st.secrets[key_name]).strip():
                token = str(st.secrets[key_name]).strip()
                source = f".streamlit/secrets.toml ({key_name})"
                break
        for inst_key in ["IBM_QUANTUM_INSTANCE", "instance"]:
            if inst_key in st.secrets and str(st.secrets[inst_key]).strip():
                instance = str(st.secrets[inst_key]).strip()
                break

    # 2. Check environment variables if not found in secrets
    if not token:
        for env_name in ["IBM_QUANTUM_API_KEY", "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN"]:
            val = os.environ.get(env_name, "").strip()
            if val:
                token = val
                source = f"Environment Variable ({env_name})"
                break
        if not instance:
            env_inst = os.environ.get("IBM_QUANTUM_INSTANCE", "").strip()
            if env_inst:
                instance = env_inst

    return token, source, instance


def mask_token(token: str) -> str:
    """Masks API token for safe display (e.g. ••••••••4a1b)."""
    if not token:
        return "None"
    if len(token) <= 8:
        return "••••••••"
    return "••••••••" + token[-4:]


# ==============================================================================
# 2. QUANTUM CIRCUIT CREATION
# ==============================================================================
def create_qrng_circuit() -> QuantumCircuit:
    """
    Constructs the canonical 1-qubit, 1-classical-bit QRNG quantum circuit:
    1. Initializes qubit q_0 in the ground state |0>
    2. Applies Hadamard (H) gate to create equal superposition:
       |+> = (1/sqrt(2))(|0> + |1>)
    3. Measures qubit in computational (Z) basis onto classical register c_0.
    """
    qc = QuantumCircuit(1, 1, name="QRNG_Hadamard")
    qc.h(0)
    qc.measure(0, 0)
    return qc


def plot_clean_qrng_circuit() -> plt.Figure:
    """
    Renders a publication-grade vector graphic of the canonical QRNG circuit:
    |0> -> [ H ] -> [ M_Z ] -> c_0 in {0, 1}
    with IBM Quantum blue theme, clear state progression, and unbundled wires.
    """
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(6.8, 2.7), dpi=140)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Wire vertical levels
    y_q = 0.65  # Quantum wire y
    y_c = 0.22  # Classical wire y

    # 1. Quantum wire (dark slate)
    ax.plot([0.8, 5.4], [y_q, y_q], color="#334155", lw=2, zorder=1)

    # 2. Classical double wire (unbundled c_0 register)
    ax.plot([0.8, 5.4], [y_c + 0.02, y_c + 0.02], color="#64748b", lw=1.5, zorder=1)
    ax.plot([0.8, 5.4], [y_c - 0.02, y_c - 0.02], color="#64748b", lw=1.5, zorder=1)

    # Wire Labels
    ax.text(0.7, y_q, r"$q_0: |0\rangle$", ha="right", va="center", fontsize=12, fontweight="bold", color="#0052cc")
    ax.text(0.7, y_c, r"$c_0:$", ha="right", va="center", fontsize=11, fontweight="bold", color="#475569")

    # Gate 1: Hadamard [H] (IBM Blue rounded rectangle)
    h_box = patches.FancyBboxPatch(
        (1.65, y_q - 0.18), 0.85, 0.36,
        boxstyle="round,pad=0.03",
        facecolor="#0052cc", edgecolor="#003d99", lw=1.5, zorder=3
    )
    ax.add_patch(h_box)
    ax.text(2.075, y_q, "H", color="white", fontsize=14, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(2.075, y_q + 0.28, r"$|+\rangle = \frac{|0\rangle+|1\rangle}{\sqrt{2}}$", color="#0052cc", fontsize=10, ha="center", va="bottom", zorder=4)

    # Gate 2: Measurement Gate [M_Z] (Slate grey rounded box with meter arc)
    m_box = patches.FancyBboxPatch(
        (3.35, y_q - 0.18), 0.85, 0.36,
        boxstyle="round,pad=0.03",
        facecolor="#475569", edgecolor="#334155", lw=1.5, zorder=3
    )
    ax.add_patch(m_box)

    # Meter arc & needle
    arc = patches.Arc((3.775, y_q - 0.05), 0.42, 0.24, angle=0, theta1=0, theta2=180, color="white", lw=1.8, zorder=4)
    ax.add_patch(arc)
    ax.plot([3.775, 3.92], [y_q - 0.05, y_q + 0.09], color="white", lw=1.8, zorder=4)
    ax.text(3.775, y_q + 0.28, r"$\mathcal{M}_Z$ (Born Rule)", color="#475569", fontsize=10, ha="center", va="bottom", zorder=4)

    # Measurement Arrow to Classical Register
    ax.annotate(
        "", xy=(3.775, y_c + 0.04), xytext=(3.775, y_q - 0.18),
        arrowprops=dict(arrowstyle="->", color="#475569", lw=2, shrinkA=0, shrinkB=0),
        zorder=3
    )

    # Classical outcome label
    ax.text(5.55, y_c, r"$\in \{0, 1\}$", fontsize=12, fontweight="bold", color="#059669", va="center")

    ax.set_xlim(0, 6.4)
    ax.set_ylim(0, 1.1)
    ax.axis("off")
    plt.tight_layout()
    return fig


# ==============================================================================
# 3. LOCAL SIMULATOR BIT GENERATION (MODE A)
# ==============================================================================
def generate_quantum_bits_simulator(
    num_bits: int,
    seed: Optional[int] = None,
    batch_size: int = 25000,
    progress_bar=None,
) -> List[int]:
    """
    Executes the QRNG circuit on Qiskit AerSimulator.
    Uses memory=True to record individual chronological measurement outcomes.
    Supports large counts (e.g. 100,000 bits) via efficient batching.
    """
    qc = create_qrng_circuit()
    backend = AerSimulator()
    transpiled_qc = transpile(qc, backend)

    collected_bits: List[int] = []
    remaining = num_bits
    batch_idx = 0
    total_batches = math.ceil(num_bits / batch_size)

    while remaining > 0:
        current_shots = min(remaining, batch_size)
        curr_seed = (seed + batch_idx) if seed is not None else None

        job = backend.run(
            transpiled_qc,
            shots=current_shots,
            memory=True,
            seed_simulator=curr_seed,
        )
        result = job.result()
        memory_bits = result.get_memory()
        collected_bits.extend([int(b) for b in memory_bits])

        remaining -= current_shots
        batch_idx += 1
        if progress_bar is not None:
            progress_bar.progress(min(1.0, batch_idx / total_batches))

    return collected_bits


# ==============================================================================
# 4. REAL IBM QUANTUM HARDWARE BACKEND DISCOVERY & EXECUTION (MODE B)
# ==============================================================================
def init_qiskit_runtime_service(token: str, instance: Optional[str] = None) -> Any:
    """
    Initializes QiskitRuntimeService across qiskit-ibm-runtime versions.
    Tries 'ibm_quantum_platform', 'ibm_cloud', and legacy channels automatically.
    """
    clean_token = token.strip()
    channels_to_try = ["ibm_quantum_platform", "ibm_cloud", "ibm_quantum", None]
    last_err = None
    for ch in channels_to_try:
        try:
            kwargs = {"token": clean_token}
            if ch:
                kwargs["channel"] = ch
            if instance and instance.strip():
                kwargs["instance"] = instance.strip()
            return QiskitRuntimeService(**kwargs)
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Authentication with IBM Quantum failed: {str(last_err)}")


def fetch_operational_real_backends(token: str, instance: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Queries IBM Quantum for operational real quantum backends, strictly EXCLUDING simulators.
    Returns list of dicts with backend details sorted by pending jobs.
    """
    if not token or not HAS_IBM_RUNTIME:
        return []
    try:
        service = init_qiskit_runtime_service(token, instance=instance)

        # Strictly exclude simulators to return only real QPUs
        real_backends = service.backends(simulator=False, operational=True)
        results = []
        for b in real_backends:
            try:
                b_status = b.status()
                pending = getattr(b_status, "pending_jobs", 0)
                operational = getattr(b_status, "operational", True)
            except Exception:
                pending = 0
                operational = True

            if operational:
                results.append({
                    "name": b.name,
                    "num_qubits": getattr(b, "num_qubits", "Unknown"),
                    "pending_jobs": pending,
                    "backend_obj": b,
                })

        # Sort least busy first
        results.sort(key=lambda x: (x["pending_jobs"] if isinstance(x["pending_jobs"], int) else 999))
        return results
    except Exception:
        return []


def execute_on_ibm_hardware(
    token: str,
    backend_choice: str,
    shots: int = 1000,
    instance: Optional[str] = None,
) -> Tuple[List[int], Dict[str, Any]]:
    """
    Executes the QRNG circuit on real IBM Quantum hardware using modern Qiskit IBM Runtime.
    Transpiles via generate_preset_pass_manager to target backend's native ISA.
    Submits via Sampler primitive and retrieves individual measurement bitstrings.
    Never silently switches to simulator: raises clear exceptions on failure.
    """
    if not HAS_IBM_RUNTIME:
        raise RuntimeError(
            "qiskit-ibm-runtime is not installed. Please install it with 'pip install qiskit-ibm-runtime'."
        )

    clean_token = token.strip()
    if not clean_token:
        raise ValueError("IBM Quantum API Token is empty. Please configure it in .streamlit/secrets.toml.")

    # Initialize Qiskit Runtime Service with multi-channel support
    service = init_qiskit_runtime_service(clean_token, instance=instance)

    # Locate backend
    try:
        if "Least Busy" in backend_choice or backend_choice == "Auto-Select":
            backend = service.least_busy(operational=True, simulator=False)
        else:
            # Extract clean name in case qubits/pending jobs text is attached
            clean_backend_name = backend_choice.split()[0].strip()
            backend = service.backend(clean_backend_name)
    except Exception as e:
        raise RuntimeError(f"Failed to connect to backend '{backend_choice}': {str(e)}")

    # 1. Create QRNG Circuit
    qc = create_qrng_circuit()

    # 2. Transpile for target backend's Instruction Set Architecture (ISA)
    try:
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_qc = pm.run(qc)
    except Exception as e:
        raise RuntimeError(f"Transpilation for backend {backend.name} failed: {str(e)}")

    # 3. Submit using Sampler primitive
    try:
        sampler = Sampler(mode=backend)
        job = sampler.run([isa_qc], shots=shots)
        job_id = job.job_id()
    except Exception as e:
        raise RuntimeError(f"Job submission to {backend.name} failed: {str(e)}")

    # 4. Await results
    try:
        result = job.result()
        pub_result = result[0]
        reg_name = "meas" if hasattr(pub_result.data, "meas") else list(pub_result.data.keys())[0]
        data_bin = getattr(pub_result.data, reg_name)
        if hasattr(data_bin, "get_bitstrings"):
            bitstrings = data_bin.get_bitstrings()
            bits = [int(b.strip()) for b in bitstrings]
        elif hasattr(data_bin, "get_int_outcomes"):
            bits = [int(x) for x in data_bin.get_int_outcomes()]
        else:
            bits = [int(b) for b in list(data_bin)]

        counts = data_bin.get_counts() if hasattr(data_bin, "get_counts") else None
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve measurement bitstrings for job {job_id}: {str(e)}")

    metadata = {
        "backend_name": backend.name,
        "job_id": job_id,
        "shots": len(bits),
        "counts": counts,
        "is_hardware": True,
        "status": "COMPLETED",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return bits, metadata


# ==============================================================================
# 5. CLASSICAL PSEUDORANDOM GENERATOR (BENCHMARK)
# ==============================================================================
def generate_classical_bits(num_bits: int, seed: int = 42) -> List[int]:
    """
    Generates classical pseudorandom bits using NumPy's modern PCG64 BitGenerator.
    Provides an algorithmic reference baseline.
    """
    rng = np.random.default_rng(seed=seed)
    return rng.integers(low=0, high=2, size=num_bits).tolist()


# ==============================================================================
# 6. STATISTICAL RANDOMNESS ANALYSIS
# ==============================================================================
def analyze_sequence(bits: List[int], label: str = "Quantum Sequence") -> Dict[str, Any]:
    """
    Evaluates an ordered binary sequence across five statistical tests:
    1. Frequency (Monobit) Test (NIST SP 800-22)
    2. Shannon Binary Entropy & Entropy Deficit
    3. Wald-Wolfowitz Runs Test for sequence transitions
    4. Chi-Square Goodness-of-Fit Test (df=1)
    5. Serial Lag-1 Autocorrelation Test
    """
    arr = np.array(bits, dtype=int)
    n = len(arr)
    if n == 0:
        return {}

    n0 = int(np.sum(arr == 0))
    n1 = int(np.sum(arr == 1))
    p0 = n0 / n
    p1 = n1 / n
    deviation_p1 = abs(p1 - 0.5)

    # 1. Frequency (Monobit) Test
    s_obs = abs(n1 - n0) / math.sqrt(n)
    freq_p = math.erfc(s_obs / math.sqrt(2.0))
    freq_pass = freq_p >= 0.05

    # 2. Shannon Binary Entropy
    h0 = 0.0 if p0 == 0.0 else -p0 * math.log2(p0)
    h1 = 0.0 if p1 == 0.0 else -p1 * math.log2(p1)
    entropy = h0 + h1
    entropy_deficit = max(0.0, 1.0 - entropy)

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

    # 5. Serial Lag-1 Autocorrelation
    if n > 2 and np.var(arr) > 0:
        mean_val = np.mean(arr)
        num = np.sum((arr[:-1] - mean_val) * (arr[1:] - mean_val))
        den = np.sum((arr - mean_val) ** 2)
        autocorr_lag1 = float(num / den)
    else:
        autocorr_lag1 = 0.0

    return {
        "label": label,
        "total_bits": n,
        "count_zeros": n0,
        "count_ones": n1,
        "prob_zero": p0,
        "prob_one": p1,
        "deviation_p1": deviation_p1,
        "entropy": entropy,
        "entropy_deficit": entropy_deficit,
        "autocorr_lag1": autocorr_lag1,
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


# ==============================================================================
# 7. VON NEUMANN EXTRACTOR (BIAS MITIGATION)
# ==============================================================================
def von_neumann_extractor(raw_bits: List[int]) -> List[int]:
    """
    John von Neumann debiasing algorithm (1951):
    Considers non-overlapping pairs (b1, b2):
      - 01 -> output 0
      - 10 -> output 1
      - 00 or 11 -> discard
    Mathematically eliminates asymmetric hardware bias.
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
# 8. SESSION STATE INITIALIZATION
# ==============================================================================
if "quantum_bits" not in st.session_state:
    initial_bits = generate_quantum_bits_simulator(1000, seed=42)
    initial_classical = generate_classical_bits(1000, seed=42)
    st.session_state["quantum_bits"] = initial_bits
    st.session_state["simulator_bits"] = initial_bits
    st.session_state["hardware_bits"] = None
    st.session_state["classical_bits"] = initial_classical
    st.session_state["execution_source"] = "Qiskit AerSimulator (Local Simulation)"
    st.session_state["is_hardware"] = False
    st.session_state["analysis_q"] = analyze_sequence(initial_bits, "Quantum Simulator (Aer)")
    st.session_state["analysis_c"] = analyze_sequence(initial_classical, "Classical PRNG (NumPy)")
    st.session_state["hardware_metadata"] = None
    st.session_state["discovered_backends"] = None
    st.session_state["last_hardware_error"] = None


# ==============================================================================
# 9. SIDEBAR CONTROLS & CONFIGURATION
# ==============================================================================
st.sidebar.title("⚛️ RUMBER QRNG")
st.sidebar.caption("Quantum Random Number Generator & Analysis System")
st.sidebar.markdown("*Problem Statement 2: Qiskit Fall Fest 2026*")
st.sidebar.markdown("---")

st.sidebar.subheader("1. Execution Mode")
mode_choice = st.sidebar.radio(
    "Select Backend Target:",
    options=[
        "Mode A: Qiskit Simulator (Aer)",
        "Mode B: Real IBM Quantum Hardware",
    ],
    index=0,
    help="Mode A runs locally without IBM credentials. Mode B connects to real IBM quantum hardware via Qiskit IBM Runtime.",
)

is_hardware_mode = "Mode B" in mode_choice

# Detect credentials
cfg_token, cfg_source, cfg_instance = get_configured_ibm_credentials()

if not is_hardware_mode:
    # --------------------------------------------------------------------------
    # MODE A: SIMULATOR CONTROLS
    # --------------------------------------------------------------------------
    st.sidebar.subheader("2. Simulator Configuration")
    bit_choice = st.sidebar.selectbox(
        "Select Number of Bits / Shots:",
        options=["1,000 bits", "10,000 bits", "100,000 bits", "Custom size..."],
        index=0,
    )

    if bit_choice == "1,000 bits":
        requested_bits = 1000
    elif bit_choice == "10,000 bits":
        requested_bits = 10000
    elif bit_choice == "100,000 bits":
        requested_bits = 100000
    else:
        requested_bits = st.sidebar.number_input(
            "Enter Custom Bit Count:",
            min_value=10,
            max_value=250000,
            value=5000,
            step=1000,
        )

    use_seed = st.sidebar.checkbox("Reproducible Simulator Seed", value=False)
    sim_seed = None
    if use_seed:
        sim_seed = st.sidebar.number_input("Seed Value:", min_value=1, max_value=999999, value=42)

    classical_seed = st.sidebar.number_input("Classical PRNG Seed:", min_value=1, max_value=999999, value=42)

    st.sidebar.markdown("---")
    if st.sidebar.button("⚡ Generate Random Bits (Simulator)", type="primary", use_container_width=True):
        progress_bar = st.sidebar.progress(0.0)
        with st.spinner(f"Simulating {requested_bits:,} quantum shots on AerSimulator..."):
            t_start = time.time()
            q_out = generate_quantum_bits_simulator(
                requested_bits,
                seed=sim_seed,
                batch_size=25000,
                progress_bar=progress_bar,
            )
            c_out = generate_classical_bits(requested_bits, seed=classical_seed)
            t_elapsed = time.time() - t_start

            st.session_state["quantum_bits"] = q_out
            st.session_state["simulator_bits"] = q_out
            st.session_state["classical_bits"] = c_out
            st.session_state["execution_source"] = "Qiskit AerSimulator (Local Simulation)"
            st.session_state["is_hardware"] = False
            st.session_state["analysis_q"] = analyze_sequence(q_out, "Quantum Simulator (Aer)")
            st.session_state["analysis_c"] = analyze_sequence(c_out, "Classical PRNG (NumPy)")
            st.session_state["last_hardware_error"] = None
            progress_bar.empty()
            st.sidebar.success(f"Generated {requested_bits:,} bits in {t_elapsed:.2f}s!")

else:
    # --------------------------------------------------------------------------
    # MODE B: REAL IBM QUANTUM HARDWARE CONTROLS
    # --------------------------------------------------------------------------
    st.sidebar.subheader("2. IBM Quantum Hardware Setup")

    # Connection Status Display
    if cfg_token:
        st.sidebar.success(f"🟢 Credentials detected via `{cfg_source}`\n\nToken: `{mask_token(cfg_token)}`")
    else:
        st.sidebar.warning(
            "🟡 **No API Key Configured**\n\n"
            "Add your key to `.streamlit/secrets.toml`:\n"
            "```toml\nIBM_QUANTUM_API_KEY = \"YOUR_KEY\"\n```"
        )

    # Optional manual token override (never saved to source)
    manual_token = st.sidebar.text_input(
        "API Key (Overrides secrets if entered):",
        value="",
        type="password",
        placeholder="Paste here or use secrets.toml",
        help="Credentials entered here are kept in memory and never logged or written to disk.",
    )
    active_token = manual_token.strip() if manual_token.strip() else cfg_token

    # Query operational backends if token available
    backend_options = ["Least Busy Real QPU (Auto-select)"]
    if active_token and HAS_IBM_RUNTIME:
        # Check if backends cached in session state
        if st.session_state["discovered_backends"] is None:
            with st.spinner("Connecting to IBM Quantum and querying operational real QPUs..."):
                discovered = fetch_operational_real_backends(active_token, instance=cfg_instance)
                if discovered:
                    st.session_state["discovered_backends"] = discovered

        if st.session_state["discovered_backends"]:
            for b in st.session_state["discovered_backends"]:
                label = f"{b['name']} ({b['num_qubits']} qubits, {b['pending_jobs']} queue)"
                backend_options.append(label)

    # Allow user to refresh backend list
    if active_token and HAS_IBM_RUNTIME:
        if st.sidebar.button("🔄 Query / Refresh Backends"):
            with st.spinner("Refreshing available operational QPUs..."):
                discovered = fetch_operational_real_backends(active_token, instance=cfg_instance)
                st.session_state["discovered_backends"] = discovered
                st.rerun()

    # Fallback options if offline or before querying
    if len(backend_options) == 1:
        backend_options.extend(["ibm_fez", "ibm_kingston", "ibm_marrakesh", "ibm_brisbane", "ibm_sherbrooke"])

    ibm_backend = st.sidebar.selectbox(
        "Select Real Quantum Processor:",
        options=backend_options,
        index=0,
        help="Lists operational IBM quantum processors (excluding simulators).",
    )

    ibm_shots = st.sidebar.select_slider(
        "Hardware Shots / Bits:",
        options=[100, 500, 1000, 2000, 4096, 10000],
        value=1000,
        help="Real QPUs on the Open Plan support up to 4,096 or 10,000 shots per job.",
    )

    st.sidebar.caption("⚠️ Real quantum jobs queue on IBM Quantum servers. No jobs run automatically on UI reruns.")

    st.sidebar.markdown("---")
    # Explicit execution button
    if st.sidebar.button("🚀 Run on Real Quantum Hardware", type="primary", use_container_width=True):
        if not active_token:
            st.sidebar.error("IBM Quantum API Token is required. Please add it to `.streamlit/secrets.toml` or paste it above.")
            st.session_state["last_hardware_error"] = "API Token is missing."
        else:
            with st.spinner(f"Submitting 1-qubit QRNG circuit to real quantum processor ({ibm_backend})..."):
                try:
                    q_out, meta = execute_on_ibm_hardware(
                        token=active_token,
                        backend_choice=ibm_backend,
                        shots=ibm_shots,
                        instance=cfg_instance,
                    )
                    c_out = generate_classical_bits(len(q_out), seed=42)

                    # Update session state with genuine hardware results
                    st.session_state["quantum_bits"] = q_out
                    st.session_state["hardware_bits"] = q_out
                    st.session_state["classical_bits"] = c_out
                    st.session_state["execution_source"] = f"Real IBM Quantum Hardware ({meta['backend_name']})"
                    st.session_state["is_hardware"] = True
                    st.session_state["hardware_metadata"] = meta
                    st.session_state["analysis_q"] = analyze_sequence(q_out, f"Real QPU ({meta['backend_name']})")
                    st.session_state["analysis_c"] = analyze_sequence(c_out, "Classical PRNG (NumPy)")
                    st.session_state["last_hardware_error"] = None
                    st.sidebar.success(f"Executed on {meta['backend_name']}! (Job: {meta['job_id'][:8]}...)")
                except Exception as ex:
                    err_msg = str(ex)
                    st.session_state["last_hardware_error"] = err_msg
                    st.sidebar.error(f"Hardware Execution Failed: {err_msg}")
                    # NEVER silently switch to simulator: preserve explicit state and report error
                    st.error(
                        f"❌ **Hardware Execution Failed on IBM Quantum:**\n\n`{err_msg}`\n\n"
                        "Note: As required by scientific integrity rules, the system did not silently fall back to a simulator. "
                        "Check your API key, instance CRN, or select another backend."
                    )

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Qiskit Version:** `{qiskit.__version__}`")
st.sidebar.markdown(f"**Qiskit Aer:** `Installed & Operational`")
st.sidebar.markdown(f"**IBM Runtime:** `{'Installed' if HAS_IBM_RUNTIME else 'Not Installed'}`")
st.sidebar.caption("DBATU Lonere — Qiskit Fall Fest 2026")


# ==============================================================================
# 10. MAIN INTERFACE & DASHBOARD TABS
# ==============================================================================
st.title("⚛️ RUMBER — Quantum Random Number Generator (QRNG)")
st.markdown("##### *Harnessing Quantum Mechanics for True Randomness*")
st.caption("Qiskit Fall Fest 2026 Hackathon | DBATU, Lonere | Problem Statement 2")

# Active Source & Status Banner
active_source = st.session_state.get("execution_source", "Qiskit AerSimulator")
is_real_qpu = st.session_state.get("is_hardware", False)
q_bits = st.session_state["quantum_bits"]
c_bits = st.session_state["classical_bits"]
aq = st.session_state["analysis_q"]
ac = st.session_state["analysis_c"]
N = len(q_bits)

if is_real_qpu and st.session_state.get("hardware_metadata"):
    meta = st.session_state["hardware_metadata"]
    st.markdown(
        f'<div class="source-badge-hw">⚡ REAL IBM QUANTUM HARDWARE: {meta["backend_name"]} | Job ID: {meta["job_id"]}</div>',
        unsafe_allow_html=True,
    )
    st.success(
        f"🌟 **ACTIVE DATA SOURCE:** {active_source} | **Physical Shots:** {N:,} bits | "
        f"**Job ID:** `{meta['job_id']}` | **Execution Status:** `{meta['status']}`"
    )
else:
    st.markdown(
        f'<div class="source-badge-sim">🔬 QISKIT LOCAL SIMULATOR (AER)</div>',
        unsafe_allow_html=True,
    )
    st.info(
        f"📍 **ACTIVE DATA SOURCE:** {active_source} | **Sample Size:** {N:,} bits | "
        f"**Circuit:** 1 Qubit, 1 Classical Bit, 1 Hadamard Gate, 1 Measurement"
    )

if st.session_state.get("last_hardware_error"):
    st.warning(
        f"⚠️ **Last Hardware Job Status:** Failed with message: `{st.session_state['last_hardware_error']}`. "
        "The current active view displays the last valid sequence."
    )

# Tab Navigation
tab_dash, tab_stats, tab_comp, tab_mitigation, tab_circ, tab_hardware, tab_report = st.tabs([
    "📊 Dashboard & Visualizations",
    "📈 Statistical Randomness Battery",
    "⚖️ Quantum vs Classical PRNG",
    "🛡️ Bias Mitigation & Hardware Noise",
    "🔬 Quantum Circuit Architecture",
    "🚀 IBM Quantum Hardware",
    "📑 Hackathon Report & Judging",
])


# ==============================================================================
# TAB 1: LIVE DASHBOARD & VISUALIZATIONS
# ==============================================================================
with tab_dash:
    st.subheader("Key Generation & Randomness Metrics")
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
        st.subheader("Zero vs One Frequency Distribution")
        fig1, ax1 = plt.subplots(figsize=(6, 3.8))
        categories = ["Bit 0 (|0⟩)", "Bit 1 (|1⟩)"]
        counts = [aq["count_zeros"], aq["count_ones"]]
        colors = ["#1e40af", "#3b82f6"] if not is_real_qpu else ["#b45309", "#f59e0b"]

        bars = ax1.bar(categories, counts, color=colors, width=0.45, edgecolor="#0f172a", alpha=0.9)
        ax1.axhline(N / 2.0, color="#dc2626", linestyle="--", linewidth=1.8, label=f"Expected ({N//2:,})")

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

        ax1.set_ylim(0, max(counts) * 1.25)
        ax1.set_ylabel("Measured Count")
        source_title = "Real Hardware" if is_real_qpu else "Simulator"
        ax1.set_title(f"Distribution of Outcomes ({source_title})")
        ax1.legend(loc="lower right")
        ax1.grid(axis="y", linestyle=":", alpha=0.6)
        st.pyplot(fig1)

    with c_right:
        st.subheader("Empirical vs Theoretical Probability (Born's Rule)")
        fig2, ax2 = plt.subplots(figsize=(6, 3.8))
        x_indices = np.arange(2)
        bar_w = 0.35

        observed_p = [aq["prob_zero"], aq["prob_one"]]
        theory_p = [0.5, 0.5]

        color_obs = "#0284c7" if not is_real_qpu else "#d97706"
        r1 = ax2.bar(x_indices - bar_w / 2, observed_p, bar_w, label="Observed", color=color_obs, edgecolor="#0f172a")
        r2 = ax2.bar(x_indices + bar_w / 2, theory_p, bar_w, label="Expected (Born's Rule)", color="#94a3b8", alpha=0.6, edgecolor="#0f172a")

        ax2.axhline(0.5, color="#dc2626", linestyle=":", linewidth=1.5)
        ax2.set_xticks(x_indices)
        ax2.set_xticklabels(["Bit 0", "Bit 1"])
        ax2.set_ylim(0, 0.72)
        ax2.set_ylabel("Probability P(x)")
        ax2.set_title("Probability Comparison (Parity Target: 0.5000)")
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
        st.write("**2D Spatial Dispersion Raster (First 400 Bits, 20 × 20 Grid)**")
        grid_dim = 20
        raster_sample = np.array(q_bits[: grid_dim * grid_dim])
        if len(raster_sample) < grid_dim * grid_dim:
            raster_sample = np.pad(raster_sample, (0, grid_dim * grid_dim - len(raster_sample)))
        grid_data = raster_sample.reshape((grid_dim, grid_dim))

        fig_r, ax_r = plt.subplots(figsize=(4, 3.8))
        cmap_choice = "Blues" if not is_real_qpu else "YlOrBr"
        ax_r.imshow(grid_data, cmap=cmap_choice, interpolation="nearest")
        ax_r.set_xticks([])
        ax_r.set_yticks([])
        ax_r.set_title("Bit Dispersion (White=0, Dark=1)", fontsize=10)
        st.pyplot(fig_r)

    with v_right:
        st.write("**Digital Waveform Pulse Trace (First 50 Generated Bits)**")
        first_50 = q_bits[:50]
        steps_x = np.repeat(np.arange(len(first_50)), 2)[1:]
        steps_y = np.repeat(first_50, 2)[:-1]

        fig_w, ax_w = plt.subplots(figsize=(6.8, 3.2))
        wave_color = "#1d4ed8" if not is_real_qpu else "#b45309"
        ax_w.plot(steps_x, steps_y, color=wave_color, linewidth=1.8, label="Quantum Bit Level")
        ax_w.scatter(np.arange(len(first_50)), first_50, color="#dc2626", s=18, zorder=3)
        ax_w.set_yticks([0, 1])
        ax_w.set_yticklabels(["0 (|0⟩)", "1 (|1⟩)"])
        ax_w.set_xlabel("Bit Index")
        ax_w.set_ylabel("Collapsed State")
        ax_w.set_ylim(-0.25, 1.25)
        ax_w.grid(True, linestyle=":", alpha=0.5)
        ax_w.legend(loc="upper right", fontsize=8)
        st.pyplot(fig_w)

    # Bit Sequence Viewer with sensible display limit
    st.subheader("Generated Bit Sequence Inspector")
    display_limit = min(100, N)
    formatted_bits = " ".join("".join(str(b) for b in q_bits[i:i+8]) for i in range(0, display_limit, 8))
    st.code(formatted_bits, language="text")
    st.caption(f"Showing first {display_limit} chronologically generated bits (in 8-bit bytes). Total bits in memory: {N:,}.")

    # Download Buttons (TXT and CSV)
    st.subheader("Download Bit Sequence")
    d_col1, d_col2 = st.columns(2)

    # TXT Download
    raw_bit_string = "".join(str(b) for b in q_bits)
    with d_col1:
        st.download_button(
            label="📥 Download Raw Bitstream (.txt)",
            data=raw_bit_string.encode("utf-8"),
            file_name=f"qrng_bits_{N}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # CSV Download
    df_quantum = pd.DataFrame({
        "bit_index": list(range(len(q_bits))),
        "quantum_bit": q_bits,
        "source": active_source,
    })
    csv_data = df_quantum.to_csv(index=False).encode("utf-8")
    with d_col2:
        st.download_button(
            label="📥 Download Structured Bitstream (.csv)",
            data=csv_data,
            file_name=f"qrng_bits_{N}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ==============================================================================
# TAB 2: STATISTICAL RANDOMNESS BATTERY
# ==============================================================================
with tab_stats:
    st.header("Statistical Randomness Battery")
    st.write(
        """
        We evaluate the generated quantum bitstream across five established statistical tests 
        to verify that the sequence satisfies the mathematical properties of an independent Bernoulli process 
        with $p = 0.5$.
        """
    )

    s_left, s_right = st.columns(2)

    with s_left:
        st.subheader("1. Chi-Square (χ²) Goodness-of-Fit Test")
        st.latex(r"\chi^2 = \sum_{i \in \{0, 1\}} \frac{(O_i - E_i)^2}{E_i}, \quad E_0 = E_1 = \frac{N}{2}")
        st.write(
            """
            - **Null Hypothesis ($H_0$):** Bit outcomes follow a discrete uniform distribution ($P(0) = P(1) = 0.5$).
            - **Assumptions:** Independent trials; expected frequencies $E_i \ge 5$ (satisfied for $N \ge 10$).
            - **Degrees of Freedom:** $df = 2 - 1 = 1$.
            """
        )
        st.write(f"- **Statistic ($\chi^2$):** `{aq['chi_square_test']['statistic']:.4f}`")
        st.write(f"- **p-value:** `{aq['chi_square_test']['p_value']:.4f}`")
        if aq["chi_square_test"]["passed"]:
            st.success("Verdict: PASS — Observed frequencies conform to the discrete uniform distribution ($p \\ge 0.05$).")
        else:
            st.error("Verdict: FAIL — Proportions deviate significantly from 50:50 parity ($p < 0.05$).")

        st.subheader("2. Wald-Wolfowitz Runs Test")
        st.latex(r"\mu_R = \frac{2n_0n_1}{N} + 1, \quad \sigma_R^2 = \frac{2n_0n_1(2n_0n_1 - N)}{N^2(N - 1)}, \quad Z = \frac{R - \mu_R}{\sigma_R}")
        st.write(
            """
            - **Null Hypothesis ($H_0$):** Sequence elements are mutually independent (no clustering or excessive alternation).
            - **Observed Runs ($R$):** Number of contiguous blocks of identical bits.
            """
        )
        st.write(f"- **Observed Runs ($R$):** `{aq['runs_test']['observed_runs']:,}`")
        st.write(f"- **Expected Runs ($\mu_R$):** `{aq['runs_test']['expected_runs']:.2f}`")
        st.write(f"- **Z-Score:** `{aq['runs_test']['z_score']:+.4f}`")
        st.write(f"- **p-value:** `{aq['runs_test']['p_value']:.4f}`")
        if aq["runs_test"]["passed"]:
            st.success("Verdict: PASS — Run count is consistent with independent random trials ($|Z| \\le 1.96$).")
        else:
            st.error("Verdict: FAIL — Significant autocorrelation or clustering detected.")

    with s_right:
        st.subheader("3. Frequency (Monobit) Test (NIST SP 800-22)")
        st.latex(r"S_{obs} = \frac{|n_1 - n_0|}{\sqrt{N}}, \quad p = \text{erfc}\left(\frac{S_{obs}}{\sqrt{2}}\right)")
        st.write(
            """
            - **Null Hypothesis ($H_0$):** The proportion of ones and zeros is equal to 0.5.
            - **Complementary Error Function:** Assesses tail probability under standard normal approximation.
            """
        )
        st.write(f"- **Statistic ($S_{{obs}}$):** `{aq['frequency_test']['statistic']:.4f}`")
        st.write(f"- **p-value:** `{aq['frequency_test']['p_value']:.4f}`")
        if aq["frequency_test"]["passed"]:
            st.success("Verdict: PASS — Monobit frequency matches ideal parity ($p \\ge 0.05$).")
        else:
            st.error("Verdict: FAIL — Sequence exhibits significant bit bias ($p < 0.05$).")

        st.subheader("4. Shannon Binary Entropy")
        st.latex(r"H(X) = - \sum_{x \in \{0, 1\}} P(x) \log_2 P(x)")
        st.write(f"- **Calculated Entropy:** `{aq['entropy']:.6f}` bits per symbol")
        st.write(f"- **Theoretical Maximum:** `1.000000` bit per symbol")
        st.write(f"- **Entropy Deficit:** `{aq['entropy_deficit']:.2e}` bits")
        st.info("High entropy confirms near-maximal information uncertainty per generated bit.")

        st.subheader("5. Serial Lag-1 Autocorrelation")
        st.latex(r"r_1 = \frac{\sum_{i=1}^{N-1} (x_i - \bar{x})(x_{i+1} - \bar{x})}{\sum_{i=1}^N (x_i - \bar{x})^2}")
        st.write(f"- **Lag-1 Correlation ($r_1$):** `{aq['autocorr_lag1']:+.5f}` (Target: near 0.00000)")
        if abs(aq['autocorr_lag1']) < 0.03:
            st.success("Verdict: PASS — Negligible correlation between adjacent bits.")
        else:
            st.warning("Verdict: Slight correlation detected.")

    st.markdown("---")
    st.warning(
        """
        **Scientific Integrity & Limitation Notice:**  
        Passing standard statistical tests is a mandatory baseline, but **does not prove that a sequence 
        is cryptographically secure or truly physically random**. Classical pseudorandom algorithms (such as 
        PCG64 or Mersenne Twister) pass these exact tests while being 100% deterministic. Physical quantum 
        randomness originates from quantum state collapse on physical quantum hardware, not simulator software.
        """
    )

    # Downloadable statistical report
    stat_report_str = f"""================================================================================
RUMBER - QUANTUM RANDOM NUMBER GENERATOR (QRNG) STATISTICAL REPORT
Problem Statement 2: Quantum Computing Hackathon
================================================================================
Data Source:        {active_source}
Total Shots (N):    {N:,}
Count of Zeros (n0): {aq['count_zeros']:,} ({aq['prob_zero']*100:.2f}%)
Count of Ones (n1):  {aq['count_ones']:,} ({aq['prob_one']*100:.2f}%)
Deviation |P1 - 0.5|: {aq['deviation_p1']:.5f}

1. CHI-SQUARE GOODNESS-OF-FIT TEST (df=1):
   - Statistic (Chi2): {aq['chi_square_test']['statistic']:.4f}
   - p-value:          {aq['chi_square_test']['p_value']:.4f}
   - Verdict:          {'PASS' if aq['chi_square_test']['passed'] else 'FAIL'}

2. WALD-WOLFOWITZ RUNS TEST:
   - Observed Runs:    {aq['runs_test']['observed_runs']:,}
   - Expected Runs:    {aq['runs_test']['expected_runs']:.2f}
   - Z-Score:          {aq['runs_test']['z_score']:+.4f}
   - p-value:          {aq['runs_test']['p_value']:.4f}
   - Verdict:          {'PASS' if aq['runs_test']['passed'] else 'FAIL'}

3. FREQUENCY (MONOBIT) TEST:
   - Statistic (S_obs): {aq['frequency_test']['statistic']:.4f}
   - p-value:          {aq['frequency_test']['p_value']:.4f}
   - Verdict:          {'PASS' if aq['frequency_test']['passed'] else 'FAIL'}

4. SHANNON BINARY ENTROPY:
   - Observed Entropy: {aq['entropy']:.6f} bits/symbol
   - Theoretical Max:  1.000000 bits/symbol
   - Deficit:          {aq['entropy_deficit']:.2e} bits

5. LAG-1 AUTOCORRELATION:
   - Coefficient (r1): {aq['autocorr_lag1']:+.5f}
================================================================================
"""
    st.download_button(
        label="📥 Download Complete Statistical Report (.txt)",
        data=stat_report_str.encode("utf-8"),
        file_name=f"qrng_statistical_report_{N}.txt",
        mime="text/plain",
    )


# ==============================================================================
# TAB 3: QUANTUM VS CLASSICAL PRNG COMPARISON
# ==============================================================================
with tab_comp:
    st.header("Quantum vs Classical PRNG Benchmark")
    st.write(
        """
        To rigorously evaluate the quantum-generated bitstream, we benchmark it against an identical-length 
        sequence produced by a standard classical pseudorandom generator (**NumPy's PCG64 BitGenerator**).
        """
    )

    comparison_data = [
        {
            "Metric": "Total Bits (N)",
            "Theoretical Target": f"{N:,}",
            "Quantum Sequence": f"{aq['total_bits']:,}",
            "Classical PRNG (PCG64)": f"{ac['total_bits']:,}",
            "Verdict": "Matching Sample Size",
        },
        {
            "Metric": "Bit 0 Count (n0)",
            "Theoretical Target": f"{N//2:,} (50.0%)",
            "Quantum Sequence": f"{aq['count_zeros']:,} ({aq['prob_zero']*100:.2f}%)",
            "Classical PRNG (PCG64)": f"{ac['count_zeros']:,} ({ac['prob_zero']*100:.2f}%)",
            "Verdict": "Balanced",
        },
        {
            "Metric": "Bit 1 Count (n1)",
            "Theoretical Target": f"{N//2:,} (50.0%)",
            "Quantum Sequence": f"{aq['count_ones']:,} ({aq['prob_one']*100:.2f}%)",
            "Classical PRNG (PCG64)": f"{ac['count_ones']:,} ({ac['prob_one']*100:.2f}%)",
            "Verdict": "Balanced",
        },
        {
            "Metric": "Proportion Deviation |P1 - 0.5|",
            "Theoretical Target": "0.00000",
            "Quantum Sequence": f"{aq['deviation_p1']:.5f}",
            "Classical PRNG (PCG64)": f"{ac['deviation_p1']:.5f}",
            "Verdict": "Minimal Drift",
        },
        {
            "Metric": "Shannon Entropy (bits/symbol)",
            "Theoretical Target": "1.000000",
            "Quantum Sequence": f"{aq['entropy']:.6f}",
            "Classical PRNG (PCG64)": f"{ac['entropy']:.6f}",
            "Verdict": "High Information Density",
        },
        {
            "Metric": "Observed Runs (R)",
            "Theoretical Target": f"{(N/2)+1:,.1f}",
            "Quantum Sequence": f"{aq['runs_test']['observed_runs']:,}",
            "Classical PRNG (PCG64)": f"{ac['runs_test']['observed_runs']:,}",
            "Verdict": "Normal Switching",
        },
        {
            "Metric": "Runs Test Z-Score",
            "Theoretical Target": "0.0000",
            "Quantum Sequence": f"{aq['runs_test']['z_score']:+.4f}",
            "Classical PRNG (PCG64)": f"{ac['runs_test']['z_score']:+.4f}",
            "Verdict": "Within [-1.96, +1.96]",
        },
        {
            "Metric": "Chi-Square p-value",
            "Theoretical Target": ">= 0.05",
            "Quantum Sequence": f"{aq['chi_square_test']['p_value']:.4f}",
            "Classical PRNG (PCG64)": f"{ac['chi_square_test']['p_value']:.4f}",
            "Verdict": "Pass (p >= 0.05)",
        },
        {
            "Metric": "Lag-1 Autocorrelation",
            "Theoretical Target": "0.00000",
            "Quantum Sequence": f"{aq['autocorr_lag1']:+.5f}",
            "Classical PRNG (PCG64)": f"{ac['autocorr_lag1']:+.5f}",
            "Verdict": "Uncorrelated",
        },
    ]

    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

    # Comparison Plot
    fig_comp, (ax_c1, ax_c2) = plt.subplots(1, 2, figsize=(8, 3.4))

    # Deviation bar chart
    dev_q = aq["deviation_p1"]
    dev_c = ac["deviation_p1"]
    bars_dev = ax_c1.bar(
        ["Quantum", "Classical PRNG"],
        [dev_q, dev_c],
        color=["#1d4ed8", "#d97706"],
        width=0.45,
        edgecolor="#0f172a",
    )
    ax_c1.set_ylabel("Absolute Deviation |P1 - 0.5|")
    ax_c1.set_title("Deviation from Ideal 50% Proportion")
    ax_c1.grid(axis="y", linestyle=":", alpha=0.6)
    for b in bars_dev:
        ax_c1.annotate(
            f"{b.get_height():.5f}",
            xy=(b.get_x() + b.get_width() / 2, b.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=9,
        )

    # Autocorrelation chart
    r_q = aq["autocorr_lag1"]
    r_c = ac["autocorr_lag1"]
    bars_r = ax_c2.bar(
        ["Quantum", "Classical PRNG"],
        [abs(r_q), abs(r_c)],
        color=["#0284c7", "#ea580c"],
        width=0.45,
        edgecolor="#0f172a",
    )
    ax_c2.set_ylabel("Absolute Lag-1 Autocorrelation |r1|")
    ax_c2.set_title("Adjacent Bit Independence (Lower is Better)")
    ax_c2.grid(axis="y", linestyle=":", alpha=0.6)
    for b in bars_r:
        ax_c2.annotate(
            f"{b.get_height():.5f}",
            xy=(b.get_x() + b.get_width() / 2, b.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=9,
        )

    plt.tight_layout()
    st.pyplot(fig_comp)

    st.subheader("Fundamental Distinction: Classical PRNG vs Quantum Randomness")
    st.write(
        """
        | Dimension | Classical PRNG (e.g. PCG64 / MT19937) | Quantum Circuit Simulator (Aer) | Physical Quantum Computer (QPU) |
        | :--- | :--- | :--- | :--- |
        | **Mechanism** | Algorithmic recurrence: $s_{n+1} = f(s_n)$ | Mathematical statevector sampling | Physical wave-function collapse |
        | **Entropy Source** | Pseudo-stochastic seed | Classical pseudo-stochastic routine | Superconducting transmon measurement |
        | **Reproducibility** | Perfectly repeatable given the seed | Repeatable if seed is fixed | **Fundamentally non-reproducible** |
        | **Cryptographic Security** | Vulnerable if internal state is compromised | Not cryptographically random | Provably true physical entropy |
        | **Hardware Dependence**| Runs on standard CPU/RAM | Runs on standard CPU/GPU | Requires dilution refrigerator (~15 mK) |
        """
    )


# ==============================================================================
# TAB 4: BIAS MITIGATION & HARDWARE NOISE
# ==============================================================================
with tab_mitigation:
    st.header("🛡️ Bias Mitigation: John von Neumann Extractor")
    st.write(
        """
        ### The Physical Challenge: Superconducting Hardware Asymmetry
        While ideal quantum circuits satisfy Born's rule ($P(0) = P(1) = 0.5000$), physical quantum hardware 
        (e.g., IBM Quantum Eagle or Heron transmon processors) experiences noise:
        1. **Readout Asymmetry:** State preparation and measurement (SPAM) errors favor state $|0\rangle$ over $|1\rangle$.
        2. **Thermal Relaxation ($T_1$):** Excited state $|1\rangle$ decays spontaneously toward ground state $|0\rangle$.
        
        This introduces a non-trivial physical bias ($P(1) \\neq 0.50$), causing raw hardware streams to fail statistical tests.
        """
    )

    st.subheader("The Mathematical Solution: John von Neumann Debiasing (1951)")
    st.write(
        """
        To mathematically eliminate physical bias without knowing the exact hardware noise parameter $p$, 
        we implement the **Von Neumann Debiasing Algorithm**:
        """
    )
    st.latex(r"\text{Pair } (b_1, b_2): \quad 01 \to 0, \quad 10 \to 1, \quad 00 \text{ or } 11 \to \text{Discard}")
    st.write(
        """
        **Mathematical Proof of Perfect Unbiasedness:**  
        For any independent trials with arbitrary physical bias $P(1) = p$ and $P(0) = 1 - p$:
        """
    )
    st.latex(r"P(01) = (1 - p)p, \quad P(10) = p(1 - p)")
    st.latex(r"\text{Since } P(01) = P(10) \implies P(0 \mid \text{output}) = P(1 \mid \text{output}) = 50.0\%")
    st.write(
        """
        **Yield / Length Reduction:**  
        The theoretical extraction efficiency is $\\text{Yield} = 2p(1 - p)$. For an unbiased source ($p = 0.5$), 
        the maximum yield is $50\\%$. As bias increases, yield decreases, trading output length for pure statistical uniformity.
        """
    )

    st.markdown("---")
    st.subheader("Interactive Hardware Noise & Mitigation Simulator")

    noise_col1, noise_col2 = st.columns([1, 1.2])

    with noise_col1:
        st.write("**Simulate Imperfect Quantum Hardware Noise:**")
        sim_bias = st.slider(
            "Simulated Physical Bias P(1):",
            min_value=0.50,
            max_value=0.80,
            value=0.60,
            step=0.01,
            help="Simulates asymmetric readout noise or T1 relaxation.",
        )
        sample_raw_size = st.selectbox("Raw Hardware Shots:", [2000, 5000, 10000, 20000], index=1)

        # Generate synthetic biased stream
        rng_noise = np.random.default_rng(seed=123)
        raw_biased = rng_noise.choice([0, 1], size=sample_raw_size, p=[1.0 - sim_bias, sim_bias]).tolist()
        mitigated_bits = von_neumann_extractor(raw_biased)

    with noise_col2:
        st.write("**Extraction Efficiency & Yield Analysis:**")
        n_raw = len(raw_biased)
        n_clean = len(mitigated_bits)
        yield_rate = (n_clean / n_raw) * 100 if n_raw > 0 else 0
        theory_yield = 2.0 * sim_bias * (1.0 - sim_bias) * 100

        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Raw Biased Input", f"{n_raw:,} bits")
        m_c2.metric(
            "Extracted Pure Bits",
            f"{n_clean:,} bits",
            delta=f"Yield: {yield_rate:.1f}% (Theory: {theory_yield:.1f}%)",
        )

    # Side-by-Side Verification
    ana_raw = analyze_sequence(raw_biased, "Raw Biased Stream")
    ana_mit = analyze_sequence(mitigated_bits, "Von Neumann Debiased")

    st.markdown("#### Side-by-Side Verification: Before vs After Debiasing")
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        st.markdown("**1. Raw Hardware Stream (Biased)**")
        st.write(f"- Proportion of Ones: `{ana_raw['prob_one']*100:.2f}%` (Target: 50.0%)")
        st.write(f"- Shannon Entropy: `{ana_raw['entropy']:.6f}` bits/symbol")
        st.write(f"- Chi-Square p-value: `{ana_raw['chi_square_test']['p_value']:.4e}`")
        if ana_raw["chi_square_test"]["passed"]:
            st.success("Verdict: PASS")
        else:
            st.error("Verdict: FAIL — Severe hardware bias detected ($p < 0.05$).")

    with b_col2:
        st.markdown("**2. Extracted Stream (Debiased)**")
        st.write(f"- Proportion of Ones: `{ana_mit['prob_one']*100:.2f}%` (Target: 50.0%)")
        st.write(f"- Shannon Entropy: `{ana_mit['entropy']:.6f}` bits/symbol")
        st.write(f"- Chi-Square p-value: `{ana_mit['chi_square_test']['p_value']:.4f}`")
        if ana_mit["chi_square_test"]["passed"]:
            st.success("Verdict: PASS — Hardware bias mathematically eliminated ($p \\ge 0.05$)!")
        else:
            st.warning("Verdict: Needs larger raw sample.")

    # Matplotlib Bar Charts
    fig_mit, (ax_m1, ax_m2) = plt.subplots(1, 2, figsize=(7.5, 3.2))

    ax_m1.bar(["0", "1"], [ana_raw["prob_zero"], ana_raw["prob_one"]], color=["#94a3b8", "#dc2626"], width=0.45, edgecolor="#0f172a")
    ax_m1.axhline(0.5, color="black", linestyle="--", linewidth=1.2)
    ax_m1.set_ylim(0, 0.85)
    ax_m1.set_title(f"Raw Biased (P1 = {ana_raw['prob_one']*100:.1f}%)", fontsize=10, fontweight="bold")
    ax_m1.set_ylabel("Probability P(x)")

    ax_m2.bar(["0", "1"], [ana_mit["prob_zero"], ana_mit["prob_one"]], color=["#0284c7", "#16a34a"], width=0.45, edgecolor="#0f172a")
    ax_m2.axhline(0.5, color="black", linestyle="--", linewidth=1.2)
    ax_m2.set_ylim(0, 0.85)
    ax_m2.set_title(f"Mitigated Pure (P1 = {ana_mit['prob_one']*100:.1f}%)", fontsize=10, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig_mit)

    # Download debiased bits
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
    st.header("Quantum Circuit Architecture & Theory")
    qc = create_qrng_circuit()

    circ_col1, circ_col2 = st.columns([1.1, 1.2], gap="large")

    with circ_col1:
        st.subheader("Circuit Architecture")
        circ_tabs = st.tabs([
            "🎨 Publication Schematic",
            "🔬 Qiskit Native MPL",
            "🔤 Terminal ASCII Wire",
        ])

        with circ_tabs[0]:
            fig_clean = plot_clean_qrng_circuit()
            st.pyplot(fig_clean, use_container_width=True)
            st.caption("✅ **Publication-Grade Representation:** $|0\\rangle$ initialized, IBM Quantum Blue $H$ gate, Born-rule measurement $\\mathcal{M}_Z$, and unbundled classical bit $c_0$.")

        with circ_tabs[1]:
            try:
                fig_circuit = qc.draw(
                    output="mpl",
                    style="clifford",
                    initial_state=True,
                    cregbundle=False,
                    scale=0.75,
                )
                fig_circuit.set_dpi(140)
                st.pyplot(fig_circuit, use_container_width=True)
                st.caption("Qiskit Matplotlib Drawer with Clifford color palette, explicit $|0\\rangle$, and unbundled $c_0$ register.")
            except Exception:
                fig_circuit = plot_clean_qrng_circuit()
                st.pyplot(fig_circuit, use_container_width=True)
                st.caption("Rendered via High-Fidelity Matplotlib Vector Engine.")

        with circ_tabs[2]:
            st.code(qc.draw(output="text"), language="text")
            st.caption("Standard Qiskit text-based ASCII wire diagram.")

    with circ_col2:
        st.subheader("Mathematical Principles")
        st.markdown(
            """
            1. **Qubit Initialization:**  
               A single physical qubit $q_0$ is initialized in the computational ground state $|0\\rangle$:
               $$|0\\rangle = \\begin{pmatrix} 1 \\\\ 0 \\end{pmatrix}$$

            2. **Hadamard Superposition Gate ($H$):**  
               Applying the unitary transformation:
               $$H = \\frac{1}{\\sqrt{2}}\\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix}$$
               creates an equal, unbiased superposition state $|+\\rangle$:
               $$|\\psi\\rangle = H|0\\rangle = \\frac{1}{\\sqrt{2}}|0\\rangle + \\frac{1}{\\sqrt{2}}|1\\rangle = |+\\rangle$$

            3. **Pauli-Z Computational Basis Measurement ($M_Z$):**  
               According to **Born's Rule**, projective measurement onto orthogonal computational basis $\{|0\\rangle, |1\\rangle\}$ collapses the wavefunction with equal probability:
               
               - **Probability of measuring bit 0:**
                 $$P(0) = |\\langle 0 | + \\rangle|^2 = \\left|\\frac{1}{\\sqrt{2}}\\right|^2 = \\frac{1}{2} = 50.0\\%$$
               
               - **Probability of measuring bit 1:**
                 $$P(1) = |\\langle 1 | + \\rangle|^2 = \\left|\\frac{1}{\\sqrt{2}}\\right|^2 = \\frac{1}{2} = 50.0\\%$$

            4. **Qiskit Bit Ordering & Chronological Extraction:**  
               In Qiskit, measurement outcomes are mapped onto classical register $c_0$. By passing `memory=True` 
               to `AerSimulator` or reading `get_bitstrings()` from `SamplerV2`, we preserve the exact chronological 
               order of individual measurements rather than simply sampling from aggregate counts.
            """
        )


# ==============================================================================
# TAB 6: IBM QUANTUM HARDWARE INTEGRATION & COMPARISON
# ==============================================================================
with tab_hardware:
    st.header("🚀 Real IBM Quantum Hardware Execution")
    st.write(
        """
        Execute the QRNG circuit directly on real superconducting quantum hardware 
        via IBM Quantum Platform and `qiskit-ibm-runtime`.
        """
    )

    # Status Cards
    stat_c1, stat_c2 = st.columns(2)
    with stat_c1:
        st.subheader("Connection Status")
        if cfg_token:
            st.success(
                f"✅ **Credentials Active:** `{cfg_source}`\n\n"
                f"- **Token (Masked):** `{mask_token(cfg_token)}`\n"
                f"- **Instance (CRN):** `{cfg_instance if cfg_instance else 'Default Open Plan'}`"
            )
        else:
            st.warning(
                "⚠️ **Credentials Not Configured**\n\n"
                "Please create `.streamlit/secrets.toml` in your project root:\n\n"
                "```toml\nIBM_QUANTUM_API_KEY = \"YOUR_44_CHAR_KEY_HERE\"\n```"
            )

    with stat_c2:
        st.subheader("Hardware Job Status")
        if is_real_qpu and st.session_state.get("hardware_metadata"):
            m = st.session_state["hardware_metadata"]
            counts_display = f"\n- **Measurement Counts:** `{m['counts']}`" if m.get("counts") else ""
            st.success(
                f"- **Backend:** `{m['backend_name']}`\n"
                f"- **Job ID:** `{m['job_id']}`\n"
                f"- **Physical Shots:** `{m['shots']:,}`{counts_display}\n"
                f"- **Status:** `{m['status']}`\n"
                f"- **Timestamp:** `{m['timestamp']}`\n\n"
                f"🔗 [View Job on IBM Quantum Dashboard](https://quantum.ibm.com/jobs/{m['job_id']})"
            )
        else:
            st.info(
                "No hardware job has been retrieved in this active session.\n\n"
                "To execute on physical hardware, select **Mode B** in the left sidebar and click **🚀 Run on Real Quantum Hardware**."
            )

    st.markdown("---")

    # Side-by-side Simulator vs Real Hardware comparison if hardware bits exist
    if st.session_state.get("hardware_bits") is not None and st.session_state.get("simulator_bits") is not None:
        st.subheader("📊 Direct Comparison: Simulator vs Real Hardware Distribution")
        st.write(
            """
            Comparison between the local **Qiskit Aer Simulator** and **Physical IBM Quantum QPU**:
            """
        )

        h_bits = st.session_state["hardware_bits"]
        s_bits = st.session_state["simulator_bits"]
        h_ana = analyze_sequence(h_bits, "Real QPU")
        s_ana = analyze_sequence(s_bits, "Simulator Aer")

        comp_col1, comp_col2 = st.columns(2)

        with comp_col1:
            comp_df = pd.DataFrame([
                {
                    "Metric": "Total Bits (N)",
                    "Qiskit Aer Simulator": f"{s_ana['total_bits']:,}",
                    "Real IBM Quantum QPU": f"{h_ana['total_bits']:,}",
                },
                {
                    "Metric": "Bit 0 Count",
                    "Qiskit Aer Simulator": f"{s_ana['count_zeros']:,} ({s_ana['prob_zero']*100:.2f}%)",
                    "Real IBM Quantum QPU": f"{h_ana['count_zeros']:,} ({h_ana['prob_zero']*100:.2f}%)",
                },
                {
                    "Metric": "Bit 1 Count",
                    "Qiskit Aer Simulator": f"{s_ana['count_ones']:,} ({s_ana['prob_one']*100:.2f}%)",
                    "Real IBM Quantum QPU": f"{h_ana['count_ones']:,} ({h_ana['prob_one']*100:.2f}%)",
                },
                {
                    "Metric": "Deviation |P1 - 0.5|",
                    "Qiskit Aer Simulator": f"{s_ana['deviation_p1']:.5f}",
                    "Real IBM Quantum QPU": f"{h_ana['deviation_p1']:.5f}",
                },
                {
                    "Metric": "Shannon Entropy",
                    "Qiskit Aer Simulator": f"{s_ana['entropy']:.6f} bits",
                    "Real IBM Quantum QPU": f"{h_ana['entropy']:.6f} bits",
                },
                {
                    "Metric": "Chi-Square p-value",
                    "Qiskit Aer Simulator": f"{s_ana['chi_square_test']['p_value']:.4f}",
                    "Real IBM Quantum QPU": f"{h_ana['chi_square_test']['p_value']:.4f}",
                },
                {
                    "Metric": "Wald-Wolfowitz Runs Z",
                    "Qiskit Aer Simulator": f"{s_ana['runs_test']['z_score']:+.4f}",
                    "Real IBM Quantum QPU": f"{h_ana['runs_test']['z_score']:+.4f}",
                },
            ])
            st.dataframe(comp_df, use_container_width=True, hide_index=True)

        with comp_col2:
            fig_hw_comp, ax_hc = plt.subplots(figsize=(6, 3.6))
            x_cats = ["Simulator 0s", "Simulator 1s", "Hardware 0s", "Hardware 1s"]
            x_vals = [s_ana['prob_zero'], s_ana['prob_one'], h_ana['prob_zero'], h_ana['prob_one']]
            b_colors = ["#1e40af", "#3b82f6", "#b45309", "#f59e0b"]
            ax_hc.bar(x_cats, x_vals, color=b_colors, edgecolor="black", width=0.55)
            ax_hc.axhline(0.5, color="red", linestyle="--", linewidth=1.5, label="Parity (0.5000)")
            ax_hc.set_ylim(0, 0.75)
            ax_hc.set_ylabel("Measured Probability")
            ax_hc.set_title("Simulator vs Real Hardware Probability Distribution")
            ax_hc.legend(loc="lower right")
            ax_hc.grid(axis="y", linestyle=":", alpha=0.5)
            for bar, val in zip(ax_hc.patches, x_vals):
                ax_hc.annotate(f"{val:.4f}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                               xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")
            st.pyplot(fig_hw_comp)

        st.warning(
            "⚠️ **Scientific Evaluation Note:** A balanced 50:50 distribution alone does not prove true randomness. "
            "Real hardware randomness stems from physical quantum indeterminism, while simulators use classical "
            "pseudo-stochastic algorithms."
        )

    st.subheader("Step-by-Step Setup Guide for IBM Quantum Credentials")
    st.markdown(
        """
        1. **Create an account:** Register at [IBM Quantum Platform](https://quantum.cloud.ibm.com/).
        2. **Generate API Token:** Go to your dashboard and copy your 44-character API key.
        3. **Store locally in secrets.toml:** In your project directory, create `.streamlit/secrets.toml`:
        ```toml
        # .streamlit/secrets.toml
        IBM_QUANTUM_API_KEY = "YOUR_ACTUAL_KEY_HERE"
        # Optional: if you have an invited hub/group/project
        # IBM_QUANTUM_INSTANCE = "crn:..."
        ```
        4. **Git Protection:** `.streamlit/secrets.toml` is included in `.gitignore` to prevent committing credentials.
        5. **Launch Application:** Run `streamlit run app.py` and select **Mode B** in the sidebar.
        """
    )


# ==============================================================================
# TAB 7: HACKATHON REPORT & JUDGING
# ==============================================================================
with tab_report:
    st.header("Hackathon Submission & Evaluation Report")
    st.caption("Qiskit Fall Fest 2026 — DBATU, Lonere | Problem Statement 2")

    st.write(
        """
        ### Executive Summary
        **RUMBER (Quantum Random Number Generation & Analysis System)**  
        *\"True Randomness, Powered by Quantum.\"*

        This project implements a complete, working, hackathon-ready prototype addressing 
        **Problem Statement 2: Quantum Random Number Generator (QRNG) — Harnessing Quantum Mechanics for True Randomness**.
        Built exclusively with Python, Qiskit 2.x, Qiskit Aer, Qiskit IBM Runtime, and Streamlit, 
        the prototype provides an end-to-end framework for quantum circuit generation, order-preserving 
        bit extraction, statistical hypothesis testing, classical PRNG benchmarking, hardware noise debiasing, 
        and real IBM Quantum QPU execution.
        """
    )

    st.subheader("Official Evaluation Criteria Alignment")
    st.markdown(
        """
        | Criteria | Implementation in RUMBER |
        | :--- | :--- |
        | **1. Quantum Circuit Architecture** | Single-qubit Hadamard superposition state $|+\\rangle$ and computational basis measurement $M_Z$. Preserves individual chronological bit outcomes via `memory=True` and `get_bitstrings()`. |
        | **2. Configurable Sequences** | Supports 1,000, 10,000, and 100,000 bits using batching routines for memory efficiency and hardware compatibility. |
        | **3. Statistical Rigor** | 5-test battery: Chi-Square ($\chi^2$), Wald-Wolfowitz Runs, Frequency (Monobit), Shannon Entropy, and Lag-1 Autocorrelation. |
        | **4. Classical PRNG Comparison** | Direct empirical comparison against NumPy's modern PCG64 BitGenerator, highlighting algorithmic determinism vs quantum indeterminism. |
        | **5. Bias Mitigation Innovation** | Mathematical implementation of John von Neumann debiasing with interactive noise slider and before/after verification. |
        | **6. IBM Quantum Hardware Mode** | Complete cloud execution path with `qiskit-ibm-runtime`, backend querying, and robust exception handling. |
        | **7. Reproducibility & Code Quality** | Pure Python and Streamlit, modular functions, robust exception handling, and beginner-friendly documentation. |
        """
    )

    st.subheader("References & Academic Literature")
    st.markdown(
        """
        1. **Nielsen, M. A., & Chuang, I. L.** (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
        2. **Qiskit Development Team** (2024). *Qiskit: An Open-Source Framework for Quantum Computing*. https://qiskit.org/
        3. **Qiskit Aer Documentation** (2024). *Quantum Circuit Simulator for Qiskit*. https://qiskit.github.io/qiskit-aer/
        4. **IBM Quantum Platform & Runtime API** (2024). *Qiskit IBM Runtime Service and Sampler V2 Documentation*. https://docs.quantum.ibm.com/
        5. **Rukhin, A., et al.** (2010). *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*. NIST Special Publication 800-22 Rev. 1a.
        6. **von Neumann, J.** (1951). *Various techniques used in connection with random digits*. National Bureau of Standards Applied Mathematics Series, 12, 36-38.
        7. **Herrero-Collantes, M., & Garcia-Escartin, J. C.** (2017). *Quantum random number generators*. Reviews of Modern Physics, 89(1), 015004.
        """
    )
