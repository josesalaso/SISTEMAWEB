// Modal de errores
function cerrarModal() {
    document.getElementById('errorModal').style.display = 'none';
}

// Modal recuperar contraseña
function abrirRecuperar() {
    document.getElementById("recuperarModal").style.display = "block";
}

function cerrarRecuperar() {
    document.getElementById("recuperarModal").style.display = "none";
}

window.onclick = function(event) {
    var modal = document.getElementById('errorModal');
    var modal1 = document.getElementById('recuperarModal');
    if (event.target == modal) {
        cerrarModal()
    }
    if (event.target == modal1) {
        cerrarRecuperar()
    }
}