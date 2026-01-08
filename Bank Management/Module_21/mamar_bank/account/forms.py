from django import forms
from .models import UserBankAccount, UserAddress, User
from .constants import ACCOUNT_TYPE, GENDER_TYPE
from django.contrib.auth.forms import UserCreationForm

class UserRagistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'id' : 'required'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'id' : 'required'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'id' : 'required'}))

    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'account_type', 'birth_date', 'gender', 'street_address', 'postal_code', 'city', 'country']
    
     # built in vabe commit = True kore deya ache. Kintu emon hotei pare user commit = False diye rakhche
    def save(self, commit = True):
        # super use kore User Model er data gulo niye ashlam (UserCreationForm)
        our_user = super().save(commit=False) # "commit = False" mane ami database e data save korbona ekhon.
       
        if commit == True:
            our_user.save() # user model e data save korlam
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            birth_date = self.cleaned_data.get('birth_date')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')

            # user er jonno ei address ta make hoye jabe.
            UserAddress.objects.create( # user er ekta object make korlam.
                user = our_user,
                postal_code = postal_code,
                country = country,
                city = city,
                street_address = street_address,
            )
            UserBankAccount.objects.create(
                user = our_user,
                account_type = account_type,
                gender = gender,
                birth_date = birth_date,
                account_no = 1000000 + our_user.id,
            )
        return our_user
    
    def __init__(self, *args, **kwargs): # Constructor.
        # parent class (UserCreationForm) ke call kortechi super er maddhome,
        # parent class ke inherite kore (__init__ er sahajje) overwrite korlam.
        # *args (keyword chara parameter), **kwargs (keyword soho parameter) --> parameter hisebe kichu dei ba na dei tate kono somossha hobe na.
        super().__init__(*args, **kwargs) # parent ke call kortechi (UserCreationForm).

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })

class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length= 100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs): # constructor
        super().__init__(*args, **kwargs) # parent class er (ModelForm) __init__ function take inherite kore niye ashlam. Tarpor Overwrite korbo.
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        # jodi user er account thake / current logged in user. 
        if self.instance: # ekta class er instance ba object. (instance jodi thake.)
            try:
                user_account = self.instance.account # orthat je user ta request korteche tar account ta (account model er data) 
                user_address = self.instance.address # addres model er data
            except UserBankAccount.DoesNotExist: # Bank account jodi na thake.
                user_account = None # bank account nai mane tar kono account nai, address o nai.
                user_address = None

            if user_account: # jodi user er account thake.
                # Tahole ei field gulate oi user er information gula thakbe jegula se account create korar somoy fillup korche.
                # Form load হলে আগের data auto fill হবে
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserBankAccount.objects.get_or_create(user=user) # jodi account thake taile seta jabe user_account ar jodi account na thake taile create hobe ar seta created er moddhe jabe (save hobe)
            user_address, created = UserAddress.objects.get_or_create(user=user) 

            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user
    
"""
Form → User
     → UserAddress
     → UserBankAccount

     
Form → User (update)
     → UserAddress (update/create)
     → UserBankAccount (update/create)

"""