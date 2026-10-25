"""Explainable observations from supplied text, with exact source excerpts.

Lexical differences are review prompts, never proof of conflicting employment facts.
No missing facts, employers, metrics or credentials are invented.
"""

from __future__ import annotations

import re

from .parser import ROLE_PATTERN, SECTION_PATTERNS, SKILL_PATTERN, YEAR_PATTERN

EVIDENCE_VERSION = 1
SECTION_NAMES = {
    "summary": "Resumo / Sobre",
    "experience": "Experiência",
    "education": "Formação",
    "skills": "Competências",
}
METRIC_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:%|por cento|percent|clientes|users|utilizadores|horas|hours|ms|milhões|million)\b|\b\d+(?:[.,]\d+)?\s*%",
    re.I,
)
RESULT_PATTERN = re.compile(
    r"\b(?:desenvolvi|implementei|liderei|melhorei|reduzi|aumentei|criei|desenvolvimento|implementação|responsável|developed|implemented|led|improved|reduced|increased|delivered|responsible)\b",
    re.I,
)


def excerpt(source: str, text: str, match: re.Match | None, note: str = "") -> dict:
    if match is None:
        return {
            "source": source,
            "status": "not_found" if text.strip() else "not_provided",
            "quote": None,
            "start": None,
            "end": None,
            "line": None,
            "note": note,
            "searched_characters": len(text),
        }
    start = max(text.rfind("\n", 0, match.start()) + 1, match.start() - 100)
    end_line = text.find("\n", match.end())
    end = min(len(text) if end_line < 0 else end_line, match.end() + 180)
    return {
        "source": source,
        "status": "found",
        "quote": text[start:end],
        "start": start,
        "end": end,
        "line": text.count("\n", 0, start) + 1,
        "note": note,
        "searched_characters": len(text),
    }


def action(source: str, section: str, instruction: str, suggested_text: str = "") -> dict:
    return {
        "source": source,
        "section": section,
        "instruction": instruction,
        "suggested_text": suggested_text,
        "requires_confirmation": True,
    }


def finding(
    rule: str,
    kind: str,
    description: str,
    recommendation: str,
    evidence: list[dict],
    actions: list[dict],
    category="content",
    message_params: dict | None = None,
) -> dict:
    return {
        "rule_id": rule,
        "message_params": message_params or {},
        "finding_kind": kind,
        "type": category,
        "priority": "important" if kind in ("difference", "missing") else "suggestion",
        "description": description,
        "recommendation": recommendation,
        "evidence": evidence,
        "actions": actions,
    }


def canonical(value: str) -> str:
    value = " ".join(value.lower().split())
    return {
        "postgresql": "postgres",
        "nodejs": "node.js",
        "nextjs": "next.js",
        "gestão de projetos": "project management",
        "liderança": "leadership",
    }.get(value, value)


def signals(pattern, text):
    result = {}
    for match in pattern.finditer(text):
        result.setdefault(canonical(match.group().strip()), match)
    return result


def build_findings(cv_text: str, linkedin_text: str) -> list[dict]:
    texts = {"cv": cv_text, "linkedin": linkedin_text}
    findings = []
    if cv_text.strip() and linkedin_text.strip():
        for name, pattern, section in [
            ("dates", YEAR_PATTERN, "Experiência / Formação"),
            ("roles", ROLE_PATTERN, "Experiência / Título profissional"),
            ("skills", SKILL_PATTERN, "Competências"),
        ]:
            left, right = signals(pattern, cv_text), signals(pattern, linkedin_text)
            only_cv, only_li = (
                sorted(left.keys() - right.keys()),
                sorted(right.keys() - left.keys()),
            )
            if not only_cv and not only_li:
                continue
            label = {"dates": "Anos", "roles": "Designações de função", "skills": "Competências"}[
                name
            ]
            cv_match = left.get(only_cv[0]) if only_cv else next(iter(left.values()), None)
            li_match = right.get(only_li[0]) if only_li else next(iter(right.values()), None)
            description = (
                f"{label} detetados apenas no CV: {', '.join(only_cv) or 'nenhum'}. "
                f"Apenas no LinkedIn: {', '.join(only_li) or 'nenhum'}. "
                "É uma diferença entre os textos enviados; não confirma uma contradição."
            )
            instruction = (
                (
                    "Confirme se os trechos se referem à mesma experiência e quais os dados corretos. "
                    "Atualize apenas a informação que confirmar; experiências diferentes podem ter datas e funções diferentes."
                )
                if name != "skills"
                else (
                    "Confirme quais destas competências pretende apresentar nos dois documentos. "
                    "Acrescente apenas competências que realmente possui; uma omissão não significa que o texto esteja errado."
                )
            )
            ev = []
            for source, text, values in [("cv", cv_text, left), ("linkedin", linkedin_text, right)]:
                grouped = {}
                for value, match in values.items():
                    evidence = excerpt(source, text, match, f"{label} reconhecido: {value}.")
                    key = (evidence["start"], evidence["end"])
                    if key in grouped:
                        grouped[key]["note"] += f" Também: {value}."
                    else:
                        grouped[key] = evidence
                ev.extend(grouped.values())
                if not grouped:
                    ev.append(
                        excerpt(
                            source,
                            text,
                            None,
                            f"Nenhum marcador de {label.lower()} foi reconhecido nesta fonte.",
                        )
                    )
            cv_quote = excerpt("cv", cv_text, cv_match)["quote"] or ""
            li_quote = excerpt("linkedin", linkedin_text, li_match)["quote"] or ""
            findings.append(
                finding(
                    f"compare.{name}",
                    "difference",
                    description,
                    instruction,
                    ev,
                    [
                        action("cv", section, instruction, li_quote),
                        action("linkedin", section, instruction, cv_quote),
                    ],
                    "relevance",
                    {"only_cv": only_cv, "only_linkedin": only_li},
                )
            )
    else:
        missing = "linkedin" if not linkedin_text.strip() else "cv"
        findings.append(
            finding(
                "compare.unavailable",
                "not_assessable",
                f"{'LinkedIn' if missing == 'linkedin' else 'CV'} não fornecido: não foi possível comparar os documentos.",
                "Envie o conteúdo dos dois documentos para comparar funções, competências e datas.",
                [excerpt(missing, texts[missing], None, "Não foi enviado texto desta fonte.")],
                [],
            )
        )

    for source, text in texts.items():
        if not text.strip():
            continue
        label = "CV" if source == "cv" else "LinkedIn"
        matches = {key: SECTION_PATTERNS[key].search(text) for key in SECTION_NAMES}
        missing = [SECTION_NAMES[key] for key, match in matches.items() if match is None]
        found = [SECTION_NAMES[key] for key, match in matches.items() if match is not None]
        evidence = [
            excerpt(source, text, match, f"Marcador reconhecido: {SECTION_NAMES[key]}.")
            for key, match in matches.items()
            if match is not None
        ]
        if missing:
            evidence.append(
                excerpt(
                    source,
                    text,
                    None,
                    "Marcadores não localizados: "
                    + ", ".join(missing)
                    + ". A secção pode existir com outro título.",
                )
            )
        instruction = (
            (
                "Verifique se estas secções já existem com outro título. Se faltarem, organize a informação verdadeira sob esses títulos: "
                + ", ".join(missing)
                + "."
            )
            if missing
            else "Os marcadores destas secções foram reconhecidos; mantenha os títulos claros."
        )
        findings.append(
            finding(
                f"{source}.sections",
                "missing" if missing else "observation",
                f"{label}: marcadores reconhecidos: {', '.join(found) or 'nenhum'}. "
                f"Não localizados: {', '.join(missing) or 'nenhum'}.",
                instruction,
                evidence,
                [action(source, section, instruction) for section in missing],
                "completeness",
                {"missing_sections": [key for key, match in matches.items() if match is None]},
            )
        )
        metrics = list(METRIC_PATTERN.finditer(text))
        result = RESULT_PATTERN.search(text)
        if metrics:
            findings.append(
                finding(
                    f"{source}.impact",
                    "observation",
                    f"{label}: encontrei {len(metrics)} referência(s) quantitativa(s): "
                    + ", ".join(m.group() for m in metrics[:6])
                    + ".",
                    "Confirme que cada número tem contexto, período e relação com o seu contributo. A presença de um número, por si só, não demonstra impacto.",
                    [excerpt(source, text, m) for m in metrics[:3]],
                    [],
                    message_params={"metrics": [m.group() for m in metrics[:6]]},
                )
            )
        else:
            ev = [
                excerpt(
                    source,
                    text,
                    result,
                    "Atividade identificada sem referência quantitativa reconhecida no documento."
                    if result
                    else "Nenhuma atividade ou métrica foi reconhecida por esta regra no texto enviado.",
                )
            ]
            instruction = "Nesta experiência, explicite a ação, o contexto e o resultado verificável. Use números apenas se os puder confirmar."
            findings.append(
                finding(
                    f"{source}.impact",
                    "missing",
                    f"{label}: não reconheci métricas com unidades, como percentagem, utilizadores, horas ou clientes. Datas não contam como resultados.",
                    instruction,
                    ev,
                    [
                        action(
                            source,
                            "Experiência",
                            instruction,
                            "[ação realizada] em [contexto], com [resultado verificável] no período [período].",
                        )
                    ],
                )
            )
        skills = signals(SKILL_PATTERN, text)
        instruction = (
            "Organize estas competências conforme a função pretendida, sem acrescentar competências não comprovadas."
            if skills
            else "Reveja a secção de competências. A lista de termos reconhecidos é limitada; a ausência de correspondência não prova ausência de competências."
        )
        findings.append(
            finding(
                f"{source}.skills",
                "observation" if skills else "not_assessable",
                f"{label}: competências reconhecidas pela regra: {', '.join(skills) or 'nenhuma'}.",
                instruction,
                [excerpt(source, text, m) for m in list(skills.values())[:3]]
                or [
                    excerpt(
                        source,
                        text,
                        None,
                        "Nenhum termo do vocabulário de competências foi reconhecido.",
                    )
                ],
                [action(source, "Competências", instruction, ", ".join(skills))] if skills else [],
                "relevance",
                {"skills": list(skills)},
            )
        )
    return findings
