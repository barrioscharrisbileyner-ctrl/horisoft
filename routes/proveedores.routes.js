const express = require("express");
const router = express.Router();

const controller = require("../controllers/proveedores.controller");
const verificarToken = require("../middlewares/authMiddleware");

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", verificarToken, controller.crear);
router.put("/:id/estado", verificarToken, controller.actualizarEstado);
router.delete("/:id", verificarToken, controller.eliminar);

module.exports = router;
