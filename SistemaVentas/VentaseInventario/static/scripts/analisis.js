document.addEventListener("DOMContentLoaded", function () {
    const abrirVentanaButton1 = document.getElementById("abrirVentana1");

    abrirVentanaButton1.addEventListener("click", function () {
        const anchoPantalla = window.screen.width;
        const alturaPantalla = window.screen.height;
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/agregarAnalisis", "MiniVentana", `width=${anchoPantalla},height=${alturaPantalla}`);
        ventanaEmergente1.document.close();
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const abrirVentanaButton2 = document.getElementById("abrirVentana2");

    abrirVentanaButton2.addEventListener("click", function () {
        const anchoPantalla = window.screen.width;
        const alturaPantalla = window.screen.height;
        const ventanaEmergente2 = window.open("http://127.0.0.1:8000/modificarAnalisis", "MiniVentana", `width=${anchoPantalla},height=${alturaPantalla}`);
        ventanaEmergente2.document.close();
    });
});
function ampliarImagenAnalisis(imagen) {
    var contenedorAmpliado = document.createElement('div');
    contenedorAmpliado.className = 'imagen-ampliada';
    var imagenAmpliada = document.createElement('img');
    imagenAmpliada.src = imagen.src;
    imagenAmpliada.alt = 'Gráfico de Análisis Ampliado';
    contenedorAmpliado.appendChild(imagenAmpliada);
    document.body.appendChild(contenedorAmpliado);
    contenedorAmpliado.onclick = function () {
        document.body.removeChild(contenedorAmpliado);
    };
}
function abrirModal(urlImagen) {
    ampliarImagenAnalisis({ src: urlImagen });
}