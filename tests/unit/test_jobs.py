import unittest

from src.engine.jobs import analyze_job


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


if __name__ == "__main__":
    unittest.main()
