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

function on_page_load() {
    const descuentos = document.querySelectorAll("[data-descuento-id]");

    const descuentos_id = Array.from(descuentos).map(descuento => descuento.getAttribute("data-descuento-id"));

    descuentos_id.forEach(descuentoId => {
        $('#guardar-' + descuentoId).on('click', function() {
            guardar_descuento(descuentoId)
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