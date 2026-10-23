from django.db import migrations


def move_aliases_to_project_types(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    ProjectType = apps.get_model("dictionaries", "ProjectType")
    database = schema_editor.connection.alias

    aliases_by_type = {}
    for project_type_id, alias in (
        Project.objects.using(database)
        .exclude(project_type_alias="")
        .values_list("project_type_id", "project_type_alias")
    ):
        if project_type_id is None:
            raise RuntimeError(
                "Cannot move project_type_alias for projects without a project_type."
            )
        aliases_by_type.setdefault(project_type_id, set()).add(alias)

    for project_type_id, aliases in aliases_by_type.items():
        if len(aliases) != 1:
            raise RuntimeError(
                f"Project type {project_type_id} has conflicting project aliases."
            )

        alias = aliases.pop()
        project_type = ProjectType.objects.using(database).get(pk=project_type_id)
        if project_type.project_type_alias and project_type.project_type_alias != alias:
            raise RuntimeError(
                f"Project type {project_type_id} already has a different alias."
            )

        if not project_type.project_type_alias:
            project_type.project_type_alias = alias
            project_type.save(using=database, update_fields=["project_type_alias"])


def restore_aliases_to_projects(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    ProjectType = apps.get_model("dictionaries", "ProjectType")
    database = schema_editor.connection.alias

    for project_type in ProjectType.objects.using(database).exclude(
        project_type_alias=""
    ):
        Project.objects.using(database).filter(
            project_type_id=project_type.pk,
            project_type_alias="",
        ).update(project_type_alias=project_type.project_type_alias)


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0007_projecttype_alias_and_name_length"),
        ("projects", "0015_project_project_type_and_alias"),
    ]

    operations = [
        migrations.RunPython(
            move_aliases_to_project_types,
            restore_aliases_to_projects,
        ),
        migrations.RemoveField(
            model_name="project",
            name="project_type_alias",
        ),
    ]
