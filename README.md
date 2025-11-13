# M3 – Sistema de Pedidos (Django + DRF)

## Resumen
Módulo de Pedidos del sistema de restaurante. Incluye:
- CRUD de pedidos.
- Confirmación con validación de stock (M1).
- Webhook de Cocina (M4) para marcar pedido `LISTO`.
- Mocks locales de M1/M4 para demo (`/mock/*`).

## Requisitos
- Python 3.11+ (probado también en 3.13)
- pip

## Variables de entorno
Configura un archivo `.env` (ejemplo en `.env.example`).

## Instalación rápida (local)
```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
Endpoints principales
GET/POST /api/pedidos/

POST /api/pedidos/{id}/confirmar

PATCH /api/pedidos/{id}/entregar

PATCH /api/pedidos/{id}/cerrar

Webhook cocina: POST /api/webhooks/cocina/pedido-listo

Mocks: POST /mock/stock/validar-reservar, POST /mock/cocina/pedidos

Pruebas rápidas (curl)
bash
Copy code
# Crear
curl -X POST http://127.0.0.1:8000/api/pedidos/ \
  -H "Content-Type: application/json" \
  -d "{\"mesa\":\"A3\",\"cliente\":\"Juan\"}"

# Listar
curl http://127.0.0.1:8000/api/pedidos/

# Confirmar (reemplaza {id})
curl -X POST http://127.0.0.1:8000/api/pedidos/{id}/confirmar

# Simular cocina -> LISTO (reemplaza {id})
curl -X POST http://127.0.0.1:8000/api/webhooks/cocina/pedido-listo \
  -H "Content-Type: application/json" \
  -d "{\"pedido_id\":\"{id}\",\"estado\":\"LISTO\"}"
Notas
Para demo local: USE_MOCKS=True usa /mock como M1/M4.

En cloud: configurar ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS y DEBUG=False.

yaml
Copy code

---

### .env.example (pega tal cual)
```env
# CORE
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost

# MOCKS / INTEGRACIONES
USE_MOCKS=True
M1_BASE_URL=http://127.0.0.1:8000/mock
M4_BASE_URL=http://127.0.0.1:8000/mock
M3_WEBHOOK_SECRET=dev-secret
Luego, commitea y sube:
bash
Copy code
git add README.md .env.example
git commit -m "docs: README y .env.example"
git push
