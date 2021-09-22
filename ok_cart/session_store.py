from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore as DjangoSessionStore

from .selectors import get_or_create_user_cart
from .settings import settings

__all__ = ('SessionStore',)

OLD_SESSION_KEY = "_old_session_key"
User = get_user_model()


class SessionStore(DjangoSessionStore):

    def save_old_session_key(self, old_session_key):
        self[OLD_SESSION_KEY] = old_session_key

    def get_old_session_key(self):
        return self.get(OLD_SESSION_KEY)

    def cycle_key(self):
        """
        Calls in login

        Save old session key to get it in `user_logged_in_handler`
        """
        old_session_key = self.session_key
        self.save_old_session_key(old_session_key)
        super().cycle_key()

    def flush(self):
        """
        Calls on logout

        Update logged out user's cart with new session key
        """
        logged_out_user_id = self.get(SESSION_KEY)
        super().flush()

        if settings.MERGE_ENABLED and logged_out_user_id:
            user = User.objects.get(pk=logged_out_user_id)

            if not self.session_key:
                self.create()

            user_cart, _ = get_or_create_user_cart(user=user)
            user_cart.session_key = self.session_key
            user_cart.save(update_fields=['session_key'])
