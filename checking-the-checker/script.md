# Checking the Checker: the script

<!-- What I say on each talk slide, one section per slide in order; the slides' speaker notes are short prompts.
     {path} is a figure from the deck's data; {if path}...{/if} holds only when the flag does.
     make script-length counts it; `python3 scripts/script_length.py <talk> --print` fills in today's figures. -->

## 1. Checking the Checker

Hi, I'm AJ, a first-year PhD student here. This talk is about a tool I wrote to check my papers' references, and the six times it failed without telling me. If a term isn't clear, stop me. Let me start with what a different tool printed.

## 2. A clean report counts only if the checker can fail and says what it skipped

This is what a public citation checker printed for a PDF cut to its first 2,000 bytes. One line says it found nothing, and a later line says everything passed anyway. That's my one point today. A clean report counts only if the checker can fail, and tells you what it skipped. Here's what I did. In four weeks of use, I found six times my own checker had failed silently. I sorted those failures into three groups, found a guard for each, and tested two of the guards on five public checkers. Here's why you should care. Think of the last green check you saw in your CI. How do you know it ran? If a tool can't fail, all clear tells you nothing. So why citation checkers?

## 3. AI models still invent references, and a top conference now checks them with software

Language models still invent references. Across thirteen recent models, between 14 and 95 percent of the citations they were asked for were invalid. Some reach print: at eight AI and security venues, the share of accepted papers with an invalid citation went from under one percent to 1.61 percent in 2025. One top conference turned to software: ACL 2026 ran an automated checker, and it flagged over a hundred accepted papers, confirmed by hand, that cited work that doesn't exist. So the trust moves to the checker, and I looked hard at my own.

## 4. Six silent failures in my own checks; one let a broken paper pass for {case1.days} days

My checker is called dokimasia. It checks one bibliography of 103 entries that seven of my papers share. Each bar is one silent failure, and its length is how long it lasted. The worst was the first. One paper looked for its bibliography in the wrong folder. All {case1.citations} of its citations came out as question marks, and its reference list was empty. But the build said success, because the build script ignored the error. That lasted 71 days, and my checks only existed for the last 25 of them. Every time, the output looked valid. This is one tool, studied by the person who built it, so it shows these failures happen, not how often; later I find the same groups in five other tools. Lined up, my six fell into three groups.

## 5. The six failures fall into three groups, and each group needs its own guard

Every check does three things: it chooses what to check, it reads the inputs, and it reports a result. Each group is a failure at one of those steps, and each group gets its own guard. First, did not run. In cases 1 and 2, the check never looked at the broken paper, so it had nothing to complain about. The guard: the checker works out what to check by itself, and names what it skipped. Second, wrong inputs. In cases 3, 4 and 5, the check ran but read the wrong thing, like reading only one of the two dates a publisher database keeps for the same article. The guard: break the check on purpose and make sure it fails. Third, misreported. In case 6, arXiv, the big preprint server, refused requests sent too fast, and my code reported each refusal as a missing entry. The guard: report no answer apart from not found. A test can only reach the last two: a test of a check runs the check, so it never sees a check that didn't run.

## 6. Today's tests caught {rebreak.caught} of {rebreak.total} small changes that break my six fixes again

To test the guards today, I wrote eleven small changes that each break one of my six fixes again, and ran the tests after each. For cases 1 and 2, a change breaks the guard that replaced the old defect, like the build gate or the code that works out what to check; the old defects were outside the tool, so a test of the tool can't reach them. Each column is one change, and its height is how many tests failed. Nine of the eleven were caught. Two got through. One let the check pass a paper whose compiled bibliography was empty. The other removed the line that says a server was refusing requests. Both have tests now. So I asked whether other checkers have the same gaps.

## 7. Three of five public checkers printed a clean result after checking nothing

These are the five tools a 2026 study compared. I gave each one two kinds of nothing to check: a PDF it couldn't read, and a PDF with no reference section. A tool passes if it says it checked nothing and prints no clean verdict. A red cross means it printed one anyway. Three of the five did: all clear, all references verified OK, all verified successfully. Then I cut the network while four of them checked ten real references. The fifth works from local databases. Two of the four reported all ten as not found. The other two called them inconclusive or unverified, but some lines said not found or non-existent web page. In their public records, each of my three groups turns up in at least two of these five tools. Let me sum up.

## 8. A checker's all-clear counts only if it can fail and names what it skipped

I found six silent failures in my own checks, in three groups, each with its own guard: work out what to check and name what you skipped, break each check on purpose, and keep no answer apart from not found. When I broke my fixes again, today's tests caught nine of eleven. And three of five public checkers printed a clean result after checking nothing. Two problems stay open. These cases show the failures happen, not how often. And I haven't tested whether the guards find new defects, or find them sooner than another practice would. So next time you see a green check, ask whether it could have failed, and what it skipped. That's my talk.

## 9. Thank you

Thank you. The slides are at the link, and I'm glad to take questions.
