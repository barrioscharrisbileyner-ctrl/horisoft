const express = require("express");
const router = express.Router();

const controller = require("../controllers/visitantes.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo", "Vigilante"],
    PUT: ["Administrador", "Administrativo", "Vigilante"],
    DELETE: ["Administrador", "Administrativo"],
}));

// GET    /visitantes              -> listar todos, o ?activas=true (público)
// GET    /visitantes/:id          -> obtener un registro específico (público)
// POST   /visitantes              -> registrar ingreso (protegido: acción del vigilante)
// PUT    /visitantes/:id/salida   -> registrar salida (protegido)
// DELETE /visitantes/:id          -> eliminar un registro (protegido)

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.registrarIngreso);
router.put("/:id/salida", controller.registrarSalida);
router.delete("/:id", controller.eliminar);

module.exports = router;
