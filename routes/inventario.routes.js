const express = require("express");
const router = express.Router();

const controller = require("../controllers/inventario.controller");

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/cantidad", controller.actualizarCantidad);
router.put("/:id/estado", controller.actualizarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
