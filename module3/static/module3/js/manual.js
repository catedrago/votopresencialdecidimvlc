function isLetter(str) {
    return str.length === 1 && str.match(/[a-z]/i);
}

function teclado() {
    console.log("Sacando teclado")

    var toggleKeysIfEmpty = function (kb) {
        var text = kb.$preview.val()
        console.log(text.length)
        var toggle = text.length != 9 || !isLetter(text.substr(text.length - 1));
        kb.$keyboard
            .find('.ui-keyboard-accept')
            .toggleClass('disabled', toggle)
            .prop('disabled', toggle);
    };

    $("#keyboardDNI").keyboard({

            visible: function (e, keyboard) {
                toggleKeysIfEmpty(keyboard);
            },
            change: function (e, keyboard) {
                toggleKeysIfEmpty(keyboard);
            },

            accepted: function (e, keyboard, el) {
                console.log('accepted');
                send();
            },
            canceled: function (e, keyboard, el) {
                console.log('canceled');
                cancel();
            },
            layout: 'custom',
            customLayout: {
                'normal': [
                    '1 2 3 4 5 6 7 8 9 0 {bksp}',
                    ' q w e r t y u i o p'.toUpperCase(),
                    'a s d f g h j k l'.toUpperCase()+  ' {accept}',
                    'z x c v b n m '.toUpperCase(),
                    '{cancel}'
                ],
                'shift': [
                    '~ ! @ # $ % ^ & * ( ) _ + {bksp}',
                    '{tab} Q W E R T Y U I O P { } |',
                    'A S D F G H J K L : " {enter}',
                    '{shift} Z X C V B N M < > ? {shift}',
                    '{accept} {cancel}'
                ],
            },
            initialized: function (e, keyboard) {
                console.log(jQuery.keyboard.language)
                jQuery.keyboard.lang = "es"
                keyboard.reveal();
            },
        }
    );

}

function cancel() {
    document.getElementById('iniciar').click();
}

function send() {
    console.log("click")
    var url = $("#manual_url").attr("href")
    console.log(url)
    // var nombre = $("#keyboardNombre").val()
    // var ap1 = $("#keyboardAp1").val()
    // var ap2 = $("#keyboardAp2").val()
    var dni = $("#keyboardDNI").val()
    dni = dni.replace(/ /g, '')
    if (dni == " " || dni == false || !dni) {
        dni = "00000000A"
    }
    // nombre = nombre + " " + ap1 + " " + ap2
    // Construct the full URL with "id"
    url = url.replace('aa', dni)
    // url = url.replace('bb', nombre)
    $("#manual_url").attr("href", url);
    $(".ui-keyboard-button").attr("href", url);
    document.getElementById('manual_url').click();
}