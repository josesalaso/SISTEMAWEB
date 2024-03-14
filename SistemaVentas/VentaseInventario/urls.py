from django.urls import path
from . import views

# Ejemplo de urls
"""
app_name = 'yourappname' # En caso de existir multiples apps en el proyecto, de no ser asi ignorar

#
urlpatterns = [
    path('', views.HomeView, name='home'),
    path('about/', views.AboutView, name='about'),
    path('contact/', views.ContactView, name='contact'),
]
"""

# TODO: Ingresar Urls de la aplicacion

urlpatterns = [
    # Ventanas principales
    path('', views.index, name='index'),
    path('servicios/', views.servicios, name='servicios'),
    path('experienciayclientes/', views.experienciayclientes, name='experienciayclientes'),
    path('contacto/', views.contacto, name='contacto'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ventas/', views.Ventas, name='ventas'),
    path('analisis/', views.analisis, name='analisis'),
    path('usuario/', views.usuario, name='usuario'),
    path('historial/', views.historial, name='historial'),
    path('cerrarSesion/', views.cerrarSesion, name='cerrarSesion'),
    path('bitacoraVentas/', views.bitacoraVentas, name='bitacoraVentas'),
    # Modificar tablas
    path('modificarinv/', views.modificarinv, name='modificarinv'),
    path('modificarventa/', views.modificarventa, name='modificarventa'),
    path('modificarAnalisis/', views.modificarAnalisis, name='modificarAnalisis'),
    # Agregar datos
    path('agregarInventario/', views.agregarInventario, name='agregarInventario'),
    path('agregarVenta/', views.agregarVenta, name='agregarVenta'),
    path('agregarAnalisis/', views.agregarAnalisis, name='agregarAnalisis'),
    path('agregarUsuario/', views.agregarUsuario, name='agregarUsuario'),
    path('agregarProveedor/', views.agregarProveedor, name='agregarProveedor'),
    path('agregarCliente/', views.agregarCliente, name='agregarCliente'),
    # Eliminar datos
    path('eliminar_producto/<str:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('eliminar_analisis/<str:analisis_id>/', views.eliminar_analisis, name='eliminar_analisis'),
    path('eliminar_venta/<str:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('eliminar_usuario/<str:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('eliminar_proveedor/<str:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('eliminar_cliente/<str:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    # Editar datos
    path('editarProducto/', views.editarProducto, name='editarProducto'),
    path('editarVenta/', views.editarVenta, name='editarVenta'),
    path('editarAnalisis/', views.editarAnalisis, name='editarAnalisis'),
    path('editarUsuario/', views.editarUsuario, name='editarUsuario'),
    path('editarProveedor/', views.editarProveedor, name='editarProveedor'),
    path('editarCliente/', views.editarCliente, name='editarCliente'),
    # Variaciones inventario
    path('productos/', views.productos, name='productos'),
    path('proveedores/', views.proveedores, name='proveedores'),
    path('clientes/', views.clientes, name='clientes'),
    path('alertas/', views.alertas, name='alertas'),
    path('reset_password/', views.reset_password, name='reset_password')
]