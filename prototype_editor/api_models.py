from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

example_prototype_node_link_data = '{"directed": true, "multigraph": false, "graph": {}, "nodes": [{"mot_element_id": 220, "mot_can_edit": false, "mot_state": "PT_PRESET", "mot_value": null, "mtt_element_name": "<ROOT>|workups|<ListIndex>", "mot_class_string": "ord_betterproto.ReactionWorkup", "id": 220}, {"mot_element_id": 221, "mot_can_edit": true, "mot_state": "PT_PRESET", "mot_value": 6, "mtt_element_name": "<ROOT>|workups|<ListIndex>|type", "mot_class_string": "ord_betterproto.ReactionWorkupType", "id": 221}, {"mot_element_id": 222, "mot_can_edit": true, "mot_state": "PT_PRESET", "mot_value": "3 x 50 mL DCM extraction in 1 L separatory funnel", "mtt_element_name": "<ROOT>|workups|<ListIndex>|details", "mot_class_string": "builtins.str", "id": 222}, {"mot_element_id": 223, "mot_can_edit": true, "mot_state": "PT_PLACEHOLDER", "mot_value": "organic", "mtt_element_name": "<ROOT>|workups|<ListIndex>|keep_phase", "mot_class_string": "builtins.str", "id": 223}], "links": [{"mot_element_id": [220, 221], "mot_can_edit": false, "mot_state": "PT_PRESET", "mot_value": "type", "mtt_element_name": ["<ROOT>|workups|<ListIndex>", "<ROOT>|workups|<ListIndex>|type"], "mot_class_string": ["ord_betterproto.ReactionWorkup", "ord_betterproto.ReactionWorkupType"], "source": 220, "target": 221}, {"mot_element_id": [220, 222], "mot_can_edit": false, "mot_state": "PT_PRESET", "mot_value": "details", "mtt_element_name": ["<ROOT>|workups|<ListIndex>", "<ROOT>|workups|<ListIndex>|details"], "mot_class_string": ["ord_betterproto.ReactionWorkup", "builtins.str"], "source": 220, "target": 222}, {"mot_element_id": [220, 223], "mot_can_edit": false, "mot_state": "PT_PRESET", "mot_value": "keep_phase", "mtt_element_name": ["<ROOT>|workups|<ListIndex>", "<ROOT>|workups|<ListIndex>|keep_phase"], "mot_class_string": ["ord_betterproto.ReactionWorkup", "builtins.str"], "source": 220, "target": 223}]}'
example_prototype_node_link_data = json.loads(example_prototype_node_link_data)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class OrdPrototypeModel(BaseModel):
    # mongodb id
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    # user defined name
    name: str = Field(...)

    # current version
    version: str = Field(None)

    # from which version this prototype is created, i.e. its parent
    from_version: Optional[str] = Field(None, description="First version")

    # actual tree data from nx.node_link_data
    node_link_data: dict = Field(...)

    # what kine of prototype?
    root_message_type: str = Field(None)

    # timestamp
    time_modified: datetime = Field(None)
    time_created: datetime = Field(None)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Suzuki Reaction",
                "version": "draft apple",
                "from_version": "draft banana",
                "node_link_data": example_prototype_node_link_data,
                "root_message_type": "ReactionWorkup",
                "time_modified": datetime.now(),
                "time_created": datetime.now(),
            }
        }


class UpdateOrdPrototypeModel(BaseModel):
    name: Optional[str]
    node_link_data: Optional[dict]
    root_message_type: Optional[str]
    time_modified: Optional[datetime]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Suzuki Reaction",
                "node_link_data": example_prototype_node_link_data,
                "root_message_type": "ReactionWorkup",
                "time_modified": datetime.now(),
            }
        }

