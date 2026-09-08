# Engine Module

Implemented responsibilities:
- baseline text parsing and normalization
- section presence detection with multi-alias coverage
- contact extraction (email, phone, LinkedIn, GitHub)
- deterministic scoring (`section_core`, `structure_depth`, `keyword`, `completeness`, `consistency`, `contact_readiness`, `impact_evidence`)
- profile-level deterministic sub-scores (`cv_quality`, `linkedin_quality`, `consistency`)
