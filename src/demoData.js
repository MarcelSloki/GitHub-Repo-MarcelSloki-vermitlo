export const demoCompany = {
  id: "company-demo-it-001",
  name: "RheinMain Cloud Solutions GmbH",
  segment: "Mittelstaendischer IT- und Software-Dienstleister",
  location: "Frankfurt am Main",
  certifications: ["ISO 27001", "BSI C5 Type 1", "TISAX"],
  capabilities: [
    "Cloud-Migration",
    "Betrieb kritischer Fachverfahren",
    "DevSecOps",
    "Barrierefreie Webentwicklung",
    "ITIL-Service-Desk",
    "Datenschutz-Folgenabschaetzung"
  ],
  constraints: {
    maxProjectValueEur: 900000,
    minGrossMarginPercent: 24,
    canProvideBidBond: false,
    hasEUHosting: true,
    hasGermanLanguageSupport: true
  },
  commercial: {
    dayRateEur: 980,
    targetMarginPercent: 31,
    successFeePercent: 3.5,
    paymentProviderMode: "sandbox"
  },
  references: [
    {
      id: "ref-gesundheitsamt",
      title: "SaaS-Migration fuer kommunales Gesundheitsamt",
      sector: "Public Health",
      valueEur: 420000,
      year: 2025,
      evidence: "Kundenfreigabe vorhanden, Kurzprofil freigegeben",
      capabilities: ["Cloud-Migration", "Datenschutz-Folgenabschaetzung", "ITIL-Service-Desk"]
    },
    {
      id: "ref-bildung",
      title: "Barrierefreies Fachportal fuer Bildungstraeger",
      sector: "Education",
      valueEur: 280000,
      year: 2024,
      evidence: "Oeffentliche Referenzseite vorhanden",
      capabilities: ["Barrierefreie Webentwicklung", "DevSecOps"]
    },
    {
      id: "ref-energie",
      title: "DevSecOps-Plattform fuer Energieversorger",
      sector: "Utilities",
      valueEur: 610000,
      year: 2025,
      evidence: "NDA: nur anonymisiert verwendbar",
      capabilities: ["DevSecOps", "Betrieb kritischer Fachverfahren", "ISO 27001"]
    }
  ]
};

export const demoTender = {
  id: "tender-demo-2026-07",
  title: "Rahmenvertrag Cloud-Betrieb und Weiterentwicklung Fachverfahren",
  buyer: "Demo-Vergabestelle Stadt Nordhain",
  source: {
    type: "public-demo",
    name: "Synthetische Ausschreibung fuer MVP-Test",
    url: "https://example.invalid/vermitlo-demo/tender-2026-07",
    evidenceStatus: "synthetic"
  },
  deadline: "2026-08-21",
  estimatedValueEur: 735000,
  durationMonths: 24,
  requiredCapabilities: [
    "Cloud-Migration",
    "Betrieb kritischer Fachverfahren",
    "DevSecOps",
    "Barrierefreie Webentwicklung",
    "ITIL-Service-Desk"
  ],
  niceToHaveCapabilities: ["BSI C5 Type 1", "TISAX", "Datenschutz-Folgenabschaetzung"],
  knockOutCriteria: [
    {
      id: "ko-eu-hosting",
      label: "Hosting und Datenverarbeitung innerhalb EU/EWR",
      required: true,
      companyField: "constraints.hasEUHosting"
    },
    {
      id: "ko-language",
      label: "Deutschsprachiger Support werktags 8-18 Uhr",
      required: true,
      companyField: "constraints.hasGermanLanguageSupport"
    },
    {
      id: "ko-bid-bond",
      label: "Bietungsbuergschaft ueber 5 Prozent",
      required: false,
      companyField: "constraints.canProvideBidBond"
    }
  ],
  commercialAssumptions: {
    estimatedPersonDays: 510,
    platformCostsEur: 78000,
    contingencyPercent: 8
  },
  requiredDocuments: [
    "Eigenerklaerung Eignung",
    "Referenzliste mit belastbaren Nachweisen",
    "Preisblatt",
    "Leistungsbeschreibung",
    "Datenschutz- und TOM-Konzept",
    "Freigabeprotokoll"
  ]
};
