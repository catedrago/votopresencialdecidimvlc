"{% load staticfiles %}"
var _DEBUG = true
var DNI = ""

// propuestas.push({
//         "titulo": "aaaaMejora de la acera de Botánico Cavanilles \n" +
//         "(puerta de Viveros a Blasco Ibañez)" ,
//         "text": "<p>Es proposa millorar l’eficiència energètica de l’enllumenat en diferents barris de la ciutat que permeta un major estalvi econòmic, la renovació del mobiliari així com una millora en la instal·lació, amb una llum més agradable i la reducció d’emissions</p>",
//         "id": 1,
//         "fecha": "11/11/2017",
//         "precio": 20000000,
//         "tipo": "Ciudadania",
//         "lugar": "Toda la ciudad",
//         "votado": false
//     })


interval = null


var id = null



function print(x){
    console.log(x)
}

function show_presupuesto(){
    span_pres = $('#presupuesto')
    span_pres.html(parseInt(presupuestoRestante).toLocaleString('es-ES') + " €")
}

function add_carrito(id){

    for(p in propuestas) {
        propuesta = propuestas[p]
        if (propuesta.id == id){
            if (presupuestoRestante - propuesta.precio < 0){
                swal(
                  'No tiene suficiente presupuesto',
                  'Revise sus propuestas',
                  'info'
                )
                return
            }else{
                presupuestoRestante = parseInt(presupuestoRestante) - parseInt(propuesta.precio);

                propuesta.votado = true
                // print("propuestas: ")
                // print(propuestas)

                reload()

            }

        }

    }


}

function add_carrito_no_reload(id){

    for(p in propuestas) {
        propuesta = propuestas[p]
        if (propuesta.id == id){
            print(id)
            if (presupuestoRestante - propuesta.precio < 0){
                swal(
                  'No tiene suficiente presupuesto',
                  'Revise sus propuestas',
                  'info'
                )
                return
            }else{
                presupuestoRestante = parseInt(presupuestoRestante) - parseInt(propuesta.precio);

                propuesta.votado = true

            }

        }

    }


}

function reload_lista(){
    // print("reload_lista")
    lista = $('.lista ul')
    lista.empty();
    total_votados = 0
    for(p in propuestas) {
        if (propuestas[p].votado) {
            total_votados += 1
            propuesta = propuestas[p]
            lista.append(
                '      ' +
                '<li>\n' +
                '      <div class="item">' +
                // '<h4>Presupuesto ' + propuesta.id + '</h4>\n' +
                '      <p class="listaCarrito">' + propuesta.titulo.substr(0, 100) + '</p>' +
                '      <h5>' + parseInt(propuesta.precio).toLocaleString('es-ES')  + ' €</h5> ' +
                '</div>' +
                '<div class=\"eliminar\" id =\" ' + propuesta.id + '\" onclick=\"eliminar(' + propuesta.id + ')\"></div></li>'
            )
        }

    }

    if(total_votados == 0){
        print("Lista vacia")
        lista.append(
            '      ' +
            '<li>\n' +
            '      <div class="item">' +
            '      <h1 class="listaCarrito"> No hay proyectos votados </h1>' +
            '</div>'
        )
    }


}

function eliminar(ident){
    // print("eliminar")
    propuesta = null
    num = null
    for (p in propuestas){
        if (propuestas[p].id == ident){
            propuesta = propuestas[p]
            num = p
            break;
        }
    }
    // propuestas.push(propuesta)
    presupuestoRestante = parseInt(presupuestoRestante) + parseInt(propuesta.precio)
    propuestas[num].votado = false
    reload()
}

function show_descripcion(id){
    for (p in propuestas) {
        propuesta = propuestas[p]
        if (propuesta.id == id) {
            swal({
                title: "<span class='tituloPropuestaInfo''>" + propuesta.titulo + "</span>",
                type: '',
                position: 'center',
                width: 1200,
                customClass: 'swal-height',
                html: "<div class='swal_scroll' > " + propuesta.text + "</div>",
                showCloseButton: true,
                confirmButtonColor: '#D6702B',
                confirmButtonClass: 'buttonAceptar',
                confirmButtonText:
                    'Cerrar',
            })

        }

    }

}

function showPropuestas() {
    print("show propuestas")

    lista = $('.propuestaDiv');
    lista.empty();
    // console.log("Distrito: " + distrito)
    for (p in propuestas) {

        propuesta = propuestas[p];
        /*Seleccionamos solo las propuestas de los distritos que nos interesen*/
        distrito_propuesta = propuesta.geozone_id

        if (distrito != -1){

            if ( distrito != distrito_propuesta){
                continue;
            }
        }else{
            // console.log("Distrito es -1, no hay filtro")
        }

        /*Fin de seleccion*/

        // print(p)
        descripcion = propuesta.text;
        titulo = propuesta.titulo
        fecha = propuesta.fecha
        precio = propuesta.precio
        tipo = propuesta.tipo
        id = propuesta.id
        lugar = propuesta.lugar


        str = "<div class=\"propuesta\">\n" +
            "            <div class=\"tituloPropuestaDiv\"><h2 class=\"w3-center tituloPropuesta\">" + titulo + " </h2></div>\n" +
             "            <div class=\"lineaProp\">\n" +
            "            <button class=\"buttonPropuesta\" id='" + id + "' onclick='add_carrito(" + id + ")'>Votar</button>\n" +

            "                <div class=\"precioPropuesta\">" + parseInt(precio).toLocaleString('es-ES') + " €" + "</div>\n" +
            "            <div class='buttonInfo' onclick='show_descripcion(" + id + ")'>Más información</div>" +
            "\n" +
            "                <!--<div class=\"codigoPropuesta\">Código de la propuesta: <span id=\"codigoP\"></span></div>-->\n" +
            "\n" +
            "            </div>\n" +
            "            <!--<div id=\"propuesta\" class=\"propuesta\"> rgrehrth</div>-->\n" +
            "        </div>\n"


        lista.append(
                str
            )

        // buscar si esta votado o no
        if (propuesta.votado) {
            // print("Votado")
            $('#'+id).html("Votado");
            $('#'+id).addClass("no-click")
        } else {
            // print("Votar")
            $('#'+id).html("Votar");
            $('#'+id).removeClass("no-click")
        }

    }



}

/**
 * return numero de proyectos votados, inversion total
 */
function recuento(){
    n = 0
    total = 0
    for (p in propuestas){

        if (propuestas[p].votado){
            n++;
            total += parseInt(propuestas[p].precio)
        }
    }

    return [n, total]
}

/**
 * return lista de ids con proyectos votados
 * [1,2 ... 7,35]
 */
function getIdsVotados(){
    res = []
    for (p in propuestas){

        if (propuestas[p].votado){

            res.push(propuestas[p].id)
        }
    }

    return res
}

function comprobarVotacion(){
    // When the user clicks the button, open the modal
    modal.style.display = "block";
    fondo.style.display = "block";
    [n, total] = recuento()
    $('.nProyectosVotados').html(n+" proyectos");
    $('.importeTotal').html(parseInt(total).toLocaleString('es-ES') +" €");

}


function reload(){
    // Order by price
    // propuestas.(function(a, b) {
    //     retursortn parseFloat(b.precio) - parseFloat(a.precio);
    // });

    // aleatory order

    print("reload")
    // Cargas los votos almacenados en la etiqueta con id 'fondo', ya que provienen de la tarjeta nfc
    votos = $("#fondo").text()
    $("#fondo").text("")
    if (votos){
        votos = votos.replace('[','');
        votos = votos.replace(']','');
        votos = votos.replace(',','');
        print("Encontrado votos " + votos)
    }
    if (votos != ""){
        votos = votos.split(" ")

        for (i = 0; i <= votos.length; i++) {
            voto = parseInt(votos[i])
            print(voto)
            add_carrito_no_reload(voto)
        }
        print("fin for")
        reload()
    }


    // print("reload")
    show_presupuesto();
    showPropuestas();
    reload_lista();
}

$.fn.extend({
    disableSelection: function() {
        this.each(function() {
            this.onselectstart = function() {
                return false;
            };
            this.unselectable = "on";
            $(this).css('-moz-user-select', 'none');
            $(this).css('-webkit-user-select', 'none');
        });
        return this;
    }
});

function disable(){

    $('body').css('cursor', 'none');

    $('body').contextmenu(function(e){

        e.preventDefault();
        e.stopPropagation();
        return false;
    });

    $('body').dblclick(function(e){

        // alert('ALERTA DE INTRUSO!');
        return false;
    });
    $('body').on('touchmove', function() {

        return false;
    });

    $('body').on('swipe', function() {

        return false;
    });

    $('body').on('swipeup', function() {

        return false;
    });

    $('body').on('swiperight', function() {

        return false;
    });

    $('body').on('swipedown', function() {

        return false;
    });

    $('body').on('swipedown', function() {

        return false;
    });

     $('body').on('taphold  ', function() {

        return false;
    });



    $('body').disableSelection();

}



function send(){
    $(".negro").addClass("negro2")
    clearInterval(interval);
    // $(".negro").html("<h1> Registrando voto.</h1>")

    jotason = {
        "user_id": DNI,
        "timestamp": new Date().getTime(),
        "votes": getIdsVotados()
    }

    ids = getIdsVotados()
    print("Vas a votar a " + ids)
    swal({
            title: 'Grabando tarjeta de votación.',
            html: 'Espere sin retirar la tarjeta, por favor.',
            type: '',
            showConfirmButton: false,
            showCloseButton: false,
            showCancelButton: false,
            allowOutsideClick: false
        })

    $("#padjango").attr("href", "module2/votar/"+ids);
    document.getElementById('padjango').click();

}
