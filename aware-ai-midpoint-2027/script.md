# AWARE-AI midpoint talk: the script

<!-- What I say on each slide, one section per slide in order; the slides' speaker notes are three short prompts.
     {readings.<key>} is a figure from federated-agents/data/readings.js; build.py fills it in, checks the sections
     against the slides, and fails past 4.5 minutes at 140 words a minute. Read out/script.md, the filled copy. -->

## 1. AJ Barea

Hi, I'm AJ Barea, a first-year PhD student in Computing and Information Sciences, in the AI Software track, advised by Dr. Leon Reznik. My research asks one question: when a model learns house style from code review, does that style belong to a group of projects, to the whole organization, or to neither? I'll show the problem, my study, what else I've done this year, and where the study stands.

## 2. AI coding assistants rarely see an organization's unwritten house style

Here's the problem. Say an AI assistant opens a database connection directly. This team's reviewers send it back: please use our helper. That's a house rule. Most are never written down. They live in code review, one comment at a time, and AI assistants rarely see them. If you put an assistant on your team, you want it to follow your team's rules. So my question is whose rules a model picks up: those of a group of projects, or those of the whole organization.

## 3. I test where a learned house style transfers: within projects, or across an organization

Here's my study. I take an organization's public code reviews, like OpenStack's, and split its projects into two halves, many times over. On each half I train a small add-on to an open coding model, which stays frozen. Then I score every add-on on reviews from half A that none of them trained on: how much probability does it give the developer's real fix? If the own add-on beats its sibling, style stays with its projects. For Qt, I add a foreign add-on, trained on the same amount of C++ from Chromium. If the sibling beats it, Qt has a house style beyond the projects it was learned on.

## 4. On development data, the test finds a house rule when one is planted

Here's what's built. An open-source tool turns public code review into checked lessons: a reviewer's comment, the code it was about, and what the developer wrote next. It produced {readings.corpus_examples_openstack} lessons from OpenStack and {readings.corpus_examples_wikimedia} from Wikimedia. On development months, tuning on a community's own reviews gets about {readings.tuned_exact_gain} more fixes in 100 exactly right than the untuned model. And so the test can't fool me, I planted a fake house rule in the training data. The score found it in {readings.planted_found} of {readings.planted_runs} splits. The real test months stay sealed.

## 5. Alongside the study: a lab rotation, an oral paper, and talks

Alongside the study: in my AWARE-AI lab rotation with Professor Richard Lange's BONSAI lab, I opened four pull requests to the lab's shared code, including tests that run on every change and a memory fix. Our hackathon teams won two awards. Our makesense paper was accepted as an oral at IAAI-27, in Montréal next month, and I co-authored two chapters in the SCADS 2026 technical report. With my lab, I'm a co-author on a journal paper and a conference paper on federated learning, and we gave a talk at the Rochester Security Summit.

## 6. Next, reviewers judge the plan; then the sealed months answer where house style belongs

Here's where the study stands. [FILL: confirm] The plan went to MSR 2027 as a registered report on November 20th, and the reviews came back December 23rd. [FILL: one line on what they said.] My response is due January 15th, and the decision comes February 4th. Reviewers judge the method before any result exists, so once they accept it in principle, the journal paper is likely published whatever the answer, if I follow the plan. Then I open the sealed months, and the full paper goes to the journal Empirical Software Engineering by September 30th. The bigger goal is coding agents that share what organizations have in common without leaking what's private. But first, I test where house style lives, if anywhere. That's my talk. Thank you.
