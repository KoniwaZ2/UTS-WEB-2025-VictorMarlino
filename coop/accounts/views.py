from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import User, Mahasiswa
from .forms import CustomLoginForm
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.db.utils import IntegrityError

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = CustomLoginForm

    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        login(self.request, user)

        # Redirect berdasarkan role
        if user.role == "mahasiswa":
            return redirect(reverse("coops:mahasiswa_dashboard"))
        elif user.role == "supervisor":
            return redirect(reverse("jobs:supervisor_dashboard"))
        elif user.role == "admin":
            return redirect(reverse("coops:status_magang"))
        return redirect("/")

    def form_invalid(self, form):
        return super().form_invalid(form)
    
def register(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "register":
            email = request.POST.get("email")
            password = request.POST.get("password")
            nama_lengkap = request.POST.get("nama")

            # Prevent duplicate usernames/emails
            if User.objects.filter(username=email).exists():
                messages.error(request, "Email sudah terdaftar. Silakan gunakan email lain atau login.")
                return render(request, "accounts/register.html")

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        role="mahasiswa"
                    )

                    # store full name on the User record as-is
                    if nama_lengkap:
                        user.first_name = nama_lengkap.strip()
                        user.save()

                    # Create Mahasiswa record linking to the created user
                    Mahasiswa.objects.create(
                        nama=nama_lengkap,
                        nim=request.POST.get("nim"),
                        prodi=request.POST.get("prodi"),
                        angkatan=int(request.POST.get("angkatan")) if request.POST.get("angkatan") else None,
                        jenis_kelamin=request.POST.get("jenis_kelamin"),
                        email=user,
                        no_hp=request.POST.get("no_hp"),
                        konsultasi=request.POST.get("konsultasi", ""),
                        sptjm=request.POST.get("sptjm", ""),
                    )

                messages.success(request, "Registrasi berhasil! Silakan masuk.")
                return redirect("login")
            except IntegrityError:
                messages.error(request, "Terjadi kesalahan pada server saat membuat akun. Silakan coba lagi.")
                return render(request, "accounts/register.html")
        else:
            messages.error(request, "Terjadi kesalahan saat registrasi. Silakan coba lagi.")
    return render(request, "accounts/register.html")
