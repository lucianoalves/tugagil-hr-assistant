import json

import pytest

from src.ai.service import analyze

CV = "Example Person\nExperience: Python engineer since 2020\nReduced latency by 20%"
LINKEDIN = "Example Person\nExperience: Python engineer since 2021"


class FakeProvider:
    def __init__(self, result):
        self.result = result
        self.sources = None

    def complete(self, model, operation, sources):
        self.sources = sources
        return json.dumps(self.result), 20, 10


def finding(**overrides):
    return {
        "kind": "difference",
        "title": "Confirmar datas",
        "explanation": "As fontes indicam anos diferentes.",
        "recommendation": "Confirma e corrige o ano.",
        "cv_ids": ["cv:2"],
        "linkedin_ids": ["linkedin:2"],
        "linkedin_section": "Experiência",
        **overrides,
    }


def test_verified_references_use_original_quotes():
    result, input_tokens, output_tokens = analyze(
        FakeProvider({"findings": [finding()]}), "fake", "cv_ai", CV, LINKEDIN
    )
    evidence = result["findings"][0]["evidence"]
    assert evidence[0]["quote"] == CV.splitlines()[1]
    assert CV[evidence[0]["start"] : evidence[0]["end"]] == evidence[0]["quote"]
    assert (input_tokens, output_tokens) == (20, 10)


@pytest.mark.parametrize(
    "overrides", [{"cv_ids": ["cv:99"]}, {"linkedin_ids": []}, {"cv_ids": ["linkedin:2"]}]
)
def test_unverifiable_differences_are_rejected(overrides):
    with pytest.raises(ValueError):
        analyze(FakeProvider({"findings": [finding(**overrides)]}), "fake", "cv_ai", CV, LINKEDIN)


def test_rewrite_cannot_invent_metrics_and_preserves_source():
    edit = {
        "source_id": "cv:3",
        "replacement": "Reduced latency by 80%",
        "reason": "Improve wording",
    }
    with pytest.raises(ValueError):
        analyze(FakeProvider({"edits": [edit]}), "fake", "rewrite", CV)
    edit["replacement"] = "Achieved a 20% reduction in latency"
    result, _, _ = analyze(FakeProvider({"edits": [edit]}), "fake", "rewrite", CV)
    assert result["proposed_text"].startswith(
        "Example Person\nExperience: Python engineer since 2020\n"
    )
    assert result["edits"][0]["before"] == "Reduced latency by 20%"


def test_rewrite_does_not_pass_ui_locale_as_translation_target():
    provider = FakeProvider(
        {
            "edits": [
                {
                    "source_id": "cv:3",
                    "replacement": "Achieved a 20% reduction in latency",
                    "reason": "Melhorar clareza",
                }
            ]
        }
    )
    analyze(provider, "fake", "rewrite", CV, request={"locale": "pt"})
    assert provider.sources["locale"] == "pt"
    assert provider.sources.get("target_language") is None
    assert provider.sources.get("document_language") == "preserve"


def test_rewrite_rejects_language_flip_from_english_to_portuguese():
    edit = {
        "source_id": "cv:2",
        "replacement": "Experiência: engenheiro Python desde 2020 com formação sólida",
        "reason": "Traduzir para português",
    }
    with pytest.raises(ValueError, match="idioma"):
        analyze(FakeProvider({"edits": [edit]}), "fake", "rewrite", CV, request={"locale": "pt"})


def test_plan_requires_confirmed_gaps_and_published_resources():
    step = {
        "title": "Study SQL",
        "job_ids": ["job:1"],
        "resource_ids": ["unknown"],
        "reason": "Requirement",
    }
    provider = FakeProvider({"steps": [step]})
    with pytest.raises(ValueError):
        analyze(provider, "fake", "learning_plan", CV, job_text="SQL is required")
    with pytest.raises(ValueError):
        analyze(
            provider,
            "fake",
            "learning_plan",
            CV,
            job_text="SQL is required",
            confirmed_gaps=[{"key": "sql"}],
        )


def test_contacts_are_not_sent_to_provider():
    provider = FakeProvider(
        {"edits": [{"source_id": "cv:3", "replacement": "Python developer", "reason": "Clarity"}]}
    )
    analyze(
        provider,
        "fake",
        "rewrite",
        "Example Person\nContact example@example.invalid\nPython engineer",
    )
    assert "example@example.invalid" not in json.dumps(provider.sources)


def test_assistant_resolves_only_verified_source_ids_and_locale():
    provider = FakeProvider({"answer": "Clarify this experience.", "answer_ids": ["cv:2"]})
    result, _, _ = analyze(
        provider,
        "fake",
        "ask_ai",
        CV,
        request={"locale": "en", "question": "What should I change?"},
    )
    assert result["evidence"][0]["quote"] == CV.splitlines()[1]
    assert provider.sources["locale"] == "en"
    with pytest.raises(ValueError):
        analyze(
            FakeProvider({"answer": "Invented", "answer_ids": ["cv:999"]}),
            "fake",
            "ask_ai",
            CV,
            request={"question": "Explain"},
        )


def test_translation_covers_every_eligible_block_preserving_contacts_and_numbers():
    text = "Example Person\nEmail example@example.invalid\nPython engineer since 2020\nReduced latency by 20%"
    edits = [
        {"source_id": "cv:3", "replacement": "Engenharia Python desde 2020", "reason": "Translate"},
        {"source_id": "cv:4", "replacement": "Reduziu a latência em 20%", "reason": "Translate"},
    ]
    result, _, _ = analyze(
        FakeProvider({"edits": edits}), "fake", "translate", text, request={"target_language": "pt"}
    )
    assert "example@example.invalid" in result["proposed_text"]
    assert result["proposed_text"].startswith("Example Person\n")
    assert "2020" in result["proposed_text"] and "20%" in result["proposed_text"]
    with pytest.raises(ValueError, match="incompleta"):
        analyze(
            FakeProvider({"edits": edits[:1]}),
            "fake",
            "translate",
            text,
            request={"target_language": "pt"},
        )
    edits[1]["replacement"] = "Reduziu a latência em 80%"
    with pytest.raises(ValueError):
        analyze(
            FakeProvider({"edits": edits}),
            "fake",
            "translate",
            text,
            request={"target_language": "pt"},
        )


def test_evidence_translation_keeps_the_original_quote():
    provider = FakeProvider(
        {
            "answer": "Confirma a experiência",
            "answer_ids": ["cv:2"],
            "evidence_translations": [
                {"source_id": "cv:2", "text": "Engenharia Python desde 2020"}
            ],
        }
    )
    result, _, _ = analyze(provider, "fake", "ask_ai", CV, request={"question": "Explica"})
    assert result["evidence"][0]["quote"] == CV.splitlines()[1]
    assert result["evidence"][0]["translated_quote"] == "Engenharia Python desde 2020"
