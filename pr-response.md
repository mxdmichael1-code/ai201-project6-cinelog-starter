# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename

**What I did:**  
Renamed `save_to_watchlist()` to `add_to_watchlist()` in `services/watchlist_service.py` to follow the project's `verb_to_noun` naming convention. Updated all imports and function calls across the codebase to use the new name.

**How I verified:**  
Performed a project-wide search for `save_to_watchlist` to confirm that no outdated references remained. Ran the test suite with `pytest tests/` to ensure the rename did not introduce any breaking changes.

## Comment 2 — Deduplication

**What I did:**  
Added duplicate prevention logic to `add_to_watchlist()` in `services/watchlist_service.py` and updated lass `AlreadyInWatchlistError(Exception)` in `collection_service.py`. The function now checks whether a `WatchlistEntry` already exists for the same `user_id` and `film_id` before creating a new entry. If a duplicate is found, it raises `AlreadyInWatchlistError` instead of adding another record.

**How I verified:**  
Reviewed the implementation against `add_to_collection()` to ensure the same deduplication pattern was applied. Ran `pytest tests/` to verify that the changes did not break existing functionality.

## Comment 3 — Missing test

**What I did:**  
Implemented the missing watchlist removal functionality by adding `remove_from_watchlist(user_id, film_id)` in `services/watchlist_service.py` and adding the corresponding `NotInWatchlistError` exception handling in `collection_service.py`. Following the existing collection service pattern, I also created `tests/test_watchlist.py` and added an equivalent test for `add_to_watchlist()` based on `test_add_to_collection_nonexistent_film_raises`, using the same fixture and assertion structure.

**How I verified:**  
Ran the new watchlist test to confirm that adding a nonexistent film correctly raises `FilmNotFoundError`. Ran the full test suite to verify that the new watchlist functionality did not introduce regressions.

## Comment 4 — Default visibility
**My position:**
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->