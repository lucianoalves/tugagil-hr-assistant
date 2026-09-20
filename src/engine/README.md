# Engine Module

Implemented responsibilities:
- baseline text parsing and normalization
- section presence detection with multi-alias coverage
- contact extraction (email, phone, LinkedIn, GitHub)
- parser signal extraction for deterministic consistency checks (roles, skills, projects, years)
- deterministic module scoring (`cv_quality`, `linkedin_quality`, `consistency`) with per-module dimensions
- configurable overall scoring weights with strict key/range/sum validation
