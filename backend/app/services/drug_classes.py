"""Static drug-class lookup used by the allergy matcher.

This is intentionally small and hand-maintained — not a clinical database.
It buys cross-member matching for the most common allergy pitfalls
(a "Penicillin" allergy should flag "Amoxicillin" because they share the
β-lactam / penicillin class). For anything beyond these, fall back to plain
name substring matching so we don't silently miss explicit allergens.

Each class entry contains a primary `name` (used as a friendly group label
and as one of the lookup tokens) and a tuple of member fragments.
Match is case-insensitive on whole-substring containment of any fragment in
the medication name OR allergen text.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DrugClass:
    """A named drug class with its lookup fragments."""

    name: str
    members: tuple[str, ...]


# Order doesn't matter for matching, but keep groups alphabetical for diffs.
DRUG_CLASSES: tuple[DrugClass, ...] = (
    DrugClass(
        name="ACE inhibitor",
        members=(
            "ace inhibitor",
            "lisinopril",
            "enalapril",
            "ramipril",
            "captopril",
            "benazepril",
            "perindopril",
            "quinapril",
            "fosinopril",
            "trandolapril",
        ),
    ),
    DrugClass(
        name="Cephalosporin",
        members=(
            "cephalosporin",
            "cefazolin",
            "cefuroxime",
            "cefdinir",
            "cefepime",
            "ceftriaxone",
            "cefotaxime",
            "cefixime",
            "cefoxitin",
            "cephalexin",
        ),
    ),
    DrugClass(
        name="NSAID",
        members=(
            "nsaid",
            "ibuprofen",
            "naproxen",
            "diclofenac",
            "ketorolac",
            "meloxicam",
            "celecoxib",
            "indomethacin",
            "aspirin",
            "acetylsalicylic",
        ),
    ),
    DrugClass(
        name="Opioid",
        members=(
            "opioid",
            "morphine",
            "codeine",
            "oxycodone",
            "hydrocodone",
            "hydromorphone",
            "fentanyl",
            "tramadol",
            "methadone",
            "buprenorphine",
            "tapentadol",
        ),
    ),
    DrugClass(
        name="Penicillin",
        members=(
            "penicillin",
            "amoxicillin",
            "ampicillin",
            "dicloxacillin",
            "nafcillin",
            "oxacillin",
            "piperacillin",
            "ticarcillin",
            "augmentin",
            "amoxiclav",
        ),
    ),
    DrugClass(
        name="Statin",
        members=(
            "statin",
            "atorvastatin",
            "simvastatin",
            "rosuvastatin",
            "pravastatin",
            "lovastatin",
            "fluvastatin",
            "pitavastatin",
        ),
    ),
    DrugClass(
        name="Sulfa",
        members=(
            "sulfa",
            "sulfonamide",
            "sulfamethoxazole",
            "trimethoprim",
            "bactrim",
            "septra",
            "co-trimoxazole",
            "sulfadiazine",
            "sulfasalazine",
        ),
    ),
)


def _normalize(text: str) -> str:
    return text.strip().lower()


def classes_for(text: str) -> set[str]:
    """Return the names of every class whose fragments appear in `text`."""
    norm = _normalize(text)
    if not norm:
        return set()
    matches: set[str] = set()
    for cls in DRUG_CLASSES:
        for fragment in cls.members:
            if fragment in norm:
                matches.add(cls.name)
                break
    return matches


def shared_classes(a: str, b: str) -> set[str]:
    """Classes that both strings share — empty if no cross-class hit."""
    return classes_for(a) & classes_for(b)
