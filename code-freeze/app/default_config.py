DEFAULT_CONFIG = {
    "version": "0.0.1",
    "app": {
        "ping-interval": 10,
        "epoch-offset": 946684800,
        "hostname": "rv-logger",
        "wifi": {
            "wan-check": "google.com",
        },
        "release": False,
    },

    "defaults": {
        "*": {
            "unit": "",
            "icon": "label",
            "filter": [
                "duplicate"
            ],
        },
        "Temperature": {
            "unit": "&#8451;",
            "icon": "thermometer",
            "filter": [
                { "lpf": 5 },
                { "abstol": 0.3 }
            ],
            "history": 100
        },
        "Humidity": {
            "unit": "%",
            "icon": "humidity_percentage",
            "filter": [
                { "lpf": 5 },
                { "abstol": 0.3 }
            ],
            "history": 100
        },
        "Voltage": {
            "unit": "V",
            "icon": "electric_bolt",
        },
        "Current": {
            "unit": "A",
            "icon": "electric_bolt",
        },
        "Power": {
            "unit": "W",
            "icon": "power",
        },
        "Energy": {
            "unit": "Wh",
            "icon": "energy_program_saving",
            "filter": [
                { "lpf": 5 },
                { "abstol": 0.3 }
            ],
            "history": 100
        },
        "Longitude": {
            "unit": "&deg;",
            "icon": "language",
            "filter": [
                { "lpf": 10 },
                { "abstol": 0.1 }
            ]
        },
        "Latitude": {
            "unit": "&deg;",
            "icon": "language",
            "filter": [
                { "lpf": 10 },
                { "abstol": 0.1 }
            ]
        },
        "Altitude": {
            "unit": "masl",
            "icon": "altitude",
            "filter": [
                { "lpf": 10 },
                { "abstol": 5 }
            ]
        },
        "accel-x": {
            "unit": "m/s",
            "filter": [ {"abstol": 0.01} ]
        },
        "accel-y": {
            "unit": "m/s",
            "filter": [ {"abstol": 0.01} ]
        },
        "accel-z": {
            "unit": "m/s",
            "filter": [ {"abstol": 0.01} ]
        },
        "rate-x": {
            "unit": "deg/s",
            "filter": [ {"abstol": 0.01} ]
        },
        "rate-y": {
            "unit": "deg/s",
            "filter": [ {"abstol": 0.01} ]
        },
        "rate-z": {
            "unit": "deg/s",
            "filter": [ {"abstol": 0.01} ]
        },
        "gateway-connections": {
            "name": "Gateway active connections",
            "icon": "dns",
        },
        "wifi-connection-attempts": {
            "name": "Wifi Connection Attempts",
            "icon": "wifi",
        },
        "wifi-lan": {
            "name": "Wifi Connected to LAN",
            "icon": "wifi",
        },
        "wifi-wan": {
            "name": "Wifi Connected to WAN",
            "icon": "wifi",
        },
        "wifi-status": {
            "name": "Wifi Status",
            "icon": "wifi",
        },
        "epoch": {
            "unit": "s",
            "icon": "timer",
            "history": 10,
        },
    },

    "views": [
        {
            "icon": "home",
            "entities": [ "*,*" ]
        },
        {
            "icon": "sunny",
            "entities": [ "*,Temperature" ]
        },
        {
            "icon": "solar_power",
            "entities": [
                "a4:c1:38:26:8c:84,RSSI",
                "SOC,Current",
                "MQTT,Yield",
            ]
        },
        {
            "icon": "analytics",
            "entities": [ 
                "stats,*",
                "wifi,*",
                "webapp,*",
            ]
        },
    ],

}
