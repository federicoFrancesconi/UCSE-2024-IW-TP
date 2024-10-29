from haystack import indexes
from .models import Descuento

class DescuentoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    nombre = indexes.CharField(model_attr='nombre')
    
    def get_model(self):
        return Descuento

    def index_queryset(self, using=None):
        return self.get_model().objects.all()