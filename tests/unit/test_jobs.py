import unittest

from src.engine.jobs import analyze_job, score_job_application


class JobAnalysisTest(unittest.TestCase):
    def test_portuguese_requirements_and_verbatim_evidence(self):
        cv = "Experiência\nImplementei serviços Python para clientes.\n"
        job = "Requisitos obrigatórios:\nPython\nValorizamos:\nSQL\n"
        result = analyze_job(cv, job)
        by_key = {item["key"]: item for item in result["requirements"]}
        self.assertEqual(by_key["python"]["kind"], "required")
        self.assertEqual(by_key["python"]["status"], "demonstrated")
        self.assertEqual(by_key["sql"]["kind"], "preferred")
        self.assertEqual(by_key["sql"]["status"], "not_demonstrated")
        self.assertIn("SQL", by_key["sql"]["job_evidence"]["quote"])
        self.assertEqual(by_key["sql"]["job_evidence"]["line"], 4)
        for item in result["requirements"]:
            for source, original in (("job_evidence", job), ("cv_evidence", cv)):
                evidence = item[source]
                if evidence["status"] == "found":
                    self.assertEqual(
                        original[evidence["start"] : evidence["end"]], evidence["quote"]
                    )

    def test_javascript_is_not_java(self):
        result = analyze_job("Experiência em JavaScript", "Required:\nJava\n")
        self.assertEqual(result["requirements"][0]["status"], "not_demonstrated")

    def test_unknown_skill_does_not_become_a_false_gap(self):
        result = analyze_job(
            "Experiência em aplicações de dados", "Required:\nCompetência especializada Zeta\n"
        )
        self.assertEqual(result["requirements"][0]["status"], "not_assessable")
        self.assertEqual(result["coverage"]["not_demonstrated"], 0)

    def test_score_job_application_returns_numeric_score(self):
        cv = (
            "Maria Silva\nmaria@example.com\nExperiência\n"
            "Desenvolvi APIs Python e SQL em equipas Scrum.\n"
            "Educação\nLicenciatura em Informática\n"
        )
        job = "Requisitos obrigatórios:\nPython\nSQL\n"
        result = score_job_application(cv, job, linkedin_text="")
        self.assertIn("score", result)
        self.assertIsInstance(result["score"]["overall"], float)
        self.assertGreaterEqual(result["score"]["overall"], 0)
        self.assertLessEqual(result["score"]["overall"], 100)
        self.assertEqual(result["score"]["modules"]["cv_quality"]["assessed"], True)
        self.assertEqual(result["score"]["job_fit"]["adapted_cv"], False)
        self.assertAlmostEqual(result["score"]["job_fit"]["coverage_ratio"], 1.0)

    def test_adapted_cv_changes_coverage_and_marks_source(self):
        original = "Experiência\nGestão de equipas e Excel.\n"
        adapted = "Experiência\nImplementei serviços Python e Docker.\n"
        job = "Requisitos obrigatórios:\nPython\nDocker\n"
        without = score_job_application(original, job, adapted=False)
        with_adapted = score_job_application(adapted, job, adapted=True)
        self.assertEqual(without["coverage"]["demonstrated"], 0)
        self.assertEqual(with_adapted["coverage"]["demonstrated"], 2)
        self.assertTrue(with_adapted["score"]["job_fit"]["adapted_cv"])
        self.assertGreater(
            with_adapted["score"]["overall"], without["score"]["overall"]
        )

    def test_missing_linkedin_does_not_break_job_score(self):
        result = score_job_application(
            "Ana\nana@example.com\nExperiência\nPython em produção.\n",
            "Required:\nPython\n",
            linkedin_text="",
        )
        self.assertTrue(result["score"]["modules"]["cv_quality"]["assessed"])
        self.assertFalse(result["score"]["modules"]["linkedin_quality"]["assessed"])


if __name__ == "__main__":
    unittest.main()
