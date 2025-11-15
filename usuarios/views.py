from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegistroForm, LoginForm, UsuarioChangeForm
from django.contrib.auth import get_user_model
from propiedades.models import Propiedad
from pqr.models import PQR

Usuario = get_user_model()

# 🌐 Vista principal del sitio (landing page)
def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html', {
            'usuario': request.user,
            'rol': request.user.rol
        })
    return render(request, 'index.html')

# 📝 Vista para registrar un nuevo usuario (público)
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('index')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

# 🔐 Vista para iniciar sesión
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

# 🚪 Vista para cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('index')

# 👤 Vista del perfil del usuario
@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})

# 📋 Vista para listar usuarios (solo admin/staff)
@user_passes_test(lambda u: u.is_staff or u.rol == "administrador")
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

# ➕ Vista para crear usuarios (solo admin/staff)
@user_passes_test(lambda u: u.is_staff or u.rol == "administrador")
def crear_usuario(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_usuarios")
    else:
        form = RegistroForm()
    return render(request, "usuarios/crear_usuario.html", {"form": form})

# 🔍 Vista para ver y editar detalle de usuario (solo admin/staff)
@user_passes_test(lambda u: u.is_staff or u.rol == "administrador")
def detalle_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect("detalle_usuario", pk=usuario.pk)
    else:
        form = UsuarioChangeForm(instance=usuario)

    propiedades = []
    pqr_creados = []
    pqr_asignados = []

    if usuario.rol == "ciudadano":
        propiedades = Propiedad.objects.filter(usuario=usuario)
        pqr_creados = PQR.objects.filter(ciudadano=usuario)
    elif usuario.rol == "tecnico":
        pqr_asignados = PQR.objects.filter(tecnico=usuario)

    return render(request, "usuarios/detalle_usuario.html", {
        "usuario": usuario,
        "form": form,
        "propiedades": propiedades,
        "pqr_creados": pqr_creados,
        "pqr_asignados": pqr_asignados,
    })
