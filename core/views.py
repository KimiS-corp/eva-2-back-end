"""
MÓDULO: views.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Define las vistas API para el sistema de gestión médica.
Implementa operaciones CRUD completas para todos los modelos.
Incluye filtros y búsquedas para una API robusta.
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count
from django.utils import timezone

from .models import Especialidad, Paciente, Medico, ConsultaMedica, Tratamiento, Medicamento, RecetaMedica, HistorialMedico
from .serializers import (
    EspecialidadSerializer, PacienteSerializer, MedicoSerializer, 
    ConsultaMedicaSerializer, TratamientoSerializer, MedicamentoSerializer, 
    RecetaMedicaSerializer, HistorialMedicoSerializer
)
from .filters import PacienteFilter, MedicoFilter, ConsultaMedicaFilter
from .forms import PacienteForm, MedicoForm, EspecialidadForm, ConsultaMedicaForm, MedicamentoForm, MedicamentoForm, TratamientoForm, RecetaMedicaForm 


# =============================================================================
# BLOQUE 1: VISTAS API CON DRF
# =============================================================================

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PacienteFilter
    search_fields = ['nombre', 'apellido', 'rut']

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = MedicoFilter
    search_fields = ['nombre', 'apellido', 'rut']

class ConsultaMedicaViewSet(viewsets.ModelViewSet):
    queryset = ConsultaMedica.objects.all()
    serializer_class = ConsultaMedicaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConsultaMedicaFilter

class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer

class MedicamentoViewSet(viewsets.ModelViewSet):
    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'laboratorio']

class RecetaMedicaViewSet(viewsets.ModelViewSet):
    queryset = RecetaMedica.objects.all()
    serializer_class = RecetaMedicaSerializer

class HistorialMedicoViewSet(viewsets.ModelViewSet):
    queryset = HistorialMedico.objects.all()
    serializer_class = HistorialMedicoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['paciente', 'medico_responsable', 'tipo_evento', 'gravedad']


# =============================================================================
# VISTAS PARA EL PANEL PERSONALIZADO
# =============================================================================

@login_required
def dashboard(request):
    """
    VISTA: Dashboard principal
    PROPÓSITO: Mostrar estadísticas y resumen del sistema
    TEMPLATE: core/panel/dashboard.html
    """
    # Estadísticas generales
    stats = {
        'total_pacientes': Paciente.objects.count(),
        'total_medicos': Medico.objects.filter(activo=True).count(),
        'total_especialidades': Especialidad.objects.count(),
        'total_consultas': ConsultaMedica.objects.count(),
        'consultas_hoy': ConsultaMedica.objects.filter(
            fecha_consulta__date=timezone.now().date()
        ).count(),
        'medicamentos_stock_bajo': Medicamento.objects.filter(stock__lt=10).count(),
        'total_tratamientos': Tratamiento.objects.count(),
        'total_recetas': RecetaMedica.objects.count(),
    }
    
    # Últimas consultas para el dashboard
    ultimas_consultas = ConsultaMedica.objects.select_related(
        'paciente', 'medico'
    ).order_by('-fecha_consulta')[:5]
    
    # Médicos más activos
    medicos_activos = Medico.objects.filter(activo=True)[:5]
    
    context = {
        'stats': stats,
        'ultimas_consultas': ultimas_consultas,
        'medicos_activos': medicos_activos,
    }
    return render(request, 'core/panel/dashboard.html', context)

@login_required
@permission_required('core.view_paciente', raise_exception=True)
def pacientes_list(request):
    """
    VISTA: Lista de pacientes con paginación y búsqueda
    PROPÓSITO: Mostrar todos los pacientes con opciones de filtrado
    TEMPLATE: core/panel/pacientes-list.html
    """
    pacientes_list = Paciente.objects.all().order_by('apellido', 'nombre')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        pacientes_list = pacientes_list.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(rut__icontains=query) |
            Q(correo__icontains=query)
        )
    
    # Filtro por estado activo
    activo_filter = request.GET.get('activo')
    if activo_filter in ['true', 'false']:
        pacientes_list = pacientes_list.filter(activo=activo_filter == 'true')
    
    # Paginación
    paginator = Paginator(pacientes_list, 10)
    page_number = request.GET.get('page')
    pacientes = paginator.get_page(page_number)
    
    return render(request, 'core/panel/pacientes-list.html', {
        'pacientes': pacientes,
        'query': query,
        'activo_filter': activo_filter
    })

@login_required
@permission_required('core.add_paciente', raise_exception=True)
def paciente_create(request):
    """
    VISTA: Crear nuevo paciente
    PROPÓSITO: Formulario para registrar nuevos pacientes
    TEMPLATE: core/panel/paciente-form.html
    """
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente creado exitosamente')
            return redirect('pacientes-list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = PacienteForm()
    
    return render(request, 'core/panel/paciente-form.html', {'form': form})

@login_required
@permission_required('core.change_paciente', raise_exception=True)
def paciente_edit(request, pk):
    """
    VISTA: Editar paciente existente
    PROPÓSITO: Formulario para modificar datos de paciente
    TEMPLATE: core/panel/paciente-form.html
    """
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado exitosamente')
            return redirect('pacientes-list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'core/panel/paciente-form.html', {
        'form': form,
        'paciente': paciente
    })

@login_required
@permission_required('core.delete_paciente', raise_exception=True)
def paciente_delete(request, pk):
    """
    VISTA: Eliminar paciente
    PROPÓSITO: Confirmar y eliminar paciente del sistema
    TEMPLATE: core/panel/paciente-delete.html
    """
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado exitosamente')
        return redirect('pacientes-list')
    
    return render(request, 'core/panel/paciente-delete.html', {'paciente': paciente})

@login_required
@permission_required('core.view_medico', raise_exception=True)
def medicos_list(request):
    """
    VISTA: Lista de médicos con especialidades
    PROPÓSITO: Mostrar todos los médicos con sus especialidades
    TEMPLATE: core/panel/medicos-list.html
    """
    medicos_list = Medico.objects.select_related('especialidad').all().order_by('apellido', 'nombre')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        medicos_list = medicos_list.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(rut__icontains=query) |
            Q(especialidad__nombre__icontains=query)
        )
    
    # Filtro por especialidad
    especialidad_id = request.GET.get('especialidad')
    if especialidad_id:
        medicos_list = medicos_list.filter(especialidad_id=especialidad_id)
    
    # Paginación
    paginator = Paginator(medicos_list, 10)
    page_number = request.GET.get('page')
    medicos = paginator.get_page(page_number)
    
    especialidades = Especialidad.objects.all()
    
    return render(request, 'core/panel/medicos-list.html', {
        'medicos': medicos,
        'especialidades': especialidades,
        'query': query,
        'especialidad_id': especialidad_id
    })

@login_required
@permission_required('core.add_medico', raise_exception=True)
def medico_create(request):
    """
    VISTA: Crear nuevo médico
    PROPÓSITO: Formulario para registrar nuevos médicos
    TEMPLATE: core/panel/medico-form.html
    """
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico creado exitosamente')
            return redirect('medicos-list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = MedicoForm()
    
    return render(request, 'core/panel/medico-form.html', {'form': form})

@login_required
@permission_required('core.change_medico', raise_exception=True)
def medico_edit(request, pk):
    """
    VISTA: Editar médico existente
    PROPÓSITO: Formulario para modificar datos de médico
    TEMPLATE: core/panel/medico-form.html
    """
    medico = get_object_or_404(Medico, pk=pk)
    
    if request.method == 'POST':
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico actualizado exitosamente')
            return redirect('medicos-list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = MedicoForm(instance=medico)
    
    return render(request, 'core/panel/medico-form.html', {
        'form': form,
        'medico': medico
    })

@login_required
@permission_required('core.delete_medico', raise_exception=True)
def medico_delete(request, pk):
    """
    VISTA: Eliminar médico
    PROPÓSITO: Confirmar y eliminar médico del sistema
    TEMPLATE: core/panel/medico-delete.html
    """
    medico = get_object_or_404(Medico, pk=pk)
    
    if request.method == 'POST':
        medico.delete()
        messages.success(request, 'Médico eliminado exitosamente')
        return redirect('medicos-list')
    
    return render(request, 'core/panel/medico-delete.html', {'medico': medico})

@login_required
def especialidades_list(request):
    """
    VISTA: Lista de especialidades médicas
    PROPÓSITO: Mostrar y gestionar especialidades
    TEMPLATE: core/panel/especialidades-list.html
    """
    especialidades_list = Especialidad.objects.annotate(
        total_medicos=Count('medico')
    ).order_by('nombre')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        especialidades_list = especialidades_list.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    paginator = Paginator(especialidades_list, 10)
    page_number = request.GET.get('page')
    especialidades = paginator.get_page(page_number)
    
    return render(request, 'core/panel/especialidades-list.html', {
        'especialidades': especialidades,
        'query': query
    })

@login_required
def consultas_list(request):
    """
    VISTA: Lista de consultas médicas
    PROPÓSITO: Mostrar historial de consultas con filtros
    TEMPLATE: core/panel/consultas-list.html
    """
    consultas_list = ConsultaMedica.objects.select_related(
        'paciente', 'medico', 'medico__especialidad'
    ).order_by('-fecha_consulta')
    
    # Filtros
    paciente_id = request.GET.get('paciente')
    medico_id = request.GET.get('medico')
    estado = request.GET.get('estado')
    
    if paciente_id:
        consultas_list = consultas_list.filter(paciente_id=paciente_id)
    if medico_id:
        consultas_list = consultas_list.filter(medico_id=medico_id)
    if estado:
        consultas_list = consultas_list.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(consultas_list, 10)
    page_number = request.GET.get('page')
    consultas = paginator.get_page(page_number)
    
    pacientes = Paciente.objects.all()
    medicos = Medico.objects.filter(activo=True)
    
    return render(request, 'core/panel/consultas-list.html', {
        'consultas': consultas,
        'pacientes': pacientes,
        'medicos': medicos,
        'filtros': {
            'paciente_id': paciente_id,
            'medico_id': medico_id,
            'estado': estado
        }
    })

@login_required
def medicamentos_list(request):
    """
    VISTA: Lista de medicamentos en inventario
    PROPÓSITO: Gestionar inventario de medicamentos
    TEMPLATE: core/panel/medicamentos-list.html
    """
    medicamentos_list = Medicamento.objects.all().order_by('nombre')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        medicamentos_list = medicamentos_list.filter(
            Q(nombre__icontains=query) |
            Q(laboratorio__icontains=query)
        )
    
    # Filtro por stock bajo
    stock_bajo = request.GET.get('stock_bajo')
    if stock_bajo:
        medicamentos_list = medicamentos_list.filter(stock__lt=10)
    
    paginator = Paginator(medicamentos_list, 10)
    page_number = request.GET.get('page')
    medicamentos = paginator.get_page(page_number)
    
    return render(request, 'core/panel/medicamentos-list.html', {
        'medicamentos': medicamentos,
        'query': query,
        'stock_bajo': stock_bajo
    })

@login_required
def documentacion_api(request):
    """
    VISTA: Documentación personalizada de la API
    PROPÓSITO: Mostrar documentación cuando Swagger falle
    TEMPLATE: core/panel/documentacion.html
    """
    return render(request, 'core/panel/documentacion.html')

# =============================================================================
# VISTAS PARA TRATAMIENTOS (AGREGAR AL FINAL)
# =============================================================================

@login_required
@permission_required('core.view_tratamiento', raise_exception=True)
def tratamientos_list(request):
    """
    VISTA: Lista de tratamientos médicos
    PROPÓSITO: Mostrar todos los tratamientos con sus consultas
    TEMPLATE: core/panel/tratamientos-list.html
    """
    tratamientos_list = Tratamiento.objects.select_related(
        'consulta', 'consulta__paciente', 'consulta__medico'
    ).all().order_by('-fecha_inicio')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        tratamientos_list = tratamientos_list.filter(
            Q(descripcion__icontains=query) |
            Q(consulta__paciente__nombre__icontains=query) |
            Q(consulta__paciente__apellido__icontains=query) |
            Q(observaciones__icontains=query)
        )
    
    # Filtro por paciente
    paciente_id = request.GET.get('paciente')
    if paciente_id:
        tratamientos_list = tratamientos_list.filter(consulta__paciente_id=paciente_id)
    
    # Paginación
    paginator = Paginator(tratamientos_list, 10)
    page_number = request.GET.get('page')
    tratamientos = paginator.get_page(page_number)
    
    pacientes = Paciente.objects.all()
    
    return render(request, 'core/panel/tratamientos-list.html', {
        'tratamientos': tratamientos,
        'pacientes': pacientes,
        'query': query,
        'paciente_id': paciente_id
    })

# =============================================================================
# VISTAS PARA RECETAS MÉDICAS
# =============================================================================

@login_required
@permission_required('core.view_recetamedica', raise_exception=True)
def recetas_list(request):
    """
    VISTA: Lista de recetas médicas
    PROPÓSITO: Mostrar todas las recetas con tratamientos y medicamentos
    TEMPLATE: core/panel/recetas-list.html
    """
    recetas_list = RecetaMedica.objects.select_related(
        'tratamiento', 'tratamiento__consulta', 'tratamiento__consulta__paciente', 'medicamento'
    ).all().order_by('-fecha_prescripcion')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        recetas_list = recetas_list.filter(
            Q(medicamento__nombre__icontains=query) |
            Q(tratamiento__consulta__paciente__nombre__icontains=query) |
            Q(tratamiento__consulta__paciente__apellido__icontains=query) |
            Q(dosis__icontains=query)
        )
    
    # Filtro por paciente
    paciente_id = request.GET.get('paciente')
    if paciente_id:
        recetas_list = recetas_list.filter(tratamiento__consulta__paciente_id=paciente_id)
    
    # Filtro por medicamento
    medicamento_id = request.GET.get('medicamento')
    if medicamento_id:
        recetas_list = recetas_list.filter(medicamento_id=medicamento_id)
    
    # Paginación
    paginator = Paginator(recetas_list, 10)
    page_number = request.GET.get('page')
    recetas = paginator.get_page(page_number)
    
    pacientes = Paciente.objects.all()
    medicamentos = Medicamento.objects.all()
    
    return render(request, 'core/panel/recetas-list.html', {
        'recetas': recetas,
        'pacientes': pacientes,
        'medicamentos': medicamentos,
        'query': query,
        'paciente_id': paciente_id,
        'medicamento_id': medicamento_id
    })
# =============================================================================
# VISTAS PARA CREAR CONSULTAS, TRATAMIENTOS Y RECETAS
# =============================================================================

@login_required
@permission_required('core.add_consultamedica', raise_exception=True)
def consulta_create(request):
    """
    VISTA: Crear nueva consulta médica
    PROPÓSITO: Formulario para registrar nuevas consultas
    TEMPLATE: core/panel/consulta-form.html
    """
    if request.method == 'POST':
        form = ConsultaMedicaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta médica creada exitosamente')
            return redirect('consultas-list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ConsultaMedicaForm()
    
    return render(request, 'core/panel/consulta-form.html', {'form': form})

@login_required
@permission_required('core.add_tratamiento', raise_exception=True)
def tratamiento_create(request):
    """
    VISTA: Crear nuevo tratamiento
    PROPÓSITO: Formulario para crear tratamientos desde una consulta
    TEMPLATE: core/panel/tratamiento-form.html
    """
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save()
            messages.success(request, 'Tratamiento creado exitosamente')
            # Redirigir a crear receta para este tratamiento
            return redirect('receta-create', tratamiento_id=tratamiento.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = TratamientoForm()
    
    return render(request, 'core/panel/tratamiento-form.html', {'form': form})

@login_required
@permission_required('core.add_recetamedica', raise_exception=True)
def receta_create(request, tratamiento_id):
    """
    VISTA: Crear receta para un tratamiento
    PROPÓSITO: Formulario para agregar medicamentos a un tratamiento
    TEMPLATE: core/panel/receta-form.html
    """
    tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id)
    
    if request.method == 'POST':
        form = RecetaMedicaForm(request.POST)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.tratamiento = tratamiento
            receta.save()
            messages.success(request, 'Receta médica creada exitosamente')
            return redirect('tratamientos-list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = RecetaMedicaForm(initial={'tratamiento': tratamiento})
    
    return render(request, 'core/panel/receta-form.html', {
        'form': form,
        'tratamiento': tratamiento
    })