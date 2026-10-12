# ==========================================
# FITUR PEMBAYARAN QRIS & VERIFIKASI ADMIN
# ==========================================

# 1. API Admin: Upload/Set QRIS
@app.post("/api/admin/qris")
@auth_required
@role_required("admin")
def set_admin_qris():
    data = request.get_json(force=True, silent=True) or {}
    qris_url = (data.get("qris_image_url") or "").strip()
    if not qris_url:
        return jsonify({"error": "URL/Gambar QRIS wajib diisi"}), 400
    
    db = get_db()
    db.execute("DELETE FROM payment_settings")
    db.execute("INSERT INTO payment_settings (qris_image_url) VALUES (%s)", (qris_url,))
    db.commit()
    return jsonify({"ok": True, "qris_image_url": qris_url})

# 2. API Public/Customer: Ambil QRIS Admin
@app.get("/api/qris")
def get_admin_qris():
    db = get_db()
    row = db.execute("SELECT qris_image_url FROM payment_settings ORDER BY id DESC LIMIT 1").fetchone()
    return jsonify({"qris_image_url": row["qris_image_url"] if row else ""})

# 3. API Customer: Upload Bukti Bayar (File JPG/PNG)
@app.post("/api/orders/<int:oid>/pay")
@auth_required
@role_required("customer")
def submit_payment_proof(oid):
    data = request.get_json(force=True, silent=True) or {}
    proof_url = (data.get("payment_proof_url") or "").strip()
    if not proof_url:
        return jsonify({"error": "Bukti pembayaran (file JPG/PNG) wajib diupload"}), 400
    
    db = get_db()
    o = db.execute("SELECT * FROM orders WHERE id=%s", (oid,)).fetchone()
    if o is None:
        return jsonify({"error": "Order tidak ditemukan"}), 404
    if o["customer_id"] != g.user["id"]:
        return jsonify({"error": "Bukan order milikmu"}), 403
    
    db.execute(
        "UPDATE orders SET payment_proof_url=%s, payment_status='verifying', updated_at=%s WHERE id=%s",
        (proof_url, now_str(), oid)
    )
    db.commit()
    return jsonify({"ok": True, "payment_status": "verifying"})

# 4. API Admin: Daftar Order & Bukti Bayar untuk Diverifikasi
@app.get("/api/admin/payments")
@auth_required
@role_required("admin")
def list_admin_payments():
    db = get_db()
    rows = db.execute(
        """SELECT o.id, o.price_snapshot, o.payment_proof_url, o.payment_status, o.created_at,
                  cu.name AS customer_name, cr.name AS creator_name, s.title AS service_title
           FROM orders o
           JOIN users cu ON cu.id = o.customer_id
           JOIN users cr ON cr.id = o.creator_id
           LEFT JOIN services s ON s.id = o.service_id
           ORDER BY o.created_at DESC"""
    ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])

# 5. API Admin: Setujui / Tolak Pembayaran
@app.patch("/api/admin/orders/<int:oid>/verify-payment")
@auth_required
@role_required("admin")
def verify_payment(oid):
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action") # 'approve' atau 'reject'
    if action not in ("approve", "reject"):
        return jsonify({"error": "Aksi harus approve atau reject"}), 400
    
    new_pay_status = 'paid' if action == 'approve' else 'rejected'
    db = get_db()
    o = db.execute("SELECT * FROM orders WHERE id=%s", (oid,)).fetchone()
    if o is None:
        return jsonify({"error": "Order tidak ditemukan"}), 404
    
    db.execute(
        "UPDATE orders SET payment_status=%s, updated_at=%s WHERE id=%s",
        (new_pay_status, now_str(), oid)
    )
    db.commit()
    return jsonify({"ok": True, "payment_status": new_pay_status})