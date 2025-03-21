# # auth_page/forms.py

# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from .models import CustomUser
# import re

# # List of countries and their country codes, sorted by country name
# COUNTRY_CHOICES = [
#     ('+93', '+93 - Afghanistan'),
#     ('+355', '+355 - Albania'),
#     ('+213', '+213 - Algeria'),
#     ('+376', '+376 - Andorra'),
#     ('+244', '+244 - Angola'),
#     ('+1', '+1 - Antigua and Barbuda'),
#     ('+54', '+54 - Argentina'),
#     ('+374', '+374 - Armenia'),
#     ('+61', '+61 - Australia'),
#     ('+43', '+43 - Austria'),
#     ('+994', '+994 - Azerbaijan'),
#     ('+1', '+1 - Bahamas'),
#     ('+973', '+973 - Bahrain'),
#     ('+880', '+880 - Bangladesh'),
#     ('+1', '+1 - Barbados'),
#     ('+375', '+375 - Belarus'),
#     ('+32', '+32 - Belgium'),
#     ('+501', '+501 - Belize'),
#     ('+229', '+229 - Benin'),
#     ('+975', '+975 - Bhutan'),
#     ('+591', '+591 - Bolivia'),
#     ('+387', '+387 - Bosnia and Herzegovina'),
#     ('+267', '+267 - Botswana'),
#     ('+55', '+55 - Brazil'),
#     ('+673', '+673 - Brunei'),
#     ('+359', '+359 - Bulgaria'),
#     ('+226', '+226 - Burkina Faso'),
#     ('+257', '+257 - Burundi'),
#     ('+855', '+855 - Cambodia'),
#     ('+237', '+237 - Cameroon'),
#     ('+1', '+1 - Canada'),
#     ('+238', '+238 - Cape Verde'),
#     ('+236', '+236 - Central African Republic'),
#     ('+235', '+235 - Chad'),
#     ('+56', '+56 - Chile'),
#     ('+86', '+86 - China'),
#     ('+57', '+57 - Colombia'),
#     ('+269', '+269 - Comoros'),
#     ('+242', '+242 - Congo'),
#     ('+506', '+506 - Costa Rica'),
#     ('+385', '+385 - Croatia'),
#     ('+53', '+53 - Cuba'),
#     ('+357', '+357 - Cyprus'),
#     ('+420', '+420 - Czech Republic'),
#     ('+45', '+45 - Denmark'),
#     ('+253', '+253 - Djibouti'),
#     ('+1', '+1 - Dominica'),
#     ('+1', '+1 - Dominican Republic'),
#     ('+670', '+670 - East Timor'),
#     ('+593', '+593 - Ecuador'),
#     ('+20', '+20 - Egypt'),
#     ('+503', '+503 - El Salvador'),
#     ('+240', '+240 - Equatorial Guinea'),
#     ('+291', '+291 - Eritrea'),
#     ('+372', '+372 - Estonia'),
#     ('+251', '+251 - Ethiopia'),
#     ('+679', '+679 - Fiji'),
#     ('+358', '+358 - Finland'),
#     ('+33', '+33 - France'),
#     ('+241', '+241 - Gabon'),
#     ('+220', '+220 - Gambia'),
#     ('+995', '+995 - Georgia'),
#     ('+49', '+49 - Germany'),
#     ('+233', '+233 - Ghana'),
#     ('+30', '+30 - Greece'),
#     ('+1', '+1 - Grenada'),
#     ('+502', '+502 - Guatemala'),
#     ('+224', '+224 - Guinea'),
#     ('+245', '+245 - Guinea-Bissau'),
#     ('+592', '+592 - Guyana'),
#     ('+509', '+509 - Haiti'),
#     ('+504', '+504 - Honduras'),
#     ('+36', '+36 - Hungary'),
#     ('+354', '+354 - Iceland'),
#     ('+91', '+91 - India'),
#     ('+62', '+62 - Indonesia'),
#     ('+98', '+98 - Iran'),
#     ('+964', '+964 - Iraq'),
#     ('+353', '+353 - Ireland'),
#     ('+972', '+972 - Israel'),
#     ('+39', '+39 - Italy'),
#     ('+1', '+1 - Jamaica'),
#     ('+81', '+81 - Japan'),
#     ('+962', '+962 - Jordan'),
#     ('+7', '+7 - Kazakhstan'),
#     ('+254', '+254 - Kenya'),
#     ('+686', '+686 - Kiribati'),
#     ('+850', '+850 - North Korea'),
#     ('+82', '+82 - South Korea'),
#     ('+965', '+965 - Kuwait'),
#     ('+996', '+996 - Kyrgyzstan'),
#     ('+856', '+856 - Laos'),
#     ('+371', '+371 - Latvia'),
#     ('+961', '+961 - Lebanon'),
#     ('+266', '+266 - Lesotho'),
#     ('+231', '+231 - Liberia'),
#     ('+218', '+218 - Libya'),
#     ('+423', '+423 - Liechtenstein'),
#     ('+370', '+370 - Lithuania'),
#     ('+352', '+352 - Luxembourg'),
#     ('+389', '+389 - North Macedonia'),
#     ('+261', '+261 - Madagascar'),
#     ('+265', '+265 - Malawi'),
#     ('+60', '+60 - Malaysia'),
#     ('+960', '+960 - Maldives'),
#     ('+223', '+223 - Mali'),
#     ('+356', '+356 - Malta'),
#     ('+692', '+692 - Marshall Islands'),
#     ('+222', '+222 - Mauritania'),
#     ('+230', '+230 - Mauritius'),
#     ('+52', '+52 - Mexico'),
#     ('+691', '+691 - Micronesia'),
#     ('+373', '+373 - Moldova'),
#     ('+377', '+377 - Monaco'),
#     ('+976', '+976 - Mongolia'),
#     ('+382', '+382 - Montenegro'),
#     ('+212', '+212 - Morocco'),
#     ('+258', '+258 - Mozambique'),
#     ('+95', '+95 - Myanmar'),
#     ('+264', '+264 - Namibia'),
#     ('+674', '+674 - Nauru'),
#     ('+977', '+977 - Nepal'),
#     ('+31', '+31 - Netherlands'),
#     ('+64', '+64 - New Zealand'),
#     ('+505', '+505 - Nicaragua'),
#     ('+227', '+227 - Niger'),
#     ('+234', '+234 - Nigeria'),
#     ('+47', '+47 - Norway'),
#     ('+968', '+968 - Oman'),
#     ('+92', '+92 - Pakistan'),
#     ('+680', '+680 - Palau'),
#     ('+970', '+970 - Palestine'),
#     ('+507', '+507 - Panama'),
#     ('+675', '+675 - Papua New Guinea'),
#     ('+595', '+595 - Paraguay'),
#     ('+51', '+51 - Peru'),
#     ('+63', '+63 - Philippines'),
#     ('+48', '+48 - Poland'),
#     ('+351', '+351 - Portugal'),
#     ('+974', '+974 - Qatar'),
#     ('+40', '+40 - Romania'),
#     ('+7', '+7 - Russia'),
#     ('+250', '+250 - Rwanda'),
#     ('+1', '+1 - Saint Kitts and Nevis'),
#     ('+1', '+1 - Saint Lucia'),
#     ('+1', '+1 - Saint Vincent and the Grenadines'),
#     ('+685', '+685 - Samoa'),
#     ('+378', '+378 - San Marino'),
#     ('+239', '+239 - Sao Tome and Principe'),
#     ('+966', '+966 - Saudi Arabia'),
#     ('+221', '+221 - Senegal'),
#     ('+381', '+381 - Serbia'),
#     ('+248', '+248 - Seychelles'),
#     ('+232', '+232 - Sierra Leone'),
#     ('+65', '+65 - Singapore'),
#     ('+421', '+421 - Slovakia'),
#     ('+386', '+386 - Slovenia'),
#     ('+677', '+677 - Solomon Islands'),
#     ('+252', '+252 - Somalia'),
#     ('+27', '+27 - South Africa'),
#     ('+211', '+211 - South Sudan'),
#     ('+34', '+34 - Spain'),
#     ('+94', '+94 - Sri Lanka'),
#     ('+249', '+249 - Sudan'),
#     ('+597', '+597 - Suriname'),
#     ('+268', '+268 - Eswatini'),
#     ('+46', '+46 - Sweden'),
#     ('+41', '+41 - Switzerland'),
#     ('+963', '+963 - Syria'),
#     ('+886', '+886 - Taiwan'),
#     ('+992', '+992 - Tajikistan'),
#     ('+255', '+255 - Tanzania'),
#     ('+66', '+66 - Thailand'),
#     ('+228', '+228 - Togo'),
#     ('+676', '+676 - Tonga'),
#     ('+1', '+1 - Trinidad and Tobago'),
#     ('+216', '+216 - Tunisia'),
#     ('+90', '+90 - Turkey'),
#     ('+993', '+993 - Turkmenistan'),
#     ('+688', '+688 - Tuvalu'),
#     ('+256', '+256 - Uganda'),
#     ('+380', '+380 - Ukraine'),
#     ('+971', '+971 - United Arab Emirates'),
#     ('+44', '+44 - United Kingdom'),
#     ('+1', '+1 - United States'),
#     ('+598', '+598 - Uruguay'),
#     ('+998', '+998 - Uzbekistan'),
#     ('+678', '+678 - Vanuatu'),
#     ('+379', '+379 - Vatican City'),
#     ('+58', '+58 - Venezuela'),
#     ('+84', '+84 - Vietnam'),
#     ('+967', '+967 - Yemen'),
#     ('+260', '+260 - Zambia'),
#     ('+263', '+263 - Zimbabwe'),
# ]

# def validate_complex_password(password):
#     """
#     Validate that the password:
#     - Is at least 8 characters long
#     - Contains at least one digit
#     - Contains at least one uppercase letter
#     - Contains at least one lowercase letter
#     - Contains at least one special character
#     """
#     if len(password) < 8:
#         raise ValidationError("Password must be at least 8 characters long.")
    
#     if not any(char.isdigit() for char in password):
#         raise ValidationError("Password must contain at least one number.")
    
#     if not any(char.isupper() for char in password):
#         raise ValidationError("Password must contain at least one uppercase letter.")
    
#     if not any(char.islower() for char in password):
#         raise ValidationError("Password must contain at least one lowercase letter.")
    
#     if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for char in password):
#         raise ValidationError("Password must contain at least one special character.")

# class CustomUserCreationForm(forms.ModelForm):
#     country_code = forms.ChoiceField(
#         choices=COUNTRY_CHOICES, 
#         required=True,
#         label="Country Code",
#         widget=forms.Select(attrs={'class': 'country-select'})
#     )
    
#     phone_number = forms.CharField(
#         max_length=15, 
#         required=True, 
#         help_text='Enter your phone number without the country code. If your number starts with 0, omit the 0.',
#         widget=forms.TextInput(attrs={'placeholder': 'Phone number without country code'})
#     )
    
#     card_number = forms.CharField(
#         max_length=16,
#         min_length=16,
#         required=True,
#         help_text='Enter your 16-digit card number',
#         widget=forms.TextInput(attrs={'placeholder': '16-digit card number'})
#     )
    
#     password1 = forms.CharField(
#         label="Password",
#         strip=False,
#         widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
#         help_text='Password must be at least 8 characters and include uppercase, lowercase, number, and special character.'
#     )
    
#     password2 = forms.CharField(
#         label="Confirm Password",
#         widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
#         strip=False,
#         help_text='Enter the same password as before, for verification.'
#     )
    
#     class Meta:
#         model = CustomUser
#         fields = ('country_code', 'phone_number', 'card_number', 'password1', 'password2')
    
#     def clean_phone_number(self):
#         phone = self.cleaned_data.get('phone_number')
        
#         # If phone starts with 0, remove it
#         if phone.startswith('0'):
#             phone = phone[1:]
            
#         # Check that phone contains only digits
#         if not phone.isdigit():
#             raise ValidationError("Phone number must contain only digits.")
            
#         return phone
        
#     def clean_card_number(self):
#         card_number = self.cleaned_data.get('card_number')
        
#         # Check that card number is exactly 16 digits
#         if not re.match(r'^\d{16}$', card_number):
#             raise ValidationError("Card number must be exactly 16 digits.")
            
#         return card_number
        
#     def clean_password1(self):
#         password = self.cleaned_data.get('password1')
#         validate_complex_password(password)
#         return password
        
#     def clean(self):
#         cleaned_data = super().clean()
#         password1 = cleaned_data.get('password1')
#         password2 = cleaned_data.get('password2')
        
#         if password1 and password2 and password1 != password2:
#             self.add_error('password2', "The two password fields didn't match.")
            
#         return cleaned_data
    
#     def save(self, commit=True):
#         user = super().save(commit=False)
        
#         country_code = self.cleaned_data.get('country_code')
#         phone_number = self.cleaned_data.get('phone_number')
#         full_phone = f"{country_code}{phone_number}"
        
#         user.full_phone = full_phone
#         user.set_password(self.cleaned_data["password1"])
        
#         if commit:
#             user.save()
#         return user

# class CustomAuthenticationForm(AuthenticationForm):
#     username = forms.CharField(
#         label='Phone Number (with country code)',
#         widget=forms.TextInput(attrs={'placeholder': 'e.g. +1234567890'})
#     )
    
#     def clean_username(self):
#         """Ensure the username field contains a properly formatted phone number."""
#         username = self.cleaned_data.get('username')
        
#         # Make sure it starts with a + sign
#         if not username.startswith('+'):
#             username = '+' + username
            
#         return username