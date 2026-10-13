from django.urls import path
from . import views

app_name = "ai"




urlpatterns = [
    path("", views.ai_page, name="generator"),
    path("generate/", views.generate_image, name="generate"),
    path("status/", views.generation_status, name="status"),
    path("history/", views.generation_history, name="history"),
    path(
        "download/<int:pk>/",
        views.download_image,
        name="download",
    ),
    path(
        "history/<int:pk>/delete/",
        views.delete_image,
        name="delete",
),

    path(
        "history/<int:pk>/delete/",
        views.delete_image,
        name="delete",
),

]
