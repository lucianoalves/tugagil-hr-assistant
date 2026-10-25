import base64
import io
import unittest
import zipfile

from src.api.server import validate_payload
from src.engine.documents import extract_document


def docx_payload(xml):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", xml)
    return {"extension": "docx", "data": base64.b64encode(output.getvalue()).decode()}


class DocumentsTest(unittest.TestCase):
    def test_docx_preserves_paragraphs(self):
        payload = docx_payload(
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Experiência</w:t></w:r></w:p><w:p><w:r><w:t>Python e SQL</w:t></w:r></w:p></w:body></w:document>'
        )
        self.assertEqual(extract_document(payload), "Experiência\nPython e SQL")

    def test_invalid_archive_and_xml_are_rejected(self):
        for payload in [
            {"extension": "docx", "data": base64.b64encode(b"not a zip").decode()},
            docx_payload("<bad>"),
            docx_payload("<!DOCTYPE test><test/>"),
            {"extension": "docx", "data": "not base64"},
        ]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                extract_document(payload)

    def test_empty_document_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_document(docx_payload("<document/>"))

    def test_zip_expansion_is_bounded(self):
        with self.assertRaises(ValueError):
            extract_document(docx_payload("a" * (10 * 1024 * 1024 + 1)))

    def test_invalid_pdf_explains_text_fallback(self):
        with self.assertRaisesRegex(ValueError, "Cole o texto"):
            extract_document({"extension": "pdf", "data": base64.b64encode(b"%PDF-1.7").decode()})

    def test_structured_feedback_contract(self):
        result, status = validate_payload({"cv_text": "Summary Python SQL experience 2023"})
        self.assertEqual(status, 200)
        self.assertEqual(result["analysis_method"], "rules")
        self.assertGreaterEqual(len(result["feedback_items"]), 3)
        for item in result["feedback_items"]:
            self.assertIn(item["type"], ["content", "formatting", "completeness", "relevance"])
            self.assertIn(item["priority"], ["critical", "important", "suggestion"])
            self.assertTrue(item["description"])
