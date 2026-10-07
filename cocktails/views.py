from django.contrib.auth.models import User
from django.db.models.deletion import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from cocktails.models import Ingredient, Cocktail
from cocktails.permissions import IsAuthorOrReadOnly
from cocktails.serializers import IngredientSerializer, CocktailSerializer, RegisterSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["is_alcoholic"]
    search_fields = ["name"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Ingredient is in use and it cannot be removed"},
                status=status.HTTP_409_CONFLICT,
            )


class CocktailViewSet(viewsets.ModelViewSet):
    queryset = Cocktail.objects.prefetch_related("recipe_items__ingredient")
    serializer_class = CocktailSerializer

    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtering by category
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        # Filtering by ingredient name
        ingredient_name = self.request.query_params.get("ingredient")
        if ingredient_name:
            queryset = queryset.filter(recipe_items__ingredient__name__icontains=ingredient_name)

        # Filtering by ingredient id
        ingredient_id = self.request.query_params.get("ingredient_id")
        if ingredient_id:
            queryset = queryset.filter(recipe_items__ingredient__id=ingredient_id)

        # Filtering by alcohol content
        is_alcoholic_param = self.request.query_params.get("is_alcoholic")
        if is_alcoholic_param is not None:
            is_alcoholic = is_alcoholic_param.lower() in ["true", "1", "yes"]
            if is_alcoholic:
                # Cocktail has ingredient flagged as is_alcoholic
                queryset = queryset.filter(recipe_items__ingredient__is_alcoholic=True).distinct()
            else:
                # Cocktail with no alcohol
                alcoholic_cocktails = Cocktail.objects.filter(recipe_items__ingredient__is_alcoholic=True)
                queryset = queryset.exclude(id__in=alcoholic_cocktails).distinct()

        # Filtering by author
        author_username = self.request.query_params.get("author")
        if author_username:
            queryset = queryset.filter(author__username__iexact=author_username)

        author_id = self.request.query_params.get("author_id")
        if author_id:
            queryset = queryset.filter(author__id=author_id)

        return queryset

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
