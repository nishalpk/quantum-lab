# Quantum computing: three introductory Qiskit labs

For learners comfortable with Python and basic linear algebra, starting with no quantum computing background. Each notebook is self-contained, contains four exercises with collapsible hints and worked solutions.

| Notebook | Core topics |
|---|---|
| [Lab 1](01_qubits_and_interference.ipynb) | Qubits, amplitudes, gates, measurement, rotations, interference |
| [Lab 2](02_entanglement_and_superdense_coding.ipynb) | Bit ordering, Bell states, classical mixtures, X/Z correlations, superdense coding |
| [Lab 3](03_quantum_algorithms.ipynb) | Oracles, phase kickback, Bernstein–Vazirani, two-qubit Grover search |

## Run in Google Colab

Open https://colab.research.google.com/, choose **File → Upload notebook**, and upload a notebook. Connect to a standard Python CPU runtime and run cells in order. Run the installation cell first. If packages were already imported before installation, restart the session and rerun from the imports cell. No IBM credentials, GPU, or hardware access are needed. Installation requires internet access.

Students should predict before executing, interpret results, then modify working baseline code. Use hints before opening worked solutions. Optional extensions follow the core activities. Retain Lab 1→2→3 teaching order even though each notebook runs independently.

## Local environment and maintenance

Target Python 3.10–3.13. The teaching dependencies are pinned in `requirements.txt`. Create a virtual environment and install them with `python -m pip install -r requirements.txt`; install Jupyter separately for interactive use.

`build_notebooks.py` is the editable source for notebook content. Run it to regenerate all three clean notebooks; regeneration replaces notebook edits and saved outputs. Distributed notebooks intentionally have no saved outputs so students make predictions before seeing results.

For automated validation, additionally install `nbformat==5.10.4 nbclient==0.10.2 ipykernel==6.29.5`, then run `python validate_notebooks.py` from the same environment. This validates notebook schemas, executes teaching cells in separate fresh kernels, and runs numerical and sampling checks. It skips only the duplicate `%pip` installation cell because dependencies are preinstalled. Executed copies, plots, and a JSON report are written to ignored `validation_artifacts/`.

## Interpretation

Exact state-vector inspection is a simulator capability; physical measurements provide samples. Fixed seeds make samples reproducible, not exact. Oracle-query comparisons are theoretical cost models and do not claim a practical speedup from these small simulations. Superdense coding requires a pre-shared entangled pair and physical transmission of Alice's qubit.

## Validation performed

All three notebooks passed schema validation and fresh-kernel execution on Python 3.12.12 with the pinned teaching dependencies. Numerical checks passed for gate behavior and normalization, Bell correlations in Z/X, classical-mixture probabilities, all four superdense-coding messages and Bob's reduced state, seven Bernstein–Vazirani secrets, all four Grover targets, and the Grover iteration curve. Representative circuit diagrams and plots were visually inspected. This was a clean local environment test; direct execution in Google Colab and live classroom pacing have not been verified.
