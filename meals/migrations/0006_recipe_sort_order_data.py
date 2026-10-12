from django.db import migrations


def assign_sort_order(apps, schema_editor):
    """Give existing recipes sort_order 10, 20, 30... in alphabetical order.

    This preserves the previous name ordering as the starting custom order.
    """
    Recipe = apps.get_model("meals", "Recipe")
    for position, recipe in enumerate(Recipe.objects.order_by("name"), start=1):
        recipe.sort_order = position * 10
        recipe.save(update_fields=["sort_order"])


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0005_recipe_sort_order"),
    ]

    operations = [
        migrations.RunPython(assign_sort_order, migrations.RunPython.noop),
    ]
