# When do quantum circuits keep federated training data private? Script

<!-- budget: 1550 words. About 11 minutes read aloud, plus 2 to 3 minutes of dragging controls on the three lab slides, inside a 13 to 15 minute slot. -->

## When do quantum circuits keep federated training data private?

Hi, I'm AJ, a first-year PhD student. My final project asks one question: when a quantum model is trained the federated way, does the gradient it sends keep the training data private? Part of this talk is a live lab: a small circuit running right here in the browser, and you'll see an attack work, and fail, as I drag the controls. Please stop me any time a term isn't clear.

## Three parts: the attack, a live lab, then what else hides the input

Three parts. First, the attack, and why two papers disagree about it. Second, the live lab, where we change one thing at a time: encoding repetitions, restarts, then shot noise. Third, two more things that might hide the input, batches and labels, plus what happens after training. Then a short summary.

## The gradient a client shares can rebuild the input it was computed from

Here's the setting. In federated learning, the client keeps its data at home and sends the server only a gradient: a list of numbers, one per trainable angle. That feels private. But the server knows the circuit, so it can play a guessing game: pick an input, compute that input's gradient, and adjust the guess until the two gradients match. If they match exactly, the guess is usually the input. That's the gradient-matching attack, and on classical networks it rebuilds images.

What I did: I attacked simulated 4- and 8-qubit circuits the way a curious server would. That's {rq1.attacks} attacks with exact gradients, then more with shot noise, batches, hidden labels and trained circuits, {paper.seeds} seeds per setting. Why you should care: these are exactly the gradients our parameter-shift code computes. With exact gradients, one input per update and a known label, every untrained circuit with one encoding layer and two or more trainable layers gave its input away on every seed.

## Two papers from one group disagree on whether the attack works on quantum circuits

So why isn't this settled? Two papers from the same group at JPMorgan disagree. Kumar and colleagues, in 2023, argue that expressive encodings make circuits private: many encoding frequencies give the matching loss many false dips, so any search gets lost. Papadopoulos and colleagues, in 2025, reconstruct inputs numerically once the circuit has enough parameters: as many gradient equations as unknowns or more, and the search finds its way down.

They use different circuits, different attacks and different definitions. So my question is narrow: on one family of circuits, with one attack, where does each claim hold?

## The attacker knows the circuit and the angles, and solves for the input

Here's the family. Each qubit gets its input as a Y rotation. Then come ℓ trainable blocks, a Y and a Z rotation on every qubit with a chain of CNOTs. That whole unit repeats r times, which is data re-uploading, and the output is the average Z measurement.

The attacker minimizes this loss. Read it as: how far my guess's gradient is from the one I received. Zero means a perfect match. It knows the angles and the label, and it sees one gradient.

Each attack ends one of four ways. Recovered: within {paper.recoveredRad} radians. Close: within {paper.closeRad}. Ambiguous: it found a different input that fits just as well, so the gradient itself can't tell them apart. Stuck: the search stopped at a worse fit. Keep stuck and ambiguous apart; they mean very different things for privacy.

## At a fixed parameter count, more encoding repetitions left the search stuck more often

This is the live lab. It's a toy: one qubit, one hidden input, running in this browser. The blue arrow on the Bloch sphere is the client's input; the red one is the attacker's best guess. The curve is the matching loss for every possible guess, and the blue line marks the truth. Each red dot is one restart rolling downhill. The starting input is a preset, picked to show the effect clearly; a random one shows it more weakly.

With one repetition the curve has a few wide dips, and nearly every restart lands on the input. Now I'll drag the repetitions up, keeping the total number of trainable blocks fixed. Watch the curve. More repetitions mean more frequencies, so more dips, and more restarts get trapped in the wrong one. That's Kumar's mechanism, live.

On the right is what the paper measured, at 8 qubits and {rq1.params} effective parameters. Recovered seeds went from {rq1.rec1} of {paper.seeds} at one repetition down to {rq1.rec8} at eight. Restarts that found the input fell from {rq1.hits1} to {rq1.hits8} of {rq1.tries}. And every one of those failures was stuck, not ambiguous.

## Stuck is not private: with {budget.large} restarts, most stuck seeds gave up their input

But stuck only means the search gave up. So, restarts. The toy is now at eight repetitions with one restart, and it's stuck. I'll add restarts one at a time. Five miss, and on the sixth a restart lands in the right dip, and since it has the lowest loss, the attacker keeps it. It needs no knowledge of the truth to pick it.

The paper did the same thing at scale. I reran the {budget.circuits} hardest 8-qubit circuits with {budget.large} restarts instead of {budget.small}. On {budget.othersCount} of them, recovery jumped to {budget.othersMin} or {budget.othersMax} of {paper.seeds} seeds. The {budget.hardest} circuit stayed hard: only {budget.hardestRate} percent of its restarts found the input, and {budget.hardestHeld} seeds held. That cost is unknown, not infinite. So on three of the four circuits, encoding repetitions acted like a work factor for the attacker, not a wall; on the eight-repetition circuit, we don't know the price.

## At 8 qubits, {rq2.lowShots} shots per expectation value hid almost every input

On a real device, the client doesn't get exact gradients. Every expectation value is estimated from shots. The toy now computes the gradient with the parameter-shift rule, from sampled measurements. I'll drag the shots down. The dip lifts off zero and shifts, and the guess slides away with it. At ten shots it misses.

The toy is the easy end: one input against many gradient entries, so the noise mostly averages out. The paper's 8-qubit circuits are where noise wins. At {rq2.lowShots} shots, at most {rq2.within8Max} seed in {paper.seeds} came within {paper.closeRad} radians, on each of the three circuits tested. At 4 qubits, it was {rq2.within4Min} to {rq2.within4Max}. Alongside that: at 8 qubits the noise in the gradient was as large as the gradient itself.

## Every batch we tried with more unknowns than effective parameters was ambiguous

Next, batches. If the client averages its gradient over several examples, the attacker has to solve for all of them at once: more unknowns, but the same number of effective parameters, the angles whose gradient can be nonzero.

Up to {rq3.leakMax} unknowns per effective parameter, every circuit leaked on at least {rq3.fewestBelow} of {paper.seeds} seeds. From {rq3.heldMin} up, none did. And these weren't stuck searches: the attacker always found a different batch that fit the gradient just as well. With more unknowns than equations, many batches are expected to fit the same gradient, and the attack found one that fit as well every time.

## Hiding the label helped a little; training the circuit made no detectable net change

Two more defenses, briefly. If the server doesn't know the labels, it can still fit each input's weight in closed form. That recovered fewer seeds: {rq4.knownOnly} were recovered only with the labels and {rq4.unknownOnly} only without, a p-value of {rq4.p}. Most of that was batches of two, on one circuit, where the extra failures were stuck: hiding the label made the search harder rather than hiding the input.

And training the circuit first? Pooled over {rq5.tasks} tasks, {rq5.before} seeds were recovered only before training and {rq5.after} only after, p of {rq5.p}. No detectable net change, though the tasks leaned opposite ways; one of them, low-frequency curves, is a lead I keep in the backup slides.

## Repetitions slowed the attack; {rq2.lowShots} shots at 8 qubits and large batches stopped it

So, to sum up. A shared gradient can rebuild the input. With exact gradients, one input per update and a known label, every untrained circuit with one encoding layer and two or more trainable layers gave it away on every seed. More encoding repetitions slowed the attack, and more restarts recovered most stuck seeds, though not on the eight-repetition circuit. What actually hid the input was {rq2.lowShots} shots per expectation value at 8 qubits, and batches with more unknowns than effective parameters.

Two questions stay open. Can a client still train on gradients as noisy as {rq2.lowShots} shots? And does the attacker's cost grow exponentially with the number of qubits? Two circuit sizes can't tell us. That's my talk.

## Thank you

Thank you. The code, the raw results and this lab are all public, and the QR code brings you here. I'm glad to take questions.
