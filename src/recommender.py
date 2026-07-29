import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represent a song and its musical attributes."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represent a user's musical preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Recommend Song objects using a user's preferences."""

    def __init__(self, songs: List[Song]):
        """Store the song catalog used by the recommender."""

        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5
    ) -> List[Song]:
        """Return the top k songs for the user."""

        scored_songs = []

        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy
        }

        for song in self.songs:
            song_data = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy
            }

            score, reasons = score_song(
                user_prefs,
                song_data
            )

            scored_songs.append(
                (song, score)
            )

        ranked_songs = sorted(
            scored_songs,
            key=lambda result: result[1],
            reverse=True
        )

        return [
            song
            for song, score in ranked_songs[:k]
        ]

    def explain_recommendation(
        self,
        user: UserProfile,
        song: Song
    ) -> str:
        """Explain why a song matches the user's preferences."""

        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy
        }

        song_data = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy
        }

        score, reasons = score_song(
            user_prefs,
            song_data
        )

        explanation = "; ".join(reasons)

        return f"Score: {score:.2f} - {explanation}"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dictionaries."""

    songs = []

    with open(
        csv_path,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Skip blank rows.
            if not row.get("id"):
                continue

            # Convert numerical strings into numbers.
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(
                row["danceability"]
            )
            row["acousticness"] = float(
                row["acousticness"]
            )

            songs.append(row)

    return songs


def score_song(
    user_prefs: Dict,
    song: Dict
) -> Tuple[float, List[str]]:
    """Score one song and return its score and explanation reasons."""

    score = 0.0
    reasons = []

    favorite_genre = str(
        user_prefs["favorite_genre"]
    ).strip().lower()

    favorite_mood = str(
        user_prefs["favorite_mood"]
    ).strip().lower()

    song_genre = str(
        song["genre"]
    ).strip().lower()

    song_mood = str(
        song["mood"]
    ).strip().lower()

    # Add 2 points for a matching genre.
    if song_genre == favorite_genre:
        score += 2.0
        reasons.append(
            "genre match (+2.0)"
        )

    # Add 1 point for a matching mood.
    if song_mood == favorite_mood:
        score += 1.0
        reasons.append(
            "mood match (+1.0)"
        )

    # Add up to 1 point for energy similarity.
    song_energy = float(
        song["energy"]
    )

    target_energy = float(
        user_prefs["target_energy"]
    )

    energy_difference = abs(
        song_energy - target_energy
    )

    energy_similarity = max(
        0.0,
        1.0 - energy_difference
    )

    score += energy_similarity

    reasons.append(
        f"energy similarity (+{energy_similarity:.2f})"
    )

    return round(score, 2), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Rank all songs and return the top k recommendations."""

    scored_songs = []

    for song in songs:
        score, reasons = score_song(
            user_prefs,
            song
        )

        explanation = "; ".join(
            reasons
        )

        scored_songs.append(
            (
                song,
                score,
                explanation
            )
        )

    ranked_songs = sorted(
        scored_songs,
        key=lambda result: result[1],
        reverse=True
    )

    return ranked_songs[:k]