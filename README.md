# Quantum Computing

Quantum computing implementations and experiments in **Python** using **Qiskit** and Jupyter Notebooks — covering quantum mechanics fundamentals, gate-based computation, and quantum algorithms.

## Notebooks

| Notebook | Topic |
|---|---|
| [01_math_foundations_and_setup.ipynb](01_math_foundations_and_setup.ipynb) | Linear algebra for QC, complex numbers, Dirac notation, environment setup |
| [02_quantum_states_and_bloch_sphere.ipynb](02_quantum_states_and_bloch_sphere.ipynb) | Qubit representation, state vectors, Bloch sphere visualization |
| [03_quantum_gates_and_superposition.ipynb](03_quantum_gates_and_superposition.ipynb) | Pauli-X/Y/Z, Hadamard, S/T gates, rotation gates, superposition states |
| [04_multi_qubit_systems_and_tensor_products.ipynb](04_multi_qubit_systems_and_tensor_products.ipynb) | Tensor products, CNOT, multi-qubit state space |
| [05_bell_states_and_entanglement.ipynb](05_bell_states_and_entanglement.ipynb) | All four Bell states, quantum entanglement, no-cloning theorem |
| [06_measurement_born_rule_and_interference.ipynb](06_measurement_born_rule_and_interference.ipynb) | Born rule, state collapse, constructive/destructive interference |
| [07_quantum_teleportation_and_superdense_coding.ipynb](07_quantum_teleportation_and_superdense_coding.ipynb) | Quantum teleportation protocol, superdense coding, Bell measurement |
| [08_qkd_oracles_and_deutsch_jozsa.ipynb](08_qkd_oracles_and_deutsch_jozsa.ipynb) | BB84 quantum key distribution, phase oracles, Deutsch-Jozsa algorithm |
| [09_grovers_search_algorithm.ipynb](09_grovers_search_algorithm.ipynb) | Grover oracle construction, amplitude amplification, O(√N) search |

## Key Algorithms

### Grover's Search — O(√N)
Quadratic speedup for unstructured search. Classical brute-force requires O(N); Grover's finds the target in O(√N) with near-certain probability.
```
Prepare uniform superposition → Apply oracle (mark target) → Apply diffusion operator → Repeat √N times → Measure
```

### Deutsch-Jozsa Algorithm
Determines whether a function is constant or balanced in a **single** quantum query vs O(2^(n-1)+1) classically.

### Quantum Teleportation
Transmits an unknown qubit state using one entangled Bell pair and two classical bits — no quantum channel required after initial entanglement.

### BB84 Quantum Key Distribution
First quantum cryptography protocol. Encodes bits in qubit basis choices; any eavesdropping introduces detectable errors.

## Technologies

- **Python 3**
- **Qiskit** — IBM's open-source quantum computing framework
- **Jupyter Notebook**
- NumPy, Matplotlib

## Setup

```bash
pip install qiskit jupyter numpy matplotlib
jupyter notebook
```

## Why This Matters

Classical RSA security relies on the hardness of integer factorization. Shor's algorithm solves it in polynomial time on a quantum computer — making quantum computing one of the most consequential areas of modern computer science.
