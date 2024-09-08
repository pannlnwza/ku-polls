import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib import admin


class Question(models.Model):
    """
    Represents a poll question.

    Attributes:
        question_text (str): The text of the question.
        pub_date (datetime): The date and time when the question was published.
        end_date (datetime): The date and time when the question will be ended.
    """

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('date ended', null=True, blank=True)

    def is_published(self):
        """Returns True if the current date is on or after the pub_date."""
        return timezone.now() >= self.pub_date

    def can_vote(self):
        """Returns True if voting is allowed."""
        now = timezone.now()
        return (self.pub_date <= now and
                (self.end_date is None or now <= self.end_date))

    def __str__(self) -> str:
        """Returns the string of the question."""
        return str(self.question_text)

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self) -> bool:
        """
        Determines if the question was published within the last day.

        Returns:
            bool: True if the question was published within the last day,
                  False otherwise.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    """
    Represents a choice for the specific poll question.

    Attributes:
        question (Question): The poll question that this choice belongs to.
        choice_text (str): The text of the choice.
        vote_count (int): The number of votes the choice has received.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    vote_count = models.IntegerField(default=0)

    @property
    def votes(self):
        """Returns the number of time choice has been voted."""
        return self.vote_set.count()

    def __str__(self) -> str:
        """Returns the string representation of the choice."""
        return str(self.choice_text)


class Vote(models.Model):
    """A vote by a user for a choice in a poll."""

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
