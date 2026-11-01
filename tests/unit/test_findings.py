import base64
import unittest

from src.api.server import validate_payload
from src.engine.documents import export_docx, extract_document
from src.engine.findings import build_findings


class FindingsTest(unittest.TestCase):
    def test_difference_has_verbatim_evidence_and_specific_adjustment_targets(self):
        cv = "Resumo\nExperiência\nSoftware Engineer — Acme, 2019–2022\nCompetências\nPython, SQL"
        li = "Sobre\nExperiência\nSoftware Engineer — Acme, 2020–2022\nCompetências\nPython, Java"
        items = build_findings(cv, li)
        dates = next(f for f in items if f["rule_id"] == "compare.dates")
        self.assertEqual(dates["message_params"], {"only_cv": ["2019"], "only_linkedin": ["2020"]})
        self.assertIn("2019", dates["description"])
        self.assertIn("2020", dates["description"])
        self.assertIn("não confirma uma contradição", dates["description"])
        self.assertEqual({e["source"] for e in dates["evidence"]}, {"cv", "linkedin"})
        skills = next(f for f in items if f["rule_id"] == "compare.skills")
        self.assertIn("sql", skills["description"])
        self.assertIn("java", skills["description"])
        self.assertTrue(
            any(
                a["source"] == "linkedin" and a["section"] == "Competências"
                for a in skills["actions"]
            )
        )
        for item in items:
            self.assertTrue(item["evidence"])
            for e in item["evidence"]:
                text = cv if e["source"] == "cv" else li
                if e["quote"] is not None:
                    self.assertEqual(text[e["start"] : e["end"]], e["quote"])
                    self.assertEqual(text.count("\n", 0, e["start"]) + 1, e["line"])

    def test_api_preserves_original_quote_offsets_with_leading_whitespace(self):
        text = "\n\n   Experiência\nDesenvolvi APIs para 200 clientes."
        result, _ = validate_payload({"cv_text": text})
        for item in result["feedback_items"]:
            for evidence in item["evidence"]:
                if evidence["quote"] is not None:
                    self.assertEqual(text[evidence["start"] : evidence["end"]], evidence["quote"])

    def test_missing_linkedin_is_not_an_inconsistency_or_score_penalty(self):
        result, _ = validate_payload(
            {"cv_text": "Experiência\nDesenvolvi APIs em 2023.\nCompetências\nPython SQL"}
        )
        self.assertFalse(any(f["finding_kind"] == "difference" for f in result["feedback_items"]))
        self.assertFalse(result["score"]["modules"]["consistency"]["assessed"])
        self.assertIsNone(result["score"]["modules"]["linkedin_quality"]["overall"])
        self.assertEqual(
            result["score"]["overall"], result["score"]["modules"]["cv_quality"]["overall"]
        )
        self.assertEqual(result["score"]["weights"]["effective_values"]["cv_quality"], 1)

    def test_identical_documents_do_not_raise_differences(self):
        text = "Experiência\nSoftware Engineer 2020–2024\nCompetências\nPython SQL"
        self.assertFalse(any(f["finding_kind"] == "difference" for f in build_findings(text, text)))

    def test_absence_is_explicit_and_quotes_are_not_invented(self):
        item = next(f for f in build_findings("Python", "") if f["rule_id"] == "cv.sections")
        self.assertTrue(all(e["quote"] is None for e in item["evidence"]))
        self.assertEqual(item["evidence"][0]["searched_characters"], 6)
        self.assertIn("outro título", item["recommendation"])

    def test_years_do_not_count_as_impact_metrics(self):
        item = next(
            f for f in build_findings("Desenvolvi APIs em 2023.", "") if f["rule_id"] == "cv.impact"
        )
        self.assertEqual(item["finding_kind"], "missing")
        self.assertEqual(item["evidence"][0]["quote"], "Desenvolvi APIs em 2023.")
        item = next(
            f
            for f in build_findings("Reduzi a latência em 30%.", "")
            if f["rule_id"] == "cv.impact"
        )
        self.assertEqual(item["finding_kind"], "observation")
        self.assertIn("30%", item["description"])
        self.assertEqual(item["message_params"]["metrics"], ["30%"])

    def test_linkedin_sections_do_not_fill_missing_cv_sections(self):
        result, _ = validate_payload(
            {"cv_text": "Python", "linkedin_text": "Summary Experience Education Skills"}
        )
        self.assertEqual(result["score"]["modules"]["cv_quality"]["dimensions"]["section_core"], 0)

    def test_docx_export_contains_exact_approved_text(self):
        text = "João — Experiência\nReduzi latência em 30%.\nR&D <equipa> & SQL"
        data = export_docx(text)
        self.assertEqual(
            extract_document({"extension": "docx", "data": base64.b64encode(data).decode()}), text
        )

    def test_no_generic_score_based_feedback(self):
        result, _ = validate_payload({"cv_text": "Experiência\nPython 2023"})
        for item in result["feedback_items"]:
            self.assertIn("rule_id", item)
            self.assertTrue(item["evidence"])
            self.assertNotIn("Reforce a estrutura", item["description"])
