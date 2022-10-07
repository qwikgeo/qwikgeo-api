from passlib.hash import bcrypt
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise import Tortoise

class User(models.Model):

    id = fields.IntField(pk=True)
    username = fields.CharField(500, unique=True)
    password_hash = fields.CharField(max_length=300, null=True)
    first_name = fields.CharField(max_length=300)
    last_name = fields.CharField(max_length=300)
    photo_url = fields.CharField(max_length=1000, null=True)
    email = fields.CharField(max_length=500)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class Group(models.Model):

    group_id = fields.UUIDField(unique=True, indexable=True, pk=True)
    name = fields.CharField(500, unique=True)
    users = fields.ReverseRelation["GroupUser"]

class GroupUser(models.Model):

    id = fields.IntField(pk=True)
    group_id: fields.ForeignKeyRelation[Group] = fields.ForeignKeyField(
        "models.Group", related_name="group_users", to_field="group_id"
    )
    username = fields.CharField(500)

class Item(models.Model):

    username: fields.ForeignKeyField(
        "models.User", related_name="items", to_field="username"
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

    portal_id: fields.ForeignKeyRelation[Item] = fields.ForeignKeyField(
        "models.Item", related_name="item_read_access_list", to_field="portal_id"
    )
    name = fields.CharField(500)

class ItemWriteAccessList(models.Model):

    portal_id: fields.ForeignKeyRelation[Item] = fields.ForeignKeyField(
        "models.Item", related_name="item_write_access_list", to_field="portal_id"
    )
    name = fields.CharField(500)

class Table(models.Model):

    username: fields.ForeignKeyField(
        "models.User", related_name="tables", to_field="username"
    )
    portal_id: fields.ForeignKeyRelation[Item] = fields.ForeignKeyField(
        "models.Item", related_name="table", to_field="portal_id"
    )
    table_id = fields.CharField(50)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)

Tortoise.init_models(["db_models"], "models")

Table_Pydantic = pydantic_model_creator(Table, name="Table")
Item_Pydantic = pydantic_model_creator(Item, name="Item")