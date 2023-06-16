from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

__author__ = 'abolfazl'


def group_permission_required(perm, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        perms = unicode(perm)

        # get all permissions of user
        u_permissions = list(user.get_all_permissions())

        # First check if the user has the permission (even anon users)
        if perms in u_permissions:
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)