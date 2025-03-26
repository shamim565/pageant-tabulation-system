from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

# @register.filter
# def add_attr(value, arg):
#     key, val = arg.split('=')
#     return value.as_widget(attrs={key: val})