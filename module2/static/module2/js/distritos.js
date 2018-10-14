function send(){

    swal({
            title: 'Leyendo tarjeta.',
            // title: 'I LOVE YOU <3.',
            html: 'Espere, por favor.',
            type: '',
            showConfirmButton: false,
            showCloseButton: false,
            showCancelButton: false,
            allowOutsideClick: false
        })
    var distrito = $( "input:checked" ).attr('id');

    $("#padjango").attr("href", "module2/votacion/"+distrito);
    document.getElementById('padjango').click();

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