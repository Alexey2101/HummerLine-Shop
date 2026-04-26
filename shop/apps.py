from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
    verbose_name = 'HummerLine'

    def ready(self):
        pass

@receiver(connection_created)
def extend_sqlite(connection=None, **kwargs):
    if connection.vendor == "sqlite":
        # Регистрируем функции lower и upper для поддержки кириллицы
        connection.connection.create_function("LOWER", 1, lambda x: x.lower() if x else x)
        connection.connection.create_function("UPPER", 1, lambda x: x.upper() if x else x)
        
        # Функция для нечеткого поиска (Trigram Similarity)
        def trigram_similarity(s1, s2):
            if not s1 or not s2: return 0.0
            s1, s2 = s1.lower(), s2.lower()
            if s1 == s2: return 1.0
            
            def get_trigrams(s):
                s = f"  {s}  "
                return {s[i:i+3] for i in range(len(s)-2)}
            
            t1 = get_trigrams(s1)
            t2 = get_trigrams(s2)
            intersection = t1.intersection(t2)
            union = t1.union(t2)
            return len(intersection) / len(union) if union else 0.0
            
        connection.connection.create_function("SIMILARITY", 2, trigram_similarity)
