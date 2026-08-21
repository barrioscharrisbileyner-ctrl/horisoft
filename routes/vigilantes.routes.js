const express = require("express");
const router = express.Router();

const controller = require("../controllers/vigilantes.controller");
const verificarToken = require("../middlewares/authMiddleware");

// GET    /vigilantes            -> listar todos (público)
// GET    /vigilantes/:id        -> obtener uno específico (público)
// POST   /vigilantes            -> crear un vigilante (protegido)
// PUT    /vigilantes/:id/estado -> actualizar estado (protegido)
// DELETE /vigilantes/:id        -> eliminar un vigilante (protegido)

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", verificarToken, controller.crear);
router.put("/:id/estado", verificarToken, controller.actualizarEstado);
router.delete("/:id", verificarToken, controller.eliminar);

module.exports = router;
