from passlib.hash import bcrypt
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)
    name = fields.CharField(max_length=50, null=True)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class Map(models.Model):
    username: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="map", to_field="username"
    )
    # updated_username: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
    #     "models.Users", related_name="map", to_field="username"
    # )
    map_id = fields.UUIDField()
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)

Map_Pydantic = pydantic_model_creator(Map, name="User")

class Table(models.Model):
    username: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="table", to_field="username"
    )
    table_id = fields.CharField(max_length=50, unique=True)
    title = fields.CharField(max_length=500)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)
    tags = fields.JSONField()
    description = fields.TextField()
    read_access_list = fields.JSONField()
    write_access_list = fields.JSONField()
    notification_access_list = fields.JSONField()
    views = fields.IntField()
    searchable = fields.BooleanField(default=True)
    geometry_type = fields.CharField(max_length=50)

Table_Pydantic = pydantic_model_creator(Table, name="User")