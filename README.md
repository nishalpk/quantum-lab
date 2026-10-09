# Introduction to Quantum Computing

Welcome to the practical labs for **Introduction to Quantum Computing**. In these three notebooks, you will use Python and Qiskit to build quantum circuits, explore how measurements work, and implement your first quantum algorithms. You do not need any prior knowledge of quantum computing.

## What you will learn

Work through the notebooks in this order:

| Lab | Topics | What you will be able to do |
|---|---|---|
| [1. Qubits, gates, and interference](01_qubits_and_interference.ipynb) | Quantum states, amplitudes, measurement, gates, rotations, and interference | Build single-qubit circuits and predict their measurement probabilities. |
| [2. Entanglement and superdense coding](02_entanglement_and_superdense_coding.ipynb) | Two-qubit states, Bell pairs, measurement correlations, and quantum communication | Create entanglement and use a shared Bell pair to encode and recover a two-bit message. |
| [3. Quantum algorithms](03_quantum_algorithms.ipynb) | Oracles, phase kickback, Bernstein-Vazirani, and Grover search | Recover a hidden bit string and amplify the probability of a marked search result. |

Each notebook contains explanations, circuit experiments, four exercises, hints, worked solutions, and optional extensions. It includes its own setup code, so you can open it in a new session without running another notebook first.

## Before you start

You should be comfortable with Python variables, lists, loops, and functions, and have some familiarity with vectors and matrices. The notebooks introduce the quantum concepts as you go. If complex numbers or tensor products are unfamiliar, ask your instructor as you reach those sections.

You will need a computer, a web browser, an internet connection, and access to Google Colab. The labs use local simulation within the notebook. You do not need an IBM Quantum account, an API key, a GPU, or access to a physical quantum computer.

## Open a notebook in Google Colab

1. Download the notebook you want to use from this repository. The file should end in `.ipynb`.
2. Open [Google Colab](https://colab.research.google.com/), select **File → Upload notebook**, and upload the file.
3. Connect to a standard Python CPU runtime.
4. Run the installation cell under **Setup**, then run the imports and helper-functions cell.
5. Continue through the notebook in order. Use **Shift+Enter** to run a cell and move to the next one.
6. Save your work to Google Drive or download your edited notebook before leaving the session.

The installation cell prepares the Qiskit packages used in the lab. If Colab asks you to restart the session after installation, do so, then continue from the imports cell. Your first installation may take a little while.

## How to work through the labs

For each experiment, **predict → run → explain → modify**. Write down what you expect before running the code, compare your prediction with the result, and explain any difference. Add text cells for your answers and observations.

The exercise cells contain working baseline examples. Modify them to complete the tasks rather than treating the initial output as your finished answer. Try the question yourself, open the hint if needed, and check the worked solution afterward. Discuss predictions with a partner when possible. Attempt optional extensions after the main activities.

Remember that a **shot** is one preparation and measurement of a circuit. A histogram of sampled results can differ slightly from exact probabilities. State-vector inspection is a simulator tool; it is not a direct measurement of every amplitude on a physical device.

## If something goes wrong

- **An import fails:** run the installation cell, then the imports cell. Restart the session if Colab requests it.
- **A variable or function is not defined:** run the earlier code cells in order. A new runtime does not remember previous sessions.
- **Your counts differ from your prediction:** first check whether your prediction concerns exact probabilities or finite-shot frequencies. Then check the gates, angles, and measurement wiring.
- **A two-qubit answer appears reversed:** revisit the bit-ordering section in Lab 2. Qiskit's default display puts q1 to the left of q0; the superdense-coding example explicitly rewires its classical output to display the message in its original order.
- **Your changes cause an error:** keep a copy of the original working cell and compare your changes with it. Ask your instructor if you cannot identify the cause.

## Further reading

- [IBM Quantum: Basics of quantum information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information)
- [Qiskit: Bit ordering](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering)
- [IBM Quantum: Fundamentals of quantum algorithms](https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms)

Use the references at the end of each notebook for more detail on that lab's topics.
