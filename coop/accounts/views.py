from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import User, Mahasiswa
from .forms import CustomLoginForm
from django.urls import reverse

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = CustomLoginForm

    def form_valid(self, form):
        # CustomLoginForm stores the authenticated user in cleaned_data['user']
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
            user = User.objects.create_user(
                username=request.POST.get("email"),  # Menggunakan email sebagai username
                email=request.POST.get("email"),
                password=request.POST.get("password"),
                role="mahasiswa"
            )
            
            Mahasiswa.objects.create(
                nama=user,
                nim=request.POST.get("nim"),
                prodi=request.POST.get("prodi"),
                angkatan=request.POST.get("angkatan"),
                jenis_kelamin=request.POST.get("jenis_kelamin"),
                email=request.POST.get("email"),
                no_hp=request.POST.get("no_hp"),
                konsultasi=request.POST.get("konsultasi", ""),
                sptjm=request.POST.get("sptjm", ""),
            )
            return redirect("login")
    return render(request, "accounts/register.html")
