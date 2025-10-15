"""
MÓDULO: filters.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Define filtros personalizados para la API REST del sistema médico.
Permite filtrar datos por campos específicos y relaciones entre modelos.
Implementa la funcionalidad de filtros requerida en la rúbrica.
"""

import django_filters
from django_filters import rest_framework as filters
from .models import Paciente, Medico, ConsultaMedica, Medicamento, HistorialMedico


# =============================================================================
# BLOQUE 1: FILTROS PARA PACIENTES
# =============================================================================
"""
BLOQUE: Filtros personalizados para el modelo Paciente
OBJETIVO: Permitir filtrado por tipo de sangre y estado activo
"""

class PacienteFilter(django_filters.FilterSet):
    """
    FILTRO: PacienteFilter
    MODELO: Paciente
    PROPÓSITO: Definir filtros personalizados para pacientes
    FUNCIONALIDAD: Filtrado por características médicas y estado
    """
    
    tipo_sangre = django_filters.ChoiceFilter(choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ])
    
    edad_min = django_filters.NumberFilter(method='filter_edad_min', label='Edad mínima')
    edad_max = django_filters.NumberFilter(method='filter_edad_max', label='Edad máxima')
    
    class Meta:
        """
        CLASE Meta: Configuración del filtro
        MODEL: Modelo al que aplica el filtro
        FIELDS: Campos disponibles para filtrado con operadores
        """
        model = Paciente
        fields = {
            'tipo_sangre': ['exact'],
            'activo': ['exact'],
            'fecha_registro': ['gte', 'lte', 'exact', 'year'],
        }
    
    def filter_edad_min(self, queryset, name, value):
        """Filtrar por edad mínima"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        if value:
            min_birth_date = date.today() - relativedelta(years=value)
            return queryset.filter(fecha_nacimiento__lte=min_birth_date)
        return queryset
    
    def filter_edad_max(self, queryset, name, value):
        """Filtrar por edad máxima"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        if value:
            max_birth_date = date.today() - relativedelta(years=value + 1)
            return queryset.filter(fecha_nacimiento__gt=max_birth_date)
        return queryset


# =============================================================================
# BLOQUE 2: FILTROS PARA MÉDICOS
# =============================================================================
"""
BLOQUE: Filtros personalizados para el modelo Medico
OBJETIVO: Permitir filtrado por especialidad y estado activo
"""

class MedicoFilter(django_filters.FilterSet):
    """
    FILTRO: MedicoFilter
    MODELO: Medico
    PROPÓSITO: Definir filtros personalizados para médicos
    FUNCIONALIDAD: Filtrado por especialidad y estado laboral
    """
    
    especialidad = django_filters.NumberFilter(field_name='especialidad__id')
    especialidad_nombre = django_filters.CharFilter(field_name='especialidad__nombre', lookup_expr='icontains')
    
    anos_experiencia_min = django_filters.NumberFilter(method='filter_anos_experiencia', label='Años experiencia mínima')

    class Meta:
        """
        CLASE Meta: Configuración del filtro para médicos
        FIELDS: Incluye filtros por especialidad y estado
        """
        model = Medico
        fields = {
            'especialidad': ['exact'],
            'activo': ['exact'],
            'fecha_contratacion': ['gte', 'lte', 'exact', 'year'],
        }
    
    def filter_anos_experiencia(self, queryset, name, value):
        """Filtrar por años de experiencia mínima"""
        from datetime import date
        if value:
            min_hire_date = date.today().replace(year=date.today().year - value)
            return queryset.filter(fecha_contratacion__lte=min_hire_date)
        return queryset


# =============================================================================
# BLOQUE 3: FILTROS PARA CONSULTAS MÉDICAS
# =============================================================================
"""
BLOQUE: Filtros personalizados para el modelo ConsultaMedica
OBJETIVO: Permitir filtrado por paciente, médico y estado de consulta
"""

class ConsultaMedicaFilter(django_filters.FilterSet):
    """
    FILTRO: ConsultaMedicaFilter
    MODELO: ConsultaMedica
    PROPÓSITO: Definir filtros personalizados para consultas médicas
    FUNCIONALIDAD: Filtrado por participantes y estado de la consulta
    """
    
    paciente = django_filters.NumberFilter(field_name='paciente__id')
    paciente_nombre = django_filters.CharFilter(field_name='paciente__nombre', lookup_expr='icontains')
    medico = django_filters.NumberFilter(field_name='medico__id')
    medico_nombre = django_filters.CharFilter(field_name='medico__nombre', lookup_expr='icontains')
    estado = django_filters.ChoiceFilter(choices=[
        ('PROG', 'Programada'),
        ('CURS', 'En Curso'),
        ('COMP', 'Completada'),
        ('CANC', 'Cancelada')
    ])
    
    fecha_desde = django_filters.DateTimeFilter(field_name='fecha_consulta', lookup_expr='gte')
    fecha_hasta = django_filters.DateTimeFilter(field_name='fecha_consulta', lookup_expr='lte')

    class Meta:
        """
        CLASE Meta: Configuración del filtro para consultas
        FIELDS: Lista explícita de campos filtrables
        """
        model = ConsultaMedica
        fields = ['paciente', 'medico', 'estado']


# =============================================================================
# BLOQUE 4: FILTROS PARA MEDICAMENTOS
# =============================================================================
"""
BLOQUE: Filtros personalizados para el modelo Medicamento
OBJETIVO: Permitir filtrado por stock y laboratorio
"""

class MedicamentoFilter(django_filters.FilterSet):
    """
    FILTRO: MedicamentoFilter
    MODELO: Medicamento
    PROPÓSITO: Definir filtros personalizados para medicamentos
    FUNCIONALIDAD: Filtrado por stock, precio y laboratorio
    """
    
    stock_min = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_max = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    precio_min = django_filters.NumberFilter(field_name='precio_unitario', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio_unitario', lookup_expr='lte')
    stock_bajo = django_filters.BooleanFilter(method='filter_stock_bajo', label='Stock bajo')
    
    class Meta:
        """
        CLASE Meta: Configuración del filtro para medicamentos
        FIELDS: Campos disponibles para filtrado
        """
        model = Medicamento
        fields = {
            'laboratorio': ['exact', 'icontains'],
            'activo': ['exact'],
        }
    
    def filter_stock_bajo(self, queryset, name, value):
        """Filtrar por stock bajo (< 10 unidades)"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


# =============================================================================
# BLOQUE 5: FILTROS PARA HISTORIAL MÉDICO (MEJORA 2)
# =============================================================================
"""
BLOQUE: Filtros personalizados para el modelo HistorialMedico
OBJETIVO: Permitir filtrado por tipo de evento y gravedad
"""

class HistorialMedicoFilter(django_filters.FilterSet):
    """
    FILTRO: HistorialMedicoFilter (MEJORA 2)
    MODELO: HistorialMedico
    PROPÓSITO: Definir filtros personalizados para historial médico
    FUNCIONALIDAD: Filtrado por eventos, gravedad y fechas
    """
    
    paciente = django_filters.NumberFilter(field_name='paciente__id')
    medico_responsable = django_filters.NumberFilter(field_name='medico_responsable__id')
    tipo_evento = django_filters.ChoiceFilter(choices=[
        ('CONSULTA', 'Consulta'),
        ('EXAMEN', 'Examen'),
        ('PROCEDIMIENTO', 'Procedimiento'),
        ('ALERGIA', 'Alergia'),
        ('ENFERMEDAD', 'Enfermedad'),
        ('TRATAMIENTO', 'Tratamiento'),
        ('OTRO', 'Otro')
    ])
    gravedad = django_filters.ChoiceFilter(choices=[
        ('LEVE', 'Leve'),
        ('MODERADO', 'Moderado'),
        ('GRAVE', 'Grave'),
        ('CRITICO', 'Crítico')
    ])
    
    fecha_desde = django_filters.DateTimeFilter(field_name='fecha_evento', lookup_expr='gte')
    fecha_hasta = django_filters.DateTimeFilter(field_name='fecha_evento', lookup_expr='lte')

    class Meta:
        """
        CLASE Meta: Configuración del filtro para historial médico
        FIELDS: Campos disponibles para filtrado
        """
        model = HistorialMedico
        fields = ['paciente', 'medico_responsable', 'tipo_evento', 'gravedad']