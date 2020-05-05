from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q

class UserListFilter(admin.RelatedOnlyFieldListFilter):
    """
    Use with the admin `list_filter` list to show full user names in the filter column,
    and also it shows only those names that are relevant to the queryset.
    Use like so:
    list_filter=(
        ('user', UserListFilter),
    )
    """

    def field_choices(self, field, request, model_admin):
        q = Q(pk__in=model_admin.get_queryset(request).distinct().values_list(field.name, flat=True))
        return [
            (u.pk, u.get_full_name())
            for u in User.objects.filter(q).only("pk", "first_name", 'last_name').order_by("-is_active", "first_name")
        ]
