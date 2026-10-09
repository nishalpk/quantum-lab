"""Execute each notebook in a fresh kernel and check quantum behavior."""
import json
import re
import sys
import asyncio
from pathlib import Path
import nbformat
from nbclient import NotebookClient

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / 'validation_artifacts'
ARTIFACTS.mkdir(exist_ok=True)
checks = [
    '''
for name, expected in [('Identity', [1,0]), ('X', [0,1]), ('H', [.5,.5]), ('H then Z', [.5,.5])]:
    assert np.allclose(Statevector.from_instruction(gate_examples[name]).probabilities(), expected)
assert np.allclose(Statevector.from_instruction(phase_test).probabilities(), [.5,.5])
assert np.isclose(np.linalg.norm(Statevector.from_instruction(prepared).data), 1)
assert abs(counts.get('1', 0)/SHOTS - target_p) < .05
# Exercise 1: Born rule and invariance under global phase.
v = np.array([.5, np.sqrt(3)/2])
assert np.isclose(np.vdot(v, v), 1)
assert np.allclose(np.abs(v)**2, [.25, .75])
assert np.allclose(np.abs(1j*v)**2, [.25, .75])
# Exercise 2: chronological gate sequences, including relative phase.
for gates, expected in [(['x','x'], [1,0]), (['h','h'], [1,0]),
                        (['h','x'], [1/np.sqrt(2),1/np.sqrt(2)]),
                        (['x','h'], [1/np.sqrt(2),-1/np.sqrt(2)])]:
    qc = QuantumCircuit(1)
    for gate in gates: getattr(qc, gate)(0)
    assert np.allclose(Statevector.from_instruction(qc).data, expected)
# Rotation demonstration and Exercises 3/4, including endpoint targets.
for phi_value in [0, np.pi/2, np.pi, 2*np.pi]:
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.rz(phi_value, 0)
    assert np.allclose(Statevector.from_instruction(qc).probabilities(), [.5,.5])
    qc.h(0)
    p = np.sin(phi_value/2)**2
    assert np.allclose(Statevector.from_instruction(qc).probabilities(), [1-p,p])
for p in [0, .25, .8, 1]:
    qc = QuantumCircuit(1)
    qc.ry(2*np.arcsin(np.sqrt(p)), 0)
    assert np.allclose(Statevector.from_instruction(qc).probabilities(), [1-p,p])
    assert abs(sample(qc).get('1',0)/SHOTS-p) < .05
assert np.isclose(2*np.arcsin(np.sqrt(.8)), 2.214297435588181)
assert np.isclose(np.sqrt(.8*.2/SHOTS), .008838834764831844)
for use_z, expected in [(False, [1,0]), (True, [0,1])]:
    qc = QuantumCircuit(1)
    qc.h(0)
    if use_z: qc.z(0)
    qc.h(0)
    assert np.allclose(Statevector.from_instruction(qc).probabilities(), expected)
''',
    '''
from qiskit.quantum_info import partial_trace
for basis in ['Z', 'X']:
    probs = exact(in_basis(bell, basis))
    assert np.isclose(probs.get('00', 0) + probs.get('11', 0), 1)
    assert agreement(sample(in_basis(bell, basis))) == 1
assert np.allclose(mixture_experiment('Z')[0], [.5,0,0,.5])
assert np.allclose(mixture_experiment('X')[0], [.25]*4)
assert abs(agreement(mixture_experiment('X')[1]) - .5) < .05
assert np.isclose(exact(in_basis(phase_bell, 'X')).get('01', 0), .5)
# Exercise 1: bit ordering and the numerical tensor-product answer.
for qubits, expected in [([0], '01'), ([1], '10'), ([0,1], '11')]:
    qc = QuantumCircuit(2)
    qc.x(qubits)
    assert sample(qc) == {expected: SHOTS}
qc = QuantumCircuit(2)
qc.h(0)
assert np.allclose(Statevector.from_instruction(qc).data,
                   np.kron([1,0], np.array([1,1])/np.sqrt(2)))
assert np.linalg.matrix_rank(Statevector.from_instruction(product).data.reshape(2,2)) == 1
assert np.linalg.matrix_rank(Statevector.from_instruction(bell).data.reshape(2,2)) == 2
assert np.allclose(Statevector.from_instruction(product).probabilities(), [.25]*4)
# Exercises 2/3: Bell-state amplitudes and basis-dependent correlations.
for gate, expected in [('x', [0,1/np.sqrt(2),1/np.sqrt(2),0]),
                       ('z', [1/np.sqrt(2),0,0,-1/np.sqrt(2)])]:
    qc = bell.copy()
    getattr(qc, gate)(0)
    assert np.allclose(Statevector.from_instruction(qc).data, expected)
assert np.allclose(Statevector.from_instruction(in_basis(phase_bell,'Z')).probabilities(), [.5,0,0,.5])
assert np.allclose(Statevector.from_instruction(in_basis(phase_bell,'X')).probabilities(), [0,.5,.5,0])
rho_mixture = np.diag([.5,0,0,.5])
rho_bell = DensityMatrix.from_instruction(bell).data
assert np.allclose(np.diag(rho_bell), np.diag(rho_mixture))
assert np.isclose(rho_bell[0,3], .5) and np.isclose(rho_mixture[0,3], 0)
for msg in ['00', '01', '10', '11']:
    _, enc, dec = dense_stages(msg)
    # Decoded state uses q1q0, while message readout uses q0q1.
    assert np.isclose(exact(dec).get(msg[::-1], 0), 1)
    assert dense_counts(dec) == {msg: SHOTS}
    assert np.allclose(partial_trace(Statevector.from_instruction(enc), [0]).data, np.eye(2)/2)
assert np.allclose(Statevector.from_instruction(without_pair).probabilities(), [.5,.5,0,0])
without_counts = dense_counts(without_pair)
assert set(without_counts) == {'00','10'}
assert abs(without_counts['10']/SHOTS - .5) < .05
''',
    '''
from qiskit.quantum_info import Operator
# Exercise 1: all oracle basis inputs and reversibility.
for x in [0,1]:
    for y in [0,1]:
        qc = QuantumCircuit(2)
        if x: qc.x(0)
        if y: qc.x(1)
        before = Statevector.from_instruction(qc)
        qc.cx(0,1)
        assert sample(qc) == {f'{y^x}{x}': SHOTS}
        qc.cx(0,1)
        assert np.allclose(Statevector.from_instruction(qc).data, before.data)
# Exhaustive BV checks for every secret of lengths 1 through 5.
for n in range(1,6):
    for value in range(2**n):
        secret = format(value, f'0{n}b')
        qc = bernstein_vazirani(secret)
        probs = Statevector.from_instruction(qc).probabilities(qargs=list(range(n)))
        assert np.isclose(probs[value], 1)
        assert classical_unit_queries(secret) == (secret,n)
        unitary = Operator(parity_oracle(secret)).data
        for x in range(2**n):
            parity = sum(int(secret[-1-q])*((x>>q)&1) for q in range(n)) % 2
            for y in [0,1]:
                source = x + (y<<n)
                dest = x + ((y^parity)<<n)
                assert np.isclose(unitary[dest,source], 1)
                assert np.count_nonzero(np.abs(unitary[:,source]) > 1e-10) == 1
for secret in ['0', '1', '0000', '0001', '1101', '10101', '11111']:
    n = len(secret)
    qc = bernstein_vazirani(secret)
    assert sample(qc, range(n)) == {secret: SHOTS}
    probs = Statevector.from_instruction(qc).probabilities(qargs=list(range(n)))
    assert np.isclose(probs[int(secret, 2)], 1)
    assert classical_unit_queries(secret) == (secret, n)
    plus_aux = QuantumCircuit(n+1)
    plus_aux.h(range(n+1))
    plus_aux.compose(parity_oracle(secret), inplace=True)
    plus_aux.h(range(n))
    assert sample(plus_aux, range(n)) == {'0'*n: SHOTS}
diffuser = QuantumCircuit(2)
diffuse(diffuser)
assert np.allclose(Operator(diffuser).data, np.ones((4,4))/2 - np.eye(4))
for target in ['00', '01', '10', '11']:
    oracle = QuantumCircuit(2)
    mark_target(oracle, target)
    diagonal = np.ones(4)
    diagonal[int(target, 2)] = -1
    assert np.allclose(Operator(oracle).data, np.diag(diagonal))
    uniform_test = QuantumCircuit(2)
    uniform_test.h([0,1])
    mark_target(uniform_test,target)
    assert np.allclose(Statevector.from_instruction(uniform_test).probabilities(), [.25]*4)
    expected_amplitudes = np.full(4,.5)
    expected_amplitudes[int(target,2)] = -.5
    assert np.allclose(Statevector.from_instruction(uniform_test).data, expected_amplitudes)
    diffuse(uniform_test)
    final_amplitudes = np.zeros(4)
    final_amplitudes[int(target,2)] = 1
    assert np.allclose(Statevector.from_instruction(uniform_test).data, final_amplitudes)
    assert np.isclose(exact(grover(target)).get(target, 0), 1)
    assert sample(grover(target)) == {target: SHOTS}
    actual = [exact(grover(target, r)).get(target, 0) for r in range(6)]
    assert np.allclose(actual, np.sin((2*np.arange(6)+1)*np.pi/6)**2)
'''
]
report = []
for index, path in enumerate(sorted(ROOT.glob('0*.ipynb'))):
    nb = nbformat.read(path, as_version=4)
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            assert '$' not in cell.source, 'Unconverted LaTeX delimiter'
            assert not re.search(r'\d+[–-]\d+\s*min|\|\s*\d+[–-]\d+\s*\|', cell.source), 'Leftover timing label'
            assert cell.source.count('```') % 2 == 0
            assert cell.source.count('<details>') == cell.source.count('</details>')
    # Execute EVERY code cell, including %pip, in a fresh kernel.
    nb.cells.append(nbformat.v4.new_code_cell(checks[index] + "\nprint('Acceptance checks passed')"))
    print('Executing', path.name, flush=True)
    client = NotebookClient(nb, timeout=180, kernel_name='python3', resources={'metadata': {'path': str(ROOT)}})
    client.execute()
    nbformat.write(nb, ARTIFACTS / path.name)
    figures = 0
    for cell_index, cell in enumerate(nb.cells):
        if cell.cell_type != 'code': continue
        for output_index, output in enumerate(cell.get('outputs', [])):
            data = output.get('data', {})
            if 'image/png' in data:
                import base64
                name = f'lab{index+1}_{cell_index}_{output_index}.png'
                (ARTIFACTS / name).write_bytes(base64.b64decode(data['image/png']))
                figures += 1
    report.append({'notebook': path.name, 'status': 'passed', 'figures': figures,
                   'installation_cell_executed': True,
                   'teaching_code_cells': sum(cell.cell_type == 'code' for cell in nb.cells)-1,
                   'code_cells_executed': sum(cell.cell_type == 'code' for cell in nb.cells)})
    print('Passed:', path.name, 'figures:', figures, flush=True)
(ARTIFACTS / 'report.json').write_text(json.dumps(report, indent=2))
print('All notebook execution and acceptance checks passed.')
