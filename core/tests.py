"""
MÓDULO: tests.py
SISTEMA: Clinica Salud Vital
AUTOR: Christofer Salazar
SECCIÓN: AP-172-N4
AÑO: 2025

DESCRIPCIÓN GENERAL:
Pruebas unitarias y de integración para el sistema de gestión médica.
Cubre modelos, vistas, formularios y API endpoints.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from .models import (
    Especialidad, Paciente, Medico, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica, HistorialMedico
)
from .forms import PacienteForm, MedicoForm


# =============================================================================
# PRUEBAS DE MODELOS
# =============================================================================

class ModelTests(TestCase):
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.especialidad = Especialidad.objects.create(
            nombre="Cardiología",
            descripcion="Especialidad en enfermedades del corazón"
        )
        
        self.paciente = Paciente.objects.create(
            rut="12.345.678-9",
            nombre="Juan",
            apellido="Pérez",
            fecha_nacimiento="1990-01-01",
            tipo_sangre="A+",
            correo="juan@test.com",
            telefono="+56912345678",
            direccion="Calle 123, Santiago"
        )
        
        self.medico = Medico.objects.create(
            rut="98.765.432-1",
            nombre="María",
            apellido="González",
            correo="maria@clinica.com",
            telefono="+56987654321",
            especialidad=self.especialidad
        )

    def test_especialidad_creation(self):
        """Test creación de especialidad"""
        self.assertEqual(self.especialidad.__str__(), "Cardiología")
        self.assertEqual(self.especialidad.nombre, "Cardiología")

    def test_paciente_creation(self):
        """Test creación de paciente"""
        self.assertEqual(self.paciente.__str__(), "Juan Pérez")
        self.assertEqual(self.paciente.tipo_sangre, "A+")
        self.assertTrue(self.paciente.activo)

    def test_medico_creation(self):
        """Test creación de médico"""
        self.assertEqual(self.medico.__str__(), "Dr. María González")
        self.assertEqual(self.medico.especialidad, self.especialidad)

    def test_consulta_medica_creation(self):
        """Test creación de consulta médica"""
        consulta = ConsultaMedica.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            fecha_consulta=timezone.now(),
            motivo="Dolor de cabeza",
            diagnostico="Migraña",
            estado="PROG"
        )
        self.assertEqual(consulta.estado, "PROG")
        self.assertIn("Juan Pérez", consulta.__str__())

    def test_medicamento_creation(self):
        """Test creación de medicamento"""
        medicamento = Medicamento.objects.create(
            nombre="Paracetamol",
            laboratorio="LabChile",
            stock=100,
            precio_unitario=1500.00
        )
        self.assertEqual(medicamento.nombre, "Paracetamol")
        self.assertEqual(medicamento.stock, 100)

    def test_historial_medico_creation(self):
        """Test creación de historial médico (MEJORA 2)"""
        historial = HistorialMedico.objects.create(
            paciente=self.paciente,
            tipo_evento="CONSULTA",
            descripcion="Consulta de rutina",
            medico_responsable=self.medico,
            gravedad="LEVE"
        )
        self.assertEqual(historial.tipo_evento, "CONSULTA")
        self.assertIn("Historial CONSULTA", historial.__str__())

    def test_receta_medica_creation(self):
        """Test creación de receta médica (MEJORA 2)"""
        consulta = ConsultaMedica.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            fecha_consulta=timezone.now(),
            motivo="Fiebre",
            estado="COMP"
        )
        
        tratamiento = Tratamiento.objects.create(
            consulta=consulta,
            descripcion="Tratamiento para fiebre",
            duracion_dias=5
        )
        
        medicamento = Medicamento.objects.create(
            nombre="Ibuprofeno",
            laboratorio="LabChile",
            stock=50,
            precio_unitario=1200.00
        )
        
        receta = RecetaMedica.objects.create(
            tratamiento=tratamiento,
            medicamento=medicamento,
            dosis="500mg",
            frecuencia="Cada 8 horas",
            duracion="5 días"
        )
        
        self.assertEqual(receta.dosis, "500mg")
        self.assertIn("Ibuprofeno", receta.__str__())


# =============================================================================
# PRUEBAS DE FORMULARIOS
# =============================================================================

class FormTests(TestCase):
    def test_paciente_form_valido(self):
        """Test formulario de paciente válido"""
        form_data = {
            'rut': '12.345.678-9',
            'nombre': 'Ana',
            'apellido': 'Silva',
            'fecha_nacimiento': '1985-05-15',
            'tipo_sangre': 'O+',
            'correo': 'ana@test.com',
            'telefono': '912345678',
            'direccion': 'Av. Principal 456',
            'activo': True
        }
        form = PacienteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_paciente_form_invalido(self):
        """Test formulario de paciente inválido"""
        form_data = {
            'rut': '123',  # RUT inválido
            'nombre': '',   # Nombre vacío
            'apellido': 'Silva',
            'fecha_nacimiento': '2050-01-01',  # Fecha futura
            'tipo_sangre': 'O+',
            'correo': 'correo-invalido',
            'telefono': '123',
            'direccion': 'Av. Principal 456'
        }
        form = PacienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rut', form.errors)
        self.assertIn('nombre', form.errors)
        self.assertIn('fecha_nacimiento', form.errors)

    def test_medico_form_valido(self):
        """Test formulario de médico válido"""
        especialidad = Especialidad.objects.create(nombre="Pediatría")
        
        form_data = {
            'rut': '11.222.333-4',
            'nombre': 'Carlos',
            'apellido': 'López',
            'correo': 'carlos@clinica.com',
            'telefono': '987654321',
            'especialidad': especialidad.id,
            'activo': True
        }
        form = MedicoForm(data=form_data)
        self.assertTrue(form.is_valid())


# =============================================================================
# PRUEBAS DE VISTAS
# =============================================================================

class ViewTests(TestCase):
    def setUp(self):
        """Configuración inicial para pruebas de vistas"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        
        # Agregar permisos al usuario
        permissions = Permission.objects.filter(
            codename__in=['view_paciente', 'add_paciente', 'change_paciente', 'delete_paciente']
        )
        self.user.user_permissions.set(permissions)
        self.user.save()
        
        self.especialidad = Especialidad.objects.create(nombre="Medicina General")
        self.paciente = Paciente.objects.create(
            rut="12.345.678-9",
            nombre="Test",
            apellido="Paciente",
            fecha_nacimiento="1990-01-01",
            tipo_sangre="A+",
            correo="test@test.com",
            telefono="912345678"
        )

    def test_dashboard_acceso_autenticado(self):
        """Test acceso al dashboard con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/panel/dashboard.html')

    def test_dashboard_acceso_no_autenticado(self):
        """Test redirección al login si no está autenticado"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirección a login

    def test_lista_pacientes(self):
        """Test vista de lista de pacientes"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('pacientes-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/panel/pacientes-list.html')
        self.assertContains(response, "Test Paciente")

    def test_crear_paciente(self):
        """Test creación de paciente"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('paciente-create'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        post_data = {
            'rut': '19.876.543-2',
            'nombre': 'Nuevo',
            'apellido': 'Paciente',
            'fecha_nacimiento': '1985-05-15',
            'tipo_sangre': 'B+',
            'correo': 'nuevo@test.com',
            'telefono': '912345678',
            'direccion': 'Calle Nueva 123',
            'activo': True
        }
        response = self.client.post(reverse('paciente-create'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirección después de crear
        
        # Verificar que el paciente fue creado
        self.assertTrue(Paciente.objects.filter(rut='19.876.543-2').exists())


# =============================================================================
# PRUEBAS DE API
# =============================================================================

class APITests(TestCase):
    def setUp(self):
        """Configuración inicial para pruebas de API"""
        self.client = Client()
        self.especialidad = Especialidad.objects.create(nombre="Traumatología")
        self.paciente = Paciente.objects.create(
            rut="12.345.678-9",
            nombre="API",
            apellido="Test",
            fecha_nacimiento="1990-01-01",
            tipo_sangre="A+",
            correo="api@test.com",
            telefono="912345678"
        )

    def test_api_pacientes_list(self):
        """Test endpoint de lista de pacientes"""
        response = self.client.get('/api/pacientes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API Test")

    def test_api_pacientes_filter(self):
        """Test filtros de API para pacientes"""
        response = self.client.get('/api/pacientes/?tipo_sangre=A+')
        self.assertEqual(response.status_code, 200)

    def test_api_medicamentos_search(self):
        """Test búsqueda en API de medicamentos"""
        Medicamento.objects.create(
            nombre="Aspirina",
            laboratorio="Bayer",
            stock=50,
            precio_unitario=800.00
        )
        
        response = self.client.get('/api/medicamentos/?search=Aspirina')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aspirina")


# =============================================================================
# PRUEBAS DE VALIDACIONES
# =============================================================================

class ValidationTests(TestCase):
    def test_rut_validation(self):
        """Test validación de formato RUT"""
        paciente = Paciente(
            rut="123",  # Formato inválido
            nombre="Test",
            apellido="Validation",
            fecha_nacimiento="1990-01-01",
            tipo_sangre="A+",
            correo="test@test.com",
            telefono="912345678"
        )
        
        with self.assertRaises(Exception):
            paciente.full_clean()

    def test_fecha_nacimiento_futura(self):
        """Test validación de fecha de nacimiento futura"""
        from datetime import date
        future_date = date(2050, 1, 1)
        
        paciente = Paciente(
            rut="12.345.678-9",
            nombre="Test",
            apellido="Future",
            fecha_nacimiento=future_date,
            tipo_sangre="A+",
            correo="test@test.com",
            telefono="912345678"
        )
        
        with self.assertRaises(Exception):
            paciente.full_clean()

    def test_stock_negativo(self):
        """Test validación de stock negativo"""
        medicamento = Medicamento(
            nombre="Test Medicamento",
            laboratorio="Test Lab",
            stock=-10,  # Stock negativo
            precio_unitario=1000.00
        )
        
        with self.assertRaises(Exception):
            medicamento.full_clean()