# Model Card — VibeMatch 2.0: Self-Checking Music Recommender

## 1. Name and original project

**Base:** CodePath AI 110 Module 3 *Music Recommender Simulation* (also documented as VibeMatch 1.0). It ranked 18 fictional songs using exact genre and mood matches plus energy similarity and displayed the top five with reasons. The original scorer is preserved in `src/recommender.py`.

**Extension:** VibeMatch 2.0 adds a production-path reliability workflow in `src/workflow.py`: input/catalog guardrails, an evaluation step, a one-pass guarded retry when the top song fails both mood and energy checks, and visible quality/coverage notes. It remains a rule-based system rather than an LLM, generative model, or model trained on listening data.

## 2. Intended use and how decisions are made

Use this educational recommender to explore how explicit song attributes shape rankings and how a reliability check can alter a misleading result. It accepts favorite genre, mood, and target energy on a 0–1 scale. The initial ranking assigns genre +2, mood +1, and energy similarity up to +1. A conflicting initial top song can trigger one alternative ranking with genre +1, mood +1, and energy similarity up to +2. It always retrieves recommendations from the known CSV catalog.

**Status interpretation:** `PASS` means the top result meets the requested genre and mood and has energy within 0.30; `PARTIAL` means at least one requested feature is not met; `REVIEW` means the top result still conflicts with both mood and energy. These are **rule checks**, not measured accuracy, predictive certainty, or confidence percentages.

## 3. Data, limitations, and biases — What are the limitations or biases in your system?

The dataset contains only 18 invented songs with a limited choice of genres and moods. It lacks real listener responses, lyrics, historical preferences, skipped songs, multilingual tags, demographic representation, and quality labels. As a result, it cannot establish whether people truly like the recommendations.

Exact text comparisons can create narrow results: `chill`, `relaxed`, and `peaceful` are treated as different moods even where listeners might see them as similar. The original genre weight over-prioritizes exact genre, while the retry can over-prioritize energy. The 0.30 energy tolerance was chosen as a transparent engineering rule, **not** validated against human preferences. The system cannot invent an unavailable matching song and warns when catalog coverage is insufficient.

## 4. Safety, misuse, and mitigation — Could your AI be misused, and how would you prevent that?

A misleading use would be to present a high numerical recommendation score as a probability of enjoyment or a definitive account of someone's musical preferences. The app avoids probabilistic claims and prints the components used to compute scores. It rejects missing or invalid inputs, non-finite or out-of-range energy, invalid top-k, empty or malformed catalogs, and duplicate song IDs. An unresolved mismatch gets a `PARTIAL` or `REVIEW` label instead of being silently treated as correct.

It should not be used for high-stakes personal profiling, automated screening, commercial claims of personalization quality, or decisions about people. This local exercise does not collect account identifiers or personal listening history. A public web service would need additional privacy and security review.

## 5. Reliability evidence — What surprised you while testing your AI's reliability?

The concrete counterexample was `classical / intense / 0.95`: the old scorer ranked **Quiet Strings** (peaceful, 0.25 energy) first only because the classical match was heavily weighted. Automated testing confirms the new integrated quality check detects that mood-and-energy conflict and re-ranks to **Gym Hero** (intense, 0.93 energy). It also outputs a warning that no catalog song satisfies all three preferences. This illustrates that a plausible top-ranked result can conflict with a user's intention, and fixing one dimension does not necessarily fix every dimension.

The three already well-matched example profiles remain unchanged at the top after the upgrade. Local automated testing produced **23 passing tests** (2 existing plus 21 new reliability-workflow cases). This confirms defined software behaviors, not real-world recommendation quality or accuracy. See `README.md` for the exact command, CLI evidence, and parseable evaluation table.

## 6. AI collaboration — How did AI help, what suggestion did you accept, and what did you reject or revise?

During development I used ChatGPT to discuss the assignment checklist, understand the existing GitHub/VS Code workflow, design a reliability-focused extension, and help implement and test the new Python functionality. Suggestions and generated code were evaluated against the rubric and existing repository rather than treated as a substitute for program testing.

**Suggestion accepted:** I followed the recommendation to build on the existing Module 3 Music Recommender instead of creating an unrelated project. That preserved the working scoring system and gave the improvement a clear baseline.

**Suggestion rejected:** I chose *not* to implement optional stretch features, even after the assistant proposed pursuing the bonus points. I wanted to prioritize completing the documented, reproducible requirements of the main 21-point rubric.

Human Review: Although the system passed all 23 automated tests, these tests only confirm that the code behaves as expected. They do not prove that real listeners would enjoy the recommended songs. I reviewed the system's outputs and confirmed that the self-checking feature works as intended, but evaluating actual listener satisfaction would require feedback from real users.

## 7. Future improvements and trade-offs

- Add more catalog coverage, including related mood and genre tags and language information.
- Allow users to express priorities (genre, mood, energy) rather than switching fixed weights automatically.
- Collect consent-based ratings and skips, then measure actual listener satisfaction on held-out sessions.
- Test energy tolerance and ranking changes against diverse profiles, including cases where re-ranking makes a result worse.
- Report calibrated uncertainty only if adequate evaluation data supports it.

The current design intentionally favors an easy-to-audit, bounded repair loop. Its status messages are honest about incomplete matches, and no generative model, model training, RAG, or agent tool calls are claimed.