import os

from flask import Flask, jsonify, request
from supabase import create_client

app = Flask(__name__)

# Las credenciales vienen de variables de entorno, no del código
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

TABLA = "tareas"
CAMPOS_EDITABLES = {"titulo", "descripcion", "completada"}


@app.get("/api/tareas")
def listar():
    res = supabase.table(TABLA).select("*").order("id").execute()
    return jsonify(res.data)


@app.get("/api/tareas/<int:id>")
def obtener(id):
    res = supabase.table(TABLA).select("*").eq("id", id).execute()
    if not res.data:
        return jsonify({"error": "No encontrada"}), 404
    return jsonify(res.data[0])


@app.post("/api/tareas")
def crear():
    datos = request.get_json(silent=True) or {}
    titulo = (datos.get("titulo") or "").strip()
    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400
    nueva = {"titulo": titulo, "descripcion": datos.get("descripcion")}
    res = supabase.table(TABLA).insert(nueva).execute()
    return jsonify(res.data[0]), 201


@app.put("/api/tareas/<int:id>")
def actualizar(id):
    datos = request.get_json(silent=True) or {}
    # Solo se aceptan los campos permitidos, se ignora el resto
    cambios = {k: v for k, v in datos.items() if k in CAMPOS_EDITABLES}
    if not cambios:
        return jsonify({"error": "Nada que actualizar"}), 400
    res = supabase.table(TABLA).update(cambios).eq("id", id).execute()
    if not res.data:
        return jsonify({"error": "No encontrada"}), 404
    return jsonify(res.data[0])


@app.delete("/api/tareas/<int:id>")
def eliminar(id):
    res = supabase.table(TABLA).delete().eq("id", id).execute()
    if not res.data:
        return jsonify({"error": "No encontrada"}), 404
    return "", 204