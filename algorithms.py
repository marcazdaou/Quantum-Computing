"""Reusable quantum circuits from the notebooks, tested in tests/test_algorithms.py.

Qiskit orders qubits little-endian: qubit 0 is the least significant bit, so the
basis state |q2 q1 q0> has integer value q2*4 + q1*2 + q0.
"""
from fractions import Fraction
from math import floor, gcd, pi, sqrt

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


# ── Entanglement ──────────────────────────────────────────────────────────────
def bell_state(which: str = "phi+") -> QuantumCircuit:
    """One of the four Bell states on 2 qubits: phi+, phi-, psi+ or psi-."""
    qc = QuantumCircuit(2, name=which)
    if which in ("psi+", "psi-"):
        qc.x(1)                  # start from |01> or |11> for the psi states
    if which in ("phi-", "psi-"):
        qc.x(0)                  # the minus states start with qubit 0 in |1>
    qc.h(0)
    qc.cx(0, 1)
    return qc


def teleportation(theta: float, phi: float) -> QuantumCircuit:
    """Teleport the state Ry(theta) Rz(phi) |0> from qubit 0 (Alice) to qubit 2 (Bob).

    Uses the deferred-measurement form: Bob's corrections are controlled gates
    instead of classically-controlled ones, which gives the same final state for
    Bob and lets the whole protocol be checked with a statevector.
    """
    qc = QuantumCircuit(3, name="teleport")
    qc.ry(theta, 0)
    qc.rz(phi, 0)                # the state to send
    qc.h(1)
    qc.cx(1, 2)                  # Bell pair shared by Alice (q1) and Bob (q2)
    qc.cx(0, 1)
    qc.h(0)                      # Alice's Bell-basis measurement (deferred)
    qc.cx(1, 2)                  # X correction if Alice measured q1 = 1
    qc.cz(0, 2)                  # Z correction if Alice measured q0 = 1
    return qc


# ── Oracles: Deutsch-Jozsa and Grover ─────────────────────────────────────────
def deutsch_jozsa(n: int, balanced_mask: int | None) -> QuantumCircuit:
    """Deutsch-Jozsa on n input qubits (+1 ancilla) without measurement.

    balanced_mask=None uses the constant function f(x) = 0. Otherwise the oracle
    computes f(x) = parity(x AND mask), which is balanced for any non-zero mask.
    The input register measures all zeros if and only if f is constant.
    """
    qc = QuantumCircuit(n + 1, name="deutsch-jozsa")
    qc.x(n)
    qc.h(range(n + 1))
    if balanced_mask:
        for i in range(n):
            if balanced_mask >> i & 1:
                qc.cx(i, n)
    qc.h(range(n))
    return qc


def phase_oracle(n: int, marked: list[str]) -> QuantumCircuit:
    """Flip the phase of each marked basis state (bit strings written q_{n-1} ... q_0)."""
    qc = QuantumCircuit(n, name="oracle")
    for bits in marked:
        zeros = [i for i, b in enumerate(reversed(bits)) if b == "0"]
        if zeros:
            qc.x(zeros)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)   # multi-controlled Z = H . MCX . H
        qc.h(n - 1)
        if zeros:
            qc.x(zeros)
    return qc


def diffuser(n: int) -> QuantumCircuit:
    """Grover diffusion operator: reflection about the uniform superposition."""
    qc = QuantumCircuit(n, name="diffuser")
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def grover_iterations(n: int, solutions: int) -> int:
    """Optimal number of Grover iterations, floor(pi/4 * sqrt(N/M))."""
    return max(1, floor(pi / 4 * sqrt(2 ** n / solutions)))


def grover(n: int, marked: list[str], iterations: int | None = None) -> QuantumCircuit:
    """Grover search for the marked states (no measurement)."""
    qc = QuantumCircuit(n, name="grover")
    qc.h(range(n))
    oracle, diff = phase_oracle(n, marked), diffuser(n)
    for _ in range(iterations or grover_iterations(n, len(marked))):
        qc.compose(oracle, inplace=True)
        qc.compose(diff, inplace=True)
    return qc


# ── Quantum Fourier transform ─────────────────────────────────────────────────
def qft(n: int, swaps: bool = True) -> QuantumCircuit:
    """Quantum Fourier transform on n qubits: |x> -> (1/sqrt(2^n)) sum_k e^(2 pi i x k / 2^n) |k>.

    Built from Hadamards and controlled phase rotations (O(n^2) gates), followed
    by swaps that reverse the qubit order.
    """
    qc = QuantumCircuit(n, name="QFT")
    for target in reversed(range(n)):
        qc.h(target)
        for control in reversed(range(target)):
            qc.cp(pi / 2 ** (target - control), control, target)
    if swaps:
        for i in range(n // 2):
            qc.swap(i, n - 1 - i)
    return qc


def inverse_qft(n: int) -> QuantumCircuit:
    qc = qft(n).inverse()
    qc.name = "QFT†"
    return qc


# ── Shor's algorithm for N = 15 ───────────────────────────────────────────────
MULTIPLIERS_MOD_15 = (1, 2, 4, 7, 8, 11, 13, 14)


def multiply_mod_15(b: int) -> QuantumCircuit:
    """4-qubit circuit for |y> -> |b*y mod 15> (for 1 <= y <= 14), with b coprime to 15.

    Multiplying by 2 mod 15 is a cyclic shift of the 4 bits (2^4 = 16 = 1 mod 15),
    so every multiplier is built from bit rotations, plus X gates because
    multiplying by 15 - b = -b mod 15 is the same as complementing the bits.
    """
    if b not in MULTIPLIERS_MOD_15:
        raise ValueError(f"{b} is not coprime to 15")
    qc = QuantumCircuit(4, name=f"×{b} mod 15")
    shifts = {1: 0, 2: 1, 4: 2, 8: 3, 14: 0, 13: 1, 11: 2, 7: 3}[b]   # b or 15 - b is 2^shifts
    for _ in range(shifts):                                          # rotate left by one bit
        qc.swap(2, 3)
        qc.swap(1, 2)
        qc.swap(0, 1)
    if b in (7, 11, 13, 14):
        qc.x(range(4))
    return qc


def order_finding_circuit(a: int, n_count: int = 8) -> QuantumCircuit:
    """Quantum phase estimation of the unitary |y> -> |a*y mod 15>.

    Counting register: qubits 0 .. n_count-1. Work register: the next 4 qubits,
    initialised to |1>. The controlled powers U^(2^j) multiply by a^(2^j) mod 15,
    which is computed classically when building the circuit (as in any
    implementation of modular exponentiation).
    """
    qc = QuantumCircuit(n_count + 4, n_count, name=f"order({a})")
    qc.h(range(n_count))
    qc.x(n_count)                                    # work register = |0001> = 1
    for j in range(n_count):
        b = pow(a, 2 ** j, 15)
        if b != 1:
            gate = multiply_mod_15(b).to_gate().control()
            qc.append(gate, [j] + list(range(n_count, n_count + 4)))
    qc.append(inverse_qft(n_count).to_gate(label="QFT†"), range(n_count))   # one box when drawn
    qc.measure(range(n_count), range(n_count))
    return qc


def order_from_measurement(value: int, n_count: int, N: int = 15) -> int:
    """Turn a phase-estimation result into a candidate order r via continued fractions."""
    return Fraction(value, 2 ** n_count).limit_denominator(N).denominator


def find_order(a: int, shots: int = 64, n_count: int = 8, seed: int = 7) -> tuple[int, dict]:
    """Run order finding and return (r, counts): the smallest r > 1 with a^r = 1 mod 15 among the results."""
    sim = AerSimulator(seed_simulator=seed)
    qc = order_finding_circuit(a, n_count)
    counts = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
    candidates = sorted({order_from_measurement(int(k, 2), n_count) for k in counts})
    for r in candidates:
        if r > 1 and pow(a, r, 15) == 1:
            return r, counts
    return 0, counts


def shor_15(a: int, **kwargs) -> tuple[int, int] | None:
    """Factor 15 with base a: find the order r, then gcd(a^(r/2) +- 1, 15)."""
    if gcd(a, 15) != 1:                               # lucky guess: a shares a factor with 15
        return tuple(sorted((gcd(a, 15), 15 // gcd(a, 15))))
    r, _ = find_order(a, **kwargs)
    if r == 0 or r % 2 or pow(a, r // 2, 15) == 14:   # odd order or a^(r/2) = -1: try another a
        return None
    p = gcd(pow(a, r // 2) - 1, 15)
    q = gcd(pow(a, r // 2) + 1, 15)
    factors = sorted(f for f in (p, q) if f not in (1, 15))
    return (factors[0], 15 // factors[0]) if factors else None
