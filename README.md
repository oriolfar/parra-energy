I’m building a home energy automation system called **Parra Energy**.

The goal is to intelligently control electrical devices (like a water heater, washing machine, or router) based on the solar energy surplus produced by my **Fronius solar inverter**, using a Raspberry Pi (or a local computer during development).

The project is structured in Python and divided into:
- `api/`: reads real-time data from the Fronius inverter using its local REST API.
- `simulators/`: simulates smart plugs or devices before I get the actual hardware.
- `automations/`: contains logic to decide when to turn devices on/off based on solar surplus.
- `web/`: an optional local web dashboard (Flask) to visualize current status.
- `tests/`: used to verify components independently.

The inverter's API endpoint returns data like current solar production (`P_PV`), consumption (`P_Load`), and grid interaction (`P_Grid`) in watts.

Right now, I’m developing and testing everything on my computer. Later, I’ll move the system to a Raspberry Pi and connect real smart plugs using Shelly, Tapo, or Sonoff via HTTP/MQTT.

My main priorities now:
1. Fetch real-time data from the Fronius API.
2. Simulate devices that turn on/off.
3. Automate control rules based on the energy surplus.
4. (Optional) Push notifications or dashboard interface.

Please help me implement and improve this step by step.
