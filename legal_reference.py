# legal_reference.py
#
# A small, hand-verified table of Indian legal citations used by LegalEase.
#
# WHY THIS FILE EXISTS:
# Large language models can "hallucinate" — confidently citing a law or
# section number that sounds correct but is wrong. A wrong citation in a
# real legal notice can get it dismissed by a lawyer or court.
#
# Instead of asking the AI to recall Indian law from memory (which is how
# hallucination happens), we give it a short, verified list of ONLY the
# sections relevant to this product, and instruct it to cite ONLY from
# this list. This does not make the system perfect — Indian law is vast
# and constantly amended — but it removes the most common and avoidable
# class of error: confusing a "goods defect" with a "service deficiency",
# or inventing a section number that does not exist.
#
# IMPORTANT: Always have a human (you, or a lawyer) verify the final
# notice before it is sent. This file is a safety net, not a replacement
# for human legal review — which is exactly why LegalEase has a
# "Human Review" stage before any notice is sent.
#
# Last manually verified: June 2026

LEGAL_REFERENCE_TABLE = """
ISSUE TYPE: Consumer Dispute — Defect in Goods (broken/faulty physical product)
  LAW: Consumer Protection Act, 2019
  CITE: Section 2(10) — defines "defect" in goods
  USE WHEN: the PRODUCT ITSELF is broken, faulty, or not working as intended
  DO NOT confuse this with a service issue — a broken TV screen is a goods defect, not a service deficiency.

ISSUE TYPE: Consumer Dispute — Deficiency of Service (refusal to repair/replace, poor service, delay)
  LAW: Consumer Protection Act, 2019
  CITE: Section 2(11) — defines "deficiency" in service
  USE WHEN: the seller/provider FAILED TO ACT properly — e.g. refused warranty repair,
  gave poor service, delayed unreasonably. The underlying product may be fine or broken;
  this section is about the seller's CONDUCT, not the product.

ISSUE TYPE: Consumer Dispute — Product Liability (seller/manufacturer liable for defective product)
  LAW: Consumer Protection Act, 2019
  CITE: Section 84 to 87 (Product Liability chapter), most commonly Section 86
  USE WHEN: holding a seller or manufacturer financially liable for a defective product
  that does not conform to an express warranty.

ISSUE TYPE: Consumer Dispute — Consumer Rights (safety, information, choice)
  LAW: Consumer Protection Act, 2019
  CITE: Section 2(9) — defines consumer rights including right to safety
  DO NOT cite Section 12 for this — Section 12 is unrelated and refers to administrative
  matters, not consumer rights. Never cite Section 12 in a consumer dispute notice.

ISSUE TYPE: Contract Breach / Non-Payment of Dues (general business or personal contracts)
  LAW: Indian Contract Act, 1872
  CITE: Section 73 — compensation for loss/damage caused by breach of contract
  USE WHEN: someone failed to pay money owed, or broke a contractual promise that is
  NOT specifically a cheque-bounce or consumer-goods matter.

ISSUE TYPE: Cheque Bounce / Dishonour of Cheque
  LAW: Negotiable Instruments Act, 1881
  CITE: Section 138 — dishonour of cheque for insufficiency of funds
  USE WHEN: a cheque issued by the recipient was bounced/dishonoured by the bank.

ISSUE TYPE: Property / Tenancy Dispute (security deposit, eviction, lease issues)
  LAW: Transfer of Property Act, 1882
  CITE: Section 106 — duration and termination of tenancy in absence of a contract
  USE WHEN: a landlord/tenant dispute involves lease termination, notice period, or
  similar tenancy matters NOT covered by a specific state Rent Control Act.
  NOTE: if the dispute is about security deposit non-refund specifically, also reference
  the general right to refund under the lease agreement terms, since deposit refund
  is usually a contractual matter (Indian Contract Act, Section 73) rather than a
  Transfer of Property Act matter. Use judgement on which fits better, and you may cite
  BOTH if genuinely applicable.

ISSUE TYPE: Harassment / Defamation
  LAW: Bharatiya Nyaya Sanhita (BNS), 2023 — replaced the Indian Penal Code (IPC) in 2024
  CITE: Use general language only — e.g. "criminal intimidation and harassment under the
  Bharatiya Nyaya Sanhita, 2023" — DO NOT invent a specific section number for this
  category unless you are highly confident, since harassment/defamation sections vary
  significantly by exact facts. When unsure, describe the conduct factually and state
  that it may attract criminal liability under applicable law, without citing a specific
  section number.

GENERAL RULES (apply to every notice, regardless of issue type):
1. NEVER invent a section number that is not listed above. If a case does not clearly
   match a category above, describe the legal wrong in plain factual language instead
   of forcing an incorrect citation.
2. NEVER threaten "criminal action" for what is purely a civil/consumer matter (e.g. a
   broken product, an unpaid bill, a contract dispute). Criminal threats in a civil
   matter are legally improper and weaken the notice's credibility. Only mention criminal
   liability when the underlying conduct is genuinely criminal in nature (e.g. cheque
   bounce under Section 138, which has criminal consequences by law; or harassment).
3. For consumer goods disputes, ALWAYS check: is this about the PRODUCT (use 2(10)) or
   the SELLER'S CONDUCT (use 2(11))? Many real cases involve both — a defective product
   AND a refusal to honor warranty — in which case cite BOTH sections separately, each
   applied to the correct part of the story.
4. If multiple categories apply, cite each relevant section, but clearly map which
   section applies to which specific fact in the case (do not blend them into one vague
   citation).
"""


def get_legal_reference_block() -> str:
    """Returns the curated legal reference table as a string for prompt injection."""
    return LEGAL_REFERENCE_TABLE


# The exact category labels covered by the verified table above. Used to check
# whether the AI's classification falls inside our verified database or not.
# Keep this list in sync with the "ISSUE TYPE:" headings above.
KNOWN_VERIFIED_CATEGORIES = [
    "Consumer Dispute",
    "Deficiency of Service",
    "Contract Breach",
    "Non-Payment of Dues",
    "Cheque Bounce",
    "Dishonour of Cheque",
    "Property Dispute",
    "Tenancy Dispute",
    "Harassment",
    "Defamation",
]


def is_known_category(issue_type: str) -> bool:
    """
    Checks if the AI's classified issue type matches one of our verified
    legal categories (case-insensitive, partial match). Returns False if
    the case falls outside our verified legal_reference.py database —
    meaning citations in the draft were NOT restricted to a verified table
    and should be reviewed with extra care.
    """
    if not issue_type:
        return False
    issue_lower = issue_type.lower()
    return any(known.lower() in issue_lower for known in KNOWN_VERIFIED_CATEGORIES)
