import { demoCompany, demoTender } from "./demoData.js";

const currency = new Intl.NumberFormat("de-DE", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0
});

function getByPath(source, path) {
  return path.split(".").reduce((value, key) => value?.[key], source);
}

function roundEuro(value) {
  return Math.round(value / 100) * 100;
}

export function analyzeRequirements(company = demoCompany, tender = demoTender) {
  const covered = tender.requiredCapabilities.filter((capability) =>
    company.capabilities.includes(capability)
  );
  const missing = tender.requiredCapabilities.filter((capability) => !covered.includes(capability));
  const niceToHaveCovered = tender.niceToHaveCapabilities.filter((capability) =>
    company.capabilities.includes(capability) || company.certifications.includes(capability)
  );

  const koResults = tender.knockOutCriteria.map((criterion) => {
    const value = Boolean(getByPath(company, criterion.companyField));
    return {
      ...criterion,
      value,
      status: value ? "passed" : criterion.required ? "failed" : "warning"
    };
  });

  const hardFailures = koResults.filter((result) => result.status === "failed");
  const capabilityScore = covered.length / tender.requiredCapabilities.length;
  const niceToHaveScore = niceToHaveCovered.length / tender.niceToHaveCapabilities.length;
  const score = Math.round((capabilityScore * 0.78 + niceToHaveScore * 0.22) * 100);

  return {
    covered,
    missing,
    niceToHaveCovered,
    koResults,
    hardFailures,
    score,
    decision:
      hardFailures.length > 0
        ? "no-bid"
        : score >= 80 && missing.length === 0
          ? "bid"
          : "review",
    confidence: hardFailures.length > 0 ? "high" : "medium"
  };
}

export function preparePricing(company = demoCompany, tender = demoTender) {
  const effortCost = tender.commercialAssumptions.estimatedPersonDays * company.commercial.dayRateEur;
  const subtotal = effortCost + tender.commercialAssumptions.platformCostsEur;
  const contingency = subtotal * (tender.commercialAssumptions.contingencyPercent / 100);
  const priceBeforeMargin = subtotal + contingency;
  const targetMargin = company.commercial.targetMarginPercent / 100;
  const offerPrice = roundEuro(priceBeforeMargin / (1 - targetMargin));
  const grossMargin = offerPrice - priceBeforeMargin;
  const grossMarginPercent = Math.round((grossMargin / offerPrice) * 100);

  return {
    effortCost: roundEuro(effortCost),
    platformCosts: tender.commercialAssumptions.platformCostsEur,
    contingency: roundEuro(contingency),
    offerPrice,
    grossMargin: roundEuro(grossMargin),
    grossMarginPercent,
    belowMinimumMargin: grossMarginPercent < company.constraints.minGrossMarginPercent
  };
}

export function selectReferences(company = demoCompany, tender = demoTender) {
  return company.references
    .map((reference) => {
      const matchedCapabilities = reference.capabilities.filter((capability) =>
        tender.requiredCapabilities.includes(capability)
      );
      return {
        ...reference,
        matchedCapabilities,
        score: matchedCapabilities.length
      };
    })
    .filter((reference) => reference.score > 0)
    .sort((a, b) => b.score - a.score || b.year - a.year)
    .slice(0, 3);
}

export function createDossier(company = demoCompany, tender = demoTender) {
  const analysis = analyzeRequirements(company, tender);
  const pricing = preparePricing(company, tender);
  const references = selectReferences(company, tender);
  const blockers = [
    ...analysis.hardFailures.map((failure) => `K.O.-Kriterium nicht erfuellt: ${failure.label}`),
    ...(analysis.missing.length > 0
      ? [`Fehlende Pflichtfaehigkeiten: ${analysis.missing.join(", ")}`]
      : []),
    ...(pricing.belowMinimumMargin ? ["Kalkulation unterschreitet Mindestmarge"] : [])
  ];

  return {
    id: `dos-${tender.id}`,
    title: `Angebotsdossier: ${tender.title}`,
    status: blockers.length > 0 ? "blocked" : "ready-for-approval",
    company: company.name,
    tender: tender.title,
    buyer: tender.buyer,
    source: tender.source,
    analysis,
    pricing,
    references,
    requiredDocuments: tender.requiredDocuments.map((name) => ({
      name,
      status: name === "Freigabeprotokoll" ? "pending-human-approval" : "prepared"
    })),
    blockers,
    auditTrail: [
      "Unternehmensprofil geladen",
      "Ausschreibung importiert",
      "Anforderungen regelbasiert analysiert",
      "K.O.-Kriterien geprueft",
      "Preisblatt vorbereitet",
      "Referenzen quellenmarkiert ausgewaehlt"
    ]
  };
}

export function approveDossier(dossier, approver = "Demo-Geschaeftsfuehrung") {
  if (dossier.status !== "ready-for-approval") {
    return {
      ...dossier,
      approval: {
        status: "rejected",
        approver,
        reason: "Dossier enthaelt Blocker und darf nicht freigegeben werden."
      }
    };
  }

  return {
    ...dossier,
    status: "approved",
    approval: {
      status: "approved",
      approver,
      approvedAt: "2026-07-12T15:21:00+02:00",
      note: "Menschliche Demo-Freigabe erteilt. Keine rechtsverbindliche echte Abgabe."
    },
    auditTrail: [...dossier.auditTrail, "Menschliche Freigabe protokolliert"]
  };
}

export function simulateSubmission(approvedDossier) {
  if (approvedDossier.status !== "approved") {
    return {
      status: "not-submitted",
      reason: "Submission-Simulation erfordert vorherige menschliche Freigabe."
    };
  }

  return {
    status: "submitted-simulated",
    portal: "Demo-Portal Sandbox",
    receiptId: `SIM-${approvedDossier.id.toUpperCase()}`,
    submittedAt: "2026-07-12T15:24:00+02:00",
    note: "Keine echte Portalaktion, keine Umgehung von Signatur- oder Portalpflichten."
  };
}

export function simulateAward(approvedDossier, submission) {
  if (submission.status !== "submitted-simulated") {
    return {
      status: "not-evaluated",
      reason: "Keine auswertbare Submission vorhanden."
    };
  }

  const score = approvedDossier.analysis.score;
  const margin = approvedDossier.pricing.grossMarginPercent;
  const winProbability = Math.min(86, Math.round(score * 0.62 + margin * 0.55));
  const awarded = winProbability >= 70;

  return {
    status: awarded ? "awarded-simulated" : "lost-simulated",
    winProbability,
    awardValueEur: awarded ? approvedDossier.pricing.offerPrice : 0,
    decisionAt: "2026-09-06T10:00:00+02:00",
    reason: awarded
      ? "Starker Fit, belastbare Referenzen und plausible Preisposition."
      : "Demo-Scoring reicht nicht fuer simulierten Zuschlag."
  };
}

export function createTestInvoice(company = demoCompany, dossier, award) {
  const successFeePercent = company.commercial.successFeePercent;
  const fee = award.status === "awarded-simulated" ? award.awardValueEur * (successFeePercent / 100) : 0;
  const vat = fee * 0.19;
  const total = roundEuro(fee + vat);

  return {
    status: fee > 0 ? "test-invoice-created" : "no-invoice",
    invoiceNo: fee > 0 ? "TEST-VM-2026-0001" : null,
    netAmountEur: roundEuro(fee),
    vatEur: roundEuro(vat),
    totalEur: total,
    basis: `${successFeePercent}% Erfolgsprovision auf simulierten Zuschlagswert`,
    payment: {
      provider: company.commercial.paymentProviderMode,
      status: fee > 0 ? "sandbox-payment-authorized" : "not-started",
      chargeType: "test-only"
    },
    safetyNote:
      "Keine echte Zahlungsbelastung. Abrechnung nur bei verifiziertem Zuschlag und gueltiger Grundlage."
  };
}

export function learnFromOutcome(dossier, award, invoice) {
  return {
    status: "learning-record-created",
    signals: [
      {
        label: "Fit-Score",
        value: dossier.analysis.score,
        learning: dossier.analysis.score >= 80 ? "Profil passt gut zu Cloud-Betrieb." : "Profil-Schaerfung pruefen."
      },
      {
        label: "Referenzdeckung",
        value: dossier.references.length,
        learning: "Referenzen mit Evidenzstatus bleiben entscheidend fuer Dossier-Qualitaet."
      },
      {
        label: "Billing",
        value: invoice.status,
        learning: "Payment bleibt bis zum echten Abrechnungstatbestand Sandbox-only."
      }
    ],
    nextActions: [
      "Echte Quellenadapter fuer oeffentliche Ausschreibungen kapseln",
      "Freigabeprotokoll mit Rollen und Vier-Augen-Prinzip erweitern",
      "Outcome-Daten getrennt je Kunde speichern"
    ]
  };
}

export function runDemoFlow(company = demoCompany, tender = demoTender) {
  const dossier = createDossier(company, tender);
  const approvedDossier = approveDossier(dossier);
  const submission = simulateSubmission(approvedDossier);
  const award = simulateAward(approvedDossier, submission);
  const invoice = createTestInvoice(company, approvedDossier, award);
  const learning = learnFromOutcome(approvedDossier, award, invoice);

  return {
    company,
    tender,
    dossier,
    approvedDossier,
    submission,
    award,
    invoice,
    learning,
    summary: {
      decision: dossier.analysis.decision,
      fitScore: `${dossier.analysis.score}%`,
      offerPrice: currency.format(dossier.pricing.offerPrice),
      simulatedAward: award.status,
      testInvoice: currency.format(invoice.totalEur)
    }
  };
}

export { demoCompany, demoTender };
