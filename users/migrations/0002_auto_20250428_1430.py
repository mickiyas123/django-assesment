from django.db import migrations

def create_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # First check if a site with ID 1 exists
    if not Site.objects.filter(id=1).exists():
        Site.objects.create(id=1, domain='localhost:8000', name='localhost')
    else:
        # Update the existing site
        site = Site.objects.get(id=1)
        site.domain = 'localhost:8000'
        site.name = 'localhost'
        site.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('users', '0001_initial'),  # Make sure this matches your actual initial migration
    ]

    operations = [
        migrations.RunPython(create_site),
    ] 