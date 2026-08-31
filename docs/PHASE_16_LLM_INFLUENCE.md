# ULTRON v3.8 — Phase 16: Multi-Seed LLM Influence Audit

## 1. 4-Tier Influence Taxonomy
To avoid conflating candidate proposal with financial decision-making, Phase 16 measures 4 separate metrics across 30 seeds ($N=30$):

1. **Metric A: Candidate Novelty Rate**:
   $$\text{Novelty Rate} = \frac{\text{Novel Candidates}}{\text{Total LLM Candidates}} = 90.0\%$$
2. **Metric B: Candidate Pool Influence**:
   $$\text{Pool Influence Rate} = \frac{\sum [CandidateSet_{ON} \ne CandidateSet_{OFF}]}{N} = 100.0\%$$
3. **Metric C: Preference Influence**:
   $$\text{Preference Influence Rate} = \frac{\sum [LLM_{preferred} \ne Baseline_{preferred}]}{N} = 66.7\%$$
4. **Metric D: Final Decision Influence**:
   $$\text{Final Decision Influence Rate} = \frac{\sum [FinalAction_{ON} \ne FinalAction_{OFF}]}{N} = 0.0\%$$

## 2. Verdict
- **Scientific Verdict**: **`CANDIDATE_INFLUENCE_ONLY`**
- **Reasoning**: The LLM enriches the candidate pool across 100% of seeds, but the deterministic Action Decision Authority and Net Expected Value (NEV) ranking govern 100% of final execution decisions.
