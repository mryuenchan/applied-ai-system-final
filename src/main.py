"""Command-line entry point for the self-checking Music Recommender."""

import argparse
import logging
from pathlib import Path

from .recommender import load_songs
from .workflow import run_workflow

CATALOG = Path(__file__).resolve().parents[1] / "data" / "songs.csv"

EXAMPLE_PROFILES = {
    "High-Energy Pop": {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.90},
    "Chill Lofi": {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.40},
    "Deep Intense Rock": {"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 0.90},
    "Conflicting Classical/Intense": {"favorite_genre": "classical", "favorite_mood": "intense", "target_energy": 0.95},
}


def display_recommendations(name, prefs, songs, k=5, result=None):
    """Print ranked songs, score evidence, and the quality-check result."""
    if result is None:
        result = run_workflow(prefs, songs, k=k)
    print("=" * 60)
    print(f"PROFILE: {name}")
    print(
        f"Genre: {result.profile['favorite_genre']} | "
        f"Mood: {result.profile['favorite_mood']} | "
        f"Energy: {result.profile['target_energy']:.2f}"
    )
    print("=" * 60)
    for position, (song, score, explanation) in enumerate(result.recommendations, start=1):
        print(f"{position}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Because: {explanation}")
    print(f"Self-check: {result.check_status} | Reranked: {'yes' if result.revised else 'no'}")
    for note in result.notes:
        print(f"Note: {note}")
    print()
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Self-checking Music Recommender Simulation")
    parser.add_argument("--genre", help="Favorite genre (requires --mood and --energy)")
    parser.add_argument("--mood", help="Favorite mood (requires --genre and --energy)")
    parser.add_argument("--energy", type=float, help="Target energy, between 0 and 1")
    parser.add_argument("--top", type=int, default=5, help="How many songs to return (default: 5)")
    args = parser.parse_args(argv)
    supplied = [args.genre is not None, args.mood is not None, args.energy is not None]
    if any(supplied) and not all(supplied):
        parser.error("--genre, --mood, and --energy must be supplied together")

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    try:
        songs = load_songs(str(CATALOG))
        if all(supplied):
            profiles = {"Custom": {"favorite_genre": args.genre, "favorite_mood": args.mood,
                                   "target_energy": args.energy}}
        else:
            profiles = EXAMPLE_PROFILES

        # Verify all inputs and recommendations before printing any output.
        completed = [(name, prefs, run_workflow(prefs, songs, k=args.top))
                     for name, prefs in profiles.items()]
        print(f"Loaded songs: {len(songs)}\n")
        for name, prefs, result in completed:
            display_recommendations(name, prefs, songs, args.top, result=result)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
