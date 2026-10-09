"""Generate the teaching notebooks. Run with Python; no third-party imports needed."""
import json
import re
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
INSTALL = '%pip install -q qiskit==2.2.3 numpy==2.2.6 matplotlib==3.10.3 pylatexenc==2.10 sympy==1.14.0'
COMMON = '''
import sys
from importlib.metadata import version
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector, DensityMatrix
from qiskit.primitives import StatevectorSampler

SEED, SHOTS = 42, 2048
print('Python:', sys.version.split()[0])
for package in ['qiskit', 'numpy', 'matplotlib', 'pylatexenc', 'sympy']:
    print(f'{package}: {version(package)}')

def exact(circuit):
    # Supply a circuit WITHOUT measurements. This is simulator-only inspection.
    return Statevector.from_instruction(circuit).probabilities_dict()

def sample(circuit, qubits=None):
    # Copy so that the original circuit stays available for state inspection.
    qubits = list(range(circuit.num_qubits)) if qubits is None else list(qubits)
    measured = circuit.copy()
    readout = ClassicalRegister(len(qubits), 'readout')
    measured.add_register(readout)
    measured.measure(qubits, readout)
    sampler = StatevectorSampler(seed=SEED)
    return sampler.run([measured], shots=SHOTS).result()[0].data.readout.get_counts()

def compare(circuit, title):
    probabilities, counts = exact(circuit), sample(circuit)
    labels = [format(i, f'0{circuit.num_qubits}b') for i in range(2**circuit.num_qubits)]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(x - .18, [probabilities.get(k, 0) for k in labels], .36, label='Exact probability')
    ax.bar(x + .18, [counts.get(k, 0) / SHOTS for k in labels], .36, label=f'Sampled frequency ({SHOTS} shots)')
    ax.set(xticks=x, xticklabels=labels, ylim=(0, 1.12), ylabel='Probability / frequency', xlabel='Measured bit string', title=title)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    print('Counts:', counts)
    return counts

def show(circuit):
    display(circuit.draw('mpl', fold=70))
    plt.show()
'''

def readable_math(expression):
    """Keep teaching notation readable in previews without a math renderer."""
    matrices = r'X=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad H=\frac{1}{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},\quad Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.'
    bell_steps = r'|00\rangle\longrightarrow\frac{|00\rangle+|01\rangle}{\sqrt2}\longrightarrow\frac{|00\rangle+|11\rangle}{\sqrt2}=|\Phi^+\rangle.'
    if expression == matrices:
        return 'X = [0  1]    H = (1/√2) [1   1]    Z = [1   0]\n    [1  0]               [1  −1]        [0  −1]'
    if expression == bell_steps:
        return '|00⟩ → (|00⟩ + |01⟩)/√2 → (|00⟩ + |11⟩)/√2 = |Φ⁺⟩'
    replacements = {
        r'\sqrt{p(1-p)/2048}': '√(p(1−p)/2048)',
        r'\sqrt{0.3}': '√0.3', r'\sqrt{0.7}': '√0.7',
        r'\sqrt{3}': '√3', r'\sqrt2': '√2',
        r'\sqrt N': '√N', r'\sqrt p': '√p',
        r'\sin^2': 'sin²', r'\sin': 'sin', r'\cos': 'cos',
        r'\arcsin': 'arcsin', r'\theta': 'θ', r'\phi': 'φ',
        r'\alpha': 'α', r'\beta': 'β', r'\psi': 'ψ',
        r'\Phi^+': 'Φ⁺', r'\pi': 'π', r'\rangle': '⟩',
        r'\langle': '⟨', r'\otimes': '⊗', r'\oplus': '⊕',
        r'\cdot': '·', r'\pmod2': ' (mod 2)', r'\leq': ' ≤ ',
        r'\bar a': 'mean(a)', 'q_1': 'q₁', 'q_0': 'q₀',
        'R_y': 'Rᵧ', 'U_f': 'U_f', 'f_s': 'f_s', 'a_x': 'aₓ',
        '^2': '²', '^T': 'ᵀ', '^b': 'ᵇ', '^a': 'ᵃ',
        '^{f(x)}': 'ᶠ⁽ˣ⁾',
    }
    for original, replacement in replacements.items():
        expression = expression.replace(original, replacement)
    if '\\' in expression or '{' in expression or '}' in expression:
        raise ValueError(f'Unconverted math notation: {expression}')
    return expression


def format_markdown(s):
    s = dedent(s).strip()
    s = re.sub(r'\$\$([\s\S]*?)\$\$', lambda m: '\n\n```text\n' + readable_math(m[1]) + '\n```\n\n', s)
    s = re.sub(r'\$([^$\n]+)\$', lambda m: '`' + readable_math(m[1]) + '`', s)
    return re.sub(r'\n{3,}', '\n\n', s) + '\n'


def md(s):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': format_markdown(s)}

def code(s):
    return {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': dedent(s).strip() + '\n'}

def exercise(number, title, task, hint, solution):
    return md(f'''### Exercise {number} — {title}

{task}

Record your prediction before editing the baseline cell below. Run it, explain the result, then make the requested change.

<details><summary>Hint</summary>

{hint}

</details>

<details><summary>Worked solution — open after attempting</summary>

{solution}

</details>''')

def intro(n, title, objectives, agenda, recap):
    return [md(f'''# Lab {n}: {title}

**Audience:** comfortable with Python and basic linear algebra; no prior quantum computing required for Lab 1.

## Learning objectives

{objectives}

## How to use this notebook

Open [Google Colab](https://colab.research.google.com/), choose **File → Upload notebook**, and upload this file. Connect to a standard Python CPU runtime. Run cells in order with Shift+Enter. No IBM account, token, GPU, or paid service is needed. Internet access is needed for package installation only. If changing an already-used package version, restart the session after installation and rerun from the imports cell. These notebooks target Python 3.10–3.13.

For each experiment: **explain → predict → run → interpret → modify**. Write predictions and observations in a new text cell or your notes. Exercise starter cells are working examples, not finished answers to every requested change. Hints and solutions are collapsed below the prompts. Keep optional extensions until after the core lab.

## Agenda

{agenda}

## Prerequisite recap

{recap}

**Instructor guidance:** have pairs compare predictions before running code. A fast learner can attempt the optional extension while others finish.
'''), md('''## Setup

The first cell installs a fixed teaching environment. Installation may take a few minutes. The helper functions below build explicit classical measurement registers and use 2,048 shots with seed 42. A shot means one fresh preparation and measurement of the circuit. Fixed seeds make classroom results repeatable; they do not remove sampling uncertainty.

`exact` inspects a simulated state without measurement. `sample` returns finite-shot counts. `compare` plots both. Access to all amplitudes is a simulator convenience: a physical quantum computer does not hand you its state vector.'''), code(INSTALL), code(COMMON)]

def save(name, cells):
    for i, cell in enumerate(cells):
        cell['id'] = f'cell-{i:03d}'
    nb = {'nbformat': 4, 'nbformat_minor': 5, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}, 'colab': {'name': name}}, 'cells': cells}
    (ROOT / name).write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')

c = intro(1, 'Qubits, gates, and interference',
'''- Represent a qubit with normalized complex amplitudes and calculate measurement probabilities.
- Build and read circuits containing X, H, Z, and rotation gates.
- Distinguish relative phase, interference, exact probabilities, and sampled frequencies.
- Prepare a qubit with a chosen measurement probability.''',
'''| Activity |
|---|
| Setup and circuit model |
| States, amplitudes, measurement; Exercise 1 |
| Gates and rotations; Exercise 2 |
| Break and checkpoint |
| Phase and interference; Exercise 3 |
| Guided state preparation; Exercise 4 |
| 115–120 | Exit questions |''',
'''A Python list can store vector components; NumPy computes norms and matrix products. A complex number has a magnitude and a phase. We will introduce the quantum meaning of these quantities here. No physics formulas need to be memorized.''')
c += [md(r'''## From bits to circuits

A classical bit takes value 0 or 1. A qubit has basis states $|0\rangle=(1,0)^T$ and $|1\rangle=(0,1)^T$. The vertical bars are **ket notation**, a name for a state vector. A general pure qubit state is $|\psi\rangle=\alpha|0\rangle+\beta|1\rangle$.

A circuit starts with every qubit in $|0\rangle$. Gates change the state; measurement produces classical bits. Read a Qiskit circuit left to right; wires identify qubits, boxes identify gates, and measurement arrows point to classical storage. A quantum circuit is not a program that reads out all possible answers at once.

**Predict:** What should a circuit with no gates return? Run this first circuit and identify the classical register in its diagram.'''), code('''first = QuantumCircuit(QuantumRegister(1, 'q'), ClassicalRegister(1, 'result'))
first.measure(0, 0)
show(first)
result = StatevectorSampler(seed=SEED).run([first], shots=SHOTS).result()[0]
print(result.data.result.get_counts())'''), md(r'''## Amplitudes become probabilities

Normalization requires $|\alpha|^2+|\beta|^2=1$. In a computational-basis (Z-basis) measurement, $P(0)=|\alpha|^2$ and $P(1)=|\beta|^2$: the **Born rule**. Amplitudes can be negative or complex; probabilities cannot. After an ideal measurement with outcome 0, the state is $|0\rangle$ (and similarly for 1). To estimate a distribution, repeat the entire preparation, not measurements of an unchanged copy.

**Predict:** Do amplitudes $\sqrt{0.3}$ and $i\sqrt{0.7}$ give probabilities 0.3 and 0.7? Does the imaginary unit change the second probability?'''), code('''amplitudes = np.array([np.sqrt(.3), 1j * np.sqrt(.7)])
print('Amplitudes:', amplitudes)
print('Norm squared:', np.vdot(amplitudes, amplitudes).real)
print('Probabilities:', np.abs(amplitudes)**2)
assert np.isclose(np.linalg.norm(amplitudes), 1)
state = Statevector(amplitudes)
print('State vector:', state.data)'''), exercise(1, 'Amplitudes are not probabilities', r'Change the baseline state to amplitudes $1/2$ and $\sqrt{3}/2$. Predict both probabilities and check normalization. Then multiply the entire vector by $i$: what changes in its measurement probabilities?', 'Use `np.abs(vector)**2`. A common phase multiplying both amplitudes is a global phase.', 'Use `vector = np.array([.5, np.sqrt(3)/2])`. The probabilities are 0.25 and 0.75 and the squared norm is 1. `np.abs(1j * vector)**2` is identical. Global phase has no observable effect.'), code('''vector = np.array([1, 1j]) / np.sqrt(2)  # Working baseline: equal probabilities
print('Norm:', np.linalg.norm(vector))
print('Probabilities:', np.abs(vector)**2)
print('After global phase:', np.abs(1j * vector)**2)'''), md(r'''## Gates transform amplitudes

Gates are unitary matrices: they preserve normalization and are reversible before measurement.

$$X=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad H=\frac{1}{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},\quad Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.$$

X swaps the basis amplitudes. H sends $|0\rangle$ to $|+\rangle=(|0\rangle+|1\rangle)/\sqrt2$ and $|1\rangle$ to $|-\rangle=(|0\rangle-|1\rangle)/\sqrt2$. Z flips the sign of the $|1\rangle$ amplitude. Sign matters when amplitudes later interfere.

**Predict:** Compare no gate, X, H, and H followed by Z. Which can you distinguish with Z-basis counts alone?'''), code('''gate_examples = {}
for name in ['Identity', 'X', 'H', 'H then Z']:
    qc = QuantumCircuit(1)
    if name == 'X': qc.x(0)
    if name.startswith('H'): qc.h(0)
    if name == 'H then Z': qc.z(0)
    gate_examples[name] = qc
    print(name, 'amplitudes:', np.round(Statevector.from_instruction(qc).data, 3))
    compare(qc, name)
show(gate_examples['H then Z'])'''), md(r'''### Rotations and the Bloch sphere

$R_y(\theta)|0\rangle=\cos(\theta/2)|0\rangle+\sin(\theta/2)|1\rangle$, so $P(1)=\sin^2(\theta/2)$. Angles are in radians. On the Bloch sphere, poles represent basis states; equatorial states have equal Z-basis probabilities but different relative phases. The sphere represents a single qubit, not its physical trajectory.

**Predict → run → interpret:** What happens for $\theta=0,\pi/2,\pi$? Modify the angle below and explain the result.'''), code('''theta = np.pi / 3
rotation = QuantumCircuit(1)
rotation.ry(theta, 0)
show(rotation)
display(Statevector.from_instruction(rotation).draw('bloch'))
plt.show()
compare(rotation, f'Ry({theta:.2f})')
print('Predicted P(1):', np.sin(theta/2)**2)'''), exercise(2, 'Compose reversible gates', 'Predict the outputs of X–X and H–H starting from zero. Modify the baseline to test both. Then compare H–X and X–H using exact amplitudes: do they prepare the same state?', 'Circuit time runs left to right; the rightmost matrix acts first in a matrix product.', r'X–X and H–H both return zero. H–X prepares $|+\rangle$; X–H prepares $|-\rangle$. Their Z-basis probabilities are equal, but their relative phases differ. Apply one final H to distinguish them.'), code('''sequence = QuantumCircuit(1)
sequence.x(0)
sequence.x(0)
show(sequence)
print('Amplitudes:', Statevector.from_instruction(sequence).data)
compare(sequence, 'Two X gates')'''), md('''## Break and checkpoint

Before the break, explain to a partner: (1) why amplitude 1/2 gives probability 1/4; (2) why H followed by Z still gives roughly half zeros; (3) why 2,048 shots need not produce exactly 1,024 of each outcome. Resume at the next section after the break.'''), md(r'''## Phase becomes visible through interference

$|+\rangle$ and $|-\rangle$ have identical Z-basis probabilities. H changes the measurement basis: H followed by Z measurement is an X-basis measurement, with bit 0 meaning $|+\rangle$ and bit 1 meaning $|-\rangle$.

In H–H, amplitudes for outcome 1 cancel; in H–Z–H, amplitudes for outcome 0 cancel. This addition and cancellation of amplitudes is **interference**. A random classical bit with probabilities 1/2, 1/2 lacks the coherent relative phase that allows this deterministic reversal.

**Predict:** Where does the minus sign go in H–Z–H? Compare intermediate amplitudes and final counts.'''), code('''for use_z in [False, True]:
    qc = QuantumCircuit(1)
    qc.h(0)
    if use_z: qc.z(0)
    print('Before final H:', np.round(Statevector.from_instruction(qc).data, 3))
    qc.h(0)
    show(qc)
    compare(qc, 'H–Z–H' if use_z else 'H–H')'''), exercise(3, 'A phase dial', 'The baseline applies H–Rz(phi)–H. Predict P(1) for phi = 0, pi/2, and pi, then run each case. Explain why Rz is invisible in Z probabilities before the final H but visible afterward.', r'Up to a global phase, Rz adds relative phase phi. The final probability is $\sin^2(\phi/2)$.', 'The probabilities are 0, 1/2, and 1. Before the last H, the two magnitudes remain equal; after H, the relative phase determines constructive and destructive interference.'), code('''phi = np.pi / 2
phase_test = QuantumCircuit(1)
phase_test.h(0)
phase_test.rz(phi, 0)
print('Before final H:', exact(phase_test))
phase_test.h(0)
compare(phase_test, 'Phase converted into probability')'''), md('''## Prepare, predict, and explain

Work in pairs: one person chooses a target probability and predicts a circuit, the other checks it. Swap roles after the first successful test. Use exact probabilities to check your design and sampled counts to illustrate experimental variation.'''), exercise(4, 'Prepare a biased qubit', 'Prepare P(1) = 0.8 using one Ry gate. Derive the angle from the formula above, then change the baseline. Explain any difference between exact probability and observed frequency. Finally, choose your own target.', r'Solve $p=\sin^2(\theta/2)$ with $\theta=2\arcsin(\sqrt p)$ for $0\leq\theta\leq\pi$.', r'Set `target_p = .8` and `theta = 2*np.arcsin(np.sqrt(target_p))`, about 2.214 radians. Exact P(1) is 0.8. Sampling fluctuates; its standard deviation in frequency is $\sqrt{p(1-p)/2048}$, about 0.0088. The seed fixes one reproducible sample, not the exact probability.'), code('''target_p = .25  # Change to .8 after deriving the angle
theta = 2 * np.arcsin(np.sqrt(target_p))
prepared = QuantumCircuit(1)
prepared.ry(theta, 0)
counts = compare(prepared, f'Target P(1) = {target_p}')
print('Observed P(1):', counts.get('1', 0) / SHOTS)
assert np.isclose(exact(prepared).get('1', 0), target_p)'''), md('''## Exit ticket

1. What is the difference between an amplitude and a probability?
2. Why can two states have the same Z measurements yet differ physically?
3. Describe H–Z–H without saying “the qubit tries all answers.”
4. What can a simulator show that measurement on hardware cannot directly reveal?

**Optional extension:** sweep phi from 0 to 2π in Exercise 3, plot exact P(1), and overlay sin²(phi/2). Explain the extrema.

## References

- [IBM: quantum information basics](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information)
- [Qiskit QuantumCircuit](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.QuantumCircuit)
- [Qiskit StatevectorSampler](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler)
- [IBM: exact local simulation](https://quantum.cloud.ibm.com/docs/en/guides/simulate-with-qiskit-sdk-primitives)
''')]
save('01_qubits_and_interference.ipynb', c)

c = intro(2, 'Entanglement and superdense coding',
'''- Read two-qubit states using Qiskit's bit-order convention.
- Prepare Bell states and distinguish entanglement from classical correlation.
- Measure correlations in two bases.
- Encode and recover two classical bits using a shared Bell pair and one transmitted qubit.''',
'''| Activity |
|---|
| Recap, tensor products, bit ordering; Exercise 1 |
| CNOT and Bell states; Exercise 2 |
| Z/X correlations and classical mixture; Exercise 3 |
| Break and checkpoint |
| Superdense coding step by step |
| All four messages; Exercise 4 |
| 115–120 | Exit questions and resource accounting |''',
'''From Lab 1: X flips a bit, H creates or reverses superposition, and Z changes relative phase. Measurement probabilities are squared amplitude magnitudes. H immediately before measurement changes from the Z basis to the X basis. This notebook repeats all setup and helper code, so no earlier notebook needs to be open.''')
c += [md(r'''## Two qubits and bit ordering

Two qubits have four basis states. Qiskit displays strings as **q1 q0**, so `01` means q1=0 and q0=1. The amplitude array is ordered `00, 01, 10, 11`. The lowest-index qubit q0 is the least significant bit. Circuit diagrams still put q0 on the top wire.

For a product state, $|q_1\rangle\otimes|q_0\rangle$, tensor products multiply the single-qubit amplitudes. For example, q1 in $|0\rangle$ and q0 in $|+\rangle$ gives $(|00\rangle+|01\rangle)/\sqrt2$. A two-qubit state need not be expressible as a product.'''), exercise(1, 'Read the bit string', 'The baseline flips q0. Predict the only outcome. Change it to flip q1, then flip both. Finally prepare q1=0 and q0=plus and compare the vector with `np.kron`.', 'For Qiskit state vectors, write the tensor factors in descending qubit index.', 'X on q0 gives `01`; X on q1 gives `10`; both give `11`. H on q0 alone gives `[1,1,0,0]/sqrt(2)`, equal to `np.kron([1,0], [1,1]/sqrt(2))`.'), code('''ordering = QuantumCircuit(2)
ordering.x(0)
show(ordering)
print('State:', Statevector.from_instruction(ordering).data)
print('Counts:', sample(ordering))
print('Example tensor product:', np.kron([1, 0], np.array([1, 1])/np.sqrt(2)))'''), md(r'''## CNOT and Bell-state preparation

`cx(control, target)` flips the target if the control is 1 in each computational-basis component. The filled dot is the control and the circled plus is the target. CNOT maps basis states to basis states; on a superposition it acts linearly on each component.

Apply H to q0 and then CNOT from q0 to q1:
$$|00\rangle\longrightarrow\frac{|00\rangle+|01\rangle}{\sqrt2}\longrightarrow\frac{|00\rangle+|11\rangle}{\sqrt2}=|\Phi^+\rangle.$$

This is a **Bell state**. It is entangled because it cannot be factored into two independent qubit states. Each qubit alone is random in Z measurements, while the pair always agrees. Correlation alone does not prove entanglement; we will compare another basis shortly.

**Predict:** Compare H on both qubits with a Bell pair. How many outcomes should each show?'''), code('''bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
product = QuantumCircuit(2)
product.h([0, 1])
show(bell)
compare(bell, 'Bell pair: correlated in Z')
compare(product, 'Product of two plus states')
# A pure two-qubit state is a product exactly when its 2x2 coefficient matrix has rank 1.
for label, qc in [('Product', product), ('Bell', bell)]:
    coefficients = Statevector.from_instruction(qc).data.reshape(2, 2)
    print(label, 'coefficient rank:', np.linalg.matrix_rank(coefficients))'''), exercise(2, 'Change a Bell state', 'Add X on q0 after Bell preparation. Predict which outcomes remain. Replace that X with Z on q0: inspect amplitudes as well as Z counts. Does unchanged Z measurement imply an unchanged state?', 'X swaps the q0 values; Z changes the sign of components with q0=1.', r'X gives $(|01\rangle+|10\rangle)/\sqrt2$, so the bits disagree. Z gives $(|00\rangle-|11\rangle)/\sqrt2$: the same Z probabilities as before but a different relative phase. X-basis correlations distinguish the two phase choices.'), code('''changed_bell = bell.copy()
changed_bell.x(0)  # Replace with z(0) for the second experiment
print('Amplitudes:', np.round(Statevector.from_instruction(changed_bell).data, 3))
compare(changed_bell, 'Modified Bell pair')'''), md(r'''## Correlation versus entanglement

Consider a classical source that chooses `00` or `11` with equal probability. This **mixture** has the same Z probabilities as $|\Phi^+\rangle$. Its density matrix averages the outer products of those two states; the Bell state has additional off-diagonal terms representing coherence.

To measure both qubits in X, apply H to each before Z measurement. Bit 0 labels plus and bit 1 labels minus. The Bell pair still agrees in X. The classical mixture produces all four X outcomes equally often. This comparison distinguishes these two specified preparations. It is not a Bell-inequality experiment or a general entanglement certification protocol.

We sample the mixture by preparing each branch on half the shots and pooling counts. This fixed 50/50 allocation models the equal mixture without adding random variation to its branch weights.'''), code('''def in_basis(circuit, basis):
    rotated = circuit.copy()
    if basis == 'X': rotated.h([0, 1])
    return rotated

def mixture_experiment(basis):
    branches = []
    for bit in [0, 1]:
        qc = QuantumCircuit(2)
        if bit: qc.x([0, 1])
        branches.append(in_basis(qc, basis))
    rho = sum((DensityMatrix.from_instruction(qc).data for qc in branches)) / 2
    probabilities = DensityMatrix(rho).probabilities()
    counts = {label: 0 for label in ['00', '01', '10', '11']}
    for branch_index, qc in enumerate(branches):
        measured = qc.copy()
        readout = ClassicalRegister(2, 'readout')
        measured.add_register(readout)
        measured.measure([0, 1], readout)
        result = StatevectorSampler(seed=SEED + branch_index).run([measured], shots=SHOTS//2).result()[0]
        for key, count in result.data.readout.get_counts().items():
            counts[key] += count
    return probabilities, counts

def agreement(counts):
    return (counts.get('00', 0) + counts.get('11', 0)) / sum(counts.values())

for basis in ['Z', 'X']:
    compare(in_basis(bell, basis), f'Bell pair measured in {basis}')
    probabilities, counts = mixture_experiment(basis)
    print(basis, 'mixture exact probabilities:', probabilities)
    print(basis, 'mixture sampled counts:', counts, 'agreement:', agreement(counts))
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(list(counts), np.array(list(counts.values())) / SHOTS)
    ax.set(ylim=(0, 1), ylabel='Sampled frequency', xlabel='Measured bits', title=f'Classical mixture in {basis}')
    fig.tight_layout()
    plt.show()'''), exercise(3, 'Detect a relative phase', 'Compare Phi-plus with the state obtained by Z on q0. Predict agreement in Z and X for each, then test. Explain why the Z data alone cannot distinguish them.', 'H converts plus/minus states to computational-basis outcomes.', 'Phi-plus agrees in both bases. Phi-minus agrees in Z but disagrees in X: after H on both, only `01` and `10` occur. In Z, squaring amplitudes loses the relative sign.'), code('''phase_bell = bell.copy()
phase_bell.z(0)
for basis in ['Z', 'X']:
    counts = compare(in_basis(phase_bell, basis), f'Phi-minus in {basis}')
    print('Agreement:', agreement(counts))'''), md('''## Break and checkpoint

Discuss: Why does “both bits agree” fail to identify an entangled source? Which additional experiment distinguished our Bell source from the specified classical source? Take a break.'''), md(r'''## Superdense coding

**Task:** Alice wants Bob to recover a two-bit classical message $ab$. They already share a Bell pair. Alice holds q0 and Bob holds q1. Alice applies $X^b$ followed by $Z^a$ on her qubit, then **sends q0 to Bob**. Bob now holds both qubits and decodes using CNOT(q0,q1), then H(q0).

We simulate the full process in one circuit; the barrier marks physical transmission, not a gate. Bob's final q0 equals a and q1 equals b. We explicitly measure q0 into classical bit 1 and q1 into classical bit 0, so the displayed classical message reads **ab**. This mapping differs from the default q1q0 state-vector label.

| Message ab | Alice's operations, in time order |
|---|---|
| 00 | Identity |
| 01 | X |
| 10 | Z |
| 11 | X then Z |

**Predict:** Choose a message and trace which Bell state Alice creates. What would Bob learn by measuring his original qubit before receiving Alice's?'''), code('''def dense_stages(message):
    if len(message) != 2 or set(message) - {'0', '1'}:
        raise ValueError('Use a two-bit string such as 01.')
    a, b = map(int, message)
    shared = QuantumCircuit(2)
    shared.h(0)
    shared.cx(0, 1)
    encoded = shared.copy()
    if b: encoded.x(0)
    if a: encoded.z(0)
    decoded = encoded.copy()
    decoded.barrier(label='Alice sends q0')
    decoded.cx(0, 1)
    decoded.h(0)
    return shared, encoded, decoded

def dense_counts(decoded):
    measured = decoded.copy()
    message_register = ClassicalRegister(2, 'message')
    measured.add_register(message_register)
    measured.measure(0, message_register[1])  # a, leftmost displayed bit
    measured.measure(1, message_register[0])  # b, rightmost displayed bit
    result = StatevectorSampler(seed=SEED).run([measured], shots=SHOTS).result()[0]
    show(measured)
    return result.data.message.get_counts()

message = '10'
shared, encoded, decoded = dense_stages(message)
for label, qc in [('Shared pair', shared), ('Encoded pair', encoded), ('Decoded q1q0', decoded)]:
    print(label, np.round(Statevector.from_instruction(qc).data, 3))
print('Recovered ab:', dense_counts(decoded))'''), md('''### Interpret the resources

Two classical bits are recovered after Alice sends one qubit **and consumes one previously shared Bell pair**. Establishing that pair required earlier resources. Bob must receive Alice's qubit and perform joint decoding. His original qubit alone has a maximally mixed state, independent of the message; entanglement does not carry a controllable faster-than-light signal.

**Modify:** Try message `11`. Follow the phases through encoding, then explain why the decoder turns them into classical output bits.'''), exercise(4, 'Recover all messages', 'Run all four messages and make a message→recovered-output table. Then remove the shared-pair preparation in a copy of the protocol and test message 10. Explain which resource was lost.', 'Loop over `00`, `01`, `10`, `11`. For the resource test, begin at `QuantumCircuit(2)` and apply the same encoding and decoding gates.', 'All four messages return themselves with 2,048 counts. Without the shared Bell pair, message 10 applies Z to zero (no observable change), then the decoder prepares a superposition on q0. The recovered messages are 00 and 10 with approximately equal frequency; deterministic recovery fails.'), code('''recovered = {}
for message in ['00', '01', '10', '11']:
    _, _, decoded = dense_stages(message)
    # The helper displays the measurement wiring as well as returning counts.
    recovered[message] = dense_counts(decoded)
print(recovered)

without_pair = QuantumCircuit(2)
without_pair.z(0)  # Encode message 10 without initial entanglement
without_pair.cx(0, 1)
without_pair.h(0)
print('Without shared pair, recovered ab:', dense_counts(without_pair))'''), md('''## Exit ticket

1. What does bit string `01` mean in the default Qiskit state ordering?
2. Why is a Bell pair different from independently prepared plus states?
3. What distinguishes our Bell state from the classical correlated mixture?
4. Which resources does superdense coding consume, and why must Alice send her qubit?

**Optional extension:** use `partial_trace` from `qiskit.quantum_info` to inspect Bob's qubit after each encoding. Show that all messages give the same reduced density matrix, identity/2.

## References

- [IBM: bit ordering](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering)
- [IBM: entanglement in action](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/entanglement-in-action)
- [Qiskit DensityMatrix](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.DensityMatrix)
''')]
save('02_entanglement_and_superdense_coding.ipynb', c)

c = intro(3, 'Quantum algorithms: hidden strings and search',
'''- Explain an oracle and distinguish oracle queries from total computational cost.
- Use phase kickback to implement Bernstein–Vazirani with explicit gates.
- Build a two-qubit Grover oracle and diffuser.
- Explain why too many Grover iterations can reduce success.''',
'''| Activity |
|---|
| Recap, oracles, query complexity; Exercise 1 |
| Bernstein–Vazirani and phase kickback |
| Hidden-string experiments; Exercise 2 |
| Break and checkpoint |
| Grover oracle, diffusion, amplitudes; Exercise 3 |
| Marked states and iteration counts; Exercise 4 |
| 115–120 | Exit questions and limitations |''',
'''H creates plus/minus states; a relative phase can affect later measurement through interference. CNOT acts linearly and can correlate qubits. Qiskit labels computational-basis strings with the highest qubit index on the left. All imports and helpers are repeated here; no earlier kernel state is required.''')
c += [md(r'''## What is an oracle?

An **oracle** is a specified interface to a function. A reversible bit oracle implements $U_f|x\rangle|y\rangle=|x\rangle|y\oplus f(x)\rangle$, where $\oplus$ is XOR. It can be applied to superpositions, but measurement does not reveal every function value.

**Query complexity** counts calls to this interface, treating each call as one unit. It leaves out gate construction, state preparation, communication, and measurement overhead. Our small oracles are built from known answers so that we can study algorithm behavior. This is an educational black-box model, not a claim that discovering an answer and building an oracle is free.'''), exercise(1, 'Read a reversible oracle', 'For f(x)=x on one input bit, a CNOT implements the oracle. Predict outputs for all four pairs (x,y), then run. Explain why replacing y with f(x) without keeping x would generally lose information.', 'The target becomes y XOR x, and the control is unchanged. Applying CNOT twice restores the input.', 'For (x,y)=00,01,10,11 the output pairs are 00,01,11,10. The printed Qiskit strings are yx, so inspect that ordering carefully. Reversible gates must preserve distinguishability; overwriting information generally does not.'), code('''for x in [0, 1]:
    for y in [0, 1]:
        oracle_demo = QuantumCircuit(2)
        if x: oracle_demo.x(0)
        if y: oracle_demo.x(1)
        oracle_demo.cx(0, 1)
        print(f'Input (x,y)=({x},{y}); output string yx:', sample(oracle_demo))'''), md(r'''## Bernstein–Vazirani

An unknown n-bit string $s$ defines $f_s(x)=s\cdot x\pmod2$, the parity of positions where both s and x are 1. A deterministic classical algorithm needs n queries to recover s exactly: query each unit vector. One quantum oracle query recovers all n bits in the ideal model.

### Phase kickback

Prepare an auxiliary qubit in $|-\rangle$ using X then H. Since $X|-\rangle=-|-\rangle$, the oracle acts as
$$U_f|x\rangle|-\rangle=(-1)^{f(x)}|x\rangle|-\rangle.$$
The auxiliary state factors out, while the input amplitudes gain x-dependent signs. This is **phase kickback**. The oracle has not copied the auxiliary qubit's measurement result into the input.

Start all input qubits in plus states. Each s bit equal to 1 makes its corresponding input effectively a minus state after the parity oracle. Final H gates turn plus to zero and minus to one. Thus measuring inputs recovers s.

We define s in displayed order: `1010` means s3=1, s2=0, s1=1, s0=0. The auxiliary qubit is q[n] and is not measured.'''), code('''def parity_oracle(secret):
    if not secret or set(secret) - {'0', '1'}:
        raise ValueError('Secret must be a nonempty binary string.')
    n = len(secret)
    oracle = QuantumCircuit(n + 1, name='Uf')
    for q, bit in enumerate(reversed(secret)):
        if bit == '1': oracle.cx(q, n)
    return oracle

def bernstein_vazirani(secret):
    n = len(secret)
    qc = QuantumCircuit(n + 1)
    qc.x(n)
    qc.h(n)                  # auxiliary is minus
    qc.h(range(n))           # inputs are uniform
    qc.barrier(label='one oracle query')
    qc.compose(parity_oracle(secret), inplace=True)
    qc.barrier()
    qc.h(range(n))           # interference reveals the secret
    return qc

secret = '1010'
bv = bernstein_vazirani(secret)
show(bv)
print('Recovered input string:', sample(bv, range(len(secret))))
print('Exact input probabilities:', Statevector.from_instruction(bv).probabilities(qargs=list(range(len(secret)))))'''), md('''### Trace the classical and quantum data

**Predict:** What happens for an all-zero secret? What if the auxiliary starts in plus rather than minus?

**Interpret:** the oracle contains one CNOT for each 1 in the secret. Counting the entire oracle as one query does not make all these gates cost one operation. The advantage here is n versus one calls to the specified function interface.'''), exercise(2, 'Recover new secrets', 'Test 0000, 0001, 1101, and your own five-bit secret. Implement the classical unit-vector queries and compare the query counts. Then change the auxiliary preparation from minus to plus and predict the result.', 'Use `int(secret, 2)` and bitwise AND to compute a parity, or take a dot product modulo 2. Plus is an eigenstate of X with eigenvalue +1.', 'Every ideal quantum run recovers its secret. A classical exact strategy queries each of n basis strings, obtaining the corresponding secret bit. With auxiliary plus, no phase is kicked back, so the final input is all zeros regardless of s.'), code('''def classical_unit_queries(secret):
    n = len(secret)
    answers = []
    for q in range(n):
        x = 1 << q
        answers.append((int(secret, 2) & x).bit_count() % 2)
    return ''.join(map(str, reversed(answers))), n

for secret in ['0000', '0001', '1101', '10101']:
    qc = bernstein_vazirani(secret)
    print(secret, 'quantum:', sample(qc, range(len(secret))),
          'classical (answer, queries):', classical_unit_queries(secret))'''), md('''## Break and checkpoint

Explain how a sign change can carry information without changing the intermediate Z probabilities. Distinguish an oracle query from a physical gate. Take a break before the search experiment.'''), md(r'''## Grover search among four candidates

Let exactly one of `00`, `01`, `10`, `11` be marked. Begin with equal amplitudes $1/2$. A **phase oracle** negates only the marked amplitude. This sign change alone leaves measurement probabilities unchanged.

The diffuser $D=2|u\rangle\langle u|-I$, where $|u\rangle$ is the uniform state, maps each amplitude $a_x$ to $2\bar a-a_x$ (inversion about the mean). After the oracle, the amplitudes are three copies of 1/2 and one of −1/2; their mean is 1/4. One diffusion step gives marked amplitude 1 and all others 0.

### Build a two-qubit phase oracle

CZ negates only `11`. To mark any target, apply X to positions where the target has zero, apply CZ, then undo those X gates. Target strings follow q1q0 ordering.

### Build the diffuser

H on both → X on both → CZ → X on both → H on both implements $-D$; an extra global phase π makes it exactly D for easier amplitude tracing. Global phase does not change measurements.

**Predict:** At which stage do probabilities change? Why is the phase oracle alone insufficient?'''), code('''def mark_target(circuit, target):
    if len(target) != 2 or set(target) - {'0', '1'}:
        raise ValueError('Use a two-bit target.')
    zeros = [q for q, bit in enumerate(reversed(target)) if bit == '0']
    for q in zeros: circuit.x(q)
    circuit.cz(0, 1)
    for q in zeros: circuit.x(q)

def diffuse(circuit):
    circuit.h([0, 1])
    circuit.x([0, 1])
    circuit.cz(0, 1)
    circuit.x([0, 1])
    circuit.h([0, 1])
    circuit.global_phase += np.pi

def grover(target, iterations=1):
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    for _ in range(iterations):
        mark_target(qc, target)
        diffuse(qc)
    return qc

target = '10'
uniform = QuantumCircuit(2)
uniform.h([0, 1])
marked = uniform.copy()
mark_target(marked, target)
amplified = marked.copy()
diffuse(amplified)
for label, qc in [('Uniform', uniform), ('After oracle', marked), ('After diffusion', amplified)]:
    print(label, 'amplitudes in 00,01,10,11 order:', np.round(Statevector.from_instruction(qc).data, 3))
    compare(qc, label)
show(amplified)'''), exercise(3, 'Construct another oracle', 'Change the target to 01. Predict which qubit needs X around CZ. Inspect the state after the oracle and verify that only the target amplitude changes sign. Then finish one iteration.', 'String 01 has q1=0, q0=1; conjugate CZ with X on q1.', 'Apply X(1), CZ(0,1), X(1). The oracle amplitudes are `[.5,-.5,.5,.5]`. Diffusion produces `[0,1,0,0]` up to numerical roundoff, so measurement returns 01.'), code('''target = '11'  # Change to 01
oracle_check = QuantumCircuit(2)
oracle_check.h([0, 1])
mark_target(oracle_check, target)
print('Oracle amplitudes:', np.round(Statevector.from_instruction(oracle_check).data, 3))
diffuse(oracle_check)
compare(oracle_check, f'Grover finds {target}')'''), md(r'''## More iterations are not always better

With one marked item among N candidates, the ideal success probability after r iterations is $\sin^2((2r+1)\theta)$, with $\sin\theta=1/\sqrt N$. Here N=4 and $\theta=\pi/6$. One iteration succeeds with probability 1, but two iterations return to probability 1/4: repeated steps rotate past the desired state.

For large N and one solution, Grover uses order $\sqrt N$ oracle queries for high success, versus order N classical queries. Our four-item example illustrates the mechanism; it does not demonstrate a practical speedup on this classical simulator.'''), exercise(4, 'Search and overshoot', 'Check all four targets after one iteration. Then sweep iterations 0 through 5 for a fixed target. Predict the curve before running, compare it with the formula, and explain why simply increasing the iterations is a poor strategy.', 'For N=4, use theta=pi/6. Exact target probabilities can be read with `exact(qc).get(target, 0)`.', 'All four targets succeed with probability 1 after one iteration. For r=0…5, success is `[.25,1,.25,.25,1,.25]`. Amplitude amplification is a rotation rather than a monotonic improvement.'), code('''for target in ['00', '01', '10', '11']:
    qc = grover(target)
    print('Target:', target, 'exact success:', exact(qc).get(target, 0), 'counts:', sample(qc))

target = '10'
iterations = np.arange(6)
success = [exact(grover(target, int(r))).get(target, 0) for r in iterations]
predicted = np.sin((2 * iterations + 1) * np.pi/6)**2
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(iterations, success, 'o-', label='Exact circuit probability')
ax.plot(iterations, predicted, 'x--', label='Analytical formula')
ax.set(xlabel='Grover iterations / oracle queries', ylabel='Target probability', ylim=(0, 1.1), xticks=iterations)
ax.legend()
fig.tight_layout()
plt.show()
assert np.allclose(success, predicted)'''), md('''## Exit ticket

1. What is the oracle interface in Bernstein–Vazirani, and what does one quantum query recover?
2. How does phase kickback differ from reading out every function value?
3. Why does Grover need both a phase oracle and diffusion?
4. Why do these demonstrations not establish a practical runtime advantage?

**Optional extension:** remove the X preparation of the BV auxiliary so it starts in plus, verify all-zero input output, and derive why. Alternatively, write the 4×4 diffuser matrix `2*np.ones((4,4))/4 - np.eye(4)` and compare its action with the gate implementation.

## References

- [IBM: quantum algorithms course](https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms)
- [IBM: Grover tutorial](https://quantum.cloud.ibm.com/docs/en/tutorials/grovers-algorithm)
- [IBM: Qiskit bit ordering](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering)
- [Qiskit Statevector](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector)
''')]
save('03_quantum_algorithms.ipynb', c)
print('Generated three notebooks.')
