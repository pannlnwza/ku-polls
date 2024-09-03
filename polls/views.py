from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Choice, Question


class IndexView(generic.ListView):
    """
    Displays the list of the  published questions.

    Attributes:
        template_name (str): The path to the template that renders the view.
        context_object_name (str): The name of the context object
                                   used in the template.
    """

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    Displays the details of a specific question.

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
        # Get the question object
        self.object = self.get_object()

        # Check if voting is allowed
        if not self.object.can_vote():
            messages.error(request, "This poll is closed.")
            return redirect('polls:index')

        return self.render_to_response(self.get_context_data(
                                        object=self.object))


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
        Handles GET requests for displaying the results of a question.

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

        # Return 404 if the question is not published
        if not self.object.is_published():
            raise Http404("Poll results are not available.")

        return render(request, self.template_name, {"question": self.object})


@login_required
def vote(request, question_id):
    """
    Handles voting for a specific question.

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

    if not question.can_vote():
        messages.error(request, "This poll is unavailable.")
        return redirect("polls:index")

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results',
                                            args=(question.id,)))
