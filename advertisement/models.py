from django.db import models
from PIL import Image

# Create your models here.
def upload_img(instance,filename):
    return f'ads_img/{filename}'

class Advertisement(models.Model):
    class AdsObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset() .filter(active=True)

    priority = (
        ('high','High'),
        ('medium','Medium'),
        ('low','Low'),
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=upload_img)
    priority = models.CharField(max_length=60,choices=priority,default='low')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    adsobjects = AdsObjects()

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
       super(Advertisement, self).save(*args, **kwargs)
       image = Image.open(self.image.path)
       image.save(self.image.path,quality=20,optimize=True)


