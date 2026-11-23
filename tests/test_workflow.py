"""Tests for the production workflow, including its new reliability mechanism."""

from pathlib import Path
import subprocess
import sys

import pytest

from src.recommender import load_songs, recommend_songs
from src.workflow import run_workflow

CATALOG = Path(__file__).resolve().parents[1] / "data" / "songs.csv"


@pytest.fixture
def songs():
    return load_songs(str(CATALOG))


@pytest.mark.parametrize("genre,mood,energy", [
    ("pop", "happy", 0.9),
    ("lofi", "chill", 0.4),
    ("rock", "intense", 0.9),
])
def test_valid_profiles_preserve_first_recommendation(songs, genre, mood, energy):
    prefs = {"favorite_genre": genre, "favorite_mood": mood, "target_energy": energy}
    original = recommend_songs(prefs, songs)
    result = run_workflow(prefs, songs)
    assert not result.revised
    assert result.check_status == "PASS"
    assert result.recommendations[0][0]["title"] == original[0][0]["title"]


def test_conflict_triggers_integrated_repair_and_changes_rank(songs):
    prefs = {"favorite_genre": "classical", "favorite_mood": "intense", "target_energy": 0.95}
    original = recommend_songs(prefs, songs)
    result = run_workflow(prefs, songs)
    assert original[0][0]["title"] == "Quiet Strings"
    assert result.initial_top == "Quiet Strings"
    assert result.revised
    assert result.recommendations[0][0]["title"] == "Gym Hero"
    assert result.check_status == "PARTIAL"
    assert any("no available song" in msg for msg in result.notes)
    assert "balanced retry weights" in result.recommendations[0][2]


def test_recommendations_are_actual_catalog_songs_and_sorted(songs):
    prefs = {"favorite_genre": "classical", "favorite_mood": "intense", "target_energy": 0.95}
    result = run_workflow(prefs, songs, 5)
    ids = {song["id"] for song in songs}
    assert len(result.recommendations) == 5
    assert all(song["id"] in ids for song, _, _ in result.recommendations)
    assert [score for _, score, _ in result.recommendations] == sorted(
        [score for _, score, _ in result.recommendations], reverse=True
    )


@pytest.mark.parametrize("bad_prefs", [
    {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 1.5},
    {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": float("nan")},
    {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": True},
    {"favorite_genre": "", "favorite_mood": "happy", "target_energy": 0.5},
    {"favorite_genre": "pop", "favorite_mood": "", "target_energy": 0.5},
    {"favorite_genre": "pop", "favorite_mood": "happy"},
])
def test_invalid_inputs_fail_safely(songs, bad_prefs):
    with pytest.raises(ValueError):
        run_workflow(bad_prefs, songs)


@pytest.mark.parametrize("top", [0, -1, 100, 2.5, True])
def test_invalid_top_k_fails_safely(songs, top):
    with pytest.raises(ValueError):
        run_workflow({"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}, songs, top)


def test_empty_catalog_is_explained():
    with pytest.raises(ValueError, match="empty"):
        run_workflow({"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}, [])


def test_duplicate_song_id_is_rejected(songs):
    with pytest.raises(ValueError, match="Duplicate"):
        run_workflow({"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}, songs + [songs[0]])


def test_unavailable_genre_reports_catalog_limitation(songs):
    result = run_workflow({"favorite_genre": "opera", "favorite_mood": "chill", "target_energy": 0.4}, songs)
    assert result.recommendations
    assert result.check_status in ("PARTIAL", "REVIEW")
    assert any("Catalog limitation" in note for note in result.notes)


def test_cli_valid_custom_profile():
    completed = subprocess.run(
        [sys.executable, "-m", "src.main", "--genre", "lofi", "--mood", "chill", "--energy", "0.4", "--top", "3"],
        capture_output=True, text=True, cwd=CATALOG.parents[1], check=False
    )
    assert completed.returncode == 0, completed.stderr
    assert "PROFILE: Custom" in completed.stdout
    assert "Midnight Coding" in completed.stdout
    assert "Self-check: PASS" in completed.stdout


def test_cli_invalid_energy_uses_clear_error():
    completed = subprocess.run(
        [sys.executable, "-m", "src.main", "--genre", "pop", "--mood", "happy", "--energy", "2"],
        capture_output=True, text=True, cwd=CATALOG.parents[1], check=False
    )
    assert completed.returncode == 2
    assert "between 0 and 1" in completed.stderr
    assert "Traceback" not in completed.stderr
