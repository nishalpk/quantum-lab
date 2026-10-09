# Notebook review and validation

**Reviewed:** 9 October 2026. **Result:** all three notebooks passed.

The explanations, exercise prompts, hints, worked solutions, bit conventions, and circuit implementations were reviewed together. Every code cell, including each `%pip` installation cell, was then executed in a separate fresh Jupyter kernel using Python 3.12.12 and the versions in `requirements.txt`. Student notebooks retain clean cells without saved answers or outputs; executed copies and the machine-readable report are in `validation_artifacts/`.

## Checks performed

| Lab | Logical and numerical checks |
|---|---|
| 1 | Born-rule probabilities; normalization and global-phase invariance; X/H/Z behavior; X–X, H–H, H–X, and X–H sequences; H–Z–H interference; phase-dial predictions; Ry state preparation including probabilities 0, 0.25, 0.8, and 1; sampling tolerance; angle and uncertainty values in the worked solution. |
| 2 | Qubit and classical-bit ordering; tensor-product example; product versus entangled coefficient ranks; Bell-state amplitudes; Z/X correlations for Phi-plus and Phi-minus; classical-mixture probabilities and coherence comparison; all four superdense-coding messages; Bob's reduced state for every message; failure of deterministic decoding without a shared Bell pair. |
| 3 | CNOT oracle truth table and reversibility; Bernstein–Vazirani recovery for every secret of lengths 1–5 (62 secrets); full parity-oracle truth tables for both auxiliary inputs; classical unit-vector recovery; sampled recovery for representative secrets; auxiliary-plus counterexample; every two-qubit Grover oracle; diffuser matrix; intermediate and final amplitudes; all four targets; success probabilities for iterations 0–5. |

Exact results were checked with floating-point tolerances; sampled nondeterministic frequencies were checked with a 0.05 absolute tolerance. Fixed seeds make the sampled checks reproducible. Notebook schemas, balanced code fences and collapsible sections, converted math notation, and removal of timing labels were also checked.

## Corrections made during review

- Clarified that overwriting the auxiliary bit loses its original value even when the input is retained; XOR preserves reversibility.
- Made the tensor-product worked example directly runnable with NumPy arrays.
- Distinguished equal theoretical probabilities from fluctuating sampled counts.
- Removed remaining timing labels from agenda rows and corrected the resulting table layout.
- Replaced instructor-facing introductory wording with instructions addressed to students.

The cost comparisons use the oracle-query model, rather than claiming a practical speedup from these simulations. Superdense coding explicitly accounts for a pre-shared Bell pair and physical qubit transmission. The comparison of Bell and classical sources is described as distinguishing those preparations, without presenting it as a Bell-inequality test.

## Reference cross-checks and limits

The review used IBM's [bit-ordering documentation](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering), [superdense-coding lesson](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/entanglement-in-action/superdense-coding), [quantum-query-algorithms lesson](https://learning.quantum.ibm.com/course/fundamentals-of-quantum-algorithms/quantum-query-algorithms), and [Grover iteration discussion](https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/grover-algorithm/number-of-iterations).

Validation was performed locally with fresh kernels. Direct Google Colab execution, real-device behavior, and classroom pacing have not been tested. The reviewed examples and checked solutions are consistent with the ideal circuit model; this review is not a guarantee against every possible future dependency or platform change.
