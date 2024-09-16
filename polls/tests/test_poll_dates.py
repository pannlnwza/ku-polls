"""
Tests for the Question model's date-related methods.

This module includes tests to ensure the correct behavior of date-related methods
in the Question model.
"""
import datetime
from django.test import TestCase
from django.utils import timezone
from polls.models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text`.

    It is published  with the specified number of `days`
    offset from now (negative for past dates,
    positive for future dates).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class PollDateTest(TestCase):
    """Test cases for the Question model's date-related methods."""

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_future_pub_date(self):
        """Test that is_published returns False for a future pub_date."""
        future_question = create_question(question_text="Future question", days=5)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_past_pub_date(self):
        """Test that is_published returns True for a past pub_date."""
        past_question = create_question(question_text="Past question", days=-5)
        self.assertIs(past_question.is_published(), True)

    def test_is_published_with_now_pub_date(self):
        """Test that is_published returns True when pub_date is now."""
        now_question = create_question(question_text="Now question", days=0)
        self.assertIs(now_question.is_published(), True)
