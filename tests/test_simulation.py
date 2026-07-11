from echem_signal_toolkit.simulation import generate_simulated_cv


def test_generate_simulated_cv_has_expected_columns():
    df = generate_simulated_cv(points_per_segment=50, random_seed=1)

    assert list(df.columns) == ["time_s", "potential_v", "current_a", "cycle"]
    assert len(df) == 100


def test_generate_simulated_cv_is_reproducible_with_seed():
    first = generate_simulated_cv(points_per_segment=20, random_seed=42)
    second = generate_simulated_cv(points_per_segment=20, random_seed=42)

    assert first["current_a"].equals(second["current_a"])