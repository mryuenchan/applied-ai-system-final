"""
Command line runner for the Music Recommender Simulation.
"""

from .recommender import load_songs, recommend_songs


def display_recommendations(
    profile_name,
    user_prefs,
    songs
):
    """Display the top five songs for one user profile."""

    recommendations = recommend_songs(
        user_prefs,
        songs,
        k=5
    )

    print("=" * 60)
    print(f"PROFILE: {profile_name}")
    print(
        f"Genre: {user_prefs['favorite_genre']} | "
        f"Mood: {user_prefs['favorite_mood']} | "
        f"Energy: {user_prefs['target_energy']}"
    )
    print("=" * 60)

    for position, recommendation in enumerate(
        recommendations,
        start=1
    ):
        song, score, explanation = recommendation

        print(
            f"{position}. {song['title']} "
            f"by {song['artist']}"
        )
        print(f"   Score: {score:.2f}")
        print(f"   Because: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    print(f"Loaded songs: {len(songs)}\n")

    profiles = {
        "High-Energy Pop": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.90
        },

        "Chill Lofi": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.40
        },

        "Deep Intense Rock": {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.90
        },

        "Conflicting Classical/Intense": {
            "favorite_genre": "classical",
            "favorite_mood": "intense",
            "target_energy": 0.95
        }
    }

    for profile_name, user_prefs in profiles.items():
        display_recommendations(
            profile_name,
            user_prefs,
            songs
        )


if __name__ == "__main__":
    main()