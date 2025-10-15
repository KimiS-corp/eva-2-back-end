"""
URL configuration for clinica_salud_vital project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Incluir las URLs de tu app core
    path('', include('core.urls')),
    
    # URLs de autenticación de DRF - SOLO UNA VEZ AQUÍ
    path('api-auth/', include('rest_framework.urls')),
]