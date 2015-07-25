from django.core.urlresolvers import resolve, reverse as _reverse, \
    NoReverseMatch


def reverse(request, prefix, app_name, view_name, kwargs={}):
    _namespace = resolve(request.path).namespace
    try:
        if prefix is not None and app_name is not None:
            _namespace = prefix + '-' + app_name
        if _namespace:
            return _reverse(u':'.join([_namespace, view_name]), kwargs=kwargs)
        return _reverse(u':'.join([_namespace, view_name]), kwargs=kwargs)
    except NoReverseMatch:
        return u''
