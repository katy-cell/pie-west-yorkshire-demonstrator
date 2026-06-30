from pie_model import MODEL_VERSION, build_model


def test_model_uses_real_place_population_baseline() -> None:
    model = build_model()
    population = model["population"]

    assert MODEL_VERSION == "WY-PIE-3.0"
    assert set(population["place"]) == {
        "Bradford District and Craven",
        "Calderdale",
        "Kirklees",
        "Leeds",
        "Wakefield",
    }
    assert int(population["population"].sum()) == 2_435_236
    assert int(population.loc[population["place"] == "Leeds", "population"].iloc[0]) == 845_189


def test_modelled_work_items_are_opaque_and_forecast_is_non_uniform() -> None:
    model = build_model()
    forecast = model["forecast"]
    work_items = model["work_items"]

    assert work_items["pie_work_item"].str.startswith("PIE-").all()
    assert work_items["record_type"].eq("Modelled operational record").all()
    assert not work_items["pie_work_item"].str.contains("Margaret|Joseph|Aisha", case=False, regex=True).any()
    assert forecast["expected_30d"].gt(0).all()
    assert forecast.groupby("place")["expected_30d"].sum().nunique() == 5
    assert forecast["opportunities_per_10k"].nunique() > 4
