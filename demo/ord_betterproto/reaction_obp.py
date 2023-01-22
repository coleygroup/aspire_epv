from ord_betterproto import *

reaction = Reaction()
reaction.reaction_id = "Making N,N-Dibenzyl-O-pivaloylhydroxylamine"
# 500-mL single-necked flask
reaction.setup.vessel = Vessel(
    type=VesselVesselType.ROUND_BOTTOM_FLASK,
    details="single-necked",
    material=VesselMaterial(VesselMaterialVesselMaterialType.GLASS),
    volume=Volume(value=500., units=VolumeVolumeUnit.MILLILITER)
)
reaction.setup.vessel.preparations = [
    VesselPreparation(VesselPreparationVesselPreparationType.OVEN_DRIED),
    VesselPreparation(VesselPreparationVesselPreparationType.PURGED, details="with nitrogen"),
]
reaction.setup.vessel.attachments = [
    VesselAttachment(VesselAttachmentVesselAttachmentType.SEPTUM, details="rubber")
]
reaction.setup.is_automated = False
reaction.setup.environment.type = ReactionSetupReactionEnvironmentReactionEnvironmentType.FUME_HOOD

# Three components charged to flask initially, in order
reaction.inputs = dict()
reaction.inputs["N,N-dibenzylhydroxylamine"] = ReactionInput()
reaction.inputs["N,N-dibenzylhydroxylamine"].addition_order = 1
reaction.inputs["N,N-dibenzylhydroxylamine"].components.append(
    Compound(
        identifiers=[
            CompoundIdentifier(
                CompoundIdentifierCompoundIdentifierType.SMILES,
                value="C1=CC=C(C=C1)CN(CC2=CC=CC=C2)O",
            ),
            CompoundIdentifier(
                CompoundIdentifierCompoundIdentifierType.NAME,
                value="N,N-dibenzylhydroxylamine",
            ),
        ],
        preparations=[
            CompoundPreparation(
                CompoundPreparationCompoundPreparationType.CUSTOM,
                details="a few colored or darker crystals, which were present in trace"
                        " amounts, were discarded using standard tweezers",
            ),
        ],
        source=CompoundSource(vendor="TCI America"),
        reaction_role=ReactionRoleReactionRoleType.REACTANT,
        amount=Amount(mass=Mass(value=21.3, units=MassMassUnit.GRAM)),
        is_limiting=True
    )
)

reaction.inputs["4-dimethyl-aminopyridine"] = ReactionInput()
reaction.inputs["4-dimethyl-aminopyridine"].addition_order = 2
reaction.inputs["4-dimethyl-aminopyridine"].components.append(
    Compound(
        identifiers=[
            CompoundIdentifier(
                CompoundIdentifierCompoundIdentifierType.SMILES,
                value="n1ccc(N(C)C)cc1",
            ),
            CompoundIdentifier(
                CompoundIdentifierCompoundIdentifierType.NAME,
                value="4-dimethyl-aminopyridine",
            ),
        ],
        preparations=[
            CompoundPreparation(
                CompoundPreparationCompoundPreparationType.NONE,
                details="used as received",
            ),
        ],
        source=CompoundSource(vendor="Sigma Aldrich"),
        reaction_role=ReactionRoleReactionRoleType.REAGENT,
        amount=Amount(mass=Mass(value=12.8, units=MassMassUnit.GRAM)),
    )
)

reaction.inputs["dichloromethane"] = ReactionInput()
reaction.inputs["dichloromethane"].addition_order = 3
reaction.inputs["dichloromethane"].components.append(
    Compound(
        identifiers=[
            CompoundIdentifier(
                CompoundIdentifierCompoundIdentifierType.SMILES,
                value="C(Cl)Cl",
            ),
            CompoundIdentifier(
                CompoundIdentifierCompoundIdentifierType.NAME,
                value="dichloromethane",
            ),
        ],
        preparations=[
            CompoundPreparation(
                CompoundPreparationCompoundPreparationType.DRIED,
                details="purified by passage under argon pressure through two packed "
                        "columns of neutral alumina and copper(II) oxide",
            ),
        ],
        source=CompoundSource(vendor="J. T. Baker"),
        reaction_role=ReactionRoleReactionRoleType.SOLVENT,
        amount=Amount(volume=Volume(250., units=VolumeVolumeUnit.MILLILITER)),
    )
)
reaction.outcomes = [
    ReactionOutcome(reaction_time=Time(6., units=TimeTimeUnit.HOUR))
]

with open("reaction_obp.json", "w") as f:
    f.write(reaction.to_json(indent=2))
