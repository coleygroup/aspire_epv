from google.protobuf.json_format import MessageToJson
from ord_schema import message_helpers
from ord_schema.proto import reaction_pb2
from ord_schema.units import UnitResolver

reaction = reaction_pb2.Reaction()
reaction.reaction_id = "Making N,N-Dibenzyl-O-pivaloylhydroxylamine"
unit_resolver = UnitResolver()
# 500-mL single-necked flask
reaction.setup.vessel.CopyFrom(
    reaction_pb2.Vessel(
        type="ROUND_BOTTOM_FLASK",
        details="single-necked",
        material=dict(type="GLASS"),
        volume=unit_resolver.resolve("500 mL"),
    )
)
reaction.setup.vessel.preparations.add(type="OVEN_DRIED")
reaction.setup.vessel.preparations.add(type="PURGED", details="with nitrogen")
reaction.setup.vessel.attachments.add(type="SEPTUM", details="rubber")
reaction.setup.is_automated = False
reaction.setup.environment.type = reaction_pb2.ReactionSetup.ReactionEnvironment.FUME_HOOD

# Three components charged to flask initially, in order
reaction.inputs["N,N-dibenzylhydroxylamine"].addition_order = 1
reaction.inputs["N,N-dibenzylhydroxylamine"].components.add().CopyFrom(
    message_helpers.build_compound(
        smiles="C1=CC=C(C=C1)CN(CC2=CC=CC=C2)O",
        name="N,N-dibenzylhydroxylamine",
        prep="custom",
        prep_details="a few colored or darker crystals, which were present in trace"
                     " amounts, were discarded using standard tweezers",
        vendor="TCI America",
        role="reactant",
        amount="21.3 g",
        is_limiting=True,
    )
)
reaction.inputs["4-dimethyl-aminopyridine"].addition_order = 2
reaction.inputs["4-dimethyl-aminopyridine"].components.add().CopyFrom(
    message_helpers.build_compound(
        smiles="n1ccc(N(C)C)cc1",
        name="4-dimethyl-aminopyridine",
        prep="none",
        prep_details="used as received",
        vendor="Sigma Aldrich",
        role="reagent",
        amount="12.8 g",
    )
)
reaction.inputs["dichloromethane"].addition_order = 3
reaction.inputs["dichloromethane"].components.add().CopyFrom(
    message_helpers.build_compound(
        smiles="C(Cl)Cl",
        name="dichloromethane",
        prep="dried",
        prep_details="purified by passage under argon pressure through two packed "
                     "columns of neutral alumina and copper(II) oxide",
        vendor="J. T. Baker",
        role="solvent",
        amount="250 ml",
    )
)

outcome = reaction.outcomes.add()
outcome.reaction_time.CopyFrom(unit_resolver.resolve("6 h"))

with open("reaction_ord.json", "w") as f:
    f.write(MessageToJson(reaction))
