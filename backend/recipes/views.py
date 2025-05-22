from django.shortcuts import get_object_or_404, redirect
from recipes.models import Recipe

def short_link_redirect_view(request, code):
    """
    Обрабатывает короткую ссылку вида /s/3d<ID> и перенаправляет на полную.
    """
    try:
        recipe_id = int(code[2:])
    except (ValueError, IndexError):
        raise Http404("Некорректный код рецепта")

    recipe = get_object_or_404(Recipe, id=recipe_id)
    return redirect('api:recipe-detail', pk=recipe.id)
