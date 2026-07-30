"""Repository for DecisionSignal feedback and forward outcomes."""

from __future__ import annotations

from typing import Any

from sqlalchemy import and_, desc, func, select

from src.storage import (
    DatabaseManager,
    DecisionSignalFeedbackRecord,
    DecisionSignalOutcomeRecord,
    DecisionSignalRecord,
    utc_naive_now,
)


class DecisionSignalOutcomeRepository:
    """DB access for signal-level outcome and feedback sidecar tables."""

    def __init__(self, db_manager: DatabaseManager | None = None):
        self.db = db_manager or DatabaseManager.get_instance()

    def list_candidate_signals(
        self,
        *,
        signal_id: int | None = None,
        stock_codes: list[str] | None = None,
        market: str | None = None,
        action: str | None = None,
        source_type: str | None = None,
        statuses: list[str] | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[DecisionSignalRecord]:
        safe_limit = max(1, min(int(limit), 500))
        safe_offset = max(0, int(offset))
        conditions = []
        if signal_id is not None:
            conditions.append(DecisionSignalRecord.id == signal_id)
        if stock_codes:
            conditions.append(DecisionSignalRecord.stock_code.in_(stock_codes))
        if market:
            conditions.append(DecisionSignalRecord.market == market)
        if action:
            conditions.append(DecisionSignalRecord.action == action)
        if source_type:
            conditions.append(DecisionSignalRecord.source_type == source_type)
        if statuses:
            conditions.append(DecisionSignalRecord.status.in_(statuses))
        where_clause = and_(*conditions) if conditions else True
        with self.db.get_session() as session:
            rows = session.execute(
                select(DecisionSignalRecord)
                .where(where_clause)
                .order_by(desc(DecisionSignalRecord.created_at), desc(DecisionSignalRecord.id))
                .offset(safe_offset)
                .limit(safe_limit)
            ).scalars().all()
            return list(rows)

    def list_outcomes_for_signals(
        self,
        *,
        signal_ids: list[int],
        engine_version: str,
    ) -> list[DecisionSignalOutcomeRecord]:
        if not signal_ids:
            return []
        with self.db.get_session() as session:
            rows = session.execute(
                select(DecisionSignalOutcomeRecord)
                .where(
                    DecisionSignalOutcomeRecord.signal_id.in_(signal_ids),
                    DecisionSignalOutcomeRecord.engine_version == engine_version,
                )
            ).scalars().all()
            return list(rows)

    def get_outcome(
        self,
        *,
        signal_id: int,
        horizon: str,
        engine_version: str,
    ) -> DecisionSignalOutcomeRecord | None:
        with self.db.get_session() as session:
            return session.execute(
                select(DecisionSignalOutcomeRecord)
                .where(
                    DecisionSignalOutcomeRecord.signal_id == signal_id,
                    DecisionSignalOutcomeRecord.horizon == horizon,
                    DecisionSignalOutcomeRecord.engine_version == engine_version,
                )
                .limit(1)
            ).scalar_one_or_none()

    def upsert_outcome(self, fields: dict[str, Any]) -> tuple[DecisionSignalOutcomeRecord, bool]:
        now = utc_naive_now()
        with self.db.get_session() as session:
            existing = session.execute(
                select(DecisionSignalOutcomeRecord)
                .where(
                    DecisionSignalOutcomeRecord.signal_id == fields["signal_id"],
                    DecisionSignalOutcomeRecord.horizon == fields["horizon"],
                    DecisionSignalOutcomeRecord.engine_version == fields["engine_version"],
                )
                .limit(1)
            ).scalar_one_or_none()
            if existing is None:
                row = DecisionSignalOutcomeRecord(**fields)
                session.add(row)
                session.commit()
                session.refresh(row)
                return row, True

            for key, value in fields.items():
                if key in {"id", "created_at"}:
                    continue
                setattr(existing, key, value)
            existing.updated_at = now
            session.commit()
            session.refresh(existing)
            return existing, False

    def list_outcomes(
        self,
        *,
        signal_id: int | None = None,
        horizon: str | None = None,
        engine_version: str | None = None,
        eval_status: str | None = None,
        outcome: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[DecisionSignalOutcomeRecord], int]:
        safe_page = max(1, int(page))
        safe_page_size = max(1, min(int(page_size), 100))
        conditions = []
        if signal_id is not None:
            conditions.append(DecisionSignalOutcomeRecord.signal_id == signal_id)
        if horizon:
            conditions.append(DecisionSignalOutcomeRecord.horizon == horizon)
        if engine_version:
            conditions.append(DecisionSignalOutcomeRecord.engine_version == engine_version)
        if eval_status:
            conditions.append(DecisionSignalOutcomeRecord.eval_status == eval_status)
        if outcome:
            conditions.append(DecisionSignalOutcomeRecord.outcome == outcome)
        where_clause = and_(*conditions) if conditions else True
        offset = (safe_page - 1) * safe_page_size
        with self.db.get_session() as session:
            total = session.execute(
                select(func.count(DecisionSignalOutcomeRecord.id))
                .select_from(DecisionSignalOutcomeRecord)
                .where(where_clause)
            ).scalar() or 0
            rows = session.execute(
                select(DecisionSignalOutcomeRecord)
                .where(where_clause)
                .order_by(desc(DecisionSignalOutcomeRecord.updated_at), desc(DecisionSignalOutcomeRecord.id))
                .offset(offset)
                .limit(safe_page_size)
            ).scalars().all()
            return list(rows), int(total)

    def list_stats_rows(
        self,
        *,
        engine_version: str,
        horizons: list[str] | None = None,
        statuses: list[str] | None = None,
    ) -> list[DecisionSignalOutcomeRecord]:
        conditions = [DecisionSignalOutcomeRecord.engine_version == engine_version]
        if horizons:
            conditions.append(DecisionSignalOutcomeRecord.horizon.in_(horizons))
        if statuses:
            conditions.append(DecisionSignalRecord.status.in_(statuses))
        with self.db.get_session() as session:
            rows = session.execute(
                select(DecisionSignalOutcomeRecord)
                .join(DecisionSignalRecord, DecisionSignalRecord.id == DecisionSignalOutcomeRecord.signal_id)
                .where(and_(*conditions))
            ).scalars().all()
            return list(rows)

    def get_feedback(self, *, signal_id: int) -> DecisionSignalFeedbackRecord | None:
        with self.db.get_session() as session:
            return session.execute(
                select(DecisionSignalFeedbackRecord)
                .where(DecisionSignalFeedbackRecord.signal_id == signal_id)
                .limit(1)
            ).scalar_one_or_none()

    def upsert_feedback(self, fields: dict[str, Any]) -> DecisionSignalFeedbackRecord:
        now = utc_naive_now()
        with self.db.get_session() as session:
            existing = session.execute(
                select(DecisionSignalFeedbackRecord)
                .where(DecisionSignalFeedbackRecord.signal_id == fields["signal_id"])
                .limit(1)
            ).scalar_one_or_none()
            if existing is None:
                row = DecisionSignalFeedbackRecord(**fields)
                session.add(row)
                session.commit()
                session.refresh(row)
                return row

            for key, value in fields.items():
                if key in {"id", "created_at"}:
                    continue
                setattr(existing, key, value)
            existing.updated_at = now
            session.commit()
            session.refresh(existing)
            return existing
