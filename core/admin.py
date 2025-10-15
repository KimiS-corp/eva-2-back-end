"""
MÓDULO: admin.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Configuración del panel de administración de Django para todos los modelos del sistema.
Permite la gestión CRUD de entidades médicas a través de la interfaz administrativa.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Especialidad, Paciente, Medico, ConsultaMedica, Tratamiento, Medicamento, RecetaMedica, HistorialMedico


# =============================================================================
# BLOQUE 1: CONFIGURACIÓN DEL PANEL ADMINISTRATIVO
# =============================================================================

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    """
    CLASE: EspecialidadAdmin
    PROPÓSITO: Configurar la interfaz admin para el modelo Especialidad
    FUNCIONALIDAD: Define qué campos mostrar en la lista del admin
    """
    list_display = ['nombre', 'descripcion_corta', 'total_medicos']
    search_fields = ['nombre', 'descripcion']
    
    def descripcion_corta(self, obj):
        """Mostrar descripción corta en la lista"""
        return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = "Descripción"
    
    def total_medicos(self, obj):
        """Mostrar total de médicos en la especialidad"""
        return obj.medico_set.count()
    total_medicos.short_description = "Total Médicos"


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """
    CLASE: PacienteAdmin  
    PROPÓSITO: Configurar la interfaz admin para el modelo Paciente
    FUNCIONALIDAD: Muestra información clave del paciente en listados
    """
    list_display = ['rut', 'nombre_completo', 'tipo_sangre', 'edad', 'activo', 'fecha_registro']
    list_filter = ['tipo_sangre', 'activo', 'fecha_registro']
    search_fields = ['rut', 'nombre', 'apellido', 'correo']
    readonly_fields = ['fecha_registro']
    date_hierarchy = 'fecha_registro'
    
    def nombre_completo(self, obj):
        """Mostrar nombre completo"""
        return f"{obj.nombre} {obj.apellido}"
    nombre_completo.short_description = "Nombre Completo"
    
    def edad(self, obj):
        """Calcular y mostrar edad"""
        from datetime import date
        if obj.fecha_nacimiento:
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return "N/A"
    edad.short_description = "Edad"


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    """
    CLASE: MedicoAdmin
    PROPÓSITO: Configurar la interfaz admin para el modelo Medico
    FUNCIONALIDAD: Visualización de datos médicos y especialidad
    """
    list_display = ['rut', 'nombre_completo', 'especialidad', 'activo', 'total_consultas', 'fecha_contratacion']
    list_filter = ['especialidad', 'activo', 'fecha_contratacion']
    search_fields = ['rut', 'nombre', 'apellido', 'especialidad__nombre']
    readonly_fields = ['fecha_contratacion']
    
    def nombre_completo(self, obj):
        """Mostrar nombre completo con título"""
        return f"Dr. {obj.nombre} {obj.apellido}"
    nombre_completo.short_description = "Médico"
    
    def total_consultas(self, obj):
        """Mostrar total de consultas del médico"""
        return obj.consultamedica_set.count()
    total_consultas.short_description = "Total Consultas"


@admin.register(ConsultaMedica)
class ConsultaMedicaAdmin(admin.ModelAdmin):
    """
    CLASE: ConsultaMedicaAdmin
    PROPÓSITO: Configurar la interfaz admin para el modelo ConsultaMedica
    FUNCIONALIDAD: Seguimiento de consultas y estados
    """
    list_display = ['paciente', 'medico', 'fecha_consulta', 'estado_badge', 'motivo_corto']
    list_filter = ['estado', 'fecha_consulta', 'medico__especialidad']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'medico__nombre', 'motivo']
    date_hierarchy = 'fecha_consulta'
    # readonly_fields removido porque no hay campos readonly necesarios
    
    def estado_badge(self, obj):
        """Mostrar estado con badge de color"""
        colors = {
            'PROG': 'blue',
            'CURS': 'orange', 
            'COMP': 'green',
            'CANC': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.estado, 'black'),
            obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"
    
    def motivo_corto(self, obj):
        """Mostrar motivo corto"""
        return obj.motivo[:50] + "..." if len(obj.motivo) > 50 else obj.motivo
    motivo_corto.short_description = "Motivo"


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    """
    CLASE: TratamientoAdmin
    PROPÓSITO: Configurar la interfaz admin para el modelo Tratamiento
    FUNCIONALIDAD: Gestión de tratamientos médicos prescritos
    """
    list_display = ['consulta', 'descripcion_corta', 'duracion_dias', 'fecha_inicio']
    list_filter = ['fecha_inicio', 'duracion_dias']
    search_fields = ['consulta__paciente__nombre', 'descripcion', 'observaciones']
    
    def descripcion_corta(self, obj):
        """Mostrar descripción corta"""
        return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = "Descripción"


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    """
    CLASE: MedicamentoAdmin
    PROPÓSITO: Configurar la interfaz admin para el modelo Medicamento
    FUNCIONALIDAD: Control de inventario y información de medicamentos
    """
    list_display = ['nombre', 'laboratorio', 'stock_badge', 'precio_unitario', 'activo']
    list_filter = ['activo', 'laboratorio']
    search_fields = ['nombre', 'laboratorio']
    actions = ['activar_medicamentos', 'desactivar_medicamentos']
    
    def stock_badge(self, obj):
        """Mostrar stock con color según cantidad"""
        color = 'green'
        if obj.stock < 10:
            color = 'red'
        elif obj.stock < 50:
            color = 'orange'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.stock
        )
    stock_badge.short_description = "Stock"
    
    def activar_medicamentos(self, request, queryset):
        """Acción para activar medicamentos"""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} medicamentos activados.')
    activar_medicamentos.short_description = "Activar medicamentos seleccionados"
    
    def desactivar_medicamentos(self, request, queryset):
        """Acción para desactivar medicamentos"""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} medicamentos desactivados.')
    desactivar_medicamentos.short_description = "Desactivar medicamentos seleccionados"


@admin.register(RecetaMedica)
class RecetaMedicaAdmin(admin.ModelAdmin):
    """
    CLASE: RecetaMedicaAdmin
    PROPÓSITO: Configurar la interfaz admin para el modelo RecetaMedica (MEJORA 2)
    FUNCIONALIDAD: Gestión de relaciones entre tratamientos y medicamentos
    """
    list_display = ['tratamiento', 'medicamento', 'dosis', 'frecuencia', 'fecha_prescripcion']
    list_filter = ['medicamento', 'fecha_prescripcion']
    search_fields = ['tratamiento__consulta__paciente__nombre', 'medicamento__nombre']
    date_hierarchy = 'fecha_prescripcion'


@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    """
    CLASE: HistorialMedicoAdmin
    PROPÓSITO: Configurar la interfaz admin para el modelo HistorialMedico (MEJORA 2)
    FUNCIONALIDAD: Visualización de eventos del historial médico
    """
    list_display = ['paciente', 'tipo_evento', 'fecha_evento', 'gravedad_badge', 'medico_responsable']
    list_filter = ['tipo_evento', 'gravedad', 'fecha_evento']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'tipo_evento', 'descripcion']
    date_hierarchy = 'fecha_evento'
    readonly_fields = ['fecha_evento']
    
    def gravedad_badge(self, obj):
        """Mostrar gravedad con badge de color"""
        colors = {
            'LEVE': 'green',
            'MODERADO': 'orange', 
            'GRAVE': 'red',
            'CRITICO': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.gravedad, 'black'),
            obj.get_gravedad_display()
        )
    gravedad_badge.short_description = "Gravedad"


# =============================================================================
# CONFIGURACIÓN GLOBAL DEL ADMIN
# =============================================================================

admin.site.site_header = "Clinica Salud Vital - Administración"
admin.site.site_title = "Sistema de Gestión Médica"
admin.site.index_title = "Panel de Administración"