import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError

import db.db as db_module
from db.db import (
    create_db_engine_with_retries,
    init_db,
    get_db,
    with_db_session,
)


@pytest.fixture(autouse=True)
def reset_engine_singleton():
    """init_db()/get_db() memoize the engine/session at module level; reset
    between tests so they don't leak into each other."""
    original_engine, original_session = db_module._engine, db_module._Session
    db_module._engine = None
    db_module._Session = None
    yield
    db_module._engine, db_module._Session = original_engine, original_session


def _operational_error():
    return OperationalError("stmt", {}, Exception("connection refused"))


def test_create_db_engine_with_retries_succeeds_immediately():
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__ = MagicMock()
    mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

    with patch("db.db.create_engine", return_value=mock_engine) as mock_create, patch(
        "db.db.time.sleep"
    ) as mock_sleep:
        engine = create_db_engine_with_retries("sqlite:///:memory:", retries=3, delay=0)

        assert engine is mock_engine
        mock_create.assert_called_once()
        mock_sleep.assert_not_called()


def test_create_db_engine_with_retries_recovers_after_failures():
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__ = MagicMock()
    mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

    failing_engine = MagicMock()
    failing_engine.connect.side_effect = _operational_error()

    with patch(
        "db.db.create_engine", side_effect=[failing_engine, failing_engine, mock_engine]
    ) as mock_create, patch("db.db.time.sleep") as mock_sleep:
        engine = create_db_engine_with_retries("sqlite:///:memory:", retries=5, delay=1)

        assert engine is mock_engine
        assert mock_create.call_count == 3
        assert mock_sleep.call_count == 2


def test_create_db_engine_with_retries_raises_after_exhausting_retries():
    failing_engine = MagicMock()
    failing_engine.connect.side_effect = _operational_error()

    with patch("db.db.create_engine", return_value=failing_engine), patch(
        "db.db.time.sleep"
    ):
        with pytest.raises(RuntimeError, match="Could not connect"):
            create_db_engine_with_retries("sqlite:///:memory:", retries=3, delay=0)


def test_init_db_is_idempotent():
    with patch("db.db.create_db_engine_with_retries") as mock_create_engine:
        mock_create_engine.return_value = MagicMock()

        init_db()
        init_db()

        mock_create_engine.assert_called_once()


def test_get_db_yields_and_closes_session():
    fake_session = MagicMock()
    with patch("db.db.init_db"), patch.object(
        db_module, "_Session", return_value=fake_session
    ):
        gen = get_db()
        db = next(gen)
        assert db is fake_session
        fake_session.close.assert_not_called()

        with pytest.raises(StopIteration):
            next(gen)
        fake_session.close.assert_called_once()


def test_with_db_session_passes_session_and_closes_after_success():
    fake_session = MagicMock()

    @with_db_session
    def do_something(db, value):
        return (db, value)

    with patch("db.db.get_db") as mock_get_db:
        def fake_gen():
            yield fake_session

        mock_get_db.return_value = fake_gen()
        result = do_something(42)

    assert result == (fake_session, 42)


def test_with_db_session_closes_session_even_if_func_raises():
    fake_session = MagicMock()

    @with_db_session
    def do_something(db):
        raise ValueError("boom")

    with patch("db.db.get_db") as mock_get_db:
        def fake_gen():
            try:
                yield fake_session
            finally:
                fake_session.close()

        mock_get_db.return_value = fake_gen()
        with pytest.raises(ValueError, match="boom"):
            do_something()

    fake_session.close.assert_called_once()
