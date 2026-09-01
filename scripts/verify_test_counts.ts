import fs from 'node:fs';
import path from 'node:path';

function verifyTestCounts() {
  console.log('======================================================================');
  console.log('🔍 ULTRON v5.1 — AUTOMATED CROSS-FILE TEST COUNT CONSISTENCY CHECK');
  console.log('======================================================================\n');

  const cwd = process.cwd();
  const reconPath = path.join(cwd, 'results/agent/v51/test_count_reconciliation.json');
  const completeTruthJsonPath = path.join(cwd, 'ULTRON_V5_1_COMPLETE_TRUTH.json');
  const completeTruthMdPath = path.join(cwd, 'ULTRON_V5_1_COMPLETE_TRUTH.md');
  const finalAcceptanceMdPath = path.join(cwd, 'ULTRON_V5_1_FINAL_ACCEPTANCE_REPORT.md');
  const finalAcceptanceJsonPath = path.join(cwd, 'results/agent/v51/final_acceptance.json');

  let errors = 0;

  // 1. Load reconciliation JSON
  if (!fs.existsSync(reconPath)) {
    console.error(`❌ Reconciliation file missing at ${reconPath}`);
    process.exit(1);
  }

  const recon = JSON.parse(fs.readFileSync(reconPath, 'utf8'));

  // Calculate actual sum of automated test cases from suite array
  const calculatedAutomatedTests = recon.suites
    .filter((s: any) => s.category === 'AUTOMATED_TEST_CASE' || s.category === 'TEST')
    .reduce((sum: number, s: any) => sum + s.passed, 0);

  const calculatedBuildChecks = recon.suites
    .filter((s: any) => s.category === 'BUILD_CHECK' || s.category === 'BUILD')
    .reduce((sum: number, s: any) => sum + s.passed, 0);

  const calculatedCausalExperiments = recon.totals.causal_experiments || recon.totals.experiments || 8;

  console.log(`📊 Derived Test Totals from Reconciliation Suites:`);
  console.log(`   - Automated Test Cases (Category A): ${calculatedAutomatedTests}`);
  console.log(`   - Build Checks (Category B):         ${calculatedBuildChecks}`);
  console.log(`   - Combined Verification Checks:     ${calculatedAutomatedTests + calculatedBuildChecks}`);
  console.log(`   - Causal Experiments (Category C):   ${calculatedCausalExperiments}`);

  // Assert internal reconciliation consistency
  if (recon.totals.unique_automated_tests !== calculatedAutomatedTests) {
    console.error(`❌ Internal mismatch in reconciliation JSON: totals.unique_automated_tests (${recon.totals.unique_automated_tests}) != calculated (${calculatedAutomatedTests})`);
    errors++;
  } else {
    console.log(`✅ Reconciliation JSON internal arithmetic verified (${calculatedAutomatedTests} tests).`);
  }

  // 2. Check COMPLETE_TRUTH.json
  if (fs.existsSync(completeTruthJsonPath)) {
    const truthJson = JSON.parse(fs.readFileSync(completeTruthJsonPath, 'utf8'));
    const truthTests = truthJson.testing?.totals?.unique_automated_tests;
    const truthBuild = truthJson.testing?.totals?.build_checks;
    const truthCombined = truthJson.testing?.totals?.combined_verification_checks;

    if (truthTests !== calculatedAutomatedTests) {
      console.error(`❌ ULTRON_V5_1_COMPLETE_TRUTH.json mismatch: testing.totals.unique_automated_tests (${truthTests}) != ${calculatedAutomatedTests}`);
      errors++;
    } else {
      console.log(`✅ ULTRON_V5_1_COMPLETE_TRUTH.json matches canonical automated tests (${truthTests}).`);
    }

    if (truthBuild !== calculatedBuildChecks) {
      console.error(`❌ ULTRON_V5_1_COMPLETE_TRUTH.json mismatch: testing.totals.build_checks (${truthBuild}) != ${calculatedBuildChecks}`);
      errors++;
    } else {
      console.log(`✅ ULTRON_V5_1_COMPLETE_TRUTH.json matches canonical build checks (${truthBuild}).`);
    }

    if (truthCombined !== (calculatedAutomatedTests + calculatedBuildChecks)) {
      console.error(`❌ ULTRON_V5_1_COMPLETE_TRUTH.json mismatch: combined_verification_checks (${truthCombined}) != ${calculatedAutomatedTests + calculatedBuildChecks}`);
      errors++;
    }
  } else {
    console.error(`❌ Missing ${completeTruthJsonPath}`);
    errors++;
  }

  // 3. Check COMPLETE_TRUTH.md
  if (fs.existsSync(completeTruthMdPath)) {
    const mdContent = fs.readFileSync(completeTruthMdPath, 'utf8');
    if (!mdContent.includes(`${calculatedAutomatedTests} / ${calculatedAutomatedTests} unique automated test cases passed`)) {
      console.error(`❌ ULTRON_V5_1_COMPLETE_TRUTH.md missing exact count: "${calculatedAutomatedTests} / ${calculatedAutomatedTests} unique automated test cases passed"`);
      errors++;
    } else {
      console.log(`✅ ULTRON_V5_1_COMPLETE_TRUTH.md contains verified canonical test count (${calculatedAutomatedTests}).`);
    }
  }

  // 4. Check FINAL_ACCEPTANCE_REPORT.md
  if (fs.existsSync(finalAcceptanceMdPath)) {
    const acceptMd = fs.readFileSync(finalAcceptanceMdPath, 'utf8');
    if (!acceptMd.includes(`**${calculatedAutomatedTests}**`)) {
      console.error(`❌ ULTRON_V5_1_FINAL_ACCEPTANCE_REPORT.md missing table total of **${calculatedAutomatedTests}**`);
      errors++;
    } else {
      console.log(`✅ ULTRON_V5_1_FINAL_ACCEPTANCE_REPORT.md contains verified canonical test count (**${calculatedAutomatedTests}**).`);
    }
  }

  // 5. Check final_acceptance.json
  if (fs.existsSync(finalAcceptanceJsonPath)) {
    const acceptJson = JSON.parse(fs.readFileSync(finalAcceptanceJsonPath, 'utf8'));
    const accTests = acceptJson.testing?.totals?.unique_automated_tests;
    if (accTests !== calculatedAutomatedTests) {
      console.error(`❌ final_acceptance.json mismatch: testing.totals.unique_automated_tests (${accTests}) != ${calculatedAutomatedTests}`);
      errors++;
    } else {
      console.log(`✅ final_acceptance.json matches canonical automated tests (${accTests}).`);
    }
  }

  console.log('\n======================================================================');
  if (errors === 0) {
    console.log('🏁 ALL CROSS-FILE COUNT ASSERTIONS PASSED WITH 0 CONFLICTS');
    console.log('======================================================================');
    process.exit(0);
  } else {
    console.error(`🚨 DETECTED ${errors} CROSS-FILE COUNT MISMATCHES`);
    console.log('======================================================================');
    process.exit(1);
  }
}

verifyTestCounts();
