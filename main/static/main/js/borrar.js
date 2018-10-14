$('#confirmar').click(function () {
    $('#cerrar').hide(200, function () {
            $('#confirmar').hide();
            $('#cancelar').hide();
            $('#borrar').show(999, function () {
                $('#borrar').hide(200, function () {
                    $('#finBorrar').show(999, function () {
                        $('#aceptar').show();

                    })
                    
                })
            });
    });
});

$('#aceptar').click(function () {
     location.href="/"
});

$('#cancelar').click(function () {
    alert("Cancelado")
});