from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
    PRESSURE_PA,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import StateType

from . import KomfoventCoordinator, KomfoventEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    coord: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]
    diagram_sensors = (
        cls(coord)
        for cls in (
            ExtractAirflowSetpoint,
            ExtractAirflowActual,
            ExtractAirflowFanLevel,
            ExhaustTemperature,
            ExtractTemperatureSetpoint,
            ExtractTemperatureActual,
            SupplyTemperatureSetpoint,
            SupplyTemperatureActual,
            OutdoorTemperature,
            HeatExchangerLevel,
            HeatExchangerEfficiency,
            InternalSupplyTemperature,
            SupplyAirflowSetpoint,
            SupplyAirflowActual,
            SupplyAirflowFanLevel,
            ReturnWaterTemperature,
            ElectricalHeaterLevel,
            WaterHeaterLevel,
            DxLevel,
            HeatpumpLevel,
            WaterCoolerLevel,
        )
    )
    async_add_entities(
        [
            VavSensorsRange(coord),
            NominalSupplyPressure(coord),
            NominalExhaustPressure(coord),
            ActiveModeSupplyFlow(coord),
            ActiveModeExtractFlow(coord),
            ActiveModeTemperatureSetpoint(coord),
            *diagram_sensors,
        ]
    )
    return True


class FlowMetaSensor(KomfoventEntity, SensorEntity):
    @property
    def icon(self) -> str:
        return "mdi:air-filter"

    @property
    def native_unit_of_measurement(self) -> str:
        return self.coordinator.settings_state.flow_units.unit_symbol()

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class PercentageMetaSensor(KomfoventEntity, SensorEntity):
    @property
    def native_unit_of_measurement(self) -> str:
        return PERCENTAGE

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class TemperatureMetaSensor(KomfoventEntity, SensorEntity):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_TEMPERATURE

    @property
    def native_unit_of_measurement(self) -> str:
        return TEMP_CELSIUS

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class VavSensorsRange(KomfoventEntity, SensorEntity):
    @property
    def name(self) -> str:
        return f"{super().name} VAV Sensors Range"

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_PRESSURE

    @property
    def native_value(self) -> StateType:
        return self._modes_state.vav_sensors_range

    @property
    def native_unit_of_measurement(self) -> str:
        return PRESSURE_PA

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class NominalSupplyPressure(KomfoventEntity, SensorEntity):
    @property
    def name(self) -> str:
        return f"{super().name} Nominal Supply Pressure"

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_PRESSURE

    @property
    def native_value(self) -> StateType:
        return self._modes_state.nominal_supply_pressure

    @property
    def native_unit_of_measurement(self) -> str:
        return PRESSURE_PA

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class NominalExhaustPressure(KomfoventEntity, SensorEntity):
    @property
    def name(self) -> str:
        return f"{super().name} Nominal Exhaust Pressure"

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_PRESSURE

    @property
    def native_value(self) -> StateType:
        return self._modes_state.nominal_exhaust_pressure

    @property
    def native_unit_of_measurement(self) -> str:
        return PRESSURE_PA

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class ActiveModeSupplyFlow(FlowMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Active Mode Supply Flow"

    @property
    def native_value(self) -> StateType:
        if active_mode := self._modes_state.active_mode:
            return active_mode.supply_flow
        return None


class ActiveModeExtractFlow(FlowMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Active Mode Extract Flow"

    @property
    def native_value(self) -> StateType:
        if active_mode := self._modes_state.active_mode:
            return active_mode.extract_flow
        return None


class ActiveModeTemperatureSetpoint(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Active Mode Temperature Setpoint"

    @property
    def native_value(self) -> StateType:
        if active_mode := self._modes_state.active_mode:
            return active_mode.setpoint_temperature
        return None


# The following sensors are all modeled after the diagram shown on page 3 of the MODBUS_C5_manual_EN.pdf manual.

# Extract airflow
class ExtractAirflowSetpoint(FlowMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Extract airflow Setpoint"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.extract_flow_setpoint


class ExtractAirflowActual(FlowMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Extract airflow Actual"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.exhaust_flow


class ExtractAirflowFanLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Extract airflow Fan level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.exhaust_fan_level


# Exhaust temperature
class ExhaustTemperature(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Exhaust temperature"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.exhaust_temp


# Extract temperature
class ExtractTemperatureSetpoint(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Extract temperature Setpoint"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.temp_setpoint


class ExtractTemperatureActual(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Extract temperature Actual"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.extract_temp


# Supply temperature


class SupplyTemperatureSetpoint(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Supply temperature Setpoint"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.supply_air_temp_setpoint


class SupplyTemperatureActual(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Supply temperature Actual"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.supply_temp


# Outdoot temperature
class OutdoorTemperature(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Outdoor temperature"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.outdoor_temp


# Heat exchanger
class HeatExchangerLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Heat exchanger Level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.heat_exchanger_level


class HeatExchangerEfficiency(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Heat exchanger Efficiency"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.heat_exchanger_thermal_efficiency


# Internal supply temperature
class InternalSupplyTemperature(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Internal supply temperature"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.internal_supply_temp


# Supply airflow
class SupplyAirflowSetpoint(FlowMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Supply airflow Setpoint"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.supply_flow_setpoint


class SupplyAirflowActual(FlowMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Supply airflow Actual"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.supply_flow


class SupplyAirflowFanLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Supply airflow Fan level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.supply_fan_level


# Return water temperature
class ReturnWaterTemperature(TemperatureMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Return water temperature"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.return_water_temp


# Air heaters/coolers
class ElectricalHeaterLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Electrical heater Level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.electric_heater_level


class WaterHeaterLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Water heater Level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.water_heater_level


class DxLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} DX level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.dx_level


class HeatpumpLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Heat-pump level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.heat_pump_level


class WaterCoolerLevel(PercentageMetaSensor):
    @property
    def name(self) -> str:
        return f"{super().name} Water cooler Level"

    @property
    def native_value(self) -> StateType:
        return self._monitoring_state.water_cooler_level
