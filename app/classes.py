from typing import Union

from matching.factory import ParticipantFactory
from matching.mentee import Mentee
from matching.mentor import Mentor
from matching.person import Person


class CSPerson(Person):
    """
    This interface contains methods for mapping CS-specific grades, as well as the specific fields in the CS spreadsheet
    """

    grade_mapping = [
        "AA",
        "AO",
        "EO",
        "HEO",
        "SEO",
        "Grade 7",
        "Grade 6",
        "SCS1",
        "SCS2",
        "SCS3",
        "SCS4",
    ]

    def __init__(self, **kwargs):
        self.biography = kwargs.get("biography")
        self.both = True if kwargs.get("both mentor and mentee") == "yes" else False
        self.map_input_to_model(kwargs)
        super(CSPerson, self).__init__(**kwargs)

    @classmethod
    def str_grade_to_val(cls, grade: str):
        return cls.grade_mapping.index(grade)

    @classmethod
    def val_grade_to_str(cls, grade: int):
        return cls.grade_mapping[grade]

    @staticmethod
    def map_input_to_model(data: dict):
        data["role"] = data["job title"]
        data["email"] = data["email address"]
        data["grade"] = CSPerson.str_grade_to_val(data.get("grade", ""))

    def map_model_to_output(self, data: dict):
        data["job title"] = data.pop("role")
        data["email address"] = data.pop("email")
        data["grade"] = self.val_grade_to_str(int(data.get("grade", "0")))
        data["biography"] = self.biography
        data["both mentor and mentee"] = "yes" if self.both else "no"

    def to_dict_for_output(self, depth=1) -> dict:
        return {
            "first name": self.first_name,
            "last name": self.last_name,
            "email address": self.email,
            "number of matches": len(self.connections),
            "mentor only": "no",
            "mentee only": "no",
            "both mentor and mentee": "yes" if self.both else "no",
            **{
                f"match {i} biography": match.biography
                for i, match in enumerate(self.connections)
            },
            "match details": "\n".join([match.biography for match in self.connections])
            if self.connections
            else None,
        }


class CSMentee(CSPerson, Mentee):
    def __init__(self, **kwargs):
        self.characteristic = kwargs.get("identity to match")
        super(CSMentee, self).__init__(**kwargs)
        self.target_profession = kwargs.get("profession")

    def core_to_dict(self) -> dict[str, dict[str, Union[str, list]]]:
        core = super(CSMentee, self).core_to_dict()
        data = core[self.class_name()]
        self.map_model_to_output(data)
        data["identity to match"] = self.characteristic
        data["profession"] = self.target_profession
        return core

    def to_dict_for_output(self, depth=1) -> dict:
        output = super(CSMentee, self).to_dict_for_output()
        if not self.both:
            output["mentee only"] = "yes"
        return output


class CSMentor(CSPerson, Mentor):
    def __init__(self, **kwargs):
        self.characteristics: list[str] = kwargs.get("characteristics", "").split(", ")
        kwargs["current profession"] = kwargs["profession"]
        super(CSMentor, self).__init__(**kwargs)

    def core_to_dict(self) -> dict[str, dict[str, Union[str, list]]]:
        core = super(CSMentor, self).core_to_dict()
        data = core[self.class_name()]
        self.map_model_to_output(data)
        data["characteristics"] = ", ".join(self.characteristics)
        data["profession"] = self.current_profession
        return core

    def to_dict_for_output(self, depth=1) -> dict:
        output = super(CSMentor, self).to_dict_for_output()
        if not self.both:
            output["mentor only"] = "yes"
        return output


class CSParticipantFactory(ParticipantFactory):
    participant_types = {"csmentee": CSMentee, "csmentor": CSMentor}
