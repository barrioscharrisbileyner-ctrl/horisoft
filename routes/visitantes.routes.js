const express = require("express");
const router = express.Router();

const controller = require("../controllers/visitantes.controller");
const verificarToken = require("../middlewares/authMiddleware");

// GET    /visitantes              -> listar todos, o ?activas=true (público)
// GET    /visitantes/:id          -> obtener un registro específico (público)
// POST   /visitantes              -> registrar ingreso (protegido: acción del vigilante)
// PUT    /visitantes/:id/salida   -> registrar salida (protegido)
// DELETE /visitantes/:id          -> eliminar un registro (protegido)

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", verificarToken, controller.registrarIngreso);
router.put("/:id/salida", verificarToken, controller.registrarSalida);
router.delete("/:id", verificarToken, controller.eliminar);

module.exports = router;
