import { CacheManager } from '../cache/redis.js';

export interface CapacityPolicy {
  merchant_id: string;
  max_links_per_hour: number;
  max_links_per_day: number;
  max_links_per_customer_per_day: number;
  time_window_hours: number;
  monthly_budget_paise: number;
}

export interface CapacityCheckResult {
  allowed: boolean;
  reason?: string;
  hourly_remaining: number;
  daily_remaining: number;
  budget_remaining_paise: number;
}

export class CapacityPolicyManager {
  private static defaultPolicy: CapacityPolicy = {
    merchant_id: 'merchant_default',
    max_links_per_hour: 20,
    max_links_per_day: 100,
    max_links_per_customer_per_day: 1, // strict customer fatigue: max 1 link per 24h
    time_window_hours: 1,
    monthly_budget_paise: 5000000, // ₹50,000 max monthly budget
  };

  /**
   * Checks if an opportunity can be allocated under the merchant's capacity policy.
   */
  public static async evaluateCapacity(
    merchantId: string,
    customerId: string,
    operationalCostPaise: number,
    customPolicy?: Partial<CapacityPolicy>
  ): Promise<CapacityCheckResult> {
    const policy: CapacityPolicy = {
      ...this.defaultPolicy,
      ...customPolicy,
      merchant_id: merchantId,
    };

    const cache = CacheManager.getInstance();

    // 1. Customer-level fatigue check (max 1 link per 24h)
    const customerKey = `fatigue:${merchantId}:${customerId}`;
    const custCount = (await cache.get<number>(customerKey)) || 0;
    if (custCount >= policy.max_links_per_customer_per_day) {
      return {
        allowed: false,
        reason: `Customer fatigue limit reached (${custCount}/${policy.max_links_per_customer_per_day} in 24h)`,
        hourly_remaining: 0,
        daily_remaining: 0,
        budget_remaining_paise: 0,
      };
    }

    // 2. Merchant Hourly Capacity Check
    const hourlyKey = `capacity:hourly:${merchantId}`;
    const hourlyCount = (await cache.get<number>(hourlyKey)) || 0;
    if (hourlyCount >= policy.max_links_per_hour) {
      return {
        allowed: false,
        reason: `Merchant hourly capacity limit reached (${hourlyCount}/${policy.max_links_per_hour})`,
        hourly_remaining: 0,
        daily_remaining: Math.max(0, policy.max_links_per_day - hourlyCount),
        budget_remaining_paise: 0,
      };
    }

    // 3. Merchant Daily Capacity Check
    const dailyKey = `capacity:daily:${merchantId}`;
    const dailyCount = (await cache.get<number>(dailyKey)) || 0;
    if (dailyCount >= policy.max_links_per_day) {
      return {
        allowed: false,
        reason: `Merchant daily capacity limit reached (${dailyCount}/${policy.max_links_per_day})`,
        hourly_remaining: Math.max(0, policy.max_links_per_hour - hourlyCount),
        daily_remaining: 0,
        budget_remaining_paise: 0,
      };
    }

    // 4. Monthly Operational Budget Cap Check
    const budgetKey = `budget:monthly:${merchantId}`;
    const spentPaise = (await cache.get<number>(budgetKey)) || 0;
    if (spentPaise + operationalCostPaise > policy.monthly_budget_paise) {
      return {
        allowed: false,
        reason: `Merchant monthly operational budget exceeded (spent: ₹${(spentPaise / 100).toFixed(2)}, limit: ₹${(policy.monthly_budget_paise / 100).toFixed(2)})`,
        hourly_remaining: policy.max_links_per_hour - hourlyCount,
        daily_remaining: policy.max_links_per_day - dailyCount,
        budget_remaining_paise: Math.max(0, policy.monthly_budget_paise - spentPaise),
      };
    }

    return {
      allowed: true,
      hourly_remaining: policy.max_links_per_hour - hourlyCount - 1,
      daily_remaining: policy.max_links_per_day - dailyCount - 1,
      budget_remaining_paise: policy.monthly_budget_paise - (spentPaise + operationalCostPaise),
    };
  }

  /**
   * Consumes capacity and records link creation against limits.
   */
  public static async recordConsumption(
    merchantId: string,
    customerId: string,
    operationalCostPaise: number
  ): Promise<void> {
    const cache = CacheManager.getInstance();

    // 1. Customer Fatigue: 24h TTL
    const customerKey = `fatigue:${merchantId}:${customerId}`;
    const curCust = (await cache.get<number>(customerKey)) || 0;
    await cache.set(customerKey, curCust + 1, 86400); // 24 hours

    // 2. Hourly Counter: 1h TTL
    const hourlyKey = `capacity:hourly:${merchantId}`;
    const curHour = (await cache.get<number>(hourlyKey)) || 0;
    await cache.set(hourlyKey, curHour + 1, 3600); // 1 hour

    // 3. Daily Counter: 24h TTL
    const dailyKey = `capacity:daily:${merchantId}`;
    const curDaily = (await cache.get<number>(dailyKey)) || 0;
    await cache.set(dailyKey, curDaily + 1, 86400); // 24 hours

    // 4. Monthly Budget Counter: 30-day TTL
    const budgetKey = `budget:monthly:${merchantId}`;
    const curBudget = (await cache.get<number>(budgetKey)) || 0;
    await cache.set(budgetKey, curBudget + operationalCostPaise, 2592000); // 30 days
  }
}
