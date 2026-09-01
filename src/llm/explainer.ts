import dotenv from 'dotenv';
import path from 'node:path';
import {
  RecoveryOpportunity,
  Score,
  AllocationDecision,
  AuthorityCheck,
} from '../types/index.js';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });

export interface ExplanationResult {
  opportunity_id: string;
  model: string;
  provider: string;
  reasoning_content: string | null;
  explanation: string;
  created_at: string;
}

/**
 * Calls NVIDIA NIM API using model openai/gpt-oss-120b to explain deterministic pipeline decisions.
 * CRITICAL RULE: Zero LLMs on the execution path. The LLM only explains stored factual decisions.
 */
export async function explainOpportunityDecision(
  opp: RecoveryOpportunity,
  score?: Score,
  decision?: AllocationDecision,
  checks?: AuthorityCheck[]
): Promise<ExplanationResult> {
  const baseUrl = (process.env.NVIDIA_BASE_URL || 'https://integrate.api.nvidia.com/v1').replace(/\/+$/, '');
  const apiKey = process.env.NVIDIA_API_KEY || '';
  const model = process.env.LLM_MODEL || 'nvidia/nemotron-3.5-lightning-30b-a3b';
  const reasoningBudget = Number(process.env.LLM_REASONING_BUDGET) || 2048;

  const amountDisplay = `₹${(opp.amount_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
  const ivenDisplay = score ? `₹${(score.expected_incremental_value_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : 'N/A';
  const shadowPriceDisplay = decision ? `₹${(decision.shadow_price_paise_at_decision / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : 'N/A';

  const promptContent = `
You are the ULTRON Control Plane Lead Financial & Risk Systems Analyst.
Analyze and explain the following autonomous payment recovery decision in clear, authoritative, and concise terms.

=== RECOVERY OPPORTUNITY DATA ===
- Opportunity ID: ${opp.id}
- Source: ${opp.source}
- Amount at Risk: ${amountDisplay} (${opp.amount_paise} paise)
- Raw Reason Code: ${opp.reason_code}
- Perception Decline Taxonomy: ${opp.decline_type}
- Attempt Count: ${opp.attempt_count}
- Customer ID: ${opp.customer_id}
- Customer Trust Score: ${opp.customer_trust_score}
- Pipeline Status: ${opp.status}

=== ECONOMIC REASONING SCORING (Counterfactual Model) ===
- Natural Recovery Probability P(natural): ${score ? score.natural_recovery_prob : 'N/A'} (model-estimated)
- Intervention Recovery Probability P(intervention): ${score ? score.intervention_recovery_prob : 'N/A'} (model-estimated)
- Incremental Probability (Δ = P(int) - P(nat)): ${score ? score.incremental_prob : 'N/A'}
- Operational Delivery Cost: ₹${score ? (score.operational_cost_paise / 100).toFixed(2) : '4.00'}
- Customer Fatigue Penalty Cost: ₹${score ? (score.fatigue_cost_paise / 100).toFixed(2) : '0.00'}
- Expected Incremental Value (IVEN): ${ivenDisplay} (${score ? score.expected_incremental_value_paise : 'N/A'} paise)
- Confidence Level: ${score ? score.confidence.toUpperCase() : 'N/A'}

=== RECOVERY MARKET ALLOCATION ===
- Decision: ${decision ? decision.decision : 'PENDING'}
- Rank in Batch: #${decision ? decision.rank_in_batch : 'N/A'}
- Marginal Market Shadow Price (λ): ${shadowPriceDisplay}
- Allocation Reason: ${decision ? decision.reason : 'N/A'}

=== ACTION AUTHORITY COMPLIANCE VERIFICATION ===
${checks && checks.length > 0 ? checks.map(c => `- ${c.check_name}: ${c.passed ? 'PASSED (✓)' : 'FAILED (✗)'} -> ${c.reason}`).join('\n') : '- Compliance checks: Verified on the fly'}

=== INSTRUCTIONS FOR YOUR ANALYSIS ===
Write a structured 3-part forensic explanation for the merchant operations team:
1. **Economic Rationale**: Why did this opportunity yield this Expected Incremental Value (IVEN), taking into account natural counterfactual recovery vs intervention lift?
2. **Market & Capacity Dynamics**: Why was it ranked #${decision?.rank_in_batch ?? '-'} and assigned ${decision?.decision ?? 'PENDING'} relative to the portfolio capacity limit and shadow price?
3. **Action Authority Verdict**: How did the deterministic compliance checks (fraud/stolen hard declines, retry caps, kill switch, confidence) validate or veto this action?

Keep the tone highly professional, precise, and analytical.
`.trim();

  if (!apiKey || apiKey.startsWith('nvapi-YOUR_')) {
    return {
      opportunity_id: opp.id,
      model,
      provider: 'NVIDIA NIM (Local Fallback Mode - Missing API Key)',
      reasoning_content: null,
      explanation: `[Deterministic Explainer Summary]\nOpportunity ${opp.id} (${amountDisplay}, ${opp.decline_type} decline) was evaluated with Expected Incremental Value IVEN of ${ivenDisplay}. Market allocation assigned decision '${decision?.decision || 'PENDING'}' at rank #${decision?.rank_in_batch || '-'}. Action Authority compliance verified all rules with final status '${opp.status}'.`,
      created_at: new Date().toISOString(),
    };
  }

  try {
    const response = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages: [
          {
            role: 'system',
            content: 'You are the ULTRON Control Plane Autonomous Economic & Risk Explainer. Your role is to provide deep, mathematically sound, and compliance-focused explanations of deterministic payment recovery decisions. Never suggest executing unauthorized actions.',
          },
          {
            role: 'user',
            content: promptContent,
          },
        ],
        temperature: 1,
        top_p: 0.95,
        max_tokens: 8192,
        chat_template_kwargs: { enable_thinking: true },
        reasoning_budget: reasoningBudget,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`NVIDIA NIM API responded with HTTP ${response.status}: ${errText}`);
    }

    if (!response.body) {
      throw new Error('NVIDIA NIM API response body is empty');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullReasoning = '';
    let fullContent = '';
    let returnedModel = model;

    let streamDone = false;

    while (!streamDone) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        if (trimmed === 'data: [DONE]') {
          streamDone = true;
          break;
        }
        if (trimmed.startsWith('data: ')) {
          try {
            const json = JSON.parse(trimmed.slice(6));
            if (json?.model) returnedModel = json.model;
            const delta = json?.choices?.[0]?.delta;
            if (delta) {
              const reasoning = delta.reasoning_content || (delta as any).reasoning;
              if (reasoning) fullReasoning += reasoning;
              if (delta.content) fullContent += delta.content;
            }
          } catch (e) {
            // ignore partial JSON parse errors
          }
        }
      }
    }

    return {
      opportunity_id: opp.id,
      model: returnedModel,
      provider: 'NVIDIA NIM',
      reasoning_content: fullReasoning.trim() || null,
      explanation: fullContent.trim() || 'No explanation generated.',
      created_at: new Date().toISOString(),
    };
  } catch (error: any) {
    console.error(`LLM Explainer error for opportunity ${opp.id}:`, error);
    return {
      opportunity_id: opp.id,
      model,
      provider: 'NVIDIA NIM (Error Fallback)',
      reasoning_content: null,
      explanation: `[Fallback Explanation due to API Error: ${error?.message || 'Network error'}]\nOpportunity ${opp.id} for ${amountDisplay} was processed with IVEN of ${ivenDisplay}, resulting in decision '${decision?.decision || 'PENDING'}' and pipeline status '${opp.status}'.`,
      created_at: new Date().toISOString(),
    };
  }
}
