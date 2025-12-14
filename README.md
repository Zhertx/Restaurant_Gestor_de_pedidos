## Historial de cambios

### [2025-12-14]
- Implementación de vista de cocina
- Acciones de pedidos desde cocina (en preparación / listo)
- Vista de stock consumiendo API externa
- Correcciones en flujo de estados de pedidos



Descripción general

Este proyecto implementa el Módulo 3: Gestión de Pedidos del sistema colaborativo para un restaurante.
Incluye:

CRUD de pedidos

Agregado de platos por pedido

Confirmación del pedido con validación automática de stock (Módulo 1)

Webhook del Módulo 4 (Cocina) para marcar pedidos como LISTO

Flujo completo: CREADO → EN_PREPARACION → LISTO → ENTREGADO → CERRADO

Mock de M1 y M4 para pruebas locales sin depender de otros módulos

Interfaz gráfica (UI) para Mesero y Cocina incluida en /ui/

Todo construido en Django + Django REST Framework.

Arquitectura del módulo
restaurante/
│
├── pedidos/       → API real del módulo 3
├── ui/            → Interfaz web (Mesero / Cocina)
├── mock/          → Simulación de M1 y M4 para desarrollo
├── panel/         → Panel administrativo (demo)
│
└── restaurante/   → Settings, URLs, configuración general

Funcionalidades principales
✔ Gestión de pedidos

Crear pedidos (por mesa o cliente)

Agregar platos al pedido

Listar pedidos activos y recientes

Cerrar / entregar / cancelar pedidos

✔ Integración con Menú & Stock (M1)

Validación de stock con reserva antes de confirmar

✔ Integración con Cocina (M4)

Recibir eventos de cocina vía Webhooks

Acción LISTO para marcar pedido terminado

✔ Mock completo para desarrollo

/mock/stock/validar-reservar

/mock/cocina/pedidos

/mock/cocina/pedido-listo

Permite probar todo el flujo sin depender de otros equipos.

✔ Interfaces gráficas (UI)

/mesero/ – gestión de pedidos

/cocina/ – monitor de cocina

/stock/ – visualización rápida

Estados del pedido
CREADO → EN_PREPARACION → LISTO → ENTREGADO → CERRADO
           ↘
           CANCELADO

⚙️ Requisitos

Python 3.11+ (probado también en 3.13)

pip

🔧 Configuración de entorno

Crea tu archivo .env:

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

🛠 Instalación y ejecución local
# Crear entorno
py -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
py -m pip install -r requirements.txt

# Migraciones
py manage.py migrate

# Ejecutar servidor
py manage.py runserver


Abre:
http://127.0.0.1:8000/mesero/
http://127.0.0.1:8000/cocina/

📡 Endpoints principales (API real)
Pedidos
GET    /api/pedidos/
POST   /api/pedidos/
GET    /api/pedidos/{id}/
PATCH  /api/pedidos/{id}/
DELETE /api/pedidos/{id}/

Acciones
POST  /api/pedidos/{id}/confirmar/
POST  /api/pedidos/{id}/cancelar/
PATCH /api/pedidos/{id}/listo/
PATCH /api/pedidos/{id}/entregar/
PATCH /api/pedidos/{id}/cerrar/

Webhook de Cocina
POST /api/webhooks/cocina/pedido-listo/

Mocks
POST /mock/stock/validar-reservar
POST /mock/cocina/pedidos

Pruebas básicas (curl)
Crear pedido
curl -X POST http://127.0.0.1:8000/api/pedidos/ \
  -H "Content-Type: application/json" \
  -d "{\"mesa\":\"A3\",\"cliente\":\"Juan\"}"

Listar pedidos
curl http://127.0.0.1:8000/api/pedidos/

Confirmar pedido
curl -X POST http://127.0.0.1:8000/api/pedidos/{id}/confirmar/

Simular cocina → pedido listo
curl -X POST http://127.0.0.1:8000/api/webhooks/cocina/pedido-listo \
  -H "Content-Type: application/json" \
  -d "{\"pedido_id\":\"{id}\"}"

Tests automáticos

Incluye tests funcionales del flujo en:

/pedidos/test/


Ejecuta:

py manage.py test
