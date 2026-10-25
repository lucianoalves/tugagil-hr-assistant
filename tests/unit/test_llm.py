import json
import unittest

from src.engine.llm import ScriptedProvider, analyze_with_provider


class LLMContractTest(unittest.TestCase):
    def test_job_evidence_and_published_resource(self):
        source = {"cv_text": "Trabalhei com Python.", "job_text": "Exige Python e SQL."}
        item = {
            "label": "Python",
            "kind": "required",
            "status": "demonstrated",
            "job_quote": "Python",
            "cv_quote": "Python",
            "resource_ids": ["published"],
            "explanation": "O mesmo termo aparece nas duas fontes.",
        }
        provider = ScriptedProvider([json.dumps({"requirements": [item]})])
        result = analyze_with_provider(provider, "job", source, resource_ids={"published"})
        self.assertEqual(result["requirements"][0]["job_quote"], "Python")
        self.assertEqual(len(provider.calls), 1)

    def test_rejects_invented_evidence_and_resource(self):
        source = {"cv_text": "Experiência Python", "job_text": "Requer SQL"}
        item = {
            "label": "SQL",
            "kind": "required",
            "status": "demonstrated",
            "job_quote": "SQL",
            "cv_quote": "SQL",
            "resource_ids": ["unknown"],
        }
        with self.assertRaisesRegex(ValueError, "Nenhum requisito"):
            analyze_with_provider(
                ScriptedProvider([json.dumps({"requirements": [item]})]),
                "job",
                source,
                resource_ids=set(),
            )

    def test_comparison_requires_both_quotes_for_difference(self):
        source = {"cv_text": "Python", "linkedin_text": "SQL"}
        item = {
            "kind": "difference",
            "cv_quote": "Python",
            "linkedin_quote": None,
            "explanation": "Divergência",
        }
        with self.assertRaisesRegex(ValueError, "Nenhuma comparação"):
            analyze_with_provider(
                ScriptedProvider([json.dumps({"findings": [item]})]), "cv_linkedin", source
            )


if __name__ == "__main__":
    unittest.main()
