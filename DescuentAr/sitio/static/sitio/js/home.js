function obtener_votos(descuentoId) {
    $.ajax({
        url: "api/obtener_votos/" + descuentoId + "/",
        type: "GET",
        dataType: "json",
        success: function(data) {
            $('#votos-positivos-' + descuentoId).text(data.votos_positivos);
            $('#votos-negativos-' + descuentoId).text(data.votos_negativos);
            
            // Actualiza el estado del botón según si el usuario ya votó
            if (data.ya_votado) {
                $('#retirar-voto-' + descuentoId).show(); // si tiene voto muestro para que pueda eliminarlo

                if (data.voto_positivo) {
                    // Usuario ha votado positivamente
                    $('#green-' + descuentoId).addClass('btn-success').removeClass('btn-default');
                    $('#red-' + descuentoId).addClass('btn-default').removeClass('btn-danger');
                } else {
                    // Usuario ha votado negativamente
                    $('#red-' + descuentoId).addClass('btn-danger').removeClass('btn-default');
                    $('#green-' + descuentoId).addClass('btn-default').removeClass('btn-success');
                }
            } else {
                $('#retirar-voto-' + descuentoId).hide(); //si no voto oculto el botón
                $('#green-' + descuentoId).addClass('btn-default').removeClass('btn-success');
                $('#red-' + descuentoId).addClass('btn-default').removeClass('btn-danger');
            }
        },
        error: function(error) {
            console.error("Error al obtener los votos:", error);
        }
    });
}

function retirar_voto(descuentoId) {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    $.ajax({
        url: 'api/retirar_voto/',  // Asegúrate de que este URL coincida con tu endpoint
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken 
        },
        data: {
            'descuento_id': descuentoId
        },
        success: function(response) {
            window.location.href = ''
            actualizarEstadoBotones(descuentoId, null);
        },
        error: function(response) {
            console.error("Error al retirar el voto:", response);
            window.location.href = '/accounts/login/';
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
                $('#guardar-' + descuentoId).html('<i class="fa-solid fa-bookmark"></i>');
            } else {
                $('#guardar-' + descuentoId).html('<i class="fa-regular fa-bookmark"></i>');
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
                $('#guardar-' + descuentoId).html('<i class="fa-solid fa-bookmark"></i>');
            } else {
                $('#guardar-' + descuentoId).html('<i class="fa-regular fa-bookmark"></i>');
            }
        },
        error: function(error) {
            window.location.href = '/accounts/login/';
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
        success: function(response) {     
            actualizarEstadoBotones(descuentoId, votoPositivo);  // Actualiza el color de los botones
            obtener_votos(descuentoId);  // Actualiza el número de votos en pantalla
            actualizarEstadoDescuento(descuentoId, response.estado_descuento);  // Actualiza el estado del descuento
        },
        error: function(response) {
            window.location.href = '/accounts/login/';
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

        $('#retirar-voto-' + descuentoId).on('click', function() {
            retirar_voto(descuentoId);
        });

        $('#eliminar-' + descuentoId).on('click', function() {
            eliminar_descuento(descuentoId);
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







function eliminar_descuento(descuentoId) {
    const csrfToken = getCookie('csrftoken');  // Obtener el token CSRF si es necesario

    $.ajax({
        url: '/api/eliminar_descuento/' + descuentoId + '/',
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken 
        },
        success: function(response) {
            window.location.href = '';
        },
        error: function(response) {
            console.error("Error al eliminar el descuento:", response);
            window.location.href = '/accounts/login/';
        }
    });
}