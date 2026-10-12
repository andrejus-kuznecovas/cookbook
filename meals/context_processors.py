from .models import Theme, UserSetting


def theme(request):
    """Expose the current user's theme choice to every template.

    Anonymous users (and users who never saved Settings) get "system",
    which keeps the browser's prefers-color-scheme behavior.
    """
    if request.user.is_authenticated:
        setting = UserSetting.objects.filter(user=request.user).first()
        if setting:
            return {"theme": setting.theme}
    return {"theme": Theme.SYSTEM.value}
