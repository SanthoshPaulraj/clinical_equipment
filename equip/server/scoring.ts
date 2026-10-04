export type Urgency = 'LOW' | 'MEDIUM' | 'HIGH' | 'EMERGENCY';
export type Freshness = 'FRESH' | 'STALE' | 'MISSING' | 'UNKNOWN';
export type Priority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'MANUAL REVIEW';

export type ImpactInputs = {
  urgency: Urgency;
  affectedProcedures: number;
  alternatives: number | null;
  serviceCriticality: number;
  repairEtaHours: number | null;
  downtimeHours: number;
  freshness: Record<string, Freshness>;
};

const urgencyValue: Record<Urgency, number> = { LOW: 20, MEDIUM: 48, HIGH: 78, EMERGENCY: 100 };
const freshnessPenalty: Record<Freshness, number> = { FRESH: 0, STALE: 12, MISSING: 30, UNKNOWN: 24 };

export function calculateImpact(input: ImpactInputs) {
  const factors = [
    { label: 'Procedure urgency', value: urgencyValue[input.urgency], weight: 0.3 },
    { label: 'Affected procedures', value: Math.min(100, input.affectedProcedures * 14), weight: 0.2 },
    { label: 'Alternative capacity risk', value: input.alternatives === null ? 60 : Math.max(0, 100 - input.alternatives * 28), weight: 0.2 },
    { label: 'Service criticality', value: input.serviceCriticality, weight: 0.15 },
    { label: 'Repair delay risk', value: input.repairEtaHours === null ? 58 : Math.min(100, input.repairEtaHours * 9), weight: 0.15 },
  ];
  const score = Math.round(factors.reduce((sum, factor) => sum + factor.value * factor.weight, 0));
  const confidence = Math.max(0, 100 - Object.values(input.freshness).reduce((sum, state) => sum + freshnessPenalty[state], 0));
  const manualReview = confidence < 60 || input.alternatives === null || input.repairEtaHours === null;
  const priority: Priority = manualReview ? 'MANUAL REVIEW' : score >= 80 ? 'CRITICAL' : score >= 60 ? 'HIGH' : score >= 40 ? 'MEDIUM' : 'LOW';
  const alternatives = input.alternatives === null ? 'alternative capacity is unknown' : `${input.alternatives} alternative${input.alternatives === 1 ? '' : 's'} available`;
  const eta = input.repairEtaHours === null ? 'repair ETA is unknown' : `repair ETA is ${input.repairEtaHours}h`;
  const explanation = `${input.affectedProcedures} scheduled procedure${input.affectedProcedures === 1 ? '' : 's'} may be affected. ${input.urgency.toLowerCase()} urgency, ${alternatives}, ${eta}, and service criticality ${input.serviceCriticality}/100. ${manualReview ? 'Manual review required because confidence is limited.' : 'Review before approving maintenance action.'}`;
  return { score, confidence, priority, factors, explanation, manualReview };
}

export function downtimeOnly(hours: number) { return Math.min(100, Math.round(hours * 4)); }
export function classify(score: number) { return score >= 80 ? 'CRITICAL' : score >= 60 ? 'HIGH' : score >= 40 ? 'MEDIUM' : 'LOW'; }
