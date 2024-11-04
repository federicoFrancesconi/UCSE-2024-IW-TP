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

function obtener_votos_general(descuentos_id) {
    descuentos_id.forEach(descuentoId => {
        obtener_votos(descuentoId);
    });
}

function on_page_load() {
    const descuentos = document.querySelectorAll("[data-descuento-id]");

    const descuentos_id = Array.from(descuentos).map(descuento => descuento.getAttribute("data-descuento-id"));

    obtener_votos_general(descuentos_id);

    // Actualizamos los votos cada 10 segundos
    setInterval(function() {
        obtener_votos_general(descuentos_id);
    }, 20000);
}

$(document).ready(function() {
    on_page_load();
});