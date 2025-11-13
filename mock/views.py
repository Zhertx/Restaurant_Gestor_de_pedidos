import json, uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# "BD" en memoria para demo
RESERVAS = {}   # reserva_id -> {"pedido_id": "...", "items":[...], "estado":"RESERVADO"}
COCINA = {}     # pedido_id -> {"estado":"EN_COLA"|"EN_PREPARACION"|"LISTO"}

def _json(request):
    return json.loads(request.body.decode("utf-8") or "{}")

@csrf_exempt
def mock_validar_reservar(request):
    """
    M1: POST /mock/stock/validar-reservar
    Body: {"pedido_id":"...", "items":[{"plato_id":101,"cantidad":2}, ...]}
    Regla inventada: si algún item tiene cantidad > 5 => SIN_STOCK
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    body = _json(request)
    if any(it.get("cantidad", 0) > 5 for it in body.get("items", [])):
        return JsonResponse({"ok": False, "error": "SIN_STOCK"}, status=409)

    reserva_id = str(uuid.uuid4())
    RESERVAS[reserva_id] = {
        "pedido_id": body.get("pedido_id"),
        "items": body.get("items", []),
        "estado": "RESERVADO",
    }
    return JsonResponse({"ok": True, "reserva_id": reserva_id, "status": "RESERVADO"})

@csrf_exempt
def mock_liberar(request):
    """
    M1: POST /mock/stock/liberar
    Body: {"reserva_id":"..."}
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    body = _json(request)
    rid = body.get("reserva_id")
    if rid in RESERVAS:
        RESERVAS[rid]["estado"] = "LIBERADO"
        return JsonResponse({"ok": True, "status": "LIBERADO"})
    return JsonResponse({"ok": False, "error": "RESERVA_NO_ENCONTRADA"}, status=404)

@csrf_exempt
def mock_confirmar(request):
    """
    M1: POST /mock/stock/confirmar
    Body: {"reserva_id":"..."}
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    body = _json(request)
    rid = body.get("reserva_id")
    if rid in RESERVAS and RESERVAS[rid]["estado"] in ("RESERVADO", "LIBERADO"):
        RESERVAS[rid]["estado"] = "CONFIRMADO"
        return JsonResponse({"ok": True, "status": "CONFIRMADO"})
    return JsonResponse({"ok": False, "error": "RESERVA_INVALIDA"}, status=400)

@csrf_exempt
def mock_cocina_pedidos(request):
    """
    M4: POST /mock/cocina/pedidos
    Body: {"id":"pedido_uuid","mesa":"A1","items":[...]}
    Simula recepción del pedido en cocina y lo deja "EN_COLA".
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    body = _json(request)
    pid = body.get("id")
    if not pid:
        return JsonResponse({"error": "id requerido"}, status=400)
    COCINA[pid] = {"estado": "EN_COLA", "items": body.get("items", [])}
    return JsonResponse({"ok": True, "cocina_id": str(uuid.uuid4()), "status": "EN_COLA"}, status=201)
