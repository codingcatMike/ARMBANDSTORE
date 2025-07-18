import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
import requests

from .models import *
from .forms import ProductForm


def home(request):
    products = Product.objects.filter(available=True)
    return render(request, "home.html", {"products": products})


@login_required
@require_POST
def send_purchase_request(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        product_id = data.get("product_id")
        color1 = data.get("color1")
        color2 = data.get("color2")

        if not product_id or not color1 or not color2:
            return JsonResponse({"status": "error", "message": "Produkt-ID und Farben müssen angegeben werden"}, status=400)

        product = Product.objects.filter(id=product_id, available=True).first()
        if not product:
            return JsonResponse({"status": "error", "message": "Produkt nicht gefunden"}, status=404)

        user = request.user
        if not user.email:
            return JsonResponse({"status": "error", "message": "Benutzer hat keine E-Mail-Adresse"}, status=400)

        if PurchaseRequest.objects.filter(product=product, buyer=user).exists():
            return JsonResponse({"status": "error", "message": "Kaufanfrage existiert bereits."}, status=400)

        # Create purchase request with colors
        pr = PurchaseRequest.objects.create(product=product, buyer=user, color1=color1, color2=color2)
        pr.save()
      

        # Send email notification to shop owner
        subject = f"Kaufanfrage für {product.name}"
        message = (
            f"Es wurde eine Kaufanfrage für '{product.name}' gesendet.\n\n"
            f"Käufer: {user.username}\n"
            f"E-Mail: {user.email}\n"
            f"Farben: {color1}, {color2}\n"
        )
        from_email = None  # Uses DEFAULT_FROM_EMAIL in settings.py
        to_email = ["system@webdevode.de"]

        send_mail(subject, message, from_email, to_email)

        return JsonResponse({"status": "success"})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Ungültiges JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def shop_1(request):
    products = Product.objects.filter(available=True)
    return render(request, "shop_1.html", {"products": products})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registrierung erfolgreich! Du kannst dich jetzt einloggen.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@staff_member_required
def manager_view(request):
    products = Product.objects.all()
    purchase_requests = PurchaseRequest.objects.select_related('product', 'buyer').all()
    products_to_make = ProductToMake.objects.select_related('product', 'buyer').all().order_by('status', 'id')

    if request.method == "POST" and 'add_product' in request.POST:
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manager')
    else:
        form = ProductForm()

    context = {
        "products": products,
        "purchase_requests": purchase_requests,
        "products_to_make": products_to_make,
        "form": form,
    }
    return render(request, "manager.html", context)



def send_email_via_api(to, message):
    api_url = "https://api-3elg.onrender.com/send_email"
    headers = {"X-API-KEY": "your_api_key_here"}  # Omit or set if needed
    payload = {"to": to, "message": message}
    try:
        res = requests.post(api_url, json=payload, headers=headers)
        res.raise_for_status()
    except Exception as e:
        print("Email API error:", e)

@staff_member_required
def accept_request(request, request_id):
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    ProductToMake.objects.create(
        product=purchase_request.product,
        buyer=purchase_request.buyer,
        color1=purchase_request.color1 or "",
        color2=purchase_request.color2 or ""
    )

    msg = (
        f"Hallo {purchase_request.buyer.username},\n\n"
        f"wir freuen uns, Ihnen mitzuteilen, dass Ihre Kaufanfrage für das Produkt '{purchase_request.product.name}' akzeptiert wurde.\n"
        "Unser Team wird sich in Kürze mit weiteren Informationen bei Ihnen melden.\n\n"
        "Sollten Sie Fragen haben, antworten Sie einfach auf diese E-Mail.\n\n"
        "Vielen Dank für Ihr Interesse!\n"
        "Ihr Kundenservice-Team"
    )

    send_email_via_api(purchase_request.buyer.email, msg)
    purchase_request.delete()
    return redirect('manager')


@staff_member_required
def reject_request(request, request_id):
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)

    msg = (
        f"Hallo {purchase_request.buyer.username},\n\n"
        f"leider müssen wir Ihnen mitteilen, dass Ihre Kaufanfrage für das Produkt '{purchase_request.product.name}' nicht erfüllt werden kann.\n"
        "Wir bitten um Ihr Verständnis.\n\n"
        "Falls Sie Fragen haben oder weitere Produkte interessieren, stehen wir Ihnen gerne zur Verfügung.\n\n"
        "Vielen Dank für Ihr Interesse!\n"
        "Ihr Kundenservice-Team"
    )

    send_email_via_api(purchase_request.buyer.email, msg)
    purchase_request.delete()
    return redirect('manager')


@staff_member_required
@require_POST
def product_finished(request, product_to_make_id):
    product_to_make = get_object_or_404(ProductToMake, id=product_to_make_id)

    if product_to_make.status != 'in_progress':
        return redirect('manager')

    product_to_make.status = 'finished'
    product_to_make.save()

    msg = (
        f"Hallo {product_to_make.buyer.username},\n\n"
        f"Ihr bestelltes Produkt '{product_to_make.product.name}' "
        f"mit den Farben {product_to_make.color1} und {product_to_make.color2} "
        "ist nun fertig und kann abgeholt werden.\n\n"
        "Viele Grüße,\nIhr Armband Boutique Team"
    )

    send_email_via_api(product_to_make.buyer.email, msg)
    return redirect('manager')


@staff_member_required
@require_POST
def product_picked_up(request, product_to_make_id):
    product_to_make = get_object_or_404(ProductToMake, id=product_to_make_id)
    product_to_make.delete()
    return redirect('manager')

def send_email_via_api(to, message):
    api_url = "https://api-3elg.onrender.com/send_email"
    headers = {"X-API-KEY": "TEST"}  # Remove if not needed
    payload = {"to": to, "message": message}
    try:
        res = requests.post(api_url, json=payload, headers=headers)
        res.raise_for_status()
    except Exception as e:
        print("Failed to send email:", e)