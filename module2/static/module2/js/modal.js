/**
 * Created by priet on 21/11/2017.
 */

var model;
var btn;
var span;




function print(x){
    console.log(x)
}

function initModal(){
    //print("init model")
    // Get the modal
    modal = document.getElementById('myModal');
    fondo = document.getElementById('fondo');

    // display en el otro js

    // Get the <span> element that closes the modal
    span = document.getElementsByClassName("close")[0];



    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
        fondo.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

}
