import uuid
from datetime import datetime, timedelta, timezone

import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
    FilmNotFoundError,
    AlreadyInWatchlistError,
    NotInWatchlistError,
)


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id


# ── Basic add ───────────────────────────────────────────────────────────────

def test_add_to_watchlist_creates_entry(app, sample_user, sample_film):
    """
    Adding a valid film should create a WatchlistEntry in the database.
    """
    with app.app_context():
        entry = add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert entry is not None
        assert entry.user_id == sample_user
        assert entry.film_id == sample_film

        # Verify it persisted
        in_db = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert in_db is not None


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """Adding a film that does not exist should raise FilmNotFoundError."""
    missing_film_id = str(uuid.uuid4())

    with app.app_context(), pytest.raises(FilmNotFoundError):
        add_to_watchlist(user_id=sample_user, film_id=missing_film_id)


def test_add_to_watchlist_rejects_duplicate(app, sample_user, sample_film):
    """A user should not be able to add the same film twice."""
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count() == 1


def test_watchlist_entries_default_to_public(app, sample_user, sample_film):
    """New watchlist entries should be public by default."""
    with app.app_context():
        entry = add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert entry.public is True


def test_remove_from_watchlist_deletes_entry(app, sample_user, sample_film):
    """Removing an existing entry should delete it from the database."""
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert remove_from_watchlist(sample_user, sample_film) is True
        assert WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first() is None


def test_remove_from_watchlist_missing_entry_raises(app, sample_user, sample_film):
    """Removing a film that is not saved should raise NotInWatchlistError."""
    with app.app_context(), pytest.raises(NotInWatchlistError):
        remove_from_watchlist(sample_user, sample_film)


def test_get_watchlist_returns_newest_first(app, sample_user):
    """The most recently added film should appear first."""
    with app.app_context():
        older_film = Film(title="Alien", year=1979)
        newer_film = Film(title="Blade Runner", year=1982)
        db.session.add_all([older_film, newer_film])
        db.session.commit()

        older_entry = WatchlistEntry(
            user_id=sample_user,
            film_id=older_film.id,
            date_added=datetime.now(timezone.utc) - timedelta(days=5),
        )
        newer_entry = WatchlistEntry(
            user_id=sample_user,
            film_id=newer_film.id,
            date_added=datetime.now(timezone.utc),
        )
        db.session.add_all([older_entry, newer_entry])
        db.session.commit()

        titles = [film["title"] for film in get_watchlist(sample_user)]

        assert titles == ["Blade Runner", "Alien"]
