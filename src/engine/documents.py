"""Bounded PDF/DOCX extraction with portable Python dependencies."""

from __future__ import annotations

import base64
import binascii
import io
import zipfile
from xml.etree import ElementTree

from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_BYTES = 10 * 1024 * 1024
MAX_TEXT = 200_000


def extract_document(payload: dict) -> str:
    kind = payload.get("extension")
    encoded = payload.get("data")
    if kind not in ("pdf", "docx") or not isinstance(encoded, str):
        raise ValueError("Use um ficheiro PDF ou DOCX.")
    try:
        content = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Ficheiro inválido.") from exc
    if not content or len(content) > MAX_BYTES:
        raise ValueError("O ficheiro deve ter até 10 MB.")
    if kind == "docx":
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                info = archive.getinfo("word/document.xml")
                if info.file_size > MAX_BYTES:
                    raise ValueError("Documento demasiado extenso.")
                xml = archive.read(info)
                if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
                    raise ValueError("Documento inválido.")
                root = ElementTree.fromstring(xml)
                ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
                text = "\n".join("".join(p.itertext()) for p in root.iter(ns + "p"))
        except (zipfile.BadZipFile, KeyError, ElementTree.ParseError) as exc:
            raise ValueError("DOCX inválido.") from exc
    else:
        if not content.startswith(b"%PDF-"):
            raise ValueError("PDF inválido.")
        try:
            reader = PdfReader(io.BytesIO(content))
            if reader.is_encrypted or len(reader.pages) > 100:
                raise ValueError("Use um PDF sem palavra-passe e até 100 páginas.")
            parts = []
            length = 0
            for page in reader.pages:
                stream = page.get_contents()
                if stream is not None and len(stream.get_data()) > MAX_BYTES:
                    raise ValueError("Página demasiado extensa.")
                part = page.extract_text(extraction_mode="layout") or ""
                length += len(part)
                if length > MAX_TEXT:
                    raise ValueError("Documento demasiado extenso.")
                parts.append(part)
            text = "\n".join(parts)
        except (PdfReadError, OSError, KeyError, RecursionError) as exc:
            raise ValueError("Não foi possível ler o PDF. Cole o texto do CV.") from exc
    text = text.strip()
    if not text:
        raise ValueError("O documento não contém texto extraível. Cole o texto do CV.")
    if len(text) > MAX_TEXT:
        raise ValueError("Documento demasiado extenso.")
    return text


def export_docx(text: str) -> bytes:
    """Render the approved text into a portable Word document without reusing a stale PDF."""
    from xml.sax.saxutils import escape

    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
        raise ValueError("Conteúdo do CV inválido.")
    if any(ord(char) < 32 and char not in "\n\r\t" for char in text):
        raise ValueError("O texto contém caracteres de controlo inválidos.")
    paragraphs = "".join(
        '<w:p><w:r><w:t xml:space="preserve">' + escape(line) + "</w:t></w:r></w:p>"
        for line in text.split("\n")
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>" + paragraphs + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/>'
        "</w:sectPr></w:body></w:document>"
    )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        )
        archive.writestr("word/document.xml", document)
    return output.getvalue()
