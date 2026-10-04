import { describe, expect, it } from 'vitest';
import { calculateImpact, downtimeOnly } from './scoring';

describe('MediPulse scoring engine', () => {
  it('weights urgent procedures and limited alternatives above downtime alone', () => {
    const result = calculateImpact({ urgency: 'EMERGENCY', affectedProcedures: 7, alternatives: 1, serviceCriticality: 94, repairEtaHours: 8, downtimeHours: 5.7, freshness: { equipment: 'FRESH', procedures: 'FRESH', alternatives: 'FRESH', repairEta: 'FRESH' } });
    expect(result.score).toBeGreaterThan(80);
    expect(result.priority).toBe('CRITICAL');
    expect(result.confidence).toBe(100);
    expect(result.explanation).toContain('7 scheduled procedures');
  });
  it('routes missing critical inputs to manual review without inventing values', () => {
    const result = calculateImpact({ urgency: 'HIGH', affectedProcedures: 3, alternatives: null, serviceCriticality: 100, repairEtaHours: null, downtimeHours: 2.1, freshness: { equipment: 'FRESH', procedures: 'FRESH', alternatives: 'MISSING', repairEta: 'MISSING' } });
    expect(result.priority).toBe('MANUAL REVIEW');
    expect(result.manualReview).toBe(true);
    expect(result.explanation).toContain('unknown');
    expect(result.confidence).toBeLessThan(60);
  });
  it('keeps baseline logic separate', () => { expect(downtimeOnly(14.8)).toBe(59); });
});
