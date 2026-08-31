from django.urls import path

from .ai_views import GenerateQuestionsAIView, RandomTestView
from .views import LearnListView, TestSubmitView

urlpatterns = [
    path("modules/", LearnListView.as_view()),
    path("test/submit/", TestSubmitView.as_view()),
    path("modules/<uuid:module_id>/random-test/", RandomTestView.as_view()),
    path("ai/generate-questions/", GenerateQuestionsAIView.as_view()),
]
