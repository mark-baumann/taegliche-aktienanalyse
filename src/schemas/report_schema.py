"""
===================================
Report Engine - Pydantic Schema
===================================

Defines AnalysisReportSchema for validating LLM JSON output.
Aligns with SYSTEM_PROMPT in src/analyzer.py.
Uses Optional for lenient parsing; business-layer integrity checks are separate.
"""

import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PositionAdvice(BaseModel):
    """Position advice for no-position vs has-position."""

    no_position: str | None = None
    has_position: str | None = None


class CoreConclusion(BaseModel):
    """Core conclusion block."""

    one_sentence: str | None = None
    signal_type: str | None = None
    time_sensitivity: str | None = None
    position_advice: PositionAdvice | None = None


class TrendStatus(BaseModel):
    """Trend status."""

    ma_alignment: str | None = None
    is_bullish: bool | None = None
    trend_score: int | float | str | None = None


class PricePosition(BaseModel):
    """Price position (may contain N/A strings)."""

    current_price: int | float | str | None = None
    ma5: int | float | str | None = None
    ma10: int | float | str | None = None
    ma20: int | float | str | None = None
    bias_ma5: int | float | str | None = None
    bias_status: str | None = None
    support_level: int | float | str | None = None
    resistance_level: int | float | str | None = None


class VolumeAnalysis(BaseModel):
    """Volume analysis."""

    volume_ratio: int | float | str | None = None
    volume_status: str | None = None
    turnover_rate: int | float | str | None = None
    volume_meaning: str | None = None


class ChipStructure(BaseModel):
    """Chip structure."""

    profit_ratio: int | float | str | None = None
    avg_cost: int | float | str | None = None
    concentration: int | float | str | None = None
    chip_health: str | None = None


class DataPerspective(BaseModel):
    """Data perspective block."""

    trend_status: TrendStatus | None = None
    price_position: PricePosition | None = None
    volume_analysis: VolumeAnalysis | None = None
    chip_structure: ChipStructure | None = None


class Intelligence(BaseModel):
    """Intelligence block."""

    latest_news: str | None = None
    risk_alerts: list[str] | None = None
    positive_catalysts: list[str] | None = None
    earnings_outlook: str | None = None
    sentiment_summary: str | None = None


class SniperPoints(BaseModel):
    """Sniper points (ideal_buy, stop_loss, etc.)."""

    ideal_buy: str | int | float | None = None
    secondary_buy: str | int | float | None = None
    stop_loss: str | int | float | None = None
    take_profit: str | int | float | None = None


class PositionStrategy(BaseModel):
    """Position strategy."""

    suggested_position: str | None = None
    entry_plan: str | None = None
    risk_control: str | None = None


class BattlePlan(BaseModel):
    """Battle plan block."""

    sniper_points: SniperPoints | None = None
    position_strategy: PositionStrategy | None = None
    action_checklist: list[str] | None = None


class PhaseDecision(BaseModel):
    """Market-phase-aware intraday decision guardrail output."""

    phase_context: dict[str, Any] | None = None
    action_window: str | None = None
    immediate_action: str | None = None
    watch_conditions: list[str] = Field(default_factory=list)
    next_check_time: str | None = None
    confidence_reason: str | None = None
    data_limitations: list[str] = Field(default_factory=list)


class SignalAttribution(BaseModel):
    """Signal attribution analysis - explains what factors contributed most to the recommendation."""

    technical_indicators: int | float | str | None = None
    news_sentiment: int | float | str | None = None
    fundamentals: int | float | str | None = None
    market_conditions: int | float | str | None = None
    strongest_bullish_signal: str | None = None
    strongest_bearish_signal: str | None = None

    @model_validator(mode='after')
    def validate_and_normalize_contributions(self) -> 'SignalAttribution':
        """Validate and normalize contribution weights.

        - Try to convert string values to numbers
        - Clamp values to 0-100
        - Normalize non-zero sum to 100 if all four values are valid numbers
        - Preserve all-zero as "no effective signal"
        - Set invalid values to None
        """
        contrib_fields = ['technical_indicators', 'news_sentiment', 'fundamentals', 'market_conditions']
        values = {}

        for field in contrib_fields:
            val = getattr(self, field)
            if val is None:
                values[field] = None
                continue

            # Try to convert string to number
            if isinstance(val, str):
                # Handle "N/A", "null", etc.
                if val.strip().upper() in ('N/A', 'NULL', 'NONE', ''):
                    values[field] = None
                    continue
                # Handle "70%" or "70"
                try:
                    # Remove % sign and convert
                    cleaned = val.replace('%', '').strip()
                    val = float(cleaned)
                except (ValueError, AttributeError):
                    values[field] = None
                    continue

            # Ensure it's a number
            try:
                val = float(val)
            except (TypeError, ValueError):
                values[field] = None
                continue

            if not math.isfinite(val):
                values[field] = None
                continue

            # Clamp to 0-100
            val = max(val, 0)
            val = min(val, 100)

            values[field] = val

        # Normalize to sum = 100 if all values are valid and non-zero
        valid_values = {k: v for k, v in values.items() if v is not None}
        if len(valid_values) == 4:
            total = sum(valid_values.values())
            if total > 0:
                # Normalize non-zero sum to 100
                for field in contrib_fields:
                    if values[field] is not None:
                        values[field] = round(values[field] * 100 / total)

                # Adjust rounding errors to keep non-zero sums at 100
                final_sum = sum(values[f] for f in contrib_fields)
                if final_sum != 100:
                    # Add/subtract the difference to/from the first non-zero value
                    diff = 100 - final_sum
                    for field in contrib_fields:
                        if values[field] > 0:
                            values[field] += diff
                            break

        # Update the model fields
        for field in contrib_fields:
            setattr(self, field, values[field])

        return self


class Dashboard(BaseModel):
    """Dashboard block."""

    core_conclusion: CoreConclusion | None = None
    data_perspective: DataPerspective | None = None
    intelligence: Intelligence | None = None
    battle_plan: BattlePlan | None = None
    phase_decision: PhaseDecision | None = None
    signal_attribution: SignalAttribution | None = None


class AnalysisReportSchema(BaseModel):
    """
    Top-level schema for LLM report JSON.
    Aligns with SYSTEM_PROMPT output format.
    """

    model_config = ConfigDict(extra="allow")  # Allow extra fields from LLM

    stock_name: str | None = None
    sentiment_score: int | None = Field(None, ge=0, le=100)
    trend_prediction: str | None = None
    operation_advice: str | None = None
    decision_type: str | None = None
    confidence_level: str | None = None

    dashboard: Dashboard | None = None

    analysis_summary: str | None = None
    key_points: str | None = None
    risk_warning: str | None = None
    buy_reason: str | None = None

    trend_analysis: str | None = None
    short_term_outlook: str | None = None
    medium_term_outlook: str | None = None
    technical_analysis: str | None = None
    ma_analysis: str | None = None
    volume_analysis: str | None = None
    pattern_analysis: str | None = None
    fundamental_analysis: str | None = None
    sector_position: str | None = None
    company_highlights: str | None = None
    news_summary: str | None = None
    market_sentiment: str | None = None
    hot_topics: str | None = None

    search_performed: bool | None = None
    data_sources: str | None = None
