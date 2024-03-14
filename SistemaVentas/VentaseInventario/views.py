#Instalada libreria pip install requests
from django.shortcuts import render, redirect
from firebase_admin import firestore, auth, credentials
import requests
from django.contrib import messages
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import json
from django.http import HttpResponse
from firebase_admin import firestore
from datetime import datetime, timedelta
import os
from django.core.mail import send_mail
from django.conf import settings
from collections import Counter
# Create your views here.
# LLamar informacion del usuario: db = firestore.client() -> db.collection('users').document(user_info['localId']).get.to_dict()

# Recordar agregar cliente - agregar proveedor

# LOGIN - DASHBOARD - CERRAR SESION
def login(request):
    if request.session.get('sesion') == True:
        return redirect('dashboard')
    if request.method == "POST":
        # Mail y contraseña del FORM
        email = request.POST.get("email")
        password = request.POST.get("pass")

        login_data = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        try:
            response = requests.post(
                'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCwA0xiXUss-zbkXFTBSCC-5lSLyox3LRE',
                json=login_data
            )

            if response.status_code == 200:
                user_info = response.json()
                db = firestore.client()
                user_ref = db.collection('users').document(user_info['localId'])
                user_data = user_ref.get()
                role = str(user_data.to_dict()['rolUsuario'])
                nombre = str(user_data.to_dict()['nombreUsuario'])

                if user_data.exists:
                    request.session['id'] = user_info['localId']
                    request.session['sesion'] = True
                    request.session['role'] = role
                    request.session['nombre'] = nombre
                    descripcion = f'Se inició una nueva sesión con la id: {request.session.get("id")}'
                    agregarHistorial(request.session.get('id'), descripcion, 'Inicio de Sesión')
                    return redirect('dashboard')
                else:
                    return render(request, 'VentaseInventario/login.html', {'error': 'Email o contraseña erronea'})
            else:
                return render(request, 'VentaseInventario/login.html', {'error': 'Email o contraseña erronea'})

        except Exception as e:
            return render(request, 'VentaseInventario/login.html', {'error': e})
        
    return render(request, 'VentaseInventario/login.html')

def dashboard(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        ventas = db.collection('Ventas').stream()
        inventario = db.collection('Inventario').stream()
        analisis = db.collection('Analisis').stream()
        proveedores = db.collection('Proveedor').stream()
        alertas = db.collection('Alerta').stream()
        detalle = db.collection('DetalleVenta').stream()
        historial = db.collection('Historial').stream()

        list_values_analisis = []
        list_values_analisis_dump = []
        for doc in analisis:
            try:
                item = doc.to_dict()
                if request.session.get('id') == item['idUsuario']:
                    item.update({'id': doc.id})
                    list_values_analisis.append(item)
                    if len(list_values_analisis_dump) == 0:
                        list_values_analisis_dump.append(list(item))
                    list_values_analisis_dump.append(list(item.values()))
            except:
                c=1
        analisis_json = json.dumps(list_values_analisis_dump)

        list_ventas = []
        for doc in ventas:
            try:
                venta = doc.to_dict()
                venta.update({'id': doc.id})
                venta['idUsuario'] = db.collection('users').document(venta['idUsuario']).get().to_dict()['nombreUsuario']
                cliente_temp = db.collection('Cliente').document(venta['rutCliente']).get().to_dict()
                venta['rutCliente'] = f"{cliente_temp['nombreCliente']}: {venta['rutCliente']}-{cliente_temp['dvCliente']}"
                list_ventas.append(venta)
            except:
                c=1

        list_values_inventario = []
        for doc in inventario:
            try:
                item = doc.to_dict()
                item.update({'id': doc.id})
                item['idUsuario'] = db.collection('users').document(item['idUsuario']).get().to_dict()['nombreUsuario']
                proveedor_temp = db.collection('Proveedor').document(item['rutProveedor']).get().to_dict()
                item['rutProveedor'] = f"{proveedor_temp['nombreProveedor']}: {item['rutProveedor']}-{proveedor_temp['dvProveedor']}"
                list_values_inventario.append(item)
            except:
                c = 1

        list_proveedores = []
        for doc in proveedores:
            if doc.id != '1':
                try:
                    proveedor = doc.to_dict()
                    proveedor.update({'id': doc.id})
                    list_proveedores.append(venta)
                except:
                    c = 1

        list_alertas = []
        for doc in alertas:
            if doc.id != '1':
                try:
                    alert = doc.to_dict()
                    alert.update({'id': doc.id})
                    list_alertas.append(alert)
                except:
                    c = 1

        list_detalles = []
        for doc in detalle:
            if doc.id != '1':
                try:
                    det = doc.to_dict()
                    det.update({'id': doc.id})
                    list_detalles.append(det)
                except:
                    c = 1

        fecha_actual = datetime.now()

        list_historial = []
        for doc in historial:
            try:
                hist = doc.to_dict()
                if hist['fecha'][:7] == f'{fecha_actual.year}-{fecha_actual.month}':
                    hist.update({'id': doc.id})
                    list_historial.append(hist)
            except:
                c = 1

        path_lista = []
        path_imgs = []
        for i in range(4):
            path_lista.append(f'VentaseInventario/static/img/graficos/{fecha_actual.day}-{fecha_actual.month}-graph{i+1}.png')
            path_imgs.append(f'img/graficos/{fecha_actual.day}-{fecha_actual.month}-graph{i+1}.png')
        
        graph_dict = {}
        cont = 0
        for path in path_lista:
            cont += 1
            if os.path.exists(path):
                graph_dict[f'img_graph{cont}'] = path_imgs[cont-1]
                fecha_temporal = fecha_actual - timedelta(days=1)
                path_temporal = f'VentaseInventario/static/img/graficos/{fecha_temporal.day}-{fecha_temporal.month}-graph{cont}.png'
                if os.path.exists(path_temporal):
                    os.remove(path_temporal)
            elif cont == 1:
                grafico = grafico1(db, 'DetalleVenta', 'idProducto', 'idVenta', f'Cantidad de veces que un producto se asocio a una venta - {fecha_actual.day}-{fecha_actual.month}', 'Productos', 'Ventas', f'{fecha_actual.day}-{fecha_actual.month}-graph{cont}')
                graph_dict[f'img_graph{cont}'] = grafico
            elif cont == 2:
                grafico = grafico2(db, 'Alerta', 'idProducto', 'cantidadActual', 'cantidadEsperada', f'Compación de productos en estado de alerta - {fecha_actual.day}-{fecha_actual.month}', 'Productos', 'Cantidad', f'{fecha_actual.day}-{fecha_actual.month}-graph{cont}', color_y='green')
                graph_dict[f'img_graph{cont}'] = grafico
            elif cont == 3:
                grafico = grafico3(db, 'Historial', 'tipoModificacion', 'fecha', f'Cantidad de modificaciones mensuales - {fecha_actual.month}-{fecha_actual.year}', 'Productos', 'Ventas', f'{fecha_actual.day}-{fecha_actual.month}-graph{cont}')
                graph_dict[f'img_graph{cont}'] = grafico
            elif cont == 4:
                grafico = grafico4(db, 'DetalleVenta', 'idProducto', 'idVenta', f'Porcentaje de influencia en ventas por proveedor - {fecha_actual.day}-{fecha_actual.month}', 'Productos', 'Ventas', f'{fecha_actual.day}-{fecha_actual.month}-graph{cont}')
                graph_dict[f'img_graph{cont}'] = grafico
        resumen_dashboard = {
            'valor_1': len(list_detalles),
            'graph_1': graph_dict['img_graph1'],
            'valor_2': len(list_alertas),
            'graph_2': graph_dict['img_graph2'],
            'valor_3': len(list_historial),
            'graph_3': graph_dict['img_graph3'],
            'valor_4': len(list_proveedores),       
            'graph_4': graph_dict['img_graph4'],   
        }

        return render(request, 'VentaseInventario/dashboard.html', {'analisis_json': analisis_json,'ventas': list_ventas, 'inventario': list_values_inventario, 'role': request.session.get('role'), 'analisis': list_values_analisis, 'resumen_dashboard': resumen_dashboard})
    else:
        return render(request, 'VentaseInventario/login.html')    
    
def cerrarSesion(request):
    descripcion = f'Se cerró una sesión con la id: {request.session.get("id")}'
    agregarHistorial(request.session.get('id'), descripcion, 'Cerrar Sesión')
    request.session['sesion'] = False
    
    return render(request, 'VentaseInventario/login.html')

def grafico1(db, tabla, x, y, title, label_x, label_y, id_grafico, color_y='green'):
    tabla_ref = db.collection(tabla).stream()

    x_lista = []
    y_lista = []

    for doc in tabla_ref:
        try:
            x_value = doc.to_dict()[x]
            y_value = doc.to_dict()[y]

            x_lista.append(x_value)
            y_lista.append(y_value)
        except KeyError:
            pass

    x_lista_mod = []
    for item in x_lista:
        try:
            x_lista_mod.append(db.collection('Inventario').document(item).get().to_dict()['nombreProducto'])
        except:
            c = 1

    x_counter = Counter(x_lista_mod)

    # Get unique y values and their counts
    unique_x_values = list(x_counter.keys())
    counts = list(x_counter.values())

    plt.bar(unique_x_values, counts, color=color_y, label=f'{y} data')

    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)

    img_path = f'VentaseInventario/static/img/graficos/{id_grafico}.png'
    mostrar_img = f'img/graficos/{id_grafico}.png'

    plt.tight_layout()  # Asegura que las etiquetas no se superpongan
    plt.savefig(img_path)
    plt.close()

    return mostrar_img

def grafico4(db, tabla, x, y, title, label_x, label_y, id_grafico, color_y='green'):
    tabla_ref = db.collection(tabla).stream()

    x_lista = []
    y_lista = []

    for doc in tabla_ref:
        try:
            x_value = doc.to_dict()[x]
            y_value = doc.to_dict()[y]

            x_lista.append(x_value)
            y_lista.append(y_value)
        except KeyError:
            pass

    x_lista_mod = []
    for item in x_lista:
        try:
            rut = db.collection('Inventario').document(item).get().to_dict()['rutProveedor']
            x_lista_mod.append(db.collection('Proveedor').document(rut).get().to_dict()['nombreProveedor'])
        except:
            c = 1

    x_counter = Counter(x_lista_mod)

    # Get unique y values and their counts
    unique_x_values = list(x_counter.keys())
    counts = list(x_counter.values())

    plt.pie(counts, labels=unique_x_values, autopct='%1.1f%%')

    plt.title(title)

    img_path = f'VentaseInventario/static/img/graficos/{id_grafico}.png'
    mostrar_img = f'img/graficos/{id_grafico}.png'

    plt.tight_layout()  # Asegura que las etiquetas no se superpongan
    plt.savefig(img_path)
    plt.close()

    return mostrar_img

def grafico3(db, tabla, x, y, title, label_x, label_y, id_grafico, color_y='green'):
    tabla_ref = db.collection(tabla).stream()

    x_lista = []
    fecha_actual = datetime.now()

    for doc in tabla_ref:
        try:
            if doc.to_dict()[y][:7] == f'{fecha_actual.year}-{fecha_actual.month}':
                print(doc.to_dict()[y][:7], '-----', f'{fecha_actual.year}-{fecha_actual.month}')

                x_value = doc.to_dict()[x]

                x_lista.append(x_value)
        except KeyError:
            pass

    x_counter = Counter(x_lista)

    print(x_counter)
    unique_x_values = list(x_counter.keys())
    counts = list(x_counter.values())

    plt.pie(counts, labels=unique_x_values, autopct='%1.1f%%')

    plt.title(title)

    img_path = f'VentaseInventario/static/img/graficos/{id_grafico}.png'
    mostrar_img = f'img/graficos/{id_grafico}.png'

    plt.tight_layout()  # Asegura que las etiquetas no se superpongan
    plt.savefig(img_path)
    plt.close()

    return mostrar_img

def grafico2(db, tabla, x, y, z, title, label_x, label_y, id_grafico, color_y='green'):
    tabla_ref = db.collection(tabla).stream()

    x_lista = []
    y_lista = []
    z_lista = []

    for doc in tabla_ref:
        if doc.id != '1':
            try:
                x_value = doc.to_dict()[x]
                print(x_value)
                inv_ref = db.collection('Inventario').document(x_value).get().to_dict()
                print(inv_ref)

                x_lista.append(inv_ref['nombreProducto'])
                y_lista.append(int(inv_ref['cantidadActual']))
                z_lista.append(int(inv_ref['cantidadEsperada']))
            except KeyError:
                pass

    x = range(len(x_lista))  # X-axis positions for the bars

    plt.bar(x, y_lista, width=0.4, align='center', label='Cantidad Actual')
    plt.bar([i + 0.4 for i in x], z_lista, width=0.4, align='center', label='Cantidad Esperada')

    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks([i + 0.2 for i in x], x_lista)
    plt.legend(loc='center', bbox_to_anchor=(0.5, 1.15), shadow=True, ncol=2)

    img_path = f'VentaseInventario/static/img/graficos/{id_grafico}.png'
    mostrar_img = f'img/graficos/{id_grafico}.png'

    plt.tight_layout()  # Asegura que las etiquetas no se superpongan
    plt.savefig(img_path)
    plt.close()

    return mostrar_img

# VENTAS
def Ventas(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        ventas = db.collection('Ventas').stream()
        inventario = db.collection('Inventario').stream()
        detalle = db.collection('DetalleVenta').stream()
        list_ventas = []

        # Ultima key bitacora
        lista_bitacora = db.collection('BitacoraVentas').stream()
        lista_keys_bitacora = []
        try:
            for doc in lista_bitacora:
                try:
                    lista_keys_bitacora.append(int(doc.id))
                except:
                    c = 1
                            
            lista_keys_bitacora = sorted(lista_keys_bitacora)

            lista_keys_bitacora_int = lista_keys_bitacora[-1] + 1
            lista_keys_bitacora_str = str(lista_keys_bitacora_int)
        except:
            lista_keys_bitacora_str = '2'
        # Fin ultima key
    

        for doc in ventas:
            try:
                verif = True
                venta = doc.to_dict()
                venta.update({'id': doc.id})
                venta['idUsuario'] = db.collection('users').document(venta['idUsuario']).get().to_dict()['nombreUsuario']
                cliente_temp = db.collection('Cliente').document(venta['rutCliente']).get().to_dict()
                venta['rutCliente'] = f"{cliente_temp['nombreCliente']}: {venta['rutCliente']}-{cliente_temp['dvCliente']}"

                if venta['estado'] == 'Finalizado':
                    verif = False
                    cont = 0
                    contKey = 0
                    bitVenta = doc.to_dict()
                    for det in detalle:
                        if det.id != "1":
                            detDict = det.to_dict()
                            if doc.id == detDict['idVenta']:
                                cont += 1
                                productoBit = db.collection('Inventario').document(str(detDict['idProducto'])).get().to_dict()
                                bitVenta[f'prod{cont}'] = f'{productoBit["nombreProducto"]} - {detDict["cantidad"]}'
                    
                    db.collection('BitacoraVentas').document(str(int(lista_keys_bitacora_str) + contKey)).set(bitVenta)
                    contKey += 1
    
                    for det in detalle:
                        if det.id != "1":
                            detDict = det.to_dict()
                            if doc.id == detDict['idVenta']:
                                db.collection('DetalleVenta').document(str(det.id)).delete()

                    db.collection('Ventas').document(str(doc.id)).delete()

                if verif:
                    list_ventas.append(venta)
            except:
                c = 1

        list_inventario = []

        for doc in inventario:
            try:
                item = doc.to_dict()
                item.update({'id': doc.id})
                list_inventario.append(item)
            except:
                c = 1

        return render(request, 'VentaseInventario/Ventas.html', {'ventas': list_ventas, 'inventario': list_inventario, 'role': request.session.get('role')})
    else:
        return render(request, 'VentaseInventario/login.html')

def agregarVenta(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'ventas'):
        db = firestore.client()

        prod_ref = db.collection('Inventario').stream()
        cliente_ref = db.collection('Cliente').stream()
        productos = []
        cliente = []      

        for prod in prod_ref:
            try:
                prodDict = prod.to_dict()
                productos.append({'id': prod.id, 'nombre': prodDict['nombreProducto'], 'precio': prodDict['precioUnitario']})
            except:
                c = 1
        productos_json = json.dumps(productos)
        
        for cli in cliente_ref:
            if cli.id != 1:
                try:
                    cliDict = cli.to_dict()
                    cliente.append({'rut': cli.id, 'nombre': cliDict['nombreCliente'], 'dv': cliDict['dvCliente']})
                except:
                    c = 1

        if request.method == "POST":
            estado = request.POST.get('estado')
            fechainicio = request.POST.get('fechainicio')
            fechafin = request.POST.get('fechafin')
            pago = request.POST.get('pago')
            total = request.POST.get('total')
            rutCliente = request.POST.get('rutCliente')
            
            nuevo_venta = {
                'estado': estado,
                'fechaInicio': fechainicio,
                'fechaFin': fechafin,
                'idUsuario': request.session.get('id'),
                'rutCliente': rutCliente,
                'tipoPago': pago,
                'total': total,
            }

            ventas_ref = db.collection('Ventas')

            detalle_ref = db.collection('DetalleVenta')


            try:
                # Ultima key ventas
                lista_ventas = ventas_ref.stream()
                lista_keys_ventas = []
                try:
                    for doc in lista_ventas:
                        try:
                            lista_keys_ventas.append(int(doc.id))
                        except:
                            c = 1
                                    
                    lista_keys_ventas = sorted(lista_keys_ventas)

                    ultima_key_ventas_int = lista_keys_ventas[-1] + 1
                    ultima_key_ventas_str = str(ultima_key_ventas_int)
                except:
                    ultima_key_ventas_str = '2'
                # Fin ultima key

                # Ultima key detalle
                lista_detalles = detalle_ref.stream()
                lista_keys_detalles = []
                try:
                    for doc in lista_detalles:
                        try:
                            lista_keys_detalles.append(int(doc.id))
                        except:
                            c = 1
                                    
                    lista_keys_detalles = sorted(lista_keys_detalles)

                    ultima_key_detalles_int = lista_keys_detalles[-1] + 1
                    ultima_key_detalles_str = str(ultima_key_detalles_int)
                except:
                    ultima_key_detalles_str = '2'
                # Fin ultima key

                # Ultima key alerta
                lista_alertas = db.collection('Alerta').stream()
                lista_keys_alertas = []
                try:
                    for doc in lista_alertas:
                        try:
                            lista_keys_alertas.append(int(doc.id))
                        except:
                            c = 1
                                    
                    lista_keys_alertas = sorted(lista_keys_alertas)

                    lista_keys_alertas_int = lista_keys_alertas[-1] + 1
                    lista_keys_alertas_str = str(lista_keys_alertas_int)
                except:
                    lista_keys_alertas_str = '2'
                # Fin ultima key

                lista_detalles = []
                productos_insuficientes = []
                verificador_productos = True
                for i in range(5):
                    if request.POST.get(f'idProducto{i+1}') != None:
                        prod_ref_dict = db.collection('Inventario').document(request.POST.get(f'idProducto{i+1}')).get().to_dict()
                        prod_canta = prod_ref_dict['cantidadActual']
                        if int(request.POST.get(f'cantidad{i+1}')) > int(prod_canta):
                            productos_insuficientes.append(f'{request.POST.get(f"idProducto{i+1}")}: {prod_ref_dict["nombreProducto"]}')
                            verificador_productos = False
                        elif verificador_productos: 
                            lista_detalles.append({
                                'cantidad': request.POST.get(f'cantidad{i+1}'),
                                'porcentajeDesc': request.POST.get(f'descuento{i+1}'),
                                'idProducto': request.POST.get(f'idProducto{i+1}'),
                                'idVenta': ultima_key_ventas_str,
                                'idUsuario': request.session.get('id')
                            })

                if verificador_productos:                
                    ventas_ref.document(ultima_key_ventas_str).set(nuevo_venta)   
                    descripcion = f'Se agregó una nueva venta con la id: {ultima_key_ventas_str}'
                    agregarHistorial(request.session.get('id'), descripcion, 'Agregar Venta')
                    for detalle in lista_detalles:
                        detalle_ref.document(ultima_key_detalles_str).set(detalle)
                        ultima_key_detalles_str = str(int(ultima_key_detalles_str)+1)
                        descripcion = f'Se agregó un nuevo detalle de venta con la id: {ultima_key_detalles_str}'
                        agregarHistorial(request.session.get('id'), descripcion, 'Agregar Detalle')
                        prod_upd = db.collection('Inventario').document(detalle['idProducto'])
                        prod_upd.update({
                            'cantidadActual': prod_upd.get().to_dict()['cantidadActual'] - int(detalle['cantidad'])
                        })
                        if int(prod_upd.get().to_dict()['cantidadActual']) < int(prod_upd.get().to_dict()['cantidadEsperada']):
                            alerta = {
                                'descripcion': f'Faltan productos de la id: {detalle["idProducto"]}, reponer lo mas pronto posible',
                                'idProducto': detalle['idProducto'],
                                'tipo': 'Stock'
                            }
                            db.collection('Alerta').document(lista_keys_alertas_str).set(alerta)

                    messages.success(request, 'Venta ingresada de manera correcta')
                else:
                    messages.error(request, f'Los siguientes productos: {productos_insuficientes} \nNo presentan stock suficiente, inténtelo nuevamente')
            except Exception as e:
                messages.error(request, 'Error al ingresar la venta: ' + str(e))

        return render(request, 'VentaseInventario/agregarVenta.html', {'productos': productos, 'cliente': cliente, 'productos_json': productos_json})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')
    
def modificarventa(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'ventas'):
        db = firestore.client()
        ventas = db.collection('Ventas').stream()
        list_values_ventas = []

        for doc in ventas:
            try:
                item = doc.to_dict()
                item.update({'id': doc.id})
                item['idUsuario'] = db.collection('users').document(item['idUsuario']).get().to_dict()['nombreUsuario']
                cliente_temp = db.collection('Cliente').document(item['rutCliente']).get().to_dict()
                item['rutCliente'] = f"{cliente_temp['nombreCliente']}: {item['rutCliente']}-{cliente_temp['dvCliente']}"
                list_values_ventas.append(item)
            except:
                c = 1
        return render(request, 'VentaseInventario/modificarventa.html', {'ventas': list_values_ventas})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')

def editarVenta(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'ventas'):
        venta_id = request.GET.get('venta_id') 
        db = firestore.client()
        venta_ref = db.collection('Ventas').document(venta_id)
        cliente_ref = db.collection('Cliente').stream()
        detalle_ref = db.collection('DetalleVenta').stream()
        prod_ref = db.collection('Inventario').stream()
        productos = []
        cliente = []
        lista_detalles = []

        # Ultima key alerta
        lista_alertas = db.collection('Alerta').stream()
        lista_keys_alertas = []
        try:
            for doc in lista_alertas:
                try:
                    lista_keys_alertas.append(int(doc.id))
                except:
                    c = 1
                            
            lista_keys_alertas = sorted(lista_keys_alertas)

            lista_keys_alertas_int = lista_keys_alertas[-1] + 1
            lista_keys_alertas_str = str(lista_keys_alertas_int)
        except:
            lista_keys_alertas_str = '2'
        # Fin ultima key

        # Ultima key detalle
        lista_detalles_keys = db.collection('DetalleVenta').stream()
        lista_keys_detalles = []
        try:
            for doc in lista_detalles_keys:
                try:
                    lista_keys_detalles.append(int(doc.id))
                except:
                    c = 1
                            
            lista_keys_detalles = sorted(lista_keys_detalles)

            ultima_key_detalles_int = lista_keys_detalles[-1] + 1
            ultima_key_detalles_str = str(ultima_key_detalles_int)
        except:
            ultima_key_detalles_str = '2'
        # Fin ultima key

        for doc in detalle_ref:
            try:
                if doc.to_dict()['idVenta'] == venta_id:
                    lista_detalles.append(doc.to_dict())
            except:
                c = 1

        for prod in prod_ref:
            try:
                prodDict = prod.to_dict()
                productos.append({'id': prod.id, 'nombre': prodDict['nombreProducto'], 'precio': prodDict['precioUnitario']})
            except:
                c = 1
        productos_json = json.dumps(productos)

        venta = venta_ref.get().to_dict()
        if venta:
            venta['fechaInicio'] = datetime.strptime(venta['fechaInicio'], '%Y-%m-%d').date()
            venta['fechaFin'] = datetime.strptime(venta['fechaFin'], '%Y-%m-%d').date() 
        
        for cli in cliente_ref:
            if cli.id != 1:
                try:
                    cliDict = cli.to_dict()
                    cliente.append({'rut': str(cli.id), 'nombre': cliDict['nombreCliente'], 'dv': cliDict['dvCliente']})
                except:
                    c = 1

        if venta:
            if request.method == "POST":
                estado = request.POST.get('estado')
                fechainicio = request.POST.get('fechainicio')
                fechafin = request.POST.get('fechafin')
                pago = request.POST.get('pago')
                total = request.POST.get('total')
                rutCliente = request.POST.get('rutCliente')
                
                nuevo_venta = {
                    'estado': estado,
                    'fechaInicio': fechainicio,
                    'fechaFin': fechafin,
                    'idUsuario': request.session.get('id'),
                    'rutCliente': rutCliente,
                    'tipoPago': pago,
                    'total': total,
                }

                try:
                    detalle_ref = db.collection('DetalleVenta').stream()
                    lista_detalles = []
                    lista_alertas_temp = []
                    id_detalle_venta = []
                    verificador_productos = True
                    productos_insuficientes = []
                    cantidadesTemporales = []

                    for det in detalle_ref:
                        try:
                            if det.to_dict()['idVenta'] == venta_id:
                                id_detalle_venta.append(det.id)     
                        except:
                            c = 1                       

                    id_dinamic = 0
                    verif = False
                    for cont in range(5):
                        try:
                            detalle_ref_temp = db.collection('DetalleVenta').document(id_detalle_venta[cont])
                        except:
                            ultima_key_detalles_str = int(ultima_key_detalles_str) + id_dinamic
                            id_detalle_venta.append(str(ultima_key_detalles_str))
                            id_dinamic += 1
                            verif = True
                        if request.POST.get(f'idProducto{cont+1}') != None:
                            prod_ref_dict = db.collection('Inventario').document(request.POST.get(f'idProducto{cont+1}')).get().to_dict()
                            if verif:
                                cantidadDetalle = '0'
                            else:
                                cantidadDetalle = detalle_ref_temp.get().to_dict()['cantidad']
                            cantidadInventario = prod_ref_dict['cantidadActual']
                            nuevaCantidad = request.POST.get(f'cantidad{cont+1}')
                            if int(nuevaCantidad) > int(cantidadInventario)+int(cantidadDetalle):
                                productos_insuficientes.append(f'{request.POST.get(f"idProducto{cont+1}")}: {prod_ref_dict["nombreProducto"]}')
                                verificador_productos = False
                            elif int(cantidadInventario)+int(cantidadDetalle)-int(nuevaCantidad) < prod_ref_dict['cantidadEsperada']:
                                lista_alertas_temp.append({
                                    'descripcion': f'Faltan productos de la id: {request.POST.get(f"idProducto{cont+1}")}, reponer lo mas pronto posible',
                                    'idProducto': request.POST.get(f"idProducto{cont+1}"),
                                    'tipo': 'Stock'
                                })
                                cantidadesTemporales.append(int(cantidadInventario)+int(cantidadDetalle)-int(nuevaCantidad))
                                lista_detalles.append({
                                    'cantidad': request.POST.get(f'cantidad{cont+1}'),
                                    'porcentajeDesc': request.POST.get(f'descuento{cont+1}'),
                                    'idProducto': request.POST.get(f'idProducto{cont+1}'),
                                    'idVenta': venta_id,
                                    'idUsuario': request.session.get('id')
                                })
                            else:
                                cantidadesTemporales.append(int(cantidadInventario)+int(cantidadDetalle)-int(nuevaCantidad))
                                lista_detalles.append({
                                    'cantidad': request.POST.get(f'cantidad{cont+1}'),
                                    'porcentajeDesc': request.POST.get(f'descuento{cont+1}'),
                                    'idProducto': request.POST.get(f'idProducto{cont+1}'),
                                    'idVenta': venta_id,
                                    'idUsuario': request.session.get('id')
                                })

                    if verificador_productos:
                        cont = 0
                        for det in lista_detalles:
                            try:
                                detalle_ref_temp = db.collection('DetalleVenta').document(id_detalle_venta[cont])
                                db.collection('Inventario').document(det['idProducto']).update({
                                    'cantidadActual': cantidadesTemporales[cont]
                                })
                                detalle_ref_temp.update(det)
                            except:
                                detalle_ref_temp = db.collection('DetalleVenta').document(id_detalle_venta[cont])
                                db.collection('Inventario').document(det['idProducto']).update({
                                    'cantidadActual': cantidadesTemporales[cont]
                                })
                                detalle_ref_temp.set(det)
                            cont += 1

                        cont_key_alertas = 0
                        for alert in lista_alertas_temp:
                            lista_keys_alertas_str = int(lista_keys_alertas_str) + cont_key_alertas
                            db.collection('Alerta').document(str(lista_keys_alertas_str)).set(alert)
                            cont_key_alertas += 1
                        venta_ref.update(nuevo_venta)
                        descripcion = f'Se editó una venta con la id: {venta_id}'
                        agregarHistorial(request.session.get('id'), descripcion,'Editar Venta')
                        messages.success(request, 'Venta cambiada correctamente')
                    else:
                        messages.error(request, f'Los siguientes productos: {productos_insuficientes} \nNo presentan stock suficiente, inténtelo nuevamente')
                except Exception as e:
                    messages.error(request, 'Error al modificar la venta: ' + str(e))
        else:
            messages.error(request, 'Producto no encontrado')
        return render(request, 'VentaseInventario/editarVenta.html', {'venta': venta, 'detalle_venta': lista_detalles, 'cliente': cliente, 'productos': productos, 'productos_json': productos_json})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')

def eliminar_venta(request, venta_id):
    if request.session.get('sesion') == True:
        try:
            db = firestore.client()
            verificador = False
            if db.collection('Ventas').document(venta_id).get().to_dict()['estado'] == 'En Proceso':
                verificador = True
            db.collection('Ventas').document(venta_id).delete()
            det_ref = db.collection('DetalleVenta').stream()
            for doc in det_ref:
                try:
                    if venta_id == doc.to_dict()['idVenta']:
                        if verificador:
                            inv_doc = db.collection('Inventario').document(doc.to_dict()['idProducto'])
                            inv_doc.update({
                                'cantidadActual': inv_doc.get().to_dict()['cantidadActual'] + int(doc.to_dict()['cantidad'])
                            })
                        db.collection('DetalleVenta').document(doc.id).delete()
                except:
                    c = 1
            descripcion = f'Se eliminó una venta con la id: {venta_id}'
            agregarHistorial(request.session.get('id'), descripcion,'Eliminación venta')
            return redirect('modificarventa')
        except Exception as e:
            return HttpResponse(f'Error al eliminar la venta: {e}')
    else:
        return render(request, 'VentaseInventario/login.html')

def bitacoraVentas(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'ventas'):
        db = firestore.client()
        bitventa_ref = db.collection('BitacoraVentas').stream()
        bitventas = []
        for doc in bitventa_ref:
            if doc.id != "1":
                try:
                    bitventDict = doc.to_dict()
                    bitventDict['id'] = doc.id
                    bitventas.append(bitventDict)
                except:
                    c = 1

        return render(request, 'VentaseInventario/bitacoraVentas.html', {'bitVentas': bitventas})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')



# INVENTARIO
def agregarInventario(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        db = firestore.client()

        inv_ref = db.collection('Inventario')
        prov_ref = db.collection('Proveedor').stream()
        proveedores = []

        for prov in prov_ref:
            if prov.id != '1':
                try:
                    provDict = prov.to_dict()
                    proveedores.append({'rut': prov.id, 'dv': provDict['dvProveedor'], 'nombre': provDict['nombreProveedor']})
                except:
                    c = 1

        if request.method == "POST":
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            cantidad_esperada = request.POST.get('cantidad_esperada')
            precio_unidad = request.POST.get('precio_unidad')
            cantidad_actual = request.POST.get('cantidad_actual')
            rut_proveedor = request.POST.get('idProveedor')

            nuevo_producto = {
                'nombreProducto': nombre,
                'descripcion': descripcion,
                'cantidadEsperada': int(cantidad_esperada),
                'precioUnitario': int(precio_unidad),
                'cantidadActual': int(cantidad_actual),
                'rutProveedor': str(rut_proveedor),
                'idUsuario': request.session.get('id')
            }

            # Ultima key inventario
            lista_inventario = inv_ref.stream()
            lista_keys_inventario = []
            verificador = True   
            try:
                for doc in lista_inventario:
                    try:
                        lista_keys_inventario.append(int(doc.id))                           
                        if verificador and doc.get('nombreProducto').lower() == nuevo_producto['nombreProducto'].lower():
                            if doc.get('rutProveedor').lower() == nuevo_producto['rutProveedor'].lower():
                                verificador = False 
                    except:
                        c = 1
                                
                lista_keys_inventario = sorted(lista_keys_inventario)

                lista_keys_inventario_int = lista_keys_inventario[-1] + 1
                lista_keys_inventario_str = str(lista_keys_inventario_int)
            except:
                lista_keys_inventario_str = '2'
            # Fin ultima key               

            if verificador:
                inv_ref.document(lista_keys_inventario_str).set(nuevo_producto)
                descripcion = f'Se agregó un nuevo producto con la id: {lista_keys_inventario_str}'
                agregarHistorial(request.session.get('id'), descripcion, 'Agregar Producto')
                messages.success(request, 'Producto ingresado de manera correcta')
            else:
                messages.error(request, 'El producto ingresado ya se encuentra en la base de datos')
        return render(request, 'VentaseInventario/agregarInventario.html', {'proveedores': proveedores})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')   

def modificarinv(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        db = firestore.client()
        inventario = db.collection('Inventario').stream()
        productos = []

        for doc in inventario:
            try:
                item = doc.to_dict()
                item['id'] = doc.id
                item['idUsuario'] = db.collection('users').document(item['idUsuario']).get().to_dict()['nombreUsuario']
                productos.append(item)
            except:
                c = 1

        return render(request, 'VentaseInventario/modificarinv.html', {'productos': productos})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')

def eliminar_producto(request, producto_id):
    if request.session.get('sesion') == True:
        db = firestore.client()
        det_ref = db.collection('DetalleVenta').stream()
        aler_ref = db.collection('Alerta').stream()
        ids_ven = []

        verificador = True
        for doc in det_ref:
            try:
                if doc.to_dict()['idVenta'] not in ids_ven:
                    if producto_id == doc.to_dict()['idProducto']:
                        ids_ven.append(doc.to_dict()['idVenta'])
                        verificador = False 
            except:
                c = 1

        if verificador:
            try:
                db.collection('Inventario').document(producto_id).delete()
                for doc in aler_ref:
                    try:
                        if aler_ref.to_dict()['idProducto'] == producto_id:
                            db.collection('Alerta').document(doc.id).delete()
                    except:
                        c = 1
                descripcion = f'Se eliminó un producto con la id: {producto_id}'
                agregarHistorial(request.session.get('id'), descripcion,'Eliminación producto')
                
                return redirect('modificarinv')

            except Exception as e:
                return HttpResponse(f'Error al eliminar el producto: {str(e)}')
        else:
            messages.error(request,f'No se puede eliminar el producto, debido a que tiene las siguientes ventas asociadas: {ids_ven}')
            return redirect('modificarinv')

    else:
        return render(request, 'VentaseInventario/login.html')

def editarProducto(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        producto_id = request.GET.get('producto_id') 
        db = firestore.client()
        producto_ref = db.collection('Inventario').document(producto_id)
        producto = producto_ref.get().to_dict()
        prov_ref = db.collection('Proveedor').stream()

        proveedores = []

        for prov in prov_ref:
            if prov.id != '1':
                try:
                    provDict = prov.to_dict()
                    proveedores.append({'rut': prov.id, 'dv': provDict['dvProveedor'], 'nombre': provDict['nombreProveedor']})
                except:
                    c = 1

        if producto:
            if request.method == "POST":
                nombre = request.POST.get('nombre')
                descripcion = request.POST.get('descripcion')
                cantidad_esperada = request.POST.get('cantidad_esperada')
                precio_unidad = request.POST.get('precio_unidad')
                cantidad_actual = request.POST.get('cantidad_actual')
                rut_proveedor = request.POST.get('idProveedor')

                nuevo_producto = {
                    'nombreProducto': nombre,
                    'descripcion': descripcion,
                    'cantidadEsperada': int(cantidad_esperada),
                    'precioUnitario': int(precio_unidad),
                    'cantidadActual': int(cantidad_actual),
                    'rutProveedor': str(rut_proveedor),
                    'idUsuario': request.session.get('id')
                }

                try:
                    producto_ref.update(nuevo_producto)
                    descripcion = f'Se editó un producto con la id: {producto_id}'
                    agregarHistorial(request.session.get('id'), descripcion,'Editar Producto')
                    messages.success(request, 'Producto editado de manera correcta')
                except Exception as e:
                    messages.error(request, f'Error al editar el producto: {str(e)}')
        elif request.session.get('sesion') == True:
            return render(request, 'VentaseInventario/dashboard.html')
        else:
            messages.error(request, 'Producto no encontrado')
        return render(request, 'VentaseInventario/editarProducto.html', {'producto': producto, 'proveedores': proveedores})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')

def productos(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        alerta_ref = db.collection('Alerta').stream()
        inventario = db.collection('Inventario').stream()
        list_alertas = []
        list_values_inventario = []
        verif_alertas = False
        alerta_ref = db.collection('Alerta').stream()

        # Ultima key alerta
        lista_alertas = db.collection('Alerta').stream()
        lista_keys_alertas = []
        try:
            for doc in lista_alertas:
                try:
                    lista_keys_alertas.append(int(doc.id))
                except:
                    c = 1
                            
            lista_keys_alertas = sorted(lista_keys_alertas)

            lista_keys_alertas_int = lista_keys_alertas[-1] + 1
            lista_keys_alertas_str = str(lista_keys_alertas_int)
        except:
            lista_keys_alertas_str = '2'
        # Fin ultima key

        for doc in alerta_ref:
            if doc.id != '1':
                item = doc.to_dict()
                list_alertas.append(item['idProducto'])

        if len(list_alertas) > 1:
            verif_alertas = True

        try:
            for doc in inventario:
                verif = True
                try:
                    item = doc.to_dict()
                    item.update({'id': doc.id})
                    if int(item['cantidadActual']) < int(item['cantidadEsperada']):
                        for id in list_alertas:
                            if str(id) == str(item['id']):
                                verif = False
                        if verif:
                            alerta = {
                                'descripcion': f'Faltan productos de la id: {item["id"]}, reponer lo mas pronto posible',
                                'idProducto': item['id'],
                                'tipo': 'Stock'
                            }
                            db.collection('Alerta').document(lista_keys_alertas_str).set(alerta)
                            lista_keys_alertas_str = str(int(lista_keys_alertas_str) + 1)
                            verif_alertas = True

                    item['idUsuario'] = db.collection('users').document(item['idUsuario']).get().to_dict()['nombreUsuario']
                    proveedor_temp = db.collection('Proveedor').document(item['rutProveedor']).get().to_dict()
                    item['rutProveedor'] = f"{proveedor_temp['nombreProveedor']}: {item['rutProveedor']}-{proveedor_temp['dvProveedor']}"
                    list_values_inventario.append(item)
                except:
                    c = 1
        except:
            list_values_inventario = []
        return render(request, 'VentaseInventario/productos.html', {'inventario': list_values_inventario, 'role': request.session.get('role'), 'alertas': list_alertas, 'verif_alerta': verif_alertas})
    else:
        return render(request, 'VentaseInventario/login.html')    

def proveedores(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        proveedores = db.collection('Proveedor').stream()
        list_values_proveedor = []
        for doc in proveedores:
            if doc.id != '1':
                try:
                    item = doc.to_dict()
                    item.update({'id': doc.id})
                    list_values_proveedor.append(item)
                except:
                    c=1
        return render(request, 'VentaseInventario/proveedores.html', {'proveedor': list_values_proveedor, 'role': request.session.get('role')})
    else:
        return render(request, 'VentaseInventario/login.html')
    
def agregarProveedor(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        db = firestore.client()

        prov_ref = db.collection('Proveedor')

        if request.method == "POST":
            rutProveedor = request.POST.get('rutProveedor')
            dvProveedor = request.POST.get('dvProveedor')
            nombreProveedor = request.POST.get('nombreProveedor')

            nuevo_proveedor = {
                'dvProveedor': dvProveedor,
                'nombreProveedor': nombreProveedor,
                'idUsuario': request.session.get('id')
            }           

            verificador = True

            prov_stream = prov_ref.stream()
            for prov in prov_stream:
                try:
                    if str(prov.id) == str(rutProveedor):
                        verificador = False
                except:
                    c = 1

            if verificador:
                prov_ref.document(str(rutProveedor)).set(nuevo_proveedor)
                descripcion = f'Se agregó un nuevo proveedor con la id: {str(rutProveedor)}'
                agregarHistorial(request.session.get('id'), descripcion, 'Agregar Proveedor')
                messages.success(request, 'Proveedor ingresado de manera correcta')
            else:
                messages.error(request, 'El proveedor ingresado ya se encuentra en la base de datos')
        return render(request, 'VentaseInventario/agregarProveedor.html')
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')   

def editarProveedor(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        proveedor_id = request.GET.get('proveedor_id') 
        db = firestore.client()
        proveedor_ref = db.collection('Proveedor').document(proveedor_id)
        proveedor = proveedor_ref.get().to_dict()
        proveedor['rutProveedor'] = proveedor_id

        if proveedor:
            if request.method == "POST":
                rutProveedor = request.POST.get('rutProveedor')
                dvProveedor = request.POST.get('dvProveedor')
                nombreProveedor = request.POST.get('nombreProveedor')

                nuevo_proveedor = {
                    'dvProveedor': dvProveedor,
                    'nombreProveedor': nombreProveedor,
                    'idUsuario': request.session.get('id')
                }    

                try:
                    if rutProveedor != proveedor_id:
                        proveedor_ref.delete()
                        proveedor_ref = db.collection('Proveedor').document(rutProveedor)
                        proveedor_ref.set(nuevo_proveedor)
                        descripcion = f'Se editó un proveedor con la id: {proveedor_id}'
                        agregarHistorial(request.session.get('id'), descripcion,'Editar Proveedor')
                    else:
                        proveedor_ref.update(nuevo_proveedor)
                        descripcion = f'Se editó un proveedor con la id: {proveedor_id}'
                        agregarHistorial(request.session.get('id'), descripcion,'Editar Proveedor')
                    
                    messages.success(request, 'Proveedor editado de manera correcta')
                except Exception as e:
                    messages.error(request, f'Error al editar el proveedor: {str(e)}')
        else:
            messages.error(request, 'Proveedor no encontrado')

        return render(request, 'VentaseInventario/editarProveedor.html', {'proveedor': proveedor})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')

def eliminar_proveedor(request, proveedor_id):
    if request.session.get('sesion') == True:
        db = firestore.client()
        inv_ref = db.collection('Inventario').stream()
        ids_inv = []
        verificador = True
        for doc in inv_ref:
            try:
                if proveedor_id == doc.to_dict()['rutProveedor']:
                    ids_inv.append(doc.id)
                    verificador = False
            except:
                c = 1
        
        if verificador:
            try:
                db.collection('Proveedor').document(proveedor_id).delete()
                descripcion = f'Se eliminó un proveedor con la id: {proveedor_id}'
                agregarHistorial(request.session.get('id'), descripcion,'Eliminación proveedor')
                return redirect('proveedores')
            except Exception as e:
                return HttpResponse(f'Error al eliminar el proveedor {str(e)}')
        else:
            messages.error(request, f'No se puede eliminar el Proveedor, debido a que tiene los siguientes productos asociados: {ids_inv}')
            return redirect('proveedores')
        
    else:
        return render(request, 'VentaseInventario/login.html')

def clientes(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        cliente = db.collection('Cliente').stream()
        list_values_cliente = []
        for doc in cliente:
            if doc.id != '1':
                try:
                    item = doc.to_dict()
                    item.update({'id': doc.id})
                    list_values_cliente.append(item)
                except:
                    c = 1
        return render(request, 'VentaseInventario/clientes.html', {'cliente': list_values_cliente, 'role': request.session.get('role')})
    else:
        return render(request, 'VentaseInventario/login.html')
    
def agregarCliente(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        db = firestore.client()

        cli_ref = db.collection('Cliente')

        if request.method == "POST":
            rutCliente = request.POST.get('rutCliente')
            dvCliente = request.POST.get('dvCliente')
            nombreCliente = request.POST.get('nombreCliente')
            estadoCliente = request.POST.get('estadoCliente')
            direccion = request.POST.get('direccion')

            nuevo_cliente = {
                'dvCliente': dvCliente,
                'nombreCliente': nombreCliente,
                'estadoCliente': estadoCliente,
                'direccion': direccion,
                'idUsuario': request.session.get('id')
            }           

            verificador = True

            cli_stream = cli_ref.stream()
            for cli in cli_stream:
                try:
                    if str(cli.id) == str(rutCliente):
                        verificador = False
                except:
                    c = 1

            if verificador:
                cli_ref.document(str(rutCliente)).set(nuevo_cliente)
                descripcion = f'Se agregó un nuevo cliente con la id: {str(rutCliente)}'
                agregarHistorial(request.session.get('id'), descripcion, 'Agregar Cliente')
                messages.success(request, 'Cliente ingresado de manera correcta')
            else:
                messages.error(request, 'El cliente ingresado ya se encuentra en la base de datos')
        return render(request, 'VentaseInventario/agregarCliente.html')
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')   

def editarCliente(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        cliente_id = request.GET.get('cliente_id') 
        db = firestore.client()
        cliente_ref = db.collection('Cliente').document(cliente_id)
        cliente = cliente_ref.get().to_dict()
        cliente['rutCliente'] = cliente_id

        if cliente:
            if request.method == "POST":
                rutCliente = request.POST.get('rutCliente')
                dvCliente = request.POST.get('dvCliente')
                nombreCliente = request.POST.get('nombreCliente')
                estadoCliente = request.POST.get('estadoCliente')
                direccion = request.POST.get('direccion')

                nuevo_cliente = {
                    'dvCliente': dvCliente,
                    'nombreCliente': nombreCliente,
                    'estadoCliente': estadoCliente,
                    'direccion': direccion,
                    'idUsuario': request.session.get('id')
                }       

                try:
                    if rutCliente != cliente_id:
                        cliente_ref.delete()
                        cliente_ref = db.collection('Cliente').document(rutCliente)
                        cliente_ref.set(nuevo_cliente)
                        descripcion = f'Se editó un cliente con la id: {cliente_id}'
                        agregarHistorial(request.session.get('id'), descripcion,'Editar Cliente')
                    else:
                        cliente_ref.update(nuevo_cliente)
                        descripcion = f'Se editó un cliente con la id: {cliente_id}'
                        agregarHistorial(request.session.get('id'), descripcion,'Editar Cliente')
                    
                    messages.success(request, 'Cliente editado de manera correcta')
                except Exception as e:
                    messages.error(request, f'Error al editar el cliente: {str(e)}')
        else:
            messages.error(request, 'cliente no encontrado')

        return render(request, 'VentaseInventario/editarCliente.html', {'cliente': cliente})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')

def eliminar_cliente(request, cliente_id):
    if request.session.get('sesion') == True:
        db = firestore.client()
        venta_ref = db.collection('Ventas').stream()
        ids_ventas = []
        verificador = True
        for doc in venta_ref:
            try:
                if cliente_id == doc.to_dict()['rutCliente']:
                    ids_ventas.append(doc.id)
                    verificador = False
            except:
                c = 1

        if verificador:
            try:            
                db.collection('Cliente').document(cliente_id).delete()
                descripcion = f'Se eliminó un cliente con la id: {cliente_id}'
                agregarHistorial(request.session.get('id'), descripcion,'Eliminación Cliente')
                return redirect('clientes')
            except Exception as e:
                return HttpResponse(f'Error al eliminar el cliente {str(e)}')
        else:
            messages.error(request,f'No se puede eliminar el cliente, debido a que tiene las siguientes ventas asociadas: {ids_ventas}')
            return redirect('clientes')
    else:
        return render(request, 'VentaseInventario/login.html')
    
def alertas(request):
    if request.session.get('sesion') == True and (request.session.get('role') == 'admin' or request.session.get('role') == 'ventasInventario' or request.session.get('role') == 'inventario'):
        db = firestore.client()
        alerta_ref = db.collection('Alerta').stream()
        list_alerta = []
        for doc in alerta_ref:
            try:
                alerta_temp = doc.to_dict()
                alerta_temp['id'] = doc.id
                prod = db.collection('Inventario').document(alerta_temp['idProducto']).get().to_dict()
                if prod['cantidadActual'] < prod['cantidadEsperada']:
                    list_alerta.append(alerta_temp)
                else:
                    db.collection('Alerta').document(doc.id).delete()
            except:
                c = 1
        return render(request, 'VentaseInventario/alertas.html', {'alerta': list_alerta})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')
    


# USUARIO   
def usuario(request):
    if request.session.get('sesion') == True and request.session.get('role') == 'admin':
        db = firestore.client()
        usuarios = db.collection('users').stream()
        list_values_usuario = []
        for doc in usuarios:
            try:
                usuario = doc.to_dict()
                if usuario['activo']:
                    usuario.update({'id': doc.id})
                    list_values_usuario.append(usuario)
            except:
                c = 1

        return render(request, 'VentaseInventario/usuario.html', {'usuarios': list_values_usuario, 'role': request.session.get('role')})
    elif request.session.get('sesion') == True:
        return render(request, 'VentaseInventario/dashboard.html')
    else:
        return render(request, 'VentaseInventario/login.html')

def agregarUsuario(request):
    if request.session.get('sesion') == True and request.session.get('role') == 'admin':
        db = firestore.client()

        usr_ref = db.collection('users')

        if request.method == "POST":
            nombreUsuario = request.POST.get('nombreUsuario')
            emailUsuario = request.POST.get('emailUsuario')
            psswUsuario = request.POST.get('psswUsuario')

            if request.POST.get('admin'):
                rolUsuario = 'admin'
            elif request.POST.get('inventario') and request.POST.get('ventas'):
                rolUsuario = 'ventasInventario'
            elif request.POST.get('inventario'):
                rolUsuario = 'inventario'
            elif request.POST.get('ventas'):
                rolUsuario = 'ventas'
            # en caso de que no se de ningun rol bloquear la creación de usuario

            nuevo_usuario_tabla = {
                'nombreUsuario': nombreUsuario,
                'rolUsuario': rolUsuario,
                'emailUsuario': emailUsuario,
                'psswUsuario': psswUsuario,
                'activo': True
            }

            verificador = True

            usr_stream = usr_ref.stream()
            for usr in usr_stream:
                try:
                    if str(usr.to_dict()['emailUsuario']) == str(emailUsuario) and usr.to_dict()['activo'] != True:
                        verificador = False
                except:
                    c = 1

            if verificador:
                nuevo_usuario = auth.create_user(
                    email=emailUsuario,
                    password=psswUsuario,
                )
                usr_ref.document(str(nuevo_usuario.uid)).set(nuevo_usuario_tabla)
                descripcion = f'Se agregó un nuevo usuario con la id: {str(nuevo_usuario.uid)}'
                agregarHistorial(request.session.get('id'), descripcion, 'Agregar Usuario')
                messages.success(request, 'Usuario ingresado de manera correcta')
            else:
                messages.error(request, 'El usuario ingresado ya se encuentra en la base de datos')
        return render(request, 'VentaseInventario/agregarUsuario.html')
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')   

def editarUsuario(request):
    if request.session.get('sesion') == True and request.session.get('role') == 'admin':
        usr_id = request.GET.get('usuario_id') 
        db = firestore.client()
        usuario_ref = db.collection('users').document(usr_id)
        usuario = usuario_ref.get().to_dict()
        usuario['rutCliente'] = usr_id 

        if usuario:
            if request.method == "POST":
                nombreUsuario = request.POST.get('nombreUsuario')
                emailUsuario = request.POST.get('emailUsuario')

                if request.POST.get('admin'):
                    rolUsuario = 'admin'
                elif request.POST.get('inventario') and request.POST.get('ventas'):
                    rolUsuario = 'ventasInventario'
                elif request.POST.get('inventario'):
                    rolUsuario = 'inventario'
                elif request.POST.get('ventas'):
                    rolUsuario = 'ventas'

                nuevo_usuario_tabla = {
                    'nombreUsuario': nombreUsuario,
                    'rolUsuario': rolUsuario,
                    'emailUsuario': emailUsuario,
                    'activo': True
                }      

                try:
                    auth.get_user(usr_id)
                    auth.update_user(
                        usr_id,
                        email=emailUsuario
                    )

                    usuario_ref.update(nuevo_usuario_tabla)
                    descripcion = f'Se editó un nuevo usuario con la id: {usr_id}'
                    agregarHistorial(request.session.get('id'), descripcion, 'Editar Usuario')
                    messages.success(request, 'Usuario editado de manera correcta')
                except Exception as e:
                    messages.error(request, f'Error al editar el usuario: {str(e)}')
        else:
            messages.error(request, 'Usuario no encontrado')

        return render(request, 'VentaseInventario/editarUsuario.html', {'usuario': usuario})
    elif request.session.get('sesion') == True:
        return redirect('dashboard')
    else:
        return render(request, 'VentaseInventario/login.html')

def eliminar_usuario(request, usuario_id):
    if request.session.get('sesion') == True:
        try:
            db = firestore.client()
            db.collection('users').document(usuario_id).update({'activo': False})
            auth.delete_user(usuario_id)
            descripcion = f'Se eliminó un usuario con la id: {usuario_id}'
            agregarHistorial(request.session.get('id'), descripcion,'Eliminación usuario')
            return redirect('usuario')
        except Exception as e:
            return HttpResponse(f'Error al eliminar el usuario {str(e)}')
    else:
        return render(request, 'VentaseInventario/login.html')   



#HISTORIAL
def historial(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        historial = db.collection('Historial').stream()
        list_values_historial = []
        for doc in historial:
            hist = doc.to_dict()
            list_values_historial.append(hist)
        list_values_historial = sorted(list_values_historial, key=lambda x: datetime.strptime(x['fecha'], '%Y-%m-%d %H:%M:%S'))
        list_values_historial.reverse()
        return render(request, 'VentaseInventario/historial.html', {'role': request.session.get('role'), 'historial': list_values_historial})
    else:
        return render(request, 'VentaseInventario/login.html')
    
def agregarHistorial(id_usuario, descripcion, tipoModificacion):
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # Ultima key inventario
    db = firestore.client()
    lista_historial = db.collection('Historial').stream() 
    lista_keys_historial = []
    try:
        for doc in lista_historial:
            lista_keys_historial.append(int(doc.id))                         

        lista_keys_historial = sorted(lista_keys_historial)

        lista_keys_historial_int = lista_keys_historial[-1] + 1
        lista_keys_historial_str = str(lista_keys_historial_int)
    except:
        lista_keys_historial_str = '2'
    # Fin ultima key  

    nuevo_hist = {
        'fecha': timestamp_str,
        'descripcion': descripcion,
        'idUsuario': id_usuario,
        'tipoModificacion': tipoModificacion
    }

    db.collection('Historial').document(lista_keys_historial_str).set(nuevo_hist)
 


# ANALISIS
def analisis(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        analisis_ref = db.collection('Analisis').stream()
        list_values_analisis = []
        for doc in analisis_ref:
            try:
                item = doc.to_dict()
                item.update({'id': doc.id})
                item['idUsuario'] = db.collection('users').document(item['idUsuario']).get().to_dict()['nombreUsuario']
                list_values_analisis.append(item)
            except:
                c = 1

        return render(request, 'VentaseInventario/analisis.html', {'role': request.session.get('role'), 'analisis': list_values_analisis})
    else:
        return render(request, 'VentaseInventario/login.html')    
    
def agregarAnalisis(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        tabla_ventas = 'Ventas'
        tabla_inventario = 'Inventario'
        keys_venta = ['estado', 'fechaInicio', 'fechaFin', 'idUsuario', 'rutCliente', 'tipoPago', 'total']
        keys_inventario = ['nombreProducto', 'cantidadEsperada', 'precioUnitario', 'cantidadActual', 'rutProveedor', 'idUsuario']

        opciones = [
            {'grafico': 'Linea'},
            {'grafico': 'Barras'},
            {'grafico': 'Histograma'},
            {'grafico': 'Puntos'}
        ]

        tablas = [[tabla_inventario,tabla_ventas],list(keys_inventario),list(keys_venta)]
        tablas_json = json.dumps(tablas)
        img_path= None

        if request.method == "POST":
            tipoGrafico = request.POST.get('tipo_grafico')
            tabla = request.POST.get('tabla')
            color_x = request.POST.get('color_x', 'red')
            color_y = request.POST.get('color_y', 'blue')
            variablex = request.POST.get('variablex')
            variabley = request.POST.get('variabley')
            titulo = request.POST.get('titulo')
            labelX = request.POST.get('label_x')
            labelY = request.POST.get('label_y')

            analisis_ref = db.collection('Analisis').stream()
            lista_id_analisis = [doc.id for doc in analisis_ref]
            ultima_id = str(int(max(lista_id_analisis, key=lambda doc_id: int(doc_id)))+1)
            if ultima_id == None:
                ultima_id = 1

            img_path = create_graph(db, tabla, variablex, variabley, titulo, labelX, labelY, ultima_id, tipoGrafico, color_x=color_x, color_y=color_y)

            nuevo_analisis = {
                'tipoGrafico': tipoGrafico,
                'tabla': tabla,
                'titulo': titulo,
                'variableX': variablex,
                'variableY': variabley,
                'labelX': labelX,
                'labelY': labelY,
                'imgAnalisis': img_path,
                'idUsuario': request.session.get('id')
            }

            try:
                almacenar_inventario = db.collection('Analisis').document(ultima_id)
                almacenar_inventario.set(nuevo_analisis)
                descripcion = f'Se agregó un nuevo análisis con la id: {ultima_id}'
                agregarHistorial(request.session.get('id'), descripcion, 'Agregar Analisis')
                messages.success(request, 'Análisis generado de manera correcta')
                return render(request, 'VentaseInventario/agregarAnalisis.html', {'opciones_graficos': opciones, 'tablas': tablas, 'tablas_json': tablas_json, 'analisis': nuevo_analisis})
            except:
                messages.error(request, 'El análisis no se logró realizar con exito, inténtelo nuevamente')

        return render(request, 'VentaseInventario/agregarAnalisis.html', {'opciones_graficos': opciones, 'tablas': tablas, 'tablas_json': tablas_json, 'imgGrafico': img_path})
    else:
        return render(request, 'VentaseInventario/login.html')

def modificarAnalisis(request):
    if request.session.get('sesion') == True:
        db = firestore.client()
        analisis_ref = db.collection('Analisis').stream()
        analisis = []

        for doc in analisis_ref:
            try:
                item = doc.to_dict()
                item['id'] = doc.id
                item['idUsuario'] = db.collection('users').document(item['idUsuario']).get().to_dict()['nombreUsuario']
                analisis.append(item)
            except:
                c = 1

        return render(request, 'VentaseInventario/modificarAnalisis.html', {'analisis': analisis})
    else:
        return render(request, 'VentaseInventario/login.html')
    
def editarAnalisis(request):
    if request.session.get('sesion') == True:
        analisis_id = request.GET.get('analisis_id') 
        db = firestore.client()
        analisis_ref = db.collection('Analisis').document(analisis_id)
        analisis = analisis_ref.get().to_dict()
        analisis['id'] = analisis_id

        # Elementos dropdowns
        tabla_ventas = 'Ventas'
        tabla_inventario = 'Inventario'
        keys_venta = ['estado', 'fechaInicio', 'fechaFin', 'idUsuario', 'rutCliente', 'tipoPago', 'total']
        keys_inventario = ['nombreProducto', 'descripcion', 'cantidadEsperada', 'precioUnitario', 'cantidadActual', 'rutProveedor', 'idUsuario']

        opciones = [
            {'grafico': 'Linea'},
            {'grafico': 'Barras'},
            {'grafico': 'Histograma'},
            {'grafico': 'Puntos'}
        ]

        tablas = [[tabla_inventario,tabla_ventas],list(keys_inventario),list(keys_venta)]
        tablas_json = json.dumps(tablas)
        img_path= None

        if request.method == "POST":
            try:
                tipoGrafico = request.POST.get('tipo_grafico')
                tabla = request.POST.get('tabla')
                variablex = request.POST.get('variablex')
                variabley = request.POST.get('variabley')
                titulo = request.POST.get('titulo')
                labelX = request.POST.get('label_x') #No es necesario guardar en base de datos
                labelY = request.POST.get('label_y') #No es necesario guardar en base de datos

                img_path = create_graph(db, tabla, variablex, variabley, titulo, labelX, labelY, analisis['id'], tipoGrafico)

                nuevos_datos_analisis = {
                    'tipoGrafico': tipoGrafico,
                    'tabla': tabla,
                    'titulo': titulo,
                    'variableX': variablex,
                    'variableY': variabley,
                    'imgAnalisis': img_path,
                    'idUsuario': request.session.get('id')
                }
                analisis_ref.update(nuevos_datos_analisis)
                descripcion = f'Se editó un nuevo análisis con la id: {analisis_id}'
                agregarHistorial(request.session.get('id'), descripcion, 'Editar Análisis')
                messages.success(request, 'Análisis editada exitosamente')
                return redirect('')
            except Exception as e:
                messages.error(request, f'Error al editar el análisis: {str(e)}')

        return render(request, 'VentaseInventario/editarAnalisis.html', {'analisis': analisis, 'tablas': tablas, 'tablas_json': tablas_json, 'opciones_graficos': opciones})
    else:
        return render(request, 'VentaseInventario/login.html')

def eliminar_analisis(request, analisis_id):
    if request.session.get('sesion') == True:
        try:
            db = firestore.client()
            img_path = f'VentaseInventario/static/img/graficos/{analisis_id}.png'
            if os.path.exists(img_path):
                os.remove(img_path)
            db.collection('Analisis').document(analisis_id).delete()
            descripcion = f'Se eliminó un análisis con la id: {analisis_id}'
            agregarHistorial(request.session.get('id'), descripcion, 'Eliminación Análisis')
            return redirect('modificarAnalisis')

        except Exception as e:
            return HttpResponse(f'Error al eliminar el análisis: {str(e)}')

    else:
        return render(request, 'VentaseInventario/login.html')

def create_graph(db, tabla, x, y, title, label_x, label_y, id_grafico, tipo_grafico='line', color_x='blue', color_y='green'):
    tabla_ref = db.collection(tabla).stream()
    x_lista = []
    y_lista = []

    for doc in tabla_ref:
        try:
            x_value = doc.to_dict()[x]
            y_value = doc.to_dict()[y]

            x_lista.append(x_value)
            y_lista.append(y_value)
        except KeyError:
            pass

    if tipo_grafico == 'bar':
        # Gráfico de barras para datos categóricos
        plt.bar(range(len(x_lista)), y_lista, color=color_y, label=f'{y} data')
        plt.xticks(range(len(x_lista)), x_lista, rotation=45, ha='right')  # Etiquetas del eje x
    elif tipo_grafico == 'Linea':
        plt.plot(x_lista, y_lista, color=color_x, label=f'{x} data', linewidth=2)
    elif tipo_grafico == 'Barras':
        plt.bar(x_lista, y_lista, color=color_y, label=f'{y} data')
    elif tipo_grafico == 'Histograma':
        plt.hist(y_lista)
    elif tipo_grafico == 'Puntos':
        plt.scatter(x_lista, y_lista, color=color_x, label=f'{x} vs {y}')
    else:
        return HttpResponse("Tipo de gráfico inválido. Solo se permiten gráficos de linea, barras, histogramas y puntos.")

    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)

    img_path = f'VentaseInventario/static/img/graficos/{id_grafico}.png'
    mostrar_img = f'img/graficos/{id_grafico}.png'

    plt.tight_layout()  # Asegura que las etiquetas no se superpongan
    plt.savefig(img_path)
    plt.close()

    return mostrar_img



# restablecer contraseña
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = auth.get_user_by_email(email)
            link= auth.generate_password_reset_link(email)

            subject = "Recuperar contraseña"
            message = f'Enlace de restablecimiento de contraseña: {link}'
            recipient_list = [email]

            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

            messages.success(request,f'Se ha enviado un enlace de restablecimiento de contraseña a {email}')

        except auth.UserNotFoundError:
            messages.error(request,f'No hay ningún usuario registrado con el correo electrónico {email}')

        return redirect('login')
    return render(request,'login')


def index(request):
    return render(request,'VentaseInventario/index.html')

def servicios(request):
    return render(request,'VentaseInventario/servicios.html')

def experienciayclientes(request):
    return render(request,'VentaseInventario/experienciayclientes.html')
def contacto(request):
    return render(request,'VentaseInventario/contacto.html')