from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.full_scope import (
    FullFormulationInput,
    FullFormulationIntelligenceResponse,
    ClassificationResult,
    IPRoutingResult,
    RegulatoryRoutingResult,
    ABSTKRoutingResult,
    KnowledgeGraphGraphData,
    BenchmarkEvaluationReport
)
from app.schemas.source import RetrievalResult
from app.schemas.assistant import Citation
from app.services.database_retriever import DatabaseRetrievalProvider
from app.services.provider_interface import EmbeddingProvider

class FormulationClassificationEngine:
    @staticmethod
    def classify(input_data: FullFormulationInput, retrieved_chunks: List[RetrievalResult]) -> ClassificationResult:
        p_type = input_data.product_type.lower()
        purpose = input_data.purpose.lower()

        missing_facts = []
        if not input_data.proportions:
            missing_facts.append("Exact quantitative ingredient percentage composition")
        if not input_data.preparation_method:
            missing_facts.append("Detailed extraction solvent and manufacturing process details")

        # 1. Ayurveda Aahara Food Category
        if "food" in p_type or "aahara" in p_type or "dietary" in p_type or "nutraceutical" in p_type or "food" in purpose:
            return ClassificationResult(
                classification="AYURVEDA_AAHARA",
                classification_reason="Product is intended for dietary consumption under FSSAI (Ayurveda Aahara) Regulations, 2022.",
                supporting_sources=["DOC-IND-AYU-AAHARA-2022"],
                missing_information=missing_facts,
                review_required=False
            )

        # 2. Cosmetic Category
        if "cosmetic" in p_type or "topical" in p_type or "skin" in purpose or "beauty" in purpose:
            return ClassificationResult(
                classification="COSMETIC",
                classification_reason="Product is intended for external application for cleansing, beautifying, or altering appearance.",
                supporting_sources=["DOC-IND-DCR-1945"],
                missing_information=missing_facts,
                review_required=False
            )

        # 3. Plant Variety Category
        if "plant variety" in p_type or "seed" in p_type or "crop" in p_type or "breeder" in purpose:
            return ClassificationResult(
                classification="PLANT_VARIETY",
                classification_reason="Target subject matter relates to a distinct, uniform, and stable plant variety under PPV&FR Act, 2001.",
                supporting_sources=["DOC-IND-PPVFR-2001"],
                missing_information=missing_facts,
                review_required=False
            )

        # 4. Phytopharmaceutical Category
        if "phytopharmaceutical" in p_type or "purified fraction" in p_type:
            return ClassificationResult(
                classification="PHYTOPHARMACEUTICAL",
                classification_reason="Purified and standardized fraction of medicinal plant extract with minimum 4 active markers under D&C Rules.",
                supporting_sources=["DOC-IND-DCR-1945"],
                missing_information=missing_facts,
                review_required=False
            )

        # 5. Classical Generic Ayurvedic Medicine
        if input_data.is_classical or "classical" in p_type or "churna" in p_type or "kwath" in p_type:
            ref = input_data.classical_reference or "Ayurvedic Pharmacopoeia of India (API)"
            return ClassificationResult(
                classification="CLASSICAL_GENERIC",
                classification_reason=f"Formulation documented in classical Ayurvedic texts ({ref}) without proprietary structural modification.",
                supporting_sources=["DOC-IND-API-FRAMEWORK", "DOC-IND-PAT-1970"],
                missing_information=missing_facts,
                review_required=False
            )

        # 6. Patent / Proprietary Medicine
        if "proprietary" in p_type or "novel" in p_type or "extract" in p_type:
            return ClassificationResult(
                classification="PATENT_OR_PROPRIETARY",
                classification_reason="Proprietary polyherbal combination or extract seeking patent protection or proprietary ASU manufacturing license.",
                supporting_sources=["DOC-IND-PAT-1970", "DOC-IND-DCR-1945"],
                missing_information=missing_facts,
                review_required=False
            )

        return ClassificationResult(
            classification="UNDETERMINED",
            classification_reason="Insufficient formulation facts provided to determine exact regulatory classification.",
            supporting_sources=[],
            missing_information=["Exact product category", "Classical reference status"],
            review_required=True
        )


class FullIPRoutingEngine:
    @staticmethod
    def route_ip(input_data: FullFormulationInput, retrieved_chunks: List[RetrievalResult]) -> List[IPRoutingResult]:
        routes = []

        # 1. Patent Routing
        sec3p_present = any("SEC03P" in c.chunk_id for c in retrieved_chunks)
        routes.append(IPRoutingResult(
            category="Patent",
            relevance="potentially_relevant",
            applicable_framework="The Patents Act, 1970 (§ 3(p), § 3(e), § 10(4)) & Patents Rules 2024",
            evidence_summary="Section 3(p) excludes traditional knowledge and aggregations of known plant properties. Section 3(e) excludes mere admixtures. Section 10(4) requires disclosure of biological material origin.",
            missing_facts=["Proof of non-obvious synergistic efficacy data", "Specific technical extraction process details"],
            next_steps=["Conduct formal TKDL prior art search", "Draft specification including biological source geographical origin"]
        ))

        # 2. Geographical Indications Routing
        routes.append(IPRoutingResult(
            category="Geographical Indications",
            relevance="potentially_relevant" if "geographical" in input_data.purpose.lower() or "regional" in input_data.purpose.lower() else "not_relevant_based_on_current_facts",
            applicable_framework="Geographical Indications of Goods Act, 1999 & GI Rules 2002",
            evidence_summary="Section 9 prohibits registration of generic plant names. Section 18 permits registration of authorized producers of regional botanical goods.",
            missing_facts=["Proof of specific geographical origin link to quality"],
            next_steps=["File Form GI-1 with Geographical Indications Registry Chennai if regional identity exists"]
        ))

        # 3. Trade Marks Routing
        routes.append(IPRoutingResult(
            category="Trade Marks",
            relevance="potentially_relevant",
            applicable_framework="The Trade Marks Act, 1999 (§ 9, § 13) & TM Rules 2017",
            evidence_summary="Section 9 prohibits registration of generic descriptive botanical terms (e.g. 'Ashwagandha Churna'). Section 13 prohibits single-ingredient chemical names.",
            missing_facts=["Proposed brand mark design"],
            next_steps=["Perform trademark clearance search under Rule 25 for coined brand names"]
        ))

        # 4. Designs Routing
        routes.append(IPRoutingResult(
            category="Designs",
            relevance="potentially_relevant",
            applicable_framework="The Designs Act, 2000 (§ 4, § 11) & Designs Rules 2001",
            evidence_summary="Section 4 prohibits registration of non-new functional shapes. Section 11 protects novel industrial shape and configuration of herbal packaging bottles.",
            missing_facts=["Visual 3D design representations of product container"],
            next_steps=["File design registration for novel packaging bottle shapes"]
        ))

        # 5. Copyright Routing
        routes.append(IPRoutingResult(
            category="Copyright",
            relevance="potentially_relevant",
            applicable_framework="The Copyright Act, 1957 (§ 13, § 52)",
            evidence_summary="Section 13 protects original literary text, analytical compilations, and brand artwork. Section 52 permits fair dealing for research.",
            missing_facts=["Original literary label artwork files"],
            next_steps=["Register original brand label artwork with Copyright Office"]
        ))

        # 6. Trade Secrets Routing (Explicit Legal Non-Statutory Note)
        routes.append(IPRoutingResult(
            category="Trade Secret",
            relevance="potentially_relevant",
            applicable_framework="Common Law Breach of Confidence & Contractual Non-Disclosure Principles (No Standalone Trade Secret Statute in India)",
            evidence_summary="India does not have a single standalone Trade Secret statute. Protection relies on non-disclosure agreements (NDAs) and common law breach of confidence principles.",
            missing_facts=["Executed internal NDA protocols"],
            next_steps=["Execute non-disclosure agreements with processing staff and manufacturing partners"]
        ))

        # 7. Plant Varieties Routing
        routes.append(IPRoutingResult(
            category="Plant Variety",
            relevance="potentially_relevant" if "plant variety" in input_data.product_type.lower() else "not_relevant_based_on_current_facts",
            applicable_framework="Protection of Plant Varieties and Farmers' Rights Act, 2001 (§ 15, § 28)",
            evidence_summary="Section 15 grants protection for new plant varieties satisfying Distinctiveness, Uniformity, and Stability (DUS) criteria.",
            missing_facts=["DUS testing trial data"],
            next_steps=["Submit DUS testing application to PPV&FR Authority"]
        ))

        return routes


class FullRegulatoryRoutingEngine:
    @staticmethod
    def route_regulatory(input_data: FullFormulationInput, retrieved_chunks: List[RetrievalResult]) -> List[RegulatoryRoutingResult]:
        routes = []
        p_type = input_data.product_type.lower()

        if "aahara" in p_type or "food" in p_type or "nutraceutical" in p_type:
            routes.append(RegulatoryRoutingResult(
                category="Ayurveda Aahara",
                applicable_framework="FSS (Ayurveda Aahara) Regulations, 2022 (Reg 3, 4, 6)",
                authority="Food Safety and Standards Authority of India (FSSAI)",
                required_licensing_or_form="FSSAI Food Business Operator License & mandatory Ayurveda Aahara logo",
                evidence_summary="Regulation 3 requires compliance with Schedule A classical texts. Regulation 4 mandates advisory warning 'FOR DIETARY USE ONLY'. Regulation 6 prohibits disease cure claims.",
                missing_information=["FSSAI FBO License Number", "Exact label advisory warning format"]
            ))
        else:
            routes.append(RegulatoryRoutingResult(
                category="ASU&H Medicine",
                applicable_framework="Drugs and Cosmetics Act, 1940 (Chapter IVA) & Rules 1945 (Schedule T)",
                authority="State Licensing Authority & CDSCO (Ministry of Ayush)",
                required_licensing_or_form="Form 25D Manufacturing License & Schedule T GMP Certification",
                evidence_summary="Rule 153 mandates application in Form 25D. Schedule T mandates factory hygiene, machinery, and raw material batch testing.",
                missing_information=["State Licensing Authority approval status", "Schedule T GMP Audit Certificate"]
            ))

        routes.append(RegulatoryRoutingResult(
            category="Advertising & Labeling",
            applicable_framework="Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954 (§ 3, § 4) & Rule 161",
            authority="Ministry of Health and Family Welfare & Ministry of Ayush",
            required_licensing_or_form="Mandatory label ingredient disclosure under Rule 161",
            evidence_summary="Section 3 prohibits advertisements claiming cures for specified diseases. Section 4 prohibits misleading claims.",
            missing_information=["Draft commercial advertisement script and label proof"]
        ))

        return routes


class ABSTKRoutingEngine:
    @staticmethod
    def route_abs_tk(input_data: FullFormulationInput, retrieved_chunks: List[RetrievalResult]) -> ABSTKRoutingResult:
        if input_data.applicant_type.lower() != "indian entity" or input_data.foreign_participation:
            return ABSTKRoutingResult(
                abs_relevance="Mandatory NBA Approval Required",
                applicable_provisions="Biological Diversity Act, 2002 (§ 3, § 6) & BD Rules 2024 (Rule 14 / Form I & Form III)",
                authority_and_forms="National Biodiversity Authority (NBA) — Form I (Access) & Form III (IP Filing)",
                tkdl_status_notice="TKDL public framework policies searchable. Detailed TKDL formulation recipes restricted under CSIR non-disclosure agreements and not searched by this system.",
                evidence_summary="Section 3 mandates NBA approval for non-Indian entities or foreign share capital participation accessing Indian bio-resources. Section 6 requires Form III approval prior to IP filing.",
                missing_information=["NBA Form I approval reference number", "Benefit sharing calculation agreement"]
            )
        else:
            return ABSTKRoutingResult(
                abs_relevance="SBB Intimation / Regulatory Compliance Check",
                applicable_provisions="Biological Diversity Act, 2002 (§ 7) & BD Rules 2024",
                authority_and_forms="State Biodiversity Board (SBB) Intimation",
                tkdl_status_notice="TKDL public framework policies searchable. Detailed TKDL formulation recipes restricted under CSIR non-disclosure agreements and not searched by this system.",
                evidence_summary="Indian citizens and domestic entities give intimation to State Biodiversity Board under Section 7 for commercial utilization.",
                missing_information=["State Biodiversity Board intimation record"]
            )


class KnowledgeGraphService:
    @staticmethod
    def generate_graph(input_data: FullFormulationInput) -> KnowledgeGraphGraphData:
        nodes = [
          {"id": "node-formulation", "label": input_data.product_name, "type": "Formulation"},
          {"id": "node-ing-1", "label": input_data.ingredients[0] if input_data.ingredients else "Ashwagandha", "type": "Ingredient"},
          {"id": "node-authority-cgpdtm", "label": "Indian Patent Office (CGPDTM)", "type": "Authority"},
          {"id": "node-authority-nba", "label": "National Biodiversity Authority (NBA)", "type": "Authority"},
          {"id": "node-act-patents", "label": "The Patents Act, 1970", "type": "Regulation"},
          {"id": "node-act-bda", "label": "Biological Diversity Act, 2002", "type": "Regulation"},
          {"id": "node-source-sec3p", "label": "Section 3(p) Traditional Knowledge", "type": "Source"}
        ]
        edges = [
          {"source": "node-formulation", "target": "node-ing-1", "relationship": "contains"},
          {"source": "node-formulation", "target": "node-act-patents", "relationship": "subject_to"},
          {"source": "node-formulation", "target": "node-act-bda", "relationship": "regulated_by"},
          {"source": "node-act-patents", "target": "node-authority-cgpdtm", "relationship": "issued_by"},
          {"source": "node-act-bda", "target": "node-authority-nba", "relationship": "issued_by"},
          {"source": "node-act-patents", "target": "node-source-sec3p", "relationship": "supported_by"}
        ]
        return KnowledgeGraphGraphData(nodes=nodes, edges=edges)
