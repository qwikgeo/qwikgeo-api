"""QwikGeo API - Database Models"""

from passlib.hash import bcrypt
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise import Tortoise

class User(models.Model):
    """Model for user in database"""

    id = fields.IntField(pk=True)
    username = fields.CharField(500, unique=True)
    password_hash = fields.CharField(max_length=300, null=True)
    first_name = fields.CharField(max_length=300)
    last_name = fields.CharField(max_length=300)
    photo_url = fields.CharField(max_length=1000, null=True)
    email = fields.CharField(max_length=500)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)

    def verify_password(self, password: str):
        """Method used to verify password is correct against hash in database."""

        return bcrypt.verify(password, self.password_hash)

class Group(models.Model):
    """Model for group in database"""

    group_id = fields.UUIDField(unique=True, indexable=True, pk=True)
    name = fields.CharField(500, unique=True)
    users = fields.ReverseRelation["GroupUser"]
    admins = fields.ReverseRelation["GroupAdmin"]

class GroupUser(models.Model):
    """Model for group_user in database"""

    id = fields.IntField(pk=True)
    group_id: fields.ForeignKeyRelation[Group] = fields.ForeignKeyField(
        "models.Group", related_name="group_users", to_field="group_id",
        on_delete='CASCADE'
    )
    username = fields.CharField(500)

class GroupAdmin(models.Model):
    """Model for group_user in database"""

    id = fields.IntField(pk=True)
    group_id: fields.ForeignKeyRelation[Group] = fields.ForeignKeyField(
        "models.Group", related_name="group_admins", to_field="group_id",
        on_delete='CASCADE'
    )
    username = fields.CharField(500)


class Item(models.Model):
    """Model for item in database"""

    username: fields.ForeignKeyField(
        "models.User", related_name="items", to_field="username",
        on_delete='CASCADE'
    )
    portal_id = fields.UUIDField(unique=True, indexable=True, pk=True)
    title = fields.CharField(max_length=500, indexable=True)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)
    tags = fields.JSONField()
    description = fields.TextField()
    read_access_list = fields.ReverseRelation["ItemReadAccessList"]
    write_access_list = fields.ReverseRelation["ItemWriteAccessList"]
    views = fields.IntField()
    searchable = fields.BooleanField(default=True)
    item_type = fields.TextField()
    url = fields.TextField(null=True)

class ItemReadAccessList(models.Model):
    """Model for item_read_access_list in database"""

    portal_id: fields.ForeignKeyRelation[Item] = fields.ForeignKeyField(
        "models.Item", related_name="item_read_access_list", to_field="portal_id",
        on_delete='CASCADE'
    )
    name = fields.CharField(500)

class ItemWriteAccessList(models.Model):
    """Model for item_read_access_list in database"""

    portal_id: fields.ForeignKeyRelation[Item] = fields.ForeignKeyField(
        "models.Item", related_name="item_write_access_list", to_field="portal_id",
        on_delete='CASCADE'
    )
    name = fields.CharField(500)

class Table(models.Model):
    """Model for table in database"""

    username: fields.ForeignKeyField(
        "models.User", related_name="tables", to_field="username",
        on_delete='CASCADE'
    )
    portal_id: fields.ForeignKeyRelation[Item] = fields.ForeignKeyField(
        "models.Item", related_name="table", to_field="portal_id",
        on_delete='CASCADE'
    )
    table_id = fields.CharField(50)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)

class Map(models.Model):
    """Model for map in database"""

    username: fields.ForeignKeyField(
        "models.User", related_name="maps", to_field="username",
        on_delete='CASCADE'
    )
    portal_id: fields.ForeignKeyRelation[Item] = fields.ForeignKeyField(
        "models.Item", related_name="map", to_field="portal_id",
        on_delete='CASCADE'
    )
    map_id = fields.UUIDField(unique=True, indexable=True, pk=True)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)
    pitch = fields.IntField(default=0)
    bearing = fields.IntField(default=0)
    basemap = fields.CharField(max_length=50)
    bounding_box = fields.JSONField()
    layers: fields.ReverseRelation["Layer"]

class Layer(models.Model):
    """Model for layer in database"""

    gid = fields.IntField(pk=True)
    id = fields.CharField(max_length=1000)
    title = fields.CharField(max_length=500)
    description = fields.CharField(max_length=500)
    map_type = fields.CharField(max_length=50)
    mapbox_name = fields.CharField(max_length=50)
    geometry_type = fields.CharField(max_length=50)
    style = fields.JSONField()
    paint = fields.JSONField()
    layout = fields.JSONField()
    fill_paint = fields.JSONField()
    border_paint = fields.JSONField()
    bounding_box = fields.JSONField()

    map: fields.ForeignKeyRelation[Map] = fields.ForeignKeyField(
        "models.Map", related_name="layers", to_field="map_id",
        on_delete='CASCADE'
    )


Tortoise.init_models(["qwikgeo_api.db_models"], "models")

Group_Pydantic = pydantic_model_creator(Group, name="Group")
Table_Pydantic = pydantic_model_creator(Table, name="Table")
Map_Pydantic = pydantic_model_creator(Map, name="Map")
Item_Pydantic = pydantic_model_creator(Item, name="Item")
ItemReadAccessListPydantic = pydantic_model_creator(ItemReadAccessList, name="ItemReadAccessList")
