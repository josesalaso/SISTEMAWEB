//buscador
const searchInput = document.getElementById("searchInput");
const dataTable = document.getElementById("dataTable");
const rows = dataTable.getElementsByTagName("tr");

searchInput.addEventListener("input", function () {
    const searchText = searchInput.value.toLowerCase();

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const rowData = row.textContent.toLowerCase();
        if (rowData.includes(searchText)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
                }
            }
});
function getColumnIndex(columnName) {
    const headers = dataTable.getElementsByTagName("th");
    for (let i = 0; i < headers.length; i++) {
        if (headers[i].textContent.trim() === columnName) {
            return i;
                }
            }
        return -1;
        }


// boton desplegar miniventana
document.addEventListener("DOMContentLoaded", function () {
    const abrirVentanaButton1 = document.getElementById("abrirVentana");

    abrirVentanaButton1.addEventListener("click", function () {
        const anchoPantalla = window.screen.width;
        const alturaPantalla = window.screen.height;
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/agregarVenta", "MiniVentana", "width=1600","height=1000");
        ventanaEmergente1.document.close();
    });
});
document.addEventListener("DOMContentLoaded", function() {
    var filterEstado = document.getElementById("filterEstado");
    var filterPago = document.getElementById("filterPago");
    var searchInput = document.getElementById("searchInput");

    filterEstado.addEventListener("change", filtrarTabla);
    filterPago.addEventListener("change", filtrarTabla);
    searchInput.addEventListener("input", filtrarTabla);

    function filtrarTabla() {
        console.log("Evento de cambio detectado");

        var selectedEstado = filterEstado.value.toLowerCase();
        var selectedPago = filterPago.value.toLowerCase();
        var searchTerm = searchInput.value.toLowerCase();

        console.log("Estado:", selectedEstado);
        console.log("Pago:", selectedPago);
        console.log("Término de búsqueda:", searchTerm);

        var rows = document.querySelectorAll("#dataTable tr");
        for (var i = 1; i < rows.length; i++) {
            var cells = rows[i].querySelectorAll("td");
            
            // Añadido código de depuración
            console.log("Fila", i, "Estado en la tabla:", cells[4].textContent.trim().toLowerCase());
            console.log("Fila", i, "Pago en la tabla:", cells[5].textContent.trim().toLowerCase());

            var estado = cells[4].textContent.trim().toLowerCase();
            var pago = cells[5].textContent.trim().toLowerCase();
            var searchContent = Array.from(cells).map(cell => cell.textContent.trim().toLowerCase()).join(' ');

            var estadoMatch = (selectedEstado === "all" || estado === selectedEstado);
            var pagoMatch = (selectedPago === "all" || pago === selectedPago);
            var searchMatch = (searchTerm === "" || searchContent.includes(searchTerm));

            console.log("Fila", i, "Estado Match:", estadoMatch);
            console.log("Fila", i, "Pago Match:", pagoMatch);
            console.log("Fila", i, "Búsqueda Match:", searchMatch);

            rows[i].style.display = (estadoMatch && pagoMatch && searchMatch) ? "" : "none";
        }
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const abrirVentanaButton1 = document.getElementById("abrirVentana1");

    abrirVentanaButton1.addEventListener("click", function () {
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/modificarventa", "width=1600","height=1000");
        ventanaEmergente1.document.close();
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const abrirVentanaButton1 = document.getElementById("abrirVentana2");

    abrirVentanaButton1.addEventListener("click", function () {
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/bitacoraVentas", "width=1600","height=1000");
        ventanaEmergente1.document.close();
    });
});