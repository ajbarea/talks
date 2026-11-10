# Federated Agents: Step One: the script

<!-- What I say on each talk slide, one section per slide in order; the slides' speaker notes are short prompts.
     ▶ marks a click: the next build step on the slide appears there.
     {path} is a figure from the deck's data; {if path}...{/if} holds only when the flag does.
     make script-length counts it; `python3 scripts/script_length.py <talk> --print` fills in today's figures. -->

## 1. Federated Agents: Step One

Hi, I'm AJ. Today I want to catch you up on Sphragis, which is my study of whether a model can learn an organization's house style, and on the Registered Report I'm sending to MSR 2027. If a term isn't clear, stop me.

## 2. Six parts, from the bigger problem to where your work connects

Six parts. The bigger problem, the arc this sits in, the venue, the method, where it stands, and where this work connects to yours.

## 3. Coding agents need a company's house style, which sits in private review history

Here is the bigger problem. A coding agent is useful once it follows how a company writes software. That is its house style, and it is mostly unwritten. In this made-up review, a reviewer says use our retry helper. Reviewers enforce this a lot: in one study of Microsoft code reviews, 38 percent gave feedback on coding conventions. Those lessons live in review history, which a company won't hand over. So federated learning is a natural fit: each company trains at home, and a server averages only what is shared.

## 4. Federated coding agents assume a house style exists, so I built the test first

Here's what I did. I built Sphragis, which turned public code review into {readings.examples_total} frozen examples from {readings.orgs_count} organizations, and I wrote the pass rule down before the test data is fetched. Here's why you should care. A federated coding agent rests on a chain of assumptions. An organization has a house style a model can learn. Training can share part of it. The private part stays private. And an attacker can't recover it. The first link is untested. To my knowledge, no study has tested whether a model learns more from an organization's other projects than from a foreign organization. And who your client is, what personalization keeps local and what an attacker can infer all rest on that link.

## 5. In federated terms, the first question is who the client should be

This is a question about the client. A client could be a project group or a whole organization. If house style stays with project groups, then a client drawn at the organization line promises more than it can keep. So step one tests two boundaries. Hypothesis one splits each organization's projects into two groups and asks whether style stays with its own group. Hypothesis two asks whether the organization carries style past its projects. I test that one on Qt, against Chromium as the foreign organization.

## 6. This report is step one of three; federated learning starts at step two

Here's the whole arc. This report is step one, and it has no federated learning in it. It asks whether there is a house style to learn at all, with one adapter per project group. An adapter is a small add-on trained beside a frozen model. ▶ Step two federates those adapters and asks what the shared part reveals about each organization. It waits on step one, because you can't federate a house style until a model can learn one. ▶ Step three is the coding agents themselves, where each company declares what may be shared. Steps two and three are where this meets your work.

## 7. MSR is a CORE rank A conference where software is studied through its data

Now the venue. MSR stands for Mining Software Repositories, a CORE rank A conference, now in its 24th edition. In 2027 it's in Dublin, Ireland, on April 26 and 27, beside ICSE. It studies software through its data, and code review is exactly that, which is why this study belongs there.

## 8. A Registered Report is reviewed twice: first as a plan, then as a study

MSR has a Registered Reports track, and a Registered Report is reviewed twice. In Stage 1, I submit a {venue.pages}-page plan with no confirmatory results, and {venue.stageOneReviewers} reviewers judge the question and the method. The best outcome is in-principle acceptance: if I follow the protocol, the study is likely to be published, whatever it finds. In Stage 2, I run it and send the full paper to the journal Empirical Software Engineering, and {venue.stageTwoReviewers} reviewers check how closely I followed the plan.

## 9. Why plan first: a reading can depend on how the data was split

Why does the plan go in first? Here's an example from my own development data, on the exact-match score I used before. One split of OpenStack's projects into two groups, read on five seeds, gave {readings.split_first} points, meaning that many more reviewer fixes matched exactly per hundred comments, and its interval sat above zero. It passed. ▶ Then I read five valid splits, two seeds each. They ran from {readings.split_low} to {readings.split_high}. ▶ On average, {readings.split_mean}. A plan written first fixes which splits are read, before the test data is read, so nobody can keep only the one that worked.

## 10. Two hypotheses, fixed before the data, compare adapters on the same test code

That is what a confirmatory study means: the hypotheses are fixed, and the data can only support them or not. Every adapter trains on {readings.n} examples, and all of them score the same held-out code. Hypothesis one: on held-out code from one project group, the adapter trained on that group beats the adapter trained on the organization's other group. ▶ Hypothesis two: that other group's adapter beats one trained on as much C++ code from Chromium. It's tested on Qt's C++ only.

## 11. The pass rule is written down: every test's interval must sit entirely above zero

And the pass rule is written down in advance. The score is how much probability an adapter gives the developer's real fix, per token. The smallest effect I care about is delta, {readings.delta} nats per token. Each token is about {readings.delta_pct} percent more likely on average, set as one more exact fix per hundred comments. A confidence interval is the range the data leave plausible. ▶ A test is supported when its interval sits entirely above zero. ▶ It's bounded when the interval sits entirely below delta, which I report as an upper limit, not as a win. ▶ Anything else is inconclusive. Hypothesis one passes only if all {readings.h1_cells} of its tests are supported: {readings.orgs_count} organizations, two scores each.

## 12. Three of four data windows are collected and frozen; the test window stays sealed

Where it stands. The data is divided by time into four windows. Pilot, train and development are collected and frozen, {readings.examples_total} examples across OpenStack, Wikimedia and Qt, plus a GitHub replication family and Chromium's pool. The fourth window, the test window, runs {readings.window_test}. It stays sealed. It is defined in the report, and it is fetched only after in-principle acceptance, so nothing can be tuned against it.

## 13. The pipeline and sizing are done; the confirmatory test has not run

What's done? The pipeline, the frozen datasets, the simulations that set each test's number of runs, and the label audit with its human check. Still open: submitting and registering the plan with the test window sealed, the final list of organizations, the GitHub family's sizing, fetching the sealed months, and every confirmatory run. The part this study is graded on hasn't happened, on purpose.

## 14. Development checks show the test finds a planted convention; the real one is untested

Can this test see a convention at all? I planted a marker in half the training examples, a fake convention I control, and the test found it in {readings.planted_found} of {readings.planted_total} development runs across three organizations. So the score responds to a planted convention. Whether it detects one as small as delta rests on the sizing simulations. It says nothing yet about real house style.

## 15. Next: reviewers see the plan, then the sealed months are fetched and run

Next. The abstract is due today, and the report is due November 20. Reviews come back December 23, my revision is due January 15, and the decision comes February 4. ▶ If it's accepted, I fetch the sealed months and run the study, present in Dublin in April, and send the full paper by September 30. ▶ Step two picks up from there.

## 16. The lab's strengths apply most at the federated-learning stages

Here's where your work connects, by area. Aggregation and robustness: which robust or control-theoretic rule still holds when each update is a low-rank adapter? Attacks: can a server tell which organization an update came from, even under secure aggregation? Data quality and metadata: can a client's data-quality profile inform how its update is weighted, and what should a company declare as shareable? There's also a way to help with this paper now. I'm the only human who has labeled these examples, so a second person labeling the same 77 OpenStack examples on their own would show how often two people agree. Metadata for the dataset release is the other small start.

## 17. Before federating agents, test that there is a house style to federate

To sum up. A federated coding agent assumes every company has a house style worth keeping. Step one tests that before we federate anything: whether style stays with project groups, and whether Qt carries it past its projects. The plan goes in before the test data is read, so the analysis can't be tuned and a negative answer can still publish. The dataset is frozen, and the test window stays sealed. Whether a house style exists at either boundary, and what a federated adapter reveals, are still open. That's my talk.

## 18. Thank you

Thank you. The slides are at the link, and I'm glad to take questions.
