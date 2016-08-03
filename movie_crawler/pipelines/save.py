# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scrapy import log


class SavePipeline(object):
    # TODO: Rename to StorePipeline
    def process_item(self, item, spider):
        model = item.django_model
        many_to_many_fields = [f.name for f in model._meta.many_to_many]

        # Update model instance without ManyToMany Fields
        instance, _ = model.objects.get_or_create(**{
            field: item.get(field)
            for field in item.unique_fields
        })
        fields = dict(item.copy())
        for field in many_to_many_fields:
            if field in fields:
                fields.pop(field)
        model.objects.filter(id=instance.id).update(**fields)

        # Create ManyToMany relationship instance
        for field in many_to_many_fields:
            if not item.get(field):
                continue
            many_to_many_objs = getattr(instance, field)
            old_set = set(many_to_many_objs.all())
            new_set = set([
                model._meta.get_field(field).rel.to.objects.get_or_create(**value)[0]
                for value in item[field]
            ])
            for obj in new_set - old_set:
                many_to_many_objs.add(obj)
            for obj in old_set - new_set:
                many_to_many_objs.remove(obj)
