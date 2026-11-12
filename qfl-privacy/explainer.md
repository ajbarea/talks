<!-- budget: 1900 words -->
# QFL privacy talk: explainer sheet

For AJ, before the CSCI-739 talk. Each equation on the slides, in plain words, with a few lines of
Python you can run. Then what the live lab does on each slide, and what to say when it misbehaves.

## Federated learning, in one picture (slide 3)

Several clients train one shared model without pooling their data (McMahan et al., 2017). Each
round, every client trains the current model on its own data and sends back only its update (here
the gradient g; FedAvg sends weights after a few local steps); the server averages the updates into
the next model. The data never leaves the client, so FL sounds private; the talk asks whether g
gives it away anyway. The diagram plays one round: red dots are gradients going up, Σ the average,
grey dots the new model coming back. In one line: "the data stays home, the gradient travels."

## The equations

### The circuit's output, f(x; θ)

Each qubit gets its input as a Y rotation, R_Y(x). Then come trainable rotations R_Y(θ) and R_Z(θ)
and a chain of CNOTs. The output is the Z measurement averaged over the qubits, a number between −1
and 1. With one qubit and nothing trainable, the output is cos x: x = 0 gives |0⟩ and +1, x = π
gives |1⟩ and −1.

```python
import numpy as np

x = 0.8
state = np.array([np.cos(x / 2), np.sin(x / 2)])  # R_Y(x)|0>
print(state[0] ** 2 - state[1] ** 2, np.cos(x))  # <Z> both ways: 0.6967 0.6967
```

### On the Bloch sphere: R_Y(x)|0⟩ sits at (sin x, 0, cos x)

An encoded input is a point on the circle through |0⟩ and |1⟩, at angle x from |0⟩. That is why
the live lab can show the hidden input and the guess as two arrows: the angle between them is the
error the paper measures. Angles are compared modulo 2π, because R_Y(x + 2π) only flips the
state's global phase.

### The client's gradient, g = ∇_θ (f(x; θ) − y)²

The client's loss is the squared gap between output and label. Its gradient is one number per
trainable angle: how the loss changes if that angle moves. That list is what the client sends.

### The parameter-shift rule: ∂f/∂θ = [f(θ + π/2) − f(θ − π/2)] / 2

For a rotation gate, the exact slope comes from running the circuit twice, with the angle shifted
up and down by a quarter turn. A device computes gradients this way, and so does the live lab.

```python
f = lambda t: np.cos(0.8 + t)  # one qubit: R_Y(x) then R_Y(t)
t = 0.3
print((f(t + np.pi / 2) - f(t - np.pi / 2)) / 2, -np.sin(0.8 + t))  # both -0.8912
```

### The attack: L(x̂) = ‖ ∇_θ (f(x̂; θ) − y)² − g ‖²

Read it as: how far my guess's gradient is from the one I received. x̂ ("x-hat") is the guess. The
attacker knows θ and y, computes the gradient its guess would produce, and moves the guess to shrink
the gap. Zero means the guess explains the gradient exactly. The attacker restarts from several
starting guesses and keeps the one with the lowest L, which needs no knowledge of the true input.

```python
y = 1.0
grad = lambda x, t: 2 * (np.cos(x + t) - y) * (-np.sin(x + t))  # d/dt of (f - y)^2
g = grad(0.8, 0.3)  # what the client sends
L = lambda xh: (grad(xh, 0.3) - g) ** 2
print(L(0.8), L(1.5))  # 0.0 at the truth, > 0 elsewhere
```

That one-parameter example also shows the 1 × 1 problem: with as many gradient entries as
inputs, another guess can give L = 0 too. Scan it: `xs = np.linspace(0, 2*np.pi, 100001);
print(xs[L(xs) < 1e-8].round(2))` finds the truth at 0.80 and a second exact match near 2.59.

### The four outcomes

- **Recovered:** every feature of the input within 0.05 rad of the truth.
- **Close:** within 0.2 rad. Still a leak at noisy shot counts.
- **Ambiguous:** further away, but L(x̂) ≤ L(x) + 10⁻⁶‖g‖². Another input fits the gradient at
  least as well as the truth, so the gradient cannot tell them apart. The 10⁻⁶‖g‖² term is a small
  slack for rounding.
- **Stuck:** further away and a worse fit than the truth. The search stopped in a false dip or ran
  out of iterations. A better search might still win, which is why "stuck is not private".

### Effective parameters, P_eff = P − N

The circuit has P = 2rℓN angles: r repetitions, ℓ blocks, two rotations per qubit per block. The
last block's Z rotations are followed only by CNOTs and a Z measurement, so they never change the output; their
gradient is always zero. The other P − N angles each give one useful equation.

### Unknowns per effective parameter, NB / P_eff (batch slide)

A batch of B inputs on N qubits has NB unknown numbers. The gradient still gives only P_eff useful equations. Above
1, there are more unknowns than equations, and many batches fit the same gradient. The paper's grid
recovered inputs up to 0.67 and never from 1.14, so the crossover lies between.

### Shot noise: ⟨Z⟩ ≈ 2k/S − 1, error shrinks like 1/√S

With S shots, k of them read 0, and 2k/S − 1 estimates ⟨Z⟩. Its standard error falls like 1/√S, a
slope of −1/2 on a log-log plot. The paper's errors fell with slopes −0.54 to −0.49, the same rate.
Shot noise blocked this attack at 8 qubits; that is not a privacy guarantee. Sedrakyan, Grosshans
and Kashefi (arXiv:2606.29293, 2026) show quantum noise "does not provide a satisfactory
replacement" for the calibrated noise of DP-SGD.

```python
rng = np.random.default_rng(0)
p = (1 + 0.3) / 2  # <Z> = 0.3
for S in (100, 10_000):
    est = 2 * rng.binomial(S, p, 2000) / S - 1
    print(S, est.std(), 2 * np.sqrt(p * (1 - p) / S))  # spread matches the formula
```

### The label-free attack (backup): input i adds c_i ∇_θ f(x_i)

With a squared loss, each input adds its own gradient times a weight c_i = 2(f − y_i)/B. Without
the labels, the attacker does not know the weights, so for each guess it solves for the best ones
by least squares and matches what remains.

### The p-values: exact McNemar test

Each seed is attacked twice (label known or hidden; before or after training). Only seeds where
the two disagree count. If hiding the label did nothing, those seeds would split 50/50 like coin
flips; p is the chance of a split at least as lopsided as 14 to 3.

```python
from scipy.stats import binomtest

print(binomtest(3, 14 + 3, 0.5).pvalue)  # 0.0127, the slide's 0.013
```

## The live lab, slide by slide

The panel is a toy: one qubit, one input, 8 trainable blocks in all, simulated in the browser. The
attack is Adam on the guess for 150 steps, with the loss's exact slope; the paper used L-BFGS-B for
up to 500 iterations. The toy can be fast because each gradient entry is a Fourier series in the
guess with frequencies up to 2r (re-uploading r times gives the output frequencies up to r), so a
few samples per client give the whole loss curve. The
outcome rule and thresholds are the paper's. Every number you quote about the paper comes from the
right-hand figure; the counts at the panel's foot are the toy's own, and the panel labels them so.

Each lab slide shows the lab page (ajbarea.github.io/talks/qfl-privacy/lab) at that slide's tab,
opening on hidden input 1; − and + step through the simulator's seeds, not picked. One input is a
noisy sample, so the rows at the foot of the panel run inputs 1 to 20 for each value of the control,
scored like the paper's figure beside them. A search takes about 5 seconds: restarts are released one
after another, each rolling for 1.8 s with a short fading trail. The bar under the panel is its
timeline: Play or Pause, step one point back or forward (Shift jumps to the next landing), drag to
scrub, and ½× or ¼× to slow it. Reduced motion opens on the end; step through it instead. "Open the
full lab" opens the page with every tab, including every run the paper made. The PDF and a
downloaded copy show the paper's figure and the lab's address in place of the panel.

| Slide | Control | Hidden input 1 | The rows (inputs 1 to 20) |
|---|---|---|---|
| Repetitions | Encoding repetitions; 10 restarts, exact | 8, 10, 10, 8 of 10 restarts hit at 1, 2, 4, 8 repetitions: no trend | Restarts that hit, of 200: 175, 161, 133, 120 |
| Restarts | Restarts; 8 × 1, exact | Stuck with 1 restart, recovered from 2 on | Inputs recovered, of 20, with 1, 2, 5, 10, 20 restarts: 9, 15, 19, 20, 20 |
| Shots | Shots; 2 × 4, 10 restarts | Recovered from exact down to 1,000 shots (0.035 rad); close at 100 (0.054) and 10 (0.162) | Within 0.2 rad, of 20, at 10, 100, 1,000 shots and exact: 15, 19, 20, 20 |

Controls: click, or Tab into the panel and use the arrow keys, which never turn the slide while a
control has them. After a click the next clicker press turns the slide again.

## If the live panel misbehaves

- **The clicker moved a control instead of the slide:** click the slide's title, then advance.
- **A result differs from what you meant to show:** set hidden input 1 again and press Replay;
  every input replays identically.
- **One input goes against the slide:** expected; say "one input is a noisy sample" and point at the
  rows, which carry the trend. Never step through inputs hunting for one that agrees.
- **The animation is too quick to talk over:** press ½× or ¼× and Replay, or Pause and step.
- **The panel is blank or frozen:** carry on from the paper's figure; it holds the slide's claim.
  The PDF and PowerPoint copies show the paper's figure and the lab's address in its place.
- **No network:** the deck works offline once loaded; a downloaded copy opened as a file shows the
  paper's figures without the panel.
- **Someone asks why the toy is so easy at 100 shots:** its gradient is about 50 times its shot
  noise there (median squared norms, inputs 1 to 200, 2 × 4). At 8 qubits the paper's noise was as
  large as the gradient (0.16 against 0.14). Entries per input match (15 each), so it is the
  signal's size, not the count.

## Questions to expect

- **"R_Y(x) then R_Y(θ) is one rotation. Is the attacker really solving for x + θ?"** Yes. The paper says so: the encoding gate and the first trainable R_Y act as R_Y(x + θ), and since the attacker knows θ, solving for that angle is solving for x.
- **"Why did the gradient shrink from 0.72 to 0.14 between 4 and 8 qubits?"** The paper reports it, but does not test why. Whether it is the start of a barren plateau is open. Say so.
- **"Would an attacker that keeps its guesses inside [0, π) avoid the ambiguous answers?"** Some, possibly. The results did not store the guesses, so we cannot count how many fell outside. It is on the backup limits slide.
- **"Does Heredge et al.'s Lie-algebra attack apply here?"** Not computed. We did not work out these circuits' Lie algebras.
- **"Is the toy cherry-picked?"** No. Every slide opens on hidden input 1, and the rows run inputs 1 to 20, the simulator's first seeds. Over 200 inputs its restarts that hit fall from 82% at one repetition to 55% at eight, but with 10 restarts an input almost never ends stuck: one qubit is the easy end. Every number in the paper's figures, on the right of each lab slide, comes from the paper.
- **"How many inputs of an ambiguous batch still leaked?"** Not measured: a batch is scored by its worst-matched input.

