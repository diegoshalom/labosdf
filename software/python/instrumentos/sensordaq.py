# https://www.vernier.com/files/manuals/sdaq.pdf
# Todo está en este manual

# Para acceder a los tres canales de sensores, se inicializa igual que una daq, y hay que darle el nombre del canal:
# Channel Name: "Dev1/_sensor0_5V"
# Max Input Limit: 5 Volt
# Min Input Limit: 0 Volt
# Input Configuration: RSE
# Ej: ai_channel = task.ai_channels.add_ai_voltage_chan("Dev1/_sensor0_5V", min_val=0, max_val=5, terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)

# Channel Name: "Dev1/_sensor0_10V"
# Max Input Limit: 10 Volt
# Min Input Limit: -10 Volt
# Input Configuration: RSE
# Ej: ai_channel = task.ai_channels.add_ai_voltage_chan("Dev1/_sensor0_10V", min_val=-10, max_val=10, terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)

# Para acceder a los tres canales, cambiar el 0 por 1 o 2.

# Además, la placa SensorDaq tiene dos canales analógicos ai0 y ai1, en la bornera.