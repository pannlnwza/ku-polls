"""
Tests for the voting functionality in the polls app.

This module contains test cases to verify that the voting behavior is
consistent with the publication and end dates of questions. It includes
tests for scenarios where voting is allowed or disallowed based on the
question's pub_date and end_date.
"""
import datetime
from django.test import TestCase
from django.utils import timezone
from polls.models import Question


def create_question(question_text, days):
    """
    Create a question with the given question_text and publish it.

    The given number of days offset from now (negative for questions
    published in the past, positive for questions that have yet to be
    published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class VotingTest(TestCase):
    """
    Tests for the voting to ensure that voting behavior is
    consistent with publication and end dates of questions.
    """

    def test_can_vote_before_pub_date(self):
        """Cannot vote before the question's pub_date."""
        question = create_question("Future Question", days=5)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_between_pub_and_end_date(self):
        """Can vote between pub_date and end_date."""
        question = create_question("Active Question", days=-1)
        question.end_date = timezone.now() + datetime.timedelta(days=5)
        question.save()
        self.assertIs(question.can_vote(), True)

    def test_cannot_vote_after_end_date(self):
        """Cannot vote if the end_date is in the past."""
        question = create_question("Expired Question", days=-10)
        question.end_date = timezone.now() - datetime.timedelta(days=1)
        question.save()
        self.assertIs(question.can_vote(), False)

    def test_can_vote_exactly_at_end_date(self):
        """Test that can_vote returns False when the end_date is now."""
        question = create_question("Question ending now", days=-1)
        question.end_date = timezone.now()
        question.save()
        self.assertIs(question.can_vote(), False)
