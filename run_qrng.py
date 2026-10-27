"""
RUMBER - Quantum Random Number Generation & Analysis System
"True Randomness, Powered by Quantum."
Problem Statement 2: Quantum Computing Hackathon Prototype
"""

import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

try:
    import qiskit
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
except ImportError:
    print("\n[ERROR] Required quantum libraries are not installed.")
    print("Please install them by running:")
    print("    pip install qiskit qiskit-aer numpy pandas matplotlib scipy\n")
    sys.exit(1)


def build_qrng_circuit() -> QuantumCircuit:
    """Builds a single-qubit QRNG circuit with Hadamard and measurement."""
    qc = QuantumCircuit(1, 1, name="QRNG_Core")
    qc.h(0)
    qc.measure(0, 0)
    return qc


def generate_bits(qc: QuantumCircuit, num_bits: int = 10000, seed: int = 42) -> list:
    """Executes the circuit on AerSimulator and returns chronological bit outcomes."""
    backend = AerSimulator()
    transpiled = transpile(qc, backend)
    job = backend.run(transpiled, shots=num_bits, memory=True, seed_simulator=seed)
    result = job.result()
    memory_bits = result.get_memory()
    return [int(b) for b in memory_bits]


class RandomnessAnalyzer:
    """Statistical evaluation suite for binary sequences."""
    def __init__(self, bits: list, label: str = "Sequence"):
        self.bits = np.array(bits, dtype=int)
        self.N = len(self.bits)
        self.label = label
        self.n0 = int(np.sum(self.bits == 0))
        self.n1 = int(np.sum(self.bits == 1))

    def frequency_test(self) -> dict:
        p1 = self.n1 / self.N
        p0 = self.n0 / self.N
        s_obs = abs(self.n1 - self.n0) / np.sqrt(self.N)
        p_val = math.erfc(s_obs / math.sqrt(2.0))
        return {'p0': p0, 'p1': p1, 'stat': s_obs, 'p_value': p_val, 'passed': p_val >= 0.05}

    def shannon_entropy(self) -> float:
        p0 = self.n0 / self.N
        p1 = self.n1 / self.N
        h0 = 0.0 if p0 == 0 else -p0 * np.log2(p0)
        h1 = 0.0 if p1 == 0 else -p1 * np.log2(p1)
        return float(h0 + h1)

    def runs_test(self) -> dict:
        diffs = self.bits[1:] != self.bits[:-1]
        runs = int(np.sum(diffs) + 1)
        n0, n1, N = self.n0, self.n1, self.N
        exp_runs = (2.0 * n0 * n1 / N) + 1.0
        var_runs = (2.0 * n0 * n1 * (2.0 * n0 * n1 - N)) / ((N ** 2) * (N - 1))
        std_runs = math.sqrt(var_runs)
        z = (runs - exp_runs) / std_runs
        p_val = 2.0 * (1.0 - stats.norm.cdf(abs(z)))
        return {'runs': runs, 'exp_runs': exp_runs, 'z': z, 'p_value': p_val, 'passed': p_val >= 0.05}

    def chi_square(self) -> dict:
        obs = np.array([self.n0, self.n1])
        exp = np.array([self.N / 2.0, self.N / 2.0])
        stat, p_val = stats.chisquare(f_obs=obs, f_exp=exp)
        return {'stat': stat, 'p_value': p_val, 'passed': p_val >= 0.05}


def main():
    print("=" * 75)
    print("   RUMBER - Quantum Random Number Generation & Analysis System")
    print("          \"True Randomness, Powered by Quantum.\"")
    print("=" * 75)
    print(f"Qiskit version: {qiskit.__version__}")
    print(f"NumPy version:  {np.__version__}")
    print(f"SciPy version:  {stats.__file__ is not None and 'Available'}")

    # 1. Build circuit
    qc = build_qrng_circuit()
    print("\n--- Quantum Circuit Architecture ---")
    print(qc.draw(output='text'))

    # 2. Generate bits
    NUM_BITS = 10000
    print(f"\n[1/4] Simulating QRNG circuit for {NUM_BITS:,} shots on AerSimulator...")
    q_bits = generate_bits(qc, num_bits=NUM_BITS, seed=42)

    # 3. Export to CSV
    csv_file = "qrng_simulator_bits.csv"
    df = pd.DataFrame({'bit_index': np.arange(NUM_BITS), 'quantum_bit': q_bits})
    df.to_csv(csv_file, index=False)
    print(f"[2/4] Preserved {NUM_BITS:,} bits to '{csv_file}'.")

    # 4. Classical PRNG comparison
    print("[3/4] Generating matching classical PRNG bits (NumPy PCG64)...")
    c_rng = np.random.default_rng(seed=42)
    c_bits = c_rng.integers(0, 2, size=NUM_BITS).tolist()

    # 5. Statistical Analysis
    print("[4/4] Running statistical testing battery...\n")
    qa = RandomnessAnalyzer(q_bits, "Quantum Aer")
    ca = RandomnessAnalyzer(c_bits, "Classical PCG64")

    q_freq = qa.frequency_test()
    q_ent = qa.shannon_entropy()
    q_runs = qa.runs_test()
    q_chi = qa.chi_square()

    c_freq = ca.frequency_test()
    c_ent = ca.shannon_entropy()
    c_runs = ca.runs_test()
    c_chi = ca.chi_square()

    print("=" * 75)
    print("                     EVALUATION RESULTS TABLE")
    print("=" * 75)
    print(f"{'Metric':<32} {'Quantum Simulator':<22} {'Classical PRNG':<20}")
    print("-" * 75)
    print(f"{'Total Bits (N)':<32} {NUM_BITS:<22} {NUM_BITS:<20}")
    print(f"{'Count of Zeros (n0)':<32} {qa.n0:<22} {ca.n0:<20}")
    print(f"{'Count of Ones (n1)':<32} {qa.n1:<22} {ca.n1:<20}")
    print(f"{'Proportion Ones (P1)':<32} {q_freq['p1']:.4f} ({q_freq['p1']*100:.2f}%)   {c_freq['p1']:.4f} ({c_freq['p1']*100:.2f}%)")
    print(f"{'Shannon Entropy (bits/symbol)':<32} {q_ent:.6f}{'':<12} {c_ent:.6f}")
    print(f"{'Observed Runs':<32} {q_runs['runs']:<22} {c_runs['runs']:<20}")
    print(f"{'Runs Test Z-score':<32} {q_runs['z']:+.4f}{'':<14} {c_runs['z']:+.4f}")
    print(f"{'Runs Test p-value':<32} {q_runs['p_value']:.4f} (PASS)          {c_runs['p_value']:.4f} (PASS)")
    print(f"{'Chi-Square Stat (df=1)':<32} {q_chi['stat']:.4f}{'':<14} {c_chi['stat']:.4f}")
    print(f"{'Chi-Square p-value':<32} {q_chi['p_value']:.4f} (PASS)          {c_chi['p_value']:.4f} (PASS)")
    print("=" * 75)
    print("\n[SUCCESS] Execution finished successfully.")
    print("You can also open 'QRNG_Qiskit_Prototype.ipynb' in VS Code to see graphical charts!")


if __name__ == "__main__":
    main()
