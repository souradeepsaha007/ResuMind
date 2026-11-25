"""
Automated Test Suite for Resume Verification & Gatekeeping Classifier
=====================================================================
Validates that authentic resumes (IT, non-IT, freshers) pass with high confidence,
while arbitrary random documents (invoices, research papers, legal contracts, recipes)
are strictly intercepted and rejected.
"""

import unittest
from tests import SAMPLE_RESUME_TEXT
from resume_validator import validate_resume_document, assert_valid_resume
from llm_analyzer import analyse_resume


class TestResumeValidator(unittest.TestCase):

    def test_valid_tech_resume(self):
        val = validate_resume_document(SAMPLE_RESUME_TEXT)
        self.assertTrue(val["is_valid"])
        self.assertGreaterEqual(val["confidence_score"], 70.0)
        self.assertEqual(val["document_type"], "Candidate Resume / CV")
        self.assertIn("experience", val["detected_sections"])
        self.assertIn("education", val["detected_sections"])
        self.assertIn("skills", val["detected_sections"])
        self.assertIsNone(val["rejection_reason"])

    def test_valid_non_it_resume(self):
        non_it = """
        Sarah Connor
        Email: sarah.connor@hrsolutions.com | Phone: +1-312-555-0144
        Chicago, IL

        PROFESSIONAL SUMMARY
        Human Resources Generalist with 5+ years of experience managing talent acquisition,
        employee relations, onboarding, and payroll compliance.

        CORE COMPETENCIES
        Recruitment, Talent Acquisition, Employee Relations, Onboarding, Payroll,
        HRIS, Performance Management, Conflict Resolution, Written Communication.

        WORK EXPERIENCE
        HR Specialist | PeopleFirst Corp (2021 - Present)
        - Managed end-to-end recruitment pipelines for 40+ corporate positions annually.
        - Administered employee onboarding workflows and HRIS records with 99% accuracy.

        HR Assistant | TalentBridge LLC (2019 - 2021)
        - Screened candidate applications and scheduled executive interviews.

        EDUCATION
        Bachelor of Business Administration (BBA) in Human Resources
        University of Illinois (2015 - 2019)
        """
        val = validate_resume_document(non_it)
        self.assertTrue(val["is_valid"])
        self.assertGreaterEqual(val["confidence_score"], 75.0)
        self.assertIn("experience", val["detected_sections"])
        self.assertIn("education", val["detected_sections"])

    def test_valid_fresher_resume(self):
        fresher = """
        David Miller
        david.miller@university.edu | +1-415-555-9012 | github.com/dmiller
        San Jose, CA

        CAREER OBJECTIVE
        Motivated Computer Science graduate seeking an entry-level Software Engineer role
        to apply algorithmic problem solving and web application development skills.

        EDUCATION
        B.Tech in Information Technology
        San Jose State University (2022 - 2026) | CGPA: 3.8 / 4.0

        TECHNICAL SKILLS
        Languages: Python, Java, C++, JavaScript, SQL
        Web: React, Node.js, HTML, CSS
        Developer Tools: Git, GitHub, Linux, VS Code

        ACADEMIC PROJECTS
        Campus Event Management System
        - Built full-stack web application using React, FastAPI, and PostgreSQL.
        - Implemented JWT user authentication and automated event ticketing.
        """
        val = validate_resume_document(fresher)
        self.assertTrue(val["is_valid"])
        self.assertGreaterEqual(val["confidence_score"], 70.0)
        self.assertIn("education", val["detected_sections"])
        self.assertIn("skills", val["detected_sections"])
        self.assertIn("projects", val["detected_sections"])

    def test_reject_invoice_document(self):
        invoice = """
        GLOBAL ENTERPRISE SERVICES - TAX INVOICE
        Invoice Number: INV-990234
        Invoice Date: October 14, 2026
        Due Date: November 14, 2026
        Bill To: Acme Technologies Ltd, Floor 4, Cyber City
        Ship To: Acme Technologies Warehouse, Dock 3
        Payment Terms: Net 30 Days

        Line Items:
        1. Cloud Server Virtual Instances - Qty: 10 - Unit Price: $150.00 - Subtotal: $1,500.00
        2. Database Managed Cluster Backup - Qty: 2 - Unit Price: $300.00 - Subtotal: $600.00
        3. Dedicated IP Subnet Allocation - Qty: 4 - Unit Price: $50.00 - Subtotal: $200.00

        Subtotal: $2,300.00
        VAT Registration / GSTIN: 07AAACH1234F1Z5
        Total Amount Payable: $2,300.00
        Remittance Details: Wire Transfer to Standard Bank, SWIFT: STDBUS33
        """
        val = validate_resume_document(invoice)
        self.assertFalse(val["is_valid"])
        self.assertEqual(val["document_type"], "Invoice / Billing Document")
        self.assertIn("Invoice", val["rejection_reason"])

    def test_reject_academic_research_paper(self):
        paper = """
        Proceedings of the International Conference on Machine Learning (ICML 2026)
        Sparse Attention Kernels for Ultra-Low Latency Transformers
        Abstract:
        We present a novel mathematical framework for sparse multi-head self-attention.
        Through structured tensor decomposition, computational complexity is reduced from quadratic to linear.
        Keywords: attention mechanism, transformer networks, tensor decomposition, deep learning.
        1. Introduction and Related Work
        The literature review shows existing models suffer from O(N^2) memory footprint.
        Experimental Results and Methodology:
        Evaluated on standard language modeling benchmarks across 100M parameter models.
        Conclusions and Future Work:
        We plan to extend this pruning method to multimodal generative audio models.
        References [1] Vaswani et al., Attention is all you need, Advances in NeurIPS, 2017. DOI: 10.1145/3345.icml2026
        """
        val = validate_resume_document(paper)
        self.assertFalse(val["is_valid"])
        self.assertEqual(val["document_type"], "Academic Research Paper / Journal Article")
        self.assertIn("Academic Research Paper", val["rejection_reason"])

    def test_reject_legal_contract(self):
        contract = """
        MUTUAL NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT
        This Agreement is made and entered into as of January 1, 2026, by and between
        Alpha Corp ("Disclosing Party") and Beta Labs LLC ("Receiving Party").
        Whereas the parties hereto desire to discuss confidential technical information.
        Now therefore, in consideration of mutual covenants contained herein, witnesseth:
        1. Confidential Information Definition:
        Any proprietary data disclosed directly or indirectly in tangible form.
        2. Governing Law and Jurisdiction:
        This Agreement shall be governed by and construed in accordance with the laws of Delaware.
        3. Indemnification and Severability:
        The Receiving Party agrees to indemnify the Disclosing Party against unauthorized disclosures.
        In witness whereof, the parties have executed this Agreement as of the date first above written.
        """
        val = validate_resume_document(contract)
        self.assertFalse(val["is_valid"])
        self.assertEqual(val["document_type"], "Legal Contract / Agreement")
        self.assertIn("Legal Contract", val["rejection_reason"])

    def test_reject_random_recipe_essay(self):
        recipe = """
        Classic Homemade Lasagna Recipe
        Preheat your oven to 375 degrees Fahrenheit. In a large skillet over medium-high heat,
        brown the ground beef and Italian sausage with minced garlic and diced onions.
        Drain excess fat and stir in marinara sauce, crushed tomatoes, basil, and oregano.
        Simmer gently for 25 minutes to let the flavors meld together.
        In a mixing bowl, combine ricotta cheese with fresh beaten eggs, chopped parsley,
        and grated parmesan cheese. Spread a layer of meat sauce in a 9x13 baking dish,
        followed by lasagna noodles, ricotta mixture, and shredded mozzarella cheese.
        Bake covered for 25 minutes, then uncover and bake for an additional 15 minutes.
        """
        val = validate_resume_document(recipe)
        self.assertFalse(val["is_valid"])
        self.assertEqual(val["document_type"], "Generic Document / Non-Resume")
        self.assertIn("Missing essential resume anchors", val["rejection_reason"])

    def test_reject_too_short_text(self):
        tiny = "Hello world this is a test document."
        val = validate_resume_document(tiny)
        self.assertFalse(val["is_valid"])
        self.assertIn("insufficient readable content", val["rejection_reason"])

    def test_assert_valid_resume_helper(self):
        # Should not raise for valid resume
        assert_valid_resume(SAMPLE_RESUME_TEXT)

        # Should raise ValueError for invoice
        with self.assertRaises(ValueError):
            assert_valid_resume("INVOICE #4029\nBill To: John\nTotal Amount Due: $500\nSubtotal: $500\nDue Date: 12/01/2026")

    def test_llm_analyzer_blocks_invalid_resume(self):
        bad_text = "This is a random recipe with cooking tips. Boil water and add pasta for ten minutes."
        result = analyse_resume(bad_text)
        self.assertIn("Document Verification Alert", result)
        self.assertIn("The submitted document could not be validated", result)


if __name__ == "__main__":
    unittest.main()
