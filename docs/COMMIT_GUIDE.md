# Commit Strategy

Format:
`<type>(<scope>): <short summary>`

Types:
- feat, fix, refactor, test, docs, chore

Examples:
- feat(api): create POST /api/validate endpoint scaffold
- feat(engine): add initial deterministic scoring pipeline
- feat(parser): add first CV text extraction flow
- feat(redaction): mask email and phone before llm step
- fix(api): return consistent error payload for invalid input
- test(smoke): add end-to-end validate pipeline happy path
- docs(readme): add local run instructions and architecture
overview
- chore(ci): add lint and test workflow

Rules:
- 1 commit = 1 clear intent
- Keep commits small, readable, and testable
- Update docs whenever behavior changes