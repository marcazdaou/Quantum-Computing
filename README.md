# Quantum Computing

Quantum computing assignments implemented in **Python** using **Qiskit** and Jupyter Notebooks — covering quantum mechanics fundamentals, gate-based computation, and quantum algorithms.

## Assignments

| # | Topics |
|---|---|
| HW 1 | Qubits, quantum states, Dirac (bra-ket) notation, measurement |
| HW 2 | Single-qubit gates: Pauli-X, Hadamard, Z, S, T; Bloch sphere |
| HW 3 | Multi-qubit systems, tensor products, CNOT gate |
| HW 4 | Quantum entanglement, Bell states, no-cloning theorem |
| HW 5 | Quantum circuits, Born rule, probability amplitudes |
| HW 6 | Grover's search algorithm — quadratic speedup: O(√N) |
| HW 7 | Quantum Fourier Transform (QFT) |
| HW 8 | Quantum phase estimation |
| HW 9 | Introduction to Shor's factoring algorithm |

## Key Concepts

### Superposition
A qubit exists in a linear combination of basis states until measured:
```
|ψ⟩ = α|0⟩ + β|1⟩    where |α|² + |β|² = 1
```

### Entanglement
Bell state — two qubits correlated regardless of distance:
```
|Φ⁺⟩ = (1/√2)(|00⟩ + |11⟩)
```

### Grover's Algorithm
Unstructured database search in **O(√N)** vs classical O(N):
```
Apply Hadamard → Oracle (mark target) → Diffusion (amplify marked state) → Measure
Repeat O(√N) times for near-certain success probability
```

### Quantum Fourier Transform
Quantum analogue of the DFT in **O(n²)** vs classical FFT O(n·2ⁿ):
```
|j⟩ → (1/√N) Σ e^(2πijk/N) |k⟩
```

## Technologies

- **Python 3**
- **Qiskit** — IBM's quantum computing framework
- **Jupyter Notebook**
- NumPy, Matplotlib

## Setup

```bash
pip install qiskit jupyter numpy matplotlib
jupyter notebook
# Open hw1.ipynb → hw9.ipynb in order
```

## Why Quantum Computing Matters

Classical computers solve factoring in exponential time — the foundation of RSA security. Shor's algorithm (HW 9) solves it in **polynomial time** on a quantum computer, demonstrating why quantum computing will reshape cryptography and optimization.