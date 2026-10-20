"""Physics checks for the circuits in algorithms.py (exact statevector results unless noted)."""
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Operator, Statevector, partial_trace, state_fidelity

import algorithms as alg


def probabilities(qc):
    return Statevector(qc).probabilities_dict()


# ── Entanglement ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize("which, outcomes", [
    ("phi+", {"00", "11"}), ("phi-", {"00", "11"}), ("psi+", {"01", "10"}), ("psi-", {"01", "10"}),
])
def test_bell_states_give_perfectly_correlated_5050_outcomes(which, outcomes):
    probs = {k: v for k, v in probabilities(alg.bell_state(which)).items() if v > 1e-12}
    assert set(probs) == outcomes
    assert all(v == pytest.approx(0.5) for v in probs.values())


def test_bell_states_are_maximally_entangled():
    for which in ("phi+", "phi-", "psi+", "psi-"):
        one_qubit = partial_trace(Statevector(alg.bell_state(which)), [1])
        assert one_qubit.purity() == pytest.approx(0.5)         # a product state would have purity 1


def test_the_four_bell_states_are_orthogonal():
    states = [Statevector(alg.bell_state(w)) for w in ("phi+", "phi-", "psi+", "psi-")]
    overlaps = np.array([[abs(a.inner(b)) for b in states] for a in states])
    assert np.allclose(overlaps, np.eye(4))


@pytest.mark.parametrize("theta, phi", [(0.0, 0.0), (np.pi, 0.0), (np.pi / 2, np.pi / 4), (1.234, -2.1)])
def test_teleportation_delivers_the_exact_state_to_bob(theta, phi):
    prep = QuantumCircuit(1)
    prep.ry(theta, 0)
    prep.rz(phi, 0)
    expected = Statevector.from_label("0").evolve(prep)
    bob = partial_trace(Statevector(alg.teleportation(theta, phi)), [0, 1])   # trace out Alice's qubits
    assert state_fidelity(bob, DensityMatrix(expected)) == pytest.approx(1.0)


# ── Deutsch-Jozsa and Grover ──────────────────────────────────────────────────
def input_register_all_zero_probability(qc, n):
    probs = probabilities(qc)
    return sum(p for k, p in probs.items() if k[-n:] == "0" * n)


@pytest.mark.parametrize("mask", [0b001, 0b101, 0b111])
def test_deutsch_jozsa_identifies_balanced_functions_in_one_query(mask):
    assert input_register_all_zero_probability(alg.deutsch_jozsa(3, mask), 3) == pytest.approx(0.0)


def test_deutsch_jozsa_identifies_the_constant_function():
    assert input_register_all_zero_probability(alg.deutsch_jozsa(3, None), 3) == pytest.approx(1.0)


def test_phase_oracle_flips_only_the_marked_state():
    diagonal = np.diag(Operator(alg.phase_oracle(3, ["101"])).data)
    expected = np.ones(8)
    expected[0b101] = -1
    assert np.allclose(diagonal, expected)


@pytest.mark.parametrize("n, marked, minimum", [(3, ["101"], 0.94), (4, ["1010"], 0.96), (5, ["11011"], 0.99),
                                                (4, ["0011", "1100"], 0.90)])
def test_grover_finds_marked_states_with_high_probability(n, marked, minimum):
    probs = probabilities(alg.grover(n, marked))
    assert sum(probs.get(m, 0) for m in marked) >= minimum


def test_grover_optimal_iterations():
    assert alg.grover_iterations(4, 1) == 3          # floor(pi/4 * 4)
    assert alg.grover_iterations(10, 1) == 25        # floor(pi/4 * 32)


def test_too_many_grover_iterations_overshoot():
    best = probabilities(alg.grover(4, ["0110"]))["0110"]
    overshoot = probabilities(alg.grover(4, ["0110"], iterations=6))["0110"]
    assert overshoot < best                           # amplitude rotates past the marked state


# ── Quantum Fourier transform ─────────────────────────────────────────────────
@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_matrix_equals_the_discrete_fourier_transform(n):
    N = 2 ** n
    dft = np.array([[np.exp(2j * np.pi * j * k / N) for j in range(N)] for k in range(N)]) / np.sqrt(N)
    assert np.allclose(Operator(alg.qft(n)).data, dft)


@pytest.mark.parametrize("n", [3, 4])
def test_qft_agrees_with_numpy_fft_on_a_random_state(n):
    rng = np.random.default_rng(n)
    amplitudes = rng.normal(size=2 ** n) + 1j * rng.normal(size=2 ** n)
    amplitudes /= np.linalg.norm(amplitudes)
    transformed = Statevector(amplitudes).evolve(alg.qft(n)).data
    assert np.allclose(transformed, np.fft.ifft(amplitudes, norm="ortho"))


def test_inverse_qft_undoes_the_qft():
    assert np.allclose(Operator(alg.qft(4).compose(alg.inverse_qft(4))).data, np.eye(16))


# ── Shor's algorithm for 15 ───────────────────────────────────────────────────
@pytest.mark.parametrize("b", alg.MULTIPLIERS_MOD_15)
def test_modular_multiplication_circuits(b):
    U = alg.multiply_mod_15(b)
    for y in range(1, 15):
        out = Statevector.from_int(y, 16).evolve(U)
        assert out.equiv(Statevector.from_int(b * y % 15, 16)), f"{b} * {y} mod 15"


def test_multiplier_rejects_non_coprime_values():
    with pytest.raises(ValueError):
        alg.multiply_mod_15(5)


def test_continued_fractions_recover_the_order():
    # With 8 counting qubits, order 4 gives phases s/4 -> measured values 0, 64, 128, 192
    assert alg.order_from_measurement(64, 8) == 4
    assert alg.order_from_measurement(192, 8) == 4
    assert alg.order_from_measurement(128, 8) == 2     # s/r = 2/4 = 1/2: only a factor of r, as in Shor's analysis


@pytest.mark.parametrize("a, order", [(2, 4), (4, 2), (7, 4), (8, 4), (11, 2), (13, 4)])
def test_order_finding_on_the_simulator(a, order):
    r, counts = alg.find_order(a, shots=128, seed=11)
    assert r == order
    # Phase estimation only produces multiples of 2^8 / r
    assert all(int(k, 2) % (256 // order) == 0 for k in counts)


@pytest.mark.parametrize("a", [2, 7, 8, 11, 13])
def test_shor_factors_15(a):
    assert alg.shor_15(a, shots=128, seed=3) == (3, 5)


def test_shor_handles_a_base_sharing_a_factor_with_15():
    assert alg.shor_15(6) == (3, 5)


def test_shor_reports_failure_when_a_to_the_r_over_2_is_minus_one():
    # 14 = -1 mod 15 has order 2 and 14^1 = -1, so this base gives no factor (the algorithm picks another a)
    assert alg.shor_15(14, shots=64, seed=3) is None
