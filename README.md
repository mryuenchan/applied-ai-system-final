# VibeMatch 2.0 — Self-Checking Music Recommender

**CodePath AI 110 — Project 4: Applied AI System (required features only)**

VibeMatch recommends songs based on a listener's preferred genre, mood, and target energy. It extends a working classroom recommender with a **reliability-aware, self-checking recommendation workflow** that can detect a misleading top-ranked result, retry with balanced weights once, and report when the catalog cannot fully satisfy the request. No API key or external model service is required.

> **Important distinction:** This is a transparent, rule-based recommendation and reliability system, not a trained neural model, LLM, or generative RAG chatbot. Its substantial new AI-system feature is the **integrated evaluation and guarded revision loop**. Recommendation scores are *not* calibrated probabilities of a listener enjoying a song.

## 1. Base project and original scope

**Original project:** CodePath AI 110 Module 3, *Music Recommender Simulation*.

The original Python application loaded **18 fictional songs** from `data/songs.csv`, scored each song using an input genre, mood, and target energy, and returned the top five songs with human-readable explanations. It included four example listening profiles, an evaluation discussion, and two pytest tests. It was a deterministic content-based recommender, not a production streaming service.

Original scoring rule (maximum four points): **+2 genre match, +1 mood match, +up to 1 energy similarity**, where similarity = `1 - abs(song_energy - target_energy)`.

## 2. New feature: reliability-aware recommendation workflow

Unlike the original version, `src/main.py` now calls `src/workflow.py` on **every request**. The workflow performs these stages:

1. **Validate** required preference fields, finite energy in `[0, 1]`, `top-k` range, and catalog completeness/duplicate IDs. Invalid requests return a clear error and nonzero exit code instead of an unhandled traceback.
2. **Retrieve and score** songs from the CSV using the **original** ranking algorithm in `src/recommender.py`.
3. **Self-check** the highest-ranked song. If it fails **both** the requested mood and an energy-distance tolerance of `0.30`, flag the ranking for revision.
4. **Revise at most once**, using weights of **+1 genre, +1 mood, +up to 2 energy similarity** on the *same actual catalog*. This is a bounded, deterministic evaluation/revision loop, not an invented song or a model call.
5. **Verify and disclose:** mark the final result `PASS` (top song meets genre, mood, energy tolerance), `PARTIAL` (top match is incomplete), or `REVIEW` (top song still conflicts with mood and energy). Display the change and a catalog-coverage warning if no available song meets all three preferences.

**Meaningful behavioral change:** With `classical / intense / 0.95`, the original algorithm ranked **Quiet Strings** first, even though it is peaceful with energy `0.25`. The new integrated self-check detects that mismatch and changes the first result to **Gym Hero** (intense, energy `0.93`). The system **does not claim Gym Hero is classical**: it explicitly reports that no song in this catalog satisfies all three requested conditions.

**Design trade-off:** A single retry with adjusted weights is simple and auditable, but cannot guarantee user satisfaction. Exact genre and mood matches remain crude, and a small catalog cannot produce missing styles. The `PARTIAL` and `REVIEW` statuses make this limitation visible rather than pretending every recommendation is a perfect match.

## 3. Architecture

The editable, required Mermaid source is [`diagrams/architecture.mmd`](diagrams/architecture.mmd). It shows the complete flow from CLI input through validation, CSV retrieval, original scorer, self-check decision, optional retry, result verification, user review, and automated testing. The diagram matches the Python functions rather than outlining future work.

| Component | Location | Role |
|---|---|---|
| CLI and demo profiles | `src/main.py` | Accept custom or example user preferences and print ranked recommendations |
| Original song retrieval/scoring | `src/recommender.py` | Load CSV and apply original genre/mood/energy scoring |
| Reliability and revision workflow | `src/workflow.py` | Validate, check, optionally re-rank, and disclose limitations |
| Music catalog | `data/songs.csv` | 18 fictional song records |
| Tests | `tests/test_recommender.py`, `tests/test_workflow.py` | Verify original scorer, integrated revision, guardrails, and CLI behavior |
| Human review | Printed explanations and status | User judges trade-offs; automated status is not a satisfaction metric |

## 4. Setup instructions (reproducible)

Requirements: Python 3.10+ and a terminal (including Windows PowerShell). Run these commands from the repository root.

```powershell
# Clone this new final-project repo, not the original starter repo
 git clone https://github.com/mryuenchan/applied-ai-system-final.git
 cd applied-ai-system-final

# Create the environment ONCE, then activate it
 python -m venv .venv
 .\.venv\Scripts\Activate.ps1

# Install project dependencies
 python -m pip install -r requirements.txt

# Run all four example profiles end-to-end
 python -m src.main

# Run tests
 python -m pytest -q
```

On macOS/Linux use `source .venv/bin/activate` instead of the PowerShell activation command. If `.venv` already exists, skip environment creation and only activate it. `.venv/` is excluded by `.gitignore`.

### Custom inputs

```powershell
python -m src.main --genre pop --mood happy --energy 0.90 --top 3
python -m src.main --genre lofi --mood chill --energy 0.40 --top 3
python -m src.main --genre classical --mood intense --energy 0.95 --top 3
```

Arguments: `--genre`, `--mood`, and `--energy` must be supplied together for a custom profile. Without them, the app demonstrates four built-in profiles. `--top` is the requested recommendation count (default 5). The app reads `data/songs.csv` relative to its source files, so its data path does not depend on the terminal's working directory once the module is available.

## 5. Reproducible execution evidence (actual runs)

The following are outputs of the project commands, verified against the submitted source and CSV data. The output is text-based so a grader can reproduce results without watching a video.

### Example 1 — Strong match, no retry

**Input command:**

```powershell
python -m src.main --genre pop --mood happy --energy 0.90 --top 3
```

**Output:**

```text
Loaded songs: 18

============================================================
PROFILE: Custom
Genre: pop | Mood: happy | Energy: 0.90
============================================================
1. Sunrise City by Neon Echo
   Score: 3.92
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.92)
2. Gym Hero by Max Pulse
   Score: 2.97
   Because: genre match (+2.0); energy similarity (+0.97)
3. Rooftop Lights by Indigo Parade
   Score: 1.86
   Because: mood match (+1.0); energy similarity (+0.86)
Self-check: PASS | Reranked: no
```

### Example 2 — Different preferences, no retry

**Input command:**

```powershell
python -m src.main --genre lofi --mood chill --energy 0.40 --top 3
```

**Output:**

```text
Loaded songs: 18

============================================================
PROFILE: Custom
Genre: lofi | Mood: chill | Energy: 0.40
============================================================
1. Midnight Coding by LoRoom
   Score: 3.98
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.98)
2. Library Rain by Paper Lanterns
   Score: 3.95
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.95)
3. Focus Flow by LoRoom
   Score: 3.00
   Because: genre match (+2.0); energy similarity (+1.00)
Self-check: PASS | Reranked: no
```

### Example 3 — Integrated reliability loop changes the answer

**Input command:**

```powershell
python -m src.main --genre classical --mood intense --energy 0.95 --top 3
```

**Output:**

```text
Loaded songs: 18

============================================================
PROFILE: Custom
Genre: classical | Mood: intense | Energy: 0.95
============================================================
1. Gym Hero by Max Pulse
   Score: 2.96
   Because: genre match (+0.0); mood match (+1.0); energy similarity (+1.96); balanced retry weights (genre=1, mood=1, energy=2)
2. Storm Runner by Voltline
   Score: 2.92
   Because: genre match (+0.0); mood match (+1.0); energy similarity (+1.92); balanced retry weights (genre=1, mood=1, energy=2)
3. Iron Pulse by Black Circuit
   Score: 1.94
   Because: genre match (+0.0); mood match (+0.0); energy similarity (+1.94); balanced retry weights (genre=1, mood=1, energy=2)
Self-check: PARTIAL | Reranked: yes
Note: Self-check revised first choice from 'Quiet Strings' to 'Gym Hero' after detecting a mood-and-energy conflict.
Note: Catalog limitation: no available song matches genre, mood, and energy within ±0.30; results are best-effort matches.
```

The revised result better satisfies the requested mood and energy, but loses the genre match. This is a transparent ranking trade-off, **not** evidence of measured human satisfaction.

### Example 4 — Guardrail refuses an invalid energy value

**Input command:**

```powershell
python -m src.main --genre pop --mood happy --energy 1.5
```

**Output (stderr, exit status 2):**

```text
Error: target_energy must be a finite number between 0 and 1.
```

## 6. Reliability evaluation and test evidence

Run `python -m pytest -q` from the repo root. **Actual local test result:**

```text
.......................                                                  [100%]
23 passed in 2.20s
```

The 23 tests include the 2 original tests plus 21 reliability-workflow cases. They cover valid profiles, actual rank revision, catalog membership, sorted scores, missing/invalid/out-of-range/NaN input, invalid `top-k`, empty catalogs, duplicate IDs, unavailable genres, a working custom CLI, and safe CLI errors. Unit tests measure expected program behavior, **not recommendation accuracy across real listeners**.

| Test input / condition | Evaluation criterion | Observed result |
|---|---|---|
| `pop / happy / 0.90` | Leave a well-matched top choice unchanged | **PASS:** Sunrise City first, no retry |
| `lofi / chill / 0.40` | Leave a well-matched top choice unchanged | **PASS:** Midnight Coding first, no retry |
| `classical / intense / 0.95` | Detect original mismatch, re-rank, disclose missing full match | **PASS:** Quiet Strings → Gym Hero; `PARTIAL` and warning |
| `pop / happy / 1.5` | Reject invalid energy without traceback | **PASS:** clear error; exit code 2 |
| Duplicate song ID | Reject corrupted catalog before producing recommendations | **PASS:** `ValueError` detected in automated test |
| Empty song catalog | Explain inability to recommend | **PASS:** `ValueError` detected in automated test |

### What improved and what still did not

- **Improved:** The conflicting profile no longer silently recommends the low-energy peaceful song first. The program explains the revision and shows a warning about catalog coverage.
- **Preserved:** The first recommended song is unchanged in the three already well-matched sample profiles.
- **Still limited:** Results use 18 synthetic songs and handcrafted thresholds. No real-user feedback, accuracy benchmark, learned preferences, or calibrated uncertainty is available. Changing weights can help mood/energy while hurting genre relevance.

## 7. Design decisions, reflection, and limitations

- **Use the original scoring code:** retains a clear baseline, minimizes unnecessary changes, and makes improvement observable.
- **One bounded repair pass:** prevents potentially endless retries while remaining easy to test and explain.
- **No unnecessary external model:** avoids API cost, credential setup, unpredictable output, and false claims of generative capability. The assignment explicitly allows an integrated reliability mechanism as the substantial extension.
- **Explicit statuses and explanations:** outputs include real catalog songs and numerically supported scoring contributions; `PARTIAL` is not portrayed as a perfect match.
- **No stretch features:** this submission intentionally focuses on the 21 required points.

**Required ethics, collaboration reflection, testing observations, possible misuse, and future work are documented under labeled prompts in [`model_card.md`](model_card.md).**

## 8. Portfolio

**Repository:** https://github.com/mryuenchan/applied-ai-system-final

**What this project says about me as an AI engineer:** I can take a working recommendation prototype, identify a concrete failure, build a bounded validation and repair workflow, and demonstrate the results with reproducible tests and transparent documentation. I focused on detecting and disclosing mismatches rather than making recommendations look convincing without evidence.

The code and Markdown examples are sufficient to reproduce the submission. A recorded Loom demo is optional and is not required to verify the outputs above.