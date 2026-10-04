# Human Review Workflow

The system is designed with a mandatory Human-in-the-Loop architecture. 

## Process Flow
`System Recommendation -> Human Verification -> Accept/Override -> Maintenance Action -> Audit Log`

## Review Points
When a Biomedical Engineer reviews a piece of equipment in the dashboard, they must complete the following checks:

1. **Equipment Status Verification**: Ensure the machine is actually DOWN and not just offline or rebooting.
2. **Procedure Verification**: Verify that the scheduled procedures listed are accurate and not cancelled.
3. **Urgency Verification**: Confirm the urgency (Emergency, Urgent, Routine) reflects clinical reality.
4. **Alternative Verification**: Confirm whether alternative equipment is genuinely available or if it's currently in use.
5. **Repair Estimate Verification**: Check if the estimated repair time is realistic based on parts availability.
6. **Priority Recommendation Review**: Review the system's generated priority and the explanation provided.
7. **Final Maintenance Decision**: Explicitly select the final priority (CRITICAL, HIGH, MEDIUM, LOW). This can match the system recommendation (Accept) or differ (Override).
8. **Override Reason**: If overriding the system, the engineer MUST provide a textual reason justifying the clinical or operational reality that the system missed.
