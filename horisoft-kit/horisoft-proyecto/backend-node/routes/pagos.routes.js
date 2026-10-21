const express = require("express");
const router = express.Router();

const controller = require("../controllers/pagos.controller");
const verificarToken = require("../middlewares/authMiddleware");

// Consultar pagos: público. Registrar un pago: protegido (afecta el saldo de una cuenta real).
router.get("/", controller.listar);
router.post("/", verificarToken, controller.registrar);

module.exports = router;
