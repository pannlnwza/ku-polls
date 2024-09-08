import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from polls.models import Question, Choice
from mysite import settings


class UserAuthTest(django.test.TestCase):
    """
    Test cases for user authentication and voting functionality in the polls app.
    """

    def setUp(self):
        # superclass setUp creates a Client object and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
                         username=self.username,
                         password=self.password,
                         email="testuser@nowhere.com"
                         )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1,4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q
        self.choice1 = self.question.choice_set.first()
        self.choice2 = self.question.choice_set.last()

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue( 
              self.client.login(username=self.username, password=self.password)
                       )
        # visit the logout page
        form_data = {}
        response = self.client.post(logout_url, form_data)
        self.assertEqual(302, response.status_code)
        
        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser", 
                     "password": "FatChance!"
                    }
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
        or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)

    def test_cannot_login_invalid_password(self):
        """A user cannot login with an incorrect password."""
        login_url = reverse("login")
        form_data = {"username": self.username, "password": "WrongPassword!"}
        response = self.client.post(login_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Please enter a correct username and password.")

    def test_user_can_change_vote_during_voting_period(self):
        """
        A user can change their vote during the voting period,
        and the new vote replaces the old vote.
        """
        # Log in the user
        self.client.login(username=self.username, password=self.password)
        vote_url = reverse('polls:vote', args=[self.question.id])

        # Cast the initial vote for choice1
        self.client.post(vote_url, {'choice': self.choice1.id})
        self.choice1.refresh_from_db()  # Refresh to get the latest vote count

        # Verify that the initial choice has one vote
        self.assertEqual(self.choice1.vote_count, 1)
        self.assertEqual(self.choice2.vote_count, 0)

        # Change the vote to choice2
        response = self.client.post(vote_url, {'choice': self.choice2.id})
        self.assertEqual(response.status_code, 302)  # Successful vote, should redirect

        self.choice1.refresh_from_db()
        self.choice2.refresh_from_db()

        # Verify that the vote count has been updated correctly
        self.assertEqual(self.choice1.vote_count, 0)  # The previous choice should now have 0 votes
        self.assertEqual(self.choice2.vote_count, 1)  # The new choice should have 1 vote

    def test_cannot_vote_when_not_logged_in(self):
        """An unauthenticated user cannot vote and is redirected to the login page."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        response = self.client.post(vote_url, {'choice': self.choice1.id})
        self.assertRedirects(response, f"{reverse('login')}?next={vote_url}")