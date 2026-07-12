import test from "node:test";
import assert from "node:assert/strict";
import {
  approveDossier,
  createDossier,
  createTestInvoice,
  demoCompany,
  demoTender,
  runDemoFlow,
  simulateSubmission
} from "../src/demoFlow.js";

test("demo flow reaches simulated award and sandbox billing", () => {
  const flow = runDemoFlow();

  assert.equal(flow.dossier.status, "ready-for-approval");
  assert.equal(flow.approvedDossier.status, "approved");
  assert.equal(flow.submission.status, "submitted-simulated");
  assert.equal(flow.award.status, "awarded-simulated");
  assert.equal(flow.invoice.status, "test-invoice-created");
  assert.equal(flow.invoice.payment.chargeType, "test-only");
  assert.ok(flow.learning.nextActions.length >= 3);
});

test("hard knock-out failure blocks approval and submission", () => {
  const companyWithoutEUHosting = {
    ...demoCompany,
    constraints: {
      ...demoCompany.constraints,
      hasEUHosting: false
    }
  };

  const dossier = createDossier(companyWithoutEUHosting, demoTender);
  const approval = approveDossier(dossier);
  const submission = simulateSubmission(approval);

  assert.equal(dossier.status, "blocked");
  assert.equal(dossier.analysis.decision, "no-bid");
  assert.equal(approval.approval.status, "rejected");
  assert.equal(submission.status, "not-submitted");
});

test("no invoice is created without simulated award", () => {
  const dossier = approveDossier(createDossier());
  const invoice = createTestInvoice(demoCompany, dossier, {
    status: "lost-simulated",
    awardValueEur: 0
  });

  assert.equal(invoice.status, "no-invoice");
  assert.equal(invoice.payment.status, "not-started");
  assert.equal(invoice.totalEur, 0);
});
