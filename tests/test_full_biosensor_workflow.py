from examples.full_biosensor_workflow import generate_biosensor_replicates


def test_generate_biosensor_replicates_has_expected_structure():
    df = generate_biosensor_replicates()

    assert list(df.columns) == [
        "sample_id",
        "concentration",
        "replicate",
        "signal",
    ]

    assert len(df) == 18
    assert set(df["concentration"]) == {0.0, 1.0, 5.0, 10.0, 20.0, 50.0}
    assert set(df["replicate"]) == {1, 2, 3}


def test_generate_biosensor_replicates_signal_increases_with_concentration():
    df = generate_biosensor_replicates()

    mean_by_concentration = (
        df.groupby("concentration")["signal"]
        .mean()
        .sort_index()
    )

    assert mean_by_concentration.loc[50.0] > mean_by_concentration.loc[0.0]
    assert mean_by_concentration.loc[20.0] > mean_by_concentration.loc[1.0]