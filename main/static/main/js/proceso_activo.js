$('#cerrar').click(function () {
    alert("Cerrando proceso");
    $('#votacionON').hide(200, function () {
        $('#cerrar').hide();
        $('#continuar').hide();
        $('#cargandoDatos').show(999, function () {

        });
    });
});

$('#continuar').click(function () {
    alert("Continuando proceso");
});