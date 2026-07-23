import re
from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, Restaurant, FoodItem, Review, DeliveryPartner, Coupon, FoodCategory
from .form_utils import widget_attrs, apply_form_control
from .payment_utils import luhn_check, DUMMY_TEST_CARDS
from . import validators as v


class BaseValidatedForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control(self)


class BaseValidatedModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control(self)


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs=widget_attrs(type='email', placeholder='you@email.com')),
    )
    phone = forms.CharField(
        max_length=10, min_length=10, required=True,
        widget=forms.TextInput(attrs=widget_attrs(
            placeholder='10-digit mobile number', maxlength='10',
            pattern='[6-9][0-9]{9}', inputmode='numeric',
            title='10-digit number starting with 6-9',
        )),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs=widget_attrs(rows=3, placeholder='Delivery address (optional)', maxlength='500')),
        required=False,
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs=widget_attrs(placeholder='First name', maxlength='50')),
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs=widget_attrs(placeholder='Last name', maxlength='50')),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs=widget_attrs(
                placeholder='Choose a username', minlength='3', maxlength='30',
                pattern='[a-zA-Z0-9_]{3,30}',
            )),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control(self)
        self.fields['password1'].widget.attrs.update(widget_attrs(placeholder='Min 8 characters', minlength='8'))
        self.fields['password2'].widget.attrs.update(widget_attrs(placeholder='Confirm password', minlength='8'))

    def clean_username(self):
        return v.clean_username(self.cleaned_data.get('username'))

    def clean_email(self):
        return v.clean_email(self.cleaned_data.get('email'))

    def clean_first_name(self):
        return v.clean_name(self.cleaned_data.get('first_name'), 'First name')

    def clean_last_name(self):
        val = self.cleaned_data.get('last_name', '')
        return v.clean_name(val, 'Last name') if val.strip() else ''

    def clean_phone(self):
        return v.clean_phone(self.cleaned_data.get('phone'))

    def clean_address(self):
        return v.clean_address(self.cleaned_data.get('address'), required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class RestaurantRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=widget_attrs(type='email')))
    restaurant_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs=widget_attrs(minlength='3', maxlength='200')))
    description = forms.CharField(widget=forms.Textarea(attrs=widget_attrs(rows=3, maxlength='1000')), required=False)
    address = forms.CharField(widget=forms.Textarea(attrs=widget_attrs(rows=2, minlength='10', maxlength='500')))
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs=widget_attrs(maxlength='10', pattern='[6-9][0-9]{9}', inputmode='numeric')),
    )
    cuisine_type = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=widget_attrs(maxlength='100')))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control(self)

    def clean_username(self):
        return v.clean_username(self.cleaned_data.get('username'))

    def clean_email(self):
        return v.clean_email(self.cleaned_data.get('email'))

    def clean_restaurant_name(self):
        return v.clean_restaurant_name(self.cleaned_data.get('restaurant_name'))

    def clean_address(self):
        return v.clean_address(self.cleaned_data.get('address'), 'Restaurant address')

    def clean_phone(self):
        return v.clean_phone(self.cleaned_data.get('phone'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'restaurant'
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            Restaurant.objects.create(
                user=user,
                name=self.cleaned_data['restaurant_name'],
                description=self.cleaned_data.get('description', ''),
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone'],
                email=user.email,
                cuisine_type=self.cleaned_data.get('cuisine_type', ''),
            )
        return user


class DeliveryRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=widget_attrs(type='email')))
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs=widget_attrs(maxlength='10', pattern='[6-9][0-9]{9}', inputmode='numeric')),
    )
    vehicle_type = forms.ChoiceField(
        choices=[('Bike', 'Bike'), ('Scooter', 'Scooter'), ('Bicycle', 'Bicycle'), ('Car', 'Car')],
        initial='Bike',
    )
    vehicle_number = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs=widget_attrs(placeholder='e.g. MH12AB1234', maxlength='20')),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control(self)

    def clean_username(self):
        return v.clean_username(self.cleaned_data.get('username'))

    def clean_email(self):
        return v.clean_email(self.cleaned_data.get('email'))

    def clean_phone(self):
        return v.clean_phone(self.cleaned_data.get('phone'))

    def clean_vehicle_number(self):
        return v.clean_vehicle_number(self.cleaned_data.get('vehicle_number'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'delivery'
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            DeliveryPartner.objects.create(
                user=user,
                vehicle_type=self.cleaned_data['vehicle_type'],
                vehicle_number=self.cleaned_data.get('vehicle_number', ''),
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs=widget_attrs(
            placeholder='Username', minlength='3', maxlength='30', autocomplete='username',
        )),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs=widget_attrs(
            placeholder='Password', autocomplete='current-password',
        )),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control(self)

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Password is required.')
        return password


class RestaurantProfileForm(BaseValidatedModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 'phone', 'email', 'cuisine_type',
                  'opening_time', 'closing_time', 'is_open', 'delivery_time', 'min_order', 'logo', 'cover_image']
        widgets = {
            'name': forms.TextInput(attrs=widget_attrs(minlength='3', maxlength='200')),
            'description': forms.Textarea(attrs=widget_attrs(rows=3, maxlength='1000')),
            'address': forms.Textarea(attrs=widget_attrs(rows=2, minlength='10', maxlength='500')),
            'phone': forms.TextInput(attrs=widget_attrs(maxlength='10', pattern='[6-9][0-9]{9}', inputmode='numeric')),
            'email': forms.EmailInput(attrs=widget_attrs(type='email')),
            'cuisine_type': forms.TextInput(attrs=widget_attrs(maxlength='100')),
            'delivery_time': forms.TextInput(attrs=widget_attrs(maxlength='50')),
            'min_order': forms.NumberInput(attrs=widget_attrs(min='0', step='0.01')),
        }

    def clean_name(self):
        return v.clean_restaurant_name(self.cleaned_data.get('name'))

    def clean_address(self):
        return v.clean_address(self.cleaned_data.get('address'), 'Address')

    def clean_phone(self):
        return v.clean_phone(self.cleaned_data.get('phone'))

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            v.clean_email(email)
        return email

    def clean_min_order(self):
        val = self.cleaned_data.get('min_order')
        if val is not None and val < 0:
            raise forms.ValidationError('Minimum order cannot be negative.')
        return val


class FoodItemForm(BaseValidatedModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'description', 'category', 'price', 'image', 'is_vegetarian', 'is_available', 'preparation_time']
        widgets = {
            'name': forms.TextInput(attrs=widget_attrs(minlength='2', maxlength='200')),
            'description': forms.Textarea(attrs=widget_attrs(rows=3, maxlength='1000')),
            'price': forms.NumberInput(attrs=widget_attrs(min='1', step='0.01')),
            'preparation_time': forms.NumberInput(attrs=widget_attrs(min='1', max='180')),
        }

    def clean_name(self):
        return v.clean_food_name(self.cleaned_data.get('name'))

    def clean_price(self):
        return v.clean_price(self.cleaned_data.get('price'))

    def clean_preparation_time(self):
        return v.clean_positive_int(self.cleaned_data.get('preparation_time'), 'Preparation time', 1, 180)


class ReviewForm(BaseValidatedModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.HiddenInput(attrs={'id': 'rating-input'}))

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs=widget_attrs(
                rows=4, minlength='10', maxlength='1000',
                placeholder='Share your experience (min 10 characters)...',
            )),
        }

    def clean_rating(self):
        return v.clean_rating(self.cleaned_data.get('rating'))

    def clean_comment(self):
        return v.clean_review_comment(self.cleaned_data.get('comment'))


class CheckoutForm(BaseValidatedForm):
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs=widget_attrs(rows=3, minlength='10', maxlength='500', placeholder='Full delivery address')),
    )
    delivery_phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs=widget_attrs(
            placeholder='10-digit mobile number', maxlength='10',
            pattern='[6-9][0-9]{9}', inputmode='numeric',
        )),
    )
    special_instructions = forms.CharField(
        widget=forms.Textarea(attrs=widget_attrs(rows=2, maxlength='300', placeholder='Optional')),
        required=False,
    )
    coupon_code = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs=widget_attrs(placeholder='e.g. WELCOME20', maxlength='20')),
    )
    payment_method = forms.ChoiceField(
        choices=[('card', 'Credit/Debit Card'), ('upi', 'UPI'), ('wallet', 'Wallet'), ('cod', 'Cash on Delivery')],
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
    )
    card_holder = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=widget_attrs(placeholder='Name on card', minlength='3', maxlength='100')))
    card_number = forms.CharField(
        max_length=19, required=False,
        widget=forms.TextInput(attrs=widget_attrs(
            placeholder='4242 4242 4242 4242', maxlength='19', inputmode='numeric',
            title='16-digit card number',
        )),
    )
    expiry_month = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs=widget_attrs(placeholder='MM', maxlength='2', inputmode='numeric')))
    expiry_year = forms.CharField(max_length=4, required=False, widget=forms.TextInput(attrs=widget_attrs(placeholder='YY', maxlength='4', inputmode='numeric')))
    cvv = forms.CharField(max_length=3, required=False, widget=forms.PasswordInput(attrs=widget_attrs(placeholder='CVV', maxlength='3', inputmode='numeric')))
    upi_id = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=widget_attrs(placeholder='yourname@upi', maxlength='100')))
    wallet_pin = forms.CharField(max_length=4, required=False, widget=forms.PasswordInput(attrs=widget_attrs(placeholder='4-digit wallet PIN', maxlength='4', inputmode='numeric')))

    def clean_delivery_address(self):
        return v.clean_address(self.cleaned_data.get('delivery_address'), 'Delivery address')

    def clean_delivery_phone(self):
        return v.clean_phone(self.cleaned_data.get('delivery_phone'), 'Delivery phone')

    def clean_special_instructions(self):
        val = (self.cleaned_data.get('special_instructions') or '').strip()
        if len(val) > 300:
            raise forms.ValidationError('Special instructions must be at most 300 characters.')
        return val

    def clean_coupon_code(self):
        return v.clean_coupon_code(self.cleaned_data.get('coupon_code'))

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get('payment_method')

        if method == 'card':
            try:
                cleaned['card_holder'] = v.clean_card_holder(cleaned.get('card_holder'))
            except forms.ValidationError as e:
                self.add_error('card_holder', e.messages[0])

            try:
                digits = v.clean_card_number(cleaned.get('card_number'))
                if not luhn_check(digits):
                    self.add_error('card_number', 'Invalid card number.')
                elif digits not in DUMMY_TEST_CARDS:
                    self.add_error('card_number', 'Use demo card: 4242 4242 4242 4242')
                else:
                    cleaned['card_number'] = digits
            except forms.ValidationError as e:
                self.add_error('card_number', e.messages[0])

            try:
                month = v.clean_expiry_month(cleaned.get('expiry_month'))
                year = v.clean_expiry_year(cleaned.get('expiry_year'))
                v.clean_expiry_not_past(month, year)
                cleaned['card_expiry'] = f'{month}/{year[-2:]}'
            except forms.ValidationError as e:
                self.add_error('expiry_month', e.messages[0])

            try:
                cleaned['cvv'] = v.clean_cvv(cleaned.get('cvv'))
            except forms.ValidationError as e:
                self.add_error('cvv', e.messages[0])

        elif method == 'upi':
            try:
                cleaned['upi_id'] = v.clean_upi(cleaned.get('upi_id'))
            except forms.ValidationError as e:
                self.add_error('upi_id', e.messages[0])

        elif method == 'wallet':
            try:
                pin = v.clean_wallet_pin(cleaned.get('wallet_pin'))
                if pin != '1234':
                    self.add_error('wallet_pin', 'Invalid wallet PIN. Demo PIN is 1234.')
                else:
                    cleaned['wallet_pin'] = pin
            except forms.ValidationError as e:
                self.add_error('wallet_pin', e.messages[0])

        return cleaned


class UserProfileForm(BaseValidatedModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs=widget_attrs(minlength='2', maxlength='50')),
            'last_name': forms.TextInput(attrs=widget_attrs(maxlength='50')),
            'email': forms.EmailInput(attrs=widget_attrs(type='email')),
            'phone': forms.TextInput(attrs=widget_attrs(maxlength='10', pattern='[6-9][0-9]{9}', inputmode='numeric')),
            'address': forms.Textarea(attrs=widget_attrs(rows=3, maxlength='500')),
        }

    def clean_first_name(self):
        return v.clean_name(self.cleaned_data.get('first_name'), 'First name')

    def clean_last_name(self):
        val = self.cleaned_data.get('last_name', '')
        return v.clean_name(val, 'Last name') if val.strip() else ''

    def clean_email(self):
        return v.clean_email(self.cleaned_data.get('email'))

    def clean_phone(self):
        return v.clean_optional_phone(self.cleaned_data.get('phone'))

    def clean_address(self):
        return v.clean_address(self.cleaned_data.get('address'), required=False)


class CategoryForm(BaseValidatedModelForm):
    class Meta:
        model = FoodCategory
        fields = ['name', 'description', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=widget_attrs(minlength='2', maxlength='100')),
            'description': forms.Textarea(attrs=widget_attrs(rows=2, maxlength='500')),
            'icon': forms.TextInput(attrs=widget_attrs(maxlength='10', placeholder='🍕')),
        }

    def clean_name(self):
        return v.clean_category_name(self.cleaned_data.get('name'))


class CouponForm(BaseValidatedModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount_type', 'discount_value', 'min_order_amount',
                  'max_discount', 'valid_from', 'valid_until', 'usage_limit', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs=widget_attrs(minlength='3', maxlength='20')),
            'description': forms.TextInput(attrs=widget_attrs(maxlength='200')),
            'discount_value': forms.NumberInput(attrs=widget_attrs(min='0.01', step='0.01')),
            'min_order_amount': forms.NumberInput(attrs=widget_attrs(min='0', step='0.01')),
            'max_discount': forms.NumberInput(attrs=widget_attrs(min='0', step='0.01')),
            'usage_limit': forms.NumberInput(attrs=widget_attrs(min='1', max='100000')),
            'valid_from': forms.DateTimeInput(attrs=widget_attrs(type='datetime-local')),
            'valid_until': forms.DateTimeInput(attrs=widget_attrs(type='datetime-local')),
        }

    def clean_code(self):
        code = v.clean_coupon_code(self.cleaned_data.get('code'))
        return code.upper() if code else code

    def clean_discount_value(self):
        return v.clean_price(self.cleaned_data.get('discount_value'), 'Discount value')

    def clean_min_order_amount(self):
        val = self.cleaned_data.get('min_order_amount')
        if val is not None and val < 0:
            raise forms.ValidationError('Minimum order amount cannot be negative.')
        return val

    def clean_usage_limit(self):
        return v.clean_positive_int(self.cleaned_data.get('usage_limit'), 'Usage limit', 1, 100000)

    def clean(self):
        cleaned = super().clean()
        valid_from = cleaned.get('valid_from')
        valid_until = cleaned.get('valid_until')
        if valid_from and valid_until and valid_until <= valid_from:
            raise forms.ValidationError('Valid until must be after valid from.')
        return cleaned


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False, max_length=100,
        widget=forms.TextInput(attrs=widget_attrs(placeholder='Search restaurants, cuisines, dishes...', maxlength='100')),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control(self)

    def clean_q(self):
        return v.clean_search_query(self.cleaned_data.get('q'))
