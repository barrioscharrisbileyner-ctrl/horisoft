const express = require("express");
const router = express.Router();

const controller = require("../controllers/vigilantes.controller");

// GET    /vigilantes            -> listar todos
// GET    /vigilantes/:id        -> obtener uno específico
// POST   /vigilantes            -> crear un vigilante
// PUT    /vigilantes/:id/estado -> actualizar estado (Activo/Inactivo)
// DELETE /vigilantes/:id        -> eliminar un vigilante

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/estado", controller.actualizarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
