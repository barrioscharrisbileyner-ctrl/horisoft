const express = require("express");
const router = express.Router();

const controller = require("../controllers/cuentasCobro.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo"],
    PUT: ["Administrador", "Administrativo"],
    DELETE: ["Administrador"],
}));

// Lectura pública, escritura protegida (mismo criterio que los demás módulos).
router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/vencida", controller.marcarVencida);
router.delete("/:id", controller.eliminar);

module.exports = router;
