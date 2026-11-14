# Five Claude apps, one favorite: the script

<!-- What I say on each talk slide, one section per slide in order; the slides' speaker notes are short prompts.
     {path} is a figure from the deck's data; {if path}...{/if} holds only when the flag does.
     make script-length counts it; `python3 scripts/script_length.py <talk> --print` fills in today's figures. -->

## 1. Five Claude apps, one favorite

Hi everyone. Dr. Reznik asked me to explain Claude Duet, the new agent Anthropic announced on October 21st. I'll do that, side by side with the other four Claude apps. Here's the one idea to take home: pick the app by the place your work lives. And for code, start with Claude Code, my favorite. Please stop me any time. Here's the map. 

<!-- Sources: Introducing Claude Duet, October 21, 2026. -->

## 2. Each Claude app is built for a different place your work lives

Your work lives in five places: a conversation, your computer, your code, your research, and your accounts, like email and calendar. Anthropic has built one app for each: Claude chat, Claude Desktop, Claude Code, Claude Science and Claude Duet. Here's what I did with them. Last week I sent three changes to Richard Lange's lab code with Claude Code, and I've been in Duet's preview since October 27th. Here's why you should care. An app can only help with work it can reach. Duet can't see your lab's files. So pick the app by the place. Let's take them in the order they came out. 

<!-- Sources: each app's announcement; nn-library #17, #18, torch-mlflow-template #3. -->

## 3. Claude chat is for a conversation: you ask, it answers and drafts

First, the oldest: Claude chat, at claude.ai since July 2023, and on your phone and desktop too. It's for a conversation. You ask; it answers, drafts and explains. On paid plans it now also makes documents, slides and designs right in the chat. In practice, researchers use it most to draft their papers: Anthropic found that's about one in five research chats, and answering peer reviewers is another one in fifteen. The limit is what it can reach. In the browser, it sees only what you paste, upload or connect. It can't open the files on your laptop. For that, there's the desktop app. 

<!-- Sources: Anthropic, Claude 2 announcement, July 11, 2023; claude.com pricing; Claude Cowork and chat are now one Claude, September 16, 2026; Anthropic, How researchers use Claude, November 5, 2026 (drafting manuscripts 18.6%, peer-review replies 6.7%). -->

## 4. Claude Desktop is for your computer: it works in your own folders

Claude Desktop came in October 2024 for Mac and Windows; Linux is in beta now. It's for your computer. One app holds the chat, Cowork for longer tasks, and Claude Code, and it can read and write the folders you choose. This summer, my SCADS team built an analyst tool called makesense. It installs into Claude Desktop from one ZIP file and runs on the analyst's own computer. The limits: to reach your files, the app has to be open on that computer. Close it, and Claude can keep working in the cloud, but not in your folders. And its Cowork mode runs a whole Linux virtual machine: when I installed it, the app took about 13 gigabytes of disk, and other users report ten to twelve. Next, the app for code. 

<!-- Sources: Anthropic on X, October 31, 2024; help center, Install Claude Desktop and Get started with Claude Cowork; makesense, August 2026. -->

## 5. Claude Code is for your code: it reads, edits and tests your repository

Claude Code arrived in February 2025 as a research preview, and became generally available that May. It's for your code. It works in your repository, from the terminal, your editor, the desktop app or the web. It reads the code, edits files and runs your tests. In my work: for Richard Lange's lab, I used it to write a change that cuts the memory one step needs, the step that compares two neural networks, from about a gigabyte to under a megabyte. It's also a tab in Desktop; the place is your repository, wherever you open it. The limit: it makes confident mistakes, so read every change before you commit it. Next, research. 

<!-- Sources: Anthropic, Claude 3.7 Sonnet and Claude Code, February 24, 2025; Claude 4, May 22, 2025; nn-library #18. -->

## 6. Claude Science is for your research: each result is traced to its code

Claude Science has been a beta since June 30th. It's for your research. It's a separate app that runs on your computer, your lab's server or a cluster. You describe an analysis in plain words. It writes and runs the code in a sandbox, and saves every figure with the code and history that made it. It started in biology, but it works for any field. In practice, UCSF's Brain Tumor Center used it to run genetic workups in about a tenth of the time they used to take, and checked the results independently. The limit: a reviewer checks its claims against what ran, but it doesn't rerun the analysis. You still check the results yourself. And last, Duet. 

<!-- Sources: Anthropic, Claude Science announcement, June 30, 2026 (UCSF Brain Tumor Center, roughly one-tenth the time, independently validated); Claude Science docs overview; Get started with Claude Science (help center). -->

## 7. Claude Duet is for your accounts: it checks them, then comes to you

Duet is the newest, a research preview since October 21st. It's for your accounts. It has its own computer in Anthropic's cloud, so it keeps working with your phone and laptop off. Every few hours it checks your connected accounts, and when something needs you, it comes to you. Here's a real one from November 1st: it read an email Richard Lange sent me and offered to draft my rotation wrap-up. Before it sends a message, makes a payment, signs a document or deletes anything, it shows you first and waits for your yes. The limits: it doesn't know what my other Claude apps have done. It read my email and offered to start work that Claude Code had already finished with me. It can't see the files on your computer either, and it isn't on Team plans yet, so it isn't on our lab's plan. Now, all five on one page. 

<!-- Sources: Introducing Claude Duet, October 21, 2026; Get started with Claude Duet (help center); my Duet app, November 1. -->

## 8. Pick the app by where the work lives; for code, start with Claude Code

Here's the whole talk on one slide. A question or a draft: the chat. Files on your laptop: Desktop. A repository: Claude Code. An analysis you'll need to reproduce: Claude Science. Your inbox and calendar: Duet. And if your work is code, start with Claude Code. Here's why it's my favorite. 

<!-- Sources: the five slides before this one. -->

## 9. Of every coding agent I've tried, rivals' included, Claude Code is my favorite

My opinion, from experience, not a measurement: of every coding agent I've tried, rivals' included, Claude Code is my favorite. Two reasons. It does real work: those three changes to Richard Lange's lab code were each measured before and after, and checked by a second AI agent. And it follows my rules. Hooks, the rules it can't skip, can run at 33 different moments in a session. The rivals I checked document between 6 and 21. My own rules plugin uses six, to check every commit, helper agent and email draft before it happens. Let me show you the smallest one. 

<!-- Sources: nn-library #17, #18, torch-mlflow-template #3; each tool's hooks page; phylax hooks.json. -->

## 10. A five-line hook blocks reads, edits and commands that name your secrets file

Your .env file holds passwords and keys. This hook, adapted from Anthropic's hooks guide, runs before Claude reads, searches or edits a file, or runs a command. If the target names .env, it blocks the call and says why. Anthropic's version watches only edits; I added reads, searches and shell commands, because in my test Opus changed a protected file through the shell. I asked Claude to add a line to .env. The hook stopped its first command, and Claude told me why instead of trying another way, with permission prompts off. Now, how to try these yourself. 

<!-- Sources: Claude Code hooks guide, "Block edits to protected files", and hooks reference; the runs' transcripts, November 2, on Opus 5.5 and Haiku 5.5. -->

## 11. Try Claude Code this week in four steps

So, try Claude Code this week, in four steps. Install it with one command. In your repository, run claude, then slash init, which writes down your build commands and conventions. Add one rule as a hook, like the .env one. Then give it one small task, and read the change before you commit. It needs a paid plan or an API account, and a PI can apply for Anthropic's discounted Team plan for scientists. The first steps for the other four apps, and where your code goes, are in the backup slides. Let me wrap up.

<!-- Sources: Claude Code overview and data-usage docs; Commercial Terms; pricing; Team plan for scientists; help center pages for Cowork, Science and Duet. -->

## 12. Each place your work lives has its own Claude app, and code starts in Claude Code

So here's where we landed. Each place your work lives has its own Claude app: a conversation, your computer, your code, your research and your accounts. For code, I start with Claude Code. It made {week.labPrs} real changes to Richard Lange's lab code, and its hooks can run at {hooks.claudeCode} moments, more than any rival I checked. Two things stay open. Duet can't see a lab's files, and it isn't on Team plans yet. And every one of these apps makes confident mistakes, so checking the work stays with you. That's my talk.

## 13. Thank you

Thank you. The slides and every source are at the link. I'm glad to take questions.
