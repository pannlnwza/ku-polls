"""
Views for the polls application.

This module contains view classes and functions to handle requests for
the polls app.
"""
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import F
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

import logging
from polls.models import Choice, Question, Vote


class IndexView(generic.ListView):
    """
    Displays the list of the published questions.

    Attributes:
        template_name (str): The path to the template that renders the view.
        context_object_name (str): The name of the context object
                                   used in the template.
    """

    template_name = 'polls/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        """
        Return the published questions.

        Not including those set to be published in the future.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class DetailView(generic.DetailView):
    """
    Displays the choices for a poll and allow voting.

    Attributes:
        model (Question): The model associated with this view.
        template_name (str): The path to the template that renders the view.
    """

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """
        Get the question object and render the template.

        Args:
            request: The HTTP request object.
            self.object (int): The ID of the question being voted on.

        Returns:
            HttpResponseRedirect: Redirects to the index page with an error
                                  message if the question is not published.
            HttpResponse: Renders the results page.
        """
        try:
            self.object = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request,
                           f"Poll number {kwargs['pk']} does not exist.")
            return redirect("polls:index")

        # Check if voting is allowed
        if not self.object.can_vote():
            messages.error(request, "This poll is closed.")
            return redirect('polls:index')

        return self.render_to_response(self.get_context_data(
                                       object=self.object))

    def get_context_data(self, **kwargs):
        """Add the previous choice of the user to the context data."""
        context = super().get_context_data(**kwargs)
        question = self.object
        this_user = self.request.user

        if this_user.is_authenticated:
            try:
                previous_vote = Vote.objects.get(user=this_user,
                                                 choice__question=question)
                context['previous_choice'] = previous_vote.choice
            except Vote.DoesNotExist:
                context['previous_choice'] = None
        else:
            context['previous_choice'] = None
        return context


class ResultsView(generic.DetailView):
    """
    Displays the results of a specific question.

    Attributes:
        model (Question): The model associated with this view.
        template_name (str): The path to the template that renders the view.
    """

    model = Question
    template_name = 'polls/results.html'

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for displaying the results of a question.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponseRedirect: Redirects to the index page with an error
                                  message if the question is not published.
            HttpResponse: Renders the results page.
        """
        try:
            self.object = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request,
                           f"Poll number {kwargs['pk']} does not exist.")
            return redirect("polls:index")

        # Redirect to index page if the question is not published
        if not self.object.is_published():
            messages.error(request,
                           f"Poll number {kwargs['pk']} does not exist.")
            return redirect("polls:index")
        return render(request, self.template_name, {"question": self.object})


@login_required
def vote(request, question_id):
    """
    Handle voting for a specific question.

    Args:
        request: The HTTP request object.
        question_id (int): The ID of the question being voted on.

    Returns:
        HttpResponseRedirect: A redirect to the results page
                              if the vote is successful.
        HttpResponse: A render of the detail page with an
                      error message if no choice is selected.
    """
    question = get_object_or_404(Question, pk=question_id)
    this_user = request.user

    logger = logging.getLogger('polls')
    ip_address = get_client_ip(request)

    if not question.can_vote():
        messages.error(request, "This poll is unavailable.")
        logger.warning(f"{this_user.username} attempted to vote on an "
                       f"unavailable poll ({question_id}) from {ip_address}")
        return redirect("polls:index")

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        logger.error(f"No choice selected by {this_user.username} "
                     f"for poll {question_id}")
        # Redisplay the question voting form with an error message
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    try:
        # Find the existing vote by this user
        _vote = Vote.objects.get(user=this_user, choice__question=question)

        # Decrement the vote count for the old choice
        _vote.choice.vote_count = F('vote_count') - 1
        _vote.choice.save()
        # Change the vote to the new choice
        _vote.choice = selected_choice
        _vote.save()
        messages.success(request, f"Your vote was changed "
                         f"to {selected_choice.choice_text}.")
        logger.info(f"{this_user.username} changed vote to "
                    f"{selected_choice.choice_text} ({selected_choice.id}) "
                    f"in poll {question.id}")
    except Vote.DoesNotExist:
        # Create a new vote if the user hasn't voted yet
        _vote = Vote.objects.create(user=this_user, choice=selected_choice)
        messages.success(request, f"You voted for "
                         f"{selected_choice.choice_text}.")
        logger.info(f"{this_user.username} voted for "
                    f"{selected_choice.choice_text} ({selected_choice.id}) "
                    f"in poll {question.id}")

    # Increment the vote count for the new choice
    selected_choice.vote_count = F('vote_count') + 1
    selected_choice.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def get_client_ip(request):
    """Retrieve the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def user_login(sender, request, user, **kwargs):
    """Log a message when a user logs in."""
    ip = get_client_ip(request)
    logger = logging.getLogger('polls')
    logger.info(f"User {user.username} logged in from {ip}")


@receiver(user_logged_out)
def user_logout(sender, request, user, **kwargs):
    """Log a message when a user logs out."""
    ip = get_client_ip(request)
    logger = logging.getLogger('polls')
    logger.info(f"User {user.username} logged out from {ip}")


@receiver(user_login_failed)
def user_login_failed(sender, credentials, request, **kwargs):
    """Log a message when a user login attempt fails."""
    ip = get_client_ip(request)
    logger = logging.getLogger('polls')
    logger.warning(f"Failed login attempt for user "
                   f"{credentials.get('username')} from {ip}")


def signup_view(request):
    """
    Handle the user signup process.

    Returns:
        HttpResponse: The rendered signup page with the form or a redirect to the login page.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
