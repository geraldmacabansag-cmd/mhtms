from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('triage/', include('triage.urls')),
    path('api/v1/', include('api.urls')),
]

from mhtms.error_handlers import handler403, handler404, handler500
handler403 = handler403
handler404 = handler404
handler500 = handler500
