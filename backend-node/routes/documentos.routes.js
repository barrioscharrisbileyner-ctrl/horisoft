const express = require("express");
const router = express.Router();

const controller = require("../controllers/documentos.controller");
const verificarToken = require("../middlewares/authMiddleware");

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", verificarToken, controller.crear);
router.delete("/:id", verificarToken, controller.eliminar);

module.exports = router;
