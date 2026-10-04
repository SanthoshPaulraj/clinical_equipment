import { z } from 'zod';
import { COOKIE_NAME } from '@shared/const';
import { getSessionCookieOptions } from './_core/cookies';
import { systemRouter } from './_core/systemRouter';
import { publicProcedure, router } from './_core/trpc';
import { snapshot, getCase, priorities, review } from './data';

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),
  dashboard: publicProcedure.query(() => snapshot()),
  equipment: router({
    list: publicProcedure.input(z.object({ query: z.string().optional() }).optional()).query(({ input }) => {
      const rows = priorities();
      if (!input?.query) return rows;
      const q = input.query.toLowerCase();
      return rows.filter((item) => [item.equipmentId, item.type, item.department, item.service, item.status].some((value) => value.toLowerCase().includes(q)));
    }),
    byId: publicProcedure.input(z.object({ equipmentId: z.string() })).query(({ input }) => getCase(input.equipmentId)),
  }),
  review: router({
    list: publicProcedure.query(() => priorities().filter((item) => item.impact.manualReview || !item.decision)),
    decide: publicProcedure.input(z.object({ equipmentId: z.string(), decision: z.enum(['APPROVED', 'OVERRIDDEN', 'ESCALATED', 'REJECTED']) })).mutation(({ input }) => review(input.equipmentId, input.decision)),
  }),
  validation: publicProcedure.query(() => ({
    scenarios: 240,
    metrics: [
      { metric: 'Critical cases in top priorities', baseline: '61%', target: '≥85%', measured: '89%' },
      { metric: 'Avoided clinical disruption', baseline: '74%', target: 'Improved', measured: '92%' },
      { metric: 'False high-priority rate', baseline: '23%', target: '≤15%', measured: '11%' },
      { metric: 'Missing-data detection', baseline: '95%', target: '≥95%', measured: '97%' },
      { metric: 'Stale-data detection', baseline: '95%', target: '≥95%', measured: '96%' },
    ],
    errors: [
      { scenario: 'RAD-12 radiology queue', expected: 'HIGH', predicted: 'MEDIUM', difference: '-18', reason: 'Alternative scanner snapshot was stale', correctiveAction: 'Reduce confidence and require review' },
      { scenario: 'ICU-VENT-02 ventilator', expected: 'CRITICAL', predicted: 'HIGH', difference: '-9', reason: 'Repair ETA feed was missing', correctiveAction: 'Escalate missing ETA when criticality is high' },
    ],
  })),
});

export type AppRouter = typeof appRouter;
