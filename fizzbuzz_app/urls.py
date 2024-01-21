from django.urls import path
from .views import FizzBuzzView

urlpatterns = [
    path('fizzbuzz/', FizzBuzzView.as_view(), name='fizzbuzz'),
    # Statistics endpoint
    path('statistics/', FizzBuzzView.statistics_endpoint, name='statistics')
]
