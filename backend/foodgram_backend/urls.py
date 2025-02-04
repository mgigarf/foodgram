from django.contrib import admin
from django.urls import include, path

from api.views import redirect_to_recipe_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        's/<slug:short_link_code>/',
        redirect_to_recipe_detail,
        name='short_link_redirect'
    )
]
