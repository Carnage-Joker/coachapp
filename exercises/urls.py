from django.urls import path
from .views import ExerciseListView, ExerciseSchemaView

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercises-list'),
    path('schema/', ExerciseSchemaView.as_view(), name='exercises-schema'),
]
