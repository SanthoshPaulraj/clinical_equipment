# Project TODO

- [x] Establish the elegant responsive command-center shell and accessible navigation
- [x] Add equipment, downtime case, procedure, alternative-capacity, data-health, review, and validation models
- [x] Implement transparent 0–100 clinical-impact scoring with configurable weights
- [x] Implement data-confidence scoring and stale/missing/unknown safeguards
- [x] Implement factor-level explanations and evidence panels for every recommendation
- [x] Implement backend procedures for dashboard, equipment cases, reviews, and validation analytics
- [x] Implement role-aware views for biomedical engineering, clinical operations, and leadership
- [x] Implement KPI cards, maintenance priority queue, filters, search, severity hierarchy, and trend charts
- [x] Implement case detail workflow with maintenance context, service impact, alternatives, recommendation, evidence, and reviewer decision capture
- [x] Implement data-health monitoring and human-review queue
- [x] Add synthetic validation analytics against downtime-only baseline
- [x] Add error analysis, edge cases, patient-journey demonstrations, and limitations
- [x] Add loading, empty, error, responsive, and accessibility states
- [x] Add Vitest coverage for scoring, confidence, explanations, prioritization, and review workflows
- [x] Run typecheck, tests, build, and visual verification; refine issues
- [x] Save final checkpoint and deliver project version

## Change History

- Initial project scope captured from the MediPulse AI master brief.
- UX refinement requested: elegant polished hospital command-center dashboard with explicit accountability and data-quality visibility.
- UX refinement requested: role-focused views, case-detail review workflow, validation analytics, error analysis, edge cases, and limitations.
- UX refinement requested: responsive accessible UX with intuitive filters, drill-down navigation, charts, and considerate states.

## Implementation Notes

- Use synthetic/anonymized operational data only; never store patient-identifying information.
- Prioritize clinical impact and disruption avoidance, not downtime duration alone.
- Recommendations remain decision support; qualified human reviewers retain final accountability.
- Use the existing full-stack scaffold, DashboardLayout, and shadcn components where appropriate.
- Persist timestamps in UTC and localize only for display.
