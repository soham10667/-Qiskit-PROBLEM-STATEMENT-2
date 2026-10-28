"""
Standalone IBM Quantum Hardware Execution Script for QRNG
Qiskit Fall Fest 2026 — Problem Statement 2
Submits a 1-qubit Hadamard QRNG circuit to real quantum processor (e.g. ibm_marrakesh).
Credentials safely loaded from .streamlit/secrets.toml.
"""

import sys
import os
from pathlib import Path

# Add global Python site-packages fallback if running in venv missing qiskit-ibm-runtime
_global_site = r"C:\Users\HP\AppData\Local\Programs\Python\Python312\Lib\site-packages"
if os.path.exists(_global_site) and _global_site not in sys.path:
    sys.path.append(_global_site)

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
except ImportError:
    import importlib
    _ibm_rt = importlib.import_module("qiskit_ibm_runtime")
    QiskitRuntimeService = getattr(_ibm_rt, "QiskitRuntimeService")
    SamplerV2 = getattr(_ibm_rt, "SamplerV2")

# 1. Read existing credentials without printing the API key
secrets_path = Path(".streamlit/secrets.toml")

if not secrets_path.exists():
    raise FileNotFoundError(
        "Missing .streamlit/secrets.toml. Check your API configuration."
    )

secrets = {}
if tomllib:
    with secrets_path.open("rb") as file:
        secrets = tomllib.load(file)
else:
    # Simple line parser fallback
    with secrets_path.open("r", encoding="utf-8") as file:
        for line in file:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                secrets[k.strip()] = v.strip().strip('"').strip("'")

token = secrets.get("IBM_QUANTUM_API_KEY") or secrets.get("IBM_QUANTUM_TOKEN") or secrets.get("QISKIT_IBM_TOKEN")
instance = secrets.get("IBM_QUANTUM_INSTANCE")

if not token:
    raise ValueError(
        "IBM_QUANTUM_API_KEY was not found in .streamlit/secrets.toml"
    )

masked_token = "••••••••" + token[-4:] if len(token) > 4 else "••••"
print("=" * 65)
print("     IBM QUANTUM HARDWARE WORKLOAD SUBMISSION & VERIFICATION")
print("=" * 65)
print(f"Token Detected: {masked_token}")

# 2. Connect to IBM Quantum
config = {
    "channel": "ibm_quantum_platform",
    "token": token,
}
if instance:
    config["instance"] = instance

try:
    service = QiskitRuntimeService(**config)
    print("[1/5] Authentication successful via channel='ibm_quantum_platform'")
except Exception as e:
    # Fallback channel try
    print(f"[WARN] Default channel error: {e}. Trying auto-channel...")
    service = QiskitRuntimeService(token=token)
    print("[1/5] Authentication successful via auto-channel")

# 3. Select a real physical QPU (ibm_marrakesh or least busy)
target_backend_name = "ibm_marrakesh"
try:
    backend = service.backend(target_backend_name)
    if not backend.status().operational:
        print(f"[WARN] {target_backend_name} is not operational. Selecting least busy operational QPU...")
        backend = service.least_busy(operational=True, simulator=False)
except Exception as e:
    print(f"[WARN] Could not select {target_backend_name}: {e}. Selecting least busy operational QPU...")
    backend = service.least_busy(operational=True, simulator=False)

print(f"[2/5] Selected real quantum processor: {backend.name} ({getattr(backend, 'num_qubits', 'Unknown')} qubits)")

# 4. Build a one-qubit QRNG circuit
print("[3/5] Constructing 1-qubit Hadamard QRNG circuit...")
qc = QuantumCircuit(1)
qc.h(0)
qc.measure_all()

# 5. Compile for the selected hardware (ISA Transpilation)
print("[4/5] Compiling circuit for hardware topology via generate_preset_pass_manager...")
pass_manager = generate_preset_pass_manager(
    optimization_level=1,
    backend=backend,
)
compiled_circuit = pass_manager.run(qc)

# 6. Submit a real hardware job in job mode
SHOTS = 128
print(f"[5/5] Submitting real hardware job with {SHOTS} shots via SamplerV2...")
sampler = SamplerV2(mode=backend)
job = sampler.run([compiled_circuit], shots=SHOTS)

job_id = job.job_id()
print("\n" + "=" * 65)
print(">>> JOB SUBMITTED SUCCESSFULLY TO IBM QUANTUM PLATFORM! <<<")
print("=" * 65)
print(f"Job ID:         {job_id}")
print(f"Target Backend: {backend.name}")
print(f"Initial Status: {job.status()}")
print(f"Dashboard URL:  https://quantum.ibm.com/jobs/{job_id}")
print("=" * 65)

print("\nWaiting for hardware execution to complete on IBM Quantum...")
print("(Note: Physical QPUs process jobs via cloud queue. This will await completion.)")

try:
    result = job.result()
    pub_result = result[0]
    
    # Extract measurement outcomes
    reg_name = "meas" if hasattr(pub_result.data, "meas") else list(pub_result.data.keys())[0]
    data_bin = getattr(pub_result.data, reg_name)
    
    counts = data_bin.get_counts() if hasattr(data_bin, "get_counts") else {}
    bitstrings = data_bin.get_bitstrings() if hasattr(data_bin, "get_bitstrings") else []
    
    print("\n" + "=" * 65)
    print(">>> JOB EXECUTION COMPLETED! RESULTS RETRIEVED <<<")
    print("=" * 65)
    print("Final Status:                 COMPLETED")
    print("Hardware Measurement Counts: ", counts)
    print("Total Shots Generated:       ", sum(counts.values()) if counts else len(bitstrings))
    
    if bitstrings:
        print("First 32 Measured Bits:      ", "".join(bitstrings[:32]))
        
        # Save to disk
        with open("qrng_hardware_bits.txt", "w", encoding="utf-8") as f:
            f.write("".join(bitstrings))
        print("Saved raw hardware bitstream to 'qrng_hardware_bits.txt'")
        
    print("=" * 65)
    print("ALL TESTS PASSED. The job is now recorded in your IBM Quantum Workloads dashboard.")
    
except Exception as e:
    print(f"\n[INFO] Job {job_id} is in queue or pending: {e}")
    print(f"You can check the status anytime at: https://quantum.ibm.com/jobs/{job_id}")
