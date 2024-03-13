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
        const ventanaEmergente1 = window.open("http://127.0.0.1:8000/agregarUsuario", "MiniVentana", `width=${anchoPantalla},height=${alturaPantalla}`);
        ventanaEmergente1.document.close();
    });
});
function confirmarEliminacion(usuarioId) {
    return confirm("¿Estás seguro de que deseas eliminar esta venta?");
}