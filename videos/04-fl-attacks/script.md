# Video Script: What Is an Attack on Federated Learning?

Production Mode: Mode A (Google Vids, AJ's personal avatar)
Long version: Landscape 16:9 (1920x1080), 2:30
Short: Vertical 9:16 (1080x1920), 50 seconds
Delivery Tone: Friendly explainer for students and people who code a little.
Look: one charcoal t-shirt and two sets (the desk, the whiteboard wall), the same in every segment.
Scope: general concepts from published papers only; nothing from unpublished lab results or papers in review.

Sources (cited here, never voiced):

- H. Brendan McMahan, Eider Moore, Daniel Ramage, Seth Hampson and Blaise Agüera y Arcas, [Communication-Efficient Learning of Deep Networks from Decentralized Data](https://arxiv.org/abs/1602.05629), AISTATS 2017. Segments 1 to 3, S1, S2: training data stays on the devices; a shared model is learned by aggregating locally computed updates; iterative model averaging (FedAvg); photos and text entry as examples.
- Leslie Lamport, Robert Shostak and Marshall Pease, [The Byzantine Generals Problem](https://doi.org/10.1145/357172.357176), ACM TOPLAS 4(3), 1982. Segment 5: where the name comes from.
- Peva Blanchard, El Mahdi El Mhamdi, Rachid Guerraoui and Julien Stainer, [Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent](https://proceedings.neurips.cc/paper/2017/hash/f4b9ec30ad9f68f89b29639786cb62ef-Abstract.html), NeurIPS 2017 (on arXiv as [Byzantine-Tolerant Machine Learning, 1703.02757](https://arxiv.org/abs/1703.02757)). Segments 6, 11 to 14, S2, S4, S5: no linear combination of updates, averaging included, tolerates a single Byzantine worker, which can make it select any vector; Krum scores each update by its squared distances to its n − f − 2 closest neighbors and picks the lowest; the guarantee needs 2f + 2 < n; Krum can slow learning when no one attacks.
- Liping Li, Wei Xu, Tianyi Chen, Georgios B. Giannakis and Qing Ling, [RSA: Byzantine-Robust Stochastic Aggregation Methods for Distributed Learning from Heterogeneous Datasets](https://arxiv.org/abs/1811.03761), AAAI 2019. Segments 7, 9, 10, S3: the sign-flipping attack sends the true value times a negative constant (σ = −4 in its tests); the Gaussian attack sends elements drawn from N(0, g²) with g = 10,000; plain averaging (SGD) fails under both.

## Long version (16:9, 1920x1080)

### Segment 1 (0:00 – 0:10): The Hook

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk, holding up a phone with the screen facing away from the camera. At 0:05, sets it down and leans in.
* **Visual Overlay:** Small photo and chat-bubble icons float up from the phone, then stop and stay inside it behind a padlock. A caption: 'your data stays on your phone'.
* **Spoken Script:**
  "What if your phone could help train an AI model without ever sending your photos or texts anywhere? That's federated learning."
* **Vocal Direction:** Curious and inviting. Land 'federated learning' clearly, as the name of the idea.

---

### Segment 2 (0:10 – 0:20): Train at Home, Send an Update

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:13, points to one phone icon. At 0:17, traces an arrow toward the server with one finger.
* **Visual Overlay:** On the whiteboard, five simple phone icons sit in a half circle around a server icon in the middle, each phone holding a small padlocked folder labeled 'your data'. One phone trains, and a small envelope labeled 'update' travels to the server; the padlocked folder stays put. Caption: 'Google, 2017'.
* **Spoken Script:**
  "In 2017, Google researchers laid it out. Each device learns from its own data and sends back only an update."
* **Vocal Direction:** Clear and steady. Stress 'only an update'.

---

### Segment 3 (0:20 – 0:30): FedAvg

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:22, sweeps a hand around the half circle. At 0:27, circles one finger: 'again'.
* **Visual Overlay:** On the whiteboard, five simple phone icons sit in a half circle around a server icon in the middle, each phone holding a small padlocked folder labeled 'your data'. Several phones send 'update' envelopes; the server blends them into one 'shared model' and sends it back out to all phones. A round counter ticks: 'round 1', 'round 2', 'round 3'. Label: 'FedAvg'.
* **Spoken Script:**
  "Each round, a server averages updates from a group of devices into one shared model. Repeat many rounds. That's FedAvg."
* **Vocal Direction:** Even and patient. Say 'Fed-Avg' as two parts.

---

### Segment 4 (0:30 – 0:40): The Catch

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 0:33, holds up one hand, palm out, like 'wait'. At 0:37, tilts the head.
* **Visual Overlay:** Two identical 'update' envelopes sit side by side, one marked 'honest?' and one marked 'bad?'. A question mark hovers between them.
* **Spoken Script:**
  "Here's the catch: the server can't see anyone's data. So it can't easily tell an honest update from a bad one."
* **Vocal Direction:** Turn to tension. Slow down on 'can't easily tell'.

---

### Segment 5 (0:40 – 0:50): Byzantine Clients

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:44, points to the one red phone.
* **Visual Overlay:** On the whiteboard, five simple phone icons sit in a half circle around a server icon in the middle, each phone holding a small padlocked folder labeled 'your data'. One phone turns red and gets a small label: 'Byzantine client'. A tiny side note: 'after the Byzantine Generals Problem, 1982'.
* **Spoken Script:**
  "A client that lies on purpose is called Byzantine. The name comes from an old puzzle about generals who can't trust messages."
* **Vocal Direction:** Storytelling tone on 'an old puzzle about generals'.

---

### Segment 6 (0:50 – 1:00): One Liar Is Enough

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:52, raises one finger. At 0:56, drags one hand sideways across the board.
* **Visual Overlay:** On the whiteboard, five simple phone icons sit in a half circle around a server icon in the middle, each phone holding a small padlocked folder labeled 'your data'. The red phone's arrow pulls the server's average far off to one side, while the honest arrows point together. Caption: 'plain averaging: one bad client can steer the result'.
* **Spoken Script:**
  "One liar is enough. A 2017 paper showed that with plain averaging, one Byzantine client can drag the result anywhere."
* **Vocal Direction:** Dramatic but controlled. Stress 'one liar' and 'anywhere'.

---

### Segment 7 (1:00 – 1:10): Attack One: Sign Flipping

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:03, turns one hand palm-up, then flips it palm-down.
* **Visual Overlay:** A green arrow labeled 'honest update' appears. A red arrow flips to point the opposite way and grows four times longer. Label: 'sign flipping'.
* **Spoken Script:**
  "Attack one: sign flipping. The attacker works out the honest update, then sends the opposite, made bigger. It pushes the model backwards."
* **Vocal Direction:** Clear, slightly ominous on 'the opposite, made bigger'.

---

### Segment 8 (1:10 – 1:20): A Tug of War

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 1:13, mimes pulling a rope with both hands. At 1:17, leans back as if pulled.
* **Visual Overlay:** A cartoon rope stretches across the frame. Four small green figures pull one way, and one red figure pulls the other way, extra hard. The rope's center marker slides toward the red figure.
* **Spoken Script:**
  "Picture a tug of war. Most clients pull one way, and the attacker pulls the other way, extra hard."
* **Vocal Direction:** Light and visual, a small grin on 'extra hard'.

---

### Segment 9 (1:20 – 1:30): Attack Two: Gaussian Noise

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:24, wiggles the fingers of one hand to suggest noise.
* **Visual Overlay:** A bell curve draws itself on the whiteboard, very wide. Random red dots spray out from it in every direction. Label: 'Gaussian noise: random numbers, huge spread'.
* **Spoken Script:**
  "Attack two: Gaussian noise. The attacker sends random numbers from a bell curve with a huge spread, instead of a real update."
* **Vocal Direction:** Even and clear. Say 'Gaussian' as 'GOW-see-un'.

---

### Segment 10 (1:30 – 1:40): Averaging Fails

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 1:33, gives a small shake of the head. At 1:37, opens one palm.
* **Visual Overlay:** A card reads 'plain averaging' with a red cross over it. Below it, a small source line: 'tested in published work: Li et al., AAAI 2019'.
* **Spoken Script:**
  "Both attacks come from published tests. Plain averaging failed against both, which is why researchers build smarter ways to combine updates."
* **Vocal Direction:** Matter-of-fact; lift on 'smarter ways'.

---

### Segment 11 (1:40 – 1:50): The Krum Defense

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:43, points from one dot to its nearest neighbors.
* **Visual Overlay:** Dots for each update appear on the whiteboard: a tight green cluster and a few red dots far away. Thin lines join one green dot to its nearest neighbors. Label: 'Krum'.
* **Spoken Script:**
  "One defense is called Krum. For each update, it measures how close that update sits to its nearest neighbors."
* **Vocal Direction:** Clear and patient. Say 'Krum' crisply, rhyming with 'drum'.

---

### Segment 12 (1:50 – 2:00): Closest to the Crowd

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:53, taps the center of the green cluster. At 1:57, waves the far red dots away.
* **Visual Overlay:** The green dot in the middle of the cluster lights up and gets a check mark: 'picked'. The far red dots fade to grey: 'not picked'.
* **Spoken Script:**
  "Then it keeps the one update that sits closest to the crowd. Far-off updates, like flipped or noisy ones, get left out."
* **Vocal Direction:** Satisfied, like a puzzle solved.

---

### Segment 13 (2:00 – 2:10): Only Works for a Minority

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 2:04, holds one hand level, then lowers it below the halfway mark.
* **Visual Overlay:** A bar splits into green 'honest' and red 'attackers'. A marker sits a little below the halfway point, labeled 'Krum needs attackers below this line'.
* **Spoken Script:**
  "Krum's guarantee needs the attackers to stay a minority: under half of the clients, with a little room to spare."
* **Vocal Direction:** Careful and exact. Stress 'minority'.

---

### Segment 14 (2:10 – 2:20): The Trade-Off

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 2:13, tips one hand side to side like a balance.
* **Visual Overlay:** A balance scale tips: one side 'safer against attackers', the other side 'can learn more slowly with none'. Small source line: 'Blanchard et al., NeurIPS 2017'.
* **Spoken Script:**
  "Krum has a cost. Keeping one update throws away honest work, so with no attackers around, it can learn more slowly."
* **Vocal Direction:** Honest and balanced.

---

### Segment 15 (2:20 – 2:30): Outro

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk, leaning in with direct eye contact. At 2:25, raises both eyebrows, inviting an answer.
* **Visual Overlay:** Five green phone icons line up along the bottom with a badge: 'Comment below'.
* **Spoken Script:**
  "So federated learning keeps your data home, but the server has to trust the crowd. Would you join one? Tell me below."
* **Vocal Direction:** Warm and curious. End on eye contact.

---

## Short (9:16, 1080x1920)

### Segment S1 (0:00 – 0:10): The Hook

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk, holding up a phone with the screen facing away. At 0:06, narrows the eyes playfully.
* **Visual Overlay:** Photo and chat icons stay locked inside the phone. Then one of five phone icons turns red. Caption: 'what if one phone lies?'
* **Spoken Script:**
  "Federated learning trains one AI model across many phones, and your data never leaves yours. But what if one phone lies?"
* **Vocal Direction:** Fast, curious hook. Stress 'lies'.

---

### Segment S2 (0:10 – 0:20): One Liar Is Enough

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:16, drags one hand sideways.
* **Visual Overlay:** On the whiteboard, five simple phone icons sit in a half circle around a server icon in the middle, each phone holding a small padlocked folder labeled 'your data'. Envelopes labeled 'update' fly to the server. The red phone's arrow drags the average off to one side.
* **Spoken Script:**
  "Each phone sends an update. The server averages them. With plain averaging, a single liar can drag the model anywhere."
* **Vocal Direction:** Quick and dramatic on 'anywhere'.

---

### Segment S3 (0:20 – 0:30): Two Attacks

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:22, flips one hand over. At 0:27, wiggles the fingers to suggest noise.
* **Visual Overlay:** A green arrow flips into a long red arrow: 'sign flipping'. Then random red dots spray out of a wide bell curve: 'Gaussian noise'.
* **Spoken Script:**
  "One trick is sign flipping: send the opposite of the honest update, made bigger. Another is sending pure random noise."
* **Vocal Direction:** Brisk, one beat per attack.

---

### Segment S4 (0:30 – 0:40): Krum

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:33, taps the center of the green cluster. At 0:37, waves the far dots away.
* **Visual Overlay:** A tight green cluster and a few far red dots. The center green dot lights up: 'picked'. Label: 'Krum'.
* **Spoken Script:**
  "A defense called Krum keeps the update that sits closest to the crowd, so far-off ones get left out."
* **Vocal Direction:** Satisfied, like a puzzle solved. 'Krum' rhymes with 'drum'.

---

### Segment S5 (0:40 – 0:50): Your Turn

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk, leaning in with direct eye contact. At 0:45, warm, open smile.
* **Visual Overlay:** A badge slides in: 'Comment below'. A phone reappears in the avatar's hand, screen facing away, ready to loop.
* **Spoken Script:**
  "Its guarantee needs attackers to stay a minority. Would you trust strangers' phones to train your AI? Tell me below."
* **Vocal Direction:** Warm and curious. End on eye contact, so the loop hands off to 'Federated learning trains one AI model'.

---

## Audio Prompt (30 s seamless loop, both cuts)

Instrumental only, 30 seconds, seamless loop. 90 BPM, key of D minor. Curious, slightly suspenseful lo-fi: a soft plucked bass, a ticking hi-hat, warm pads and a light music-box motif. Calm enough for teaching, with a hint of mystery. Clean start and end for an infinite loop, no vocals. Mix at -22 dB under the voice.

---

## Transitions & SFX Schedule

Long version: a soft paper-swipe on each cut between the desk and the whiteboard (0.6 s, centered on the cut). A low 'whomp' as the average is dragged off (about 0:56). A quick flip sound as the arrow reverses (about 1:03). A rope creak under the tug of war (1:10 to 1:20). A soft static hiss under the noise spray (about 1:24). A light chime as Krum picks its update (about 1:53).

Short: a quick whoosh into each cut (0:10, 0:20, 0:30, 0:40), 0.5 s each, and the loop bed carries 0:50 back to 0:00.

---

## YouTube Studio Metadata

**Long version**

Title: What Is an Attack on Federated Learning?

Description:
Federated learning trains one AI model across many devices while the data stays home. So what happens when one device lies?

Each device trains on its own data and sends back only an update, and a server averages the updates (FedAvg). Plain averaging has a weak spot: a single bad client, called Byzantine, can drag the result anywhere. Two simple attacks show how: sign flipping and Gaussian noise. One defense, Krum, keeps the update closest to the crowd.

00:00 Your data stays home
00:10 How FedAvg works
00:30 The catch
00:40 Byzantine clients
01:00 Two attacks
01:40 The Krum defense
02:10 The trade-off
02:20 Your turn

Papers:
McMahan et al., AISTATS 2017: https://arxiv.org/abs/1602.05629
Blanchard et al., NeurIPS 2017: https://proceedings.neurips.cc/paper/2017/hash/f4b9ec30ad9f68f89b29639786cb62ef-Abstract.html
Li et al., AAAI 2019: https://arxiv.org/abs/1811.03761
Lamport, Shostak and Pease, 1982: https://doi.org/10.1145/357172.357176

An AI avatar of AJ narrates this video. It was made in Google Vids from AJ's own verified face and voice.

#FederatedLearning #MachineLearning #AISecurity #Privacy #ComputerScience #Programming

Pinned comment: Would you trust a crowd of strangers' devices to train your AI? Tell me why or why not.

Tags: federated learning, FedAvg, Byzantine, poisoning attack, sign flipping, Gaussian noise attack, Krum, robust aggregation, machine learning security, privacy, AI for beginners, distributed learning

**Short**

Title: What If One Phone Lies?

Description: Federated learning keeps your data on your phone, but plain averaging lets one bad client drag the model anywhere. Full video: (link the long version). An AI avatar of AJ narrates this video, made in Google Vids from his own verified face and voice. #Shorts #FederatedLearning #AISecurity

Upload: tick 'Altered or synthetic content: Yes' in YouTube Studio for both cuts.

---

## Assets

- AJ's personal avatar, selected in the Vids character selector, and a phone as a hand prop.
- Overlays, drawn as described: the padlocked phone, the half circle of phones around a server, the update envelopes and round counter, the red Byzantine phone, the dragged average, the flipped arrow, the tug of war, the wide bell curve, the crossed-out averaging card, the Krum cluster, the minority bar, the balance scale.
- The 30 s audio loop above, generated once and used under both cuts.
