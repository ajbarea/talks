# Channel refresh: review file (talks #44)

Every change planned for the public videos on @AJBarea, in one place, before anything is applied in YouTube Studio.

| Tier | Videos | What changes |
|---|---|---|
| 1. Tech and research | 20 | New description (hook, summary, chapters from the video's own captions, links one per line, hashtags), tags, a pinned question, an end screen; title only where it was unclear or wrong |
| 2. Live music | 113 | One template from each upload's own band, song, venue, city, date, tour and show playlist |
| 3. Gaming clips | 36 | Formatting only: the music credit once instead of four times |

Every description passes `make videos-check` (`tests/test_channel_refresh.py` for Tiers 2 and 3). Content comes only from the video's captions, its current description and its linked public repository. Each Tier 1 row lists the source of every number.

<details><summary>Rules and their sources</summary>

- Description layout, chapters, hashtags and tags: [upload-package.md](../youtube-director/references/upload-package.md), with YouTube Help [9884579](https://support.google.com/youtube/answer/9884579) (chapters), [6390658](https://support.google.com/youtube/answer/6390658) (hashtags) and [146402](https://support.google.com/youtube/answer/146402) (tags "play a minimal role").
- Editing old metadata keeps the URL, views and comments, and does not reset a video; edits should match what the video actually covers ([TubeBuddy](https://www.tubebuddy.com/blog/get-more-views-old-youtube-videos/), [ytshark](https://ytshark.com/optimize-old-youtube-videos/); vendor guidance, no official statement found). Frequent title churn is a risk ([Radaar](https://www.radaar.io/resources-121/blog-388/ever-wondered-how-to-change-your-thumbnail-and-title-after-publishing-on-youtube-8459)), so titles change only to fix an error.
- End screens: Subscribe plus one related video, on videos of 25 s or more ([YouTube Help 6388789](https://support.google.com/youtube/answer/6388789)); two or three elements beat four ([NexLev](https://www.nexlev.io/youtube-end-screen-tips); vendor). Vertical Shorts get none.
- Pinned comments: one narrow question, one to three lines ([TubeMilestone](https://tubemilestone.com/blog/youtube-pinned-comments), [AIR Media-Tech](https://air.io/en/youtube-hacks/what-to-write-in-your-youtube-pinned-comment-to-get-a-reaction-from-your-audience); vendor).
- Concert uploads: YouTube's automatic music credits do not cover live recordings, so the band credit is typed in the description ([Rightstech, YouTube spokesperson](https://rightstech.com/2018/05/no-artist-writer-credits-for-cover-or-live-videos-youtube-spokesperson-confirms/)). No claims about rights.
- AI disclosure: the Altered or synthetic content setting plus a narrator line, only where an AI avatar narrates ([YouTube Help 14328491](https://support.google.com/youtube/answer/14328491)).

</details>

<details><summary>Not in this pass</summary>

- Custom thumbnails for Tier 1 uploads that still show an auto frame: each needs a face frame and the video's own visual (upload-package.md), so they are a follow-up.
- The 2016 to 2017 gaming clips keep their titles, tags and casual notes.

</details>

## Tier 1: tech and research

### Webots Lab 1 - Basic Robot Programming (`MX-L8MLTDGI`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | webots, webots tutorial, e-puck, epuck, e puck robot, cyberbotics, python robot controller, mobile robots, CDA 4621, wheel encoder, robot kinematics, differential drive |
| Pinned comment | At 4:35 the e-puck spins in place for a zero-radius circle by giving its wheels opposite speeds. How would you handle radius zero in your controller: spin in place, or reject it as an error? |
| End screen | Subscribe + Dhs7CLsRlh8 "Webots Lab 2 - Kinematics" (next lab in the series) |
| Chapters from | captions 0:00 (task 1), 0:15 (over 2π), 0:30 (max 6.28, 30 inches), 1:01 and 1:17 (zero, negative), 1:32 line end "for lab one task two" (01:45), 2:21, 2:52 line end "try a negative velocity" (03:05), 3:46 line end "positive velocity of five" (03:58), 4:35 (radius zero); meta chapters were YouTube's automatic ones |
| Facts | straight line of distance X at constant speed -> captions 0:00; four test cases -> 0:15; error past 2π, range -2π to 2π -> 0:15, 0:30; 6.28 for 30 inches -> 0:30; expected vs actual time and distance -> 0:46; zero speed no move -> 1:01; negative backward -> 1:17; encoders via position sensor -> 1:49; five test cases -> 1:49, 2:05; negative counterclockwise -> 3:11; positive clockwise -> 4:02; zero radius, +5/-5 wheels, one full turn -> 4:35, 5:06. Webots 2021 note -> current description (AJ); "repo now targets Webots R2025a" -> repo README badge and Tech Stack (commit 538c717 upgraded world files to R2025a). Caution: the 2022-08 world files in the repo carry an R2022a header, so "Webots 2021" rests on AJ's current description only. Course CDA 4621 -> current description. e-puck, Python -> current description. |
| Category | Gaming -> Education (matches Lab 6) |

Description: [tier1/MX-L8MLTDGI-description.txt](tier1/MX-L8MLTDGI-description.txt)

<details><summary>Current description</summary>

```text
Control of Mobile Robotics
CDA4621 Lab 1 - Basic Robot Programming

Simulator:
http://www.cyberbotics.com/#download

Robot:
http://www.cyberbotics.com/doc/guide/epuck

Controller Language:
Python

Source Code:
https://github.com/ajbarea/control-of-mobile-robots

⚠️ Note (2025 Update):
This project was developed using Webots 2021. Due to major updates in newer Webots versions, the simulation code may no longer run as-is.
I plan to refactor and update this project for Webots 2025 in the future. In the meantime, you can try installing an older version of Webots (2021.x) from the Cyberbotics archive to replicate the original results.
```

</details>

<details><summary>New description</summary>

```text
What happens when you tell a robot to drive faster than its motors allow, or in a circle of radius zero?

Lab 1 programs an e-puck to drive a straight line of a set distance at a constant speed. I run four test cases: a speed past the motor limit of 2π (the controller prints an error), full speed of 6.28 for 30 inches, zero speed, and a negative speed that drives it backward. Each run prints the expected time and distance next to the actual ones.

Task 2 reads the wheel encoders (position sensors in Webots) to drive full circles. Five more test cases: over the speed limit, zero speed, a negative speed that circles counterclockwise, a positive speed that circles clockwise, and a zero radius, where opposite speeds on the two wheels spin the robot in place for one full turn.

Lab 1 of 6 in my Webots series, made for CDA 4621 Control of Mobile Robots. Python controllers on the e-puck robot.
Note: these labs were built in Webots 2021, and newer Webots versions changed a lot. The source repo now targets Webots R2025a, so its code may not match the video; to replicate the video exactly, install Webots 2021 from the Cyberbotics archive.

00:00 Task 1: drive straight at a set speed
00:15 Speed over the 2π limit
00:30 Full speed for 30 inches
01:01 Zero and negative speed
01:45 Task 2: circles with the wheel encoders
02:21 Over-limit and zero-speed circles
03:05 Negative speed: counterclockwise
03:58 Positive speed: clockwise
04:35 Zero radius: spin in place

Simulator (Webots): https://cyberbotics.com/#download
Older Webots releases: https://github.com/cyberbotics/webots/releases
Robot (e-puck): https://cyberbotics.com/doc/guide/epuck
Source code: https://github.com/ajbarea/control-of-mobile-robots
Full Webots series: https://www.youtube.com/playlist?list=PLmQVFU1FBDddYV_4IRW1zfXH6CAKuZjIM
More videos: https://youtube.com/@AJBarea

#webots #robotics #epuck #python #mobilerobots
```

</details>

### Webots Lab 2 - Kinematics (`Dhs7CLsRlh8`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | webots, webots tutorial, e-puck, epuck, cyberbotics, differential drive robot, robot kinematics, kinamatics, python robot controller, mobile robots, CDA 4621, robot trajectory, oval path |
| Pinned comment | At 2:59 the controller rejects a 10-second deadline for the two circles before the robot moves. Do you check feasibility up front like this, or let the robot try and report the miss? |
| End screen | Subscribe + 2Kv8GSIrge4 "Webots Lab 3 - Navigation with Distance Sensors" (next lab in the series) |
| Chapters from | captions 0:08 (overview, first line), 0:40 line end / 0:56 "so for task one" (00:58), 2:12 (task 2), 2:59 (time warning), 3:16 (rerun), 4:13 (task 3), 4:46 (speed warning then oval); meta chapters were YouTube's automatic ones |
| Facts | three controllers, differential drive, Python, distances/widths/heights/speeds/radii -> captions 0:08; two warnings (time, max velocity) -> 0:24, 0:40; heading in degrees from yaw -> 0:40, 1:13; rectangle clockwise -> 0:56; distance and time printed -> 1:55; two clockwise circles -> 2:27; 10-second deadline rejected -> 2:59; radius 10 and 14 -> 3:54; oval from half circles and straight lines, clockwise -> 4:28; speed-limit warning -> 4:13, 4:46; distance, time, speed prints -> 5:24. Webots 2021 note -> current description (AJ); "repo now targets Webots R2025a" -> repo README badge and Tech Stack (commit 538c717 upgraded world files to R2025a). Caution: the 2022-08 world files in the repo carry an R2022a header, so "Webots 2021" rests on AJ's current description only. Course CDA 4621 -> current description. e-puck, Python -> current description. |
| Category | Gaming -> Education (matches Lab 6) |

Description: [tier1/Dhs7CLsRlh8-description.txt](tier1/Dhs7CLsRlh8-description.txt)

<details><summary>Current description</summary>

```text
Control of Mobile Robotics
CDA4621 Lab 2 - Kinematics

Simulator:
http://www.cyberbotics.com/#download

Robot:
http://www.cyberbotics.com/doc/guide/epuck

Controller Language:
Python

Source Code:
https://github.com/ajbarea/control-of-mobile-robots

⚠️ Note (2025 Update):
This project was developed using Webots 2021. Due to major updates in newer Webots versions, the simulation code may no longer run as-is.
I plan to refactor and update this project for Webots 2025 in the future. In the meantime, you can try installing an older version of Webots (2021.x) from the Cyberbotics archive to replicate the original results.
```

</details>

<details><summary>New description</summary>

```text
Can a robot drive a rectangle, two circles and an oval on wheel speeds and timing alone? Lab 2 tries all three.

Lab 2 writes three Python controllers for a differential drive robot, each tracing a shape from given distances, widths, heights, radii and speeds. Every controller warns when the path cannot be finished in the time given or when the speed passes the motor limit, and prints the heading in degrees from the robot's yaw as it drives.

Task 1 drives a rectangle clockwise. Task 2 drives two clockwise circles of radius 10 and 14, after first rejecting a 10-second deadline as impossible. Task 3 drives an oval race track built from two half circles and two straight lines, after a speed-limit warning. Each run ends with the distance, time and speed it calculated.

Lab 2 of 6 in my Webots series, made for CDA 4621 Control of Mobile Robots. Python controllers on the e-puck robot.
Note: these labs were built in Webots 2021, and newer Webots versions changed a lot. The source repo now targets Webots R2025a, so its code may not match the video; to replicate the video exactly, install Webots 2021 from the Cyberbotics archive.

00:00 Three shapes and two warnings
00:58 Task 1: rectangle, heading in degrees
02:12 Task 2: two clockwise circles
02:59 Warning: 10 seconds is too short
03:16 Circles of radius 10 and 14
04:13 Task 3: oval race track
04:46 Speed-limit warning, then the oval

Simulator (Webots): https://cyberbotics.com/#download
Older Webots releases: https://github.com/cyberbotics/webots/releases
Robot (e-puck): https://cyberbotics.com/doc/guide/epuck
Source code: https://github.com/ajbarea/control-of-mobile-robots
Full Webots series: https://www.youtube.com/playlist?list=PLmQVFU1FBDddYV_4IRW1zfXH6CAKuZjIM
More videos: https://youtube.com/@AJBarea

#webots #robotics #epuck #python #kinematics #differentialdrive
```

</details>

### Webots Lab 3 - Navigation with Distance Sensors (`2Kv8GSIrge4`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | webots, webots tutorial, e-puck, epuck, cyberbotics, distance sensor, proportional control, p controller, pid controller, wall following, corridor navigation, robot maze, python robot controller, CDA 4621 |
| Pinned comment | At 2:55 the robot zigzags around 10 inches from the wall but never settles exactly on it. Would you add an integral term here, or is close enough fine for wall following? |
| End screen | Subscribe + kwqOO57f73g "Webots Lab 4 - Navigation with Camera" (next lab in the series) |
| Chapters from | captions 0:10 (intro, first line), 0:43 (PID diagram), 1:49 "task 1 is a simple straight line drive" (01:50), 3:11 line end / 3:29 "task two" (03:27), 4:39 (task 3), 6:08 (facing the other way), 7:12 (task 4); the video has no chapters today |
| Facts | left, front, right sensors printed -> captions 0:10; proportional control, error = r - y, times Kp, saturation -> 0:43 to 1:32; cap 2π / 6.28 -> 1:32, 2:39; 10 inches -> 1:00, 1:49; gain 2.5 -> 2:39; never exactly 10, zigzags -> 2:55; 2.5 to 5.5 inches from side walls -> 3:45; left-wall priority, 90-degree spins -> 4:39, 4:57; both directions -> 5:13, 6:08; maze not solved, "watching me fail" -> 7:12, 7:28. Webots 2021 note -> current description (AJ); "repo now targets Webots R2025a" -> repo README badge and Tech Stack (commit 538c717 upgraded world files to R2025a). Caution: the 2022-08 world files in the repo carry an R2022a header, so "Webots 2021" rests on AJ's current description only. Course CDA 4621 -> current description. e-puck, Python -> current description. |
| Category | Gaming -> Education (matches Lab 6) |

Description: [tier1/2Kv8GSIrge4-description.txt](tier1/2Kv8GSIrge4-description.txt)

<details><summary>Current description</summary>

```text
Control of Mobile Robotics
CDA4621 Lab 3 - Navigation with Distance Sensors

Simulator:
http://www.cyberbotics.com/#download

Robot:
http://www.cyberbotics.com/doc/guide/epuck

Controller Language:
Python

Source Code:
https://github.com/ajbarea/control-of-mobile-robots

⚠️ Note (2025 Update):
This project was developed using Webots 2021. Due to major updates in newer Webots versions, the simulation code may no longer run as-is.
I plan to refactor and update this project for Webots 2025 in the future. In the meantime, you can try installing an older version of Webots (2021.x) from the Cyberbotics archive to replicate the original results.
```

</details>

<details><summary>New description</summary>

```text
Why does a proportional controller never stop exactly 10 inches from a wall? An e-puck shows it with three distance sensors.

Lab 3 drives the e-puck with its left, front and right distance sensors, printed live in the console. A proportional controller sets the motor speed: the distance error times a gain, then capped at the motor limit of 6.28. I explain that loop first, then use it in four tasks.

Task 1 slows to a stop 10 inches from the wall with a gain of 2.5; it zigzags close to 10 but never lands on it exactly. Task 2 drives down a hallway while staying 2.5 to 5.5 inches from both side walls. Task 3 follows a corridor with turns, favoring the left wall and spinning 90 degrees at each wall, run in both directions. Task 4 is a maze I had not solved yet, so you get to watch it fail.

Lab 3 of 6 in my Webots series, made for CDA 4621 Control of Mobile Robots. Python controllers on the e-puck robot.
Note: these labs were built in Webots 2021, and newer Webots versions changed a lot. The source repo now targets Webots R2025a, so its code may not match the video; to replicate the video exactly, install Webots 2021 from the Cyberbotics archive.

00:00 Four tasks, three distance sensors
00:43 How proportional control works
01:50 Task 1: stop 10 inches from the wall
03:27 Task 2: hold the middle of the hallway
04:39 Task 3: corridor with turns, clockwise
06:08 The same corridor, counterclockwise
07:12 Task 4: the maze, still unsolved

Simulator (Webots): https://cyberbotics.com/#download
Older Webots releases: https://github.com/cyberbotics/webots/releases
Robot (e-puck): https://cyberbotics.com/doc/guide/epuck
Source code: https://github.com/ajbarea/control-of-mobile-robots
Full Webots series: https://www.youtube.com/playlist?list=PLmQVFU1FBDddYV_4IRW1zfXH6CAKuZjIM
More videos: https://youtube.com/@AJBarea

#webots #robotics #epuck #python #pidcontrol #wallfollowing
```

</details>

### Webots Lab 4 - Navigation with Camera (`kwqOO57f73g`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | webots, webots tutorial, e-puck, epuck, cyberbotics, webots camera, color detection, object tracking, goal seeking, bug 0 algorithm, bug zero, bug algorithm, proportional control, python robot controller, CDA 4621 |
| Pinned comment | At 7:55 bug zero loops forever because it always wall-follows left. Have you tried bug one or bug two on a map like this, and which reached the goal more often? |
| End screen | Subscribe + xc2BawXN-ok "Webots Lab 5 - Localization" (next lab in the series) |
| Chapters from | captions 0:00 (camera), 1:04 "now for task one" (01:05), 3:41 line "test two" after "looks like it works" (03:44), 6:18 "there is a third task" (06:23), 6:34 line end "so the way this one works" (06:47), 7:37 line end "there's a fail case" (07:50), 8:44 line "an actual bug bug in my controller" (08:52); meta chapters were YouTube's automatic ones |
| Facts | first-person camera window, yellow recognition -> captions 0:17, 0:48; tall yellow cylinder goal -> 0:33, 0:48; 80 positions, centered at 40, spin left/right -> 1:21, 1:37; robot and goal moved -> 1:54, 3:20; 5 inches with P control, wiggles, reverses when too close, follows moved goal -> 3:41 to 5:42; bug zero partly done -> 6:18; motion to goal vs wall follow -> 6:49; infinite loop fail case, left vs right -> 7:37 to 8:28; bug one and two -> 8:44; corner bug in my controller -> 8:44 to 9:32. Webots 2021 note -> current description (AJ); "repo now targets Webots R2025a" -> repo README badge and Tech Stack (commit 538c717 upgraded world files to R2025a). Caution: the 2022-08 world files in the repo carry an R2022a header, so "Webots 2021" rests on AJ's current description only. Course CDA 4621 -> current description. e-puck, Python -> current description. |
| Category | Gaming -> Education (matches Lab 6) |

Description: [tier1/kwqOO57f73g-description.txt](tier1/kwqOO57f73g-description.txt)

<details><summary>Current description</summary>

```text
Control of Mobile Robotics
CDA4621 Lab4 - Navigation with Camera

Simulator:
http://www.cyberbotics.com/#download

Robot:
http://www.cyberbotics.com/doc/guide/epuck

Controller Language:
Python

Source Code:
https://github.com/ajbarea/control-of-mobile-robots

⚠️ Note (2025 Update):
This project was developed using Webots 2021. Due to major updates in newer Webots versions, the simulation code may no longer run as-is.
I plan to refactor and update this project for Webots 2025 in the future. In the meantime, you can try installing an older version of Webots (2021.x) from the Cyberbotics archive to replicate the original results.
```

</details>

<details><summary>New description</summary>

```text
Can an e-puck find a yellow cylinder with its camera, turn to face it and stop 5 inches away? Lab 4 adds the camera.

Lab 4 gives the robot a camera, shown in a first-person window, set to recognize yellow. The goal for every task is a tall yellow cylinder. Task 1 keeps the robot facing it: the camera reports where the goal sits across 80 positions on its x-axis, and the robot spins until the goal is centered at 40. I move the robot and the goal around the map to test it.

Task 2 drives toward the goal and holds 5 inches away with proportional control, backing up when pushed too close and following the cylinder when it moves. Task 3 is bug zero, partly done at recording: I explain how it switches between heading for the goal and wall following, show a case where it loops forever, and show the corner bug in my own controller.

Lab 4 of 6 in my Webots series, made for CDA 4621 Control of Mobile Robots. Python controllers on the e-puck robot.
Note: these labs were built in Webots 2021, and newer Webots versions changed a lot. The source repo now targets Webots R2025a, so its code may not match the video; to replicate the video exactly, install Webots 2021 from the Cyberbotics archive.

00:00 The camera and the yellow goal
01:05 Task 1: always face the goal
03:44 Task 2: stop 5 inches from the goal
06:23 Task 3: bug zero, partly done
06:47 How bug zero works
07:50 When bug zero loops forever
08:52 The wall-following bug in my controller

Simulator (Webots): https://cyberbotics.com/#download
Older Webots releases: https://github.com/cyberbotics/webots/releases
Robot (e-puck): https://cyberbotics.com/doc/guide/epuck
Source code: https://github.com/ajbarea/control-of-mobile-robots
Full Webots series: https://www.youtube.com/playlist?list=PLmQVFU1FBDddYV_4IRW1zfXH6CAKuZjIM
More videos: https://youtube.com/@AJBarea

#webots #robotics #epuck #python #computervision #bugalgorithm
```

</details>

### Webots Lab 5 - Localization (`xc2BawXN-ok`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | webots, webots tutorial, e-puck, epuck, cyberbotics, robot localization, trilateration, triangulation, trilateration robot, gps trilateration, grid localization, python robot controller, CDA 4621 |
| Pinned comment | At 8:08 the final build travels the grid but skips cells 2 and 3. Any guess what in a scan-then-move loop would make it drive past exactly those cells? |
| End screen | Subscribe + DuN2028KPBQ "Webots Lab 6 - Mapping & Path Planning" (next lab in the series) |
| Chapters from | captions 0:00, 0:31 line end "for task 1" (00:45), 1:37 (GPS), 2:57 line "here are the distance formulas" (03:03), 4:19 line "here are the details on the grid" (04:27), 5:06 line "demo my beta version" (05:18), 8:02 line "let's see what's going on with my task one" (08:08), 12:55 (task 2), 14:02 "here's a visual example" (14:05), 15:05 line "let's go to the bot" (15:12); AJ's description had none, meta chapters were automatic |
| Facts | localization definition -> captions 0:15; x visited, dot unvisited, pose x/y/cell/orientation -> 0:15, 0:31; 4x4 grid, origin at center -> 0:47; trilateration over triangulation, distances only -> 0:47, 1:04; GPS comparison -> 1:37; four colored corner pillars, known xy -> 3:12; distance sensor gives r -> 3:28; two equations two unknowns, divide-by-zero flag -> 3:44, 4:02, 4:19; x and y from -20 to 20 -> 4:35; early build every cell correct -> 5:23, 8:02; skips cells 2 and 3 -> 9:26, 10:55, 11:34, 12:38; Task 2 no pillars, known walls, three sensors + compass heading -> 12:55 to 13:44; stops when every cell visited -> 16:09, 16:46. Webots 2021 note -> current description (AJ); "repo now targets Webots R2025a" -> repo README badge and Tech Stack (commit 538c717 upgraded world files to R2025a). Caution: the 2022-08 world files in the repo carry an R2022a header, so "Webots 2021" rests on AJ's current description only. Course CDA 4621 -> current description. e-puck, Python -> current description. |
| Category | Gaming -> Education (matches Lab 6) |

Description: [tier1/xc2BawXN-ok-description.txt](tier1/xc2BawXN-ok-description.txt)

<details><summary>Current description</summary>

```text
Control of Mobile Robotics
CDA4621 Lab 5 - Localization

Simulator:
http://www.cyberbotics.com/#download

Robot:
http://www.cyberbotics.com/doc/guide/epuck

Controller Language:
Python

Source Code:
https://github.com/ajbarea/control-of-mobile-robots

⚠️ Note (2025 Update):
This project was developed using Webots 2021. Due to major updates in newer Webots versions, the simulation code may no longer run as-is.
I plan to refactor and update this project for Webots 2025 in the future. In the meantime, you can try installing an older version of Webots (2021.x) from the Cyberbotics archive to replicate the original results.
```

</details>

<details><summary>New description</summary>

```text
Three distances are enough to pin down a robot. Trilateration, the idea behind GPS, localizes an e-puck on a 4x4 grid.

Lab 5 is about localization: working out where the robot is on a map. The console prints the grid, with an x for each cell visited and a dot for each one not yet visited, and the robot pose: x, y, grid cell and heading.

Task 1 uses trilateration. Four colored pillars stand at known corners of the grid, and the robot measures its distance to three of them with a distance sensor. I explain the circles, then the algebra that turns three distances into two equations with two unknowns. An early build finds the right cell from every square. The final build travels the whole grid, though at recording it still skipped cells 2 and 3.

Task 2 drops the pillars. The wall layout is known in advance, so the three distance sensors and the compass heading are enough to rule out cells until only one fits. The robot stops once every cell is visited.

Lab 5 of 6 in my Webots series, made for CDA 4621 Control of Mobile Robots. Python controllers on the e-puck robot.
Note: these labs were built in Webots 2021, and newer Webots versions changed a lot. The source repo now targets Webots R2025a, so its code may not match the video; to replicate the video exactly, install Webots 2021 from the Cyberbotics archive.

00:00 Localization and the grid printout
00:45 Task 1: trilateration on a 4x4 grid
01:37 How trilateration works, GPS style
03:03 From three distances to x and y
04:27 The grid and the four pillars
05:18 Early build: every cell checked
08:08 Final Task 1: scanning the whole grid
12:55 Task 2: localizing from walls alone
14:05 Reading the wall patterns
15:12 Task 2 run

Simulator (Webots): https://cyberbotics.com/#download
Older Webots releases: https://github.com/cyberbotics/webots/releases
Robot (e-puck): https://cyberbotics.com/doc/guide/epuck
Source code: https://github.com/ajbarea/control-of-mobile-robots
Full Webots series: https://www.youtube.com/playlist?list=PLmQVFU1FBDddYV_4IRW1zfXH6CAKuZjIM
More videos: https://youtube.com/@AJBarea

#webots #robotics #epuck #python #localization #trilateration
```

</details>

### Webots Lab 6 - Mapping & Path Planning (`DuN2028KPBQ`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | webots, webots tutorial, e-puck, epuck, cyberbotics, robot mapping, path planning, wavefront planner, wave front algorithm, wavefront path planning, particle filter localization, monte carlo localization, maze mapping, python robot controller, CDA 4621 |
| Pinned comment | At 12:35 the route from cell 13 to cell 1 has two shortest paths of nine steps each, and my planner picks one at random. How would you break the tie: fewest turns, or something else? |
| End screen | Subscribe + MX-L8MLTDGI "Webots Lab 1 - Basic Robot Programming" (series loops back to Lab 1; the playlist is the alternative) |
| Chapters from | captions 0:00, 0:47 line end "for task 1 it's the mapping section" (00:58), 1:19 line end "explain the grid print" (01:28), 4:22 line "moving on for task two" (04:24), 5:08 line "a little bit on the wavefront algorithm first" (05:12), 7:31 line end "my task 2 algorithm" (07:42), 8:40 (first test), 11:16 line end "next test" (11:26), 12:35 (last test); meta chapters were YouTube's automatic ones |
| Facts | Monte Carlo particle filter localization, distance sensors -> captions 0:15; unknown map for mapping, known for planning -> 0:47; ? unvisited, V visited, 1/0 walls -> 1:51, 2:08; starts at cell 16 -> 2:24; stops when all visited, inner walls mapped -> 3:14, 4:22; wavefront: goal 2, walls 1, free 0, plus one, descend from start -> 5:41 to 7:31; four-point connectivity, 9x9 grid for the 4x4 maze -> 7:48, 8:23; tests 16 to 10 -> 8:40, 16 to 6 -> 11:32, 13 to 1 with two nine-step shortest paths -> 12:35, 12:50; random pick between equal paths -> 8:05. Webots 2021 note -> current description (AJ); "repo now targets Webots R2025a" -> repo README badge and Tech Stack (commit 538c717 upgraded world files to R2025a). Caution: the 2022-08 world files in the repo carry an R2022a header, so "Webots 2021" rests on AJ's current description only. Course CDA 4621 -> current description. e-puck, Python -> current description. |

Description: [tier1/DuN2028KPBQ-description.txt](tier1/DuN2028KPBQ-description.txt)

<details><summary>Current description</summary>

```text
Control of Mobile Robotics
CDA4621 Lab 6 - Mapping & Path Planning

Simulator:
http://www.cyberbotics.com/#download

Robot:
http://www.cyberbotics.com/doc/guide/epuck

Controller Language:
Python

Source Code:
https://github.com/ajbarea/control-of-mobile-robots

⚠️ Note (2025 Update):
This project was developed using Webots 2021. Due to major updates in newer Webots versions, the simulation code may no longer run as-is.
I plan to refactor and update this project for Webots 2025 in the future. In the meantime, you can try installing an older version of Webots (2021.x) from the Cyberbotics archive to replicate the original results.
```

</details>

<details><summary>New description</summary>

```text
How does a robot find the shortest path through a maze? First the e-puck maps every wall, then a wavefront planner plans the route.

Lab 6 has two halves. In Task 1 the maze is unknown: the robot uses its distance sensors and Monte Carlo particle filter localization to work out which cell it is in, then marks that cell visited and records the walls around it. The printout shows a question mark for each unvisited cell, a V once visited, and a 1 or 0 for each wall. It stops when every cell is visited and the inner walls are mapped.

In Task 2 the maze is known. I explain the wavefront planner: the goal gets a 2, walls a 1, and each free neighbor gets its cell's value plus one until the grid is filled; the path then steps down from the start. My version uses four-point connectivity on a 9x9 grid that stands for the 4x4 maze. I run three cases: cell 16 to 10, cell 16 to 6, and cell 13 to 1, which has two shortest paths of nine steps.

Lab 6 of 6 in my Webots series, made for CDA 4621 Control of Mobile Robots. Python controllers on the e-puck robot.
Note: these labs were built in Webots 2021, and newer Webots versions changed a lot. The source repo now targets Webots R2025a, so its code may not match the video; to replicate the video exactly, install Webots 2021 from the Cyberbotics archive.

00:00 Mapping and path planning
00:58 Task 1: mapping the maze walls
01:28 Reading the wall map printout
04:24 Task 2: shortest path on a known maze
05:12 How the wavefront planner works
07:42 My version: four-point, 9x9 grid
08:40 Test 1: cell 16 to cell 10
11:26 Test 2: cell 16 to cell 6
12:35 Test 3: cell 13 to cell 1, two shortest paths

Simulator (Webots): https://cyberbotics.com/#download
Older Webots releases: https://github.com/cyberbotics/webots/releases
Robot (e-puck): https://cyberbotics.com/doc/guide/epuck
Source code: https://github.com/ajbarea/control-of-mobile-robots
Full Webots series: https://www.youtube.com/playlist?list=PLmQVFU1FBDddYV_4IRW1zfXH6CAKuZjIM
More videos: https://youtube.com/@AJBarea

#webots #robotics #epuck #python #pathplanning #wavefront
```

</details>

### PhiQuest Blockchain Demo - Problem Statement 1 (`s_4SQaAf_34`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | private blockchain, blockchain explorer, document verification, document signing, e-signature, DocBridge, DocBridge.io, dockbridge, docbridge blockchain, PhiQuest, senior design project, USF capstone, document hash, SHA-256, Node.js |
| Pinned comment | At 3:16 an edited copy of the signed PDF no longer matches its hash on the chain. What other tampering would you want a private blockchain like this to catch? |
| End screen | Subscribe + h5FIODBvD60 "PhiQuest Blockchain Demo - Problem Statement 2" (part 2 of the same project, same playlist) |
| Chapters from | caption word timings: 0:13 "here's the login page" (00:00, music before it), 0:31 "if we were to try" (00:31), 1:11 "this is the blockchain explorer" (01:11), 1:52 "here's a simple document" (01:52), 2:47 "a new transaction will" (02:47), 3:16 "here's the same file" (03:16); the video had no chapters before |
| Facts | admin dashboard login by email/password or Google account in the admin table -> captions 0:17; unlisted account gets "not an admin" error, then added via admin management page -> 0:33 to 0:49; explorer shows latest documents, IDs and blocks; search by document ID; upload a file to search by its hash -> 1:11 to 1:26; workflow via DocBridge extension, email signing, final verified copy -> 1:52 to 2:27; new transaction at end of workflow -> 2:47; edited file no longer found -> 3:20 to 3:35. User-story summary -> current description and repo README. Node.js, Express, Sequelize, Google OAuth -> repo README. Team names and roles, "USF Senior Project" -> current description. "Computer Engineering", 2022 -> repo README ("Computer Engineering Capstone Project (2022)"). "Part 1 of 2" -> the two Problem Statement videos and the Blockchain Explorer playlist. |

Description: [tier1/s_4SQaAf_34-description.txt](tier1/s_4SQaAf_34-description.txt)

<details><summary>Current description</summary>

```text
USF Senior Project - PhiQuest Team

Ethan Wuitschick - Team Lead
Allen Cheng - Programming Lead
AJ Barea - Blockchain Specialist

https://github.com/ajbarea/blockchain-explorer

(PS.1): Can a private blockchain system be implemented to certify transactions and documents signed via the DocBridge.io user interface?

1) As a user of DocBridge.io I want to be able to tie user signatures for a document to a private blockchain so that I may know that the signature is authentic.

2) As an administrator I want a blockchain explorer so that I can search for real-time and historical information related to the transactions that are stored in the private blockchain.

3) As an administrator, I want the blockchain to be a private blockchain that restricts who holds the ledger so that documents and signatures are kept private within the system and cannot be publicly viewed.
```

</details>

<details><summary>New description</summary>

```text
Can a private blockchain prove a signed document was never changed? We sign a PDF through DocBridge.io, then edit it and check.

Problem statement 1 of our USF senior project asked whether a private blockchain can certify documents signed through DocBridge.io. Its user stories ask for signatures tied to the chain, a blockchain explorer for admins, and a ledger only admins can see. The full user stories and acceptance criteria are in the repo.

The admin dashboard lets in only Google accounts stored in the admin table, so an unlisted account gets an error until an admin adds it. The blockchain explorer lists the latest documents and blocks, and finds a transaction by its document ID or by uploading the file, which it matches by hash. We start a signing workflow with the DocBridge extension, see the new transaction on the explorer, then show that an edited copy of the signed file is no longer found. The back end is Node.js with Express and Sequelize, with Google OAuth sign-in.

PhiQuest team: Ethan Wuitschick (team lead), Allen Cheng (programming lead), AJ Barea (blockchain specialist).
Our Computer Engineering senior project at USF, 2022. Part 1 of 2.

00:00 Admin login with Google
00:31 Only admin accounts get in
01:11 Blockchain explorer: search by ID or file
01:52 Signing a document with DocBridge
02:47 The new transaction on the chain
03:16 An edited file fails verification

Source code: https://github.com/ajbarea/blockchain-explorer
Part 2, the admin dashboard: https://youtu.be/h5FIODBvD60
Playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDdc3XyzoCp5NDFkoY5kzW3bT
More videos: https://youtube.com/@AJBarea

#blockchain #nodejs #capstone #USF #documentverification
```

</details>

### PhiQuest Blockchain Demo - Problem Statement 2 (`h5FIODBvD60`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | admin dashboard, administration interface, DocBridge, DocBridge.io, dockbridge, PhiQuest, user management, metrics dashboard, activity log, audit log, Google OAuth, token refresh, senior design project, USF capstone, Node.js |
| Pinned comment | At 1:15 the dashboard gets a button to refresh a user's expired Google OAuth token, because the extension would otherwise sit on an endless loading screen. How would you have handled token expiry instead? |
| End screen | Subscribe + s_4SQaAf_34 "PhiQuest Blockchain Demo - Problem Statement 1" (part 1 of the same project, same playlist) |
| Chapters from | caption word timings: 0:14 "here's the admin management page" (00:00, music before it), 0:39 "this is the metrics page" (00:39), 1:02 "the user page" (01:02), 1:35 "admins can also display" (01:35), 1:58 "this is the transaction view page" (01:58), 3:30 "as you can see all activity logs" (03:30); the meta chapters (Metrics Page 0:39, User Page 1:02, Transaction View Page 1:57) are not in the current description, so YouTube's automatic ones; they agree with the captions |
| Facts | admin management page: add, edit, delete admin accounts -> captions 0:14; metrics page: total users, total documents stored in the private blockchain, graph of documents stored and workflows started this and last month -> 0:30 to 0:46; user page edits non-admin accounts, API key refresh button, Google OAuth token expiry, infinite loading screen -> 1:02 to 1:17; groups and workflows edited -> 1:35; transaction view page logs successful and failed operations; demo of syncing, deleting, adding groups and sending a workflow -> 1:58 to 2:14; search by email or group name -> 3:30. User-story summary -> current description and repo README. Team names and roles, "USF Senior Project" -> current description. "Computer Engineering", 2022 -> repo README. "Part 2 of 2" -> the two Problem Statement videos. |

Description: [tier1/h5FIODBvD60-description.txt](tier1/h5FIODBvD60-description.txt)

<details><summary>Current description</summary>

```text
USF Senior Project - PhiQuest Team

Ethan Wuitschick - Team Lead
Allen Cheng - Programming Lead
AJ Barea - Blockchain Specialist

https://github.com/ajbarea/blockchain-explorer

(PS.2): Can an administration user interface be implemented so that operations personnel can visualize Docbridge.io metrics, perform user administration, and log selective events and transactions?


1) As an administrator I want a back-end administration interface for the DocBridge.io system so that I can edit information of users that are using DocBridge.io. 

2) As an administrator I want a back-end visualization interface for the DocBridge.io system so that I can visualize DocBridge metrics.

3) As an administrator I want a back-end administration interface for the DocBridge.io system so that I can view and edit information of all users of DocBridge.io.

4) As an administrator I want a back-end administration interface for the DocBridge.io system so that I can view information on previous operations.
```

</details>

<details><summary>New description</summary>

```text
Every workflow started and every group created or deleted lands in one searchable log. A tour of the DocBridge.io admin dashboard.

Problem statement 2 of our USF senior project asked whether an admin interface can let operations staff see DocBridge.io metrics, manage users and log selected events. Its user stories cover editing users, a metrics dashboard and a record of past operations. The full user stories and acceptance criteria are in the repo.

The admin management page adds, edits and deletes admin accounts. The metrics page shows the total users of the DocBridge extension, the total documents stored in the private blockchain, and a graph of documents stored and workflows started this month and last. The user page edits user accounts and their groups and workflows, and has a button that refreshes a user's expired Google OAuth token, which otherwise leaves the extension on an endless loading screen. The transaction view page logs successful and failed operations, and we sync, delete and add groups and send a workflow to show each log entry appear. A search by email or group name filters the log.

PhiQuest team: Ethan Wuitschick (team lead), Allen Cheng (programming lead), AJ Barea (blockchain specialist).
Our Computer Engineering senior project at USF, 2022. Part 2 of 2.

00:00 Admin management page
00:39 Metrics page
01:02 User page and token refresh
01:35 Groups and workflows
01:58 Transaction view page: the activity log
03:30 Searching logs by user or group

Source code: https://github.com/ajbarea/blockchain-explorer
Part 1, the private blockchain: https://youtu.be/s_4SQaAf_34
Playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDdc3XyzoCp5NDFkoY5kzW3bT
More videos: https://youtube.com/@AJBarea

#admindashboard #blockchain #nodejs #capstone #USF
```

</details>

### Expense Reimbursement System (`t2p_fUak_Mw`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | expense reimbursement system, ERS, reimbursement app, expense tracker, Java REST API, Javalin, javelin, PostgreSQL, Postgres, Postman, JDBC, role-based access control, java backend project |
| Pinned comment | At 4:19 the API refuses to resolve a ticket twice, and at 10:07 someone asks whether a manager can approve their own ticket. How would you block that case? |
| End screen | Subscribe + RiDxzmMX-qk "TBD Banking Application" (next project in the same Java, PostgreSQL and REST line, same period) |
| Chapters from | caption word timings: 0:15 "I'm going to start with a blank database" (00:00), 0:46 "log in with an invalid" (00:46), 1:42 "some of the stuff that a user is not allowed" (01:42), 2:19 "log out and I'll log in as myself" (02:19), 3:07 "show you that you can read the tickets" (03:07), 4:01 "try to resolve some of these" (04:01), 5:02 "this tab here" (05:02), 5:35 "I didn't show you that I can delete" (05:35), 6:18 start of the first question (06:18), 7:05 "why did you opt to use a put" (07:05), 7:46 "I heard you said you used cookies" (07:46), 10:07 "Andrew go ahead", manager approving own ticket (10:07); the video had no chapters before |
| Facts | Java, Javalin, PostgreSQL -> repo README (Javalin also captions 8:33, PostgreSQL also current description); Postman -> captions 8:48; tickets carry cost and description, manager approves or denies, status locked after processing -> current description, captions 4:19, 6:24; invalid name and password warnings -> 0:46; regular user cannot delete users or approve own ticket -> 1:42 to 2:12; manager updates user details -> 2:28 to 3:02; filter by status -> 3:52; filter by author -> 5:02; delete users with cascade -> 5:35 to 6:05; cookie identifies the user, role looked up for admin rights -> 9:04 to 9:37. User-story summary -> current description. "Solo project" -> current description. Left out: family member names and "seven tickets" from the captions (personal detail, not needed). |

Description: [tier1/t2p_fUak_Mw-description.txt](tier1/t2p_fUak_Mw-description.txt)

<details><summary>Current description</summary>

```text
AJ Barea - Solo Project - ERS

The Expense Reimbursement System allows an Employee to submit reimbursement requests to their employer to be refunded for various paid activities. Financial Managers can approve or deny pending reimbursement tickets. All users and their submitted requests are stored in a PostgreSQL database.

https://github.com/ajbarea/expense-reimbursement-system

(Problem Statement): Can an expense reimbursement system be implemented to allow for the submission, approval, and denial of employee expense reimbursements?


1) As an Employee I want an expense reimbursement system so that I can submit reimbursement requests and view pending request tickets.

Acceptance criteria:
a) Employees must be able to log into the ERS application using username and password input.
b) New users of ERS must not be allowed to register with a username that is already registered.
c) New users created in ERS should default to a non-administrative role.
d) Requests must include the financial cost and a description of the expense.
e) Employees must be able to view previously submitted reimbursement submissions.

2) As a Financial Manager I want an expense reimbursement system to process employee reimbursement requests.

Acceptance criteria:
a) Submitted tickets are initially 'Pending' and may be either 'Approved' or 'Denied'.
b) Reimbursement expense requests cannot change status after processing.
```

</details>

<details><summary>New description</summary>

```text
Can a manager change a ticket after approving it? A live demo of my Java expense reimbursement API, with roles and status locks.

The Expense Reimbursement System lets employees submit reimbursement tickets with a cost and a description. A financial manager approves or denies each one, and a ticket cannot change status after that. The user stories cover the employee side (login, unique usernames, submitting and viewing tickets) and the manager side (processing tickets once). The full text is in the repo.

I built it with Java, Javalin and PostgreSQL and drive it from Postman. The demo shows invalid logins, a regular user blocked from deleting users or approving their own ticket, a manager updating user details, reading tickets and filtering them by status and by author, and a manager deleting users whose tickets go with them through a cascade delete. The last part is the Q&A from the live presentation, including how the auth cookie tells the API which user is calling and what role they have.

Solo project.

00:00 Fresh database and test users
00:46 Login checks
01:42 What a regular user cannot do
02:19 Manager login and user updates
03:07 Reading and filtering tickets
04:01 Approving and denying tickets
05:02 Tickets by author
05:35 Manager deletes users, tickets cascade
06:18 Q&A: changing a resolved ticket
07:05 Q&A: why PUT for updates
07:46 Q&A: cookie authorization
10:07 Q&A: can a manager approve their own ticket?

Source code: https://github.com/ajbarea/expense-reimbursement-system
More videos: https://youtube.com/@AJBarea

#java #javalin #postgresql #restapi #postman #softwareengineering
```

</details>

### TDB Banking Application (`RiDxzmMX-qk`)
| Field | Value |
|---|---|
| Title | new: "TBD Banking Application" (typo fix: the repo is tbd-banking-application with README title "TBD Banking Application", the team is "TBD Team", and captions 0:00 say "TBD banking application") |
| AI-narrated | no |
| Tags | TBD bank, TBD banking app, TDB banking, banking application, bank app project, Spring Boot, Spring Security, Angular, Angular Material, JWT authentication, PostgreSQL, full stack java, Figma wireframe, entity relationship diagram, Trello scrum |
| Pinned comment | At 18:04 the transfer form grays out the account you are sending from, so you cannot send money to the same account. What other validation would you add to a transfer form? |
| End screen | Subscribe + w8TgRcd1uWQ "ThoughtCloud Social Media" (same teammates Seth Evry and Elian Felix, same Spring Boot and Angular stack, the next project) |
| Chapters from | caption word timings: 0:00 (intro, Trello and stand-ups), 1:00 "next we'll go over the team setup" (01:01), 2:06 "now I get to show off some of that useful planning documentation" (02:06), 2:50 "next I'll show you the website wireframe" (02:50), 3:27 "let's go over the back end ERD" (03:28), 4:46 "we can go to the next slide where we start talking about some of the technologies" (04:46), 6:00 "specifically for our branching" (05:59), 6:50 "if we go to the next slide" before "here we can see" 6:54 features (06:50), 7:45 line "like AJ mentioned already we had some issues" (07:45), 9:08 "show you a little bit about the project" (09:08), 12:58 "we didn't have too many defects" (12:58), 13:48 "okay oh starting off" first question (13:48); the meta chapters are not in the current description, so YouTube's automatic ones; their times agree within a few seconds |
| Facts | features list (register, login, profile and password, accounts, own-account transfers, send/request money, notifications, filter by income/expense) -> current description and repo README; agile process, Trello kanban, daily stand-ups -> captions 0:16 to 0:48; team restructure -> 1:04; flowchart -> 2:08; light and dark Figma wireframes -> 2:57 to 3:12; ERD, Spring Boot creating tables -> 3:27 to 4:16; Angular, Bootstrap, Angular Material -> 4:48 to 5:05; Java, Spring Boot, PostgreSQL, JWT -> 5:20 to 5:35, 7:28; Spring Security -> 7:45 to 8:16, 16:58, repo README; branching -> 5:51 to 6:39; live demo -> 9:05 to 12:40; backlog -> 12:58 to 13:32; Q&A -> 13:48. Team names -> current description. Three developers -> current description, captions 1:38. |

Description: [tier1/RiDxzmMX-qk-description.txt](tier1/RiDxzmMX-qk-description.txt)

<details><summary>Current description</summary>

```text
TBD Team:
Seth Evry
Elian Felix
AJ Barea

TBD Bank is a banking app that offers a range of features to help users manage their finances efficiently and securely. Users can create a user account and log in to access their profile, where they can view and update their information, including the option to change their password. In addition to creating and viewing bank accounts, users can also transfer money between their own accounts and request or send money to other users. They can also view their transaction history and filter it by income or expense. Additionally, users can stay informed about incoming money requests through their notifications and easily process them as needed.

https://github.com/ajbarea/tbd-banking-application
```

</details>

<details><summary>New description</summary>

```text
How does a team that loses and gains members mid-project still ship a banking app? Our planning docs, stack and a live demo.

TBD Bank is a full-stack banking app. Users register, log in, edit their profile and password, open accounts, transfer money between their own accounts, send or request money from other users, answer money requests from their notifications, and filter their transaction history by income or expense.

We walk through our agile process on a Trello kanban board with daily stand-ups, the team restructure, the flowchart, the light and dark Figma wireframes, the entity relationship diagram, our branching strategy and the challenges we hit. Then we demo the app live, list the backlog for a future sprint, and take questions. The front end is Angular with Bootstrap and Angular Material. The back end is Java with Spring Boot, Spring Security and JWT authentication, on PostgreSQL.

TBD team: Seth Evry, Elian Felix, AJ Barea.

00:00 Intro and agile process
01:01 Team structure and restructure
02:06 Planning: flowchart
02:50 Planning: Figma wireframes
03:28 Planning: entity relationship diagram
04:46 Tech stack
05:59 Branching strategy
06:50 Features implemented
07:45 Challenges
09:08 Live demo
12:58 Backlog for a future sprint
13:48 Q&A

Source code: https://github.com/ajbarea/tbd-banking-application
More videos: https://youtube.com/@AJBarea

#springboot #angular #java #postgresql #fullstack #bankingapp
```

</details>

### ThoughtCloud Social Media (`w8TgRcd1uWQ`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | ThoughtCloud, thought cloud, thoughtcloud social, social media app, full stack project, Angular, Angular Material, Spring Boot, Spring Security, AWS EC2, AWS RDS, S3 static website, Jenkins pipeline, Docker, test coverage |
| Pinned comment | At 4:41 we report hitting our 70% test coverage goal on both ends, and at 16:42 we say test-first slowed us when the models kept changing. Would you write tests first on a project like this? |
| End screen | Subscribe + RiDxzmMX-qk "TBD Banking Application" (same teammates Seth Evry and Elian Felix, same Spring Boot and Angular stack, the previous project) |
| Chapters from | caption word timings: 0:00 Julio's overview, 0:24 "now I'll hand it over to Seth" (00:24), 0:46 "and then for the software development life cycle" (00:46), 1:22 "next I'll hand it off to Elian" (01:22), 2:09 "right here we can see our Technologies used for the devops" (02:09), 3:03 "now I'll hand it over to Abraham" (03:03), 4:26 "I'll hand it over to AJ for code test coverage" (04:26), 5:09 "now we'll take you through a bit of a tour" (05:09), 7:49 "the browse button" (07:49), 9:51 "now we'll actually go ahead and show you another feature ... password recovery" (09:51), 10:44 line "great so that works ... bell icon" (10:44), 12:20 "as this was the biggest project" (12:20), 13:21 "we'll now open the floor for any questions" (13:21); the video had no chapters before |
| Facts | 70% coverage goal met front and back -> captions 4:41, 16:04; features (account, text and image posts, likes, comments, follows, browse, search, password reset email, notifications) -> current description and captions 5:13 to 12:04; capstone, presented live -> captions 0:01, 12:20; Scrum, Trello -> 0:46; branching -> 1:22; EC2 (back end, Jenkins), RDS (Postgres), S3 (front end), SES (password reset) -> 2:09 to 2:32; Jenkins pipelines, Docker, Linux -> 2:32 to 2:50, repo README; Angular, Angular Material, Bootstrap -> 3:05 to 3:22; Java, Spring Boot, Hibernate, Spring Security, JWT -> 3:37 to 4:08; JUnit, Mockito, Jasmine, Karma -> 4:57, repo README; pre-made code base -> 12:20. Seth Evry as team lead -> captions 0:24 (other roles not stated clearly enough to use). Team names -> current description. Left out: "115 front-end unit tests" (16:04, said with "I think"). |

Description: [tier1/w8TgRcd1uWQ-description.txt](tier1/w8TgRcd1uWQ-description.txt)

<details><summary>Current description</summary>

```text
ThoughtCloud Team:
Seth Evry
Elian Felix
Julio Canales
Abraham Barboza
AJ Barea

ThoughtCloud is a social media application that allows users to connect and share their thoughts and ideas with others. Users can create and customize an account, follow other users, make posts, like and unlike posts, and receive notifications when other users engage with their content. With ThoughtCloud, users can easily stay connected with their friends, family, and like-minded individuals, and discover new perspectives on the world around them. Whether you're looking to share your own thoughts and ideas, or simply want to stay informed about what's going on in the world, ThoughtCloud has you covered.

https://github.com/ajbarea/thought-cloud-social
```

</details>

<details><summary>New description</summary>

```text
We set a 70% test coverage goal for our full-stack social media app and hit it on both the front end and the back end.

ThoughtCloud is a social media app. Users create and customize an account, write text and image posts, like, comment and follow, browse posts from everyone, search for other users, reset a forgotten password by email, and get notifications when someone engages with their content.

This is our team capstone, presented live. We cover our Scrum process and branching strategy, the AWS deployment (EC2 for the back end and Jenkins, RDS for PostgreSQL, S3 for the front end, SES for password reset emails, with Jenkins pipelines and Docker), and the stack: Angular with Angular Material and Bootstrap, and Java with Spring Boot, Hibernate, Spring Security and JWT. Tests use JUnit and Mockito on the back end and Jasmine and Karma on the front end. Then a live demo, the challenges of working in a pre-made code base, and questions.

ThoughtCloud team: Seth Evry (team lead), Elian Felix, Julio Canales, Abraham Barboza, AJ Barea.

00:00 Overview
00:24 Team structure
00:46 Scrum process
01:22 Git flow and branching
02:09 DevOps on AWS
03:03 Front-end and back-end stack
04:26 Test coverage
05:09 Live demo: register, post, like
07:49 Browse, comments and follows
09:51 Password recovery
10:44 Notifications and deleting comments
12:20 Challenges
13:21 Q&A

Source code: https://github.com/ajbarea/thought-cloud-social
More videos: https://youtube.com/@AJBarea

#angular #springboot #aws #java #fullstack #socialmedia
```

</details>

### TaskMaster (`Lu6pgKajgLA`)
| Field | Value |
|---|---|
| Title | new: "TaskMaster: Full-Stack App with React, Flask and PostgreSQL" (the bare name does not say what the video is; the stack comes from the current description; 58 characters) |
| AI-narrated | no |
| Tags | TaskMaster, task master, React, Reactstrap, Flask, Flask-RESTful, Python REST API, PostgreSQL, Postgres, full stack web app, SWEN-610, RIT software engineering |
| Pinned comment | Flask-RESTful serves the API behind this React front end. Would you pick Flask-RESTful again for a project like this, or FastAPI? (no captions, so no moment is cited) |
| End screen | Subscribe + NwgSDL2SWTc "AI Dev Tool Showdown" (default; the other RIT SWEN coursework video on the channel) |
| Chapters from | none (the video has no captions, so no section breaks can be timed) |
| Facts | full-stack project for RIT SWEN-610 -> current description; React with Reactstrap, Python Flask-RESTful API, PostgreSQL -> current description. No public repo, so no repo link. Nothing else is claimed because the video has no speech to check against. |

Description: [tier1/Lu6pgKajgLA-description.txt](tier1/Lu6pgKajgLA-description.txt)

<details><summary>Current description</summary>

```text
AJ Barea - TaskMaster

Full-Stack Project for RIT SWEN-610

Tech Stack
Frontend: React (Reactstrap)
Backend: Python (Flask-RESTful API)
Database: PostgreSQL
```

</details>

<details><summary>New description</summary>

```text
A demo of TaskMaster, my full-stack project for RIT SWEN-610: React with Reactstrap, a Flask REST API, and PostgreSQL.

The front end is React with Reactstrap. The back end is a Python Flask-RESTful API, and the data lives in PostgreSQL.

More videos: https://youtube.com/@AJBarea

#react #flask #postgresql #python #fullstack
```

</details>

### AI Dev Tool Showdown: GitHub Copilot vs Amazon Q & Gemini CLI vs Claude Code (`NwgSDL2SWTc`)
| Field | Value |
|---|---|
| Title | unchanged (76 characters, but clear, and the channel's most-viewed video; no churn) |
| AI-narrated | no |
| Tags | AI coding assistant comparison, best AI coding tool, Copilot vs Amazon Q, Claude Code vs Gemini CLI, AI pair programmer, VS Code AI extension, Amazon Q Developer, Gemini CLI review, Claude Code review, github copliot, cluade code, Kiro IDE, model context protocol, pygame AI game, AI dev tools 2025 |
| Pinned comment | At 21:24 Copilot on GPT-4.1 scanned the right file and still missed my planted Bellman bug, then found it once I switched to Claude Sonnet 4. Have you seen the model matter more than the tool in your own work? |
| End screen | Subscribe + vYWXLaDjp2M "Kourai Khryseai: I Built a 10-Agent AI System That Thinks Out Loud" (the closest follow-on: my own multi-agent AI dev system, the next step after comparing AI coding agents) |
| Chapters from | kept AJ's 9 chapters; all checked against captions: 4:05 line "let's step back and look at the full AI dev tool ecosystem" (04:08), 9:57 line "let's meet our first contender. So, Amazon Q" (10:03), 21:57 line "Battle one ... is in the books ... recap" (22:04), 26:04 line "let's switch over to our terminal agents" (26:10), 32:17 line end "All in all, both CLI agents really impressed me" (32:30, the game results), 34:12 "And that wraps Battle 2" (34:12), 34:29 line "When it comes to tooling, I prefer GitHub Copilot" (34:38), 35:31 line end "let's compare the pricing" (35:40). No time is wrong. "Roadmap" in the last title is loose (that section is pricing, the hands-on activity and summary) but kept as AJ wrote it |
| Facts | graduate lecture -> captions 0:00, catcher README "graduate project"; four tools, same prompts -> 0:50; Python Q-learning project from a past AI course -> 13:26; README, pytest coverage, planted Bellman bug -> 16:09 to 17:16, 20:50; Copilot GPT-4.1 missed the bug, fixed after switch to Sonnet 4 -> 21:24, 24:43, 24:58; one prompt file, empty folder, doc plan, user guide, Pygame Catcher -> 29:37 to 30:58; Gemini followed the spec, simple graphics -> 32:34, 32:51; Claude multipliers, game over after three misses, keyboard bug -> 33:09 to 33:40; landscape: chatbots, ask/edit/agent modes, AI-first editors incl. Kiro, terminal agents, MCP -> 4:05 to 9:42; pros/cons, free tiers, student deals -> 35:00 to 36:19; hands-on AWS Lambda activity -> 36:19 to 37:41; SWEN-614 -> current description (slide and activity file names); "as of July 2025" -> 34:45. Chapter titles -> AJ's current description. Q's model is said inconsistently in captions (Sonnet 4 at 15:37, Sonnet 3.7 at 22:30 and 25:32), so the description does not name it. Links -> current description, files confirmed in ajbarea/catcher |

Description: [tier1/NwgSDL2SWTc-description.txt](tier1/NwgSDL2SWTc-description.txt)

<details><summary>Current description</summary>

```text
Ever wondered which AI coding assistant reigns supreme? In this video we put four of the hottest AI dev tools head‑to‑head:

• *IDE Showdown:* Amazon Q vs GitHub Copilot  
• *CLI Showdown:* Google Gemini CLI vs Anthropic’s Claude Code  
• *Coding challenges:* Easy, medium, & hard tasks  
• *Pricing & subscriptions:* Free tiers, student perks, and paid plans  
• *Final verdict & recommendations*

⏱️ *Timestamps*
0:00 Intro & Motivation 
4:08 Dev Tool Landscape
10:03 IDE Showdown: Q vs Copilot  
22:04 Battle One Winner?
26:10 CLI Showdown: Gemini vs Claude  
32:30 Video Games
34:12 Battle Two Winner?
34:38 Conclusions & "Who Wins?"
35:40 Pricing & Roadmap  

🔗 *Resources & Slides*
– GitHub: https://github.com/ajbarea/catcher
– Lecture Slides: https://github.com/ajbarea/catcher/blob/main/SWEN-614_AJ-Barea_AI-Dev-Tools_Slides.pdf
– Hands-On Activity: https://github.com/ajbarea/catcher/blob/main/SWEN-614_AJ-Barea_AWS_HandsOn_Activity.pdf

💬 *Join the conversation:*  
Which assistant impressed you the most? Drop a comment below!
```

</details>

<details><summary>New description</summary>

```text
Does the AI coding tool matter, or the model behind it? Copilot missed my planted bug on GPT-4.1, then fixed it on Claude Sonnet 4.

In this graduate lecture I put four AI coding tools through the same tasks. Battle one pits two VS Code extensions, Amazon Q and GitHub Copilot, against a Python Q-learning project from an earlier AI course: write a README, add pytest coverage, then find and fix a bug I planted in the Bellman update. Battle two gives two terminal agents, Gemini CLI and Claude Code, one prompt file and an empty folder, and asks each for a documentation plan, a user guide and a playable Pygame game called Catcher.

Gemini's game followed the spec exactly, with simple graphics. Claude Code's added score multipliers and a game over after three misses, but its keyboard input had a bug. Before the battles I map the AI dev tool landscape: chatbots, IDE extensions with ask, edit and agent modes, AI-first editors such as Kiro, terminal agents, and MCP. I close with pros and cons, free tiers and student deals, and a hands-on activity that builds an AWS Lambda function with an AI agent.

Made for SWEN-614. Tools and prices are as of July 2025.

00:00 Intro & Motivation
04:08 Dev Tool Landscape
10:03 IDE Showdown: Q vs Copilot
22:04 Battle One Winner?
26:10 CLI Showdown: Gemini vs Claude
32:30 Video Games
34:12 Battle Two Winner?
34:38 Conclusions & "Who Wins?"
35:40 Pricing & Roadmap

Source code and both Catcher games: https://github.com/ajbarea/catcher
Lecture slides: https://github.com/ajbarea/catcher/blob/main/SWEN-614_AJ-Barea_AI-Dev-Tools_Slides.pdf
Hands-on activity: https://github.com/ajbarea/catcher/blob/main/SWEN-614_AJ-Barea_AWS_HandsOn_Activity.pdf
AI, Research and Software Projects playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDddL1sPe9Qj-drkwZ3v-wuQo
More videos: https://youtube.com/@AJBarea

#AIcoding #GitHubCopilot #ClaudeCode #GeminiCLI #AmazonQ #devtools
```

</details>

### FL Framework – UI/UX Showcase (Visual Demo) (`dhk6-uB_gNc`)
| Field | Value |
|---|---|
| Title | new: "InteFL UI/UX Showcase (Visual Demo, No Audio)" ("FL Framework" is generic; names the framework InteFL and tells viewers up front there is no sound) |
| AI-narrated | no (no audio at all) |
| Tags | InteFL, federated learning UI, federated learning dashboard, FL simulation, federated learning demo, Flower framework, React 19, FastAPI, Byzantine robust aggregation, Multi-Krum, Bulyan, data poisoning, IID vs non-IID, Dirichlet partition, federated learnig |
| Pinned comment | Which view would you open first when a run looks wrong: per-client results with malicious clients highlighted, or the multi-simulation comparison overlay? (no m:ss: the video has no captions, so no moment could be verified) |
| End screen | Subscribe + UtOHEHz2pWw "FL Framework – Full Walkthrough: Educational UI & AI Analysis" (the narrated tour of the same interface) |
| Chapters from | none (no captions and no audio, so no section breaks can be verified) |
| Facts | every feature, the 30+ parameters, IID/Dirichlet/Pathological, GPU tracking, malicious-client highlighting, zoom and brush, Material Design 3 themes, the 7 strategies, the stack, "alpha footage", "student researchers and developers" -> current description (AJ; none checkable in captions, which do not exist). InteFL name, "our team's" -> repo README (title; citation lists Barea as an author). "later version" of the UI in the walkthrough -> upload dates (2025-10-14 vs 2026-02-14). "Visual demo, no audio" -> current description |

Description: [tier1/dhk6-uB_gNc-description.txt](tier1/dhk6-uB_gNc-description.txt)

<details><summary>Current description</summary>

```text
FL Framework – UX Showcase

A visual walkthrough of the FL Framework — a research-focused web interface for configuring, running, and analyzing federated learning simulations. It features built-in attack mitigation, dynamic dataset poisoning, and real-time visualization.

Built for student researchers and developers who want a powerful FL experimentation environment without sacrificing usability.

What you'll see:
→ Simulation Config: 30+ parameters including dataset partitioning (IID, Dirichlet, Pathological) & attack strategies.
→ Real-time Monitoring: Training progress with interactive charts & GPU tracking.
→ Result Analysis: Per-client metric visualization with malicious client highlighting.
→ Comparison Tools: Multi-simulation overlay with zoom & brush controls.
→ UI: Dark/Light theming (Material Design 3).

Supported Aggregation Strategies:
FedAvg · Trust/Reputation · PID · Multi-Krum · Bulyan · RFA · Trimmed-Mean

Tech Stack:
   · Frontend: React 19 + Vite, React Bootstrap, Recharts
   · Backend: FastAPI, Flower (FL), PyTorch, HuggingFace Transformers
   · ML: scikit-learn, PEFT/LoRA, pandas, numpy

🔇 Note: No audio — visual UX showcase alpha footage only.
```

</details>

<details><summary>New description</summary>

```text
A silent tour of the InteFL web interface: configure, run and compare federated learning simulations from the browser.

This is early alpha footage of the front end for InteFL, our team's federated learning research framework. It is built for student researchers and developers who want a full experimentation environment that stays easy to use. The video moves through the whole experiment loop: a configuration form with 30+ parameters, including dataset partitioning (IID, Dirichlet, Pathological) and attack strategies; live training progress with interactive charts and GPU tracking; per-client results with malicious clients highlighted; and a comparison view that overlays several simulations with zoom and brush controls. The interface has dark and light themes in Material Design 3.

Aggregation strategies: FedAvg, Trust/Reputation, PID, Multi-Krum, Bulyan, RFA and Trimmed-Mean.
Stack: React 19, Vite, React Bootstrap and Recharts on the front end; FastAPI, Flower, PyTorch and Hugging Face Transformers on the back end; scikit-learn, PEFT/LoRA, pandas and numpy for the ML.

No audio: this is a visual demo only. For a narrated tour of a later version, see the full walkthrough linked below.

InteFL repo: https://github.com/dmitrykoro/fl-execution-framework
Narrated full walkthrough: https://youtu.be/UtOHEHz2pWw
AI, Research and Software Projects playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDddL1sPe9Qj-drkwZ3v-wuQo
More videos: https://youtube.com/@AJBarea

#FederatedLearning #InteFL #MachineLearning #React #FastAPI #UXdesign
```

</details>

### IntelliFL: Full-Stack Federated Learning Framework | RIT MS SE Capstone (`2Q3Fv6Df3gU`)
| Field | Value |
|---|---|
| Title | new: "InteFL: Full-Stack Federated Learning Framework \| RIT MS SE Capstone" (IntelliFL -> InteFL, the framework's name; 68 characters) |
| AI-narrated | no |
| Tags | InteFL, RIT capstone, RIT graduate showcase, federated learning, federated learning framework, full stack ML app, React 19, FastAPI, pytest, data poisoning attacks, label flipping, Gaussian noise attack, MS software engineering capstone, federated learnig, Rochester Institute of Technology |
| Pinned comment | At 7:05 I mention my home GPU ran the same simulation faster than the RIT cluster. Have you hit that too, and was it the hardware, the queue or the container setup? |
| End screen | Subscribe + UtOHEHz2pWw "FL Framework – Full Walkthrough: Educational UI & AI Analysis" (a full narrated tour of the front end this talk describes) |
| Chapters from | captions: 0:05 first line, onboarding on what KP means (00:00), 0:21 line "the first thing I did was build a pytest" (00:23), 0:37 line "their next idea was dynamic poisoning" (00:48), 1:40 line end "What's cool about federated learning" (01:52), 2:45 line ">> oh yeah ... I have a desktop at home" (02:57), 3:49 line "Yeah. So actually all of these are mine" (03:56), 4:38 line "what was the overall set of goals for the front end" (04:43), 6:15 line "I actually have seven different presets" (06:18), 7:03 line "what's cool about ... the way I set it up with Docker" (07:05). Exact word times from the en-orig VTT. The recording is a poster Q&A, so each chapter starts at a new question or topic |
| Facts | RIT Graduate Showcase, Master's capstone, MS SE, advisor Dr. Leon Reznik -> current description (captions 0:37 "PhD team under Dr. Resnik"); test suite first, then dynamic attacks -> 0:21, 0:37; label flipping, Gaussian noise, per-round poisoning -> 0:53, 1:23, 1:40; papers for a dependability conference and on metacognition -> 4:55; front end on my own, tooltips instead of a notes file -> 3:18, 4:55, 5:11; data stays on clients, server gets gradients -> 1:56, 2:12; React front end, FastAPI, subprocess so crashes stop leaking resources -> 3:49, 4:04; seven presets -> 6:15; Recharts in place of static Matplotlib PDFs -> 6:31; integrated terminal -> 5:28; Docker -> 7:03; 45 seconds on my GPU, faster than the RIT cluster -> 7:03, 7:18. 1,136 tests, 95% coverage, under 90 s, 12 endpoints, 30+ validated fields, CLI-only to full stack, and the stack list -> current description only (AJ; not in captions or the repo README). InteFL name -> repo README |

Description: [tier1/2Q3Fv6Df3gU-description.txt](tier1/2Q3Fv6Df3gU-description.txt)

<details><summary>Current description</summary>

```text
Recording of my Master's Capstone presentation at the Rochester Institute of Technology (RIT) Graduate Showcase.

📄 Project Abstract 
I presented IntelliFL, a robust enhancement of a Federated Learning simulation framework. The project transformed a research-grade, CLI-only simulation engine into a production-ready, full-stack application with a GUI and comprehensive testing infrastructure.

🛠️ The Tech Stack
- Frontend: React 19, Vite, Recharts, Material Design 3 
- Backend: Python, FastAPI (Async I/O), WebSocket 
- ML Engine: Flower AI, PyTorch, Hugging Face Datasets 
- Testing: Pytest (1,100+ tests), Pytest-xdist 

🚀 Key Achievements
- Testing: Engineered a suite of 1,136 automated tests achieving 95% code coverage, ensuring reproducibility for research.
- Performance: Reduced total test runtime to under 90 seconds via parallel execution.
- Architecture: Decoupled the engine using a RESTful API with 12 endpoints to support programmatic access.
- UX: Built a configuration wizard with 30+ validated fields to help students avoid CLI errors.

🎓 Context
- Degree: MS in Software Engineering
- Advisor: Dr. Leon Reznik 
- Institution: Rochester Institute of Technology (RIT) 

#FederatedLearning #SoftwareEngineering #RIT #React19 #FastAPI #Python #Capstone #MachineLearning #TestDrivenDevelopment
```

</details>

<details><summary>New description</summary>

```text
How do you turn a CLI-only federated learning simulator into a full-stack app with a GUI, an API and 1,136 automated tests?

A recording of my Master's capstone at the Rochester Institute of Technology (RIT) Graduate Showcase, mostly a conversation at my poster. I worked with a PhD team under Dr. Leon Reznik on InteFL, their federated learning simulation framework. They asked first for a test suite, then for dynamic attacks that poison client data, by label flipping or Gaussian noise, only in the rounds you choose. Both fed the team's papers, one for a dependability conference and one on metacognition. On my own, I added a web front end, so new team members learn what each parameter does from tooltips instead of a notes file.

I explain how federated learning keeps data on each client and sends only gradients to the server, then walk through what I built: the React front end, a FastAPI layer, and a subprocess wrapper so a crashed simulation no longer leaves processes eating resources. The front end has seven quick presets, interactive Recharts plots in place of static Matplotlib PDFs, an integrated terminal, and it runs in Docker. On my own GPU the same simulation ran in 45 seconds, faster than on the RIT cluster.

In numbers: 1,136 automated tests at 95% code coverage, a full test run in under 90 seconds with parallel execution, a REST API with 12 endpoints, and a configuration wizard with 30+ validated fields.
Stack: React 19, Vite, Recharts, Material Design 3; Python, FastAPI, WebSocket; Flower, PyTorch, Hugging Face Datasets; Pytest, pytest-xdist.

MS in Software Engineering, Rochester Institute of Technology. Advisor: Dr. Leon Reznik.

00:00 Onboarding: what do the parameters mean?
00:23 The first ask: a test suite
00:48 Dynamic poisoning attacks
01:52 How federated learning works
02:57 GPU training and the live demo
03:56 What I built: UI, API and subprocesses
04:43 Why I built the front end
06:18 Presets and interactive plots
07:05 Docker and the cluster run

InteFL repo: https://github.com/dmitrykoro/fl-execution-framework
Narrated UI walkthrough: https://youtu.be/UtOHEHz2pWw
AI, Research and Software Projects playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDddL1sPe9Qj-drkwZ3v-wuQo
More videos: https://youtube.com/@AJBarea

#FederatedLearning #InteFL #SoftwareEngineering #RIT #Capstone #React #FastAPI #Python
```

</details>

### FL Framework – Full Walkthrough: Educational UI & AI Analysis (`UtOHEHz2pWw`)
| Field | Value |
|---|---|
| Title | new: "InteFL Full Walkthrough: Educational UI and AI Analysis" ("FL Framework" is generic; names the framework InteFL) |
| AI-narrated | no (no AI label on the live page; captions and description name no AI voice) |
| Tags | InteFL, federated learning UI, federated learning tutorial, federated learning dashboard, FL experiment platform, Flower framework, React 19, FastAPI, Redis, AI assistant, model poisoning, Recharts, Byzantine robust aggregation, ArKrum, federated learnig |
| Pinned comment | At 7:40 the second preset turns on model poisoning from round two. Which plot told you most clearly that something was wrong: the accuracy curve or the weight distribution comparison at 8:56? |
| End screen | Subscribe + 2Q3Fv6Df3gU "InteFL: Full-Stack Federated Learning Framework \| RIT MS SE Capstone" (the capstone talk on why this UI was built) |
| Chapters from | captions (word times from the en-orig VTT): 0:00 intro (00:00), "The entire platform" 0:15 (00:15), "At the top" 0:38 (00:38), "move to the new simulation" 1:06 (01:06), "Advanced users ... live validation" 2:01 (02:01), "Clicking create simulation" 3:01 (03:01), "explore the dashboard" 3:37 (03:37), "When a simulation transitions from" 4:24 (04:24), "Now that the first simulation is complete" 5:14 (05:14), "The plots tab" 5:32 (05:32), "Because this first experiment" 6:12 (06:12), "At this stage ... the integrated AI assistant" 6:41 (06:41), "Here is the full screen chat ... Now the second experiment" 7:40 (07:40), "The weight distribution comparison" 8:56 (08:56); meta chapters were YouTube's automatic ones |
| Facts | one command; installs deps, FastAPI, React 19, Redis, opens browser -> captions 0:15; RTX 3060 detected as training device -> 0:31; presets with estimated runtime and difficulty -> 1:05, 1:23; tooltips -> 1:38; live validation blocks bad config -> 1:54; JSON side panel syncs with the form -> 2:09; queue to avoid overloading hardware -> 3:01; insights tab, defense effectiveness, attack impact -> 5:14; interactive Recharts -> 5:32; metrics summaries, raw CSV -> 6:12; Argus AI assistant -> 6:41, 7:03; dynamic model poisoning from round two -> 7:40; Matplotlib before/after, weight distribution -> 8:18 to 8:56; terminal Ctrl + backtick -> 3:59. Strategy list and all library versions (Vite 7, React Router 7, Flower 1.26, PyTorch 2.10, Transformers 5.1, Datasets 4.5, numpy 2) -> current description only (AJ). InteFL name -> repo README |

Description: [tier1/UtOHEHz2pWw-description.txt](tier1/UtOHEHz2pWw-description.txt)

<details><summary>Current description</summary>

```text
FL Framework – In-Depth Walkthrough (Educational UI)

This video provides a deep dive into the FL Framework’s educational user experience—designed to make advanced distributed training approachable without sacrificing depth.

Watch how the platform goes from zero to fully operational with a single command, guiding users through the complete experimentation lifecycle.

What you'll see:
→ One-Command Launch: See the system spin up FastAPI, React 19, and Redis automatically.
→ Smart Configuration: Use research-backed presets or a two-way sync JSON editor with live validation.
→ Resource Awareness: Automatic hardware detection (GPU) and an experiment queue to prevent overload.
→ Interactive Analysis: "Argus" AI assistant for result interpretation & anomaly detection.
→ Advanced Visualization: Interactive Recharts for metrics and Matplotlib plotting data for weight distribution and poisoning analysis.
→ Dev Tools: Integrated terminal (Ctrl + `) for direct shell access.

Supported Aggregation Strategies:
FedAvg · Trust/Reputation · PID · Krum · ArKrum · Multi-Krum · Bulyan · RFA · Trimmed-Mean

Tech Stack:
   · Frontend: React 19 + Vite 7, React Bootstrap, Recharts, React Router 7
   · Backend: FastAPI, Flower 1.26, PyTorch 2.10, HF Transformers 5.1 + Datasets 4.5
   · ML: scikit-learn, PEFT/LoRA, pandas, numpy 2

🎙️ Narrated walkthrough — audio on.
```

</details>

<details><summary>New description</summary>

```text
Can a federated learning research framework be easy to learn without hiding what it does? A narrated tour of the educational UI for InteFL.

The whole platform starts with one command, which installs dependencies, starts the FastAPI back end, the React 19 front end and Redis, and opens the browser. The app detects my RTX 3060 and offers it as the training device. From there the video follows one experiment end to end: pick a research-backed preset with an estimated runtime and difficulty, read the tooltip on each hyperparameter, edit the JSON in a side panel that syncs with the form, and let live validation block a bad config before it wastes compute. Jobs wait in a queue so heavy runs do not overload limited hardware.

Then the results: an insights tab that explains defense effectiveness and attack impact, interactive Recharts plots, metric summaries with the raw CSV, and Argus, the built-in AI assistant. A second preset adds dynamic model poisoning from round two, and Matplotlib plots compare model behavior and weight distributions before and after the attack. An integrated terminal (Ctrl + backtick) gives direct shell access.

Aggregation strategies: FedAvg, Trust/Reputation, PID, Krum, ArKrum, Multi-Krum, Bulyan, RFA and Trimmed-Mean.
Stack: React 19, Vite 7, React Bootstrap, Recharts and React Router 7; FastAPI, Flower 1.26, PyTorch 2.10, Hugging Face Transformers 5.1 and Datasets 4.5; scikit-learn, PEFT/LoRA, pandas and numpy 2.

00:00 What the educational UI is for
00:15 One-command launch
00:38 Navigation and GPU detection
01:06 Research-backed presets
02:01 Live validation and the JSON editor
03:01 Creating a simulation and the queue
03:37 Dashboard and integrated terminal
04:24 Watching a run live
05:14 Results: the insights tab
05:32 Interactive plots
06:12 Attack and metrics tabs
06:41 Argus, the AI assistant
07:40 Second run: dynamic model poisoning
08:56 Weight distributions and wrap-up

InteFL repo: https://github.com/dmitrykoro/fl-execution-framework
Capstone talk on why I built the UI: https://youtu.be/2Q3Fv6Df3gU
AI, Research and Software Projects playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDddL1sPe9Qj-drkwZ3v-wuQo
More videos: https://youtube.com/@AJBarea

#FederatedLearning #InteFL #MachineLearning #React #FastAPI #AIassistant
```

</details>

### Kourai Khryseai: I Built a 10-Agent AI System That Thinks Out Loud (`vYWXLaDjp2M`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | Kourai Khryseai, multi-agent system, multiagent AI, agentic AI, AI coding agents, human-on-the-loop, A2A protocol, agent to agent protocol, model context protocol, Ren'Py, Pygame, LLM agents, CHAI poster, RIT PhD, kourai khrysiai |
| Pinned comment | At 2:46 I describe the virtue system: Hephaestus adds points when you collaborate, and Mneme notices when you document carefully. What would you want an AI teammate to track about how you work, and what would feel like too much? |
| End screen | Subscribe + NwgSDL2SWTc "AI Dev Tool Showdown" (the channel's other AI coding agent video, and its most viewed) |
| Chapters from | captions (word times from the en-orig VTT): 0:00 intro and name (00:00), "And so this came out to be multiple experiments" 0:35 (00:35), "And so it started off as a CLI experiment" 1:02 (01:02), "Some of the systems ... narrative interfaces" 1:25 (01:25), "But, basically, the user decides" 2:14 (02:14), "we have this virtue system" 2:46 (02:46), "And so, that's one game mechanic system" 3:30 (03:30), "for this we're going to focus on the human-centered AI aspect" 4:12 (04:12); meta chapters were YouTube's automatic ones |
| Facts | RIT CHAI Poster Session, PhD CIS, advisor Dr. Leon Reznik -> current description; golden automata of Hephaestus -> captions 0:00; plan, code, test, document -> 0:16; ten agents -> current title, current description, repo README; MCP and A2A -> 0:34; stream work, ask for guidance -> current description, repo README; CLI to group chat, gossip -> 1:06; three interfaces CLI, Pygame GUI with voices, Ren'Py visual novel -> 1:22 to 1:56, repo README; accepting suggestions, finishing tasks -> 2:26; Synergy, Sophia, Techne -> 2:44; Forge Virtues, Mass Effect and Disco Elysium -> current description; human-centered AI focus -> 4:04; LiteLLM, Starlette, OpenTelemetry, Jaeger, SQLite memory core -> current description |

Description: [tier1/vYWXLaDjp2M-description.txt](tier1/vYWXLaDjp2M-description.txt)

<details><summary>Current description</summary>

```text
Recording of my poster presentation at the Rochester Institute of Technology (RIT) Center for Human-Aware AI (CHAI) Poster Session.

📄 Project Abstract
I presented Kourai Khryseai, an interactive multi-agent development system that reimagines multi-agent development as a collaborative narrative experience. By translating psychological engagement models from game design, the system shifts from silent automation to a transparent, human-on-the-loop environment. Instead of running autonomously, agents stream their work in real-time and ask for guidance when critical decisions matter.

🛠️ The Tech Stack
- Core Engine: LiteLLM & Starlette
- Protocols: A2A Protocol and MCP
- Interfaces: Connects a 10-agent backend to a CLI REPL, Pygame GUI, and Ren'Py VN
- Observability: OpenTelemetry & Jaeger

🚀 Key Achievements & Features
- The Forge Agents: A 10-agent backend featuring core specialists, companion spirits, and quality validators like Aidos and Aletheia.
- Psychological Models: Implements "System Affinity" trust tiers and "Forge Virtues" inspired by Mass Effect and Disco Elysium.
- Memory Architecture: Uses an SQLite Memory Core for episodic and semantic memory.
- Host-Agnostic Delivery: Three equal-citizen hosts connect to the exact same backend.

🎓 Context
- Degree: PhD in Computing and Information Sciences
- Faculty Advisor: Dr. Leon Reznik
- Institution: Rochester Institute of Technology (RIT) 

#MultiAgentSystems #ArtificialIntelligence #SoftwareEngineering #RIT #HumanOnTheLoop #Python #LLM #DeveloperTools
```

</details>

<details><summary>New description</summary>

```text
What if AI coding agents worked like characters in a game, showing their work and asking you when a decision matters?

A recording of my poster at the Rochester Institute of Technology (RIT) Center for Human-Aware AI (CHAI) Poster Session. Kourai Khryseai is named for the golden automata Hephaestus built to help at his forge. It is a multi-agent development system: you pick the app, then plan, code, test and document it with ten AI agents. The agents follow MCP and the A2A (agent-to-agent) protocol and talk to each other and to you. Instead of running silently, they stream their work and ask for guidance.

It started as a CLI where Hephaestus gave orders to each agent in turn, and grew into a group chat where agents overhear and gossip. The same backend drives three interfaces: the CLI, a Pygame GUI with a voice for each agent, and a Ren'Py visual novel. As you work, the system tracks how you treat each agent, such as accepting suggestions and finishing tasks together, through relationship scores and Forge Virtues like Synergy, Sophia and Techne, inspired by Mass Effect and Disco Elysium. These player metrics are the human-centered AI focus of the poster.

Built with LiteLLM and Starlette, observed with OpenTelemetry and Jaeger, with an SQLite memory core for episodic and semantic memory.

PhD in Computing and Information Sciences, Rochester Institute of Technology. Faculty advisor: Dr. Leon Reznik.

00:00 What Kourai Khryseai is
00:35 One multi-agent backend: MCP and A2A
01:02 From CLI to group chat
01:25 Three interfaces: CLI, Pygame and Ren'Py
02:14 Tracking how you work with each agent
02:46 The virtue system
03:30 Relationship and play-through stats
04:12 The human-centered AI focus

Source code: https://github.com/ajbarea/kourai-khryseai
AI, Research and Software Projects playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDddL1sPe9Qj-drkwZ3v-wuQo
More videos: https://youtube.com/@AJBarea

#MultiAgentSystems #AgenticAI #HumanOnTheLoop #A2A #MCP #RIT #Python
```

</details>

### Kourai Khryseai (`m5_-WdJdzL4`)
| Field | Value |
|---|---|
| Title | new: "Kourai Khryseai: AI Agents as a Game" (the bare name says nothing to a new viewer) |
| AI-narrated | no: the captions are AJ's own poster speech, the same words as vYWXLaDjp2M (its 0:00 to 1:04 is the full talk's opening from the name onward, filler words included; the middle of the talk is cut). "AI slop-cut" names how it was cut, not the voice |
| Tags | Kourai Khryseai, kourai khrysiai, multi-agent system, agentic AI, AI agents game, AI coding agents, A2A protocol, model context protocol, Hephaestus AI, human-centered AI |
| Pinned comment | At 1:04 I say the agents went from taking orders in sequence to a group chat where they overhear and gossip. Would you want your coding agents talking behind your back? Full talk: https://youtu.be/vYWXLaDjp2M |
| End screen | Subscribe + vYWXLaDjp2M "Kourai Khryseai: I Built a 10-Agent AI System That Thinks Out Loud" (the full talk this is cut from; the upload is 16:9) |
| Chapters from | captions (word times from the en-orig VTT): 0:00 name (00:00), "I follow two protocols" 0:34 (00:34), "And so it started off as a CLI" 0:53 (00:53), "for this we're going to focus on the human-centered AI aspect" 1:29 (01:29); meta chapters were YouTube's automatic ones |
| Facts | "AI slop-cut edition" and full-video link -> current description; own voice -> captions match vYWXLaDjp2M; golden automata -> 0:00; plan, code, test, document -> 0:18; MCP and A2A -> 0:34; CLI to group chat, gossip -> 0:49 to 1:04; human-centered side, tracking how you work with each agent -> 1:21 to 1:39. No venue named, since this video's own sources do not give it |

Description: [tier1/m5_-WdJdzL4-description.txt](tier1/m5_-WdJdzL4-description.txt)

<details><summary>Current description</summary>

```text
AI slop-cut edition

Full video: https://youtu.be/vYWXLaDjp2M
```

</details>

<details><summary>New description</summary>

```text
Kourai Khryseai in under two minutes: a game where AI agents plan, code, test and document an app with you.

AI slop-cut edition: a short cut of my Kourai Khryseai poster talk, in my own voice. The project is named for the golden automata Hephaestus built to help at his forge. You choose an app to build and work on it with a team of AI agents that follow MCP and the A2A (agent-to-agent) protocol. It began as a CLI where Hephaestus gave orders in sequence, and became a group chat where agents overhear and gossip. The poster focuses on the human-centered side: systems that track how you work with each agent and show which ones you get along with.

00:00 What the name means
00:34 Agents on MCP and A2A
00:53 From CLI to group chat
01:29 The human-centered AI focus

Full poster talk: https://youtu.be/vYWXLaDjp2M
Source code: https://github.com/ajbarea/kourai-khryseai
More videos: https://youtube.com/@AJBarea

#AgenticAI #MultiAgentSystems #A2A #MCP #AI
```

</details>

### How We Test FL Plot Pipelines Without Running Federated Training (`iPsUL5e4a_E`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | no |
| Tags | InteFL, federated learning testing, visual regression testing, smoke tests, ML pipeline testing, GitHub Actions, CI artifacts, Flower framework, Krum, Multi-Krum, Bulyan, label flipping, Gaussian noise attack, mock simulation, federated learnig |
| Pinned comment | At 0:52 the mock replays recorded metrics but still runs the real aggregation and plotting code. How do you test ML plotting or reporting code without paying for full training runs? |
| End screen | Subscribe + UtOHEHz2pWw "FL Framework – Full Walkthrough: Educational UI & AI Analysis" (same framework, the UI that shows these plots) |
| Chapters from | kept AJ's titles, corrected 5 of 7 times: captions show his times run 30 to 40 s early (at his 1:00 he is still explaining the mock, at his 3:20 still explaining the smoke directory). Word times from the en-orig VTT: "here's how it works" 0:14 (kept 00:15), "you're probably wondering where you can find these artifacts" 1:33 (was 1:00), "And then you can unzip it" 2:09 (was 1:45), "The workflow fires on every PR" 2:41 (was 2:30), "looking towards the future, if you want to add new configs" 3:11 (was 2:50), "And that's it" 4:01 (was 3:20) |
| Facts | just merged visual smoke test pipeline -> captions 0:00; five configs, two no-attack baselines -> 0:16; Bulyan vs Gaussian noise, Krum vs 20% label flipping, Multi-Krum vs both at 50% each -> 0:16 to 0:32; mock replays recorded metrics, real aggregation, real plots/CSV/HTML -> 0:48 to 1:06; about 3 minutes -> 1:21; Actions tab, simulation outputs artifact -> 1:40; four PDFs (accuracy, loss, absolute distance, removal criterion), index.html dashboard, per-round and per-client CSVs -> 2:09 to 2:26; PRs to main, pushes to main, workflow_dispatch -> 2:41; drop a JSON, record_baselines, commit both, auto-discovery -> 3:23 to 3:41; "our team's ... framework" -> current description |

Description: [tier1/iPsUL5e4a_E-description.txt](tier1/iPsUL5e4a_E-description.txt)

<details><summary>Current description</summary>

```text
Walking through the visual smoke test pipeline I just merged into InteFL, our team's federated learning simulation framework. It catches regressions in plots, CSVs, and HTML dashboards on every PR without paying the cost of full FL training rounds.

- *What it tests:* 5 representative configs covering distinct pipeline paths
- *Baselines:* 2 no-attack runs for sanity checks
- *Attack scenarios:* Bulyan vs Gaussian noise, Krum vs 20% label flipping, multi-Krum vs concurrent Gaussian + label flipping at 50%
- *How it works:* Mock simulation pulls pre-recorded baseline metrics in place of real training, but executes the real strategy aggregation logic plus real plot, CSV, and HTML generation
- *Runtime:* ~3 minutes per CI run
- *Triggers:* PRs to main, pushes to main, and manual workflow_dispatch
- *Extensibility:* Drop a JSON into the smoke directory, run record_baselines locally, commit both files, done. Auto-discovery means no code changes.

⏱️ *Timestamps*
0:00 Intro
0:15 How the pipeline works
1:00 Where to find CI artifacts
1:45 What's inside simulation-outputs.zip
2:30 When the workflow runs
2:50 Adding new configs
3:20 Sign-off

🔗 *Resources*
– InteFL repo: https://github.com/dmitrykoro/fl-execution-framework

💬 *Join the conversation:*
How are you handling visual regression testing in your ML pipelines? Drop a comment below!
```

</details>

<details><summary>New description</summary>

```text
How do you catch broken plots in a federated learning framework on every PR without running any training? Replay recorded baselines.

I walk through the visual smoke test pipeline I just merged into InteFL, our team's federated learning simulation framework. Five representative JSON configs cover distinct paths through the pipeline: two baselines with no attack, Bulyan against Gaussian noise, Krum against 20% label flipping, and Multi-Krum facing Gaussian noise and label flipping together at 50% each. In CI, a mock simulation replays pre-recorded baseline metrics instead of training, but runs the real aggregation logic and the real plot, CSV and HTML generation. A run takes about 3 minutes.

Then I show where to download the simulation-outputs artifact from the Actions tab and what is inside: for each config, four PDFs (accuracy, loss, absolute distance, removal criterion), an index.html dashboard, and per-round and per-client CSVs. The workflow runs on PRs to main, pushes to main and manual workflow_dispatch. To add a config, drop a JSON into the smoke directory, run record_baselines, and commit both files. The test finds it with no code changes.

00:00 Intro
00:15 How the pipeline works
01:33 Where to find CI artifacts
02:09 What's inside simulation-outputs.zip
02:41 When the workflow runs
03:11 Adding new configs
04:01 Sign-off

InteFL repo: https://github.com/dmitrykoro/fl-execution-framework
AI, Research and Software Projects playlist: https://www.youtube.com/playlist?list=PLmQVFU1FBDddL1sPe9Qj-drkwZ3v-wuQo
More videos: https://youtube.com/@AJBarea

#FederatedLearning #InteFL #MLOps #CICD #GitHubActions #Testing
```

</details>

### I cloned myself using Google Vids 🤯 (`zc_W9tCGO1I`)
| Field | Value |
|---|---|
| Title | unchanged |
| AI-narrated | yes |
| Tags | Google Vids, Google Vids AI avatar, AI clone, AI avatar, digital twin, AI voice clone, made with Google Vids, google vid, AI video generator, Gemini Vids |
| Pinned comment | At 0:01 my avatar says it is a nice day at the beach, but I never filmed anything or said a word. Did you notice it was not really me before it told you? |
| End screen | none (36 s, 16:9: an end screen would cover over a third of it) |
| Chapters from | none (36 s vertical Short) |
| Facts | AI avatar speaking with my exact voice -> captions 0:01; generated from scratch in Google Vids, no webcam, no words spoken -> 0:18; beach scene -> 0:01; face matched, four different scenes, step-by-step digital twin guide offer -> current description (AJ; "four scenes" not in captions); "Made with Google Vids" credit and vids.new link -> current description |

Description: [tier1/zc_W9tCGO1I-description.txt](tier1/zc_W9tCGO1I-description.txt)

<details><summary>Current description</summary>

```text
I generated this entire video from scratch using Google Vids—without ever turning on a camera or saying a single word. The AI matched my voice and face perfectly while dropping me into four completely different scenes.

Want the full step-by-step tutorial on how to build your own 24/7 digital twin? Let me know in the comments!

Subscribe so you don't miss the full guide:
🔗 https://youtube.com/@AJBarea

Made with Google Vids https://vids.new/

Tags:
#Shorts #GoogleVids #AIAvatar #AIClone #ArtificialIntelligence #MadeWithGoogleVids
```

</details>

<details><summary>New description</summary>

```text
Can an AI avatar pass for me? I made this whole Short in Google Vids without turning on a camera or saying a word.

Google Vids generated the video from scratch: an AI avatar with my face and my voice, placed in four different scenes, starting at the beach. Want a step-by-step guide to building your own digital twin? Tell me in the comments.

An AI avatar of me narrates this video, with my voice.

Made with Google Vids: https://vids.new/
More videos: https://youtube.com/@AJBarea

#Shorts #GoogleVids #AIAvatar #AIClone #MadeWithGoogleVids
```

</details>

## Tier 2: live music, one template

113 concert uploads. Every field comes from the upload's current first line (`Band @ Venue in City [Date] (Tour)`) and title (`Band - Song`); the playlist is the show's own playlist on the channel. Table: [music.tsv](music.tsv). Rendered by `python3 videos/channel/refresh.py render DIR`.

Category: 24 of them sit in Education; bulk-set Music.

Three rendered samples:

`HPSG9s36jaE` was:

```text
Modest Mouse @ HISTORY in Toronto, Ontario, Canada [November 17, 2024] (Good News For People Who Love Bad News 20th Anniversary Tour)
```

now:

```text
Wooden Soldiers (ft GCVI Chamber Choir) by Modest Mouse, live at HISTORY in Toronto, Ontario, Canada, on November 17, 2024.

Tour: Good News For People Who Love Bad News 20th Anniversary Tour

Full show: https://www.youtube.com/playlist?list=PLmQVFU1FBDdewJrFGuTcgXDhPDChiT7NN
More videos: https://youtube.com/@AJBarea

#ModestMouse #LiveMusic #Toronto #Concert
```

`YdPIf9HF28A` was:

```text
Half Me (from Hamburg, Germany) @ Montage Music Hall in Rochester, New York [September 7, 2024]
```

now:

```text
Wraith by Half Me, live at Montage Music Hall in Rochester, New York, on September 7, 2024.

Half Me is from Hamburg, Germany.

More videos: https://youtube.com/@AJBarea

#HalfMe #LiveMusic #Rochester #Concert
```

`r-Ov6m_VXi8` was:

```text
Microwave @ The Great American Music Hall in San Francisco, California [May 23, 2024]

+ a tiny bit of But Not Often, at the end :)
```

now:

```text
Lighterless by Microwave, live at The Great American Music Hall in San Francisco, California, on May 23, 2024.

+ a tiny bit of But Not Often, at the end :)

Full show: https://www.youtube.com/playlist?list=PLmQVFU1FBDdccdLB_v8OqjhITzP1R8V0X
More videos: https://youtube.com/@AJBarea

#Microwave #LiveMusic #SanFrancisco #Concert
```

## Tier 3: gaming clips, formatting only

36 clips from 2016 and 2017. AJ's note stays word for word; the music credit repeated four times becomes one `Music: Song by Artist` line. Table: [gaming.tsv](gaming.tsv).

Sample:

`CbRwhNhAS0U` was:

```text
an homage to my favorite crucible gun in Destiny history. this is all year one footage when the original Last Word first came out.
[Paper Moon by Plini]
[Paper Moon by Plini]
[Paper Moon by Plini]
[Paper Moon by Plini]
```

now:

```text
an homage to my favorite crucible gun in Destiny history. this is all year one footage when the original Last Word first came out.

Music: Paper Moon by Plini
```

