const express = require("express");
const router = express.Router();

const controller = require("../controllers/reservas.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo", "Residente"],
    PUT: ["Administrador", "Administrativo"],
    DELETE: ["Administrador"],
}));

// GET    /reservas               -> listar todas, o filtrar con ?id_zona= (público)
// GET    /reservas/:id           -> obtener una reserva específica (público)
// POST   /reservas               -> crear una reserva (protegido: exige sesión)
// PUT    /reservas/:id/estado    -> cambiar estado (protegido)
// DELETE /reservas/:id           -> eliminar una reserva (protegido)
//
// Decisión de diseño: crear, cambiar o eliminar una reserva son acciones que
// un residente ejecuta sobre su propia reserva, así que exigen estar
// autenticado (Token JWT). Consultar las reservas existentes queda público.

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/estado", controller.cambiarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
