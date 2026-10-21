const express = require("express");
const router = express.Router();

const controller = require("../controllers/configuracion.controller");
const verificarToken = require("../middlewares/authMiddleware");

// Consultar parámetros: público. Crear/editar/eliminar: protegido (solo administración).
router.get("/", controller.listar);
router.get("/:clave", controller.obtener);
router.post("/", verificarToken, controller.crear);
router.put("/:clave", verificarToken, controller.actualizarValor);
router.delete("/:clave", verificarToken, controller.eliminar);

module.exports = router;
