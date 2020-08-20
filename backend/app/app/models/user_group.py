from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base, Default

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .permission import Permission  # noqa


class UserGroupUserRel(Base, Default):
    """Many-to-many association table for UserGroups and Users.
    """

    user_group_id = Column(Integer, ForeignKey("user_group.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)


class UserGroupPermissionRel(Base, Default):
    """Many-to-many association table for Permissions *in* UserGroups
    """
    user_group_id = Column(Integer, ForeignKey("user_group.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permission.id"), primary_key=True)
    enabled = Column(Boolean, default=False)


class UserGroup(Base, Default):
    """Class representing UserGroup objects

    UserGroups represent the relational 'glue' between Users and
    access to perform CRUD operations on resources such as Nodes, 
    Interfaces, or even UserGroups. UserGroups are connected to
    Users through the UserGroupUserRel relational table, to a parent
    Node through a direct foreign key relationship, and to Permissions 
    in two distinct ways. 

    ## Users

    A User is said to *belong* to a UserGroup if the User is associated
    to the UserGroup through a UserGroupUserRel relationship. 
    Permissions associated with that UserGroup are available to those
    Users that belong to the UserGroup.

    ## Nodes

    Each UserGroup is associated with a Node that is considered to be
    the *parent* Node for that UserGroup. A UserGroup may have 
    Permissions *in* it (more on that later) that are no higher in the
    organizational hierarchy than the parent Node. The UserGroup table
    contains the following fields:

    - id: primary key
    - node_id: primary key for the UserGroup's parent Node
    - created_at: timestamp for creation datetime
    - updated_at: timestamp for update datetime
    - created_by_id: User id for the user who created the node record
    - updated_by_id: User id for the user who last updated the node record
    - name: string representing the name for this UserGroup

    ## Permissions

    For Permissions *in* a UserGroup, that is, the Permissions
    granted to Users in the UserGroup, the relationship is 
    mediated through the UserGroupPermissionRel table.

    For Permissions *for* a UserGroup, that is, the Permissions to 
    perform CRUD operations on the UserGroup itself that may or may not
    be *in* the UserGroup, the relationship is mediated through the
    Permission table using the UserGroupPermission child object.

    To clarify the distinction, Permissions *in* a UserGroup grant the
    Users associated with that UserGroup permissions to perform CRUD 
    operations on resources, while Permissions *for* a UserGroup are 
    used to grant users permission to perform CRUD operations on that
    UserGroup and are not necessarily also *in* the UserGroup. A 
    Permission may be both *in* and *for* a UserGroup, in which case 
    Users in the UserGroup will have rights to perform CRUD operations
    on the UserGroup itself and could lead to Permission escalation.
    """

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("node.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    created_by_id = Column(
        Integer,
        ForeignKey("user.id", name=f"fk_user_group_created_by_id", use_alter=True),
        nullable=False,
    )
    created_by_user = relationship(
        "User", back_populates="user_groups_created", foreign_keys=[created_by_id]
    )
    updated_by_id = Column(
        Integer,
        ForeignKey("user.id", name=f"fk_user_group_updated_by_id", use_alter=True),
        nullable=False,
    )
    updated_by_user = relationship(
        "User", back_populates="user_groups_updated", foreign_keys=[updated_by_id]
    )
    name = Column(String(256), nullable=False, unique=True)

    users = relationship(
        "User", secondary=lambda: UserGroupUserRel.__table__, backref="user_groups"
    )
    permissions_in = relationship("UserGroupPermissionRel", cascade="all, delete")

    permissions_for = relationship(
        "UserGroupPermission",
        primaryjoin="and_(UserGroup.id==UserGroupPermission.resource_id, UserGroupPermission.resource_type=='user_group')",
        foreign_keys="UserGroupPermission.resource_id",
        cascade="all, delete",
    )
