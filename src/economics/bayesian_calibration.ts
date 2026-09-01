import { DatabaseAdapter } from '../db/adapter.js';

export const STATIC_PROBABILITY_TABLE: Record<string, { natural_recovery_prob: number; intervention_recovery_prob: number }> = {
  insufficient_funds: { natural_recovery_prob: 0.35, intervention_recovery_prob: 0.55 },
  expired_card: { natural_recovery_prob: 0.05, intervention_recovery_prob: 0.60 },
  generic_decline: { natural_recovery_prob: 0.25, intervention_recovery_prob: 0.45 },
  network_error: { natural_recovery_prob: 0.45, intervention_recovery_prob: 0.75 },
  hard_decline: { natural_recovery_prob: 0.02, intervention_recovery_prob: 0.02 },
  default: { natural_recovery_prob: 0.15, intervention_recovery_prob: 0.35 },
};

export interface BetaDistribution {
  alpha: number;
  beta: number;
  expected: number;
  sampleSize: number;
}

export interface CalibratedModelRecord {
  reason_code: string;
  p_natural_mean: number;
  p_interv_mean: number;
  sample_size: number;
  model_type: 'STATIC' | 'CALIBRATED';
  status: 'ACTIVE' | 'CANDIDATE';
  lift_vs_baseline: number;
  p_value: number;
  updated_at: string;
}

export class BayesianProbabilityCalibrator {
  public static async initTable(db?: DatabaseAdapter): Promise<void> {
    const adapter = db || DatabaseAdapter.getInstance();
    await adapter.execute(`
      CREATE TABLE IF NOT EXISTS probability_models (
        reason_code TEXT PRIMARY KEY,
        p_natural_mean REAL NOT NULL,
        p_interv_mean REAL NOT NULL,
        sample_size INTEGER NOT NULL,
        model_type TEXT NOT NULL CHECK(model_type IN ('STATIC', 'CALIBRATED')),
        status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'CANDIDATE')),
        lift_vs_baseline REAL NOT NULL DEFAULT 0.0,
        p_value REAL NOT NULL DEFAULT 1.0,
        updated_at TEXT NOT NULL
      );
    `);
  }

  /**
   * Computes Bayesian posterior mean from Beta(alpha, beta) prior and observed data.
   */
  public static computeBetaPosterior(
    priorAlpha: number,
    priorBeta: number,
    successes: number,
    total: number
  ): BetaDistribution {
    const postAlpha = priorAlpha + successes;
    const postBeta = priorBeta + (total - successes);
    const expected = postAlpha / (postAlpha + postBeta);
    return {
      alpha: postAlpha,
      beta: postBeta,
      expected: Number(expected.toFixed(4)),
      sampleSize: total,
    };
  }

  /**
   * Evaluates A/B test lift and auto-promotes model if lift > 5% and p < 0.05.
   */
  public static evaluateModelPromotion(
    staticProb: number,
    calibratedProb: number,
    sampleSize: number
  ): { lift: number; pValue: number; shouldPromote: boolean } {
    if (sampleSize < 100) {
      return { lift: 0, pValue: 1.0, shouldPromote: false };
    }

    const lift = (calibratedProb - staticProb) / staticProb;
    // Standard Z-test approximation for proportion comparison
    const se = Math.sqrt((staticProb * (1 - staticProb)) / sampleSize);
    const zScore = se > 0 ? (calibratedProb - staticProb) / se : 0;
    // Two-tailed p-value approximation
    const pValue = zScore > 0 ? Math.max(0.001, 1 - 0.5 * (1 + Math.tanh(zScore * 0.797884))) : 1.0;

    const shouldPromote = lift > 0.05 && pValue < 0.05;
    return {
      lift: Number(lift.toFixed(4)),
      pValue: Number(pValue.toFixed(4)),
      shouldPromote,
    };
  }

  /**
   * Retrieves effective probability distribution for a decline code.
   * If calibrated model has < 100 observations, falls back to static baseline.
   */
  public static async getEffectiveProbabilities(
    reasonCode: string
  ): Promise<{ p_natural: number; p_intervention: number; source: 'STATIC' | 'CALIBRATED' }> {
    const adapter = DatabaseAdapter.getInstance();
    await this.initTable(adapter);

    const records = await adapter.query<CalibratedModelRecord>(
      `SELECT * FROM probability_models WHERE reason_code = ? AND status = 'ACTIVE' LIMIT 1;`,
      [reasonCode]
    );

    if (records.length > 0 && records[0].sample_size >= 100 && records[0].model_type === 'CALIBRATED') {
      return {
        p_natural: records[0].p_natural_mean,
        p_intervention: records[0].p_interv_mean,
        source: 'CALIBRATED',
      };
    }

    // Static fallback baseline
    const staticBase = STATIC_PROBABILITY_TABLE[reasonCode] || STATIC_PROBABILITY_TABLE['default'];
    return {
      p_natural: staticBase.natural_recovery_prob,
      p_intervention: staticBase.intervention_recovery_prob,
      source: 'STATIC',
    };
  }

  /**
   * Updates probability models from observed dataset.
   */
  public static async updateCalibratedDistributions(
    reasonCode: string,
    naturalObservations: { successes: number; total: number },
    intervObservations: { successes: number; total: number }
  ): Promise<CalibratedModelRecord> {
    const adapter = DatabaseAdapter.getInstance();
    await this.initTable(adapter);

    const staticBase = STATIC_PROBABILITY_TABLE[reasonCode] || STATIC_PROBABILITY_TABLE['default'];
    const priorNatAlpha = staticBase.natural_recovery_prob * 10;
    const priorNatBeta = 10 - priorNatAlpha;

    const priorIntAlpha = staticBase.intervention_recovery_prob * 10;
    const priorIntBeta = 10 - priorIntAlpha;

    const postNat = this.computeBetaPosterior(
      priorNatAlpha,
      priorNatBeta,
      naturalObservations.successes,
      naturalObservations.total
    );
    const postInt = this.computeBetaPosterior(
      priorIntAlpha,
      priorIntBeta,
      intervObservations.successes,
      intervObservations.total
    );

    const totalObs = naturalObservations.total + intervObservations.total;
    const { lift, pValue, shouldPromote } = this.evaluateModelPromotion(
      staticBase.intervention_recovery_prob,
      postInt.expected,
      intervObservations.total
    );

    const modelType = totalObs >= 100 ? 'CALIBRATED' : 'STATIC';
    const status = shouldPromote || totalObs < 100 ? 'ACTIVE' : 'CANDIDATE';

    await adapter.execute(
      `INSERT INTO probability_models (reason_code, p_natural_mean, p_interv_mean, sample_size, model_type, status, lift_vs_baseline, p_value, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(reason_code) DO UPDATE SET
         p_natural_mean = excluded.p_natural_mean,
         p_interv_mean = excluded.p_interv_mean,
         sample_size = excluded.sample_size,
         model_type = excluded.model_type,
         status = excluded.status,
         lift_vs_baseline = excluded.lift_vs_baseline,
         p_value = excluded.p_value,
         updated_at = excluded.updated_at;`,
      [
        reasonCode,
        postNat.expected,
        postInt.expected,
        totalObs,
        modelType,
        status,
        lift,
        pValue,
        new Date().toISOString(),
      ]
    );

    return {
      reason_code: reasonCode,
      p_natural_mean: postNat.expected,
      p_interv_mean: postInt.expected,
      sample_size: totalObs,
      model_type: modelType,
      status,
      lift_vs_baseline: lift,
      p_value: pValue,
      updated_at: new Date().toISOString(),
    };
  }
}
