from ord_betterproto import *

reaction_mojito = Reaction(
    reaction_id="mojito",
    identifiers=[ReactionIdentifier(type=ReactionIdentifierReactionIdentifierType.NAME, value="making mojito"), ],
    inputs=dict(
        rum=ReactionInput(
            components=[
                Compound(
                    identifiers=[CompoundIdentifier(CompoundIdentifierCompoundIdentifierType.NAME, "Rum")],
                    amount=Amount(volume=Volume(120., units=VolumeVolumeUnit.MILLILITER)),
                    reaction_role=ReactionRoleReactionRoleType.REACTANT,
                    is_limiting=True
                ),
            ],
            addition_order=1,
        ),
        lime=ReactionInput(
            components=[
                Compound(
                    identifiers=[CompoundIdentifier(CompoundIdentifierCompoundIdentifierType.NAME, "lime juice")],
                    amount=Amount(volume=Volume(10., units=VolumeVolumeUnit.MILLILITER)),
                    reaction_role=ReactionRoleReactionRoleType.REAGENT,
                    is_limiting=False
                ),
            ],
            addition_order=2,
        ),
        soda=ReactionInput(
            components=[
                Compound(
                    identifiers=[CompoundIdentifier(CompoundIdentifierCompoundIdentifierType.NAME, "soda")],
                    amount=Amount(volume=Volume(10., units=VolumeVolumeUnit.MILLILITER)),
                    reaction_role=ReactionRoleReactionRoleType.REAGENT,
                    is_limiting=False
                ),
                Compound(
                    identifiers=[
                        CompoundIdentifier(CompoundIdentifierCompoundIdentifierType.NAME, "sugar"),
                        CompoundIdentifier(CompoundIdentifierCompoundIdentifierType.SMILES, "OCC1OC(O)C(O)C(O)C1O")
                    ],
                    amount=Amount(mass=Mass(20., units=MassMassUnit.GRAM)),
                    reaction_role=ReactionRoleReactionRoleType.REAGENT,
                    is_limiting=False
                ),
            ],
            addition_order=3,
        ),
    ),
    setup=ReactionSetup(
        vessel=Vessel(
            type=VesselVesselType.VIAL,
            preparations=[VesselPreparation(VesselPreparationVesselPreparationType.PURGED, details="air")]
        ),
        is_automated=False,
    ),
    conditions=ReactionConditions(
        temperature=TemperatureConditions(
            control=TemperatureConditionsTemperatureControl(
                TemperatureConditionsTemperatureControlTemperatureControlType.AMBIENT
            ),
            setpoint=Temperature(value=50, units=TemperatureTemperatureUnit.CELSIUS)),
    ),
    outcomes=[
        ReactionOutcome(
            reaction_time=Time(3, units=TimeTimeUnit.MINUTE),
            analyses={
                "taste": Analysis(AnalysisAnalysisType.CUSTOM, details="tasted by me", instrument_manufacturer="my mom")
            }
        ),
        ReactionOutcome(
            products=[
                ProductCompound(
                    identifiers=[
                        CompoundIdentifier(type=CompoundIdentifierCompoundIdentifierType.NAME, value="Very good mojito")
                    ],
                    is_desired_product=True,
                )
            ]
        )
    ]
)
if __name__ == '__main__':
    from google.protobuf.json_format import Parse
    from ord_schema.proto import reaction_pb2
    from ord_schema.validations import validate_reaction
    from ord_betterproto.ord_tree import message_to_tree
    from utils.tree_related import write_dot

    with open("mojito.json", "w") as f:
        f.write(reaction_mojito.to_json())

    write_dot(message_to_tree(reaction_mojito), "mojito.dot")

    # convert back to official message
    old_mojito = Parse(reaction_mojito.to_json(), reaction_pb2.Reaction())
    validate_reaction(old_mojito)