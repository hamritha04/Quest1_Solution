from src.search import similarity


def test_exact_match():
    score = similarity(
        "My mind rebels at stagnation",
        "My mind rebels at stagnation",
    )

    assert score == 100.0


def test_case_insensitive_match():
    score = similarity(
        "My mind rebels at stagnation",
        "MY MIND REBELS AT STAGNATION",
    )

    assert score == 100.0


def test_punctuation_difference():
    score = similarity(
        "My mind rebels at stagnation",
        "My mind rebels at stagnation.",
    )

    assert score >= 95.0


def test_asr_variation():
    score = similarity(
        "My mind rebels at stagnation",
        "My mind rebelled. It's stagnation.",
    )

    assert score > 70.0


def test_unrelated_sentence():
    score = similarity(
        "My mind rebels at stagnation",
        "The weather is beautiful today",
    )

    assert score < 70.0