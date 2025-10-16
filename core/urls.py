"""
MÓDULO: urls.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Configuración de URLs para la API REST y panel personalizado.
Define las rutas para todas las vistas del sistema.
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from . import views

# Importaciones para Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Clinica Salud Vital - API",
        default_version='v1',
        description="""
        Sistema de Gestión Médica - Documentación API REST
        
        Esta API permite gestionar:
        - Pacientes y sus historiales médicos
        - Médicos y especialidades  
        - Consultas médicas y tratamientos
        - Medicamentos y recetas médicas
        
        **Autenticación requerida para todas las operaciones**
        """,
        terms_of_service="https://www.clinicasaludvital.com/terms/",
        contact=openapi.Contact(email="soporte@clinicasaludvital.com"),
        license=openapi.License(name="Licencia Propietaria"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Router para API REST
router = DefaultRouter()
router.register(r'especialidades', views.EspecialidadViewSet)
router.register(r'pacientes', views.PacienteViewSet)
router.register(r'medicos', views.MedicoViewSet)
router.register(r'consultas', views.ConsultaMedicaViewSet)
router.register(r'tratamientos', views.TratamientoViewSet)
router.register(r'medicamentos', views.MedicamentoViewSet)
router.register(r'recetas', views.RecetaMedicaViewSet)
router.register(r'historial-medico', views.HistorialMedicoViewSet)

 # URLs para el panel personalizado
panel_patterns = [
    path('', views.dashboard, name='dashboard'),
    path('pacientes/', views.pacientes_list, name='pacientes-list'),
    path('pacientes/nuevo/', views.paciente_create, name='paciente-create'),
    path('pacientes/<int:pk>/editar/', views.paciente_edit, name='paciente-edit'),
    path('pacientes/<int:pk>/eliminar/', views.paciente_delete, name='paciente-delete'),
    path('medicos/', views.medicos_list, name='medicos-list'),
    path('medicos/nuevo/', views.medico_create, name='medico-create'),
    path('medicos/<int:pk>/editar/', views.medico_edit, name='medico-edit'),
    path('medicos/<int:pk>/eliminar/', views.medico_delete, name='medico-delete'),
    path('especialidades/', views.especialidades_list, name='especialidades-list'),
    path('consultas/', views.consultas_list, name='consultas-list'),
    path('consultas/nuevo/', views.consulta_create, name='consulta-create'), 
    path('medicamentos/', views.medicamentos_list, name='medicamentos-list'),
    path('tratamientos/', views.tratamientos_list, name='tratamientos-list'),
    path('tratamientos/nuevo/', views.tratamiento_create, name='tratamiento-create'), 
    path('recetas/nuevo/<int:tratamiento_id>/', views.receta_create, name='receta-create'), 
    path('recetas/', views.recetas_list, name='recetas-list'),
    path('documentacion/', views.documentacion_api, name='documentacion-api')
]

urlpatterns = [
    # API REST (accesible en /api/...)
    path('api/', include(router.urls)),
    
    # Panel personalizado (accesible en /panel/...)
    path('panel/', include(panel_patterns)),
    
    # Redirección desde raíz al panel
    path('', RedirectView.as_view(url='/panel/', permanent=False)),
    
    # Documentación Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]