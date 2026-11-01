"""Evidence-first preparation for a member's own job application.

The rules engine is deliberately conservative. An absent phrase in a CV is
"not demonstrated", never proof that the person lacks the skill.
"""

from __future__ import annotations

import hashlib
import re

from src.engine.findings import excerpt

SKILLS = {
    "python": ("python",),
    "sql": ("sql",),
    "postgresql": ("postgresql", "postgres"),
    "javascript": ("javascript",),
    "java": ("java",),
    "typescript": ("typescript",),
    "react": ("react",),
    "aws": ("aws",),
    "azure": ("azure",),
    "docker": ("docker",),
    "kubernetes": ("kubernetes", "k8s"),
    "git": ("git",),
    "fastapi": ("fastapi",),
    "django": ("django",),
    "power bi": ("power bi",),
    "excel": ("excel",),
    "scrum": ("scrum",),
    "gestão de projetos": ("gestão de projetos", "project management"),
    "liderança": ("liderança", "leadership"),
}
REQUIRED = re.compile(
    r"\b(required|requirements?|must.have|essential|mandatory|obrigat[oó]ri[oa]s?|requisitos?|essenciais|necess[aá]ri[oa]s?)\b",
    re.I,
)
PREFERRED = re.compile(
    r"\b(preferred|nice.to.have|desirable|bonus|valued|desej[aá]ve[il]s?|valorizamos|preferenciais|diferencial)\b",
    re.I,
)
RESPONSIBILITY = re.compile(
    r"\b(responsibilities|you.will|responsabilidades|fun[cç][oõ]es|atividades)\b", re.I
)


def _phrase(text: str, aliases: tuple[str, ...]) -> re.Match | None:
    for alias in aliases:
        found = re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", text, re.I)
        if found:
            return found
    return None


def _kind(line: str, current: str) -> str:
    if PREFERRED.search(line):
        return "preferred"
    if REQUIRED.search(line):
        return "required"
    if RESPONSIBILITY.search(line):
        return "responsibility"
    return current


def analyze_job(cv_text: str, job_text: str) -> dict:
    if not isinstance(cv_text, str) or not isinstance(job_text, str):
        raise ValueError("CV e descrição da vaga devem ser texto")
    if not cv_text.strip() or not job_text.strip():
        raise ValueError("Envie o CV e a descrição da vaga")
    if len(cv_text) > 200_000 or len(job_text) > 100_000:
        raise ValueError("Documento demasiado extenso")

    requirements = []
    section = "unclear"
    seen = set()
    offset = 0
    for line in job_text.splitlines(keepends=True):
        section = _kind(line, section)
        found_skills = False
        for skill, aliases in SKILLS.items():
            found = _phrase(line, aliases)
            if not found or skill in seen:
                continue
            found_skills = True
            seen.add(skill)
            job_match = re.compile(re.escape(found.group()), re.I).search(
                job_text, offset, offset + len(line)
            )
            if job_match is None:
                continue
            cv_match = _phrase(cv_text, aliases)
            status = "demonstrated" if cv_match else "not_demonstrated"
            kind = section if section in ("required", "preferred") else "unclear"
            requirements.append(
                {
                    "key": skill,
                    "label": skill,
                    "kind": kind,
                    "status": status,
                    "job_evidence": excerpt("job", job_text, job_match),
                    "cv_evidence": excerpt(
                        "cv",
                        cv_text,
                        cv_match,
                        "Termo não encontrado; confirme se possui experiência descrita de outra forma."
                        if not cv_match
                        else "",
                    ),
                    "recommendation": (
                        "Confirme se esta experiência está demonstrada no contexto de uma função ou projeto."
                        if cv_match
                        else "Se possui esta competência, acrescente uma experiência verdadeira ao CV; se não, considere aprendizagem."
                    ),
                }
            )
        raw_line = line.strip().lstrip("-•* ").strip()
        heading = bool(re.fullmatch(r"[\w\sáàâãéêíóôõúç/]+:\s*", line.strip(), re.I))
        if (
            len(raw_line) >= 8
            and not heading
            and (
                section == "responsibility"
                or (section in ("required", "preferred") and not found_skills)
            )
        ):
            # Unknown requirements remain visible for human interpretation, without
            # pretending that a keyword search can assess them.
            key = "text:" + hashlib.sha256(raw_line.casefold().encode()).hexdigest()[:16]
            line_match = re.compile(re.escape(raw_line)).search(
                job_text, offset, offset + len(line)
            )
            if line_match:
                requirements.append(
                    {
                        "key": key,
                        "label": raw_line[:200],
                        "kind": section,
                        "status": "not_assessable",
                        "job_evidence": excerpt("job", job_text, line_match),
                        "cv_evidence": excerpt(
                            "cv",
                            cv_text,
                            None,
                            "Esta frase exige interpretação; nenhum paralelo foi confirmado automaticamente.",
                        ),
                        "recommendation": "Confirme com o associado ou mentor qual experiência demonstra este requisito.",
                    }
                )
        offset += len(line)
    return {
        "analysis_method": "rules",
        "requirements": requirements,
        "coverage": {
            "demonstrated": sum(r["status"] == "demonstrated" for r in requirements),
            "not_demonstrated": sum(r["status"] == "not_demonstrated" for r in requirements),
            "unclear_requirements": sum(r["kind"] == "unclear" for r in requirements),
            "not_assessable": sum(r["status"] == "not_assessable" for r in requirements),
        },
        "limitations": [
            "A ausência de texto no CV não demonstra ausência da competência.",
            "Esta análise por regras reconhece um vocabulário limitado e não interpreta experiência equivalente.",
        ],
    }
