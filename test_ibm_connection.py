"""
Test and verify IBM Quantum API connection using credentials stored in .streamlit/secrets.toml
"""

import sys
import os

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# 1. Read token from .streamlit/secrets.toml or env
token = None
secrets_path = os.path.join(".streamlit", "secrets.toml")
if os.path.exists(secrets_path) and tomllib:
    try:
        with open(secrets_path, "rb") as f:
            data = tomllib.load(f)
            token = data.get("IBM_QUANTUM_API_KEY") or data.get("IBM_QUANTUM_TOKEN") or data.get("QISKIT_IBM_TOKEN")
    except Exception as e:
        print(f"[WARN] Could not parse secrets.toml: {e}")

if not token:
    token = os.environ.get("IBM_QUANTUM_API_KEY") or os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")

if not token:
    # Fallback line parsing
    if os.path.exists(secrets_path):
        with open(secrets_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and ("IBM_QUANTUM_API_KEY" in line or "TOKEN" in line):
                    token = line.split("=")[1].strip().strip('"').strip("'")
                    break

if not token:
    print("[ERROR] No IBM Quantum API token found in .streamlit/secrets.toml or environment variables.")
    sys.exit(1)

masked = "••••••••" + token[-4:] if len(token) > 4 else "••••"
print("=" * 65)
print("       IBM QUANTUM CONNECTION & BACKEND VERIFICATION")
print("=" * 65)
print(f"API Key Detected: {masked}")

# 2. Test Qiskit IBM Runtime import
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
    print("[OK] qiskit-ibm-runtime library is installed.")
except ImportError:
    print("\n[ERROR] qiskit-ibm-runtime is NOT installed in the active environment.")
    print("Please install it by running:")
    print("    pip install qiskit-ibm-runtime streamlit\n")
    sys.exit(1)

# 3. Authenticate with IBM Quantum
print("\n[1/2] Connecting to IBM Quantum Platform...")
service = None
auth_error = None

for ch in ["ibm_quantum_platform", "ibm_cloud", None]:
    try:
        if ch:
            service = QiskitRuntimeService(channel=ch, token=token)
        else:
            service = QiskitRuntimeService(token=token)
        print(f"      >> SUCCESS: Authentication successful via channel='{ch or 'default'}'!")
        break
    except Exception as e:
        auth_error = e

if not service:
    print(f"      >> FAILED: Authentication error: {auth_error}")
    sys.exit(1)

# 4. Query real operational QPUs (excluding simulators)
print("\n[2/2] Querying operational real quantum backends (excluding simulators)...")
try:
    backends = service.backends(simulator=False, operational=True)
    if not backends:
        print("      >> No operational physical QPUs currently online for this account.")
    else:
        print(f"      >> Found {len(backends)} operational real quantum processor(s):\n")
        print(f"      {'Backend Name':<20} {'Qubits':<10} {'Pending Jobs (Queue)':<20}")
        print("      " + "-" * 52)
        for b in backends:
            try:
                status = b.status()
                pending = getattr(status, "pending_jobs", "N/A")
            except Exception:
                pending = "N/A"
            print(f"      {b.name:<20} {getattr(b, 'num_qubits', 'N/A'):<10} {pending:<20}")

        least_busy = service.least_busy(simulator=False, operational=True)
        print("      " + "-" * 52)
        print(f"      >> Recommended Least Busy QPU: {least_busy.name}")

    print("\n[ALL SYSTEMS OPERATIONAL] Your IBM Quantum API is fully connected and ready!")
    print("You can now launch the Streamlit app:")
    print("    streamlit run app.py\n")

except Exception as e:
    print(f"      >> Error querying backends: {e}")
