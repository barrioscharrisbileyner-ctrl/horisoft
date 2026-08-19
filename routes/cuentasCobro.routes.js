const express = require("express");
const router = express.Router();

const controller = require("../controllers/cuentasCobro.controller");

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/vencida", controller.marcarVencida);
router.delete("/:id", controller.eliminar);

module.exports = router;
