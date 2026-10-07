from rest_framework.routers import DefaultRouter

from .views import CocktailViewSet, IngredientViewSet

router = DefaultRouter()
router.register("ingredients", IngredientViewSet)
router.register("cocktails", CocktailViewSet)

urlpatterns = router.urls