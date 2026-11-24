# When do quantum circuits keep federated training data private? Script

<!-- budget: 1300 words. About 9.5 minutes read aloud, plus about 2 minutes of dragging controls on the three lab slides: about 12 minutes inside a 13 to 14 minute slot. -->

## When do quantum circuits keep federated training data private?

Hi, I'm AJ, a first-year PhD student. My project asks one question: when a quantum model is trained the federated way, does the gradient it sends keep the training data private? By the end you'll know where it does and where it doesn't, and you can run the attack yourself in your browser. Please stop me any time a term isn't clear.

## Three parts: the attack, a live lab, then what else might stop it

Three parts. First, the attack, and why two papers disagree about it. Second, a live lab, where we change one thing at a time. Third, batches, hidden labels and training.

## In federated learning the data stays home; each client's update, here a gradient, travels

A quick setup. Several clients, say phones or hospitals, want to train one shared model without pooling their data. Each client trains the model on its own data and sends the server only its update; in my setting, one gradient. The server averages the updates and sends the new model back. The data stays home; the gradient travels. So, quick bet, type it in the chat: is that gradient private, yes or no?

## The gradient a client shares can rebuild the input it was computed from

A gradient is just a list of numbers, one per trainable angle, and that feels private. Here's the catch: the server knows the circuit, so it can play a guessing game: pick an input, compute that input's gradient, and adjust the guess until the two gradients match. If they match exactly, the guess is usually the input. That's the gradient-matching attack, and on classical networks it rebuilds images.

What I did: I attacked simulated 4- and 8-qubit circuits the way a curious server would, {rq1.attacks} attacks with exact gradients, then shot noise, batches, hidden labels and trained circuits, {paper.seeds} seeds per setting. Why you should care: these are exactly the gradients our parameter-shift code computes. With exact gradients, one input per update and a known label, every untrained circuit with one encoding layer and two or more trainable layers gave its input away on every seed. So if you typed yes, the answer is: not by itself.

## Two papers from one group disagree on whether the attack works on quantum circuits

Why isn't this settled? Two papers from the same group at JPMorgan disagree. Kumar and colleagues, in 2023, argue that expressive encodings make circuits private: many encoding frequencies give the matching loss many false dips, so the search gets lost. Papadopoulos and colleagues, in 2025, reconstruct inputs numerically once the gradient gives as many equations as unknowns or more.

They use different circuits, attacks and definitions. So my question is narrow: on one family of circuits, with one attack, where does each claim hold?

## The attacker knows the circuit and the angles, and solves for the input

Here's the family. Each qubit gets its input as a Y rotation. Then come ℓ trainable blocks, Y and Z rotations with a chain of CNOTs. That whole unit repeats r times, which is data re-uploading, and the output is the average Z measurement.

The attacker minimizes this loss: how far my guess's gradient is from the one I received. Zero means a perfect match.

Each attack ends one of four ways. Recovered: within {paper.recoveredRad} radians. Close: within {paper.closeRad}. Ambiguous: a different input fits just as well, so the gradient itself can't tell them apart. Stuck: the search stopped at a worse fit. Keep stuck and ambiguous apart; they mean very different things for privacy.

## At a fixed parameter count, more encoding repetitions left the search stuck more often

This is the live lab. It's a toy: one qubit, one hidden input, running in this browser. The curve is the matching loss for every possible guess, and the blue line marks the hidden input. Each restart is a ball rolling downhill. The number to watch is restarts that found the input.

I'll drag the repetitions up, keeping the total number of trainable blocks fixed. More repetitions mean more frequencies, so more dips for a restart to get trapped in. That's Kumar's mechanism. One input is a noisy sample, so at the foot of the panel the toy runs hidden inputs one to twenty, not picked. The pies thin out as repetitions grow.

On the right is what the paper measured, at 8 qubits and {rq1.params} effective parameters. Recovered seeds went from {rq1.rec1} of {paper.seeds} at one repetition down to {rq1.rec8} at eight. Restarts that found the input fell from {rq1.hits1} to {rq1.hits8} of {rq1.tries}. And every one of those failures was stuck, not ambiguous.

## Stuck is not private: with {budget.large} restarts, most stuck seeds gave up their input

But stuck only means the search gave up. So I'll add restarts. The attacker keeps the restart with the lowest loss, so it never needs to know the truth to pick the winner. In the toy's rows, one restart recovers about half of the twenty inputs, and twenty restarts recover them all.

The paper did the same at scale. I reran the {budget.circuits} hardest 8-qubit circuits with {budget.large} restarts instead of {budget.small}. On {budget.othersCount} of them, recovery jumped to {budget.othersMin} or {budget.othersMax} of {paper.seeds} seeds. The {budget.hardest} circuit stayed hard: only {budget.hardestRate} percent of its restarts found the input, and {budget.hardestHeld} seeds held. Its cost is unknown, not infinite. So on three of the four circuits, encoding repetitions acted like a work factor for the attacker, not a wall.

## With {rq2.lowShots} shots at 8 qubits, this attack almost always failed

On a real device, the client doesn't get exact gradients. Every expectation value is estimated from shots. I'll drag the shots down. The dip lifts off zero and shifts, and the restarts' end points spread. The toy still finds nearly every input at a hundred shots; only at ten does the noise defeat it on several. One qubit is the easy end: its gradient is far larger than its shot noise.

At 8 qubits, noise wins. At {rq2.lowShots} shots, at most {rq2.within8Max} seed in {paper.seeds} came within {paper.closeRad} radians, on each of the three circuits tested; at 4 qubits it was {rq2.within4Min} to {rq2.within4Max}. At 8 qubits the noise was as large as the gradient itself. One caution: that blocks this attack, and it is not a privacy guarantee. Sedrakyan, Grosshans and Kashefi show this year that quantum noise is no substitute for the calibrated noise of differentially private training.

## Every batch we tried with more unknowns than effective parameters was ambiguous

Next, batches. If the client averages its gradient over several examples, the attacker has to solve for all of them at once: more unknowns, but the same number of effective parameters, the angles whose gradient can be nonzero.

Up to {rq3.leakMax} unknowns per effective parameter, every circuit leaked on at least {rq3.fewestBelow} of {paper.seeds} seeds. From {rq3.heldMin} up, none did, and these weren't stuck searches: the attacker always found a different batch that fit the gradient just as well. With more unknowns than equations, many batches are expected to fit the same gradient.

## Hiding the label helped a little; training the circuit made no detectable net change

Two more, briefly. If the server doesn't know the labels, it can still fit each input's weight in closed form. That recovered fewer seeds: {rq4.knownOnly} only with the labels and {rq4.unknownOnly} only without, a p-value of {rq4.p}. Most of that was batches of two, where the extra failures were stuck: a harder search, not a hidden input.

And training the circuit first? Pooled over {rq5.tasks} tasks, {rq5.before} seeds were recovered only before training and {rq5.after} only after, p of {rq5.p}. No detectable net change.

## Repetitions slowed the attack; {rq2.lowShots} shots at 8 qubits and large batches stopped it

So, to sum up. A shared gradient can rebuild the input: with exact gradients, one input and a known label, every untrained circuit with one encoding layer and two or more trainable layers gave it away. More encoding repetitions slowed the attack, and more restarts recovered most stuck seeds. If you remember one line, make it this one: stuck is not private. What actually blocked this attack was {rq2.lowShots} shots per expectation value at 8 qubits, and batches with more unknowns than effective parameters, and neither one is a guarantee.

Two questions stay open. Can a client still train on gradients that noisy? And does the attacker's cost grow exponentially with the number of qubits? Two circuit sizes can't tell us. That's my talk.

## Thank you

Thank you. I'm pasting the lab's link in the chat now, and the QR code goes to the same place. Try to find a setting where the attack fails, then add restarts and see if it holds. I'm glad to take questions.
