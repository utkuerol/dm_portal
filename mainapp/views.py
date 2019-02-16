from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic import DetailView


class UserProfileView(DetailView):
    model = User
    template_name = 'user_profile.html'

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super(UserProfileView, self).dispatch(*args, **kwargs)

