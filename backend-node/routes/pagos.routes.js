const express = require("express");
const router = express.Router();

const controller = require("../controllers/pagos.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo"],
}));

// Consultar pagos: público. Registrar un pago: protegido (afecta el saldo de una cuenta real).
router.get("/", controller.listar);
router.post("/", controller.registrar);

module.exports = router;
