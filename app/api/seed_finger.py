import psycopg2
import uuid
from datetime import datetime, timedelta

# ================= CONFIGURACIÓN =================
# Edita esto con tus credenciales reales
DB_HOST = "localhost"
DB_NAME = "gym_admin"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_PORT = "55432"
# =================================================

def run_seed():
    conn = None
    try:
        print("🔌 Conectando a PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        cur = conn.cursor()

        print("🚀 Iniciando inserción masiva...")

        # 1. GENERAR O BUSCAR DATOS ESTÁTICOS (MÉTODO PAGO Y MEMBRESÍA)
        
        # A. Método de Pago
        cur.execute("SELECT id FROM metodo_pago WHERE tipo = 'Script Python' LIMIT 1;")
        res = cur.fetchone()
        
        if res:
            pago_id = res[0]
        else:
            pago_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO metodo_pago (id, tipo, created, updated)
                VALUES (%s, %s, %s, %s)
            """, (pago_id, 'Script Python', datetime.now(), datetime.now()))

        # B. Membresía (Plan)
        cur.execute("SELECT id FROM membresia WHERE tipo = 'Plan Python' LIMIT 1;")
        res = cur.fetchone()
        
        if res:
            plan_id = res[0]
        else:
            plan_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO membresia (id, tipo, duracion_dias, precio_actual, created, updated)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (plan_id, 'Plan Python', 30, 0, datetime.now(), datetime.now()))

        # 2. BUCLE DE 243 USUARIOS
        # Usamos un solo bloque de transacción para todo el bucle
        
        for i in range(1, 244):
            # Generar UUIDs en Python para evitar problemas de sintaxis SQL
            cliente_id = str(uuid.uuid4())
            membresia_cliente_id = str(uuid.uuid4())
            
            # Fechas
            ahora = datetime.now()
            ayer = ahora - timedelta(days=1)
            fin_mes = ahora + timedelta(days=30)
            
            # A. Insertar Cliente
            cur.execute("""
                INSERT INTO cliente (id, nombre, correo, telefono, fecha_nacimiento, created, updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente_id, 
                f"Python User {i}", 
                f"py_user_{i}@test.com", 
                f"300{i:07d}", 
                "1990-01-01", 
                ahora, 
                ahora
            ))

            # B. Insertar Huella (Fingerprint)
            # Asumiendo que 'id' es autoincremental (SERIAL), no lo pasamos. 
            # Si tu 'id' en fingerprints no es SERIAL, avísame.
            cur.execute("""
                INSERT INTO fingerprints (user_id, template_id, created_at, created, updated)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                cliente_id, 
                i,  # Aquí va el slot del 1 al 243
                ahora,
                ahora,
                ahora
            ))

            # C. Insertar Membresía Activa
            cur.execute("""
                INSERT INTO membresia_cliente 
                (id, cliente_id, membresia_id, metodo_pago_id, fecha_inicio, fecha_fin, precio_pagado, active, created, updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                membresia_cliente_id,
                cliente_id,
                plan_id,
                pago_id,
                ayer,
                fin_mes,
                0,
                True, # Active = True
                ahora,
                ahora
            ))

            if i % 50 == 0:
                print(f"✅ Procesados {i} registros...")

        # 3. CONFIRMAR CAMBIOS
        conn.commit()
        print("🎉 ¡ÉXITO! 243 usuarios insertados correctamente.")
        cur.close()

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        if conn:
            conn.rollback()
            print("🔄 Se han revertido los cambios (Rollback).")
    
    finally:
        if conn:
            conn.close()
            print("🔌 Conexión cerrada.")

if __name__ == "__main__":
    run_seed()