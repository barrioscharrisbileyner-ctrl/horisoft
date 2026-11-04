const express = require("express");
const router = express.Router();

const controller = require("../controllers/documentos.controller");
const { autorizarMetodos } = require("../middlewares/authorizationMiddleware");

router.use(autorizarMetodos({
    POST: ["Administrador", "Administrativo"],
    DELETE: ["Administrador"],
}));

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.delete("/:id", controller.eliminar);

module.exports = router;
