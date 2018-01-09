from django.contrib import admin
from django.urls import path

from web.views import IndexView, FilteredView

urlpatterns = [
    path('', IndexView.as_view()),
    path('filtered/', FilteredView.as_view()),
    path('admin/', admin.site.urls),
]
