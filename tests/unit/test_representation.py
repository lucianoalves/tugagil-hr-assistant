from src.engine.representation import evaluate_variant

CV = "Jane Doe\njane@example.invalid\nSoftware engineer with Python and SQL experience.\nExperience\nEngineer at Example 2020-2025\nEducation\nComputer science degree"
JOB = "Requirements: Python and SQL experience required."


def test_identical_documents_have_no_degradation():
    result = evaluate_variant(CV, CV, CV, JOB)
    assert result["no_score_drop"]
    assert result["facts_supported"]
    assert result["passed"]
    assert result["baseline"] == result["variant"]


def test_invented_claim_cannot_be_approved_by_better_score():
    result = evaluate_variant(CV, CV + "\nLed 500 employees and grew revenue by 90%.", CV, JOB)
    assert not result["facts_supported"]
    assert not result["passed"]
    assert result["unsupported_lines"]


def test_removing_demonstrated_requirements_blocks_delivery():
    result = evaluate_variant(CV, CV.replace("Python and SQL", "engineering"), CV, JOB)
    assert not result["no_score_drop"]
    assert not result["passed"]


def test_unassessable_job_is_not_reported_as_passed():
    result = evaluate_variant(
        CV, CV, CV, "Seeking an experienced professional for an unspecified role."
    )
    assert not result["comparable"]
    assert not result["passed"]
