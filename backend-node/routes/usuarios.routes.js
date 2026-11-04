const express = require("express");
const router = express.Router();

const controller = require("../controllers/authController");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    GET: ["Administrador"],
    PUT: ["Administrador"],
    DELETE: ["Administrador"],
}));

// Ruta equivalente a "/api/fichas" del ejercicio: solo se puede acceder
// con un Token JWT válido en el header Authorization: Bearer <token>.
// Sin token, o con un token inválido/expirado, se deniega el acceso.

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.put("/:id/rol", controller.actualizarRol);
router.put("/:id/estado", controller.actualizarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
