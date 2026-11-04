const express = require("express");
const router = express.Router();

const controller = require("../controllers/pqr.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo", "Residente"],
    PUT: ["Administrador", "Administrativo"],
    DELETE: ["Administrador"],
}));

// GET    /pqr                 -> listar todas, o filtrar con ?id_residencia= (público)
// GET    /pqr/:id              -> obtener una PQR específica (público)
// POST   /pqr                  -> crear una PQR (protegido: el residente debe estar autenticado)
// PUT    /pqr/:id/respuesta    -> responder y cerrar la PQR (protegido: acción administrativa)
// PUT    /pqr/:id/estado       -> cambiar estado (protegido: acción administrativa)
// DELETE /pqr/:id               -> eliminar una PQR (protegido)
//
// Decisión de diseño: igual que en Zonas Comunes y Reservas, la lectura queda
// pública y la escritura exige un Token JWT válido, porque crear, responder
// o cerrar una PQR son acciones que dependen de quién las hace (residente o
// administrador).

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/respuesta", controller.responder);
router.put("/:id/estado", controller.cambiarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
