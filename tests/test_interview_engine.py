import unittest
from tests import SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION
from interview_engine import generate_interview_test, evaluate_test, generate_interview_pdf_report
from matcher import calculate_match


class TestInterviewAndMatching(unittest.TestCase):

    def test_calculate_match(self):
        result = calculate_match(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)
        self.assertIn("Python", result["resume_skills"])
        self.assertIn("Python", result["matched_skills"])
        self.assertGreater(result["match_score"], 50.0)

    def test_generate_interview_test(self):
        skills = ["Python", "Docker", "SQL"]
        questions = generate_interview_test(skills, "IT & SOFTWARE", num_questions=5)
        self.assertEqual(len(questions), 5)
        for q in questions:
            self.assertIn("question", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(q["correct_idx"], [0, 1, 2, 3])

    def test_evaluate_test(self):
        skills = ["Python", "SQL"]
        questions = generate_interview_test(skills, "IT & SOFTWARE", num_questions=3)
        user_answers = {q["test_id"]: q["correct_idx"] for q in questions}
        result = evaluate_test(questions, user_answers)
        self.assertEqual(result["score_pct"], 100.0)
        self.assertEqual(result["correct_count"], 3)
        self.assertEqual(result["tier"], "Elite Candidate")

    def test_pdf_report_generation(self):
        questions = generate_interview_test(["Python"], "IT & SOFTWARE", num_questions=3)
        user_answers = {questions[0]["test_id"]: questions[0]["correct_idx"]}
        eval_result = evaluate_test(questions, user_answers)
        pdf_bytes = generate_interview_pdf_report("Jane Doe", eval_result)
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 500)


if __name__ == "__main__":
    unittest.main()
