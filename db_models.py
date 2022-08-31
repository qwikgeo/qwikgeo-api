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

class Group(models.Model):
    name = fields.CharField(50)
    users = fields.JSONField()

class Table(models.Model):

    username = fields.CharField(50)
    table_id = fields.CharField(max_length=50, unique=True, indexable=True)
    title = fields.CharField(max_length=500, indexable=True)
    created_time = fields.DatetimeField(auto_now_add=True)
    modified_time = fields.DatetimeField(auto_now=True)
    tags = fields.JSONField()
    description = fields.TextField()
    read_access_list = fields.JSONField()
    write_access_list = fields.JSONField()
    views = fields.IntField()
    searchable = fields.BooleanField(default=True)
    geometry_type = fields.CharField(max_length=50)

Table_Pydantic = pydantic_model_creator(Table, name="Table")
