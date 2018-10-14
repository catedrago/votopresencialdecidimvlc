var files = false;


$(function () {
    'use strict';

    $("#generar_usb").click(function () {
        if (!window.FileReader) {
            alert('Este navegador no es compatible con la funcionalidad necesaria.');
            return false;
        }
        createJSON()
        createCSV()
    });

});

function createJSON(){
    /*
    {
        censo: {
            ["23432157V","23876327B"]
        },
        votacion:{
            {
                titulo: "Testr",
                descripcion: "Esto es un test",
                presupuesto:"13.000.000"
            }
        },
        impresora: 1/0, #Depende de si se quiere utilizar o no la impresora,

    }
    */
    terminado = false

    if($('#censo')[0].files.length && $('#votacion')[0].files.length){

        let printer = $(".selectPrinter");
        let selection_printer = printer.find("option:selected").val();

        let anon = $(".selectAnon");
        let selection_anon = anon.find("option:selected").val();

        let correo = $('#email').val();
        let convocante = $('#convocante').val();
        let proces = $('#proceso').val();

        var json = new Object();
        var votacion = new Object();
        votacion.correo = correo;
        votacion.convocante = convocante;
        votacion.proces = proces;
        json.censo = [];
        json.configuracion = votacion;
        json.impresora = selection_printer;
        json.anonimo = selection_anon;

        $('#censo').parse({
                config: {
                    step: function(results){
                        json.censo.push(results.data[0][0])
                    }
                },
                error: function(err, file, inputElem, reason)
                {
                    alert("Error creando el archivo configuracion.json")
                },
                complete: function()
                {
                    download("configuracion.json", JSON.stringify(json));
                }
        });
    }else{
        alert("Necesitamos ficheros yummi!")
    }
}

function createCSV(){
     var result = "";
     $('#votacion').parse({
                config: {
                    step: function(results){
                        /*
                        Parsear cada results y comprobar.
                         */
                    }
                },
                error: function(err, file, inputElem, reason)
                {
                    alert("Error creando el archivo configuracion.json")
                },
                complete: function()
                {
                    download("votaciones.json", result);
                }
        });
}
function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

function enableButton()
{
    $('#generar_usb').prop('disabled', false);
}

function disableButton()
{
    $('#generar_usb').prop('disabled', true);
}