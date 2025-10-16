"""
MÓDULO: forms.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Define formularios Django para el panel administrativo personalizado.
Proporciona validación y widgets personalizados para mejor UX.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from .models import (
    Paciente, Medico, Especialidad, ConsultaMedica, Medicamento,
    Tratamiento, RecetaMedica 
)


# =============================================================================
# FORMULARIOS PARA PACIENTES
# =============================================================================

class PacienteForm(forms.ModelForm):
    """
    FORMULARIO: PacienteForm
    MODELO: Paciente
    PROPÓSITO: Crear y editar pacientes con validación
    CARACTERÍSTICAS: Campos con placeholders y clases Bootstrap
    """
    
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control rut-input',
                'placeholder': '12.345.678-9',
                'pattern': '^\\d{1,2}\\.\\d{3}\\.\\d{3}-[\\dKk]$',
                'title': 'Formato: 12.345.678-9',
                'autocomplete': 'off' 
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese apellido'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tipo_sangre': forms.Select(attrs={
                'class': 'form-control'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control telefono-input', 
                'placeholder': '+56 9 1234 5678',
                'title': 'Formato: +56 9 1234 5678',
                'autocomplete': 'off'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese dirección completa'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_rut(self):
        """Validación personalizada para RUT"""
        rut = self.cleaned_data.get('rut')
        if rut:
            # Validar formato básico de RUT chileno
            rut_pattern = re.compile(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$')
            if not rut_pattern.match(rut):
                raise ValidationError("El RUT debe tener formato: 12.345.678-9")
        return rut
    
    def clean_telefono(self):
        """Validación flexible de teléfono chileno"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Limpiar y validar formato
            telefono_limpio = telefono.replace(' ', '').replace('-', '').replace('+', '')
            
            # Validar que sea número chileno (9 dígitos después de 56 o solo 9 dígitos)
            if len(telefono_limpio) == 9 and telefono_limpio.startswith('9'):
                # Formato 912345678
                return f"+56 {telefono_limpio[0]} {telefono_limpio[1:5]} {telefono_limpio[5:]}"
            elif len(telefono_limpio) == 11 and telefono_limpio.startswith('569'):
                # Formato 56912345678
                return f"+56 {telefono_limpio[2]} {telefono_limpio[3:7]} {telefono_limpio[7:]}"
            elif len(telefono_limpio) == 12 and telefono_limpio.startswith('569'):
                # Ya tiene +56912345678
                return telefono
            else:
                raise ValidationError("Formato de teléfono inválido. Use: +56 9 1234 5678 o 912345678")
        return telefono
    
    def clean_correo(self):
        """Validar que el correo sea único"""
        correo = self.cleaned_data.get('correo')
        if correo and Paciente.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este correo electrónico ya está registrado")
        return correo
    
    def clean_fecha_nacimiento(self):
        """Validar que la fecha de nacimiento no sea futura"""
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento and fecha_nacimiento > timezone.now().date():
            raise ValidationError("La fecha de nacimiento no puede ser futura")
        return fecha_nacimiento


# =============================================================================
# FORMULARIOS PARA MÉDICOS
# =============================================================================

class MedicoForm(forms.ModelForm):
    """
    FORMULARIO: MedicoForm
    MODELO: Medico
    PROPÓSITO: Gestionar información de médicos
    CARACTERÍSTICAS: Select para especialidades relacionadas
    """
    
    class Meta:
        model = Medico
        fields = '__all__'
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control rut-input',
                'placeholder': '12.345.678-9',
                'pattern': '^\\d{1,2}\\.\\d{3}\\.\\d{3}-[\\dKk]$',
                'title': 'Formato: 12.345.678-9',
                'autocomplete': 'off'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese apellido'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'medico@clinica.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control telefono-input',
                'placeholder': '+56 9 1234 5678',
                'pattern': '^\\+56\\s9\\s\\d{4}\\s\\d{4}$',
                'title': 'Formato: +56 9 1234 5678',
                'autocomplete': 'off'
            }),
            'especialidad': forms.Select(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_rut(self):
        """Validación personalizada para RUT"""
        rut = self.cleaned_data.get('rut')
        if rut:
            rut_pattern = re.compile(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$')
            if not rut_pattern.match(rut):
                raise ValidationError("El RUT debe tener formato: 12.345.678-9")
        return rut
    
    def clean_telefono(self):
        """Validación flexible de teléfono chileno"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono_limpio = telefono.replace(' ', '').replace('-', '').replace('+', '')
            
            if len(telefono_limpio) == 9 and telefono_limpio.startswith('9'):
                return f"+56 {telefono_limpio[0]} {telefono_limpio[1:5]} {telefono_limpio[5:]}"
            elif len(telefono_limpio) == 11 and telefono_limpio.startswith('569'):
                return f"+56 {telefono_limpio[2]} {telefono_limpio[3:7]} {telefono_limpio[7:]}"
            elif len(telefono_limpio) == 12 and telefono_limpio.startswith('569'):
                return telefono
            else:
                raise ValidationError("Formato de teléfono inválido. Use: +56 9 1234 5678 o 912345678")
        return telefono
    
    def clean_correo(self):
        """Validar que el correo sea único"""
        correo = self.cleaned_data.get('correo')
        if correo and Medico.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este correo electrónico ya está registrado")
        return correo


# =============================================================================
# FORMULARIOS PARA ESPECIALIDADES
# =============================================================================

class EspecialidadForm(forms.ModelForm):
    """
    FORMULARIO: EspecialidadForm
    MODELO: Especialidad
    PROPÓSITO: Gestionar especialidades médicas
    CARACTERÍSTICAS: Textarea para descripción amplia
    """
    
    class Meta:
        model = Especialidad
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cardiología, Pediatría, etc.'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción de la especialidad médica...'
            })
        }


# =============================================================================
# FORMULARIOS PARA CONSULTAS MÉDICAS
# =============================================================================

class ConsultaMedicaForm(forms.ModelForm):
    """
    FORMULARIO: ConsultaMedicaForm
    MODELO: ConsultaMedica
    PROPÓSITO: Registrar consultas médicas
    CARACTERÍSTICAS: Selects relacionados para paciente y médico
    """
    
    class Meta:
        model = ConsultaMedica
        fields = '__all__'
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'medico': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_consulta': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo de la consulta...'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Diagnóstico médico...'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_fecha_consulta(self):
        """Validar que la fecha de consulta no sea futura"""
        fecha_consulta = self.cleaned_data.get('fecha_consulta')
        if fecha_consulta and fecha_consulta > timezone.now():
            raise ValidationError("La fecha de consulta no puede ser en el futuro")
        return fecha_consulta


# =============================================================================
# FORMULARIOS PARA MEDICAMENTOS
# =============================================================================

class MedicamentoForm(forms.ModelForm):
    """
    FORMULARIO: MedicamentoForm
    MODELO: Medicamento
    PROPÓSITO: Gestionar inventario de medicamentos
    CARACTERÍSTICAS: Validación de stock y precio
    """
    
    class Meta:
        model = Medicamento
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre comercial del medicamento'
            }),
            'laboratorio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Laboratorio fabricante'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            })
        }
    
    def clean_stock(self):
        """Validar que el stock no sea negativo"""
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise ValidationError("El stock no puede ser negativo")
        return stock
    
    def clean_precio_unitario(self):
        """Validar que el precio sea positivo"""
        precio = self.cleaned_data.get('precio_unitario')
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor a 0")
        return precio


# =============================================================================
# FORMULARIOS PARA TRATAMIENTOS Y RECETAS
# =============================================================================

class TratamientoForm(forms.ModelForm):
    """
    FORMULARIO: TratamientoForm
    MODELO: Tratamiento
    PROPÓSITO: Crear y editar tratamientos médicos
    """
    
    class Meta:
        model = Tratamiento
        fields = ['consulta', 'descripcion', 'duracion_dias', 'observaciones']
        widgets = {
            'consulta': forms.Select(attrs={
                'class': 'form-control'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del tratamiento...'
            }),
            'duracion_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            })
        }

class RecetaMedicaForm(forms.ModelForm):
    """
    FORMULARIO: RecetaMedicaForm
    MODELO: RecetaMedica
    PROPÓSITO: Crear recetas médicas con medicamentos
    """
    
    class Meta:
        model = RecetaMedica
        fields = ['medicamento', 'dosis', 'frecuencia', 'duracion']
        widgets = {
            'medicamento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'dosis': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 500mg, 1 tableta, etc.'
            }),
            'frecuencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cada 8 horas, 1 vez al día, etc.'
            }),
            'duracion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 7 días, 2 semanas, etc.'
            })
        }


# =============================================================================
# FORMULARIOS DE BÚSQUEDA
# =============================================================================

class BusquedaForm(forms.Form):
    """
    FORMULARIO: BusquedaForm
    PROPÓSITO: Formulario genérico para búsquedas
    CARACTERÍSTICAS: Campo de búsqueda simple
    """
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar...',
            'aria-label': 'Buscar'
        })
    )