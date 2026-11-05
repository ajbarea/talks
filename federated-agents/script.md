# Federated Agents: the script

<!-- What I say on each talk slide, one section per slide in order; the slides' speaker notes are short prompts.
     {path} is a figure from the deck's data; {if path}...{/if} holds only when the flag does.
     make script-length counts it; `python3 scripts/script_length.py <talk> --print` fills in today's figures. -->

## 1. Federated Agents

Hi, I'm AJ Barea, a PhD student at RIT. This is Federated Agents: coding agents that learn each company's house rules without its code leaving.

## 2. I built two checked datasets of real code-review lessons

Here's what I did. I built an open-source tool that turns public code review into checked lessons. Each lesson is three things: a reviewer's comment, the code it was about, and the code the developer wrote next. With it I built two datasets: {readings.corpus_examples_openstack} lessons from OpenStack and {readings.corpus_examples_wikimedia} from Wikimedia, and the same tool builds GitHub communities for a replication. Here's why you should care. If you write code on a team, your reviewers keep repeating rules that no AI assistant has seen. Lessons like these could teach them, and my study tests whether an assistant learns them without your code leaving. Let me start with one of those rules.

## 3. AI coding assistants miss a company's unwritten house rules

Here's a house rule. An AI assistant opens a database connection directly, and this company's reviewers send it back: use our helper. Some rules are written into a rules file the assistant reads. Most are learned in code review, comment by comment, which AI assistants never see.

## 4. The data that would teach them is data no company wants to share

Every accepted, fixed or rejected suggestion is a training example. Pooled across companies, they would teach every assistant more, since much good practice carries over. But each company's code, and how its team works, would leave the building. So today it's all or nothing.

## 5. Four research fields meet in this work

This work sits where four research fields meet. Learning together, apart: many owners train one model, and each owner's data stays home. Small add-ons: instead of retraining a large model, you train a small add-on beside it. Learning from code review: the public record of review shows the rules teams really enforce. And testing what a model gives away: attacks that ask what a trained model reveals about its data. My idea puts all four together.

## 6. My idea: a shared add-on, a private add-on, and the company decides

My idea: every company runs the same frozen, open-weight base model with two small add-ons. The gold one is shared: only each company's changes to it go to a server that averages them, so code never travels. The green one is private and never leaves. Before training, the company lists which repositories may feed the shared add-on; the rest teach only the private one, and anyone can audit the list.

## 7. Other designs let the method pick what is shared; none tests whose it is

The blue dots are published designs. Across the bottom: who decides what is shared, from training itself to a fixed rule or a filter. Up the side: whether anyone tested the shared part. Most never did, and none asked whose it is. Mine, in gold, lets the company decide before training, and tests which company the shared part came from.

## 8. Tuning helps, {readings.team_title}

These are first runs on development data, not the sealed test. First, tuning helps: tuned on its community's own reviews, an assistant gets about {readings.tuned_exact_gain} more of every 100 reviewer fixes exactly right. Second, the team-specific part: I split a community's projects into two groups, each with its own assistant. OpenStack's own group's assistant {readings.team_openstack}; Wikimedia's {readings.team_wikimedia}. Next is privacy: can someone tell which company the shared add-on came from? The attacks are built.

## 9. {readings.split_gain_orgs}'s clear gain sits in the fix itself{if readings.split_beyond_names}, not only in names{/if}

Is the gain just a team's function and variable names? I split each gain into parts that add up to it. The top dot is the whole gain, measured in how likely the assistant finds the real fix, and its line is how sure I am. First, names against the rest: {if readings.split_beyond_names}on {readings.split_gain_orgs}, part of the gain clearly lies outside names.{/if}{unless readings.split_beyond_names}names may be most of it.{/unless} Second, what the fix changed against code carried over: {if readings.split_in_fix}the fix itself carries the gain.{/if}{unless readings.split_in_fix}whether the fix carries it is still open.{/unless} {if readings.split_copied_none}Carried-over code carries next to none.{/if} {if readings.split_any_unsettled}{readings.split_unsettled_orgs}'s whole gain is unsettled, so its split shows only a direction.{/if} The sealed test reads both again.

<!-- Each split's two parts, with a small end-of-text term, add up to the whole gain; one scale for both communities. -->

## 10. Every step up to the sealed test is built

Here's the whole method in three stages. The dataset: the tool collects public code review, drops account names, pairs each comment with the code the developer wrote next, cleans it, and seals the test months. The study: it splits each community's projects in two, trains an add-on per half, and scores how likely each one finds the developer's real fix. Both are built. Next come the sealed test, the shared and private add-ons, and the attacks on them.

## 11. Most of what code review holds never becomes a lesson

Here's what the tool sets aside on OpenStack. Most review comments go; the biggest group is about the commit message or the change as a whole. Of the pairs left, some drop out, like ones where the reviewer wrote the fix, which gives away the answer. Then copies go. The rest is what the study uses; Wikimedia follows the same rules.

<!-- Every rule and what it removed: ajbarea.github.io/sphragis/dataset -->

## 12. The test is built so it can't fool me

I made sure the test can't fool me. It must win twice: on the whole fix, and on the fix without its names, so a team's names alone cannot pass it. Each dot on the left is one way of dividing the data; any one can mislead, so the test averages many. I planted a fake house rule in half the training lessons: {if readings.planted_all}the test found it in every run.{/if}{unless readings.planted_all}it was missed in some runs, so the test waits until that is fixed.{/unless} And in simulations, it finds a real effect of the smallest size that matters almost every time.

## 13. The datasets are stage one; federated coding agents are the goal

The datasets are stage one, and I'm still collecting and checking data. By November 20th the plan goes to MSR 2027, the Mining Software Repositories conference, as a registered report: reviewers accept the method before any result exists, so even a no gets published. From February I open the sealed test, then build the two add-ons and try to break them, toward federated coding agents.

## 14. Three communities decide the answer, and GitHub checks it elsewhere

OpenStack, Wikimedia and Qt decide the answer, and each must pass; Qt said yes in writing. Beside them, Qt's own data is compared with Google projects: Chromium is the registered comparison, and Fuchsia is exploratory. GitHub, where review is often optional, is a separate replication: Apache and .NET qualify, LLVM and Grafana don't. Membership is fixed by November 20th, before any test result exists.

## 15. Before agents share a team's habits, test that there are habits to learn

Before agents share a team's habits, I first test that there are habits to learn. I built two datasets of real review lessons, {readings.corpus_examples_openstack} from OpenStack and {readings.corpus_examples_wikimedia} from Wikimedia. Tuned on them, an assistant gets about {readings.tuned_exact_gain} more fixes in 100 exactly right. And on OpenStack, a team's own assistant {readings.team_openstack}{if readings.split_in_fix}, in the fix itself{/if}. Two problems stay open. Whether the gain holds on the sealed test months, in every community. And whether the shared add-on gives away which company it came from. That's my talk.

<!-- Open problems: sphragis README "Where it stands" (the confirmatory contrast has not been run; dev readings size the design) and the FAQ on leakage (a measurement, not yet run on the shared add-on). -->

## 16. Thank you

Thank you. The slides are at the link, and I'm glad to take questions.
