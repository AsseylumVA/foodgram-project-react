from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet,
                       RecipeViewSet,
                       TagViewSet,
                       SubscriptionsViewSet,
                       UserSubscribeView)

router = DefaultRouter()

router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)


urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'})),
    path('users/<int:user_id>/subscribe/', UserSubscribeView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
