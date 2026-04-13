"""
Synthetic clinical note generator for development and evaluation.

Generates realistic but entirely fictional discharge summaries aligned to WHO ICD-10 style coding.
"""

import random
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class SyntheticNote:
    """A generated clinical note with attached ground-truth metadata."""

    note_id: str
    text: str
    note_type: str
    expected_codes: list[str]
    expected_principal: str
    edge_cases: list[str] = field(default_factory=list)
    template_name: str = ""


_PMH_OPTIONS = [
    "Type 2 diabetes mellitus - on metformin",
    "Hypertension - on amlodipine",
    "Hypercholesterolaemia - on atorvastatin",
    "Atrial fibrillation - on apixaban",
    "Chronic kidney disease stage 3",
    "Asthma - on salbutamol PRN",
    "Previous ischaemic stroke - 2019",
    "Obesity (BMI 34)",
]

_SMOKING_OPTIONS = [
    "Ex-smoker (40 pack-years, quit 2015)",
    "Current smoker (10 cigarettes/day)",
    "Non-smoker",
]


def _pmh_block(n: int = 3) -> str:
    selected = random.sample(_PMH_OPTIONS, min(n, len(_PMH_OPTIONS)))
    return "\n".join(f"- {item}" for item in selected)


_STEMI_WALLS = ["anterior", "inferior", "lateral"]
_STEMI_WALL_CODES = {
    "anterior": ["I21.0"],
    "inferior": ["I21.1"],
    "lateral": ["I21.2"],
}
_STEMI_VESSELS = {
    "anterior": "left anterior descending artery (LAD)",
    "inferior": "right coronary artery (RCA)",
    "lateral": "left circumflex artery (LCx)",
}


def _generate_stemi(
    laterality_specified: bool = True,
    include_dm: bool = True,
    include_aki: bool = True,
) -> SyntheticNote:
    wall = random.choice(_STEMI_WALLS)
    vessel = _STEMI_VESSELS[wall]
    codes = list(_STEMI_WALL_CODES[wall])
    edge_cases = []

    dm_block = ""
    if include_dm:
        codes.append("E11.2")
        dm_block = f"""
{random.randint(2, 5)}. Type 2 diabetes mellitus with nephropathy - HbA1c {random.randint(75,110)} mmol/mol.
   Plan: Continue metformin. Renal follow-up arranged. Lifestyle advice provided."""

    aki_block = ""
    creatinine_peak = random.randint(145, 260)
    if include_aki:
        codes.append("N17.9")
        aki_block = f"""
{random.randint(3, 6)}. Acute kidney injury - creatinine peaked at {creatinine_peak} umol/L post-procedure, likely contrast nephropathy.
   Plan: IV hydration. Creatinine improving at discharge ({creatinine_peak - random.randint(20,50)} umol/L)."""

    note = f"""\
DISCHARGE SUMMARY

PRESENTING COMPLAINT:
{random.choice([
    "Central crushing chest pain radiating to the left arm.",
    "Sudden onset severe chest tightness, associated diaphoresis.",
    "Acute chest pain, 8/10 severity, onset at rest.",
])} Duration approximately {random.randint(1, 6)} hours prior to arrival.

PAST MEDICAL HISTORY:
{_pmh_block()}
{random.choice(_SMOKING_OPTIONS)}

INVESTIGATIONS:
ECG: ST elevation in {wall} leads ({random.randint(2,5)}mm)
Troponin I: {random.uniform(1.5, 8.0):.1f} ng/mL (reference < 0.04)
Echo: {wall.capitalize()} wall hypokinesis, EF {random.randint(38, 50)}%

ASSESSMENT AND PLAN:

1. {wall.capitalize()} acute transmural myocardial infarction - confirmed on ECG and troponin rise.
   Plan: Emergency PCI performed to {vessel}. Drug-eluting stent inserted. Dual antiplatelet therapy commenced.
{dm_block}
{aki_block}

DISCHARGE MEDICATIONS:
Aspirin 75mg daily, Clopidogrel 75mg daily, Ramipril 5mg daily,
Atorvastatin 80mg nocte, Bisoprolol 2.5mg daily

FOLLOW UP:
Cardiology outpatients in 6 weeks. Cardiac rehabilitation referral made.
"""
    return SyntheticNote(
        note_id=f"SYNTH-STEMI-{random.randint(1000,9999)}",
        text=note.strip(),
        note_type="discharge_summary",
        expected_codes=codes,
        expected_principal=_STEMI_WALL_CODES[wall][0],
        edge_cases=edge_cases,
        template_name="STEMI",
    )


def _generate_heart_failure(
    include_acute_on_chronic: bool = True,
    include_afib: bool = True,
) -> SyntheticNote:
    ef = random.randint(20, 65)
    ef_type = "HFrEF (reduced EF)" if ef < 40 else ("HFmrEF (mildly reduced EF)" if ef < 50 else "HFpEF (preserved EF)")
    hf_code = "I50.9"
    timing = "acute-on-chronic" if include_acute_on_chronic else "acute"
    codes = [hf_code]
    edge_cases = []

    if include_acute_on_chronic:
        edge_cases.append("acute_on_chronic_selection")

    afib_block = ""
    if include_afib:
        codes.append("I48.9")
        afib_block = f"""
2. Atrial fibrillation - rate {random.randint(90, 140)} bpm on admission, now rate-controlled.
   Plan: Continue anticoagulation (apixaban). Rate control with bisoprolol."""

    note = f"""\
DISCHARGE SUMMARY

PRESENTING COMPLAINT:
Progressive dyspnoea over {random.randint(3, 14)} days.
{random.choice(["Orthopnoea.", "Paroxysmal nocturnal dyspnoea.", "Ankle swelling noted."])}
Unable to lie flat.

PAST MEDICAL HISTORY:
{_pmh_block()}

INVESTIGATIONS:
CXR: Cardiomegaly, bilateral pleural effusions, upper lobe diversion
BNP: {random.randint(1200, 5000)} pg/mL
Echo: EF {ef}% ({ef_type})

ASSESSMENT AND PLAN:

1. {timing.capitalize()} heart failure ({ef_type}) - decompensated presentation.
   Plan: IV furosemide {random.randint(40,120)}mg daily.
   Fluid restrict to {random.randint(1,2)}L/day. Daily weights.
   Optimise treatment and arrange heart failure follow-up.
{afib_block}

DISCHARGE MEDICATIONS:
Furosemide {random.randint(40,80)}mg daily, Ramipril 5mg BD, Bisoprolol 5mg daily,
Eplerenone 25mg daily, Apixaban 5mg BD

FOLLOW UP:
Heart failure clinic in 2 weeks. Community HF nurse to visit within 48 hours.
"""
    return SyntheticNote(
        note_id=f"SYNTH-HF-{random.randint(1000,9999)}",
        text=note.strip(),
        note_type="discharge_summary",
        expected_codes=codes,
        expected_principal=hf_code,
        edge_cases=edge_cases,
        template_name="HEART_FAILURE",
    )


TEMPLATES: dict[str, Callable[[], SyntheticNote]] = {
    "STEMI": _generate_stemi,
    "HEART_FAILURE": _generate_heart_failure,
}


def generate_note(template_name: str = "STEMI", **kwargs) -> SyntheticNote:
    """Generate a single synthetic clinical note from a named template."""

    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template '{template_name}'. Available: {list(TEMPLATES)}")
    return TEMPLATES[template_name](**kwargs)


def generate_batch(
    n: int = 10,
    templates: list[str] | None = None,
) -> list[SyntheticNote]:
    """Generate n notes, cycling through templates."""

    available = templates or list(TEMPLATES.keys())
    notes = []
    for i in range(n):
        template = available[i % len(available)]
        notes.append(generate_note(template))
    return notes
