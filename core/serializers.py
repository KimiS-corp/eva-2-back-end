"""
MÓDULO: serializers.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Define los serializers para la API REST del sistema médico.
Convierte instancias de modelos en JSON y valida datos entrantes.
Implementa relaciones y campos calculados para la API.
"""

from rest_framework import serializers
from .models import Especialidad, Paciente, Medico, ConsultaMedica, Tratamiento, Medicamento, RecetaMedica, HistorialMedico


# =============================================================================
# BLOQUE 1: SERIALIZERS BÁSICOS PARA MODELOS PRINCIPALES
# =============================================================================
"""
BLOQUE: Serializers para modelos sin relaciones complejas
OBJETIVO: Convertir modelos simples a JSON y viceversa
"""

class EspecialidadSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: EspecialidadSerializer
    MODELO: Especialidad
    PROPÓSITO: Serializar datos de especialidades médicas
    FUNCIONALIDAD: Convierte modelo Especialidad a JSON para API REST
    """
    total_medicos = serializers.SerializerMethodField()
    
    class Meta:
        """Configuración Meta para el serializer"""
        model = Especialidad
        fields = '__all__'
    
    def get_total_medicos(self, obj):
        """Obtener cantidad de médicos en la especialidad"""
        return obj.medico_set.count()


class PacienteSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: PacienteSerializer
    MODELO: Paciente  
    PROPÓSITO: Serializar datos completos de pacientes
    FUNCIONALIDAD: Maneja todos los campos incluyendo tipo_sangre (CHOICES)
    """
    edad = serializers.SerializerMethodField()
    tipo_sangre_display = serializers.CharField(source='get_tipo_sangre_display', read_only=True)
    
    class Meta:
        """Configuración Meta para el serializer"""
        model = Paciente
        fields = '__all__'
    
    def get_edad(self, obj):
        """Calcular edad del paciente"""
        from datetime import date
        if obj.fecha_nacimiento:
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return None


class MedicamentoSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: MedicamentoSerializer
    MODELO: Medicamento
    PROPÓSITO: Serializar datos del inventario de medicamentos
    FUNCIONALIDAD: Incluye control de stock y precios
    """
    estado_stock = serializers.SerializerMethodField()
    
    class Meta:
        """Configuración Meta para el serializer"""
        model = Medicamento
        fields = '__all__'
    
    def get_estado_stock(self, obj):
        """Determinar estado del stock"""
        if obj.stock == 0:
            return "AGOTADO"
        elif obj.stock < 10:
            return "BAJO"
        elif obj.stock < 50:
            return "MEDIO"
        else:
            return "ALTO"


class TratamientoSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: TratamientoSerializer
    MODELO: Tratamiento
    PROPÓSITO: Serializar datos de tratamientos médicos
    FUNCIONALIDAD: Maneja relación con consulta y datos del tratamiento
    """
    paciente_nombre = serializers.CharField(source='consulta.paciente.nombre_completo', read_only=True)
    
    class Meta:
        """Configuración Meta para el serializer"""
        model = Tratamiento
        fields = '__all__'


# =============================================================================
# BLOQUE 2: SERIALIZERS CON RELACIONES Y CAMPOS CALCULADOS
# =============================================================================
"""
BLOQUE: Serializers que incluyen relaciones y campos adicionales
OBJETIVO: Enriquecer la API con datos relacionados y calculados
"""

class MedicoSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: MedicoSerializer
    MODELO: Medico
    PROPÓSITO: Serializar datos de médicos con información de especialidad
    FUNCIONALIDAD: Incluye campo calculado para nombre de especialidad
    """
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    total_consultas = serializers.SerializerMethodField()

    class Meta:
        """Configuración Meta para el serializer"""
        model = Medico
        fields = '__all__'
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del médico"""
        return f"Dr. {obj.nombre} {obj.apellido}"
    
    def get_total_consultas(self, obj):
        """Obtener total de consultas del médico"""
        return obj.consultamedica_set.count()


class ConsultaMedicaSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: ConsultaMedicaSerializer
    MODELO: ConsultaMedica
    PROPÓSITO: Serializar consultas médicas con datos de paciente y médico
    FUNCIONALIDAD: Incluye nombres legibles de paciente y médico
    """
    paciente_nombre = serializers.SerializerMethodField()
    medico_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    especialidad_medico = serializers.CharField(source='medico.especialidad.nombre', read_only=True)

    class Meta:
        """Configuración Meta para el serializer"""
        model = ConsultaMedica
        fields = '__all__'

    def get_paciente_nombre(self, obj):
        """Método para obtener nombre completo del paciente"""
        return f"{obj.paciente.nombre} {obj.paciente.apellido}"

    def get_medico_nombre(self, obj):
        """Método para obtener nombre completo del médico"""
        return f"Dr. {obj.medico.nombre} {obj.medico.apellido}"


# =============================================================================
# BLOQUE 3: SERIALIZERS PARA MEJORA 2 - TABLAS ADICIONALES
# =============================================================================
"""
BLOQUE: Serializers para las nuevas tablas adicionales
OBJETIVO: Implementar serialización para las mejoras del modelo
"""

class HistorialMedicoSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: HistorialMedicoSerializer (MEJORA 2)
    MODELO: HistorialMedico
    PROPÓSITO: Serializar datos del historial médico de pacientes
    FUNCIONALIDAD: Registro completo de eventos médicos con información de médicos
    """
    paciente_nombre = serializers.SerializerMethodField()
    medico_nombre = serializers.SerializerMethodField()
    gravedad_display = serializers.CharField(source='get_gravedad_display', read_only=True)
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)

    class Meta:
        """Configuración Meta para el serializer"""
        model = HistorialMedico
        fields = '__all__'

    def get_paciente_nombre(self, obj):
        """Método para obtener nombre completo del paciente"""
        return f"{obj.paciente.nombre} {obj.paciente.apellido}"

    def get_medico_nombre(self, obj):
        """Método para obtener nombre completo del médico"""
        if obj.medico_responsable:
            return f"Dr. {obj.medico_responsable.nombre} {obj.medico_responsable.apellido}"
        return "No asignado"


class RecetaMedicaSerializer(serializers.ModelSerializer):
    """
    SERIALIZER: RecetaMedicaSerializer (MEJORA 2)
    MODELO: RecetaMedica
    PROPÓSITO: Serializar recetas médicas con información de medicamentos
    FUNCIONALIDAD: Relación muchos-a-muchos entre tratamientos y medicamentos
    """
    medicamento_nombre = serializers.CharField(source='medicamento.nombre', read_only=True)
    tratamiento_descripcion = serializers.CharField(source='tratamiento.descripcion', read_only=True)
    paciente_nombre = serializers.CharField(source='tratamiento.consulta.paciente.nombre_completo', read_only=True)

    class Meta:
        """Configuración Meta para el serializer"""
        model = RecetaMedica
        fields = '__all__'


# =============================================================================
# SERIALIZERS PARA DASHBOARD Y ESTADÍSTICAS
# =============================================================================

class DashboardStatsSerializer(serializers.Serializer):
    """
    SERIALIZER: DashboardStatsSerializer
    PROPÓSITO: Serializar estadísticas para el dashboard
    FUNCIONALIDAD: Proporciona datos consolidados para el panel principal
    """
    total_pacientes = serializers.IntegerField()
    total_medicos = serializers.IntegerField()
    total_especialidades = serializers.IntegerField()
    total_consultas = serializers.IntegerField()
    consultas_hoy = serializers.IntegerField()
    medicamentos_stock_bajo = serializers.IntegerField()
    total_tratamientos = serializers.IntegerField()
    total_recetas = serializers.IntegerField()