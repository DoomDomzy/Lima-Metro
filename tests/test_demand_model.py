import numpy as np
import pandas as pd
import pytest

from demand_model import (
    doubly_constrained_gravity, multinomial_logit_safe,
    compute_mode_utilities, compute_mode_shares, estimate_demand,
)


def _sample_matrix(n=6, rng=None):
    rng = rng or np.random.default_rng(0)
    m = rng.uniform(5, 90, size=(n, n))
    np.fill_diagonal(m, 0)
    return m


def test_multinomial_logit_safe_probs_sum_to_one():
    u = np.random.default_rng(1).uniform(-3, 3, size=(10, 4))
    p = multinomial_logit_safe(u)
    np.testing.assert_allclose(p.sum(axis=-1), 1.0, atol=1e-12)
    assert (p >= 0).all()


def test_gravity_balances_origins_and_destinations():
    rng = np.random.default_rng(42)
    n = 8
    O = rng.uniform(500, 2000, size=n)
    D = rng.uniform(500, 2000, size=n)
    cost = _sample_matrix(n, rng)

    T = doubly_constrained_gravity(O, D, cost, beta=0.02, max_iter=500, tol=1e-3)

    np.testing.assert_allclose(T.sum(axis=1), O / O.sum() * O.sum(), rtol=1e-3)
    np.testing.assert_allclose(T.sum(axis=0), D / D.sum() * O.sum(), rtol=1e-3)
    assert (T >= 0).all()


def test_gravity_is_deterministic():
    rng = np.random.default_rng(7)
    n = 8
    O = rng.uniform(500, 2000, size=n)
    D = rng.uniform(500, 2000, size=n)
    cost = _sample_matrix(n, rng)

    T1 = doubly_constrained_gravity(O, D, cost, beta=0.02)
    T2 = doubly_constrained_gravity(O, D, cost, beta=0.02)
    np.testing.assert_array_equal(T1, T2)


def test_train_never_reaches_zones_without_train_service():
    utilities = compute_mode_utilities(
        t_car=np.full((3, 3), 30.0),
        t_bus=np.full((3, 3), 50.0),
        t_metro=np.full((3, 3), 20.0),
        t_train=np.full((3, 3), np.inf),
    )
    assert np.isneginf(utilities["train"]).all()


def test_base_scenario_has_no_train_service():
    rng = np.random.default_rng(5)
    n = 6
    matrices = {
        "car": _sample_matrix(n, rng),
        "bus": _sample_matrix(n, rng) + 15,
        "metro_base": _sample_matrix(n, rng),
        "metro_full": _sample_matrix(n, rng) + 5,
        "train": np.where(_sample_matrix(n, rng) > 50, _sample_matrix(n, rng), np.inf),
    }
    trip_gen = pd.DataFrame({
        "trips_produced": rng.uniform(100, 500, n),
        "trips_attracted": rng.uniform(100, 500, n),
    })
    base = estimate_demand(matrices, trip_gen, scenario="base")
    full = estimate_demand(matrices, trip_gen, scenario="full")
    assert base["train_pax"] == 0, "En el escenario base los trenes no existen"
    assert full["train_pax"] > 0, "En la red completa sí hay tren"
    assert full["metro_pax"] > base["metro_pax"]


def test_estimate_demand_deterministic():
    rng = np.random.default_rng(3)
    n = 6
    matrices = {
        "car": _sample_matrix(n, rng),
        "bus": _sample_matrix(n, rng) + 15,
        "metro_base": _sample_matrix(n, rng),
        "metro_full": _sample_matrix(n, rng) + 5,
        "train": np.full((n, n), np.inf),
    }
    trip_gen = pd.DataFrame({
        "trips_produced": rng.uniform(100, 500, n),
        "trips_attracted": rng.uniform(100, 500, n),
    })

    r1 = estimate_demand(matrices, trip_gen, scenario="base")
    r2 = estimate_demand(matrices, trip_gen, scenario="base")
    assert r1["metro_pax"] == r2["metro_pax"]
    assert r1["train_pax"] == r2["train_pax"]
