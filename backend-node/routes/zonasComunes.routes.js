const express = require("express");
const router = express.Router();

const controller = require("../controllers/zonasComunes.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo"],
    PUT: ["Administrador", "Administrativo"],
    DELETE: ["Administrador"],
}));

// GET    /zonas-comunes            -> listar todas (público: consultar disponibilidad)
// GET    /zonas-comunes/:id        -> obtener una zona específica (público)
// POST   /zonas-comunes            -> crear una zona (protegido: solo usuarios autenticados)
// PUT    /zonas-comunes/:id/estado -> actualizar el estado de la zona (protegido)
// DELETE /zonas-comunes/:id        -> eliminar una zona (protegido)
//
// Decisión de diseño: la lectura queda pública porque cualquier residente debe
// poder ver qué zonas comunes existen y su disponibilidad sin necesidad de
// iniciar sesión. La escritura (crear/modificar/eliminar) exige un Token JWT
// válido, porque es una operación administrativa.

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/estado", controller.actualizarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
