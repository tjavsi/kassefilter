from django import template

register = template.Library()


def get_item(dictionary, key):
    if key in dictionary:
        return dictionary.get(key)
    else:
        return ''


register.filter('get_item', get_item)
