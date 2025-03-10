# Generated by Django 4.2.11 on 2024-12-17 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CorpTimerView',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('system_id', models.BigIntegerField()),
                ('timer_type_id', models.IntegerField()),
                ('timer_datetime', models.DateTimeField()),
                ('comment', models.CharField(blank=True, max_length=1000)),
                ('created_by_id', models.BigIntegerField()),
                ('created_date', models.DateTimeField()),
                ('hostility_type_id', models.IntegerField(blank=True, null=True)),
                ('structure_type_id', models.IntegerField(blank=True, null=True)),
                ('structure_type', models.CharField(max_length=50)),
                ('solar_system', models.CharField(max_length=50)),
                ('timer_type_name', models.CharField(max_length=50)),
                ('created_by', models.CharField(max_length=255)),
                ('structure_id', models.BigIntegerField(blank=True, null=True)),
                ('fleet_commander', models.CharField(blank=True, max_length=255, null=True)),
                ('structure_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'cm_corp_timer_view',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StructureRegistryView',
            fields=[
                ('structure_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('structure_name', models.CharField(max_length=1000)),
                ('structure_type_id', models.IntegerField()),
                ('structure_type', models.CharField(blank=True, max_length=100)),
                ('solar_system_id', models.IntegerField()),
                ('solar_system', models.CharField(blank=True, max_length=100)),
                ('constellation_id', models.IntegerField()),
                ('constellation', models.CharField(blank=True, max_length=100)),
                ('region_id', models.IntegerField()),
                ('alliance_id', models.IntegerField()),
                ('alliance', models.CharField(blank=True, max_length=50)),
                ('corporation_id', models.IntegerField()),
                ('corporation', models.CharField(blank=True, max_length=50)),
                ('fit_json', models.TextField(blank=True)),
                ('fit_last_updated_date', models.DateTimeField(blank=True, null=True)),
                ('fit_last_updated_by', models.CharField(blank=True, max_length=254)),
                ('vulnerability', models.CharField(blank=True, max_length=10, null=True)),
                ('timer_datetime', models.DateTimeField(blank=True, null=True)),
                ('timer_type', models.CharField(blank=True, max_length=50, null=True)),
                ('removed_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cm_structure_registry_view',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Alliance',
            fields=[
                ('alliance_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('ticker', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'cm_alliance',
            },
        ),
        migrations.CreateModel(
            name='Constellation',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('region_id', models.IntegerField()),
            ],
            options={
                'db_table': 'cm_constellation',
            },
        ),
        migrations.CreateModel(
            name='Corporation',
            fields=[
                ('corporation_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('ticker', models.CharField(max_length=50)),
                ('alliance_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cm_corporation',
            },
        ),
        migrations.CreateModel(
            name='CorpTimer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('system_id', models.BigIntegerField()),
                ('timer_type_id', models.IntegerField()),
                ('timer_datetime', models.DateTimeField()),
                ('comment', models.CharField(blank=True, max_length=1000)),
                ('created_by_id', models.BigIntegerField()),
                ('created_date', models.DateTimeField()),
                ('hostility_type_id', models.IntegerField(blank=True, null=True)),
                ('structure_type_id', models.IntegerField(blank=True, null=True)),
                ('structure_id', models.BigIntegerField(blank=True, null=True)),
                ('fleet_commander', models.CharField(blank=True, max_length=255, null=True)),
                ('planet', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'cm_corp_timer',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'cm_region',
            },
        ),
        migrations.CreateModel(
            name='SolarSystem',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('constellation_id', models.IntegerField()),
                ('x', models.FloatField(null=True)),
                ('y', models.FloatField(null=True)),
                ('z', models.FloatField(null=True)),
                ('security', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'cm_solar_system',
            },
        ),
        migrations.CreateModel(
            name='StructureRegistry',
            fields=[
                ('structure_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('structure_name', models.CharField(max_length=1000)),
                ('structure_type_id', models.IntegerField()),
                ('solar_system_id', models.IntegerField()),
                ('corporation_id', models.IntegerField()),
                ('removed', models.BooleanField()),
                ('removed_date', models.DateTimeField(blank=True, null=True)),
                ('vulnerability', models.CharField(blank=True, max_length=10, null=True)),
                ('vulnerability_updated', models.DateTimeField(blank=True, null=True)),
                ('vulnerability_character_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cm_structure_registry',
            },
        ),
        migrations.CreateModel(
            name='StructureRegistryFit',
            fields=[
                ('structure_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('fit_json', models.TextField()),
                ('modified_date', models.DateTimeField()),
                ('character_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'cm_structure_registry_fit',
            },
        ),
        migrations.CreateModel(
            name='StructureType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'cm_structure_type',
            },
        ),
        migrations.CreateModel(
            name='TimerHostility',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'cm_timer_hostility',
            },
        ),
        migrations.CreateModel(
            name='TimerStructureType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'cm_timer_structure_type',
            },
        ),
        migrations.CreateModel(
            name='TimerType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'cm_timer_type',
            },
        ),
    ]
