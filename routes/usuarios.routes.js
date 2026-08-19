const express = require("express");
const router = express.Router();

const controller = require("../controllers/authController");
const verificarToken = require("../middlewares/authMiddleware");

// Ruta equivalente a "/api/fichas" del ejercicio: solo se puede acceder
// con un Token JWT válido en el header Authorization: Bearer <token>.
// Sin token, o con un token inválido/expirado, se deniega el acceso.

router.get("/", verificarToken, controller.listar);
router.get("/:id", verificarToken, controller.obtener);
router.put("/:id/rol", verificarToken, controller.actualizarRol);
router.put("/:id/estado", verificarToken, controller.actualizarEstado);
router.delete("/:id", verificarToken, controller.eliminar);

module.exports = router;
