const express = require("express");
const router = express.Router();

const controller = require("../controllers/comunicados.controller");
const verificarToken = require("../middlewares/authMiddleware");

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", verificarToken, controller.crear);
router.put("/:id/archivar", verificarToken, controller.archivar);
router.delete("/:id", verificarToken, controller.eliminar);

module.exports = router;
