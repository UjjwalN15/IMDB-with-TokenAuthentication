from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.validators import RegexValidator
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        # Check for lowercase letters
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("The password must contain at least one lowercase letter."),
            )
        # Check for uppercase letters
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
            )
        # Check for digits
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("The password must contain at least one digit."),
            )
        # Check for special symbols
        if all(char.isalnum() for char in password):
            raise ValidationError(
                _("The password must contain at least one special symbol."),
            )

    def __call__(self, value):
        self.validate(value)

    def get_help_text(self):
        return _(
            "Your password must contain at least one lowercase letter, one uppercase letter, one digit, and one special symbol."
        )
        
contact_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='Contact number must be exactly 10 digits.'
    )
def validate_password(value):
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')

    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')

    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')

    if not re.search(r'\d', value):
        raise ValidationError('Password must contain at least one number.')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>+ - * = _]', value):
        raise ValidationError('Password must contain at least one special character.')