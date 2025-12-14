# ui/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import requests
import datetime
from django.utils.timezone import localtime

# ================== APIS ==================
MESAS_API  = "https://sistema-gestion-restaurant.up.railway.app/api/mesas/"
PLATOS_API = "https://web-production-2d3fb.up.railway.app/api/platos/"

ESTADOS_ACTIVOS = {"CREADO", "EN_PREPARACION", "LISTO", "ENTREGADO"}

# ================== HELPERS ==================
def _load_mesas():
    r = requests.get(MESAS_API, timeout=10)
    r.raise_for_status()
    return r.json().get("results", [])

def _load_platos():
    r = requests.get(PLATOS_API, timeout=10)
    r.raise_for_status()
    data = r.json().get("results", [])
    return [p for p in data if p.get("activo")]

def _load_pedidos(request):
    r = requests.get(
        request.build_absolute_uri("/api/pedidos/"),
        timeout=10
    )
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    return data

def _mesa_ocupada(pedidos, mesa_num):
    for p in pedidos:
        if str(p.get("mesa")) == str(mesa_num) and p.get("estado") in ESTADOS_ACTIVOS:
            return True
    return False

def _fmt_fecha(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        dt = localtime(dt) if dt.tzinfo else dt
        return dt.strftime("%d/%m %H:%M")
    except Exception:
        return iso

# ================== MESERO ==================
def mesero(request):
    try:
        pedidos = _load_pedidos(request)
        mesas = _load_mesas()
        platos = _load_platos()
    except Exception as e:
        messages.error(request, f"Error cargando datos: {e}")
        pedidos, mesas, platos = [], [], []

    # Enriquecer pedidos
    platos_dict = {str(p["id"]): p["nombre"] for p in platos}
    for p in pedidos:
        p["plato_nombre"] = platos_dict.get(str(p.get("plato")), p.get("plato"))
        p["creado_str"] = _fmt_fecha(p.get("creado_en"))
        p["actu_str"] = _fmt_fecha(p.get("actualizado_en"))

    # Marcar mesas ocupadas
    mesas_disponibles = []
    for m in mesas:
        if not _mesa_ocupada(pedidos, m["numero"]) and m["estado"] == "disponible":
            mesas_disponibles.append(m)

    context = {
        "pedidos": pedidos,
        "mesas": mesas_disponibles,
        "platos": platos,
    }
    return render(request, "ui/mesero.html", context)

@require_http_methods(["POST"])
def crear_pedido(request):
    mesa    = request.POST.get("mesa")
    cliente = request.POST.get("cliente", "").strip()
    plato   = request.POST.get("plato")

    if not mesa or not cliente or not plato:
        messages.error(request, "Todos los campos son obligatorios.")
        return redirect("ui:mesero")

    try:
        pedidos = _load_pedidos(request)
        if _mesa_ocupada(pedidos, mesa):
            messages.error(request, f"La mesa {mesa} ya está ocupada.")
            return redirect("ui:mesero")
    except Exception as e:
        messages.error(request, f"No se pudo validar la mesa: {e}")
        return redirect("ui:mesero")

    try:
        body = {
            "mesa": mesa,
            "cliente": cliente,
            "plato": plato
        }
        r = requests.post(
            request.build_absolute_uri("/api/pedidos/"),
            json=body,
            timeout=10
        )
        if r.status_code in (200, 201):
            messages.success(request, f"Pedido creado para mesa {mesa}.")
        else:
            messages.error(request, f"Error al crear pedido (HTTP {r.status_code}).")
    except Exception as e:
        messages.error(request, f"Error creando pedido: {e}")

    return redirect("ui:mesero")

# ================== ACCIONES ==================
def accion_confirmar(request, pedido_id):
    requests.post(request.build_absolute_uri(f"/api/pedidos/{pedido_id}/confirmar/"))
    return redirect("ui:mesero")

def accion_cancelar(request, pedido_id):
    requests.post(request.build_absolute_uri(f"/api/pedidos/{pedido_id}/cancelar/"))
    return redirect("ui:mesero")

def accion_entregar(request, pedido_id):
    requests.patch(request.build_absolute_uri(f"/api/pedidos/{pedido_id}/entregar/"))
    return redirect("ui:mesero")

def accion_cerrar(request, pedido_id):
    requests.patch(request.build_absolute_uri(f"/api/pedidos/{pedido_id}/cerrar/"))
    return redirect("ui:mesero")

def cocina(request):
    try:
        pedidos = _load_pedidos(request)
        platos = _load_platos()
    except Exception as e:
        messages.error(request, f"Error cargando pedidos: {e}")
        return render(request, "ui/cocina.html", {"pedidos": []})

    # Enriquecer pedidos
    platos_dict = {str(p["id"]): p["nombre"] for p in platos}
    pedidos_cocina = []

    for p in pedidos:
        if p.get("estado") in ("CREADO", "EN_PREPARACION"):
            p["plato_nombre"] = platos_dict.get(str(p.get("plato")), p.get("plato"))
            p["creado_str"] = _fmt_fecha(p.get("creado_en"))
            p["actu_str"] = _fmt_fecha(p.get("actualizado_en"))
            pedidos_cocina.append(p)

    return render(request, "ui/cocina.html", {
        "pedidos": pedidos_cocina
    })



@require_http_methods(["POST"])
def cocina_en_preparacion(request, pedido_id):
    requests.patch(
        request.build_absolute_uri(f"/api/pedidos/{pedido_id}/en-preparacion/")
    )
    return redirect("ui:cocina")


@require_http_methods(["POST"])
def cocina_sin_ingredientes(request, pedido_id):
    requests.post(
        request.build_absolute_uri(f"/api/pedidos/{pedido_id}/cancelar/")
    )
    return redirect("ui:cocina")



@require_http_methods(["POST"])
@require_http_methods(["POST"])
def cocina_listo(request, pedido_id):
    r = requests.patch(
        request.build_absolute_uri(f"/api/pedidos/{pedido_id}/listo/")
    )
    if r.status_code not in (200, 204):
        messages.error(
            request,
            f"No se pudo marcar el pedido como listo (HTTP {r.status_code})."
        )
    return redirect("ui:cocina")


def stock(request):
    try:
        platos = _load_platos()
    except Exception as e:
        messages.error(request, f"Error cargando stock: {e}")
        platos = []

    return render(request, "ui/stock.html", {
        "platos": platos
    })
