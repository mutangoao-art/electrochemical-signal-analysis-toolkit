from echem_signal_toolkit.simulation import (
    generate_simulated_amperometry,
    generate_simulated_cv,
)


def test_generate_simulated_cv_has_expected_columns():
    df = generate_simulated_cv(points_per_segment=50, random_seed=1)

    assert list(df.columns) == ["time_s", "potential_v", "current_a", "cycle"]
    assert len(df) == 100


def test_generate_simulated_cv_is_reproducible_with_seed():
    first = generate_simulated_cv(points_per_segment=20, random_seed=42)
    second = generate_simulated_cv(points_per_segment=20, random_seed=42)

    assert first["current_a"].equals(second["current_a"])

def test_generate_simulated_amperometry_has_expected_columns():
    df = generate_simulated_amperometry(
        run_time_s=10.0,
        sample_interval_s=1.0,
        channels=["i4", "i6"],
        random_seed=1,
    )

    assert list(df.columns) == ["time_s", "i4_a", "i6_a"]
    assert len(df) == 10


def test_generate_simulated_amperometry_is_reproducible_with_seed():
    first = generate_simulated_amperometry(random_seed=42)
    second = generate_simulated_amperometry(random_seed=42)

    assert first["i4_a"].equals(second["i4_a"])