import typing
from enum import IntEnum

from google.protobuf.message import Message  # type: ignore
from protobuf_to_pydantic.customer_validator import check_one_of
from pydantic import BaseModel, root_validator
from pydantic.fields import FieldInfo


class ReactionIdentifierType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    REACTION_SMILES = 2
    REACTION_CXSMILES = 6
    RDFILE = 3
    RINCHI = 4
    NAME = 5


class AdditionSpeedType(IntEnum):
    UNSPECIFIED = 0
    ALL_AT_ONCE = 1
    FAST = 2
    SLOW = 3
    DROPWISE = 4
    CONTINUOUS = 5
    PORTIONWISE = 6


class AdditionDeviceType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    NONE = 2
    SYRINGE = 3
    CANNULA = 4
    ADDITION_FUNNEL = 5


class UnmeasuredAmountType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    SATURATED = 2
    CATALYTIC = 3
    TITRATED = 4


class Source(BaseModel):
    vendor: str = FieldInfo(default='')
    catalog_id: str = FieldInfo(default='')
    lot: str = FieldInfo(default='')


class ReactionRole(BaseModel):
    pass


class ReactionRoleType(IntEnum):
    UNSPECIFIED = 0
    REACTANT = 1
    REAGENT = 2
    SOLVENT = 3
    CATALYST = 4
    WORKUP = 5
    INTERNAL_STANDARD = 6
    AUTHENTIC_STANDARD = 7
    PRODUCT = 8


class CompoundPreparationType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    NONE = 2
    REPURIFIED = 3
    SPARGED = 4
    DRIED = 5
    SYNTHESIZED = 6


class CompoundIdentifierType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    SMILES = 2
    INCHI = 3
    MOLBLOCK = 4
    IUPAC_NAME = 5
    NAME = 6
    CAS_NUMBER = 7
    PUBCHEM_CID = 8
    CHEMSPIDER_ID = 9
    CXSMILES = 10
    INCHI_KEY = 11
    XYZ = 12
    UNIPROT_ID = 13
    PDB_ID = 14
    AMINO_ACID_SEQUENCE = 15
    HELM = 16


class VesselType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    ROUND_BOTTOM_FLASK = 2
    VIAL = 3
    WELL_PLATE = 4
    MICROWAVE_VIAL = 5
    TUBE = 6
    CONTINUOUS_STIRRED_TANK_REACTOR = 7
    PACKED_BED_REACTOR = 8
    NMR_TUBE = 9
    PRESSURE_FLASK = 10
    PRESSURE_REACTOR = 11
    ELECTROCHEMICAL_CELL = 12


class VesselMaterialType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    GLASS = 2
    POLYPROPYLENE = 3
    PLASTIC = 4
    METAL = 5
    QUARTZ = 6


class VesselAttachmentType(IntEnum):
    UNSPECIFIED = 0
    NONE = 1
    CUSTOM = 2
    SEPTUM = 3
    CAP = 4
    MAT = 5
    REFLUX_CONDENSER = 6
    VENT_NEEDLE = 7
    DEAN_STARK = 8
    VACUUM_TUBE = 9
    ADDITION_FUNNEL = 10
    DRYING_TUBE = 11
    ALUMINUM_FOIL = 12
    THERMOCOUPLE = 13
    BALLOON = 14
    GAS_ADAPTER = 15
    PRESSURE_REGULATOR = 16
    RELEASE_VALVE = 17


class VesselPreparationType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    NONE = 2
    OVEN_DRIED = 3
    FLAME_DRIED = 4
    EVACUATED_BACKFILLED = 5
    PURGED = 6


class ReactionEnvironmentType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    FUME_HOOD = 2
    BENCH_TOP = 3
    GLOVE_BOX = 4
    GLOVE_BAG = 5


class TemperatureControlType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    AMBIENT = 2
    OIL_BATH = 3
    WATER_BATH = 4
    SAND_BATH = 5
    ICE_BATH = 6
    DRY_ALUMINUM_PLATE = 7
    MICROWAVE = 8
    DRY_ICE_BATH = 9
    AIR_FAN = 10
    LIQUID_NITROGEN = 11


class TemperatureMeasurementType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    THERMOCOUPLE_INTERNAL = 2
    THERMOCOUPLE_EXTERNAL = 3
    INFRARED = 4


class PressureControlType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    AMBIENT = 2
    SLIGHT_POSITIVE = 3
    SEALED = 4
    PRESSURIZED = 5


class AtmosphereType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    AIR = 2
    NITROGEN = 3
    ARGON = 4
    OXYGEN = 5
    HYDROGEN = 6
    CARBON_MONOXIDE = 7
    CARBON_DIOXIDE = 8
    METHANE = 9
    AMMONIA = 10
    OZONE = 11
    ETHYLENE = 12
    ACETYLENE = 13


class PressureMeasurementType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    PRESSURE_TRANSDUCER = 2


class StirringRateType(IntEnum):
    UNSPECIFIED = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class StirringMethodType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    NONE = 2
    STIR_BAR = 3
    OVERHEAD_MIXER = 4
    AGITATION = 5
    BALL_MILLING = 6
    SONICATION = 7


class IlluminationType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    AMBIENT = 2
    DARK = 3
    LED = 4
    HALOGEN_LAMP = 5
    DEUTERIUM_LAMP = 6
    SOLAR_SIMULATOR = 7
    BROAD_SPECTRUM = 8


class ElectrochemistryCellType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    DIVIDED_CELL = 2
    UNDIVIDED_CELL = 3


class ElectrochemistryType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    CONSTANT_CURRENT = 2
    CONSTANT_VOLTAGE = 3


class TubingType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    STEEL = 2
    COPPER = 3
    PFA = 4
    FEP = 5
    TEFLONAF = 6
    PTFE = 7
    GLASS = 8
    QUARTZ = 9
    SILICON = 10
    PDMS = 11


class FlowType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    PLUG_FLOW_REACTOR = 2
    CONTINUOUS_STIRRED_TANK_REACTOR = 3
    PACKED_BED_REACTOR = 4


class ReactionNotes(BaseModel):
    _one_of_dict = {'ReactionNotes._forms_precipitate': {'fields': {'forms_precipitate'}},
                    'ReactionNotes._is_exothermic': {'fields': {'is_exothermic'}},
                    'ReactionNotes._is_heterogeneous': {'fields': {'is_heterogeneous'}},
                    'ReactionNotes._is_sensitive_to_light': {'fields': {'is_sensitive_to_light'}},
                    'ReactionNotes._is_sensitive_to_moisture': {'fields': {'is_sensitive_to_moisture'}},
                    'ReactionNotes._is_sensitive_to_oxygen': {'fields': {'is_sensitive_to_oxygen'}},
                    'ReactionNotes._offgasses': {'fields': {'offgasses'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    is_heterogeneous: bool = FieldInfo(default=False)
    forms_precipitate: bool = FieldInfo(default=False)
    is_exothermic: bool = FieldInfo(default=False)
    offgasses: bool = FieldInfo(default=False)
    is_sensitive_to_moisture: bool = FieldInfo(default=False)
    is_sensitive_to_oxygen: bool = FieldInfo(default=False)
    is_sensitive_to_light: bool = FieldInfo(default=False)
    safety_notes: str = FieldInfo(default='')
    procedure_details: str = FieldInfo(default='')


class ReactionWorkupType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    ADDITION = 2
    ALIQUOT = 3
    TEMPERATURE = 4
    CONCENTRATION = 5
    EXTRACTION = 6
    FILTRATION = 7
    WASH = 8
    DRY_IN_VACUUM = 9
    DRY_WITH_MATERIAL = 10
    FLASH_CHROMATOGRAPHY = 11
    OTHER_CHROMATOGRAPHY = 12
    SCAVENGING = 13
    WAIT = 14
    STIRRING = 15
    PH_ADJUST = 16
    DISSOLUTION = 17
    DISTILLATION = 18


class TextureType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    POWDER = 2
    CRYSTAL = 3
    OIL = 4
    AMORPHOUS_SOLID = 5
    FOAM = 6
    WAX = 7
    SEMI_SOLID = 8
    SOLID = 9
    LIQUID = 10


class MassSpecMeasurementType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    TIC = 2
    TIC_POSITIVE = 3
    TIC_NEGATIVE = 4
    EIC = 5


class SelectivityType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    EE = 2
    ER = 3
    DR = 4
    EZ = 5
    ZE = 6


class ProductMeasurementType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    IDENTITY = 2
    YIELD = 3
    SELECTIVITY = 4
    PURITY = 5
    AREA = 6
    COUNTS = 7
    INTENSITY = 8
    AMOUNT = 9


class DateTime(BaseModel):
    value: str = FieldInfo(default='')


class AnalysisType(IntEnum):
    UNSPECIFIED = 0
    CUSTOM = 1
    LC = 2
    GC = 3
    IR = 4
    NMR_1H = 5
    NMR_13C = 6
    NMR_OTHER = 7
    MP = 8
    UV = 9
    TLC = 10
    MS = 11
    HRMS = 12
    MSMS = 13
    WEIGHT = 14
    LCMS = 15
    GCMS = 16
    ELSD = 17
    CD = 18
    SFC = 19
    EPR = 20
    XRD = 21
    RAMAN = 22
    ED = 23


class Person(BaseModel):
    username: str = FieldInfo(default='')
    name: str = FieldInfo(default='')
    orcid: str = FieldInfo(default='')
    organization: str = FieldInfo(default='')
    email: str = FieldInfo(default='')


class TimeUnit(IntEnum):
    UNSPECIFIED = 0
    DAY = 4
    HOUR = 1
    MINUTE = 2
    SECOND = 3


class MassUnit(IntEnum):
    UNSPECIFIED = 0
    KILOGRAM = 1
    GRAM = 2
    MILLIGRAM = 3
    MICROGRAM = 4


class MolesUnit(IntEnum):
    UNSPECIFIED = 0
    MOLE = 1
    MILLIMOLE = 2
    MICROMOLE = 3
    NANOMOLE = 4


class VolumeUnit(IntEnum):
    UNSPECIFIED = 0
    LITER = 1
    MILLILITER = 2
    MICROLITER = 3
    NANOLITER = 4


class ConcentrationUnit(IntEnum):
    UNSPECIFIED = 0
    MOLAR = 1
    MILLIMOLAR = 2
    MICROMOLAR = 3


class PressureUnit(IntEnum):
    UNSPECIFIED = 0
    BAR = 1
    ATMOSPHERE = 2
    PSI = 3
    KPSI = 4
    PASCAL = 5
    KILOPASCAL = 6
    TORR = 7
    MM_HG = 8


class TemperatureUnit(IntEnum):
    UNSPECIFIED = 0
    CELSIUS = 1
    FAHRENHEIT = 2
    KELVIN = 3


class CurrentUnit(IntEnum):
    UNSPECIFIED = 0
    AMPERE = 1
    MILLIAMPERE = 2


class VoltageUnit(IntEnum):
    UNSPECIFIED = 0
    VOLT = 1
    MILLIVOLT = 2


class LengthUnit(IntEnum):
    UNSPECIFIED = 0
    CENTIMETER = 1
    MILLIMETER = 2
    METER = 3
    INCH = 4
    FOOT = 5


class WavelengthUnit(IntEnum):
    UNSPECIFIED = 0
    NANOMETER = 1
    WAVENUMBER = 2


class FlowRateUnit(IntEnum):
    UNSPECIFIED = 0
    MICROLITER_PER_MINUTE = 1
    MICROLITER_PER_SECOND = 2
    MILLILITER_PER_MINUTE = 3
    MILLILITER_PER_SECOND = 4
    MICROLITER_PER_HOUR = 5


class Percentage(BaseModel):
    _one_of_dict = {'Percentage._precision': {'fields': {'precision'}}, 'Percentage._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)


class FloatValue(BaseModel):
    _one_of_dict = {'FloatValue._precision': {'fields': {'precision'}}, 'FloatValue._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)


class Data(BaseModel):
    _one_of_dict = {'Data.kind': {'fields': {'bytes_value', 'float_value', 'integer_value', 'string_value', 'url'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    float_value: float = FieldInfo(default=0.0)
    integer_value: int = FieldInfo(default=0)
    bytes_value: bytes = FieldInfo(default=b'')
    string_value: str = FieldInfo(default='')
    url: str = FieldInfo(default='')
    description: str = FieldInfo(default='')
    format: str = FieldInfo(default='')


class ReactionIdentifier(BaseModel):
    _one_of_dict = {'ReactionIdentifier._is_mapped': {'fields': {'is_mapped'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    type: ReactionIdentifierType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    value: str = FieldInfo(default='')
    is_mapped: bool = FieldInfo(default=False)


class AdditionSpeed(BaseModel):
    type: AdditionSpeedType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class AdditionDevice(BaseModel):
    type: AdditionDeviceType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class UnmeasuredAmount(BaseModel):
    type: UnmeasuredAmountType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class CompoundPreparation(BaseModel):
    type: CompoundPreparationType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    reaction_id: str = FieldInfo(default='')


class CompoundIdentifier(BaseModel):
    type: CompoundIdentifierType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    value: str = FieldInfo(default='')


class VesselMaterial(BaseModel):
    type: VesselMaterialType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class VesselAttachment(BaseModel):
    type: VesselAttachmentType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class VesselPreparation(BaseModel):
    type: VesselPreparationType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class ReactionEnvironment(BaseModel):
    type: ReactionEnvironmentType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class TemperatureControl(BaseModel):
    type: TemperatureControlType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class PressureControl(BaseModel):
    type: PressureControlType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class Atmosphere(BaseModel):
    type: AtmosphereType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class StirringRate(BaseModel):
    type: StirringRateType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    rpm: int = FieldInfo(default=0)


class ElectrochemistryCell(BaseModel):
    type: ElectrochemistryCellType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class Texture(BaseModel):
    type: TextureType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class MassSpecMeasurementDetails(BaseModel):
    _one_of_dict = {'MassSpecMeasurementDetails._tic_maximum_mz': {'fields': {'tic_maximum_mz'}},
                    'MassSpecMeasurementDetails._tic_minimum_mz': {'fields': {'tic_minimum_mz'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    type: MassSpecMeasurementType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    tic_minimum_mz: float = FieldInfo(default=0.0)
    tic_maximum_mz: float = FieldInfo(default=0.0)
    eic_masses: typing.List[float] = FieldInfo(default_factory=list)


class Selectivity(BaseModel):
    type: SelectivityType = FieldInfo(default=0)
    details: str = FieldInfo(default='')


class Analysis(BaseModel):
    _one_of_dict = {'Analysis._is_of_isolated_species': {'fields': {'is_of_isolated_species'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    type: AnalysisType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    chmo_id: int = FieldInfo(default=0)
    is_of_isolated_species: bool = FieldInfo(default=False)
    data: typing.Dict[str, Data] = FieldInfo(default_factory=dict)
    instrument_manufacturer: str = FieldInfo(default='')
    instrument_last_calibrated: DateTime = FieldInfo()


class RecordEvent(BaseModel):
    time: DateTime = FieldInfo()
    person: Person = FieldInfo()
    details: str = FieldInfo(default='')


class Time(BaseModel):
    _one_of_dict = {'Time._precision': {'fields': {'precision'}}, 'Time._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: TimeUnit = FieldInfo(default=0)


class Mass(BaseModel):
    _one_of_dict = {'Mass._precision': {'fields': {'precision'}}, 'Mass._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: MassUnit = FieldInfo(default=0)


class Moles(BaseModel):
    _one_of_dict = {'Moles._precision': {'fields': {'precision'}}, 'Moles._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: MolesUnit = FieldInfo(default=0)


class Volume(BaseModel):
    _one_of_dict = {'Volume._precision': {'fields': {'precision'}}, 'Volume._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: VolumeUnit = FieldInfo(default=0)


class Concentration(BaseModel):
    _one_of_dict = {'Concentration._precision': {'fields': {'precision'}},
                    'Concentration._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: ConcentrationUnit = FieldInfo(default=0)


class Pressure(BaseModel):
    _one_of_dict = {'Pressure._precision': {'fields': {'precision'}}, 'Pressure._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: PressureUnit = FieldInfo(default=0)


class Temperature(BaseModel):
    _one_of_dict = {'Temperature._precision': {'fields': {'precision'}}, 'Temperature._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: TemperatureUnit = FieldInfo(default=0)


class Current(BaseModel):
    _one_of_dict = {'Current._precision': {'fields': {'precision'}}, 'Current._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: CurrentUnit = FieldInfo(default=0)


class Voltage(BaseModel):
    _one_of_dict = {'Voltage._precision': {'fields': {'precision'}}, 'Voltage._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: VoltageUnit = FieldInfo(default=0)


class Length(BaseModel):
    _one_of_dict = {'Length._precision': {'fields': {'precision'}}, 'Length._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: LengthUnit = FieldInfo(default=0)


class Wavelength(BaseModel):
    _one_of_dict = {'Wavelength._precision': {'fields': {'precision'}}, 'Wavelength._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: WavelengthUnit = FieldInfo(default=0)


class FlowRate(BaseModel):
    _one_of_dict = {'FlowRate._precision': {'fields': {'precision'}}, 'FlowRate._value': {'fields': {'value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    value: float = FieldInfo(default=0.0)
    precision: float = FieldInfo(default=0.0)
    units: FlowRateUnit = FieldInfo(default=0)


class Amount(BaseModel):
    _one_of_dict = {'Amount._volume_includes_solutes': {'fields': {'volume_includes_solutes'}},
                    'Amount.kind': {'fields': {'mass', 'moles', 'unmeasured', 'volume'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    mass: Mass = FieldInfo()
    moles: Moles = FieldInfo()
    volume: Volume = FieldInfo()
    unmeasured: UnmeasuredAmount = FieldInfo()
    volume_includes_solutes: bool = FieldInfo(default=False)


class Vessel(BaseModel):
    type: VesselType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    material: VesselMaterial = FieldInfo()
    preparations: typing.List[VesselPreparation] = FieldInfo(default_factory=list)
    attachments: typing.List[VesselAttachment] = FieldInfo(default_factory=list)
    volume: Volume = FieldInfo()
    plate_id: str = FieldInfo(default='')
    plate_position: str = FieldInfo(default='')


class TemperatureMeasurement(BaseModel):
    type: TemperatureMeasurementType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    time: Time = FieldInfo()
    temperature: Temperature = FieldInfo()


class PressureMeasurement(BaseModel):
    type: PressureMeasurementType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    time: Time = FieldInfo()
    pressure: Pressure = FieldInfo()


class StirringConditions(BaseModel):
    type: StirringMethodType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    rate: StirringRate = FieldInfo()


class IlluminationConditions(BaseModel):
    type: IlluminationType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    peak_wavelength: Wavelength = FieldInfo()
    color: str = FieldInfo(default='')
    distance_to_vessel: Length = FieldInfo()


class ElectrochemistryMeasurement(BaseModel):
    _one_of_dict = {'ElectrochemistryMeasurement.kind': {'fields': {'current', 'voltage'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    time: Time = FieldInfo()
    current: Current = FieldInfo()
    voltage: Voltage = FieldInfo()


class Tubing(BaseModel):
    type: TubingType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    diameter: Length = FieldInfo()


class ReactionObservation(BaseModel):
    time: Time = FieldInfo()
    comment: str = FieldInfo(default='')
    image: Data = FieldInfo()


class ReactionProvenance(BaseModel):
    experimenter: Person = FieldInfo()
    city: str = FieldInfo(default='')
    experiment_start: DateTime = FieldInfo()
    doi: str = FieldInfo(default='')
    patent: str = FieldInfo(default='')
    publication_url: str = FieldInfo(default='')
    record_created: RecordEvent = FieldInfo()
    record_modified: typing.List[RecordEvent] = FieldInfo(default_factory=list)


class CrudeComponent(BaseModel):
    _one_of_dict = {'CrudeComponent._has_derived_amount': {'fields': {'has_derived_amount'}},
                    'CrudeComponent._includes_workup': {'fields': {'includes_workup'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    reaction_id: str = FieldInfo(default='')
    includes_workup: bool = FieldInfo(default=False)
    has_derived_amount: bool = FieldInfo(default=False)
    amount: Amount = FieldInfo()


class Compound(BaseModel):
    _one_of_dict = {'Compound._is_limiting': {'fields': {'is_limiting'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    identifiers: typing.List[CompoundIdentifier] = FieldInfo(default_factory=list)
    amount: Amount = FieldInfo()
    reaction_role: ReactionRoleType = FieldInfo(default=0)
    is_limiting: bool = FieldInfo(default=False)
    preparations: typing.List[CompoundPreparation] = FieldInfo(default_factory=list)
    source: Source = FieldInfo()
    features: typing.Dict[str, Data] = FieldInfo(default_factory=dict)
    analyses: typing.Dict[str, Analysis] = FieldInfo(default_factory=dict)


class ReactionSetup(BaseModel):
    _one_of_dict = {'ReactionSetup._is_automated': {'fields': {'is_automated'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    vessel: Vessel = FieldInfo()
    is_automated: bool = FieldInfo(default=False)
    automation_platform: str = FieldInfo(default='')
    automation_code: typing.Dict[str, Data] = FieldInfo(default_factory=dict)
    environment: ReactionEnvironment = FieldInfo()


class TemperatureConditions(BaseModel):
    control: TemperatureControl = FieldInfo()
    setpoint: Temperature = FieldInfo()
    measurements: typing.List[TemperatureMeasurement] = FieldInfo(default_factory=list)


class PressureConditions(BaseModel):
    control: PressureControl = FieldInfo()
    setpoint: Pressure = FieldInfo()
    atmosphere: Atmosphere = FieldInfo()
    measurements: typing.List[PressureMeasurement] = FieldInfo(default_factory=list)


class ElectrochemistryConditions(BaseModel):
    type: ElectrochemistryType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    current: Current = FieldInfo()
    voltage: Voltage = FieldInfo()
    anode_material: str = FieldInfo(default='')
    cathode_material: str = FieldInfo(default='')
    electrode_separation: Length = FieldInfo()
    measurements: typing.List[ElectrochemistryMeasurement] = FieldInfo(default_factory=list)
    cell: ElectrochemistryCell = FieldInfo()


class FlowConditions(BaseModel):
    type: FlowType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    pump_type: str = FieldInfo(default='')
    tubing: Tubing = FieldInfo()


class ReactionInput(BaseModel):
    components: typing.List[Compound] = FieldInfo(default_factory=list)
    crude_components: typing.List[CrudeComponent] = FieldInfo(default_factory=list)
    addition_order: int = FieldInfo(default=0)
    addition_time: Time = FieldInfo()
    addition_speed: AdditionSpeed = FieldInfo()
    addition_duration: Time = FieldInfo()
    flow_rate: FlowRate = FieldInfo()
    addition_device: AdditionDevice = FieldInfo()
    addition_temperature: Temperature = FieldInfo()


class ReactionConditions(BaseModel):
    _one_of_dict = {'ReactionConditions._conditions_are_dynamic': {'fields': {'conditions_are_dynamic'}},
                    'ReactionConditions._ph': {'fields': {'ph'}}, 'ReactionConditions._reflux': {'fields': {'reflux'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    temperature: TemperatureConditions = FieldInfo()
    pressure: PressureConditions = FieldInfo()
    stirring: StirringConditions = FieldInfo()
    illumination: IlluminationConditions = FieldInfo()
    electrochemistry: ElectrochemistryConditions = FieldInfo()
    flow: FlowConditions = FieldInfo()
    reflux: bool = FieldInfo(default=False)
    ph: float = FieldInfo(default=0.0)
    conditions_are_dynamic: bool = FieldInfo(default=False)
    details: str = FieldInfo(default='')


class ProductMeasurement(BaseModel):
    _one_of_dict = {'ProductMeasurement._is_normalized': {'fields': {'is_normalized'}},
                    'ProductMeasurement._uses_authentic_standard': {'fields': {'uses_authentic_standard'}},
                    'ProductMeasurement._uses_internal_standard': {'fields': {'uses_internal_standard'}},
                    'ProductMeasurement.value': {'fields': {'amount', 'float_value', 'percentage', 'string_value'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    analysis_key: str = FieldInfo(default='')
    type: ProductMeasurementType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    uses_internal_standard: bool = FieldInfo(default=False)
    is_normalized: bool = FieldInfo(default=False)
    uses_authentic_standard: bool = FieldInfo(default=False)
    authentic_standard: Compound = FieldInfo()
    percentage: Percentage = FieldInfo()
    float_value: FloatValue = FieldInfo()
    string_value: str = FieldInfo(default='')
    amount: Amount = FieldInfo()
    retention_time: Time = FieldInfo()
    mass_spec_details: MassSpecMeasurementDetails = FieldInfo()
    selectivity: Selectivity = FieldInfo()
    wavelength: Wavelength = FieldInfo()


class ReactionWorkup(BaseModel):
    _one_of_dict = {'ReactionWorkup._is_automated': {'fields': {'is_automated'}},
                    'ReactionWorkup._target_ph': {'fields': {'target_ph'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    type: ReactionWorkupType = FieldInfo(default=0)
    details: str = FieldInfo(default='')
    duration: Time = FieldInfo()
    input: ReactionInput = FieldInfo()
    amount: Amount = FieldInfo()
    temperature: TemperatureConditions = FieldInfo()
    keep_phase: str = FieldInfo(default='')
    stirring: StirringConditions = FieldInfo()
    target_ph: float = FieldInfo(default=0.0)
    is_automated: bool = FieldInfo(default=False)


class ProductCompound(BaseModel):
    _one_of_dict = {'ProductCompound._is_desired_product': {'fields': {'is_desired_product'}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)
    identifiers: typing.List[CompoundIdentifier] = FieldInfo(default_factory=list)
    is_desired_product: bool = FieldInfo(default=False)
    measurements: typing.List[ProductMeasurement] = FieldInfo(default_factory=list)
    isolated_color: str = FieldInfo(default='')
    texture: Texture = FieldInfo()
    features: typing.Dict[str, Data] = FieldInfo(default_factory=dict)
    reaction_role: ReactionRoleType = FieldInfo(default=0)


class ReactionOutcome(BaseModel):
    reaction_time: Time = FieldInfo()
    conversion: Percentage = FieldInfo()
    products: typing.List[ProductCompound] = FieldInfo(default_factory=list)
    analyses: typing.Dict[str, Analysis] = FieldInfo(default_factory=dict)


class Reaction(BaseModel):
    identifiers: typing.List[ReactionIdentifier] = FieldInfo(default_factory=list)
    inputs: typing.Dict[str, ReactionInput] = FieldInfo(default_factory=dict)
    setup: ReactionSetup = FieldInfo()
    conditions: ReactionConditions = FieldInfo()
    notes: ReactionNotes = FieldInfo()
    observations: typing.List[ReactionObservation] = FieldInfo(default_factory=list)
    workups: typing.List[ReactionWorkup] = FieldInfo(default_factory=list)
    outcomes: typing.List[ReactionOutcome] = FieldInfo(default_factory=list)
    provenance: ReactionProvenance = FieldInfo()
    reaction_id: str = FieldInfo(default='')


class Dataset(BaseModel):
    name: str = FieldInfo(default='')
    description: str = FieldInfo(default='')
    reactions: typing.List[Reaction] = FieldInfo(default_factory=list)
    reaction_ids: typing.List[str] = FieldInfo(default_factory=list)
    dataset_id: str = FieldInfo(default='')


class DatasetExample(BaseModel):
    dataset_id: str = FieldInfo(default='')
    description: str = FieldInfo(default='')
    url: str = FieldInfo(default='')
    created: RecordEvent = FieldInfo()
