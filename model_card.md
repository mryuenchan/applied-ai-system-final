
# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

VibeMatch 1.0 is a simple music recommendation system created for a classroom programming project. It recommends songs by comparing a user's preferred genre, mood, and energy level with the information stored for each song.

The system assumes that the user can describe their taste using one favorite genre, one favorite mood, and one target energy level. It is intended for learning how recommendation systems use data, scoring, and ranking.

This project should not be used as a real commercial music recommender. It should also not be used to make important decisions about people because it uses a small fictional dataset and a very simple scoring system.

---

## 3. How the Model Works

Each user provides a favorite genre, favorite mood, and target energy level. The recommender compares those preferences with every song in the catalog.

A song receives 2 points when its genre matches the user's favorite genre. It receives 1 point when its mood matches the user's favorite mood. It can also receive up to 1 point depending on how close its energy is to the user's target energy.

After every song receives a score, the system sorts the songs from highest score to lowest score. It returns the five songs with the highest scores and explains which features contributed to each score.

---

## 4. Data

The catalog contains 18 fictional songs. Each song includes:

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

The catalog includes genres such as pop, lofi, rock, ambient, jazz, classical, hip hop, electronic, folk, reggae, R&B, metal, and country.

I expanded the starter dataset by adding eight new fictional songs. This created more variety, but the catalog is still very small. It does not represent every genre, mood, artist, language, or type of listener. Because the dataset has no actual listener ratings, it cannot provide ground-truth labels for measuring recommendation accuracy.

---

## 5. Strengths

The recommender works well when the user's genre, mood, and energy preferences agree with one another. For example, the Chill Lofi profile correctly ranked calm lofi songs near the top.

The system is easy to understand because each recommendation includes a score and specific reasons. It also produces different rankings for users with different preferences.

The energy comparison works better than simply rewarding songs with the highest energy. It rewards songs that are closer to the particular energy level requested by the user.

---

## 6. Limitations and Bias

One weakness is that the recommender gives 2 of the 4 possible points for an exact genre match. During testing, this caused Quiet Strings to rank first for a user who requested classical music, an intense mood, and very high energy, even though the song had low energy and did not match the requested mood.

The system also treats related moods such as chill, relaxed, and peaceful as completely different because it only uses exact text matches. This may create a filter bubble by repeatedly recommending songs from the selected genre instead of introducing suitable songs from related genres.

The catalog is small and fictional. The scoring system does not currently use tempo, valence, danceability, acousticness, listening history, skipped songs, favorite artists, lyrics, or user feedback.

---

## 7. Evaluation

I tested the recommender with four different profiles:

- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Conflicting Classical/Intense

For each profile, I examined whether the top five songs matched the requested genre, mood, and energy level.

The Chill Lofi profile produced the most intuitive results. Midnight Coding and Library Rain ranked first because they matched the lofi genre and chill mood while also having energy levels close to the target.

The most surprising result came from the Conflicting Classical/Intense profile. Quiet Strings ranked first mainly because its classical genre match was worth 2 points, even though its mood and energy did not closely fit the user's other preferences.

### Profile Comparisons

**High-Energy Pop and Chill Lofi:**  
The High-Energy Pop profile favored songs such as Sunrise City and Gym Hero because they had higher energy or pop-related matches. The Chill Lofi profile favored Midnight Coding and Library Rain because their lower energy, genre, and mood better matched calm study music.

**Chill Lofi and Deep Intense Rock:**  
The Chill Lofi profile preferred calm songs with energy near 0.40. The Deep Intense Rock profile favored Storm Runner and other high-energy songs. This difference makes sense because the profiles requested opposite genres, moods, and energy levels.

**Deep Intense Rock and Conflicting Classical/Intense:**  
Both profiles requested intense and energetic music, but their preferred genres were different. Storm Runner matched all three preferences for the rock profile. Quiet Strings ranked first for the classical profile because the strong genre weight overpowered its weaker mood and energy matches.

**High-Energy Pop and Deep Intense Rock:**  
Both profiles requested high energy, but `Sunrise City` ranked first for pop/happy while `Storm Runner` ranked first for rock/intense. Their different genre and mood matches made the difference.

**High-Energy Pop and Conflicting Classical/Intense:**  
Both requested energetic music. `Sunrise City` matched the pop user's genre and mood, while the classical user's high genre weight pushed the much calmer `Quiet Strings` into first place.

**Chill Lofi and Conflicting Classical/Intense:**  
`Midnight Coding` matched the chill user's genre, mood, and energy, but `Quiet Strings` ranked first for the conflicting user mainly because of its genre. The second profile showed that matching one feature can be misleading.

### Weight-Shift Experiment

I temporarily reduced the genre match from 2 points to 1 point and increased energy similarity from a maximum of 1 point to a maximum of 2 points.

After the change, high-energy intense songs ranked above Quiet Strings for the conflicting profile. This result seemed more accurate for that user because the requested energy was 0.95.

For the conflicting profile, the top three changed as follows:

```text
Original:                        Increased energy weight:
1. Quiet Strings — 2.30         1. Gym Hero — 2.96
2. Gym Hero — 1.98              2. Storm Runner — 2.92
3. Storm Runner — 1.96          3. Iron Pulse — 1.94
```

However, the experimental weights may be less accurate for users who care more about genre than energy. This showed that changing weights can improve one type of recommendation while making another type less accurate.

### Recommendation Outputs

```text
Loaded songs: 18

============================================================
PROFILE: High-Energy Pop
Genre: pop | Mood: happy | Energy: 0.9
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

4. Storm Runner by Voltline
   Score: 0.99
   Because: energy similarity (+0.99)

5. Electric Horizon by Pixel Current
   Score: 0.98
   Because: energy similarity (+0.98)

============================================================
PROFILE: Chill Lofi
Genre: lofi | Mood: chill | Energy: 0.4
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

4. Spacewalk Thoughts by Orbit Bloom
   Score: 1.88
   Because: mood match (+1.0); energy similarity (+0.88)

5. Coffee Shop Stories by Slow Stereo
   Score: 0.97
   Because: energy similarity (+0.97)

============================================================
PROFILE: Deep Intense Rock
Genre: rock | Mood: intense | Energy: 0.9
============================================================
1. Storm Runner by Voltline
   Score: 3.99
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.99)

2. Gym Hero by Max Pulse
   Score: 1.97
   Because: mood match (+1.0); energy similarity (+0.97)

3. Electric Horizon by Pixel Current
   Score: 0.98
   Because: energy similarity (+0.98)

4. Sunrise City by Neon Echo
   Score: 0.92
   Because: energy similarity (+0.92)

5. Iron Pulse by Black Circuit
   Score: 0.92
   Because: energy similarity (+0.92)

============================================================
PROFILE: Conflicting Classical/Intense
Genre: classical | Mood: intense | Energy: 0.95
============================================================
1. Quiet Strings by Aurora Hall
   Score: 2.30
   Because: genre match (+2.0); energy similarity (+0.30)

2. Gym Hero by Max Pulse
   Score: 1.98
   Because: mood match (+1.0); energy similarity (+0.98)

3. Storm Runner by Voltline
   Score: 1.96
   Because: mood match (+1.0); energy similarity (+0.96)

4. Iron Pulse by Black Circuit
   Score: 0.97
   Because: energy similarity (+0.97)

5. Electric Horizon by Pixel Current
   Score: 0.93
   Because: energy similarity (+0.93)
```

---

## 8. Future Work

I would improve the system by using more of the available song features, including tempo, valence, danceability, and acousticness.

I would also group related moods together so that words such as chill, relaxed, and peaceful can receive partial matching points instead of being treated as completely unrelated.

A future version could learn from likes, skips, replay history, and favorite artists. I would also use a much larger catalog and add a diversity rule so the top recommendations do not all come from the same genre.

---

## 9. Personal Reflection

My biggest learning moment was understanding that a recommendation system can be built by scoring every option and then ranking the scores. Before this project, recommendation systems seemed much more mysterious. I learned that even a simple formula can produce results that feel personalized.

AI tools helped me understand the scoring formula, write the Python functions, and troubleshoot errors. However, I still needed to double-check the suggested code against the starter files. For example, the starter `main.py` used different dictionary keys from the scoring function, which caused a `KeyError`. I also had to make sure the required return formats matched the rest of the project.

I was surprised that such a small algorithm could produce recommendations that often felt reasonable. At the same time, the conflicting profile showed how easily the weights can create strange results. A song can rank first because of one strongly weighted feature even when the rest of its attributes do not fit the user.

Next, I would add partial matches for related moods and genres, use more numerical features, and let the system learn from user feedback. I would also test it with a much larger and more realistic song catalog.
