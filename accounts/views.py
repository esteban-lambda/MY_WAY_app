from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q, Count, Sum
from .models import Account
from .forms import UserRegistrationForm
from contacts.models import Contact
from deals.models import Deal

def register_view(request):
    """Vista de registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Autenticar y hacer login automático
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.get_full_name()}! Tu cuenta ha sido creada exitosamente.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def accounts_list(request):
    """Lista de todas las empresas con búsqueda"""
    query = request.GET.get('q', '')
    
    accounts = Account.objects.annotate(
        contacts_count=Count('contacts'),
        deals_count=Count('deals'),
        deals_value=Sum('deals__value')
    )
    
    if query:
        accounts = accounts.filter(
            Q(name__icontains=query) |
            Q(industry__icontains=query) |
            Q(website__icontains=query)
        )
    
    accounts = accounts.order_by('-created_at')
    
    context = {
        'accounts': accounts,
        'query': query,
    }
    return render(request, 'accounts/accounts_list.html', context)

@login_required
def account_detail(request, account_id):
    """Detalle de una empresa con sus contactos y deals"""
    account = get_object_or_404(Account, id=account_id)
    
    contacts = Contact.objects.filter(account=account).order_by('first_name')
    deals = Deal.objects.filter(account=account).select_related('contact', 'assigned_to').order_by('-created_at')
    
    # Estadísticas del account
    total_deals = deals.count()
    won_deals = deals.filter(stage='closed_won').count()
    total_value = deals.aggregate(Sum('value'))['value__sum'] or 0
    won_value = deals.filter(stage='closed_won').aggregate(Sum('value'))['value__sum'] or 0
    
    context = {
        'account': account,
        'contacts': contacts,
        'deals': deals,
        'total_deals': total_deals,
        'won_deals': won_deals,
        'total_value': total_value,
        'won_value': won_value,
    }
    return render(request, 'accounts/account_detail.html', context)
