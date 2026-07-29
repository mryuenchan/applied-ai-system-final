# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

My project uses a simple content-based music recommendation system. Real music platforms may use listening history, likes, skips, playlists, song information, and the behavior of similar users. My version is simpler because it directly compares a user's preferences with the features of each song.

### Song Data

The songs are stored in `data/songs.csv`. Each song includes:

- ID
- Title
- Artist
- Genre
- Mood
- Energy
- Tempo in BPM
- Valence
- Danceability
- Acousticness

My first version mainly uses `genre`, `mood`, and `energy` when calculating a recommendation score. The other features may be used in later experiments.

### User Profile

The recommender uses this example user profile:

```python
user_profile = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40
}
```

This profile represents a user who prefers chill lofi music with a fairly calm energy level.

### Algorithm Recipe

1. Read all songs from `data/songs.csv`.
2. Start each song with a score of 0.
3. Add 2 points if the song's genre matches the user's favorite genre.
4. Add 1 point if the song's mood matches the user's favorite mood.
5. Add up to 1 point based on how close the song's energy is to the user's target energy.
6. Save the song and its completed score.
7. Repeat the scoring process for every song.
8. Sort the songs from highest score to lowest score.
9. Return the three songs with the highest scores.

### Scoring Rule

The energy-similarity formula is:

```text
energy similarity = 1 - |song energy - target energy|
```

A song with an energy level close to the user's target receives nearly 1 full energy point. A song with a very different energy level receives fewer energy points.

The total score is:

```text
total score = genre points + mood points + energy-similarity points
```

The maximum possible score is:

```text
2 + 1 + 1 = 4 points
```

### Data Flow

```text
INPUT
User profile:
- Favorite genre
- Favorite mood
- Target energy

        ↓

LOAD DATA
Read all songs from data/songs.csv

        ↓

PROCESS EACH SONG
Start the song's score at 0

Genre matches? → Add 2 points
Mood matches? → Add 1 point
Energy closeness → Add up to 1 point

        ↓

STORE RESULT
Save the song and its total score

        ↓

RANK
Sort all songs from highest score to lowest score

        ↓

OUTPUT
Display the top 3 recommended songs
```

### Potential Biases

The system may over-prioritize genre because a genre match is worth 2 of the 4 possible points. This could cause it to rank a mediocre lofi song above a very suitable song from a related genre, such as ambient music.

The system also requires exact genre and mood matches. It does not understand that words such as `peaceful`, `relaxed`, and `chill` may represent similar feelings. It uses a small fictional catalog and does not consider lyrics, language, listening history, skips, favorite artists, or the preferences of similar users. Because of these limitations, the recommendations may be narrow or repetitive.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

The default user profile is:

```python
user_prefs = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.8
}
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

Loaded songs: 18
>> 
>> ============================================================
>> PROFILE: High-Energy Pop
>> Genre: pop | Mood: happy | Energy: 0.9
>> ============================================================
>> 1. Sunrise City by Neon Echo
>>    Score: 3.92
>>    Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.92)
>> 
>> 2. Gym Hero by Max Pulse
>>    Score: 2.97
>>    Because: genre match (+2.0); energy similarity (+0.97)
>> 
>> 3. Rooftop Lights by Indigo Parade
>>    Score: 1.86
>>    Because: mood match (+1.0); energy similarity (+0.86)
>> 
>> 4. Storm Runner by Voltline
>>    Score: 0.99
>>    Because: energy similarity (+0.99)
>> 
>> 5. Electric Horizon by Pixel Current
>>    Score: 0.98
>>    Because: energy similarity (+0.98)
>> 
>> ============================================================
>> PROFILE: Chill Lofi
>> Genre: lofi | Mood: chill | Energy: 0.4
>> ============================================================
>> 1. Midnight Coding by LoRoom
>>    Score: 3.98
>>    Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.98)
>> 
>> 2. Library Rain by Paper Lanterns
>>    Score: 3.95
>>    Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.95)
>> 
>> 3. Focus Flow by LoRoom
>>    Score: 3.00
>>    Because: genre match (+2.0); energy similarity (+1.00)
>> 
>> 4. Spacewalk Thoughts by Orbit Bloom
>>    Score: 1.88
>>    Because: mood match (+1.0); energy similarity (+0.88)
>> 
>> 5. Coffee Shop Stories by Slow Stereo
>>    Score: 0.97
>>    Because: energy similarity (+0.97)
>> 
>> ============================================================
>> PROFILE: Deep Intense Rock
>> Genre: rock | Mood: intense | Energy: 0.9
>> ============================================================
>> 1. Storm Runner by Voltline
>>    Score: 3.99
>>    Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.99)
>> 
>> 2. Gym Hero by Max Pulse
>>    Score: 1.97
>>    Because: mood match (+1.0); energy similarity (+0.97)
>> 
>> 3. Electric Horizon by Pixel Current
>>    Score: 0.98
>>    Because: energy similarity (+0.98)
>> 
>> 4. Sunrise City by Neon Echo
>>    Score: 0.92
>>    Because: energy similarity (+0.92)
>> 
>> 5. Iron Pulse by Black Circuit
>>    Score: 0.92
>>    Because: energy similarity (+0.92)
>> 
>> ============================================================
>> PROFILE: Conflicting Classical/Intense
>> Genre: classical | Mood: intense | Energy: 0.95
>> ============================================================
>> 1. Quiet Strings by Aurora Hall
>>    Score: 2.30
>>    Because: genre match (+2.0); energy similarity (+0.30)
>> 
>> 2. Gym Hero by Max Pulse
>>    Score: 1.98
>>    Because: mood match (+1.0); energy similarity (+0.98)
>> 
>> 3. Storm Runner by Voltline
>>    Score: 1.96
>>    Because: mood match (+1.0); energy similarity (+0.96)
>> 
>> 4. Iron Pulse by Black Circuit
>>    Score: 0.97
>>    Because: energy similarity (+0.97)
>> 
>> 5. Electric Horizon by Pixel Current
>>    Score: 0.93
>>    Because: energy similarity (+0.93)
