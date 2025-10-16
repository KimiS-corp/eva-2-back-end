"""
MÓDULO: models.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Este módulo define todos los modelos de datos del sistema de gestión médica.
Incluye entidades para pacientes, médicos, consultas, tratamientos y recetas.
Implementa dos mejoras específicas: uso de CHOICES y creación de tabla adicional.
"""

from django.db import models
from django.core.exceptions import ValidationError
import re


# =============================================================================
# BLOQUE 1: DEFINICIÓN DE CLASES CHOICES - MEJORA 1 DEL MODELO
# =============================================================================

class EstadosConsulta(models.TextChoices):
    PROGRAMADA = 'PROG', 'Programada'
    EN_CURSO = 'CURS', 'En Curso'
    COMPLETADA = 'COMP', 'Completada'
    CANCELADA = 'CANC', 'Cancelada'


class TipoSangre(models.TextChoices):
    A_POSITIVO = 'A+', 'A+'
    A_NEGATIVO = 'A-', 'A-'
    B_POSITIVO = 'B+', 'B+'
    B_NEGATIVO = 'B-', 'B-'
    AB_POSITIVO = 'AB+', 'AB+'
    AB_NEGATIVO = 'AB-', 'AB-'
    O_POSITIVO = 'O+', 'O+'
    O_NEGATIVO = 'O-', 'O-'


# =============================================================================
# BLOQUE 2: MODELOS PRINCIPALES DEL SISTEMA
# =============================================================================

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la especialidad")
    descripcion = models.TextField(blank=True, verbose_name="Descripción detallada")

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.nombre


def validar_rut_chileno(rut):
    """
    Valida un RUT chileno con dígito verificador
    Formato aceptado: 12.345.678-9 o 12345678-9
    """
    rut = rut.replace('.', '').replace('-', '').upper()
    
    if len(rut) < 8:
        raise ValidationError('El RUT debe tener al menos 8 dígitos')
    
    numero = rut[:-1]
    dv = rut[-1]
    
    if not numero.isdigit():
        raise ValidationError('La parte numérica del RUT debe contener solo dígitos')
    
    if dv not in '0123456789K':
        raise ValidationError('El dígito verificador debe ser un número o K')
    
    suma = 0
    multiplo = 2
    
    for i in range(len(numero)-1, -1, -1):
        suma += int(numero[i]) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
    
    resto = suma % 11
    dv_esperado = str(11 - resto)
    
    if dv_esperado == '11':
        dv_esperado = '0'
    elif dv_esperado == '10':
        dv_esperado = 'K'
    
    if dv != dv_esperado:
        raise ValidationError(f'RUT inválido. Dígito verificador debería ser {dv_esperado}')


class Paciente(models.Model):
    """
    MODELO: Paciente
    DESCRIPCIÓN: Almacena información personal y médica de los pacientes
    """
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT del paciente")
    nombre = models.CharField(max_length=100, verbose_name="Nombres")
    apellido = models.CharField(max_length=100, verbose_name="Apellidos")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")
    tipo_sangre = models.CharField(max_length=3, choices=TipoSangre.choices, verbose_name="Tipo de sangre")
    correo = models.EmailField(verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono de contacto")
    direccion = models.TextField(verbose_name="Dirección particular")
    activo = models.BooleanField(default=True, verbose_name="Paciente activo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    def clean(self):
        """Validación personalizada para RUT"""
        if self.rut:
            validar_rut_chileno(self.rut)
        
        from django.utils import timezone
        if self.fecha_nacimiento and self.fecha_nacimiento > timezone.now().date():
            raise ValidationError({'fecha_nacimiento': 'La fecha de nacimiento no puede ser futura'})

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"


class Medico(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombres")
    apellido = models.CharField(max_length=100, verbose_name="Apellidos")
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT del médico")
    correo = models.EmailField(verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono de contacto")
    activo = models.BooleanField(default=True, verbose_name="Médico activo")
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, verbose_name="Especialidad médica")
    fecha_contratacion = models.DateField(auto_now_add=True, verbose_name="Fecha de contratación")

    def clean(self):
        """Validación personalizada para RUT de médico"""
        if self.rut:
            validar_rut_chileno(self.rut)

    def __str__(self):
        return f"Dr. {self.nombre} {self.apellido}"

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"


class ConsultaMedica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente atendido")
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, verbose_name="Médico tratante")
    fecha_consulta = models.DateTimeField(verbose_name="Fecha y hora de consulta")
    motivo = models.TextField(verbose_name="Motivo de la consulta")
    diagnostico = models.TextField(blank=True, verbose_name="Diagnóstico médico")
    estado = models.CharField(
        max_length=4, 
        choices=EstadosConsulta.choices, 
        default=EstadosConsulta.PROGRAMADA,
        verbose_name="Estado de la consulta"
    )

    class Meta:
        verbose_name = "Consulta Médica"
        verbose_name_plural = "Consultas Médicas"
        ordering = ['-fecha_consulta']

    def clean(self):
        from django.utils import timezone
        if self.fecha_consulta and self.fecha_consulta > timezone.now():
            raise ValidationError({'fecha_consulta': 'La fecha de consulta no puede ser en el futuro'})

    def __str__(self):
        return f"Consulta {self.paciente} - {self.medico}"


class Tratamiento(models.Model):
    consulta = models.ForeignKey(ConsultaMedica, on_delete=models.CASCADE, verbose_name="Consulta relacionada")
    descripcion = models.TextField(verbose_name="Descripción del tratamiento")
    duracion_dias = models.IntegerField(verbose_name="Duración en días")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones adicionales")
    fecha_inicio = models.DateField(auto_now_add=True, verbose_name="Fecha de inicio del tratamiento")

    def clean(self):
        if self.duracion_dias <= 0:
            raise ValidationError({'duracion_dias': 'La duración debe ser mayor a 0 días'})

    def __str__(self):
        return f"Tratamiento {self.consulta}"


class Medicamento(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre comercial")
    laboratorio = models.CharField(max_length=100, verbose_name="Laboratorio fabricante")
    stock = models.IntegerField(default=0, verbose_name="Cantidad en stock")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    activo = models.BooleanField(default=True, verbose_name="Medicamento activo")

    def clean(self):
        if self.stock < 0:
            raise ValidationError({'stock': 'El stock no puede ser negativo'})
        if self.precio_unitario <= 0:
            raise ValidationError({'precio_unitario': 'El precio debe ser mayor a 0'})

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"


# =============================================================================
# BLOQUE 3: MEJORA 2 - NUEVAS TABLAS ADICIONALES
# =============================================================================

class HistorialMedico(models.Model):
    GRAVEDAD_CHOICES = [
        ('LEVE', 'Leve'),
        ('MODERADO', 'Moderado'),
        ('GRAVE', 'Grave'),
        ('CRITICO', 'Crítico')
    ]
    
    TIPO_EVENTO_CHOICES = [
        ('CONSULTA', 'Consulta'),
        ('EXAMEN', 'Examen'),
        ('PROCEDIMIENTO', 'Procedimiento'),
        ('ALERGIA', 'Alergia'),
        ('ENFERMEDAD', 'Enfermedad'),
        ('TRATAMIENTO', 'Tratamiento'),
        ('OTRO', 'Otro')
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    fecha_evento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del evento")
    tipo_evento = models.CharField(max_length=50, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de evento")
    descripcion = models.TextField(verbose_name="Descripción detallada")
    medico_responsable = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Médico responsable")
    gravedad = models.CharField(max_length=20, choices=GRAVEDAD_CHOICES, default='LEVE', verbose_name="Nivel de gravedad")
    archivos_adjuntos = models.FileField(upload_to='historial_medico/', null=True, blank=True, verbose_name="Archivos adjuntos")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones adicionales")

    class Meta:
        verbose_name = "Historial Médico"
        verbose_name_plural = "Historiales Médicos"
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"Historial {self.tipo_evento} - {self.paciente}"


class RecetaMedica(models.Model):
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE, verbose_name="Tratamiento asociado")
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, verbose_name="Medicamento recetado")
    dosis = models.CharField(max_length=50, verbose_name="Dosis prescrita")
    frecuencia = models.CharField(max_length=100, verbose_name="Frecuencia de administración")
    duracion = models.CharField(max_length=50, verbose_name="Duración del tratamiento")
    fecha_prescripcion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de prescripción")

    class Meta:
        verbose_name = "Receta Médica"
        verbose_name_plural = "Recetas Médicas"
        unique_together = ['tratamiento', 'medicamento']

    def clean(self):
        if not self.dosis.strip():
            raise ValidationError({'dosis': 'La dosis no puede estar vacía'})
        if not self.duracion.strip():
            raise ValidationError({'duracion': 'La duración no puede estar vacía'})

    def __str__(self):
        return f"Receta {self.tratamiento} - {self.medicamento}"