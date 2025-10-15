Product Requirements Document (PRD) for your Transcriptor Overlay System (TOS) — written from a product design + behavioral psychology standpoint, not just software architecture.

It’s optimized for minimal distraction, maximum behavioral reinforcement, and low resource usage, specifically for your OpenOffice-based transcription workflow.

⸻

🧩 Product Requirements Document (PRD)

Title: Transcriptor Overlay System (TOS)

Purpose:

Keep transcribers focused, efficient, and consistent while reinforcing the correct workflow — obtaining automatic transcriptions, performing word-by-word corrections, and uploading both the correction and the final PDF — without ever leaving their workspace.

⸻

🧠 1. Core UX Philosophy
	1.	Zero clutter, full presence:
The overlay should never intrude, block OpenOffice, or demand interaction. It exists as a transparent layer always visible, like a subtle dashboard.
	2.	Persistent feedback loop:
It continuously reflects state, progress, and small coaching prompts — not pop-ups, but ambient cues (color, icons, micro-animations).
	3.	Positive reinforcement only:
Encourage ideal behavior through success cues (color, tone, badges), never punishment or scolding.
	4.	Minimal cognitive load:
No text longer than one line on screen; all information encoded via icons, colors, or short phrases.
	5.	Always-on-top & cross-window:
Must remain visible across window switches and OpenOffice focus changes — effectively a floating HUD tied to the OS compositor.

⸻

🖥️ 2. Functional Overview

The Overlay (HUD) will:
	•	Display current audio progress using a visual workflow bar.
	•	Indicate clipboard state (empty / transcription / edited).
	•	Provide micro-feedback messages when key actions occur (Ctrl+6, Ctrl+7, Ctrl+9).
	•	Optionally display daily correction counter and gentle motivational prompts.
	•	Show a morning reminder message at first app open.

⸻

🎛️ 3. Visual Structure

🧱 3.1 Layout Zones (Fixed on Screen)

Recommended position: bottom-right corner, 240×120 px block, always-on-top.

┌────────────────────────────┐
│ 🎧  audio_1760.mp3          │   ← current file name (fades in/out)
│ 🔈🧠✅📄                      │   ← progress icons (grayed / colored when done)
│ 🟢 Clipboard: transcription  │   ← small colored label
│ ⭐ 7 / 10 corrections today  │   ← optional (tiny font, fades if <3s idle)
└────────────────────────────┘

	•	Transparent dark background (≈ 70 % opacity)
	•	Rounded corners, subtle drop shadow
	•	Color-coded status icons
	•	Font: light sans (e.g. Noto Sans, 12 pt)

⸻

🪄 4. Behavior Logic

🧩 4.1 Persistent Overlay Lifecycle
	•	Always visible once app is launched.
	•	Overlay auto-minimizes to a 40×40 px pill icon after 5 s inactivity but stays on screen.
	•	Re-expands automatically when a new event occurs (keyboard command or WS update).

⸻

🧠 4.2 Progress State Logic

Icons:
	•	🔈 Played
	•	🧠 Transcribed
	•	✅ Corrected
	•	📄 PDF Uploaded

Each icon fades from gray → colored upon completion.
Transitions animate gently (fade/scale-in).

Trigger events:

Command	Effect	Message
Ctrl 6	Activates 🧠	“✅ Copied transcription – remember Ctrl 7 after correcting”
Ctrl 7	Activates ✅	“⬆️ Correction uploaded – great job!”
Ctrl 9	Activates 📄	“📄 PDF uploaded – audio done!”

If Ctrl 9 is pressed before Ctrl 7 → show small amber warning bubble:
“⚠ Correction missing – won’t count toward progress.” (auto-fades in 3 s)

⸻

📋 4.3 Clipboard Indicator Logic

Three states, color coded:

State	Color	Label
Empty	⚪ White	“Clipboard empty”
Transcription-like (≥ 0.9 similarity)	🟢 Green	“Transcription ready”
Edited / misaligned	🟡 Amber	“Edited text (not aligned)”

Updates every ~0.5 s silently in background.

⸻

🕹️ 4.4 Daily Correction Counter

Small counter under clipboard line:
“⭐ 7 / 10 goal”
Appears only when a correction upload event occurs.
On reaching target: subtle success ding + short flash of green outline.

⸻

☀️ 4.5 Morning Reminder

Once per day, when the app first detects activity (first audio loaded):

🧭 “Remember: Copy → Correct → Ctrl 7 → Edit → Ctrl 9.
Word-by-word corrections make automatic transcriptions better!”

Displayed centered for 3 s, then slides down to its usual bottom-right dock.

⸻

🎉 4.6 Weekly Encouragement

On Mondays, overlay briefly shows:

“Last week you uploaded 27 perfect corrections! 💪”

If data unavailable, skip message.
Encouragement fades in 5 s, out 5 s.

⸻

⚙️ 5. Event Model (High-level)

Event	Source	Overlay Reaction
command: play_pause	WS message	Marks 🔈 as active
command: get_transcription	WS	Activates 🧠 + shows micro-tip
command: save_edited_transcription	WS	Could verify clipboard similarity, no visual if unneeded
command: upload_correction (after Ctrl 7)	WS	Activates ✅ + increment counter
command: upload_pdf (after Ctrl 9)	WS	Activates 📄 + checks if ✅ exists


⸻

🔒 6. UX Guardrails
	•	Never steal focus from OpenOffice or intercept keyboard input.
	•	No mouse interaction required. Entirely passive visual feedback.
	•	Animations ≤ 300 ms — smooth but subtle.
	•	Opacity < 80 % — avoid text overlap confusion.
	•	Font brightness adaptive: dynamic brightness based on window contrast (optional).

⸻

🪶 7. Resource & Performance Guidelines
	•	Single-process, single-thread overlay (Qt, PySide6, or lightweight Electron alternative).
	•	Avoid polling except clipboard (~0.5 s).
	•	WS events drive most updates.
	•	No GPU-intensive animations.
	•	Memory footprint < 80 MB; CPU < 1 %.
	•	Optionally, run as a detached overlay module that starts with the app (easier isolation).

⸻

🧩 8. Integration Strategy

Option A — Embedded Mode (Recommended)

Overlay launched within the same process as the existing desktop app:
	•	Directly subscribes to the same WS messages.
	•	Shares global state (current_file, command events).
	•	Simplifies deployment, ensures it appears only when app active.

Option B — Companion Process

Overlay runs as a lightweight separate process that:
	•	Connects to the same WS endpoint (read-only).
	•	Starts/stops automatically when the main app starts (via subprocess call).
	•	Pros: better isolation, no risk of slowing down transcription logic.
	•	Cons: slightly more complexity in setup.

Recommendation: Start with embedded; move to companion if stability or performance issues arise.

⸻

🧩 9. Optional Extensions (Future)
	•	🔊 Sound cues toggle (per user preference).
	•	🌙 Dark/light adaptive mode.
	•	🕓 Time-on-audio tracker (shows minutes worked).
	•	🏆 Weekly leaderboard (“Top 3 correctors”).

⸻

✅ 10. Success Metrics

Metric	Target	Measurement
% of audios with corrections uploaded	> 90 %	Compare Ctrl 7 vs Ctrl 9 counts
Average daily corrections per user	+25 % over baseline	Server logs
User error rate (PDF before correction)	< 5 %	Sequence pattern
Subjective distraction (user survey)	“Not distracting” (> 80 %)	Weekly feedback


⸻

🧭 11. Implementation Notes (non-specific)
	•	Language-agnostic structure: any GUI framework that can create a top-most frameless transparent window.
	•	Communicates via lightweight WebSocket JSON messages (same payload structure as your app).
	•	No persistent local database — in-memory counters reset daily.
	•	Morning and weekly messages fetched from local user stats JSON or server summary.

⸻

Summary

The Transcriptor Overlay should behave like a coach in the corner of your screen — silent, encouraging, and always present. It never distracts, only informs and motivates.
Visually small, psychologically powerful.

When done right, users will feel progress, avoid skipping correction uploads, and improve your automatic transcriptions — all without thinking about it.