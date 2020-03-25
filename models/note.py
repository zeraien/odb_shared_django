from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_extensions.db.models import TimeStampedModel

def add_note(instance, text, note_type=None, author=None):
    """
    add a note to the supplied object instance.
    :param instance: The instance
    :param text: The note
    :param note_type: The type of the note, can be anything, but recommend a useful identifier (max length 50)
    :param author: The author, optional
    :return: Return the `Note` object, but you'll probably not care.
    """
    return Note.objects.create(content_type=ContentType.objects.get_for_model(instance),
                               object_id=instance.pk,
                               content=text,
                               author=author,
                               note_type=note_type
                               )

class Note(TimeStampedModel):
    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")
        ordering = ['-created']
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    markup = models.SlugField(_("markup language"), default="markdown")
    note_type = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    content = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(db_index=True)
    parent = GenericForeignKey()

    def __str__(self):
        return "Note for %s:%s" % (self.content_type, self.object_id)
