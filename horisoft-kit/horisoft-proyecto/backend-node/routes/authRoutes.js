const express = require("express");
const router = express.Router();

const controller = require("../controllers/authController");
const verificarToken = require("../middlewares/authMiddleware");

// POST   /auth/registro   -> crear un usuario
// POST   /auth/login      -> autenticar un usuario y generar el Token JWT
// GET    /auth/perfil     -> ruta protegida de prueba: exige token válido
//
// Las rutas de gestión de usuarios (listar/obtener/actualizar/eliminar)
// están montadas aparte en /usuarios (ver routes/usuarios.routes.js),
// que es la ruta protegida "equivalente a /api/fichas" pedida en el
// ejercicio.

router.post("/registro", controller.registrar);
router.post("/login", controller.login);
router.get("/perfil", verificarToken, controller.perfil);

module.exports = router;
