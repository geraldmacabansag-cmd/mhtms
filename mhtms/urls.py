from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('triage/', include('triage.urls')),
    path('api/v1/', include('api.urls')),
    # ── JWT token endpoints (Member 2) ────────────────────────────────
    # POST /api/token/          → send username+password → get access+refresh tokens
    # POST /api/token/refresh/  → send refresh token    → get new access token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

from mhtms.error_handlers import handler403, handler404, handler500
handler403 = handler403
handler404 = handler404
handler500 = handler500

from mhtms.error_handlers import handler403, handler404, handler500
handler403 = handler403
handler404 = handler404
handler500 = handler500
