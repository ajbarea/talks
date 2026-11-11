# Federated Agents: the script

<!-- What I say on each talk slide, one section per slide in order; the slides' speaker notes are short prompts.
     {path} is a figure from the deck's data; {if path}...{/if} holds only when the flag does.
     make script-length counts it; `python3 scripts/script_length.py <talk> --print` fills in today's figures. -->

## 1. Federated Agents

Hi, I'm AJ Barea, a PhD student at RIT. This is Federated Agents: coding agents that learn each company's house style without its code leaving.

## 2. I built two checked datasets of real code-review lessons

Here's what I did. I built an open-source tool that turns public code review into checked lessons. Each lesson is three things: a reviewer's comment, the code it was about, and the code the developer wrote next. With it I built two datasets: {readings.corpus_examples_openstack} lessons from OpenStack and {readings.corpus_examples_wikimedia} from Wikimedia, and the same tool builds Qt's data and GitHub's for a replication. Here's why you should care. If you write code on a team, your reviewers keep repeating rules that AI assistants rarely see. Lessons like these could teach them, and my study first tests whether an assistant can learn them at all. Let me start with one of those rules.

## 3. AI coding assistants miss a company's unwritten house style

Here's a house rule. An AI assistant opens a database connection directly, and this company's reviewers send it back: use our helper. Some rules are written into a rules file the assistant reads. Most are learned in code review, comment by comment, which AI assistants rarely see.

## 4. The data that would teach them is data no company wants to share

Every accepted, fixed or rejected suggestion is a training example. Pooled across companies, they would teach every assistant more, since much good practice carries over. But each company's code, and how its team works, would leave the building. So today it's all or nothing.

## 5. Four research fields meet in this work

This work sits where four research fields meet. Learning together, apart: many owners train one model, and each owner's data stays home. Small add-ons: instead of retraining a large model, you train a small add-on beside it. Learning from code review: the public record of review shows the rules teams really enforce. And testing what a model gives away: attacks that ask what a trained model reveals about its data. My idea puts all four together.

## 6. My idea: a shared add-on, a private add-on, and the company decides

My idea: every company runs the same frozen, open-weight base model with two small add-ons. The blue one is shared: only each company's changes to it go to a server that averages them, so code never travels. The orange one is private and never leaves. Before training, the company lists which repositories may feed the shared add-on; the rest teach only the private one, and anyone can audit the list.

## 7. Other designs let the method pick what's shared; none I found tests its source

The grey dots are published designs. Across the bottom: who decides what is shared, from training itself to a fixed rule or a filter. Up the side: whether anyone tested the shared part. Most never did, and none I found asked whose it is. Mine, in blue and orange, lets the company decide before training, and will test which company the shared part came from.

## 8. Tuning helps; the sealed test asks if the gain is the team's

These are first runs on development data, not the sealed test. First, tuning helps: tuned on its community's own reviews, an assistant gets about {readings.tuned_exact_gain} more of every 100 reviewer fixes exactly right than the untuned model. Second, the team-specific part: I split a community's projects into two groups, each with its own assistant. Whether a group's own assistant beats its sibling's is the registered test, and it is read only on the sealed months; the development runs size that test rather than preview its answer. Next is privacy: can someone tell which company the shared add-on came from? The attacks are built.

## 9. Every step up to the sealed test is built

Here's the whole method in three stages. The dataset: the tool collects public code review, pseudonymizes accounts, pairs each comment with the code the developer wrote next, cleans it, and seals the test months. The study: it splits each community's projects in two, trains an add-on per half, and scores how likely each one finds the developer's real fix. Both are built. Next come the sealed test, the shared and private add-ons, and the attacks on them.

## 10. Most of what code review holds never becomes a lesson

Here's what the tool sets aside on OpenStack. Most review comments go; the biggest group is about the commit message or the change as a whole. Of the pairs left, some drop out, like ones where the reviewer wrote the fix, which gives away the answer. Then copies go. The rest is what the study uses; Wikimedia follows the same rules.

<!-- Every rule and what it removed: ajbarea.github.io/sphragis/dataset -->

## 11. The test is built so it can't fool me

I made sure the test can't fool me. The main test must win twice: on the whole fix, and on the fix without its names, so a team's names alone cannot pass it. Each dot on the left is one way of dividing the data; any one can mislead, so the test averages many. On the development months, I planted a fake house rule in half the training lessons: {if readings.planted_all}the test found it in every run.{/if}{unless readings.planted_all}it was missed in some runs, so the test waits until that is fixed.{/unless} And in simulations, it finds a real effect of the smallest size that matters almost every time.

## 12. The datasets are stage one; federated coding agents are the goal

The datasets are stage one, and I'm still collecting and checking data. By November 20th the plan goes to MSR 2027, the Mining Software Repositories conference, as a registered report: reviewers judge the method before any test result exists, so publication rests on the method, not the answer. If they accept it in February, I open the sealed test and the full paper goes to the journal Empirical Software Engineering before September 30th; then I build the two add-ons and try to break them, toward federated coding agents.

## 13. Three communities decide the answer, and GitHub checks it elsewhere

OpenStack, Wikimedia and Qt decide the answer, and each must pass; Qt said yes in writing. Second, Qt's C++ is compared with Google projects' C++: Chromium is the registered comparison, and Fuchsia is exploratory. GitHub, where review is often optional, is a separate replication: Apache and .NET qualify, LLVM and Grafana don't. Membership is fixed by November 20th, before any test result exists.

## 14. Before agents share a team's habits, test that there are habits to learn

Before agents share a team's habits, I first test that there are habits to learn. I built two datasets of real review lessons, {readings.corpus_examples_openstack} from OpenStack and {readings.corpus_examples_wikimedia} from Wikimedia. On the development months, an assistant tuned on them gets about {readings.tuned_exact_gain} more fixes in 100 exactly right, and the score found a planted house rule in {readings.planted_found} of {readings.planted_runs} splits, across all three communities. Two problems stay open. Whether style transfers on the sealed months: a community's own assistant against its sibling's in all three, and Qt against Chromium. And whether the shared add-on gives away which company it came from. That's my talk.

<!-- Open problems: sphragis README "Where it stands" (the confirmatory contrast has not been run; dev readings size the design) and the FAQ on leakage (a measurement, not yet run on the shared add-on). -->

## 15. Thank you

Thank you. The slides are at the link, and I'm glad to take questions.
