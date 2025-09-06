from django.urls import path
from .views import GenerateWorkoutView, GeneratePlanView

urlpatterns = [
    path('generate/', GenerateWorkoutView.as_view(), name='workouts-generate'),
    path('plan/', GeneratePlanView.as_view(), name='workouts-plan'),
]
