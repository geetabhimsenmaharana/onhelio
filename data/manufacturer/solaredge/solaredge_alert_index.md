# SolarEdge Monitoring Portal Alerts: Complete Index

Source: SolarEdge, "Troubleshooting Alerts in the Monitoring Portal - Application Note", Version 1.0, November 2023
(se-troubleshooting-alert-application-note.pdf). The meaning and troubleshooting steps for each alert are in that guide.

This index lists every alert type in the guide, grouped by category, so the full list can be found in one place.
Some alerts appear more than once in the guide (for different inverter models or wire phases); they are listed once here.

## What types of alerts does SolarEdge have?

SolarEdge monitoring alerts fall into these categories:
1. Production alerts: the system or part of it is not producing energy
2. Communication alerts: the monitoring platform cannot reach a device or the site
3. Grid and electrical safety alerts: grid voltage or frequency problems, isolation and surge protection issues
4. Temperature and hardware alerts: overheating terminals, fans, PID mitigation
5. Battery and backup alerts: only for sites with SolarEdge batteries or backup interfaces
6. Smart energy device alerts: hot water controllers, DCS devices, load control

## 1. Production alerts
- Inverter - Production issue detected
- Inverter not producing - Firefighters safety mode on
- Inverter not producing - OFF mode
- Inverter not producing - Standby mode
- Inverter not producing energy - low voltage
- Inverter not producing Energy Limit mode
- Inverter not producing Energy Shutdown codes
- Inverter shutdown by Sense Connect
- Module voltage mismatch
- DC string is not producing energy
- String is not producing
- Snow on-site
- System overload
- G100 Export restriction

## 2. Communication alerts
- No communication with the site
- No communication with the Inverter
- No communication with Power Optimizer
- No communication with the Meter
- No communication with Battery
- Rapid alert - No communication with the site
- Rapid alert - No communication with the Inverter
- Rapid alert - No communication with the Meter
- Internal communication fault - Inverter is not producing
- Low RSSI reached

## 3. Grid and electrical safety alerts
- Grid voltage
- Grid frequency
- Grid Voltage Disruption
- Recurring grid voltage issue
- Recurring grid frequency issue
- DC Isolation Disruption
- Recurring DC Isolation issue
- Residual current device
- AC SPD failure
- DC SPD failure
- Orion AC SPD failure
- Synergy SPD failure
- SenseConnect event on Optimizer connector

## 4. Temperature and hardware alerts
- Critical ambient temperature reached
- Production issue - Inverter overheated
- Critical temperature on AC terminal (also per L1, L2, L3 conductor and AC terminal block)
- Critical temperature on DC+ terminal
- Critical temperature on DC- terminal
- Temperature warning on AC terminal (also per L1, L2, L3 conductor and AC terminal block)
- Temperature warning on DC terminal, DC+ terminal and DC- terminal
- Internal fan fault
- External fan fault
- Orion fan failure
- PID mitigation not functioning
- PID mitigation over voltage
- PID mitigation under voltage

## 5. Battery and backup alerts
- Battery below min SOE
- Battery connection error
- Battery DC wiring error
- Battery internal fault
- Battery Lockout
- Battery over voltage protection
- Battery under voltage protection
- Battery switch is off
- Battery - circuit breaker tripped
- Battery temperature too high
- Battery temperature too low
- No communication with Battery
- Backup disabled
- Backup failed
- Backup failed - Auto transformer overheated
- Backup failed - Internal circuit breaker tripped
- Backup interface - grid relay fault (on grid state)
- Backup interface - grid relay fault backup state
- Backup interface - internal fault
- Backup interface - unable to switch to on-grid
- Backup interface - generator relay fault
- Backup socket operation malfunction
- Inverter doesn't allow transition to on-grid
- System failed to return to on-grid mode

## 6. Smart energy device alerts
- DCS Critical ambient temperature reached
- DCS Device failure
- DCS Low RSSI reached
- DCS Max load reached
- Max load reached
- Hot water controller device critical ambient temperature reached
- Hot water controller device failure
- Hot water controller low RSSI reached

## Common symptoms and which alerts to look up
This section is an onHelio guide for finding the right alert by name. It is not text from SolarEdge.
Look up each named alert in the SolarEdge troubleshooting guide for its meaning and fix.

- "My inverter is not working" or "the inverter is not producing": see the Production alerts that start with
  "Inverter not producing" (Standby mode, OFF mode, low voltage, Energy Limit mode, Shutdown codes,
  Firefighters safety mode), "Inverter - Production issue detected" and "Production issue - Inverter overheated".
- "I see no data in the portal" or "the system is offline": see the Communication alerts, starting with
  "No communication with the site" and "No communication with the Inverter".
- "One panel or one row is producing less": see "Module voltage mismatch", "String is not producing",
  "DC string is not producing energy" and "No communication with Power Optimizer".
- "The same alert keeps coming back": see the "Recurring" alerts (Recurring DC Isolation issue,
  Recurring grid voltage issue, Recurring grid frequency issue).
- "Production dropped in winter": see "Snow on-site".
- "The grid or power company may be the problem": see "Grid voltage", "Grid frequency" and "Grid Voltage Disruption".
