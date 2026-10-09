"""Execute each notebook in a fresh kernel and check quantum behavior."""
import json
from pathlib import Path
import nbformat
from nbclient import NotebookClient

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
for msg in ['00', '01', '10', '11']:
    _, enc, dec = dense_stages(msg)
    # Decoded state uses q1q0, while message readout uses q0q1.
    assert np.isclose(exact(dec).get(msg[::-1], 0), 1)
    assert dense_counts(dec) == {msg: SHOTS}
    assert np.allclose(partial_trace(Statevector.from_instruction(enc), [0]).data, np.eye(2)/2)
''',
    '''
from qiskit.quantum_info import Operator
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
    # Dependencies are installed in the clean environment before validation.
    # Skip only the duplicate network install; run every teaching code cell.
    nb.cells = [cell for cell in nb.cells if not (cell.cell_type == 'code' and cell.source.startswith('%pip'))]
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
                   'code_cells_executed': sum(cell.cell_type == 'code' for cell in nb.cells)})
    print('Passed:', path.name, 'figures:', figures, flush=True)
(ARTIFACTS / 'report.json').write_text(json.dumps(report, indent=2))
print('All notebook execution and acceptance checks passed.')
