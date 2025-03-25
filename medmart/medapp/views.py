from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
import razorpay
from django.conf import settings
from .forms import CustomAuthenticationForm, ContactForm, MedicineForm, MedUserForm
from .models import Medicine, Cart, health_Product, meduser1, Order,OrderItem 

def homepage(request):
    return render(request, 'home.html')

def contactpage(request):
    return render(request, 'contact.html')

def contact_submit_page(request):
    return render(request, 'contact_submit.html')

def privacypolicypage(request):
    return render(request, 'privacy_policy.html')

def faqpage(request):
    return render(request, 'faq.html')


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    next_page = reverse_lazy('home')

    def form_valid(self, form):
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)  
        return super().form_valid(form)


@login_required
@permission_required('auth.change_permission', raise_exception=True)
def assign_permission_to_user(request):
    try:
        User = get_user_model()
        
        med_user = get_object_or_404(User, username="Love")
        permission = get_object_or_404(Permission, codename="can_add_medicine")
        med_user.user_permissions.add(permission)
        med_user.save()

        med_user2 = get_object_or_404(User, username="Love")
        permission2 = get_object_or_404(Permission, codename="can_update_medicine")
        med_user2.user_permissions.add(permission2)
        med_user2.save()

        return HttpResponse("Permissions added successfully.")
    except Exception as e:
        return HttpResponse(f"Error while assigning permissions: {e}")


def UserCreateView(request):
    if request.method == 'POST':
        med_user_form = MedUserForm(request.POST)
        if med_user_form.is_valid():
            med_user_form.save()
            return redirect('meduser_list')
    else:
        med_user_form = MedUserForm()
    return render(request, 'user_create_form.html', {'med_user_form': med_user_form})

from django.shortcuts import render
from medapp.models import Medicine

def search_results(request):
    query = request.GET.get('query', '')
    results = Medicine.objects.filter(name__icontains=query) if query else []
    return render(request, 'search_results.html', {'results': results, 'query': query})

class MedUserList(ListView):
    model = meduser1
    template_name = "meduser_list.html"
    context_object_name = 'users'

class MedicineCreateView(CreateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'med_create_form.html'
    success_url = reverse_lazy('medicine_list')

class MedicineListView(ListView):
    model = Medicine
    template_name = 'medicine_list.html'
    context_object_name = 'medicines'

class MedicineDetailView(DetailView):
    model = Medicine
    template_name = "med_detail_view.html"

class MedicineUpdateView(UpdateView):
    model = Medicine
    template_name = "med_update_form.html"
    fields = ['name', 'price', 'company_name', 'description', 'image']
    success_url = reverse_lazy('medicine_list')

class MedicineDeleteView(DeleteView):
    model = Medicine
    template_name = "med_delete_view.html"
    success_url = reverse_lazy('medicine_list')

class ProductCreateView(CreateView):
    model = health_Product
    fields = ['product_name', 'category', 'price', 'quantity_in_stock', 'description', 'image']
    template_name = 'product_create_form.html'
    success_url = reverse_lazy('product_list')

class ProductListView(ListView):
    model = health_Product
    template_name = 'product_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = health_Product
    template_name = 'product_detail_view.html'
    context_object_name = 'product'

class ProductUpdateView(UpdateView):
    model = health_Product
    template_name = "product_update_form.html"
    fields = ['product_name', 'category', 'price', 'quantity_in_stock', 'description', 'image']
    success_url = reverse_lazy('product_list')

class ProductDeleteView(DeleteView):
    model = health_Product
    template_name = "product_delete_view.html"
    success_url = reverse_lazy('product_list')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_submit')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.utils.timezone import now
from django.urls import reverse_lazy
import razorpay
from django.conf import settings
from medapp.models import Cart, Order, OrderItem, Medicine, health_Product

class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        return render(request, 'cart.html', {'cart_items': cart_items})

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request):
        item_id = request.POST.get('item_id')
        item_type = request.POST.get('item_type') 
        quantity = int(request.POST.get('quantity', 1))

        if item_type == "medicine":
            item = get_object_or_404(Medicine, id=item_id)
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, medicine=item, product=None,
                defaults={'quantity': quantity, 'date_added': now()}
            )
        elif item_type == "health_product":
            item = get_object_or_404(health_Product, id=item_id)
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, product=item, medicine=None,
                defaults={'quantity': quantity, 'date_added': now()}
            )
        else:
            return JsonResponse({'error': 'Invalid item type'}, status=400)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({'message': 'Item added to cart successfully'})

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, cart_id):
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        cart_item.delete()
        return JsonResponse({"success": True, "message": "Item removed from cart"})
class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return JsonResponse({'error': 'Cart is empty. Add items first.'}, status=400)

        total_amount = sum(
            (item.medicine.price if item.medicine else item.product.price) * item.quantity
            for item in cart_items
        )

        order = Order.objects.create(user=request.user, order_date=now(), total_amount=total_amount)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                medicine=item.medicine if item.medicine else None,
                product=item.product if item.product else None,
                quantity=item.quantity,
                price=(item.medicine.price if item.medicine else item.product.price) * item.quantity
            )

        cart_items.delete()

        return redirect('order_summary', order_id=order.id)

class OrderSummaryView(LoginRequiredMixin, View):
    template_name = 'order_summary.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, self.template_name, {'order': order, 'order_items': order_items})

class ProceedToPaymentView(LoginRequiredMixin, View):
    template_name = 'proceed_to_payment.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_status != 'PENDING':
            return JsonResponse({'error': 'This order is already processed.'}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        razorpay_order = client.order.create({
            'amount': int(order.total_amount * 100),
            'currency': 'INR',
            'payment_capture': '1',
        })

        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return render(request, self.template_name, {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_api_key': settings.RAZORPAY_API_KEY,
            'order_total': order.total_amount,
        })

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({'error': 'Invalid payment details.'}, status=400)

        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }
            client.utility.verify_payment_signature(params_dict)

            payment = client.payment.fetch(razorpay_payment_id)
            if payment['status'] == 'captured':
                order.payment_status = 'COMPLETED'
                order.razorpay_payment_id = razorpay_payment_id
                order.save()
                return redirect('payment_success', order_id=order.id)

            order.payment_status = 'FAILED'
            order.save()
            return JsonResponse({'error': 'Payment not captured.'}, status=400)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Payment verification failed.'}, status=400)

class PaymentSuccessView(LoginRequiredMixin, View):
    template_name = 'payment_success.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.payment_status == 'COMPLETED':
            return render(request, self.template_name, {'order': order})
        return JsonResponse({'error': 'Invalid request.'}, status=400)
