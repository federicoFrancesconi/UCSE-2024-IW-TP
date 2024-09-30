$(document).ready(function() {
    // Obtén el token CSRF desde el HTML
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // Configura el token CSRF en cada solicitud AJAX
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^GET|HEAD|OPTIONS|TRACE$/.test(settings.type)) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });

    // Manejar el click en el botón de suscribirse
    $('button[id^="btn-suscribirse-"]').on('click', function() {
        const categoriaId = $(this).data('id');
        suscribirseACategoria(categoriaId);
    });

    // Manejar el click en el botón de desuscribirse
    $('button[id^="btn-desuscribirse-"]').on('click', function() {
        const categoriaId = $(this).data('id');
        desuscribirseDeCategoria(categoriaId);
    });

    function suscribirseACategoria(categoriaId) {
        $.ajax({
            url: "/api/suscribir_categoria/",
            type: "POST",
            data: {
                'categoria_id': categoriaId
            },
            success: function(response) {
                location.reload(); // Recargar la página después de la suscripción
            },
            error: function(error) {
                console.error("Error al suscribirse:", error);
            }
        });
    }

    function desuscribirseDeCategoria(categoriaId) {
        $.ajax({
            url: "/api/desuscribir_categoria/",
            type: "POST",
            data: {
                'categoria_id': categoriaId
            },
            success: function(response) {
                location.reload(); // Recargar la página después de la desuscripción
            },
            error: function(error) {
                console.error("Error al desuscribirse:", error);
            }
        });
    }
});
