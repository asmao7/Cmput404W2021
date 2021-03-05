from django import forms

#TODO data validation for form data 
class SignUpForm(forms.Form):

    fistName = forms.CharField(label='First Name', max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'First Name'
        }))
    lastName = forms.CharField(label='Last Name', max_length=1000, required=True,widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'Last Name'
        }))
    displayName = forms.CharField(label='Display Name', max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'User Name'
        }))
    Email = forms.EmailField(label='Email', max_length=100, required=True, widget=forms.EmailInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'Email Address'
        }))
    GithubUrl = forms.URLField(label='Github URL', max_length=3000,required=False, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'Enter your github url'
        }))
    Password = forms.CharField(label='Password',max_length=32, widget=forms.PasswordInput)
    Confirm_Password = forms.CharField(label='Confirm Password',max_length=32, widget=forms.PasswordInput)


class LoginForm(forms.Form):
    UserName = forms.CharField(label='UserName', max_length=1000, required=True, widget=forms.TextInput)
    Password = forms.CharField(label='Password', max_length=32, required=True, widget=forms.PasswordInput)

class EditProfileForm(forms.Form):

    fistName = forms.CharField(label='First Name', max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'First Name'
        }))
    lastName = forms.CharField(label='Last Name', max_length=1000, required=True,widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'Last Name'
        }))
    displayName = forms.CharField(label='Display Name', max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'User Name'
        }))
    Password = forms.CharField(label='Password',max_length=32, widget=forms.PasswordInput)
    Confirm_Password = forms.CharField(label='Confirm Password',max_length=32, widget=forms.PasswordInput)
