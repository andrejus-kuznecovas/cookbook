from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0004_usersetting"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="sort_order",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="recipe",
            options={"ordering": ["sort_order", "name"]},
        ),
    ]
