from django.urls import path

from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("register/", views.register, name="register"),
    path("my-attempts/", views.my_attempts, name="my_attempts"),
    path("quiz/<slug:slug>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<slug:slug>/start/", views.quiz_start, name="quiz_start"),
    path("attempt/<int:pk>/", views.attempt_take, name="attempt_take"),
    path("attempt/<int:pk>/result/", views.attempt_result, name="attempt_result"),
]
