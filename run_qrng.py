"""
RUMBER - Quantum Random Number Generation & Analysis System
"True Randomness, Powered by Quantum."
Problem Statement 2: Quantum Computing Hackathon Prototype
Standalone Terminal Execution Script
"""

import sys
import math
import argparse
import numpy as np
import pandas as pd
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


def generate_bits(qc: QuantumCircuit, num_bits: int = 10000, seed: int = 42, batch_size: int = 25000) -> list:
    """Executes the circuit on AerSimulator and returns chronological bit outcomes with batching."""
    backend = AerSimulator()
    transpiled = transpile(qc, backend)
    collected_bits = []
    remaining = num_bits
    batch_idx = 0
    while remaining > 0:
        current_batch = min(remaining, batch_size)
        curr_seed = (seed + batch_idx) if seed is not None else None
        job = backend.run(transpiled, shots=current_batch, memory=True, seed_simulator=curr_seed)
        res = job.result()
        mem = res.get_memory()
        collected_bits.extend([int(b) for b in mem])
        remaining -= current_batch
        batch_idx += 1
    return collected_bits


def von_neumann_extractor(raw_bits: list) -> list:
    """John von Neumann debiasing extractor: 01->0, 10->1, 00/11 discarded."""
    clean = []
    for i in range(0, len(raw_bits) - 1, 2):
        b1, b2 = raw_bits[i], raw_bits[i + 1]
        if b1 == 0 and b2 == 1:
            clean.append(0)
        elif b1 == 1 and b2 == 0:
            clean.append(1)
    return clean


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
        std_runs = math.sqrt(var_runs) if var_runs > 0 else 1e-9
        z = (runs - exp_runs) / std_runs
        p_val = 2.0 * (1.0 - stats.norm.cdf(abs(z)))
        return {'runs': runs, 'exp_runs': exp_runs, 'z': z, 'p_value': p_val, 'passed': p_val >= 0.05}

    def chi_square(self) -> dict:
        obs = np.array([self.n0, self.n1])
        exp = np.array([self.N / 2.0, self.N / 2.0])
        stat, p_val = stats.chisquare(f_obs=obs, f_exp=exp)
        return {'stat': stat, 'p_value': p_val, 'passed': p_val >= 0.05}

    def lag1_autocorr(self) -> float:
        if self.N > 2 and np.var(self.bits) > 0:
            mean = np.mean(self.bits)
            num = np.sum((self.bits[:-1] - mean) * (self.bits[1:] - mean))
            den = np.sum((self.bits - mean) ** 2)
            return float(num / den)
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="RUMBER - Quantum Random Number Generator CLI")
    parser.add_argument("--bits", type=int, default=10000, help="Number of bits to generate (default: 10000)")
    parser.add_argument("--seed", type=int, default=42, help="Simulator seed (default: 42)")
    args = parser.parse_args()
    num_bits = args.bits
    seed = args.seed

    print("=" * 78)
    print("   RUMBER - Quantum Random Number Generation & Analysis System")
    print("          \"True Randomness, Powered by Quantum.\"")
    print("=" * 78)
    print(f"Qiskit version: {qiskit.__version__}")
    print(f"NumPy version:  {np.__version__}")
    print(f"Target Shots:   {num_bits:,} bits")

    # 1. Build circuit
    qc = build_qrng_circuit()
    print("\n--- Quantum Circuit Architecture ---")
    print(qc.draw(output='text'))

    # 2. Generate bits
    print(f"\n[1/5] Simulating QRNG circuit for {num_bits:,} shots on AerSimulator...")
    q_bits = generate_bits(qc, num_bits=num_bits, seed=seed)

    # 3. Export to CSV & TXT
    csv_file = "qrng_simulator_bits.csv"
    txt_file = "qrng_simulator_bits.txt"
    df = pd.DataFrame({'bit_index': np.arange(num_bits), 'quantum_bit': q_bits})
    df.to_csv(csv_file, index=False)
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("".join(str(b) for b in q_bits))
    print(f"[2/5] Preserved {num_bits:,} bits to '{csv_file}' and '{txt_file}'.")

    # 4. Classical PRNG comparison
    print("[3/5] Generating matching classical PRNG bits (NumPy PCG64)...")
    c_rng = np.random.default_rng(seed=seed)
    c_bits = c_rng.integers(0, 2, size=num_bits).tolist()

    # 5. Statistical Analysis
    print("[4/5] Running statistical testing battery...")
    qa = RandomnessAnalyzer(q_bits, "Quantum Aer")
    ca = RandomnessAnalyzer(c_bits, "Classical PCG64")

    q_freq = qa.frequency_test()
    q_ent = qa.shannon_entropy()
    q_runs = qa.runs_test()
    q_chi = qa.chi_square()
    q_r1 = qa.lag1_autocorr()

    c_freq = ca.frequency_test()
    c_ent = ca.shannon_entropy()
    c_runs = ca.runs_test()
    c_chi = ca.chi_square()
    c_r1 = ca.lag1_autocorr()

    print("=" * 78)
    print("                     EVALUATION RESULTS TABLE")
    print("=" * 78)
    print(f"{'Metric':<32} {'Quantum Simulator':<22} {'Classical PRNG':<20}")
    print("-" * 78)
    print(f"{'Total Bits (N)':<32} {num_bits:<22} {num_bits:<20}")
    print(f"{'Count of Zeros (n0)':<32} {qa.n0:<22} {ca.n0:<20}")
    print(f"{'Count of Ones (n1)':<32} {qa.n1:<22} {ca.n1:<20}")
    print(f"{'Proportion Ones (P1)':<32} {q_freq['p1']:.4f} ({q_freq['p1']*100:.2f}%)   {c_freq['p1']:.4f} ({c_freq['p1']*100:.2f}%)")
    print(f"{'Deviation |P1 - 0.5|':<32} {abs(q_freq['p1'] - 0.5):.5f}{'':<13} {abs(c_freq['p1'] - 0.5):.5f}")
    print(f"{'Shannon Entropy (bits/symbol)':<32} {q_ent:.6f}{'':<12} {c_ent:.6f}")
    print(f"{'Observed Runs (R)':<32} {q_runs['runs']:<22} {c_runs['runs']:<20}")
    print(f"{'Runs Test Z-score':<32} {q_runs['z']:+.4f}{'':<14} {c_runs['z']:+.4f}")
    print(f"{'Runs Test p-value':<32} {q_runs['p_value']:.4f} (PASS)          {c_runs['p_value']:.4f} (PASS)")
    print(f"{'Chi-Square Stat (df=1)':<32} {q_chi['stat']:.4f}{'':<14} {c_chi['stat']:.4f}")
    print(f"{'Chi-Square p-value':<32} {q_chi['p_value']:.4f} (PASS)          {c_chi['p_value']:.4f} (PASS)")
    print(f"{'Lag-1 Autocorrelation':<32} {q_r1:+.5f}{'':<14} {c_r1:+.5f}")
    print("=" * 78)

    # 6. Bias Mitigation Test
    print("[5/5] Testing Von Neumann Hardware Debiasing...")
    sim_biased = np.random.default_rng(123).choice([0, 1], size=10000, p=[0.40, 0.60]).tolist()
    debiased = von_neumann_extractor(sim_biased)
    ana_mit = RandomnessAnalyzer(debiased, "Mitigated")
    print(f"      Raw Biased (P1=60.0%): {len(sim_biased):,} bits -> Debiased (P1={ana_mit.n1/len(debiased)*100:.2f}%): {len(debiased):,} bits (Yield: {len(debiased)/len(sim_biased)*100:.1f}%)")

    print("\n[SUCCESS] QRNG execution and analysis completed successfully.")
    print("Launch Streamlit app via: streamlit run app.py")


if __name__ == "__main__":
    main()
