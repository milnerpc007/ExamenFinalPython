from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import datosUsuario, tareasInformacion, comentarioTarea
import datetime
import json

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Create your views here.
def index(request):
    if request.method == 'POST':
        nombreUsuario = request.POST.get('nombreUsuario')
        contraUsuario = request.POST.get('contraUsuario')
        usuarioInfo = authenticate(request,username=nombreUsuario,password=contraUsuario)
        if usuarioInfo is not None:
            login(request,usuarioInfo)
            if usuarioInfo.datosusuario.tipoUsuario == 'ADMINISTRADOR':
                return HttpResponseRedirect(reverse('django_tareas:consolaAdministrador'))
            else:
                return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':usuarioInfo.id}))
        else:
            return HttpResponseRedirect(reverse('django_tareas:index'))
    return render(request,'ingresoUsuario.html')

@login_required(login_url='/')
def cerrarSesion(request):
    logout(request)
    return HttpResponseRedirect(reverse('django_tareas:index'))

@login_required(login_url='/')
def consolaAdministrador(request):
    if request.user.datosusuario.tipoUsuario == 'ADMINISTRADOR':
        if request.method == 'POST':
            usernameUsuario = request.POST.get('usernameUsuario')
            contraUsuario = request.POST.get('contraUsuario')
            nombreUsuario = request.POST.get('nombreUsuario')
            apellidoUsuario = request.POST.get('apellidoUsuario')
            tipoUsuario = request.POST.get('tipoUsuario')
            nroCelular = request.POST.get('nroCelular')
            profesionUsuario = request.POST.get('profesionUsuario')
            perfilUsuario = request.POST.get('perfilUsuario')
            emailUsuario = request.POST.get('emailUsuario')
            usuarioNuevo = User.objects.create(
                username=usernameUsuario,
                email=emailUsuario,
            )
            usuarioNuevo.set_password(contraUsuario)
            usuarioNuevo.first_name = nombreUsuario
            usuarioNuevo.last_name = apellidoUsuario
            usuarioNuevo.is_staff = True
            usuarioNuevo.save()
            datosUsuario.objects.create(
                user=usuarioNuevo,
                tipoUsuario = tipoUsuario,
                nroCelular = nroCelular,
                profesionUsuario=profesionUsuario,
                perfilUsuario = perfilUsuario
            )
            return HttpResponseRedirect(reverse('django_tareas:consolaAdministrador'))
        return render(request,'consolaAdministrador.html',{
            'usuariosTotales':User.objects.all().order_by('id')
        })
    else:
        return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':request.user.id}))

def eliminarUsuario(request,ind):
    usuarioEliminar = User.objects.get(id=ind)
    datosUsuario.objects.get(user=usuarioEliminar).delete()
    usuarioEliminar.delete()
    return HttpResponseRedirect(reverse('django_tareas:consolaAdministrador'))

@login_required(login_url='/')
def verUsuario(request, ind):
    usuarioInformacion = User.objects.get(id=ind)
    tareasUsuario = tareasInformacion.objects.filter(usuarioRelacionado=usuarioInformacion).order_by('id')
    return render(request,'informacionUsuario.html',{
        'usuarioInfo': usuarioInformacion,
        'tareasUsuario': tareasUsuario
    })

def nuevaTarea(request, ind):
    if request.method == 'POST':
        usuarioRelacionado = User.objects.get(id=ind)
        fechaInicio = request.POST.get('fechaInicio')
        fechaFin = request.POST.get('fechaFin')
        descripcionTarea = request.POST.get('descripcionTarea')
        fechaSeparada = fechaInicio.split('-')
        ini_dia = int(fechaSeparada[2])
        ini_mes = int(fechaSeparada[1])
        ini_anho = int(fechaSeparada[0])
        fechaSeparada = fechaFin.split('-')
        fin_dia = int(fechaSeparada[2])
        fin_mes = int(fechaSeparada[1])
        fin_anho = int(fechaSeparada[0])
        fechaInicioRegistro = datetime.datetime(ini_anho, ini_mes, ini_dia)
        fechaFinRegistro = datetime.datetime(fin_anho, fin_mes, fin_dia)
        tareasInformacion.objects.create(
            fechaInicio=fechaInicioRegistro,
            fechaFin=fechaFinRegistro,
            descripcionTarea=descripcionTarea,
            usuarioRelacionado=usuarioRelacionado,
        )
        return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':ind}))

def devolverMensaje(request):
    print(request.GET)
    nombre = request.GET.get('nombre')
    apellido = request.GET.get('apellido')
    edad = request.GET.get('edad')
    profesion = request.GET.get('profesion')
    print(nombre)
    print(apellido)
    print(edad)
    print(profesion)
    return JsonResponse({
        "nombre":nombre,
        "edad":edad,
        "apellido":apellido,
        "profesion":profesion,
        "funcion":"devolverMensaje",
        "fechaEjecuacion":"2023-04-14",
    })

def conseguirInfoTarea(request):
    comentariosTotales = []
    idTarea = request.GET.get('idTarea')
    tareaSeleccionada = tareasInformacion.objects.get(id=idTarea)
    comentariosTarea = tareaSeleccionada.comentariotarea_set.all()
    for comentario in comentariosTarea:
        comentariosTotales.append([str(comentario.usuarioRelacionado.first_name + ' ' + comentario.usuarioRelacionado.last_name),comentario.comentarioTarea])
    print(comentariosTotales)
    return JsonResponse({
        'descripcionTarea':tareaSeleccionada.descripcionTarea,
        'estadoTarea':tareaSeleccionada.estadoTarea,
        'fechaInicio':tareaSeleccionada.fechaInicio.strftime("%d-%m-%Y"),
        'fechaFin':tareaSeleccionada.fechaFin.strftime("%d-%m-%Y"),
        'idTarea':str(tareaSeleccionada.id),
        'comentariosTotales':comentariosTotales,
    })

def eliminarTarea(request,idTarea,idUsuario):
    tareasInformacion.objects.get(id=idTarea).delete()
    return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':idUsuario}))

def descargarTareas(request,idUsuario):
    usuarioInformacion = User.objects.get(id=idUsuario)
    tareasUsuario = tareasInformacion.objects.filter(usuarioRelacionado=usuarioInformacion).order_by('id')
    nombreArchivo = 'tareas-' + f'{usuarioInformacion.username}' + '.pdf'

    archivoPdf = canvas.Canvas(nombreArchivo,A4)

    archivoPdf.drawImage('./django_tareas/static/logoApp.png',20, 700, width=140, height=80)
    archivoPdf.drawImage('./django_tareas/static/logoPUCP.png',430, 700, width=140, height=80)
    
    archivoPdf.setFont('Helvetica-Bold',25)
    archivoPdf.drawCentredString(297.5,730,'Reporte de tareas')

    ###### Informacion del usuario #########
    archivoPdf.setFont('Helvetica-Bold',12)
    archivoPdf.drawString(40,620, 'Nombre de usuario')
    archivoPdf.drawString(40,605, 'Primer nombre')
    archivoPdf.drawString(40,590, 'Apellido')
    archivoPdf.drawString(40,575, 'Email')

    archivoPdf.drawString(155,620, ':')
    archivoPdf.drawString(155,605, ':')
    archivoPdf.drawString(155,590, ':')
    archivoPdf.drawString(155,575, ':')

    archivoPdf.setFont('Helvetica',12)
    archivoPdf.drawString(160,620, f'{usuarioInformacion.username}')
    archivoPdf.drawString(160,605, f'{usuarioInformacion.first_name}')
    archivoPdf.drawString(160,590, f'{usuarioInformacion.last_name}')
    archivoPdf.drawString(160,575, f'{usuarioInformacion.email}')

    archivoPdf.setFont('Helvetica-Bold',12)
    archivoPdf.drawString(300,620, 'Tipo de usuario')
    archivoPdf.drawString(300,605, 'Profesion del usuario')
    archivoPdf.drawString(300,590, 'Nro de celular')
    archivoPdf.drawString(300,575, 'Fecha de ingreso')

    archivoPdf.drawString(425,620, ':')
    archivoPdf.drawString(425,605, ':')
    archivoPdf.drawString(425,590, ':')
    archivoPdf.drawString(425,575, ':')

    archivoPdf.setFont('Helvetica',12)
    archivoPdf.drawString(430,620, f'{usuarioInformacion.datosusuario.tipoUsuario}')
    archivoPdf.drawString(430,605, f'{usuarioInformacion.datosusuario.profesionUsuario}')
    archivoPdf.drawString(430,590, f'{usuarioInformacion.datosusuario.nroCelular}')
    archivoPdf.drawString(430,575, f'{usuarioInformacion.datosusuario.fechaIngreso.strftime("%d-%m-%Y")}')

    archivoPdf.setFont('Helvetica-Bold',10)
    archivoPdf.drawString(55,545, 'Fecha de Inicio')
    archivoPdf.drawString(160,545, 'Fecha de Fin')
    archivoPdf.drawString(270,545, 'Estado')
    archivoPdf.drawString(380,545, 'Descripcion')

    lista_x = [40,550]
    lista_y = [500,540]
    archivoPdf.setStrokeColorRGB(255, 255, 255)

    for tarea in tareasUsuario:
        archivoPdf.grid(lista_x,lista_y)
        archivoPdf.setFont('Helvetica',12)
        archivoPdf.drawString(lista_x[0] + 20, lista_y[1]-15, f'{tarea.fechaInicio}')
        archivoPdf.drawString(lista_x[0] + 120, lista_y[1]-15, f'{tarea.fechaFin}')
        archivoPdf.drawString(lista_x[0] + 220, lista_y[1]-15, f'{tarea.estadoTarea}')
        archivoPdf.drawString(lista_x[0] + 300, lista_y[1]-15, f'{tarea.descripcionTarea}')
        lista_y[0] = lista_y[0] - 30
        lista_y[1] = lista_y[1] - 30
    archivoPdf.save()

    archivoTareas = open(nombreArchivo,'rb')
    return FileResponse(archivoTareas,as_attachment=True)

def react(request):
    return render(request,'react.html')

def iterarReact(request):
    return render(request,'iterarReact.html')


def publicarComentario(request):
    datos = json.load(request)
    idTarea = datos.get('idTarea')
    comentario = datos.get('comentario')
    usuarioRelacionado = request.user
    tareaRelacionada = tareasInformacion.objects.get(id=idTarea)
    comentarioTarea(
        usuarioRelacionado=usuarioRelacionado,
        tareaRelacionada=tareaRelacionada,
        comentarioTarea=comentario
    ).save()
    return JsonResponse({
        'resp':'ok'
    })

#####################################
###########  PREGUNTA 1  ############
#####################################
def descargarReporteUsuarios(request):
       
    usuarioInformacion = User.objects.all()
    nombreArchivo = 'reporteUsuarios.pdf'

    archivoPdf = canvas.Canvas(nombreArchivo,A4)

    ##########################################
    ###############  CABECERA  ###############
    ##########################################
    archivoPdf.drawImage('./django_tareas/static/logoApp.png',20, 700, width=140, height=80)
    archivoPdf.drawImage('./django_tareas/static/logoPUCP.png',430, 700, width=140, height=80)
    
    archivoPdf.setFont('Helvetica-Bold',25)
    archivoPdf.drawCentredString(297.5,730,'Reporte de usuarios')

    archivoPdf.setFont('Helvetica-Bold',12)
    archivoPdf.drawString(40,620, 'Fecha de reporte')
    archivoPdf.drawString(40,605, 'Cantidad usuarios')
    archivoPdf.drawString(40,590, 'Nombre de usuario')
    archivoPdf.drawString(40,575, 'Tipo de usuario')
    
    archivoPdf.drawString(155,620, ':')
    archivoPdf.drawString(155,605, ':')
    archivoPdf.drawString(155,590, ':')
    archivoPdf.drawString(155,575, ':')

    archivoPdf.setFont('Helvetica',12)
    archivoPdf.drawString(160,620, f'{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    archivoPdf.drawString(160,605, f'{usuarioInformacion.count()}')
    archivoPdf.drawString(160,590, f'{request.user.username}')
    archivoPdf.drawString(160,575, f'{request.user.datosusuario.tipoUsuario}')
    
    ##########################################
    ########  INFORMACION DE USUARIOS  #######
    ##########################################
    archivoPdf.setFont('Helvetica-Bold',10)
    archivoPdf.drawString(50,545, 'Nombre')
    archivoPdf.drawString(130,545, 'Apellido')
    archivoPdf.drawString(210,545, 'Username')
    archivoPdf.drawString(275,545, 'Fec Ingreso')
    archivoPdf.drawString(360,545, 'Celular')
    archivoPdf.drawString(425,545, 'Tareas')
    archivoPdf.drawString(470,545, 'Tipo Usuario')

    lista_x = [40,550]
    lista_y = [500,530]
    archivoPdf.setStrokeColorRGB(255, 255, 255)

    #for tarea in tareasUsuario:
    for usuario in usuarioInformacion:
        archivoPdf.grid(lista_x,lista_y)
        archivoPdf.setFont('Helvetica',9)
        fecha_ingreso = usuario.last_login
        if fecha_ingreso != None:
            fecha_ingreso = usuario.last_login.strftime("%d/%m/%Y")

        archivoPdf.drawString(lista_x[0] + 10, lista_y[1]-15, f'{usuario.first_name}')
        archivoPdf.drawString(lista_x[0] + 90, lista_y[1]-15, f'{usuario.last_name}')
        archivoPdf.drawString(lista_x[0] + 170, lista_y[1]-15, f'{usuario.username}')
        archivoPdf.drawString(lista_x[0] + 238, lista_y[1]-15, f'{usuario.datosusuario.fechaIngreso}')
        archivoPdf.drawString(lista_x[0] + 320, lista_y[1]-15, f'{usuario.datosusuario.nroCelular}')
        archivoPdf.drawString(lista_x[0] + 400, lista_y[1]-15, f'{tareasInformacion.objects.filter(usuarioRelacionado=usuario).count()}')
        archivoPdf.drawString(lista_x[0] + 430, lista_y[1]-15, f'{usuario.datosusuario.tipoUsuario}')
        lista_y[0] = lista_y[0] - 20
        lista_y[1] = lista_y[1] - 20
    archivoPdf.save()

    reporteUsuarios = open(nombreArchivo,'rb')
    return FileResponse(reporteUsuarios,as_attachment=True)

def conseguirInfoUsuario(request):
    idUsuario = request.GET.get('idUsuario')
    usuarioSeleccionado = datosUsuario.objects.get(id=idUsuario)
    return JsonResponse({
        'nombreUsuario':usuarioSeleccionado.user.first_name,
        'apellidoUsuario':usuarioSeleccionado.user.last_name,
        'tipoUsuario':usuarioSeleccionado.tipoUsuario,
        'emailUsuario':usuarioSeleccionado.user.email,
        'profesionUsuario':usuarioSeleccionado.profesionUsuario,
        'nroCelular':usuarioSeleccionado.nroCelular,
        'idUsuario':str(usuarioSeleccionado.id),
    })

def actualizarInfoUsuario(request):
    datos = json.load(request)
    idUsuariox = datos.get('idUsuario')
    nroCelularx = datos.get('nroCelular')
    profesionUsuariox = datos.get('profesionUsuario')
    print('Prueba' + nroCelularx)
    
    usuarioSeleccionado = datosUsuario.objects.get(id=idUsuariox)
    
    usuarioSeleccionado.nroCelular = nroCelularx
    usuarioSeleccionado.profesionUsuario = profesionUsuariox
    usuarioSeleccionado.save()

    
    return JsonResponse({
        'resp':'ok'
    })

def actualizarEstadoTarea(request):
    datos = json.load(request)
    idTareax = datos.get('idTarea')
    tareaSeleccionado = tareasInformacion.objects.get(id=idTareax)
    tareaSeleccionado.estadoTarea = "FINALIZADO"
    tareaSeleccionado.save()
   
    return JsonResponse({
        'resp':'ok'
    })

