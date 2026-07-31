import numpy as np
import pytest

from cost_benefit import (
    compute_social_benefits, compute_investment_cost, compute_cost_benefit,
    LINE_LENGTHS, DISCOUNT_RATE, YEARS, PENUSD,
)


def test_benefit_components_sum_to_total():
    b = compute_social_benefits(metro_pax=500_000, train_pax=50_000, scenario_label="test")
    parts = (b["annual_time"] + b["annual_accidents"]
             + b["annual_co2"] + b["annual_fuel"] + b["annual_bus_ops"])
    assert b["annual_total"] == parts


def test_npv_matches_annual_total_geometric_series():
    b = compute_social_benefits(metro_pax=500_000, train_pax=50_000, scenario_label="test")
    expected = sum(b["annual_total"] / (1 + DISCOUNT_RATE) ** t for t in range(1, YEARS + 1))
    assert b["npv_benefit_30yr"] == pytest.approx(expected)


def test_investment_cost_total_matches_per_line_breakdown():
    total, inv_df = compute_investment_cost()
    assert total == pytest.approx(inv_df["cost_SOLES_M"].sum() * 1e6)


def test_train_lines_use_lower_unit_cost():
    _, inv_df = compute_investment_cost()
    tren = inv_df[inv_df["line"].str.startswith("TREN")]["cost_USD_M"].iloc[0]
    metro = inv_df[~inv_df["line"].str.startswith("TREN")]["cost_USD_M"].iloc[0]
    assert tren / LINE_LENGTHS[inv_df.loc[inv_df["line"].str.startswith("TREN").idxmax(), "line"]] == 50
    assert metro / 35 == 150


def test_bc_ratio_below_one_when_benefits_do_not_cover_costs():
    b = compute_social_benefits(metro_pax=100_000, train_pax=10_000, scenario_label="test")
    total_inv, _ = compute_investment_cost()
    cb = compute_cost_benefit(b, total_inv, "test")
    assert cb["bc_ratio"] < 1.0
