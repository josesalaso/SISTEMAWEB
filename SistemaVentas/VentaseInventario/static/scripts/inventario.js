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
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/agregarInventario", "MiniVentana", "width=1800,height=600");
        ventanaEmergente1.document.close();
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const abrirVentanaButton1 = document.getElementById("abrirVentana1");

    abrirVentanaButton1.addEventListener("click", function () {
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/modificarinv", "MiniVentana", "width=1800,height=600");
        ventanaEmergente1.document.close();
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const abrirVentanaButton1 = document.getElementById("abrirVentana2");

    abrirVentanaButton1.addEventListener("click", function () {
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/alertas", "MiniVentana", "width=1800,height=600");
        ventanaEmergente1.document.close();
    });
});
document.addEventListener("DOMContentLoaded", function() {
    var filterEstado = document.getElementById("filterEstado");
    var filterPago = document.getElementById("filterPago");
    var filterCantidad = document.getElementById("filterCantidad");
    var filterCantidadActual = document.getElementById("filterCantidadActual");

    filterEstado.addEventListener("change", function() {
        filtrarTabla();
    });

    filterPago.addEventListener("change", function() {
        filtrarTabla();
    });

    filterCantidad.addEventListener("change", function() {
        filtrarTabla();
    });

    filterCantidadActual.addEventListener("change", function() {
        filtrarTabla();
    });

    function filtrarTabla() {
        var selectedEstado = filterEstado.value.toLowerCase();
        var selectedPago = filterPago.value;
        var selectedCantidad = filterCantidad.value;
        var selectedCantidadActual = filterCantidadActual.value;

        var rows = document.querySelectorAll("#dataTable tr");
        for (var i = 1; i < rows.length; i++) {
            var estado = rows[i].querySelectorAll("td")[3].textContent.toLowerCase();
            var pago = rows[i].querySelectorAll("td")[2].textContent;
            var cantidad = parseInt(rows[i].querySelectorAll("td")[5].textContent);
            var cantidadActual = parseInt(rows[i].querySelectorAll("td")[6].textContent);

            var estadoMatch = (selectedEstado === "all" || estado === selectedEstado);
            var pagoMatch = (selectedPago === "all" || pago === selectedPago);

            var cantidadMatch = (selectedCantidad === "all" ||
                (selectedCantidad === "mayor" && cantidad > 100) ||
                (selectedCantidad === "menor" && cantidad <= 100));

            var cantidadActualMatch = (selectedCantidadActual === "all" ||
                (selectedCantidadActual === "mayor" && cantidadActual > 100) ||
                (selectedCantidadActual === "menor" && cantidadActual <= 100));

            if (estadoMatch && pagoMatch && cantidadMatch && cantidadActualMatch) {
                rows[i].style.display = "";
            } else {
                rows[i].style.display = "none";
            }
        }
    }
});
function confirmarEliminacion(productoId) {
    return confirm("¿Estás seguro de que deseas eliminar esta venta?");
}