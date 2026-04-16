# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_gateway_enums.py - Home Assistant Gateway Enums
Version: 2025-12-17_1
Description: Enum definitions for HA Gateway interfaces

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from enum import Enum


class HAGatewayInterface(Enum):
    """Home Assistant Gateway Interface enumeration.

    These represent the main functional areas of Home Assistant operations.
    Each interface routes to a specific handler module.
    """

    # Voice assistant interfaces
    ALEXA = "alexa"          # Amazon Alexa integration
    ASSIST = "assist"        # Home Assistant Assist/Conversational AI
    ALEXA_RESPONSE = "alexa_response"  # Alexa response generation with consolidation support

    # Core Home Assistant functionality
    DEVICES = "devices"      # Device state management and control
    CONFIG = "config"        # Configuration management
    WEBSOCKET = "websocket"  # WebSocket communication
    REGISTRY = "registry"    # Registry management (area, device, entity, category)
    AUTOMATION = "automation"  # Automation, script, and trigger management
    BLUEPRINT = "blueprint"  # Blueprint management
    SUPERVISOR = "supervisor"  # Supervisor, host, OS, and add-on management
    CAMERA = "camera"        # Camera management and streaming
    ENERGY = "energy"        # Energy management and monitoring
    BACKUP = "backup"        # Backup management and restoration
    HISTORY = "history"      # Historical data access
    REPAIRS = "repairs"      # System repairs and issue management
    STATISTICS = "statistics"  # Long-term statistics analytics
    LOGBOOK = "logbook"        # Human-readable event logs
    SCENE = "scene"            # Scene activation
    SCRIPT = "script"          # Script execution
    NOTIFY = "notify"          # Notification sending
    ESPHOME = "esphome"        # ESPHome integration
    MOBILE_APP = "mobile_app"  # Mobile app integration
    LOGGER = "logger"          # Logging level management
    HARDWARE = "hardware"      # Hardware information
    SENSOR = "sensor"          # Sensor entity metadata
    NUMBER = "number"          # Number entity metadata
    PERSISTENT = "persistent"  # Persistent notification management
    CONVERSATION = "conversation"  # Conversational AI agent management
    ZONE = "zone"              # Zone management for location-based grouping
    COUNTER = "counter"        # Counter helper entities
    TIMER = "timer"            # Timer helper entities
    INPUT_BOOLEAN = "input_boolean"  # Input boolean helper entities
    INPUT_BUTTON = "input_button"    # Input button helper entities (PHASE 11)
    INPUT_DATETIME = "input_datetime"  # Input datetime helper entities (PHASE 11)
    INPUT_NUMBER = "input_number"    # Input number helper entities (PHASE 11)
    INPUT_SELECT = "input_select"    # Input select helper entities (PHASE 11)
    INPUT_TEXT = "input_text"        # Input text helper entities (PHASE 11)
    SWITCH = "switch"                # Switch device control (PHASE 12)
    LIGHT = "light"                  # Light device control (PHASE 12)
    CLIMATE = "climate"              # Climate/HVAC control (PHASE 12)
    COVER = "cover"                  # Cover/blinds control (PHASE 12)
    LOCK = "lock"                    # Lock control (PHASE 12)
    MEDIA_PLAYER = "media_player"    # Media player control (PHASE 12)
    BINARY_SENSOR = "binary_sensor"  # Binary sensor state queries (PHASE 13)
    VACUUM = "vacuum"                # Vacuum cleaner control (PHASE 13)
    FAN = "fan"                      # Fan control (PHASE 13)
    HUMIDIFIER = "humidifier"        # Humidifier/dehumidifier control (PHASE 13)
    WATER_HEATER = "water_heater"    # Water heater control (PHASE 13)
    ALARM_CONTROL_PANEL = "alarm_control_panel"  # Security/alarm system control (PHASE 14)
    BUTTON = "button"                # Button helper entities (PHASE 14)
    GROUP = "group"                  # Group management (PHASE 14)
    WEATHER = "weather"              # Weather information (PHASE 14)
    PERSON = "person"                # Person tracking (PHASE 14)
    REMOTE = "remote"                # Remote control with advanced command sending (PHASE 15)
    SIREN = "siren"                  # Siren control with tone/volume/duration (PHASE 15)
    UPDATE = "update"                # Update installation and management (PHASE 15)
    CALENDAR = "calendar"            # Calendar event creation (PHASE 15)
    IMAGE_PROCESSING = "image_processing"  # Image processing scan operations (PHASE 16)
    STT = "stt"                      # Speech-to-text operations (PHASE 16)
    TTS = "tts"                      # Text-to-speech operations (PHASE 16)
    FILE = "file"                    # File reading operations (PHASE 17)
    TODO = "todo"                    # Todo list management
    TEMPLATE = "template"            # Template entity reloading (PHASE 18)
    MQTT = "mqtt"                    # MQTT message broker operations (PHASE 18)
    SHOPPING_LIST = "shopping_list"  # Shopping list management (PHASE 18)
    UTILITY_METER = "utility_meter"  # Utility meter management (PHASE 19)
    WAKE_ON_LAN = "wake_on_lan"      # Wake-on-LAN operations (PHASE 19)
    ZHA = "zha"                      # Zigbee Home Automation (PHASE 19)
    SONOS = "sonos"                  # Sonos speaker system control (PHASE 20)
    ANDROIDTV = "androidtv"          # Android TV / Fire TV control (PHASE 20)
    WEBOSTV = "webostv"              # LG webOS TV control (PHASE 20)
    DENONAVR = "denonavr"            # Denon AVR receiver control (PHASE 20)
    ROKU = "roku"                    # Roku streaming device control (PHASE 20)
    GOOGLE_MAIL = "google_mail"      # Gmail integration (PHASE 20)
    HUE = "hue"                      # Philips Hue bridge control (PHASE 21)
    NEATO = "neato"                  # Neato robot vacuum control (PHASE 21)
    TADO = "tado"                    # Tado° smart thermostat control (PHASE 21)
    TPLINK = "tplink"                # TP-Link Kasa smart devices (PHASE 21)
    ZWAVE_JS = "zwave_js"          # Z-Wave JS lock usercodes (PHASE 22)
    DECONZ = "deconz"                # deCONZ Zigbee gateway (PHASE 22)
    HOMEKIT = "homekit"              # Apple HomeKit integration (PHASE 22)
    TRANSMISSION = "transmission"    # BitTorrent client (PHASE 22)
    FFMPEG = "ffmpeg"                # Video processing (PHASE 22)
    BROWSER = "browser"              # Browser automation (PHASE 23)
    BLUE_CURRENT = "blue_current"    # EV charging management (PHASE 23)
    CAST = "cast"                    # Google Cast control (PHASE 23)
    ECOVACS = "ecovacs"              # Robot vacuum control (PHASE 23)
    PS4 = "ps4"                      # PlayStation 4 control (PHASE 24)
    VIZIO = "vizio"                  # Vizio TV control (PHASE 24)
    SNAPCAST = "snapcast"            # Multiroom audio (PHASE 24)
    WEMO = "wemo"                    # WeMo device control (PHASE 24)
    BLUESOUND = "bluesound"          # Bluesound audio (PHASE 24)
    NUKI = "nuki"                    # Nuki smart lock (PHASE 24)
    IMAP = "imap"                    # Email integration (PHASE 25)
    BLINK = "blink"                  # Security camera system (PHASE 25)
    ICLOUD = "icloud"                # Apple ecosystem integration (PHASE 25)
    FLUX_LED = "flux_led"            # LED lighting effects (PHASE 25)
    HIVE = "hive"                    # Hive heating control (PHASE 25)
    ALERT = "alert"                  # Alert notifications (PHASE 25)
    ECOBEE = "ecobee"                # Ecobee thermostat (PHASE 26)
    SHELLY = "shelly"                # Shelly smart home devices (PHASE 26)
    SIMPLISAFE = "simplisafe"        # SimpliSafe security system (PHASE 26)
    GOOGLE_ASSISTANT = "google_assistant"  # Google Assistant sync (PHASE 26)
    LIFX = "lifx"                    # LIFX LED lighting (PHASE 26)
    ADGUARD = "adguard"              # AdGuard DNS filtering (PHASE 26)
    ABODE = "abode"                  # Abode security system (PHASE 27)
    AMCREST = "amcrest"              # Amcrest IP cameras (PHASE 27)
    IFTTT = "ifttt"                  # IFTTT webhooks (PHASE 27)
    ADS = "ads"                      # ADS automation data (PHASE 27)
    ALARMDECODER = "alarmdecoder"    # AlarmDecoder keypad (PHASE 27)
    ADVANTAGE_AIR = "advantage_air"  # Advantage Air HVAC (PHASE 28)
    AMBERELECTRIC = "amberelectric"  # Amber Electric energy (PHASE 28)
    AGENT_DVR = "agent_dvr"          # Agent DVR camera (PHASE 28)
    AI_TASK = "ai_task"              # AI task generation (PHASE 28)
    AFTERSHIP = "aftership"          # AfterShip tracking (PHASE 28)
    BANG_OLUFSEN = "bang_olufsen"    # Bang & Olufsen BeoLink (PHASE 29)
    ASSIST_SATELLITE = "assist_satellite"  # Assist Satellite (PHASE 29)
    TOUCH_PANEL = "touch_panel"      # Touch panel control (PHASE 29)
    SQUEEZEBOX = "squeezebox"        # Squeezebox music player (PHASE 29)
    ALEXA_DEVICES = "alexa_devices"  # Alexa device control (PHASE 30)
    BOND = "bond"                    # Bond hub control (PHASE 30)
    BOSCH_ALARM = "bosch_alarm"      # Bosch alarm system (PHASE 30)
    BRING = "bring"                  # Bring! shopping list (PHASE 30)
    BSBLAN = "bsblan"                # BSBLan heating system (PHASE 30)
    TIMED_BACKUP = "timed_backup"    # Timed backup management (PHASE 30)
    PROXIMITY = "proximity"          # Proximity zone monitoring (PHASE 31)
    SUN = "sun"                      # Sun position and timing (PHASE 31)

    # Supporting infrastructure
    CACHE = "cache"          # Caching layer for performance
    HEALTH = "health"        # Health monitoring and diagnostics


# ===== INTERFACE DESCRIPTIONS =====

INTERFACE_DESCRIPTIONS = {
    HAGatewayInterface.ALEXA: "Amazon Alexa smart home integration",
    HAGatewayInterface.ASSIST: "Home Assistant conversational AI",
    HAGatewayInterface.ALEXA_RESPONSE: "Alexa response generation with consolidation support",
    HAGatewayInterface.DEVICES: "Device state management and control",
    HAGatewayInterface.CONFIG: "Configuration and settings management",
    HAGatewayInterface.WEBSOCKET: "Real-time WebSocket communication",
    HAGatewayInterface.REGISTRY: "Registry management (area, device, entity, category)",
    HAGatewayInterface.AUTOMATION: "Automation, script, and trigger management",
    HAGatewayInterface.BLUEPRINT: "Blueprint management for automation, script, and template",
    HAGatewayInterface.SUPERVISOR: "Supervisor, host, OS, and add-on management",
    HAGatewayInterface.CAMERA: "Camera management and streaming",
    HAGatewayInterface.ENERGY: "Energy management and monitoring",
    HAGatewayInterface.BACKUP: "Backup management and restoration",
    HAGatewayInterface.HISTORY: "Historical data access and analysis",
    HAGatewayInterface.REPAIRS: "System repairs and issue management",
    HAGatewayInterface.STATISTICS: "Long-term statistics analytics",
    HAGatewayInterface.LOGBOOK: "Human-readable event logs",
    HAGatewayInterface.SCENE: "Scene activation",
    HAGatewayInterface.SCRIPT: "Script execution",
    HAGatewayInterface.NOTIFY: "Notification sending",
    HAGatewayInterface.ESPHOME: "ESPHome integration",
    HAGatewayInterface.MOBILE_APP: "Mobile app integration",
    HAGatewayInterface.LOGGER: "Logging level management",
    HAGatewayInterface.HARDWARE: "Hardware information",
    HAGatewayInterface.SENSOR: "Sensor entity metadata",
    HAGatewayInterface.NUMBER: "Number entity metadata",
    HAGatewayInterface.PERSISTENT: "Persistent notification management",
    HAGatewayInterface.CONVERSATION: "Conversational AI agent management",
    HAGatewayInterface.ZONE: "Zone management for location-based grouping",
    HAGatewayInterface.COUNTER: "Counter helper entities",
    HAGatewayInterface.TIMER: "Timer helper entities",
    HAGatewayInterface.INPUT_BOOLEAN: "Input boolean helper entities",
    HAGatewayInterface.INPUT_BUTTON: "Input button helper entities",
    HAGatewayInterface.INPUT_DATETIME: "Input datetime helper entities",
    HAGatewayInterface.INPUT_NUMBER: "Input number helper entities",
    HAGatewayInterface.INPUT_SELECT: "Input select helper entities",
    HAGatewayInterface.INPUT_TEXT: "Input text helper entities",
    HAGatewayInterface.SWITCH: "Switch device control",
    HAGatewayInterface.LIGHT: "Light device control",
    HAGatewayInterface.CLIMATE: "Climate/HVAC control",
    HAGatewayInterface.COVER: "Cover/blinds control",
    HAGatewayInterface.LOCK: "Lock control",
    HAGatewayInterface.MEDIA_PLAYER: "Media player control",
    HAGatewayInterface.BINARY_SENSOR: "Binary sensor state queries",
    HAGatewayInterface.VACUUM: "Vacuum cleaner control",
    HAGatewayInterface.FAN: "Fan control",
    HAGatewayInterface.HUMIDIFIER: "Humidifier/dehumidifier control",
    HAGatewayInterface.WATER_HEATER: "Water heater control",
    HAGatewayInterface.ALARM_CONTROL_PANEL: "Security/alarm system control",
    HAGatewayInterface.BUTTON: "Button helper entities",
    HAGatewayInterface.GROUP: "Group management",
    HAGatewayInterface.WEATHER: "Weather information",
    HAGatewayInterface.PERSON: "Person tracking",
    HAGatewayInterface.REMOTE: "Remote control with advanced command sending",
    HAGatewayInterface.SIREN: "Siren control with tone/volume/duration",
    HAGatewayInterface.UPDATE: "Update installation and management",
    HAGatewayInterface.CALENDAR: "Calendar event creation",
    HAGatewayInterface.IMAGE_PROCESSING: "Image processing scan operations",
    HAGatewayInterface.STT: "Speech-to-text operations",
    HAGatewayInterface.TTS: "Text-to-speech operations",
    HAGatewayInterface.FILE: "File reading operations",
    HAGatewayInterface.TODO: "Todo list management",
    HAGatewayInterface.TEMPLATE: "Template entity reloading",
    HAGatewayInterface.MQTT: "MQTT message broker operations",
    HAGatewayInterface.SHOPPING_LIST: "Shopping list management",
    HAGatewayInterface.UTILITY_METER: "Utility meter management",
    HAGatewayInterface.WAKE_ON_LAN: "Wake-on-LAN operations",
    HAGatewayInterface.ZHA: "Zigbee Home Automation",
    HAGatewayInterface.SONOS: "Sonos speaker system control",
    HAGatewayInterface.ANDROIDTV: "Android TV / Fire TV control",
    HAGatewayInterface.WEBOSTV: "LG webOS TV control",
    HAGatewayInterface.DENONAVR: "Denon AVR receiver control",
    HAGatewayInterface.ROKU: "Roku streaming device control",
    HAGatewayInterface.GOOGLE_MAIL: "Gmail integration",
    HAGatewayInterface.HUE: "Philips Hue bridge control",
    HAGatewayInterface.NEATO: "Neato robot vacuum control",
    HAGatewayInterface.TADO: "Tado° smart thermostat control",
    HAGatewayInterface.TPLINK: "TP-Link Kasa smart devices",
    HAGatewayInterface.ZWAVE_JS: "Z-Wave JS lock usercodes",
    HAGatewayInterface.DECONZ: "deCONZ Zigbee gateway",
    HAGatewayInterface.HOMEKIT: "Apple HomeKit integration",
    HAGatewayInterface.TRANSMISSION: "BitTorrent client",
    HAGatewayInterface.FFMPEG: "Video processing",
    HAGatewayInterface.BROWSER: "Browser automation",
    HAGatewayInterface.BLUE_CURRENT: "EV charging management",
    HAGatewayInterface.CAST: "Google Cast control",
    HAGatewayInterface.ECOVACS: "Robot vacuum control",
    HAGatewayInterface.PS4: "PlayStation 4 control",
    HAGatewayInterface.VIZIO: "Vizio TV control",
    HAGatewayInterface.SNAPCAST: "Multiroom audio",
    HAGatewayInterface.WEMO: "WeMo device control",
    HAGatewayInterface.BLUESOUND: "Bluesound audio",
    HAGatewayInterface.NUKI: "Nuki smart lock",
    HAGatewayInterface.IMAP: "Email integration",
    HAGatewayInterface.BLINK: "Security camera system",
    HAGatewayInterface.ICLOUD: "Apple ecosystem integration",
    HAGatewayInterface.FLUX_LED: "LED lighting effects",
    HAGatewayInterface.HIVE: "Hive heating control",
    HAGatewayInterface.ALERT: "Alert notifications",
    HAGatewayInterface.ECOBEE: "Ecobee smart thermostat",
    HAGatewayInterface.SHELLY: "Shelly smart home devices",
    HAGatewayInterface.SIMPLISAFE: "SimpliSafe security system",
    HAGatewayInterface.GOOGLE_ASSISTANT: "Google Assistant sync",
    HAGatewayInterface.LIFX: "LIFX LED lighting effects",
    HAGatewayInterface.ADGUARD: "AdGuard DNS filtering",
    HAGatewayInterface.ABODE: "Abode security system",
    HAGatewayInterface.AMCREST: "Amcrest IP camera control",
    HAGatewayInterface.IFTTT: "IFTTT webhook automation",
    HAGatewayInterface.ADS: "ADS automation data system",
    HAGatewayInterface.ALARMDECODER: "AlarmDecoder security keypad",
    HAGatewayInterface.ADVANTAGE_AIR: "Advantage Air HVAC control",
    HAGatewayInterface.AMBERELECTRIC: "Amber Electric energy forecasting",
    HAGatewayInterface.AGENT_DVR: "Agent DVR camera control",
    HAGatewayInterface.AI_TASK: "AI task data generation",
    HAGatewayInterface.AFTERSHIP: "AfterShip package tracking",
    HAGatewayInterface.BANG_OLUFSEN: "Bang & Olufsen BeoLink multiroom audio",
    HAGatewayInterface.ASSIST_SATELLITE: "Assist satellite voice assistant announcements",
    HAGatewayInterface.TOUCH_PANEL: "Touch panel navigation and brightness control",
    HAGatewayInterface.SQUEEZEBOX: "Squeezebox music player control",
    HAGatewayInterface.ALEXA_DEVICES: "Alexa device text and sound control",
    HAGatewayInterface.BOND: "Bond hub device control for fans, lights, and switches",
    HAGatewayInterface.BOSCH_ALARM: "Bosch alarm system time synchronization",
    HAGatewayInterface.BRING: "Bring! shopping list messaging",
    HAGatewayInterface.BSBLAN: "BSBLan heating system scheduling",
    HAGatewayInterface.TIMED_BACKUP: "Timed backup management and restoration",
    HAGatewayInterface.CACHE: "Performance caching layer",
    HAGatewayInterface.HEALTH: "System health monitoring",
}


def get_interface_description(interface: HAGatewayInterface) -> str:
    """Get description for an interface."""
    return INTERFACE_DESCRIPTIONS.get(interface, "Unknown interface")


def list_all_interfaces() -> list[HAGatewayInterface]:
    """List all available HA interfaces."""
    return list(HAGatewayInterface)


def get_voice_interfaces() -> list[HAGatewayInterface]:
    """Get all voice assistant interfaces."""
    return [HAGatewayInterface.ALEXA, HAGatewayInterface.ASSIST, HAGatewayInterface.ALEXA_RESPONSE]


def get_core_interfaces() -> list[HAGatewayInterface]:
    """Get core Home Assistant interfaces."""
    return [HAGatewayInterface.DEVICES, HAGatewayInterface.CONFIG, HAGatewayInterface.WEBSOCKET, HAGatewayInterface.REGISTRY, HAGatewayInterface.AUTOMATION, HAGatewayInterface.BLUEPRINT, HAGatewayInterface.SUPERVISOR, HAGatewayInterface.CAMERA, HAGatewayInterface.ENERGY, HAGatewayInterface.BACKUP, HAGatewayInterface.HISTORY, HAGatewayInterface.REPAIRS, HAGatewayInterface.STATISTICS, HAGatewayInterface.LOGBOOK, HAGatewayInterface.SCENE, HAGatewayInterface.SCRIPT, HAGatewayInterface.NOTIFY, HAGatewayInterface.ESPHOME, HAGatewayInterface.MOBILE_APP, HAGatewayInterface.LOGGER, HAGatewayInterface.HARDWARE, HAGatewayInterface.SENSOR, HAGatewayInterface.NUMBER, HAGatewayInterface.PERSISTENT, HAGatewayInterface.CONVERSATION, HAGatewayInterface.ZONE, HAGatewayInterface.COUNTER, HAGatewayInterface.TIMER, HAGatewayInterface.INPUT_BOOLEAN, HAGatewayInterface.SWITCH, HAGatewayInterface.LIGHT, HAGatewayInterface.CLIMATE, HAGatewayInterface.COVER, HAGatewayInterface.LOCK, HAGatewayInterface.MEDIA_PLAYER, HAGatewayInterface.BINARY_SENSOR, HAGatewayInterface.VACUUM, HAGatewayInterface.FAN, HAGatewayInterface.HUMIDIFIER, HAGatewayInterface.WATER_HEATER, HAGatewayInterface.ALARM_CONTROL_PANEL, HAGatewayInterface.BUTTON, HAGatewayInterface.GROUP, HAGatewayInterface.WEATHER, HAGatewayInterface.PERSON, HAGatewayInterface.REMOTE, HAGatewayInterface.SIREN, HAGatewayInterface.UPDATE, HAGatewayInterface.CALENDAR, HAGatewayInterface.IMAGE_PROCESSING, HAGatewayInterface.TTS, HAGatewayInterface.FILE, HAGatewayInterface.TODO, HAGatewayInterface.TEMPLATE, HAGatewayInterface.MQTT, HAGatewayInterface.SHOPPING_LIST, HAGatewayInterface.UTILITY_METER, HAGatewayInterface.WAKE_ON_LAN, HAGatewayInterface.ZHA, HAGatewayInterface.SONOS, HAGatewayInterface.ANDROIDTV, HAGatewayInterface.WEBOSTV, HAGatewayInterface.DENONAVR, HAGatewayInterface.ROKU, HAGatewayInterface.GOOGLE_MAIL, HAGatewayInterface.HUE, HAGatewayInterface.NEATO, HAGatewayInterface.TADO, HAGatewayInterface.TPLINK, HAGatewayInterface.ZWAVE_JS, HAGatewayInterface.DECONZ, HAGatewayInterface.HOMEKIT, HAGatewayInterface.TRANSMISSION, HAGatewayInterface.FFMPEG, HAGatewayInterface.CAMERA]


def get_infrastructure_interfaces() -> list[HAGatewayInterface]:
    """Get infrastructure supporting interfaces."""
    return [HAGatewayInterface.CACHE, HAGatewayInterface.HEALTH]


# ===== EXPORTS =====

__all__ = [
    "INTERFACE_DESCRIPTIONS",
    "HAGatewayInterface",
    "get_core_interfaces",
    "get_infrastructure_interfaces",
    "get_interface_description",
    "get_voice_interfaces",
    "list_all_interfaces",
]

# EOF
