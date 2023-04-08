from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from store.models import Product
from .forms import RegistrationForm, UserEditForm, UserAddressForm, UserRestoreForm
from .models import Address, Customer
from .token import account_activation_token
from django.contrib import messages


@login_required
def dashboard(request):
    return render(request, 'account/user/dashboard.html')


def account_register(request):

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        register_form = RegistrationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.email = register_form.cleaned_data['email']
            user.set_password(register_form.cleaned_data['password'])
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate your account'
            message = render_to_string('account/registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return HttpResponse('registered successfully and activation sent')

    else:
        register_form = RegistrationForm()
    return render(request, 'account/registration/register.html', {'form': register_form})


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('account:dashboard')
    else:
        return render(request, 'account/registration/activation_invalid.html')


@login_required
def edit_details(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        name_to_change = request.POST.get('first_name')
        current_user_name = Customer.objects.get(user_name=request.user.user_name)
        if user_form.is_valid():
            if Customer.objects.filter(user_name=name_to_change).count() == 0:

                user = Customer.objects.get(user_name=current_user_name)
                user.user_name = name_to_change
                user.save()
                messages.success(request, f'Your name has been changed to {name_to_change}')

            else:
                messages.error(request, f'User with name {name_to_change} already exists, try something else')

    else:
        user_form = UserEditForm(instance=request.user)

    return render(request, 'account/user/edit_details.html', {'user_form': user_form})


@login_required
def delete_user(request):
    user = Customer.objects.get(user_name=request.user.user_name)
    user.is_active = False
    user.save()
    logout(request)
    return redirect('account:delete_confirmation')


def enable_user(request):
    if request.method == 'POST':
        form = UserRestoreForm(request.POST)
        email = request.POST.get('email')
        try:
            user = Customer.objects.get(email=email)
            current_site = get_current_site(request)
            subject = 'Activate your account'
            message = render_to_string('account/registration/account_restore_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return HttpResponse('Your need to check your email in order to confirm restoring the account')
        except:
            user = None
            error = f'User with {email} does not exist'
            messages.error(request, f'User with {email} does not exist')

        if user:
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('account:dashboard')

    else:
        form = UserRestoreForm()
    return render(request, 'account/user/restore_account.html', {'user_form': form})


@login_required
def view_address(request):
    addresses = Address.objects.filter(customer=request.user)
    return render(request, "account/user/addresses.html", {"addresses": addresses})


@login_required
def add_address(request):
    if request.method == "POST":
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.customer = request.user
            address_form.save()
            return HttpResponseRedirect(reverse("account:addresses"))
    else:
        address_form = UserAddressForm()
    return render(request, "account/user/edit_addresses.html", {"form": address_form})


@login_required
def edit_address(request, id):
    if request.method == "POST":
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse("account:addresses"))
    else:
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address)
    return render(request, "account/user/edit_addresses.html", {"form": address_form})


@login_required
def delete_address(request, id):
    address = Address.objects.filter(pk=id, customer=request.user).delete()
    return redirect("account:addresses")


@login_required
def set_default(request, id):
    Address.objects.filter(customer=request.user, default=True).update(default=False)
    Address.objects.filter(pk=id, customer=request.user).update(default=True)
    return redirect("account:addresses")


@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
        messages.success(request, f'{product.title} has been removed from your WishList')
    else:
        product.users_wishlist.add(request.user)
        messages.success(request, f'Added {product.title} to your WishList')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def wishlist(request):
    products = Product.objects.filter(users_wishlist=request.user)
    return render(request, 'account/user/user_wishlist.html', {'wishlist': products})