"""Drug interaction checking service."""

from app.schemas.prescription import (
    DrugInteraction,
    DrugInteractionRequest,
    DrugInteractionResponse,
)

# Known interaction pairs: (drug_a_lower, drug_b_lower) -> interaction
KNOWN_INTERACTIONS = {
    ("warfarin", "aspirin"): DrugInteraction(
        drug_a="Warfarin",
        drug_b="Aspirin",
        severity="major",
        description="Increased risk of bleeding. Aspirin inhibits platelet aggregation and may increase warfarin's anticoagulant effect.",
        mechanism="Additive anticoagulant effect",
        recommendation="Monitor INR closely. Consider alternative analgesic if possible.",
    ),
    ("warfarin", "ibuprofen"): DrugInteraction(
        drug_a="Warfarin",
        drug_b="Ibuprofen",
        severity="major",
        description="Increased risk of GI bleeding and enhanced anticoagulant effect.",
        mechanism="NSAID effect on gastric mucosa + displacement from protein binding",
        recommendation="Avoid combination. Use acetaminophen for pain if appropriate.",
    ),
    ("metformin", "contrast"): DrugInteraction(
        drug_a="Metformin",
        drug_b="Iodinated contrast media",
        severity="moderate",
        description="Risk of lactic acidosis, especially with impaired renal function.",
        mechanism="Reduced renal excretion of metformin",
        recommendation="Hold metformin 48 hours before and after contrast procedure. Check renal function.",
    ),
    ("lisinopril", "spironolactone"): DrugInteraction(
        drug_a="Lisinopril",
        drug_b="Spironolactone",
        severity="major",
        description="Risk of hyperkalemia, especially in patients with renal impairment.",
        mechanism="Both drugs reduce potassium excretion",
        recommendation="Monitor potassium levels. Consider dose adjustment.",
    ),
    ("simvastatin", "clarithromycin"): DrugInteraction(
        drug_a="Simvastatin",
        drug_b="Clarithromycin",
        severity="major",
        description="Increased risk of myopathy and rhabdomyolysis.",
        mechanism="CYP3A4 inhibition increases statin levels",
        recommendation="Avoid combination or use lower statin dose. Consider pravastatin as alternative.",
    ),
    ("fluoxetine", "tramadol"): DrugInteraction(
        drug_a="Fluoxetine",
        drug_b="Tramadol",
        severity="moderate",
        description="Increased risk of serotonin syndrome.",
        mechanism="SSRI + serotonergic opioid",
        recommendation="Monitor for serotonin syndrome symptoms. Consider alternative analgesic.",
    ),
    ("amoxicillin", "warfarin"): DrugInteraction(
        drug_a="Amoxicillin",
        drug_b="Warfarin",
        severity="moderate",
        description="Antibiotics may alter gut flora affecting vitamin K synthesis.",
        mechanism="Reduced vitamin K production by gut bacteria",
        recommendation="Monitor INR during and after antibiotic course.",
    ),
    ("prednisone", "nsaid"): DrugInteraction(
        drug_a="Prednisone",
        drug_b="NSAID",
        severity="moderate",
        description="Increased risk of GI ulceration and bleeding.",
        mechanism="Both agents damage gastric mucosa",
        recommendation="Use PPI prophylaxis. Monitor for GI symptoms.",
    ),
    ("digoxin", "furosemide"): DrugInteraction(
        drug_a="Digoxin",
        drug_b="Furosemide",
        severity="moderate",
        description="Diuretic-induced hypokalemia increases digoxin toxicity risk.",
        mechanism="Hypokalemia enhances digoxin binding to Na+/K+ ATPase",
        recommendation="Monitor potassium and digoxin levels.",
    ),
    ("atorvastatin", "gemfibrozil"): DrugInteraction(
        drug_a="Atorvastatin",
        drug_b="Gemfibrozil",
        severity="major",
        description="Increased risk of severe myopathy and rhabdomyolysis.",
        mechanism="Additive muscle toxicity",
        recommendation="Avoid combination. Use fenofibrate if fibrate therapy needed.",
    ),
    ("phenytoin", "fluconazole"): DrugInteraction(
        drug_a="Phenytoin",
        drug_b="Fluconazole",
        severity="major",
        description="Fluconazole inhibits phenytoin metabolism leading to toxicity.",
        mechanism="CYP2C9/CYP2C19 inhibition",
        recommendation="Monitor phenytoin levels. Consider alternative antifungal.",
    ),
    ("methotrexate", "probenecid"): DrugInteraction(
        drug_a="Methotrexate",
        drug_b="Probenecid",
        severity="contraindicated",
        description="Probenecid reduces methotrexate renal clearance causing severe toxicity.",
        mechanism="Reduced renal tubular secretion",
        recommendation="Contraindicated. Do not use together.",
    ),
    ("sertraline", "linezolid"): DrugInteraction(
        drug_a="Sertraline",
        drug_b="Linezolid",
        severity="contraindicated",
        description="Linezolid is MAO inhibitor. Risk of serotonin syndrome.",
        mechanism="Combined serotonergic activity",
        recommendation="Avoid concurrent use. Washout period required.",
    ),
}


def normalize(drug: str) -> str:
    """Normalize drug name for lookup."""
    return drug.strip().lower().rstrip("s")


def check_interactions(request: DrugInteractionRequest) -> DrugInteractionResponse:
    """Check for drug interactions among the provided medications."""
    drugs = [d.strip() for d in request.drugs]
    normalized = [normalize(d) for d in drugs]
    interactions: list[DrugInteraction] = []

    checked = set()
    for i in range(len(normalized)):
        for j in range(i + 1, len(normalized)):
            pair = tuple(sorted([normalized[i], normalized[j]]))
            if pair in checked:
                continue
            checked.add(pair)

            if pair in KNOWN_INTERACTIONS:
                interactions.append(KNOWN_INTERACTIONS[pair])

    # Also check if any single drug matches a known pair
    for (d_a, d_b), interaction in KNOWN_INTERACTIONS.items():
        if d_a in normalized and d_b in normalized:
            continue  # Already found above

    severity_order = {"minor": 0, "moderate": 1, "major": 2, "contraindicated": 3}
    highest = None
    if interactions:
        highest = max(interactions, key=lambda x: severity_order.get(x.severity, 0)).severity

    if not interactions:
        summary = f"No known interactions found among {len(drugs)} checked medications."
    elif highest == "contraindicated":
        summary = f"CONTRAINDICATED interactions found. Do not co-administer without specialist review."
    elif highest == "major":
        summary = f"Major interactions found. Review therapy and consider alternatives."
    elif highest == "moderate":
        summary = f"Moderate interactions found. Monitor closely and adjust therapy if needed."
    else:
        summary = f"Minor interactions found. Generally manageable with monitoring."

    return DrugInteractionResponse(
        drugs_checked=drugs,
        interactions_found=interactions,
        total_interactions=len(interactions),
        highest_severity=highest,
        summary=summary,
    )
