---
date: 2026-11-05
url: https://www.linkedin.com/feed/update/urn:li:activity:7524095473792626688/
impressions_2026_11_05: 20
---

Our team drove a robot with one forearm, and our talk won Best Presentation at RIT's AWARE-AI Fall Hackathon. 🏆

In 24 hours, Kiransree Vijayakumar, Xinyi Liu and I built a controller for a simulated Clearpath Jackal robot using a Myo armband. Raise your arm and it stops. Hold it level and it goes. Roll your forearm to steer, and make a firm fist to brake. Anyone can calibrate and drive with one command.

The design came from what broke. Muscle-gesture classification read still poses correctly 99% of the time, but only 38% once the forearm rolled, which is exactly what you do while steering. So the motion sensor steers and the muscle signal only brakes.

We also tested a neural network against a simple linear model. With one short calibration per person, the simple model won for three of our four drivers.

Xinyi built a shared-control gate assist that spots gates in the raw lidar scan and plots a smooth, drivable arc through the one you're heading for, plus a live minimap of what the robot sees.

Thank you to Dr. Ferat Sahin, Dr. Cecilia O. Alm and Angelique Armstrong. In the spring my team won Best AI Model here; this time, Best Presentation.

Code, site and the full deck are in the first comment.

#AWAREAI #RIT

<!-- post details, not part of the post text -->
## Details

- Collaborators: Kiransree Vijayakumar, Xinyi Liu (invited). Tags: Ferat Sahin, Cecilia O. Alm, Angelique Armstrong.
- Images (1200x1200, padded, alt text on each): award certificate; deck slide 5 "Muscle gestures broke once the forearm rolled"; simulator L2 slalom.
- First comment: code https://github.com/ajbarea/myo-lever and site and deck https://ajbarea.github.io/myo-lever/.
- Posted Thursday about 8:10 AM ET.
- Cut during review: a teammate who only spectated; "51 recorded runs" (selection bias); "not significant, and the deck says so"; a defensive line about the gate assist; a generic closing question; a wrong-model Myo photo (Wikimedia, "ALPHA" dev kit).
