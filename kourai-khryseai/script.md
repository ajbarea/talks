# Kourai Khryseai: the script

<!-- What I say on each talk slide, one section per slide in order; the slides' speaker notes are short prompts.
     {path} is a figure from the deck's data; {if path}...{/if} holds only when the flag does.
     make script-length counts it; `python3 scripts/script_length.py <talk> --print` fills in today's figures. -->

## 1. Kourai Khryseai

Hi, I'm AJ Barea, a PhD student at RIT. This is Kourai Khryseai, a team of ten AI agents that builds software with you rather than for you. The name means the Golden Maidens: in Greek myth, the gold attendants Hephaestus built for his workshop, each able to think, speak and work on its own.

## 2. I built a team of ten AI agents that writes software with you

Here's what I built: an open-source team of ten AI agents, each running as its own server. On the left is the project's own demo scene: Metis stops to ask me before a real choice. Between them they plan, write the code, test it, review the style and write the commit message, and each one shows its reasoning as it works. Here's why you should care. If you use a coding agent today, you find out what it decided only when it hands you the finished change. With this team you watch those choices being made, and the ones that matter come to you first. Let me show you what a lone agent hides.

## 3. A coding agent that works alone hands you its result, not its choices

Ask a coding agent to add user authentication and it goes away and comes back with a finished change. Along the way it made real decisions: sessions or tokens, what counts as tested, which style rules apply. You find out what it chose only at the end. And one model is being asked to do five jobs well at once: plan, code, test, review and document. So I asked what it would look like if the work were split up, and done in the open.

## 4. Ten specialists, each with one job, working with you in the open

So the work is split across ten agents, each with one job. Six do the development: Hephaestus runs the workshop, Metis plans, Techne writes the code, Dokimasia tests it, Kallos reviews the style, and Mneme writes the commit messages. Two are companions: Puck walks you through your first session, and Cupid coaches the romance side of the game, which I'll come back to. And two check quality: Aidos catches vague, corporate or passive writing, and Aletheia checks citations and facts. Here's how a request moves through them.

## 5. Hephaestus hands the whole conversation to each specialist in turn

Here's a full feature request. Metis writes the plan. Techne writes the code from that plan. Dokimasia writes and runs the tests. Kallos reviews the style, and if it finds something Techne can fix, the work goes back to Techne, by default up to five rounds; anything still left after that is reported rather than retried forever. Mneme writes the commit message. Underneath all of it, Hephaestus keeps one running record of the whole exchange and hands all of it to each specialist, so Kallos reads everything Techne wrote, and nobody works from a summary. Smaller requests take shorter routes: a bug fix skips planning, and a cleanup is just style and the commit message.

## 6. You decide twice: before the work starts, and when a real choice comes up

You stay in the loop at two points. Before anything runs, Hephaestus reads the order back to you: here's the plan, shall I start? You confirm or redirect before any work is spent. Then, midway, any specialist can stop and ask when a choice is really yours. Here Metis asks whether a CSV export should stream large files, and gives the trade-off for each answer. And the whole time, every agent streams its reasoning as it works, so you watch the plan form instead of waiting for a result.

## 7. Three ways in, all talking to the same team of agents

There are three ways in, and they all reach the same agents. The terminal is the fast one: you type a request and watch each agent's work stream past. The desktop app shows each agent's portrait and gives each one a voice. And the visual novel turns the same work into a story game, where your rapport with each agent grows as you work together; that's where Cupid comes in. Behind all three is one back end.

## 8. Each agent is its own server, so any one can be tested or swapped

Under the hood, each agent is its own small web server, and they talk over A2A, an open agent-to-agent protocol. That means any one agent can be run alone, tested on its own, or replaced with a different implementation. The models are swappable too: Claude, Google's models, or free local models through Ollama. And every request leaves a trace, so you can see exactly what each agent did and how long it took.

## 9. Split across ten agents, a coding job puts its choices in front of you

So here's the point once more. Split a coding job across ten agents, each with one job, and its choices come to you instead of hiding in a finished change. Each agent is its own server. You decide twice: before the work starts, and when a real choice comes up. And every specialist reads the whole conversation, never a summary. Two things are still open. Each agent's own voice is still being cast and tuned for the desktop app. And style problems still left after five rounds are reported, not fixed. That's my talk.

<!-- Sources: kourai-khryseai IMPL.md (voice casting in progress), the deck's slide 5 (five rounds, then reported). -->

## 10. Thank you

Thank you. The code and the documentation are public, and the link is here. I'm glad to take questions.
