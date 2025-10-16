// ALGORITMO OFICIAL RUT CHILENO - VERSIÓN DEFINITIVA MEJORADA
function calcularDigitoVerificador(rut) {
    let suma = 0;
    let multiplicador = 2;
    
    for (let i = rut.length - 1; i >= 0; i--) {
        suma += parseInt(rut.charAt(i)) * multiplicador;
        multiplicador = multiplicador < 7 ? multiplicador + 1 : 2;
    }
    const dv = 11 - (suma % 11);
    return dv === 11 ? '0' : dv === 10 ? 'K' : dv.toString();
}

function validarRUT(rutCompleto) {
    if (!rutCompleto || rutCompleto.length < 3) {
        return { valido: false, mensaje: 'RUT incompleto' };
    }

    // Limpiar y normalizar
    const rutLimpio = rutCompleto.replace(/[^0-9kK]/g, '').toUpperCase();
    if (rutLimpio.length < 8) {
        return { valido: false, mensaje: 'RUT muy corto' };
    }

    const rut = rutLimpio.slice(0, -1);
    const dvIngresado = rutLimpio.slice(-1);

    if (!/^\d+$/.test(rut)) {
        return { valido: false, mensaje: 'RUT inválido' };
    }

    // 🚫 Bloquear RUT con todos los dígitos iguales (11111111, 22222222, etc.)
    if (/^(\d)\1+$/.test(rut)) {
        return { valido: false, mensaje: 'RUT inválido (repetitivo)' };
    }

    // 🚫 Validar rango real de RUT
    const rutNum = parseInt(rut, 10);
    if (rutNum < 1000000 || rutNum > 99999999) {
        return { valido: false, mensaje: 'RUT fuera de rango válido' };
    }

    // Calcular DV
    const dvCalculado = calcularDigitoVerificador(rut);
    const esValido = dvIngresado === dvCalculado;

    console.log(`RUT: ${rut}-${dvIngresado}, DV Calculado: ${dvCalculado}, Válido: ${esValido}`);

    return { 
        valido: esValido, 
        mensaje: esValido ? 'RUT válido' : 'RUT inválido (DV no coincide)' 
    };
}

// TEST AUTOMÁTICO
function testRUT() {
    const tests = [
        { rut: '111111111', esperado: false, desc: '11.111.111-1' },
        { rut: '222222222', esperado: false, desc: '22.222.222-2' },
        { rut: '444444444', esperado: false, desc: '44.444.444-4' },
        { rut: '123456785', esperado: true, desc: '12.345.678-5' },
        { rut: '999999999', esperado: false, desc: '99.999.999-9' },
        { rut: '87654321K', esperado: true, desc: '8.765.432-1K' }
    ];

    console.log('=== TEST RUT ===');
    tests.forEach(test => {
        const resultado = validarRUT(test.rut);
        const status = resultado.valido === test.esperado ? '✅' : '❌';
        console.log(`${status} ${test.desc}: ${resultado.valido ? 'VÁLIDO' : 'INVÁLIDO'} (esperado: ${test.esperado ? 'VÁLIDO' : 'INVÁLIDO'})`);
    });
}

// FORMATEO RUT CON CURSOR INTELIGENTE
function formatearRUT(input) {
    const cursorPos = input.selectionStart;
    const valorOriginal = input.value;
    
    let valor = input.value.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (!valor) {
        input.value = '';
        limpiarValidacion(input);
        return;
    }
    
    let cuerpo = valor.slice(0, -1);
    let dv = valor.slice(-1);
    
    let nuevoValor;
    if (cuerpo.length > 0) {
        let formateado = '';
        for (let i = cuerpo.length - 1, contador = 0; i >= 0; i--, contador++) {
            formateado = cuerpo[i] + formateado;
            if (contador % 3 === 2 && i !== 0) formateado = '.' + formateado;
        }
        nuevoValor = formateado + '-' + dv;
    } else {
        nuevoValor = dv;
    }
    
    // Solo actualizar si cambió
    if (nuevoValor !== valorOriginal) {
        input.value = nuevoValor;
        // Mantener cursor en posición similar
        const cambio = nuevoValor.length - valorOriginal.length;
        const nuevaPos = Math.max(0, cursorPos + cambio);
        input.setSelectionRange(nuevaPos, nuevaPos);
    }
    
    // Validar solo si está completo
    if (input.value.includes('-') && input.value.length >= 10) {
        const resultado = validarRUT(input.value);
        aplicarValidacion(input, resultado);
    } else {
        limpiarValidacion(input);
    }
}

// FORMATEO TELÉFONO
function formatearTelefono(input) {
    const cursorPos = input.selectionStart;
    const valorOriginal = input.value;
    
    let valor = input.value.replace(/[^0-9]/g, '');
    
    if (!valor) {
        input.value = '';
        limpiarValidacion(input);
        return;
    }
    
    let nuevoValor = input.value;
    
    if (valor.length === 9 && valor.startsWith('9')) {
        nuevoValor = `+56 ${valor[0]} ${valor.slice(1, 5)} ${valor.slice(5)}`;
        aplicarValidacionTelefono(input, true);
    } else if (input.value.match(/^\+\d{2} \d \d{4} \d{4}$/)) {
        aplicarValidacionTelefono(input, true);
    } else if (valor.length > 0 && valor.length < 9) {
        limpiarValidacion(input);
    } else {
        aplicarValidacionTelefono(input, false);
    }
    
    // Solo actualizar si cambió
    if (nuevoValor !== valorOriginal) {
        input.value = nuevoValor;
        const cambio = nuevoValor.length - valorOriginal.length;
        const nuevaPos = Math.max(0, cursorPos + cambio);
        input.setSelectionRange(nuevaPos, nuevaPos);
    }
}

// FUNCIONES AUXILIARES
function aplicarValidacion(input, resultado) {
    if (resultado.valido) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        mostrarFeedback(input, '✓ ' + resultado.mensaje, 'valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        mostrarFeedback(input, '✗ ' + resultado.mensaje, 'invalid');
    }
}

function aplicarValidacionTelefono(input, esValido) {
    if (esValido) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        mostrarFeedback(input, '✓ Teléfono válido', 'valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        mostrarFeedback(input, '✗ Formato: +56 9 1234 5678', 'invalid');
    }
}

function limpiarValidacion(input) {
    input.classList.remove('is-valid', 'is-invalid');
    let feedback = input.nextElementSibling;
    if (feedback && (feedback.classList.contains('valid-feedback') || feedback.classList.contains('invalid-feedback'))) {
        feedback.remove();
    }
}

function mostrarFeedback(input, mensaje, tipo) {
    // Remover feedback existente
    let feedbackExistente = input.nextElementSibling;
    if (feedbackExistente && (feedbackExistente.classList.contains('valid-feedback') || feedbackExistente.classList.contains('invalid-feedback'))) {
        feedbackExistente.remove();
    }
    
    // Crear nuevo feedback
    let feedback = document.createElement('div');
    feedback.className = tipo + '-feedback';
    feedback.textContent = mensaje;
    input.parentNode.appendChild(feedback);
}

// VALIDACIÓN DE TECLADO
function validarEntradaRUT(event) {
    const tecla = event.key;
    const teclasPermitidas = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'k', 'K', 'Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight'
    ];
    
    if (!teclasPermitidas.includes(tecla)) {
        event.preventDefault();
        return false;
    }
    return true;
}

function validarEntradaTelefono(event) {
    const tecla = event.key;
    const teclasPermitidas = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight'
    ];
    
    if (!teclasPermitidas.includes(tecla)) {
        event.preventDefault();
        return false;
    }
    return true;
}

// INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Iniciando validación RUT...');
    testRUT();
    
    // Campos RUT
    document.querySelectorAll('input[name="rut"]').forEach(input => {
        input.addEventListener('keydown', validarEntradaRUT);
        input.addEventListener('input', function() { formatearRUT(this); });
        input.addEventListener('blur', function() { 
            if (this.value.includes('-')) formatearRUT(this); 
        });
        
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const texto = (e.clipboardData || window.clipboardData).getData('text');
            const textoLimpio = texto.replace(/[^0-9kK]/g, '').toUpperCase();
            this.value = textoLimpio;
            formatearRUT(this);
        });
        
        if (input.value) formatearRUT(input);
    });
    
    // Campos Teléfono
    document.querySelectorAll('input[name="telefono"]').forEach(input => {
        input.addEventListener('keydown', validarEntradaTelefono);
        input.addEventListener('input', function() { formatearTelefono(this); });
        
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const texto = (e.clipboardData || window.clipboardData).getData('text');
            const textoLimpio = texto.replace(/[^0-9]/g, '');
            this.value = textoLimpio;
            formatearTelefono(this);
        });
        
        if (input.value) formatearTelefono(input);
    });
});