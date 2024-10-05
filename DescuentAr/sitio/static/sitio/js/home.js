function obtener_votos(descuentoId) {
    $.ajax({
        url: "api/obtener_votos/" + descuentoId + "/",
        type: "GET",
        dataType: "json",
        success: function(data) {
            $('#votos-positivos-' + descuentoId).text(data.votos_positivos);
            $('#votos-negativos-' + descuentoId).text(data.votos_negativos);
        },
        error: function(error) {
            console.error("Error al obtener los votos:", error);
        }
    });
}

function obtener_guardado(descuentoId) {
    $.ajax({
        url: "api/obtener_guardado/" + descuentoId + "/",
        type: "GET",
        dataType: "json",
        success: function(data) {
            if (data.guardado) {
                $('#guardar-' + descuentoId).text("Quitar de guardados");
            } else {
                $('#guardar-' + descuentoId).text("Guardar");
            }
        },
        error: function(error) {
            console.error("Error al obtener si el descuento estaba guardado:", error);
        }
    });
}

function guardar_descuento(descuentoId) {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    const url = $('#guardar-' + descuentoId).data('url');

    $.ajax({
        url: url,
        type: "POST",
        data: {
            descuento_id: descuentoId,
            csrfmiddlewaretoken: csrfToken
        },
        success: function(response) {
            // Update button text based on the response
            if (response.message === "Descuento guardado correctamente") {
                $('#guardar-' + descuentoId).text("Quitar de guardados");
            } else {
                $('#guardar-' + descuentoId).text("Guardar");
            }
        },
        error: function(error) {
            console.error("Error al guardar/quitar el descuento:", error);
        }
    });
}

function obtener_votos_general(descuentos_id) {
    descuentos_id.forEach(descuentoId => {
        obtener_votos(descuentoId);
    });
}

function enviarVoto(descuentoId, votoPositivo) {
    $.ajax({
        url: '/api/guardar_voto/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')  // Incluye el token CSRF si es necesario
        },
        data: {
            'descuento_id': descuentoId,  // ID del descuento
            'voto_positivo': votoPositivo  // Voto positivo o negativo
        },
        success: function (response) {     
            actualizarEstadoBotones(descuentoId, votoPositivo);  // Actualiza el color de los botones
            obtener_votos(descuentoId);  // Actualiza el número de votos en pantalla
            actualizarEstadoDescuento(descuentoId,response.estado_descuento);  // Actualiza el estado del descuento
        },
        error: function (response) {
            alert(response.responseJSON.error);  // Muestra el error si ocurre
        }
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function actualizarEstadoBotones(descuentoId, votoPositivo) {
    var botonPositivo = $('#green-' + descuentoId);
    var botonNegativo = $('#red-' + descuentoId);

    if (votoPositivo) {
        // Voto positivo: verde para el botón positivo, quita el rojo del negativo
        botonPositivo.css('color', 'green');
        botonNegativo.css('color', 'black');
    } else {
        // Voto negativo: rojo para el botón negativo, quita el verde del positivo
        botonNegativo.css('color', 'red');
        botonPositivo.css('color', 'black');
    }
}

function actualizarEstadoDescuento(descuentoId, estado) {
    $('#estado-' + descuentoId).text(estado);
}

function on_page_load() {
    const descuentos = document.querySelectorAll("[data-descuento-id]");

    const descuentos_id = Array.from(descuentos).map(descuento => descuento.getAttribute("data-descuento-id"));

    descuentos_id.forEach(descuentoId => {
        $('#guardar-' + descuentoId).on('click', function() {
            guardar_descuento(descuentoId)
        });

        $('#green-' + descuentoId).on('click', function() {
            enviarVoto(descuentoId, true);  // Voto positivo
        });
    
        $('#red-' + descuentoId).on('click', function() {
            enviarVoto(descuentoId, false);  // Voto negativo
        });

        obtener_guardado(descuentoId);
    });

    obtener_votos_general(descuentos_id);

    // Actualizamos los votos cada 10 segundos
    setInterval(function() {
        obtener_votos_general(descuentos_id);
    }, 10000);
}

$(document).ready(function() {
    on_page_load();
});