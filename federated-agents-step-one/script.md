# Federated Agents: Step One: the script

<!-- What I say on each talk slide, one section per slide in order; the slides' speaker notes are short prompts.
     {path} is a figure from the deck's data; {if path}...{/if} holds only when the flag does.
     make script-length counts it; `python3 scripts/script_length.py <talk> --print` fills in today's figures. -->

## 1. Federated Agents: Step One

Hi, I'm AJ. Today I want to catch you up on Sphragis, which is my study of whether a model can learn an organization's house style, and on the Registered Report I'm sending to MSR 2027. If a term isn't clear, stop me.

## 2. Six parts, from the bigger problem to where your work connects

Six parts. The bigger problem, the arc this sits in, the venue, the method, where it stands, and where this work connects to yours.

## 3. Coding agents need a company's house style, which sits in private review history

Here is the bigger problem. A coding agent is useful once it knows how a company writes software: what its reviewers reject and what they ask for. That is its house style, and it is mostly unwritten. In this made-up review, a reviewer says use our retry helper. Lessons like that live in review history, which a company won't hand over. So federated learning is the natural fit: each company trains at home, and a server averages only what is shared.

## 4. Federated coding agents assume a house style exists, so I built the test first

Here's what I did. I built Sphragis, which turned public code review into {readings.examples_total} frozen examples from {readings.orgs_count} organizations, and I wrote the pass rule down before any test data exists. Here's why you should care. A federated coding agent rests on a chain of assumptions. An organization has a house style a model can learn. Training can share part of it. The private part stays private. And an attacker can't recover it. The first link is untested, and who your client is, what personalization keeps local and what an attacker can infer all rest on it.

## 5. In federated terms, the first question is who the client should be

In federated terms, this is a question about the client. A client could be a project group or a whole organization. If house style attaches to project groups, then a client drawn at the organization line promises more than it can keep. So step one tests two boundaries: between halves of an organization's projects, and between an organization and a foreign one.

## 6. This report is step one of three; federated learning starts at step two

Here's the whole arc. This report is step one, and it has no federated learning in it. It asks whether there is a house style to learn at all, with one adapter per half of an organization. An adapter is a small add-on trained beside a frozen model. Step two federates those adapters and asks what the shared part reveals about each organization. Step three is the coding agents themselves, where each company declares what may be shared. Federated learning comes after step one because you can't federate a house style until a model can learn one. Steps two and three are where this meets your work.

## 7. MSR is a CORE rank A conference where software is studied through its data

Now the venue. MSR stands for Mining Software Repositories, a CORE rank A conference, now in its 24th edition. In 2027 it's in Dublin, Ireland, on April 26 and 27, beside ICSE. It studies software through its data, and code review is exactly that, which is why this study belongs there.

## 8. A Registered Report is reviewed twice: first as a plan, then as a study

MSR has a Registered Reports track, and a Registered Report is reviewed twice. In Stage 1, I submit a {venue.pages}-page plan with no results, and {venue.stageOneReviewers} reviewers judge the question and the method. They can give in-principle acceptance, continuity acceptance or a rejection. With in-principle acceptance, if I follow the protocol, the study is likely to be published. In Stage 2, I run it and send the full paper to Empirical Software Engineering, and {venue.stageTwoReviewers} reviewers check how closely I followed the plan.

## 9. Why plan first: one split of my data passed, five splits averaged near zero

Why does the plan go in first? Here's an example from my own development data. One split of OpenStack's projects into two halves gave {readings.split_first} exact-match points, meaning that many more reviewer fixes matched exactly per hundred comments, and its interval sat above zero. It passed. Then I tried other valid splits. They ran from {readings.split_low} to {readings.split_high}, and the five averaged {readings.split_mean}. If I'd only seen the first, I would have reported a win. A plan written first fixes the analysis before the test data exists, so nobody can keep only the split that worked.

## 10. A confirmatory study fixes its hypotheses before the data; mine compare adapters

That is what a confirmatory study means: the hypotheses are fixed, and the data can only support them or not. Here are mine. Hypothesis one: on held-out code from one half of an organization, the adapter trained on that half beats the adapter trained on the other half. Hypothesis two: the other half's adapter beats one trained on another organization's C++ code. That one is tested on Qt, with Chromium as the foreign organization.

## 11. The pass rule is fixed: every test's confidence interval must sit entirely above zero

And the pass rule is fixed in advance. The score is how much probability an adapter gives the developer's real fix, per token. The smallest effect I care about is delta, {readings.delta} nats per token. In plain words, each token is about {readings.delta_pct} percent more likely, set as one more exact fix per hundred comments. A confidence interval is the range the data leave plausible. Hypothesis one passes only if all {readings.h1_cells} of its tests have an interval entirely above zero: {readings.orgs_count} organizations, on two scores. If every interval sits below delta, I report that as an upper limit, not as a win.

## 12. Three of four data windows are collected and frozen; the test window stays sealed

Where it stands. The data is divided by time into four windows. Pilot, train and development are collected and frozen, {readings.examples_total} examples across OpenStack, Wikimedia and Qt, plus a GitHub replication family and Chromium's pool. The fourth window, the test window, runs {readings.window_test}. It is sealed. Its definition is hashed, and it is fetched only after in-principle acceptance. So the data for this study isn't all collected, and that is by design.

## 13. The pipeline and sizing are done; the confirmatory test has not run

So exactly what's done? The pipeline, the frozen datasets, the simulations that fix each test's number of runs, and the label audit with its human check. Still open: the report's registration, the final list of admitted organizations, fetching the sealed months, and every confirmatory run. The part this study is graded on hasn't happened, on purpose.

## 14. Development checks show the test finds a planted convention; the real one is untested

Can this test see a convention at all? I planted a marker in half the training examples, a fake convention I control, and the test found it in {readings.planted_found} of {readings.planted_total} development runs across three organizations. That shows the instrument can see a convention when one is there. It says nothing yet about real house style.

## 15. Next: reviewers see the plan, then the sealed months are fetched and run

Next. The abstract is due today, and the report is due November 20. Reviews come back December 23, my revision is due January 15, and the decision comes February 4. If it's accepted, I fetch the sealed months and run the study, present in Dublin in April, and send the full paper by September 30. Step two picks up from there.

## 16. The lab's strengths apply most at the federated-learning stages

Here's where your work connects, by area. Aggregation and robustness: which robust or control-theoretic rule still holds when the update is a low-rank adapter? Attacks: can a server tell which organization an update came from, even under secure aggregation? Data quality and metadata: can a client's data-quality profile inform how its update is weighted, and what should a company declare as shareable? Those are the federated stages, steps two and three. There's also a small start before federation: a second human rater for the label audit, and metadata for the dataset release.

## 17. Before federating agents, test that there is a house style to federate

To sum up. A federated coding agent assumes every company has a house style worth keeping. Step one tests that assumption before we federate anything. The plan goes in before the data exists, so the analysis can't be tuned and a negative answer can still publish. The dataset is frozen, and the test window stays sealed. Whether a house style exists at either boundary, and what a federated adapter reveals, are still open. That's my talk.

## 18. Thank you

Thank you. The slides are at the link, and I'm glad to take questions.
