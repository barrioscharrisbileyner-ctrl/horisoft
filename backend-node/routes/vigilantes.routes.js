const express = require("express");
const router = express.Router();

const controller = require("../controllers/vigilantes.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo"],
    PUT: ["Administrador", "Administrativo"],
    DELETE: ["Administrador"],
}));

// GET    /vigilantes            -> listar todos (público)
// GET    /vigilantes/:id        -> obtener uno específico (público)
// POST   /vigilantes            -> crear un vigilante (protegido)
// PUT    /vigilantes/:id/estado -> actualizar estado (protegido)
// DELETE /vigilantes/:id        -> eliminar un vigilante (protegido)

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/estado", controller.actualizarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
