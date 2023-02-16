from datetime import datetime

from ord_schema import message_helpers
from ord_schema import validations
from ord_schema.proto import reaction_pb2
from ord_schema.units import UnitResolver

from ord_tree.utils import write_file

unit_resolver = UnitResolver()
reaction = reaction_pb2.Reaction()
reaction.reaction_id = "Making N,N-Dibenzyl-O-pivaloylhydroxylamine"

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

# Nothing in the schema can capture the 5 minutes stirring at RT? Then 20 min
# of cooling! Need to use catch-all
reaction.conditions.conditions_are_dynamic = True
reaction.conditions.details = """reaction started in ice bath before addition of
pivaloyl chloride, then allowed to warm to 23 C, then stirred for '
an additional 6 hours at RT (23 degC)"""

reaction.inputs["pivaloyl chloride"].addition_order = 4
reaction.inputs["pivaloyl chloride"].addition_speed.type = reaction_pb2.ReactionInput.AdditionSpeed.DROPWISE
reaction.inputs["pivaloyl chloride"].addition_duration.CopyFrom(unit_resolver.resolve("5 min"))
reaction.inputs["pivaloyl chloride"].components.add().CopyFrom(
    message_helpers.build_compound(
        smiles="CC(C)(C)C(=O)Cl",
        name="pivaloyl chloride",
        prep="none",
        prep_details="used as received",
        vendor="Alfa Aesar",
        role="reactant",
        amount="12.9 ml",
    )
)
reaction.inputs["pivaloyl chloride"].addition_device.type = reaction_pb2.ReactionInput.AdditionDevice.SYRINGE
reaction.inputs["pivaloyl chloride"].addition_device.details = "plastic 30-mL syringe"

# System described as a suspension
reaction.notes.is_heterogeneous = True

# Connected to nitrogen manifold; flask sealed with rubber septum
p_conds = reaction.conditions.pressure
p_conds.control.type = p_conds.PressureControl.SLIGHT_POSITIVE
p_conds.control.details = "sealed with rubber septum, pierced with needle connected to manifold"
p_conds.atmosphere.type = p_conds.Atmosphere.NITROGEN
p_conds.atmosphere.details = "dry nitrogen"

# 4 cm Teflon-coated magnetic stir bar, speed unknown
s_conds = reaction.conditions.stirring
s_conds.type = s_conds.STIR_BAR

# Temperature schedule is rather complicated; this assumes that the reaction
# takes place in the 6 hours at room temperautre after warming up...but we should
# capture that it starts on ice!
t_conds = reaction.conditions.temperature
t_conds.setpoint.CopyFrom(reaction_pb2.Temperature(units="CELSIUS", value=0))
t_conds.control.type = t_conds.TemperatureControl.ICE_BATH
t_conds.control.details = """reaction started in ice bath before addition of pivaloyl 
chloride, then allowed to warm to 23 C, then stirred for additional 6 hours at 
RT (23 degC)"""

# Workup step 1 - add 50 mL saturated aqueous ammonium chloride
workup = reaction.workups.add()
workup.type = workup.ADDITION
workup.input.components.add().CopyFrom(message_helpers.build_compound(smiles="O", name="water", amount="50 ml"))
workup.input.components[0].amount.volume_includes_solutes = True
workup.input.components.add().CopyFrom(
    message_helpers.build_compound(
        smiles="[NH4+].[Cl-]",
        name="ammonium chloride",
        amount="19.15 g",  # estimated from solubility of 383.0 g/L @ 25 degC
    )
)

# Workup step 2 - use 3 x 50 mL DCM to extract product into organic phase
workup = reaction.workups.add()
workup.type = workup.ADDITION
workup.input.components.add().CopyFrom(message_helpers.build_compound(smiles="C(Cl)Cl", name="DCM", amount="50 ml"))
workup = reaction.workups.add()
workup.type = workup.ADDITION
workup.input.components.add().CopyFrom(message_helpers.build_compound(smiles="C(Cl)Cl", name="DCM", amount="50 ml"))
workup = reaction.workups.add()
workup.type = workup.ADDITION
workup.input.components.add().CopyFrom(message_helpers.build_compound(smiles="C(Cl)Cl", name="DCM", amount="50 ml"))
workup = reaction.workups.add()
workup.type = workup.EXTRACTION
workup.details = "3 x 50 mL DCM extraction in 1 L separatory funnel"
workup.keep_phase = "organic"

# Workup step 3 - rinse with 200 mL DI water
workup = reaction.workups.add()
workup.type = workup.WASH
workup.input.components.add().CopyFrom(message_helpers.build_compound(smiles="O", name="water", amount="200 ml"))

# Workup step 4 - concentrate using rotovap (30 C, 80 mmHg)
workup = reaction.workups.add()
workup.type = workup.CONCENTRATION
workup.details = "rotary evaporator (30 degC, 80 mmHg)"

# Workup step 5 - dissolve heterogeneous mixture in DCM
workup = reaction.workups.add()
workup.type = workup.DISSOLUTION
workup.input.components.add().CopyFrom(message_helpers.build_compound(smiles="C(Cl)Cl", name="DCM", amount="50 ml"))

# Workup step 6 - pass through alumina column and collect fractions
workup = reaction.workups.add()
workup.type = workup.FLASH_CHROMATOGRAPHY
workup.details = """Aluminum oxide (neutral, powder, reagent-grade) was 
purchased from J.T. Baker. The crude reaction mixture is suspended in 
dichloromethane (50 mL) and is loaded onto a column, with interior diameter of 
roughly 2 inches, packed with alumina (100 g) and wetted with hexanes. 
dichloromethane is used as the eluent, and fractions are collected in Erlenmeyer
 flasks (50 mL each). The desired product typically elutes in fractions 2 
 through 25. The fractions that contain the desired product are combined"""

# Workup step 7 - remove solvent with rotovap and dry under vacuum
workup = reaction.workups.add()
workup.type = workup.CONCENTRATION
workup.details = "rotary evaporator (30 degC, 80 mmHg)"
workup = reaction.workups.add()
workup.type = workup.DRY_IN_VACUUM

## Product and characterization
outcome = reaction.outcomes.add()
outcome.reaction_time.CopyFrom(unit_resolver.resolve("6 h"))
analysis = reaction_pb2.Analysis()  # for handy enum reference

outcome.analyses["isolated_weight"].type = analysis.WEIGHT
outcome.analyses["isolated_weight"].is_of_isolated_species = True
outcome.analyses["isolated_weight"].details = "27.5-28.0 g recovered after workup"

outcome.analyses["1H NMR"].type = analysis.NMR_1H
outcome.analyses["1H NMR"].is_of_isolated_species = True
outcome.analyses["1H NMR"].details = "400 MHz, CDCl3"
outcome.analyses["1H NMR"].data[
    "peaks"
].string_value = r"0.92 (s, 9H), 4.06 (s, 4H), 7.23 - 7.34 (m, 6H), 7.40 (d, J = 7.1 Hz, 4H)"
outcome.analyses["1H NMR"].data["peaks"].description = "List of peaks"

outcome.analyses["13C NMR"].type = analysis.NMR_13C
outcome.analyses["13C NMR"].is_of_isolated_species = True
outcome.analyses["13C NMR"].details = "101 MHz, CDCl3"
outcome.analyses["13C NMR"].data["peaks"].string_value = r"27.1, 38.4, 62.4, 127.7, 128.3, 129.6, 136.2, 176.3"
outcome.analyses["13C NMR"].data["peaks"].description = "List of peaks"

outcome.analyses["thin film IR"].type = analysis.IR
outcome.analyses["thin film IR"].is_of_isolated_species = True
outcome.analyses["thin film IR"].details = "neat film, NaCl"
outcome.analyses["thin film IR"].data[
    "peaks"
].string_value = r"3064, 3031, 2973, 2932, 2906, 2872, 1751, 1496, 1479, 1456, 1273, 1116, 1029, 738, 698"
outcome.analyses["thin film IR"].data["peaks"].description = "List of peaks [cm-1]"

outcome.analyses["HRMS"].type = analysis.HRMS
outcome.analyses["HRMS"].is_of_isolated_species = True
outcome.analyses["HRMS"].details = "ESI-TOF"
outcome.analyses["HRMS"].data["expected"].float_value = 298.1802
outcome.analyses["HRMS"].data["expected"].description = "Expected m/z"
outcome.analyses["HRMS"].data["found"].float_value = 298.1794
outcome.analyses["HRMS"].data["found"].description = "Observed m/z"

outcome.analyses["quantitative NMR"].type = analysis.NMR_1H
outcome.analyses["quantitative NMR"].is_of_isolated_species = True
outcome.analyses[
    "quantitative NMR"
].details = "Quantitative NMR using 1,1,2,2-tetrachloroethane (>98%, purchased from Alfa Aesar) in CDCl3"

# A single product was desired and characterized
product = outcome.products.add()
product.identifiers.add(type="SMILES", value="O=C(C(C)(C)C)ON(CC1=CC=CC=C1)CC2=CC=CC=C2")
product.identifiers.add(type="NAME", value="N,N-Dibenzyl-O-pivaloylhydroxylamine")
product.is_desired_product = True
product.reaction_role = reaction_pb2.ReactionRole.PRODUCT

# Define which analyses were used for which aspects of characterization
product.measurements.add(type="IDENTITY", analysis_key="1H NMR")
product.measurements.add(type="IDENTITY", analysis_key="13C NMR")
product.measurements.add(type="IDENTITY", analysis_key="HRMS")
product.measurements.add(type="IDENTITY", analysis_key="thin film IR")
product.measurements.add(type="YIELD", analysis_key="isolated_weight", percentage=dict(value=93.5, precision=0.5))
product.measurements.add(type="PURITY", analysis_key="quantitative NMR", percentage=dict(value=99))
product.measurements.add(
    type="AMOUNT", analysis_key="isolated_weight", amount=reaction_pb2.Amount(mass=unit_resolver.resolve("27.75 g"))
)

product.isolated_color = "white"
product.texture.type = product.Texture.POWDER

reaction.provenance.experimenter.CopyFrom(reaction_pb2.Person(name="Richard Y. Liu", organization="MIT"))
reaction.provenance.city = r"Cambridge, MA"
reaction.provenance.doi = r"10.15227/orgsyn.095.0080"
reaction.provenance.publication_url = r"http://www.orgsyn.org/demo.aspx?prep=v95p0080"
reaction.provenance.record_created.time.value = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
reaction.provenance.record_created.person.CopyFrom(
    reaction_pb2.Person(name="Connor W. Coley", organization="MIT", orcid="0000-0002-8271-8723", email="ccoley@mit.edu")
)

for msg in [reaction, product, outcome]:
    validation_output = validations.validate_message(msg)
    print(validation_output)
    js = message_helpers.json_format.MessageToJson(msg)
    write_file(js, f"ORD_{msg.__class__.__name__}.json")
