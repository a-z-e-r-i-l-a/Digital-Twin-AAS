# BaSyx Setup

Eclipse BaSyx Asset Administration Shell platform running on Docker. An nginx reverse proxy allows access from any machine on the network through a single entry point.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose

## Configuration

Before starting, edit the `.env` file to match your deployment:

```
EXTERNAL_HOSTNAME=10.19.1.136
EXTERNAL_PORT=3001
```

| Variable | Description |
|---|---|
| `EXTERNAL_HOSTNAME` | IP address or hostname of the machine running the stack |
| `EXTERNAL_PORT` | Port the nginx proxy listens on (the single entry point for all services) |

## Starting the stack

```bash
docker compose up -d
```

To stop:

```bash
docker compose down
```

## Accessing the services

All services are accessible through the nginx reverse proxy at `http://<EXTERNAL_HOSTNAME>:<EXTERNAL_PORT>`.

| Service | URL |
|---|---|
| **AAS Web UI** | `http://<EXTERNAL_HOSTNAME>:<EXTERNAL_PORT>/` |
| AAS Environment | `http://<EXTERNAL_HOSTNAME>:<EXTERNAL_PORT>/aas-env/` |
| AAS Registry | `http://<EXTERNAL_HOSTNAME>:<EXTERNAL_PORT>/aas-registry/` |
| Submodel Registry | `http://<EXTERNAL_HOSTNAME>:<EXTERNAL_PORT>/sm-registry/` |
| AAS Discovery | `http://<EXTERNAL_HOSTNAME>:<EXTERNAL_PORT>/aas-discovery/` |
| Dashboard API | `http://<EXTERNAL_HOSTNAME>:<EXTERNAL_PORT>/dashboard-api/` |

With the default `.env` values, the Web UI is at **http://10.19.1.136:3001**.

## Include your own Asset Administration Shells

Place AAS JSON files in the `aas/` folder before starting the stack, or upload them through the AAS Web UI at runtime.

## Project structure

```
├── .env                          # Hostname and port configuration
├── docker-compose.yml            # Service definitions
├── nginx/
│   └── nginx.conf                # Reverse proxy routing rules
├── basyx/
│   ├── aas-env.properties        # AAS Environment config
│   ├── aas-registry.yml          # AAS Registry config
│   ├── sm-registry.yml           # Submodel Registry config
│   ├── aas-discovery.properties  # Discovery Service config
│   └── aas-dashboard.yml         # Dashboard API config
├── mosquitto/
│   └── config/
│       └── mosquitto.conf        # MQTT broker config
├── aas/                          # AAS files loaded at startup
└── logo/                         # Custom logo for the Web UI
```

## Services overview

| Service | Image | Internal Port | Description |
|---|---|---|---|
| nginx | `nginx:stable-alpine` | 80 | Reverse proxy — single entry point |
| aas-env | `eclipsebasyx/aas-environment:2.0.0-SNAPSHOT` | 8081 | AAS and Submodel repository |
| aas-registry | `eclipsebasyx/aas-registry-log-mongodb:2.0.0-SNAPSHOT` | 8080 | AAS descriptor registry |
| sm-registry | `eclipsebasyx/submodel-registry-log-mongodb:2.0.0-SNAPSHOT` | 8080 | Submodel descriptor registry |
| aas-discovery | `eclipsebasyx/aas-discovery:2.0.0-SNAPSHOT` | 8081 | AAS discovery service |
| mongo | `mongo:5.0.10` | 27017 | MongoDB persistence |
| mosquitto | `eclipse-mosquitto:2.0.15` | 1883 | MQTT broker |
| aas-web-ui | `eclipsebasyx/aas-gui:SNAPSHOT` | 3000 | Web-based AAS viewer |
| dashboard-api | `aaronzi/basyx-dashboard-api:SNAPSHOT_02` | 8085 | Dashboard API |
