"""Form widget helpers."""
from django import forms

FORM_CONTROL_CLASS = 'form-control'


def widget_attrs(**extra):
    attrs = {'class': FORM_CONTROL_CLASS}
    attrs.update(extra)
    return attrs


def apply_form_control(form):
    """Add form-control class and novalidate handling to all visible fields."""
    for field in form.visible_fields():
        existing = field.field.widget.attrs.get('class', '')
        if FORM_CONTROL_CLASS not in existing:
            field.field.widget.attrs['class'] = f'{existing} {FORM_CONTROL_CLASS}'.strip()
    return form
