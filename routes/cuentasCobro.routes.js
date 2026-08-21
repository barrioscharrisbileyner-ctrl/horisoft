const express = require("express");
const router = express.Router();

const controller = require("../controllers/cuentasCobro.controller");
const verificarToken = require("../middlewares/authMiddleware");

// Lectura pública, escritura protegida (mismo criterio que los demás módulos).
router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", verificarToken, controller.crear);
router.put("/:id/vencida", verificarToken, controller.marcarVencida);
router.delete("/:id", verificarToken, controller.eliminar);

module.exports = router;
